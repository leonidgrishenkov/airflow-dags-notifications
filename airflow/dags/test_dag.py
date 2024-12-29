from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator


def raise_error():
    """A simple function to raise an error."""
    raise ValueError("This is a test error for demonstration purposes.")

default_args = {
    'owner': 'l.grishenkov',
    'depends_on_past': False,
    'retries': 0,  # Set retries to 0 to immediately mark as failed
}

with DAG(
    dag_id='test_dag',
    default_args=default_args,
    description='A simple DAG to test error handling',
    schedule_interval=None,  # No automatic scheduling, can be triggered manually
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['test', 'error'],
) as dag:

    start = EmptyOperator(
        task_id="start",
    )

    end = EmptyOperator(
        task_id="end",
    )

    task_raise_error = PythonOperator(
        task_id='raise_error',
        python_callable=raise_error,
    )

    chain(
            start,
            task_raise_error,
            end,
    )
