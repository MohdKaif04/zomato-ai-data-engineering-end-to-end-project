# Zomato AI Data Engineering End-to-End Project

An end-to-end data engineering project built around Zomato-like restaurant data, combining **Airflow orchestration**, **dbt transformations**, **Snowflake warehousing**, **dimensional modeling**, and **AI-powered analytics** for reviews and natural-language querying.

## Project Highlights

- Automated data ingestion and orchestration with **Apache Airflow**
- Data transformation and modeling with **dbt**
- Warehousing and analytics on **Snowflake**
- Dimensional warehouse design with **staging** and **mart** layers
- AI-based review enrichment and embeddings
- Natural-language to SQL workflow for analytics queries
- End-to-end pipeline built for structured and semi-structured restaurant data

## Tech Stack

- **Orchestration:** Apache Airflow
- **Transformations:** dbt
- **Warehouse:** Snowflake
- **Programming:** Python, SQL
- **AI / NLP:** embeddings, LLM-based review processing, text-to-SQL
- **Storage / Input Data:** CSV-based source data
- **Version Control:** Git, GitHub

## Architecture Overview

```text
Raw Data (CSV)
      ↓
Airflow DAGs
      ↓
Staging Models (dbt)
      ↓
Marts / Dimensional Models (dbt)
      ↓
Snowflake
      ↓
Analytics / AI Insights / Text-to-SQL
