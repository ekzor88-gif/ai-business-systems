import json
from unittest.mock import patch
from agents.reviewer import ReviewerAgent

@patch.object(ReviewerAgent, "_load_yaml")
def test_reviewer_audit(mock_yaml, tmp_path):
    mock_yaml.side_effect = lambda filename: {
        "settings.yaml": {"system": {"debug": True}},
        "paths.yaml": {"paths": {"logs_dir": "logs", "schemas_dir": "schemas"}},
        "models.yaml": {},
        "agents.yaml": {}
    }.get(filename, {})

    knowledge_file = tmp_path / "knowledge.json"
    knowledge_file.write_text(json.dumps({
        "technologies": [{"id": "t1", "name": "Python"}, {"id": "t2", "name": "Astro"}]
    }), encoding="utf-8")

    feed_data = {
        "meta": {
            "title": "Portfolio Feed",
            "description": "Engineering Portfolio",
            "theme": "dark"
        },
        "profile": {
            "name": "Dev",
            "title": "Engineer",
            "bio": "Bio",
            "contacts": {"github": "https://github.com/test"}
        },
        "items": [
            {
                "id": "item-1",
                "type": "case",
                "title": "Case 1",
                "summary": "Summary of case 1",
                "content": "Full text of case 1",
                "tags": ["Python"],
                "technologies": ["Python", "Astro"]
            }
        ]
    }

    agent = ReviewerAgent()
    report = agent.audit_portfolio_feed(feed_data, json.loads(knowledge_file.read_text(encoding="utf-8")))

    assert report.is_approved is True
    assert report.score >= 0.8
    assert len(report.issues) == 0
