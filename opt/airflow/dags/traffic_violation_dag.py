import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import os
import traceback
import kagglehub
import boto3
from airflow import DAG
from airflow.operators.python import PythonOperator

load_dotenv()

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

def extract_data():
    path = kagglehub.dataset_download("khushikyad001/indian-traffic-violation")
    df = pd.read_csv(f"{path}/Indian_Traffic_Violations.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    first_day_of_current_month = datetime.now().replace(day=1)
    last_day_of_prev_month = first_day_of_current_month - timedelta(days=1)
    prev_month = last_day_of_prev_month.month
    prev_year = last_day_of_prev_month.year
    df_prev_month = df[(df['Date'].dt.month == prev_month) & (df['Date'].dt.year == prev_year)]
    df_prev_month.to_csv("/opt/airflow/dags/temp/extracted.csv", index=False)

def transform_data():
    df = pd.read_csv("./opt/airflow/dags/temp/extracted.csv")
    df = df.drop_duplicates().dropna()
    df.to_csv("./opt/airflow/dags/temp/cleaned.csv", index=False)

def upload_to_s3(**context):
    try:
        file_path = "/opt/airflow/dags/temp/cleaned.csv"
        logging.info(f"Attempting to upload file: {file_path}")
        logging.info(f"Current working directory: {os.getcwd()}")
        abs_file_path = os.path.abspath(file_path)
        logging.info(f"Absolute file path: {abs_file_path}")
        if not os.path.exists(abs_file_path):
            logging.error(f"File does not exist: {abs_file_path}")
            logging.error(f"Directory contents: {os.listdir(os.path.dirname(abs_file_path))}")
            raise FileNotFoundError(f"File not found: {abs_file_path}")
        file_size = os.path.getsize(abs_file_path)
        logging.info(f"Confirmed file size: {file_size} bytes")
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
        logging.info(f"Uploading to bucket: {BUCKET_NAME}")
        logging.info(f"S3 destination path: {s3_file_path}")
        s3.upload_file(abs_file_path, BUCKET_NAME, s3_file_path)
        logging.info(f"Successfully uploaded {abs_file_path} to {BUCKET_NAME}/{s3_file_path}")
    except Exception as e:
        logging.error(f"Upload error: {e}")
        logging.error(traceback.format_exc())
        raise

default_args = {
    "max_active_runs": 1, 
    "retries": 0,
    "start_date": datetime(2023, 1, 1),
}
dag = DAG("traffic_violation_pipeline", default_args=default_args, schedule_interval='@monthly', catchup=True)

task_extract = PythonOperator(task_id="extract_data", python_callable=extract_data, dag=dag)
task_transform = PythonOperator(task_id="transform_data", python_callable=transform_data, dag=dag)
task_upload = PythonOperator(
    task_id="upload_to_s3", 
    python_callable=upload_to_s3, 
    dag=dag, 
    retries=0,
    retry_delay=timedelta(seconds=0),
    max_retry_delay=timedelta(seconds=0)
)

task_extract >> task_transform >> task_upload