import os
import json
import logging
import pytest
from unittest.mock import MagicMock, patch
from agents.context_manager import ContextManagerAgent

# Настройка заглушек для тестирования ИИ-агента
@pytest.fixture
def mock_agent():
    # Мокаем методы чтения YAML-конфигов, чтобы тесты не зависели от физических файлов
    with patch.object(ContextManagerAgent, "_load_yaml") as mock_yaml:
        mock_yaml.side_effect = lambda filename: {
            "settings.yaml": {"system": {"debug": True, "max_retries": 3}},
            "paths.yaml": {
                "paths": {
                    "workspace_root": "c:/projects/portfolio_factory",
                    "input_dir": "tests/test_input",
                    "output_dir": "tests/test_output",
                    "logs_dir": "logs",
                    "schemas_dir": "schemas",
                    "knowledge_file": "tests/test_output/knowledge.json"
                }
            },
            "models.yaml": {
                "agent_routing": {
                    "context_manager": {
                        "provider": "gemini",
                        "model": "gemini-2.5-flash",
                        "temperature": 0.1
                    }
                }
            },
            "agents.yaml": {
                "agents": [
                    {
                        "name": "context_manager",
                        "prompt_file": "prompts/context_manager.md",
                        "system_role": "Test System Role"
                    }
                ]
            }
        }.get(filename, {})
        
        # Создаем экземпляр агента
        agent = ContextManagerAgent()
        # Подменяем директорию ввода-вывода для тестов
        agent.paths["paths"]["input_dir"] = "tests/test_input"
        agent.paths["paths"]["knowledge_file"] = "tests/test_output/knowledge.json"
        
        yield agent

def test_parse_txt_md(tmp_path, mock_agent):
    """Тест парсинга файлов TXT и Markdown."""
    test_file = tmp_path / "test.md"
    content = "# John Doe\nSoftware Engineer"
    test_file.write_text(content, encoding="utf-8")
    
    parsed = mock_agent.parse_txt_md(str(test_file))
    assert parsed == content

def test_parse_json(tmp_path, mock_agent):
    """Тест парсинга JSON файлов."""
    test_file = tmp_path / "test.json"
    data = {"repositories": [{"url": "https://github.com/test/repo"}]}
    test_file.write_text(json.dumps(data), encoding="utf-8")
    
    parsed = mock_agent.parse_json(str(test_file))
    assert parsed == data

@patch("pypdf.PdfReader")
def test_parse_pdf(mock_reader_cls, mock_agent):
    """Тест парсинга PDF-файлов через мок PdfReader."""
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "PDF Text Content"
    mock_reader.pages = [mock_page]
    mock_reader_cls.return_value = mock_reader
    
    parsed = mock_agent.parse_pdf("dummy.pdf")
    assert "PDF Text Content" in parsed

@patch("docx.Document")
def test_parse_docx(mock_doc_cls, mock_agent):
    """Тест парсинга DOCX-файлов через мок Document."""
    mock_doc = MagicMock()
    mock_p1 = MagicMock()
    mock_p1.text = "Paragraph Text"
    mock_doc.paragraphs = [mock_p1]
    
    # Мок таблиц
    mock_table = MagicMock()
    mock_row = MagicMock()
    mock_cell1 = MagicMock()
    mock_cell1.text = "Cell 1"
    mock_cell2 = MagicMock()
    mock_cell2.text = "Cell 2"
    mock_row.cells = [mock_cell1, mock_cell2]
    mock_table.rows = [mock_row]
    mock_doc.tables = [mock_table]
    
    mock_doc_cls.return_value = mock_doc
    
    parsed = mock_agent.parse_docx("dummy.docx")
    assert "Paragraph Text" in parsed
    assert "Cell 1 | Cell 2" in parsed

def test_merge_knowledge_data_no_conflicts(mock_agent):
    """Тест корректного слияния данных базы знаний без конфликтов."""
    base = {
        "raw_resume_data": {
            "personal_info": {"full_name": "Иван Иванов", "email": "ivan@example.com"},
            "skills": ["Python"]
        },
        "repositories": [],
        "extracted_facts": []
    }
    new_data = {
        "raw_resume_data": {
            "personal_info": {"phone": "+79991112233"},
            "skills": ["Go"]
        },
        "repositories": [{"url": "https://github.com/ivan/pyproject", "local_path": ""}]
    }
    
    merged = mock_agent.merge_knowledge_data(base, new_data)
    assert merged["raw_resume_data"]["personal_info"]["full_name"] == "Иван Иванов"
    assert merged["raw_resume_data"]["personal_info"]["email"] == "ivan@example.com"
    assert merged["raw_resume_data"]["personal_info"]["phone"] == "+79991112233"
    assert "Python" in merged["raw_resume_data"]["skills"]
    assert "Go" in merged["raw_resume_data"]["skills"]
    assert len(merged["repositories"]) == 1
    assert merged["repositories"][0]["url"] == "https://github.com/ivan/pyproject"

