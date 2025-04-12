from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import boto3
import io
import os

load_dotenv()

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
TABLE_NAME = "traffic_violations"

def download_from_s3():
    try:
        s3 = boto3.client("s3", 
            aws_access_key_id=AWS_ACCESS_KEY, 
            aws_secret_access_key=AWS_SECRET_KEY
        )
        today = datetime.now()
        first_day_of_current_month = today.replace(day=1)
        last_day_of_prev_month = first_day_of_current_month - timedelta(days=1)
        year = last_day_of_prev_month.year
        month = last_day_of_prev_month.month
        s3_file_path = f"indian-traffic-violations/year={year}/month={month}/data.csv"
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=s3_file_path)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()))
        df.to_csv("/opt/airflow/dags/temp/traffic_violations.csv", index=False)
        print("File downloaded successfully.")
    except Exception as e:
        print(f"Error downloading file: {e}")

def load_to_postgres():
    df = pd.read_csv("/opt/airflow/dags/temp/traffic_violations.csv")
    pg_hook = PostgresHook(postgres_conn_id="postgres_dw")
    engine = pg_hook.get_sqlalchemy_engine()
    df.to_sql(TABLE_NAME, engine, if_exists="append", index=False)

default_args = {"retries": 0}
dag = DAG("s3_to_postgres_pipeline", default_args=default_args, schedule="@monthly", catchup=True)

extract = PythonOperator(task_id="download_from_s3", python_callable=download_from_s3, dag=dag)
load = PythonOperator(task_id="load_to_postgres", python_callable=load_to_postgres, dag=dag)

extract >> load