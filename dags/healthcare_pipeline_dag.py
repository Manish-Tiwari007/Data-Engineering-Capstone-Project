import sys

sys.path.insert(0, "/opt/airflow/scripts")

from airflow import DAG  # noqa: E402
from airflow.operators.python import PythonOperator  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

from extract import extract_data  # noqa: E402
from load_bronze import load_to_bronze  # noqa: E402
from transform_silver import transform_to_silver  # noqa: E402
from build_gold import build_gold_layer  # noqa: E402


def extract_task(ti, ds, **kwargs):
    records = extract_data(run_date=ds)
    ti.xcom_push(key="records", value=records)
    ti.xcom_push(key="run_date", value=ds)


def bronze_task(ti):
    run_date = ti.xcom_pull(key="run_date", task_ids="extract_data")
    records = ti.xcom_pull(key="records", task_ids="extract_data")
    load_to_bronze(records=records, run_date=run_date)


def silver_task(ti):
    run_date = ti.xcom_pull(key="run_date", task_ids="extract_data")
    transform_to_silver(run_date=run_date)


def gold_task(ti):
    run_date = ti.xcom_pull(key="run_date", task_ids="extract_data")
    build_gold_layer(run_date=run_date)


default_args = {
    "owner": "data_eng_student",
    "depends_on_past": False,
    "email": ["stakeholder@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="healthcare_data_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    tags=["medallion", "snowflake", "healthcare"],
) as dag:

    extract = PythonOperator(task_id="extract_data", python_callable=extract_task)

    bronze = PythonOperator(task_id="load_bronze", python_callable=bronze_task)

    silver = PythonOperator(task_id="transform_silver", python_callable=silver_task)

    gold = PythonOperator(task_id="build_gold", python_callable=gold_task)

    extract >> bronze >> silver >> gold
