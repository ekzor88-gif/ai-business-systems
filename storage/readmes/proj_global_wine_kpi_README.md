# Автоматизация аналитики продаж и расчета KPI

![Excel](https://img.shields.io/badge/-Excel-111?style=flat&logo=excel) ![OLAP Cubes](https://img.shields.io/badge/-OLAP%20Cubes-111?style=flat&logo=olap cubes)

> **Status**: Production  
> **Type**: Commercial

## Overview
ETL-процесс подготовки управленческой отчетности, классификация ассортимента и автоматизация расчета мотивации торговой команды на базе OLAP и Excel.

## Architecture & Pipeline

```mermaid
graph TD
    A[Sales Data] --> B[OLAP Cubes]
    B --> C[ETL Process]
    C --> D[SKU Classification Model]
    D --> E[KPI & Motivation Calc]
    E --> F[Unified Excel Report]
```

## Tech Stack
- **Excel**
- **OLAP Cubes**


---
*This README was automatically generated based on the Portfolio Knowledge Graph.*
