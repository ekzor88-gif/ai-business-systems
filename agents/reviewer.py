import os
import json
import logging
from typing import Dict, Any, List, Optional
from core.base_agent import BaseAgent
from schemas.models import PortfolioFeed, ReviewReport, ReviewIssue

class ReviewerAgent(BaseAgent):
    """
    Агент аудита качества и предотвращения галлюцинаций (Reviewer Agent).
    Выполняет кросс-валидацию сгенерированной ленты портфолио (portfolio.json / feed.json)
    с фактической базой знаний (knowledge.json).
    """
    def __init__(self):
        super().__init__("reviewer")

    def audit_portfolio_feed(self, feed_data: Dict[str, Any], knowledge_data: Dict[str, Any]) -> ReviewReport:
        """
        Проверяет сгенерированные элементы ленты на предмет полноты,
        несоответствий с базой знаний и фактической достоверности.
        """
        issues: List[ReviewIssue] = []

        # 1. Валидация Pydantic-структуры
        try:
            feed = PortfolioFeed.model_validate(feed_data)
        except Exception as e:
            self.logger.error(f"Pydantic validation error in Reviewer: {e}")
            issues.append(
                ReviewIssue(
                    severity="high",
                    field="root",
                    issue_type="schema_mismatch",
                    description=f"Ошибка структуры ленты контента: {e}",
                    suggestion="Исправьте структуру ответа Portfolio Generator согласно Pydantic схеме."
                )
            )
            return ReviewReport(
                is_approved=False,
                score=0.0,
                issues=issues,
                summary="Валидация схемы не пройдена."
            )

        # 2. Извлечение известных технологий и проектов из knowledge_data
        known_techs = set()
        raw_techs = knowledge_data.get("technologies", []) or knowledge_data.get("skills", [])
        if isinstance(raw_techs, list):
            for t in raw_techs:
                if isinstance(t, str):
                    known_techs.add(t.lower())
                elif isinstance(t, dict) and "name" in t:
                    known_techs.add(str(t["name"]).lower())

        # 3. Кросс-проверка элементов ленты
        unsupported_tech_count = 0
        for item in feed.items:
            # Проверка наличия заголовка и содержимого
            if not item.title or not item.summary:
                issues.append(
                    ReviewIssue(
                        severity="medium",
                        field=f"item[{item.id}]",
                        issue_type="missing_fact",
                        description=f"Элемент '{item.id}' содержит пустой заголовок или краткое описание.",
                        suggestion="Добавьте содержательный заголовок и summary."
                    )
                )

            # Аудит упомянутых технологий
            for tech in item.technologies:
                if known_techs and tech.lower() not in known_techs:
                    unsupported_tech_count += 1
                    issues.append(
                        ReviewIssue(
                            severity="low",
                            field=f"item[{item.id}].technologies",
                            issue_type="hallucination",
                            description=f"Технология '{tech}' отсутствует в базе знаний.",
                            suggestion=f"Убедитесь, что '{tech}' действительно использовалась в проекте."
                        )
                    )

        # Расчет итогового рейтинга качества (Score)
        score = 1.0 - (len(issues) * 0.1)
        if score < 0.0:
            score = 0.0

        is_approved = score >= 0.7 and not any(i.severity == "critical" for i in issues)

        summary = (
            f"Аудит завершен успешно. Одобрено: {is_approved}. "
            f"Оценка: {score:.2f}, Найдено замечаний: {len(issues)}."
        )
        self.logger.info(summary)

        return ReviewReport(
            is_approved=is_approved,
            score=round(score, 2),
            issues=issues,
            summary=summary
        )

    def run_review(self, feed_file_path: str, knowledge_file_path: str) -> Dict[str, Any]:
        """Точка входа для запуска проверки из файла."""
        if not os.path.exists(feed_file_path) or not os.path.exists(knowledge_file_path):
            self.logger.error("Файлы для аудита не найдены.")
            return {"is_approved": False, "reason": "Missing files"}

        with open(feed_file_path, "r", encoding="utf-8") as f:
            feed_data = json.load(f)

        with open(knowledge_file_path, "r", encoding="utf-8") as f:
            knowledge_data = json.load(f)

        report = self.audit_portfolio_feed(feed_data, knowledge_data)
        return report.model_dump()

    def execute(self, feed_file_path: Optional[str] = None, knowledge_file_path: Optional[str] = None, *args, **kwargs) -> Dict[str, Any]:
        """Основной метод запуска работы агента аудотора."""
        if not feed_file_path:
            feed_file_path = os.path.join(self.paths.get("paths", {}).get("output_dir", "portfolio_website/src/data"), "feed.json")
        if not knowledge_file_path:
            knowledge_file_path = self.paths.get("paths", {}).get("knowledge_file", "storage/knowledge/knowledge.json")
        return self.run_review(feed_file_path, knowledge_file_path)
