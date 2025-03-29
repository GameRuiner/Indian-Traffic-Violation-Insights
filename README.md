# Indian Traffic Violation Insights

## Batch data pipeline to data lake

Data pipeline using Apache Airflow to extract, transform, and load (ETL) traffic violation data into an AWS S3-based data lake. The pipeline is orchestrated with Airflow, running in a Dockerized environment.

### Data Flow

1.	Input: A CSV file (Indian_Traffic_Violations.csv) stored in Airflow’s DAG directory.
2.	Processing: Airflow DAG executes three tasks:
    - extract_data: Reads the file and saves it as an intermediate CSV.
    - transform_data: Cleans the data by removing duplicates and NaNs.
    - upload_to_s3: Uploads the final processed file to AWS S3.
3.	Output: The cleaned data is stored in the raw/traffic_violations.csv path in an S3 bucket.

### Airflow DAG

The DAG (traffic_violation_pipeline) automates the ETL process on a daily schedule.

### Docker Setup

The pipeline runs in a Dockerized environment using docker-compose. Key services:
-	PostgreSQL (Metadata database)
-   Redis (Message broker for Celery)
-	Airflow Scheduler & Webserver
-	Airflow Worker (Executes DAG tasks)

### Running the Pipeline

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

### Environment Variables

Set these variables in a .env file:

```
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
BUCKET_NAME=your_bucket_name
```