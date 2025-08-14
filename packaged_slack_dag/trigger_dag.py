from __future__ import annotations
from datetime import datetime

from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.models.dagrun import DagRun
from airflow.models.variable import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.task_group import TaskGroup

# --- Constants ---
TARGET_DAG_ID = "postgres_pipeline_example"
TRIGGER_FILE_PATH = "/opt/airflow/trigger_files/run"
# Slack channel ID is now read from Airflow Variable 'slack_channel_id'
SLACK_CHANNEL_ID = Variable.get("slack_channel_id")

@task
def send_alert_to_slack(**kwargs):
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    dag_run = kwargs.get("dag_run")
    slack_token = Variable.get("slack_token")
    client = WebClient(token=slack_token)
    message = f"Airflow DAG '{dag_run.dag_id}' finished successfully at {dag_run.execution_date}."
    try:
        response = client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
        print(f"Slack message sent: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending Slack message: {e.response['error']}")
        raise

with DAG(
    dag_id="packaged_controller_with_slack_and_vault",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["controller-dag", "vault", "slack"],
) as dag:
    wait_for_trigger_file = FileSensor(
        task_id="wait_for_trigger_file",
        filepath=TRIGGER_FILE_PATH,
        poke_interval=10,
    )

    trigger_target_dag = TriggerDagRunOperator(
        task_id="trigger_target_dag",
        trigger_dag_id=TARGET_DAG_ID,
        wait_for_completion=True,
        poke_interval=20,
    )

    with TaskGroup(group_id="process_results") as process_results:
        remove_trigger_file = BashOperator(
            task_id="remove_trigger_file",
            bash_command=f"rm -f {TRIGGER_FILE_PATH}",
        )

    send_notification = send_alert_to_slack()

    wait_for_trigger_file >> trigger_target_dag >> process_results >> send_notification
