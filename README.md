# Zomato AI Data Engineering End-to-End Project

An end-to-end data engineering project that processes Zomato-like restaurant, customer, order, and review data using **Amazon S3, Apache Airflow, dbt, Snowflake, Python, SQL, and AI-powered analytics**.

The project demonstrates a complete data pipeline — from raw data ingestion and cloud storage to transformation, dimensional modeling, data warehousing, and AI-driven analytics.

---

## 🚀 Project Overview

This project is designed as a production-style data engineering pipeline for processing large-scale food delivery data.

The pipeline:

- Stores raw data in **Amazon S3**
- Uses **Apache Airflow** for workflow orchestration
- Uses **dbt** for data transformation and modeling
- Uses **Snowflake** as the analytical data warehouse
- Implements **staging and mart layers**
- Performs dimensional modeling for analytical workloads
- Enriches customer reviews using AI
- Generates review embeddings for semantic analysis
- Supports **Natural Language → SQL** querying
- Provides an AI/RAG-based interface for interacting with the data

---

## 🏗️ Architecture

```text
                         RAW DATA
                            │
                            ▼
                    ┌───────────────┐
                    │   Amazon S3   │
                    │  Raw Storage  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Apache Airflow│
                    │ Orchestration │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   dbt         │
                    │   Staging     │
                    │ Transformation│
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   dbt Marts   │
                    │ Dimensional   │
                    │   Modeling    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Snowflake   │
                    │ Data Warehouse│
                    └───────┬───────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
        ┌─────────────────┐    ┌──────────────────┐
        │    Analytics    │    │   AI Analytics   │
        │  & SQL Queries  │    │ RAG / Text-to-SQL│
        └─────────────────┘    └──────────────────┘

✨ Key Features
1. Cloud Data Storage

Raw Zomato datasets are stored in Amazon S3, providing centralized cloud-based storage for the pipeline.

2. Workflow Orchestration

Apache Airflow is used to automate and orchestrate the pipeline through scheduled DAGs.

The pipeline coordinates tasks such as:

Raw data loading
Data processing
dbt transformations
AI-based review enrichment
Downstream analytical processing
3. Data Transformation with dbt

The project uses dbt to transform raw data into clean, analytics-ready datasets.

The dbt project follows a layered architecture:

Raw Data
   │
   ▼
Staging Layer
   │
   ▼
Mart Layer
   │
   ▼
Analytics
4. Dimensional Data Modeling

The mart layer contains analytical dimensions and fact tables for business-oriented analysis.

Examples include:

Customer dimension
Date dimension
Food dimension
Restaurant dimension
Orders fact
Order items fact
Restaurant performance
Delivery SLA
Review insights
Daily city-level revenue
5. Snowflake Data Warehouse

Snowflake is used as the centralized analytical warehouse for storing transformed data and supporting SQL-based analytics.

6. AI-Powered Review Analytics

Customer reviews are processed using AI-based workflows for enrichment and semantic analysis.

The project also generates embeddings that can be used for semantic search and AI-powered retrieval.

7. Natural Language → SQL

The project includes a Text-to-SQL workflow that allows users to ask analytical questions in natural language and generate SQL queries against the warehouse.

Example:

"Which restaurants generated the highest revenue last month?"

The system can translate the question into a SQL query that can be executed against the analytical data.

8. RAG-Based Data Interaction

The project includes an AI/RAG workflow for interacting with the processed review and analytical data using natural language.

🛠️ Tech Stack
Category	Technologies
Cloud Storage	Amazon S3
Orchestration	Apache Airflow
Transformation	dbt
Data Warehouse	Snowflake
Programming	Python
Query Language	SQL
AI / NLP	LLMs, Embeddings, RAG, Text-to-SQL
Containerization	Docker
Data Formats	CSV, Parquet
Version Control	Git, GitHub
📊 Dataset

The project uses Zomato-like datasets containing information about:

Customers / Users
Restaurants
Food items
Menus
Orders
Order items
Customer reviews

The raw dataset is not included in this GitHub repository because of its large size.

Download Dataset
https://drive.google.com/drive/folders/1kB2wxjqDvITE1_lh5tIP_SB22vISKOHo?usp=drive_link

After downloading the dataset, place the CSV files inside the project's Data/ directory:

Data/
├── food.csv
├── menu.csv
├── order_items.csv
├── orders.csv
├── restaurant.csv
├── reviews.csv
└── users.csv
📁 Project Structure
ZOMATO_DATA_PIPELINE/
│
├── README.md
├── .gitignore
│
├── ai/
│   ├── enrich_reviews.py
│   ├── rag_chat.py
│   ├── text_to_sql.py
│   ├── .env.example
│   └── ...
│
├── airflow/
│   ├── dags/
│   │   └── zomato_batch.py
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   ├── .env.example
│   └── ...
│
├── zomato/
│   ├── analyses/
│   ├── macros/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── seeds/
│   ├── snapshots/
│   ├── tests/
│   ├── dbt_project.yml
│   └── profiles.yml
│
└── Data/
    └── Raw CSV files
🧩 dbt Models
Staging Models

The staging layer cleans and standardizes source data before it reaches the analytical layer.

staging/
├── stg_food.sql
├── stg_menu.sql
├── stg_order_items.sql
├── stg_orders.sql
├── stg_restaurants.sql
├── stg_reviews.sql
└── stg_users.sql
Mart Models

The mart layer contains business-ready analytical models.

marts/
├── dim_customer.sql
├── dim_date.sql
├── dim_food.sql
├── dim_restaurants.sql
├── fact_order_items.sql
├── fct_orders.sql
├── mart_daily_city_revenue.sql
├── mart_delivery_sla.sql
├── mart_restaurant_performance.sql
└── mart_review_insights.sql
⚙️ Pipeline Workflow

The overall workflow can be summarized as:

Raw Zomato Data
       │
       ▼
   Amazon S3
       │
       ▼
 Apache Airflow
       │
       ├───────────────┐
       │               │
       ▼               ▼
    dbt Build      AI Processing
       │               │
       ▼               ▼
 Staging Models   Review Enrichment
       │               │
       ▼               ▼
   Mart Models     Embeddings
       │               │
       └───────┬───────┘
               ▼
          Snowflake
               │
       ┌───────┴────────┐
       ▼                ▼
   SQL Analytics    AI Analytics
                         │
                  ┌──────┴──────┐
                  ▼             ▼
                RAG         Text-to-SQL


🔐 Environment Variables

Sensitive credentials and API keys are not stored in this repository.

Environment variables are provided through example files:

ai/.env.example
airflow/.env.example

Create your local .env files using these examples and add your actual credentials.

Typical configuration includes:

SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_PASSWORD
SNOWFLAKE_DATABASE
SNOWFLAKE_WAREHOUSE
API_KEYS

Never commit real passwords, API keys, or cloud credentials to GitHub.

🐳 Docker

The Airflow environment is containerized using Docker.

The project includes:

airflow/
├── Dockerfile
└── docker-compose.yaml

Docker Compose can be used to start the Airflow environment and its required services.

▶️ Getting Started
1. Clone the repository
git clone https://github.com/MohdKaif04/zomato-ai-data-engineering-end-to-end-project.git
cd zomato-ai-data-engineering-end-to-end-project
2. Download the dataset

Zomato Dataset

Place the CSV files inside:

Data/
3. Configure environment variables

Create the required .env files using:

ai/.env.example
airflow/.env.example

Add your own credentials locally.

4. Start Airflow

From the Airflow directory:

docker compose up -d
5. Run dbt

Navigate to the dbt project:

cd zomato

Then run the required dbt commands:

dbt deps
dbt debug
dbt run
6. Run AI Components

The AI workflows can be executed from the ai/ directory depending on the configured environment.

📈 Analytical Use Cases

The transformed data can support analytical questions such as:

Which restaurants generate the highest revenue?
Which cities have the highest order volume?
What are the most popular food items?
Which restaurants have the best delivery performance?
What is the average order value?
Which restaurants receive the most positive reviews?
What are the major themes in customer reviews?
Which restaurants are experiencing poor customer sentiment?

These analytical workloads can be extended through the AI Text-to-SQL and RAG workflows.

🔮 Future Improvements
Add automated data quality monitoring
Implement more incremental dbt models
Add CI/CD for dbt and Airflow
Add BI dashboards using Power BI or Tableau
Improve Text-to-SQL query validation
Add automated pipeline failure notifications
Add comprehensive unit and data tests
Introduce infrastructure-as-code for cloud resources

## 👨‍💻 Author

**Mohd Kaif**  
B.Tech Data Science

🔗 **GitHub:** [MohdKaif04](https://github.com/MohdKaif04)

---

## ⭐ Project

If you found this project useful or interesting, consider giving the repository a ⭐..


### Ek cheez main deliberately nahi kar raha

README mein **fake claims** nahi daale hain—for example "production-ready", "millions of records", "highly scalable", "real-time pipeline" etc. Jab tak tumne actually implement nahi kiya, aise claims recruiter ke technical interview mein ulte pad sakte hain.

Aur **S3 → Airflow → dbt → Snowflake** architecture tabhi exactly aise present karo agar tumhare actual DAG/pipeline