def test_merge_knowledge_data_with_conflicts(mock_agent):
    """Тест выявления конфликтов при слиянии несовпадающих данных."""
    base = {
        "raw_resume_data": {
            "personal_info": {"email": "ivan@example.com"},
            "summary": "Junior Developer"
        },
        "repositories": [],
        "extracted_facts": []
    }
    new_data = {
        "raw_resume_data": {
            "personal_info": {"email": "ivan.new@example.com"},
            "summary": "Senior Developer"
        }
    }
    
    merged = mock_agent.merge_knowledge_data(base, new_data)
    assert merged["raw_resume_data"]["personal_info"]["email"].startswith("CONFLICT:")
    assert "ivan@example.com" in merged["raw_resume_data"]["personal_info"]["email"]
    assert "ivan.new@example.com" in merged["raw_resume_data"]["personal_info"]["email"]
    assert merged["raw_resume_data"]["summary"].startswith("CONFLICT:")

def test_merge_knowledge_data_facts_conflict(mock_agent):
    """Тест разрешения коллизий идентификаторов фактов."""
    base = {
        "repositories": [],
        "extracted_facts": [
            {"id": "python_exp", "source": "resume", "description": "5 лет опыта разработки"}
        ]
    }
    new_data = {
        "extracted_facts": [
            {"id": "python_exp", "source": "user_input", "description": "3 года опыта"}
        ]
    }
    
    merged = mock_agent.merge_knowledge_data(base, new_data)
    assert len(merged["extracted_facts"]) == 2
    ids = [f["id"] for f in merged["extracted_facts"]]
    assert "python_exp" in ids
    assert "python_exp_conflict" in ids

@patch.object(ContextManagerAgent, "call_llm")
def test_execute_pipeline(mock_call_llm, mock_agent, tmp_path):
    """Сквозной тест работы пайплайна выполнения ContextManager."""
    # Настраиваем временные папки для теста
    test_input_dir = tmp_path / "input"
    test_input_dir.mkdir()
    mock_agent.paths["paths"]["input_dir"] = str(test_input_dir)
    
    test_output_dir = tmp_path / "output"
    test_output_dir.mkdir()
    mock_agent.paths["paths"]["knowledge_file"] = str(test_output_dir / "knowledge.json")
    
    # Создаем тестовые файлы во входной директории
    (test_input_dir / "resume.txt").write_text("Иван Иванов. Опыт работы с Python.", encoding="utf-8")
    (test_input_dir / "repo.json").write_text(json.dumps({
        "repositories": [{"url": "https://github.com/ivan/repo", "local_path": ""}]
    }), encoding="utf-8")
    
    # Задаем ответ LLM на нормализацию
    llm_response = {
        "raw_resume_data": {
            "personal_info": {
                "full_name": "Иван Иванов",
                "target_title": "Python Developer",
                "email": "ivan@example.com"
            },
            "summary": "Разработчик на Python",
            "work_experience": [],
            "education": [],
            "skills": ["Python"]
        },
        "repositories": [],
        "extracted_facts": [
            {"id": "fact_1", "source": "resume", "technology": "Python", "description": "Разработчик на Python"}
        ]
    }
    mock_call_llm.return_value = json.dumps(llm_response)
    
    # Мокаем промпт шаблон
    with patch.object(ContextManagerAgent, "get_prompt_template", return_value="Template {{RAW_EXTRACTED_TEXT}}"):
        result = mock_agent.execute()
        
    assert result["raw_resume_data"]["personal_info"]["full_name"] == "Иван Иванов"
    assert len(result["repositories"]) == 1
    assert result["repositories"][0]["url"] == "https://github.com/ivan/repo"
    assert len(result["extracted_facts"]) == 1  # Только один факт от LLM
    # Проверяем, что файл действительно записан
    assert os.path.exists(mock_agent.paths["paths"]["knowledge_file"])
    with open(mock_agent.paths["paths"]["knowledge_file"], "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert "raw_resume_data" not in saved_data  # raw_resume_data не должен храниться в knowledge.json!
    
    # Проверяем, что сырые данные сохранены в normalized слой
    normalized_file = os.path.join(mock_agent.paths["paths"].get("storage_normalized_dir", "storage/normalized"), "resume.json")
    if not os.path.isabs(normalized_file):
        normalized_file = os.path.join("c:/projects/portfolio_factory", normalized_file)
    assert os.path.exists(normalized_file)
    with open(normalized_file, "r", encoding="utf-8") as f:
        normalized_data = json.load(f)
    assert normalized_data["personal_info"]["full_name"] == "Иван Иванов"
