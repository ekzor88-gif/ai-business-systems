import os
import logging
import yaml
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import jsonschema
import dotenv

class BaseAgent(ABC):
    """
    Базовый абстрактный класс для всех ИИ-агентов платформы Portfolio Factory.
    Обеспечивает загрузку конфигурации, логирование и базовые утилиты работы с LLM.
    """
    def __init__(self, agent_name: str):
        dotenv.load_dotenv(override=True)
        self.agent_name = agent_name
        self.config_dir = "config"
        self.settings = self._load_yaml("settings.yaml")
        self.paths = self._load_yaml("paths.yaml")
        self.models_config = self._load_yaml("models.yaml")
        self.agents_config = self._load_yaml("agents.yaml")
        
        self.logger = self._setup_logging()
        self.logger.info(f"Агент {self.agent_name} успешно инициализирован.")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Вспомогательный метод для загрузки конфигурационных файлов YAML."""
        path = os.path.join(self.config_dir, filename)
        if not os.path.exists(path):
            # Попытка найти относительно корня проекта
            path = os.path.join("c:/projects/portfolio_factory", self.config_dir, filename)
        
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Ошибка загрузки YAML {filename}: {e}")
            return {}

    def _setup_logging(self) -> logging.Logger:
        """Настройка логирования для конкретного агента."""
        log_dir = self.paths.get("paths", {}).get("logs_dir", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        logger = logging.getLogger(self.agent_name)
        logger.setLevel(logging.DEBUG if self.settings.get("system", {}).get("debug", False) else logging.INFO)
        
        # Предотвращение дублирования логов при повторной инициализации
        if not logger.handlers:
            log_file = os.path.join(log_dir, f"{self.agent_name}.log")
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Также выводим в консоль для отладки
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
        return logger

    def validate_data(self, data: Dict[str, Any], schema_name: str) -> bool:
        """Валидирует переданные данные по JSON-схеме из папки schemas/."""
        schemas_dir = self.paths.get("paths", {}).get("schemas_dir", "schemas")
        schema_path = os.path.join(schemas_dir, schema_name)
        if not os.path.exists(schema_path):
            schema_path = os.path.join("c:/projects/portfolio_factory", schemas_dir, schema_name)
            
        if not os.path.exists(schema_path):
            self.logger.error(f"Схема {schema_name} не найдена по пути {schema_path}")
            return False
            
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            jsonschema.validate(instance=data, schema=schema)
            self.logger.info(f"Данные успешно валидированы по схеме {schema_name}")
            return True
        except jsonschema.exceptions.ValidationError as ve:
            self.logger.error(f"Ошибка валидации по схеме {schema_name}: {ve.message}")
            return False
        except Exception as e:
            self.logger.error(f"Непредвиденная ошибка при валидации схемы {schema_name}: {e}")
            return False

    def get_agent_routing(self) -> Dict[str, Any]:
        """Возвращает параметры маршрутизации моделей для текущего агента."""
        routing = self.models_config.get("agent_routing", {}).get(self.agent_name, {})
        if not routing:
            # Дефолтные параметры
            routing = {
                "provider": "gemini",
                "model": "gemini-2.5-flash",
                "temperature": 0.2
            }
        return routing

    def get_system_role(self) -> str:
        """Получает системную роль агента из agents.yaml."""
        agents_list = self.agents_config.get("agents", [])
        for agent in agents_list:
            if agent.get("name") == self.agent_name:
                return agent.get("system_role", "")
        return ""

    def get_prompt_template(self) -> str:
        """Считывает шаблон промпта из prompts/."""
        prompts_dir = self.paths.get("paths", {}).get("prompts_dir", "prompts")
        prompt_file = f"{self.agent_name}.md"
        path = os.path.join(prompts_dir, prompt_file)
        if not os.path.exists(path):
            path = os.path.join("c:/projects/portfolio_factory", prompts_dir, prompt_file)
            
        if not os.path.exists(path):
            self.logger.warning(f"Шаблон промпта {prompt_file} не найден.")
            return ""
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Ошибка чтения шаблона промпта {prompt_file}: {e}")
            return ""

    def call_llm(self, prompt: str, system_role: Optional[str] = None) -> str:
        """
        Метод обращения к LLM. Реализует интеграцию с установленными SDK (Gemini, OpenAI, Anthropic)
        в зависимости от конфигурации маршрутизации моделей.
        """
        routing = self.get_agent_routing()
        provider = routing.get("provider", "gemini")
        model = routing.get("model")
        temp = routing.get("temperature", 0.2)
        sys_role = system_role or self.get_system_role()

        self.logger.info(f"Обращение к LLM ({provider}/{model}) с температурой {temp}")
        
        # Получаем API ключи из окружения
        gemini_key = os.environ.get("GEMINI_API_KEY")
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("QWEN_API_KEY")
        openai_base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("QWEN_BASE_URL")

        try:
            if provider == "openai" and openai_key:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key, base_url=openai_base_url)
                messages = []
                if sys_role:
                    messages.append({"role": "system", "content": sys_role})
                messages.append({"role": "user", "content": prompt})
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temp
                )
                return response.choices[0].message.content.strip()

            elif provider == "openrouter" and openrouter_key:
                from openai import OpenAI
                client = OpenAI(
                    api_key=openrouter_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                messages = []
                if sys_role:
                    messages.append({"role": "system", "content": sys_role})
                messages.append({"role": "user", "content": prompt})
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temp,
                    extra_headers={
                        "HTTP-Referer": "https://portfolio-factory.local",
                        "X-Title": "Portfolio Factory"
                    }
                )
                return response.choices[0].message.content.strip()

            elif provider == "gemini" and gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                llm_model = genai.GenerativeModel(
                    model_name=model,
                    generation_config={"temperature": temp},
                    system_instruction=sys_role if sys_role else None
                )
                response = llm_model.generate_content(prompt)
                return response.text.strip()

            else:
                self.logger.warning(
                    f"API ключ для провайдера '{provider}' отсутствует. Пробуем резервный OpenRouter fallback..."
                )
                return self._call_openrouter_fallback(prompt, sys_role, temp)

        except Exception as primary_error:
            self.logger.warning(f"Основной провайдер {provider} вернул ошибку: {primary_error}. Переключаемся на резервный OpenRouter...")
            if openrouter_key:
                try:
                    return self._call_openrouter_fallback(prompt, sys_role, temp)
                except Exception as fb_error:
                    self.logger.error(f"Резервный OpenRouter также вернул ошибку: {fb_error}")
            
            return self._get_mock_response(self.agent_name, prompt)

    def _call_openrouter_fallback(self, prompt: str, sys_role: Optional[str], temp: float) -> str:
        """Резервный вызов бесплатных моделей OpenRouter при недоступности основной модели."""
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        if not openrouter_key:
            return self._get_mock_response(self.agent_name, prompt)

        from openai import OpenAI
        client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        messages = []
        if sys_role:
            messages.append({"role": "system", "content": sys_role})
        messages.append({"role": "user", "content": prompt})

        # Использование авто-роутера бесплатных моделей OpenRouter
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            temperature=temp,
            extra_headers={
                "HTTP-Referer": "https://portfolio-factory.local",
                "X-Title": "Portfolio Factory"
            }
        )
        return response.choices[0].message.content.strip()

    def _get_mock_response(self, agent_name: str, prompt: str) -> str:
        """Возвращает мок-ответ при отсутствии ключей API (для тестирования)."""
        if "JSON" in prompt or "json" in prompt:
            if agent_name == "context_manager":
                return json.dumps({
                    "repositories": [],
                    "extracted_facts": [
                        {
                            "id": "mock_python_fact",
                            "source": "resume",
                            "technology": "Python",
                            "description": "Более 5 лет опыта разработки серверных приложений на Python."
                        }
                    ]
                })
        return "Мок-ответ ИИ"

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Основной метод запуска работы агента."""
        pass
