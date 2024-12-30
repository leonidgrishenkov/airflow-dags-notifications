import random
from datetime import datetime

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator
from airflow.operators.python_operator import PythonOperator


def almost_success_func():
    value = random.randint(1, 3)
    if value == 1:
        raise ValueError("This is a test error for demonstration purposes.")
    else:
        print(value)


with DAG(
    dag_id="success_dag",
    default_args={
        "owner": "l.grishenkov",
        "depends_on_past": False,
        "retries": 0,
    },
    schedule_interval="* * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["test", "success"],
) as dag:
    start = EmptyOperator(
        task_id="start",
    )

    end = EmptyOperator(
        task_id="end",
    )

    success_func = PythonOperator(
        task_id="success_func",
        python_callable=almost_success_func,
    )

    chain(
        start,
        success_func,
        end,
    )
