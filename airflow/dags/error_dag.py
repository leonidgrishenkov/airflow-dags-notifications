from datetime import datetime

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator
from airflow.operators.python_operator import PythonOperator


def raise_error():
    raise ValueError("This is a test error for demonstration purposes.")

with DAG(
    dag_id="error_dag",
    default_args={
        "owner": "l.grishenkov",
        "depends_on_past": False,
        "retries": 0,
    },
    schedule_interval="* * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["test", "error"],
) as dag:
    start = EmptyOperator(
        task_id="start",
    )

    end = EmptyOperator(
        task_id="end",
    )

    raise_error = PythonOperator(
        task_id="raise_error",
        python_callable=raise_error,
    )

    chain(
        start,
        raise_error,
        end,
    )
