import os
import json
import logging
from typing import Dict, Any, List

class PortfolioGenerator:
    def __init__(self):
        self.logger = logging.getLogger("portfolio_generator")
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        self.knowledge_file = "c:/projects/portfolio_factory/storage/knowledge/knowledge.json"
        self.output_dir = "c:/projects/portfolio_factory/portfolio_website/src/data"

    def execute(self):
        self.logger.info("Начало работы Portfolio Generator Agent...")
        
        if not os.path.exists(self.knowledge_file):
            self.logger.error(f"Файл базы знаний не найден: {self.knowledge_file}")
            return
            
        with open(self.knowledge_file, "r", encoding="utf-8") as f:
            knowledge = json.load(f)
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        self._generate_cases(knowledge)
        
        self.logger.info("Работа Portfolio Generator Agent успешно завершена.")
        
    def _generate_cases(self, knowledge: Dict[str, Any]):
        projects = knowledge.get("projects", [])
        cases = []
        
        import shutil
        public_media_dir = "c:/projects/portfolio_factory/portfolio_website/public/media"
        os.makedirs(public_media_dir, exist_ok=True)
        
        for p in projects:
            p_desc = p.get("description", "").lower()
            p_name = p.get("name", "").lower()
            
            # Находим связанные evidence (скриншоты)
            # Так как медиа файлы не привязаны к проектам жестко, мы используем эвристику по имени файла
            images = []
            for ev in knowledge.get("evidence", []):
                if ev.get("type") in ["image", "screenshot", "video"] and ev.get("source") == "manual_upload":
                    filename = os.path.basename(ev.get("location")).lower()
                    # Эвристика: если имя файла похоже на проект или просто привяжем вручную для демо
                    if "greenleaf" in filename and "greenleaf" in p_name:
                        images.append(ev)
                    elif "mediacube" in filename and ("mc pay" in p_name or "mediacube" in p_name):
                        images.append(ev)
                    elif "estimate" in filename and "estimate" in p_name:
                        images.append(ev)
                    elif "wine" in filename and "wine" in p_name:
                        images.append(ev)
                        
            image_paths = []
            for ev in images:
                src_loc = os.path.join("c:/projects/portfolio_factory", ev.get("location"))
                if os.path.exists(src_loc):
                    filename = os.path.basename(src_loc)
                    dest_loc = os.path.join(public_media_dir, filename)
                    shutil.copy2(src_loc, dest_loc)
                    image_paths.append(f"/media/{filename}")
                    
            if not image_paths:
                # Generate an SVG placeholder
                placeholder_path = os.path.join(public_media_dir, f"placeholder_{p.get('id')}.svg")
                svg_content = f'''<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
                  <rect width="100%" height="100%" fill="#111111" stroke="#333333" stroke-width="2"/>
                  <text x="50%" y="50%" font-family="monospace" font-size="24" fill="#666666" text-anchor="middle" dominant-baseline="middle">
                    Architecture Interface Placeholder
                  </text>
                  <text x="50%" y="60%" font-family="monospace" font-size="14" fill="#444444" text-anchor="middle" dominant-baseline="middle">
                    {p.get("name")}
                  </text>
                </svg>'''
                with open(placeholder_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)
                image_paths.append(f"/media/placeholder_{p.get('id')}.svg")

            # Разрешаем уроки и сохраняем подробный формат
            lessons_text = []
            for l_id in p.get("lessons_learned", []):
                lesson = next((l for l in knowledge.get("lessons_learned", []) if l.get("id") == l_id), None)
                if lesson:
                    lessons_text.append({
                        "title": lesson.get("title"),
                        "description": lesson.get("description")
                    })
            
            # Разрешаем технологии
            tech_names = []
            for t_id in p.get("technologies", []):
                tech = next((t for t in knowledge.get("technologies", []) if t.get("id") == t_id), None)
                if tech:
                    tech_names.append(tech.get("name"))
                else:
                    tech_names.append(t_id)

            solution = "\n".join([f"• {l['title']}" for l in lessons_text]) if lessons_text else "Архитектура реализована успешно."
            
            case = {
                "id": p.get("id"),
                "title": p.get("name"),
                "subtitle": "Pet Project" if p.get("project_type") == "pet_project" else "Коммерческий проект",
                "category": "Интеграция" if "Integration" in p.get("name") else "AI",
                "status": p.get("status", "completed"),
                "problem": p.get("description", ""),
                "solution": solution,
                "result": "Успешно реализовано.",
                "tech": tech_names,
                "tags": tech_names[:3],
                "images": image_paths,
                "architecture": p.get("architecture", {}),
                "lessons_text": lessons_text
            }
            metrics = [m for m in knowledge.get("metrics", []) if m.get("project_id") == p.get("id")]
            if metrics:
                results = []
                for m in metrics:
                    before = m.get('before')
                    after = m.get('after')
                    mtype = m.get('metric_type')
                    
                    if before and after and before.lower() != "unknown" and after.lower() != "unknown":
                        if mtype == 'Time Reduction':
                            res_str = f"• Время выполнения сокращено с {before} до {after}"
                        elif mtype == 'Cost Reduction':
                            res_str = f"• Расходы снизились с {before} до {after}"
                        else:
                            res_str = f"• {mtype}: с {before} до {after}"
                    else:
                        res_str = f"• Улучшено {mtype}"
                        if m.get('improvement_percent'):
                            res_str += f" на {m.get('improvement_percent')}%"
                            
                    results.append(res_str)
                case["result"] = "\n".join(results)
                
            cases.append(case)
            
        out_file = os.path.join(self.output_dir, "cases.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Сгенерировано {len(cases)} кейсов в {out_file}")

        # Генерируем decisions.json на основе lessons_learned
        decisions = []
        for l in knowledge.get("lessons_learned", []):
            decisions.append({
                "title": f"Почему {l.get('tags', ['это'])[0].upper()}?" if l.get('tags') else l.get('title'),
                "subtitle": l.get("title"),
                "description": l.get("description"),
                "category": l.get("category", "Architecture"),
                "tech": [t.split('_')[-1].upper() for t in l.get("technologies", [])]
            })
            
        dec_file = os.path.join(self.output_dir, "decisions.json")
        with open(dec_file, "w", encoding="utf-8") as f:
            json.dump(decisions, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Сгенерировано {len(decisions)} инженерных решений в {dec_file}")

        # Генерируем about.json
        about_data = {
            "summary": knowledge.get("raw_resume_data", {}).get("summary", ""),
            "personal_info": knowledge.get("raw_resume_data", {}).get("personal_info", {}),
            "photo": "",
            "facts": [f.get("description") for f in knowledge.get("extracted_facts", [])]
        }
        
        # Найти фото
        for ev in knowledge.get("evidence", []):
            if "photo" in ev.get("location", "").lower() or "avatar" in ev.get("location", "").lower():
                filename = os.path.basename(ev.get("location"))
                src_loc = os.path.join("c:/projects/portfolio_factory", ev.get("location"))
                if os.path.exists(src_loc):
                    dest_loc = os.path.join(public_media_dir, filename)
                    import shutil
                    shutil.copy2(src_loc, dest_loc)
                    about_data["photo"] = f"/media/{filename}"
                    break
                    
        # Скопировать оригинальный Markdown-текст, чтобы сохранить повествование
        about_md_src = "c:/projects/portfolio_factory/input/about/about.md"
        about_dir = os.path.join("c:/projects/portfolio_factory/portfolio_website/src/pages/about")
        os.makedirs(about_dir, exist_ok=True)
        if os.path.exists(about_md_src):
            shutil.copy2(about_md_src, os.path.join(about_dir, "content.md"))
            
        about_file = os.path.join(self.output_dir, "about.json")
        with open(about_file, "w", encoding="utf-8") as f:
            json.dump(about_data, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Сгенерировано about.json в {about_file}")

        # Генерируем единый feed.json для унифицированной ленты материалов
        feed_items = []
        for c in cases:
            feed_items.append({
                "id": f"case-{c['id']}",
                "type": "case",
                "title": c["title"],
                "summary": c["problem"],
                "content": c["solution"],
                "tags": c.get("tags", []),
                "technologies": c.get("tech", []),
                "media": c.get("images", []),
                "architecture": c.get("architecture")
            })
        for idx, d in enumerate(decisions):
            feed_items.append({
                "id": f"decision-{idx}",
                "type": "decision",
                "title": d["title"],
                "summary": d.get("subtitle", d["title"]),
                "content": d["description"],
                "tags": [d.get("category", "Architecture")],
                "technologies": d.get("tech", []),
                "media": []
            })

        feed_data = {
            "meta": {
                "title": "Инженерное Портфолио",
                "description": "Единая лента проектов, решений и материалов",
                "theme": "dark"
            },
            "profile": {
                "name": about_data.get("personal_info", {}).get("name", "Разработчик"),
                "title": "Software & System Engineer",
                "bio": about_data.get("summary", ""),
                "contacts": {
                    "github": "https://github.com"
                }
            },
            "items": feed_items
        }

        feed_file = os.path.join(self.output_dir, "feed.json")
        with open(feed_file, "w", encoding="utf-8") as f:
            json.dump(feed_data, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Сгенерировано {len(feed_items)} элементов в единой ленте {feed_file}")

if __name__ == "__main__":
    generator = PortfolioGenerator()
    generator.execute()
