import sys
sys.path.insert(0, '/opt/airflow/scripts')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from extract import extract_data
from load_bronze import load_to_bronze
from transform_silver import transform_to_silver
from build_gold import build_gold_layer


def extract_task(ti):
    df = extract_data()
    ti.xcom_push(key="df", value=df)


def bronze_task(ti):
    df = ti.xcom_pull(key="df", task_ids="extract_data")
    load_to_bronze(df)


def silver_task(ti):
    transform_to_silver()


def gold_task(ti):
    build_gold_layer()


with DAG(
    dag_id="healthcare_data_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    extract = PythonOperator(
        task_id="extract_data",
        python_callable=extract_task
    )

    bronze = PythonOperator(
        task_id="load_bronze",
        python_callable=bronze_task
    )

    silver = PythonOperator(
        task_id="transform_silver",
        python_callable=silver_task
    )

    gold = PythonOperator(
        task_id="build_gold",
        python_callable=gold_task
    )

    extract >> bronze >> silver >> gold