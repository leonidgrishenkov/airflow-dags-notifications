from airflow.plugins_manager import AirflowPlugin
from hooks import listeners


class TelegramNoticationsPlugin(AirflowPlugin):
    name = "TelegramNoticationsPlugin"
    listeners = [listeners]
