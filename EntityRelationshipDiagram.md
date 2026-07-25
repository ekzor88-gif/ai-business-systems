# Схема Сущностей и Связей (Entity Relationship Diagram)

В данном документе приведена диаграмма сущностей и связей новой **Инженерной базы знаний (Engineering Knowledge Base)** платформы **Portfolio Factory**.

---

## 1. ER-диаграмма связей графа знаний

Связи в графе знаний построены на основе ссылочной целостности по уникальным идентификаторам (IDs). Каждое ребро графа направлено и отражает логическую подчиненность или владение.

```mermaid
erDiagram
    Person ||--o{ Experience : has_experience
    Person ||--o{ Skill : possesses_skill
    Experience ||--o{ Project : includes_project
    Project ||--o{ Fact : produces_fact
    Project ||--o{ Repository : has_repository
    Project ||--o{ Lesson : learns_lesson
    Project ||--o{ Decision : records_decision
    Fact ||--o| Metric : measures_with
    Fact }o--o{ Technology : uses_technology
    Skill ||--|| Technology : evaluates
    Repository ||--o{ Technology : references
    Fact ||--o{ Evidence : proven_by
    Skill ||--o{ Evidence : backed_by
    Project ||--o{ Evidence : backed_by
    Experience ||--o{ Evidence : proven_by
    Lesson }o--o{ Technology : relates_to
    Decision }o--o{ Technology : involves_tech
```

---

## 2. Спецификация вершин графа (Сущностей)

### 2.1. Группа Профиля
*   `Person`: Агрегирует ФИО, контакты, саммари и общие метаданные кандидата.
*   `Experience`: Модель стажа работы (компания, должность, даты начала/окончания). Ссылается на проекты через список `projects` (внешний ключ).
*   `Skill`: Количественная оценка (уровень владения, стаж, даты использования) кандидата в рамках конкретной `Technology`.

### 2.2. Группа Разработки и Реализации
*   `Project`: Самостоятельный объект проекта. Хранит описание, роль, стек, архитектурные диаграммы и списки ссылок на факты, уроки, решения и коммиты.
*   `Repository`: Отражает характеристики репозитория на GitHub (языки, фреймворки, звезды, видимость, файл README).
*   `Technology`: Глобальный справочник библиотек и языков (FastAPI, pgvector). Содержит ссылки на документацию и вендора.

### 2.3. Группа Метрик и Доказательств
*   `Fact`: Конкретное атомарное достижение (например, «Внедрение идемпотентного ETL»). Ссылается на задействованные технологии, метрики и доказательства.
*   `Metric`: Структурированная сущность количественного сравнения параметров «до» и «после» оптимизации.
*   `Evidence`: Ссылка на вещественное доказательство существования опыта (номера строк кода в файле Git-репозитория, хэш коммита, сертификат PDF).

### 2.4. Группа Знаний и Решений
*   `Lesson`: Извлеченный инженерный урок (категория, проблема, решение, связи с технологиями).
*   `Decision`: Архитектурное решение (почему был выбран SOAP вместо REST, компромиссы, последствия).
