# SaaS AI-консультант для e-commerce каталога

![Python](https://img.shields.io/badge/-Python-111?style=flat&logo=python) ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-111?style=flat&logo=postgresql) ![pgvector](https://img.shields.io/badge/-pgvector-111?style=flat&logo=pgvector) ![OpenAI API](https://img.shields.io/badge/-OpenAI%20API-111?style=flat&logo=openai api) ![Aiogram 3](https://img.shields.io/badge/-Aiogram%203-111?style=flat&logo=aiogram 3)

> **Status**: Production  
> **Type**: Commercial

## Overview
AI-ассистент для автоматизированной консультации клиентов по каталогу из 370+ SKU. Реализована RAG-система с гибридным семантическим поиском и Telegram-интерфейсом.

## Architecture & Pipeline

```mermaid
graph TD
    A[Telegram User] --> B[Aiogram 3 Bot]
    B --> C[FastAPI Backend]
    C --> D[PostgreSQL + pgvector]
    C --> E[OpenAI API]
    D --> F[Hybrid Semantic Search]
    F --> G[RAG Response Generation]
    G --> B
```

## Tech Stack
- **Python**
- **PostgreSQL**
- **pgvector**
- **OpenAI API**
- **Aiogram 3**
- **FastAPI**


---
*This README was automatically generated based on the Portfolio Knowledge Graph.*
