import json
import os
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

class ReadmeGenerator:
    def __init__(self):
        self.logger = logging.getLogger("readme_generator")
        self.knowledge_path = "c:/projects/portfolio_factory/storage/knowledge/knowledge.json"
        self.output_dir = "c:/projects/portfolio_factory/storage/readmes"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_knowledge(self) -> dict:
        if os.path.exists(self.knowledge_path):
            with open(self.knowledge_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_readme(self, project: dict, knowledge: dict) -> str:
        # Resolve technologies
        techs = []
        for t_id in project.get("technologies", []):
            tech = next((t for t in knowledge.get("technologies", []) if t.get("id") == t_id), None)
            if tech:
                techs.append(tech.get("name"))
        
        # Resolve lessons
        lessons = []
        for l_id in project.get("lessons_learned", []):
            lesson = next((l for l in knowledge.get("lessons_learned", []) if l.get("id") == l_id), None)
            if lesson:
                lessons.append(f"### {lesson.get('title')}\n{lesson.get('description')}")

        badges = " ".join([f"![{t}](https://img.shields.io/badge/-{t.replace(' ', '%20')}-111?style=flat&logo={t.lower()})" for t in techs[:5]])

        readme = f"""# {project.get('name')}

{badges}

> **Status**: {project.get('status', 'Completed').capitalize()}  
> **Type**: {project.get('project_type', 'Commercial').capitalize()}

## Overview
{project.get('description')}

## Architecture & Pipeline

```mermaid
{project.get('architecture', {}).get('diagram_mermaid', 'graph TD\\n  A[System]')}
```

## Tech Stack
"""
        for t in techs:
            readme += f"- **{t}**\n"

        if lessons:
            readme += "\n## Engineering Decisions & Lessons Learned\n"
            readme += "\n\n".join(lessons)

        readme += """

---
*This README was automatically generated based on the Portfolio Knowledge Graph.*
"""
        return readme

    def run(self):
        self.logger.info("Starting README Generator...")
        knowledge = self.load_knowledge()
        projects = knowledge.get("projects", [])
        
        count = 0
        for p in projects:
            readme_content = self.generate_readme(p, knowledge)
            
            # Use project id for filename
            filename = f"{p.get('id')}_README.md"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(readme_content)
            self.logger.info(f"Generated README for {p.get('name')} -> {filename}")
            count += 1
            
        self.logger.info(f"Successfully generated {count} README files.")

if __name__ == "__main__":
    generator = ReadmeGenerator()
    generator.run()
