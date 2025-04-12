import pandas as pd
from sqlalchemy import create_engine

# Define your test database connection manually
DB_USER = "postgres"
DB_PASS = "***REMOVED***"
DB_HOST = "datawarehouse.c3w6kkqw8mjx.eu-north-1.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "postgres"

TABLE_NAME = "traffic_violations"

# Create SQLAlchemy engine
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Load and upload
def load_to_postgres():
    df = pd.read_csv("./opt/airflow/dags/temp/traffic_violations.csv")
    df.to_sql(TABLE_NAME, engine, if_exists="append", index=False, method="multi")
    print(f"Uploaded {len(df)} rows to {TABLE_NAME}")

load_to_postgres()