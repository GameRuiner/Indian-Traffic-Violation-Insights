import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import boto3
import os
import traceback

load_dotenv()

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
S3_FILE_PATH = os.environ.get("S3_FILE_PATH")

LOCAL_FILE_PATH = "/opt/airflow/dags/files/Indian_Traffic_Violations.csv"

def extract_data():
    df = pd.read_csv(LOCAL_FILE_PATH)
    df.to_csv("/opt/airflow/dags/temp/extracted.csv", index=False)

def transform_data():
    df = pd.read_csv("/opt/airflow/dags/temp/extracted.csv")
    df = df.drop_duplicates().dropna()
    df.to_csv("/opt/airflow/dags/temp/cleaned.csv", index=False)

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
        logging.info(f"Uploading to bucket: {BUCKET_NAME}")
        logging.info(f"S3 destination path: {S3_FILE_PATH}")
        s3.upload_file(abs_file_path, BUCKET_NAME, S3_FILE_PATH)
        logging.info(f"Successfully uploaded {abs_file_path} to {BUCKET_NAME}/{S3_FILE_PATH}")
    except Exception as e:
        logging.error(f"Upload error: {e}")
        logging.error(traceback.format_exc())
        raise


default_args = {"start_date": datetime(2025, 2, 27), "max_active_runs": 1, "retries": 0,}
dag = DAG("traffic_violation_pipeline", default_args=default_args, schedule="@daily", catchup=False)

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