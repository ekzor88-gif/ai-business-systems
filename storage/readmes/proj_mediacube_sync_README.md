# MC PAY -> NAV Integration

![n8n](https://img.shields.io/badge/-n8n-111?style=flat&logo=n8n) ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-111?style=flat&logo=postgresql) ![SOAP Web Services](https://img.shields.io/badge/-SOAP%20Web%20Services-111?style=flat&logo=soap web services) ![XML](https://img.shields.io/badge/-XML-111?style=flat&logo=xml) ![JSON](https://img.shields.io/badge/-JSON-111?style=flat&logo=json)

> **Status**: Production  
> **Type**: Commercial

## Overview
ETL-пайплайн синхронизации биллинговой платформы MC PAY с ERP Microsoft Dynamics NAV. Автоматизация создания контрагентов, идемпотентная обработка, логирование и уведомления.

## Architecture & Pipeline

```mermaid
graph TD
    A[MC PAY PostgreSQL] -->|SQL SELECT| B[n8n Workflow]
    B --> C{Check Vendor Exists?}
    C -->|No| D[SOAP Create Vendor]
    C -->|Yes| E[Skip]
    D --> F[XML to JSON Mapping]
    F --> G[Update Mapping File]
    G --> H[Log & Slack Notification]
    B -->|Error| I[Retry with Batch]
```

## Tech Stack
- **n8n**
- **PostgreSQL**
- **SOAP Web Services**
- **XML**
- **JSON**
- **Slack API**
- **Microsoft Dynamics NAV / Business Central**

## Engineering Decisions & Lessons Learned
### Идемпотентность обязательна для ETL
Идемпотентность является обязательным свойством для любых ETL-процессов, работающих по расписанию. Проверка существования записей по бизнес-идентификатору предотвращает дублирование при повторных запусках.

### SOAP эффективен для корпоративных ERP
SOAP остается эффективным инструментом для интеграции корпоративных ERP-систем и обеспечивает высокую производительность при работе с большими объемами данных.

### UI оркестратора как узкое место
Основным узким местом интеграции может быть не ERP, а инструмент оркестрации или пользовательский интерфейс. При обработке >30 000 записей требуется пакетная обработка.

### Важность тестовой среды
Полноценная тестовая среда значительно снижает риски при внедрении изменений в production. Тестирование в Sandbox-копии ERP обязательно перед публикацией.

### Координация с администраторами ERP
При работе с enterprise-системами важную роль играет взаимодействие с администраторами и поставщиками ERP (настройка доступов, публикация сервисов, изменение конфигурации).

---
*This README was automatically generated based on the Portfolio Knowledge Graph.*
