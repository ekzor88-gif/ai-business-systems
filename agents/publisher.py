import os
import subprocess
import logging
from dotenv import load_dotenv

class PublisherAgent:
    def __init__(self):
        self.logger = logging.getLogger("publisher")
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        
        # Загружаем переменные окружения, переопределяя кэш ОС
        load_dotenv(override=True)
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_url = "github.com/v-artemyev-ai/v-artemyev-ai.github.io.git"
        self.work_dir = "c:/projects/portfolio_factory/portfolio_website"

    def execute(self):
        self.logger.info("Начало работы Publisher Agent...")
        
        if not self.github_token:
            self.logger.error("Ключ GITHUB_TOKEN не найден в .env файле!")
            return False

        if not os.path.exists(self.work_dir):
            self.logger.error(f"Директория сайта {self.work_dir} не найдена!")
            return False

        # Формируем URL с токеном
        remote_url = f"https://x-access-token:{self.github_token}@{self.repo_url}"

        try:
            self._run_cmd(["git", "init"], cwd=self.work_dir)
            
            # Меняем ветку на main
            self._run_cmd(["git", "checkout", "-B", "main"], cwd=self.work_dir)
            
            # Настраиваем пользователя для коммита
            self._run_cmd(["git", "config", "user.name", "Portfolio Factory Bot"], cwd=self.work_dir)
            self._run_cmd(["git", "config", "user.email", "bot@portfolio-factory.local"], cwd=self.work_dir)
            
            # Добавляем все файлы
            self.logger.info("Добавление файлов в индекс git...")
            self._run_cmd(["git", "add", "."], cwd=self.work_dir)
            
            # Коммит
            self.logger.info("Создание коммита...")
            try:
                self._run_cmd(["git", "commit", "-m", "Auto-update portfolio from Engineering Knowledge Base"], cwd=self.work_dir)
            except Exception as e:
                # Коммит может упасть, если нет изменений
                self.logger.warning("Возможно, изменений нет. Ошибка commit: " + str(e))
            
            # Отправка изменений
            self.logger.info("Отправка изменений в GitHub...")
            self._run_cmd(["git", "push", "--force", remote_url, "main"], cwd=self.work_dir)
            
            self.logger.info("Сайт успешно отправлен в GitHub репозиторий!")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при публикации сайта: {e}")
            return False

    def create_pull_request(self, branch_name: str = "update-portfolio-feed") -> bool:
        """Создание ветки с публикацией и подпуш для генерации Pull Request."""
        if not self.github_token:
            self.logger.error("Ключ GITHUB_TOKEN не найден!")
            return False

        remote_url = f"https://x-access-token:{self.github_token}@{self.repo_url}"
        try:
            self._run_cmd(["git", "init"], cwd=self.work_dir)
            self._run_cmd(["git", "checkout", "-B", branch_name], cwd=self.work_dir)
            self._run_cmd(["git", "config", "user.name", "Portfolio Factory Bot"], cwd=self.work_dir)
            self._run_cmd(["git", "config", "user.email", "bot@portfolio-factory.local"], cwd=self.work_dir)
            self._run_cmd(["git", "add", "."], cwd=self.work_dir)
            try:
                self._run_cmd(["git", "commit", "-m", f"feat: portfolio content update ({branch_name})"], cwd=self.work_dir)
            except Exception as e:
                self.logger.warning(f"Нет изменений для коммита в PR ветку: {e}")
            self._run_cmd(["git", "push", "--force", remote_url, branch_name], cwd=self.work_dir)
            self.logger.info(f"Ветка {branch_name} успешно отправлена в GitHub для Pull Request!")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка создания ветки для PR: {e}")
            return False
            
    def _run_cmd(self, cmd_args, cwd):
        """Вспомогательный метод для запуска shell команд."""
        # Убираем вывод токена в логи
        safe_cmd = " ".join([arg if "x-access-token" not in arg else "https://***@github..." for arg in cmd_args])
        self.logger.debug(f"Выполнение команды: {safe_cmd}")
        
        result = subprocess.run(
            cmd_args, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            error_msg = f"Команда завершилась с ошибкой ({result.returncode}):\n{result.stderr}"
            # Убираем токен из сообщения об ошибке
            if self.github_token:
                error_msg = error_msg.replace(self.github_token, "***")
            raise Exception(error_msg)
            
        return result.stdout

if __name__ == "__main__":
    agent = PublisherAgent()
    agent.execute()
