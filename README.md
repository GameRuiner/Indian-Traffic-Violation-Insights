# Indian traffic violation insights

## Problem description

Traffic violations are a significant issue in India, contributing to road congestion, accidents, and safety risks. With a vast number of violations recorded daily, analyzing this data is crucial for identifying patterns, improving law enforcement strategies, and enhancing road safety measures.

However, raw traffic violation data is often complex, scattered, and difficult to interpret. Decision-makers, policymakers, and analysts need clear insights to understand:
-   Common types of violations (e.g., speeding, signal jumping, illegal parking)
-   Violation trends over time (e.g., seasonal or regional patterns)

This project processes and visualizes Indian traffic violation data, providing actionable insights through a structured BI dashboard.

## Batch data pipeline to data lake

Data pipeline using Apache Airflow to extract, transform, and load (ETL) traffic violation data into an AWS S3-based data lake. The pipeline is orchestrated with Airflow, running in a Dockerized environment.

### Data flow

1.	Input: A CSV file (Indian_Traffic_Violations.csv) stored in Airflow’s DAG directory.
2.	Processing: Airflow DAG executes three tasks:
    - extract_data: Reads the file and saves it as an intermediate CSV.
    - transform_data: Cleans the data by removing duplicates and NaNs.
    - upload_to_s3: Uploads the final processed file to AWS S3.
3.	Output: The cleaned data is stored in the raw/traffic_violations.csv path in an S3 bucket.

### Airflow DAG

The DAG (traffic_violation_pipeline) automates the ETL process on a daily schedule.

### Docker setup

The pipeline runs in a Dockerized environment using docker-compose. Key services:
-	PostgreSQL (Metadata database)
-   Redis (Message broker for Celery)
-	Airflow Scheduler & Webserver
-	Airflow Worker (Executes DAG tasks)

### Running the pipeline

1.	Start Services:
```sh
docker-compose up -d
```

2.	Access Airflow UI:

Open http://localhost:8080 and log in with:

```
Username: airflow
Password: airflow
```

3.	Trigger DAG Manually (Optional):

```sh
docker exec -it airflow-webserver airflow dags trigger traffic_violation_pipeline
```

### Environment variables

Set these variables in a .env file:

```
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
BUCKET_NAME=your_bucket_name
```

## Moving data from the lake to a data warehouse

Once data is stored in the data lake (S3), the next step is to load it into a Data Warehouse (PostgreSQL) for further analysis and querying.

### Data flow

1. Extract: Download data from S3.
2. Load: Insert data into a PostgreSQL table.
3. Schedule: Automate the process using Apache Airflow.

### Running the data warehouse pipeline

1. Trigger the DAG manually (optional):

```sh
docker exec -it airflow-webserver airflow dags trigger s3_to_postgres_pipeline
```

2. Verify the data in PostgreSQL:
```sh
docker exec -it db psql -U postgres -d db -c "SELECT COUNT(*) FROM traffic_violations;"
```

## Dashboard

To visualize and analyze data effectively, I researched various Business Intelligence (BI) tools and their compatibility with PostgreSQL. Below are my findings:

1. Power BI – works only on Windows, limiting cross-platform accessibility.
2. Tableau – the free public version does not support PostgreSQL as a data source.
3. Looker – unable to connect to PostgreSQL, despite my Airflow DAG successfully doing so.
4. Amazon QuickSight – the best option for my use case. It is cloud-based, supports multiple data sources (including PostgreSQL) even in the free version. However, a limitation is that dashboards cannot be made public, so insights are exported as a PDF file named insights.pdf.

## 🔧 Tech stack summary

- **Data Lake**: AWS S3

- **Data Warehouse**: PostgreSQL

- **ETL Pipeline**: Apache Airflow 

- **Dashboard**: QuickSight