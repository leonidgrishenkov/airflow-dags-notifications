from __future__ import annotations

import logging
import os
import socket
from pprint import pformat
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

import requests

from airflow.configuration import conf
from airflow.listeners import hookimpl
from airflow.models.taskinstance import TaskInstance
from airflow.utils.session import create_session
from airflow.utils.state import TaskInstanceState
from airflow.utils.types import DagRunType

if TYPE_CHECKING:
    from airflow.models.dagrun import DagRun

logger = logging.getLogger("airflow.plugins.listeners")


class TelegramNotifierBot:
    def __init__(self) -> None:
        # TODO: where to store these values?
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.username = os.getenv("TELEGRAM_BOT_USERNAME")

    def send_message(self, message: str, chat_id: int):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }
        logger.info(
            "Sending telegram message from '%s' bot using payload:\n %s",
            self.username,
            pformat(payload),
        )
        try:
            response = requests.post(url=url, json=payload, timeout=30)
            response.raise_for_status()
            logger.info("Telegram message sent successfully")
        except requests.exceptions.RequestException:
            logger.error(f"Failed to send telegram message. API response: {response.json()}")


def _get_task_instances(dag_run: DagRun, state: TaskInstanceState) -> list[TaskInstance]:
    # WARN: got error: RuntimeError: UNEXPECTED COMMIT - THIS WILL BREAK HA LOCKS!
    # After that sheduler start crushing in endless loop.
    with create_session() as session:
        return (
            session.query(TaskInstance)
            .filter(
                TaskInstance.dag_id == dag_run.dag_id,
                TaskInstance.run_id == dag_run.run_id,
                TaskInstance.state == state,
            )
            .all()
        )


def _map_responsible(owner: str) -> str:
    mapping = {
        "l.grishenkov": "@leonidgrishenkov",
    }
    if owner not in mapping.keys():
        return "Owner not in responsibles mapping"
    return mapping[owner]


@hookimpl
def on_dag_run_failed(dag_run: DagRun, msg: str):
    """
    This method is called when dag run state changes to FAILED.
    """
    TELEGRAM_CHAT_ID = 196255068

    airflow_instance = socket.gethostname()  # TODO: is it correct?
    dag_id = dag_run.dag_id
    run_id = dag_run.run_id
    run_type = dag_run.run_type
    owner = dag_run.get_dag().owner
    data_interval_start = dag_run.data_interval_start.strftime("%Y-%m-%d %H:%M:%S UTC")
    data_interval_end = dag_run.data_interval_end.strftime("%Y-%m-%d %H:%M:%S UTC")

    # TODO: how to get correct webserver url?
    # base_url = conf.get("webserver", "base_url")
    base_url = "http://leonidgrishenkov.com:8080"
    dag_run_url = f"{base_url}/dags/{dag_id}/grid?search={dag_id}&dag_run_id={quote_plus(run_id)}"

    message = (
        f"DAG run failed! 🙈\n\n"
        f"<b>DAG:</b> {dag_id}\n"
        f"<b>Run ID:</b> {run_id}\n"
        f"<b>Run type:</b> {run_type}\n"
        f"<b>Data interval start:</b> {data_interval_start}\n"
        f"<b>Data interval end:</b> {data_interval_end}\n"
        f"<b>Owner:</b> {owner}\n"
        f"<b>Airflow instance:</b> {airflow_instance}\n"
        f"<b>Responsible:</b> {_map_responsible(owner)}\n\n"
        f'<a href="{dag_run_url}">Open DAG Run</a>'
    )

    TelegramNotifierBot().send_message(message, TELEGRAM_CHAT_ID)

@hookimpl
def on_dag_run_success(dag_run: DagRun, msg: str):
    """
    This method is called when dag run state changes to SUCCESS.
    """
    TELEGRAM_CHAT_ID = 196255068

    # NOTE: We will send message only if DAG was triggered manually
    if dag_run.run_type == DagRunType.MANUAL:

        airflow_instance = socket.gethostname()
        dag_id = dag_run.dag_id
        run_id = dag_run.run_id
        owner = dag_run.get_dag().owner
        start_date = dag_run.start_date.strftime("%Y-%m-%d %H:%M:%S UTC")
        end_date = dag_run.end_date.strftime("%Y-%m-%d %H:%M:%S UTC")

        base_url = "http://leonidgrishenkov.com:8080"
        dag_run_url = f"{base_url}/dags/{dag_id}/grid?search={dag_id}&dag_run_id={quote_plus(run_id)}"

        message = (
            f"Manually triggered DAG completed successfully! 🍻\n\n"
            f"<b>DAG:</b> {dag_id}\n"
            f"<b>Run ID:</b> {run_id}\n"
            f"<b>Started:</b> {start_date}\n"
            f"<b>Ended:</b> {end_date}\n"
            f"<b>Owner:</b> {owner}\n"
            f"<b>Airflow instance:</b> {airflow_instance}\n"
            f"<b>Responsible:</b> {_map_responsible(owner)}\n\n"
            f'<a href="{dag_run_url}">Open DAG Run</a>'
        )

        TelegramNotifierBot().send_message(message, TELEGRAM_CHAT_ID)

    else:
        pass
