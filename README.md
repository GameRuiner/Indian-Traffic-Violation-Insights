# 🚦 Indian traffic violation insights

## 🤔 Problem description

Traffic violations are a significant issue in India, contributing to road congestion, accidents, and safety risks. With a vast number of violations recorded daily, analyzing this data is crucial for identifying patterns, improving law enforcement strategies, and enhancing road safety measures.

However, raw traffic violation data is often complex, scattered, and difficult to interpret. Decision-makers, policymakers, and analysts need clear insights to understand:
-   Common types of violations (e.g., speeding, signal jumping, illegal parking)
-   Violation trends over time (e.g., seasonal or regional patterns)

This project processes and visualizes Indian traffic violation data, providing actionable insights through a structured BI dashboard.

## 🛠️ Infrastructure as Code (IaC)

This project uses Terraform to provision and manage AWS resources, including an RDS PostgreSQL database, an S3 data lake, and a security group for database access.

## Terraform setup & deployment

### 1️⃣ Define variables

Sensitive credentials (e.g., database username and password) are stored in terraform.tfvars, which is gitignored for security.

These variables are declared in variables.tf.

### 2️⃣ AWS credentials setup

Terraform uses AWS credentials configured via:

```sh
aws configure
```

### 3️⃣ Plan & apply

To preview changes before applying:

```sh
terraform plan -var-file="terraform.tfvars"
```

To apply the infrastructure:
```sh
terraform apply -var-file="terraform.tfvars"
```

## Batch data pipeline to data lake

Data pipeline using Apache Airflow to extract, transform, and load (ETL) traffic violation data into an AWS S3-based data lake. The pipeline is orchestrated with Airflow, running in a Dockerized environment.

### 📈 Data flow

1.	Input: dataset is downloaded from Kaggle using kagglehub.
2.	Processing: Airflow DAG executes three tasks:
    - extract_data: Reads the raw CSV and saves a filtered copy for the previous month
    - transform_data: Cleans the data by removing duplicates and missing values.
    - upload_to_s3: Uploads the processed file to an S3 bucket with a dynamic path based on year/month.
3.	Output: The cleaned dataset is uploaded to an S3 bucket using a structured path.

### 📅 Scheduling

- The DAG runs monthly (@monthly), always processing data for the previous calendar month.

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

Once data is stored in the data lake (S3), the next step is to load it into a Data Warehouse (PostgreSQL) for efficient querying and dashboarding.

### Data flow

#### 1. Extract
The pipeline downloads the latest processed file (monthly) from S3 into the Airflow environment.
#### 2. Load 
The CSV data is loaded into a traffic_violations table in PostgreSQL using SQLAlchemy. The table is automatically created on the first run.
#### 3.	Materialized Views
After loading, two materialized views are created (if not already present) for analytical use:
- mv_violation_type_summary: summarizes violation counts by Violation_Type.
- mv_date_summary: summarizes violation counts by Date.
These views are refreshed on every DAG run to stay up-to-date with new data.
#### 3. Schedule
The entire pipeline is orchestrated using Apache Airflow, scheduled to run monthly with @monthly frequency.

### Running the data warehouse pipeline

1. Trigger the DAG manually (optional):

```sh
docker exec -it airflow-webserver airflow dags trigger s3_to_postgres_pipeline
```

2. Verify the data in PostgreSQL:
```sh
docker exec -it db psql -U postgres -d db -c "SELECT COUNT(*) FROM traffic_violations;"
```

## Transformations

Data prepared for dashboard in the data warehouse. Data transformed with simple SQL transformation (no dbt or similar tools were used). Two materialized view were created, tied to DB with refresh logic.

## 📊 Dashboard

To effectively visualize and analyze the processed data, I evaluated several Business Intelligence (BI) tools for their compatibility with PostgreSQL and ease of use. Here’s a summary of the findings:

1. Power BI – is limited to Windows environments, reducing cross-platform flexibility.
2. Tableau – the free public version does not support PostgreSQL as a data source, which makes it unsuitable for this use case.
3. Looker Studio (formerly Google Data Studio) – despite Airflow being able to connect to PostgreSQL successfully, Looker repeatedly failed to connect. Eventually, it began showing persistent “Server failed” errors.
4. Metabase - subscription price starts at $85/month, which is too costly for a single public dashboard.
5. Amazon QuickSight – the most practical option in this case. It’s cloud-based, supports many data sources (including PostgreSQL) in its free tier, and integrates easily with AWS services. However, dashboards cannot be made public, so insights are exported as a PDF report (insights.pdf) instead.

If you’re willing to pay for a subscription to make a dashboard public, that’s your choice — but in my opinion, exporting the dashboard to a PDF file is more than enough to demonstrate the concept effectively.

## 🔧 Tech stack summary

- **IaC tool**: Terraform

- **Data lake**: AWS S3

- **Data warehouse**: PostgreSQL

- **ETL pipeline**: Apache Airflow 

- **Dashboard**: QuickSight