from datetime import datetime
from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.bash import BashOperator

# The DAG ID of the pipeline we want to trigger
# This must match the dag_id from your previous practice file.
TARGET_DAG_ID = 'dag_1'

# The path to the trigger file the FileSensor will wait for.
# This path must be accessible from inside the Airflow containers.
TRIGGER_FILE_PATH = '/opt/airflow/trigger_files/run'


with DAG(
    dag_id='dag_controller_and_file_trigger',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    # Add a descriptive tag for better organization in the UI
    tags=['controller-dag', 'sensor-example'],
) as dag:

    # Task 1: Wait for a file to appear.
    # This task will keep running ("poking") until the file exists.
    wait_for_trigger_file = FileSensor(
        task_id='wait_for_trigger_file',
        # The filesystem connection to use. 'fs_default' points to the
        # local filesystem of the container.
        fs_conn_id='fs_default',
        # The full path to the file to sense.
        filepath=TRIGGER_FILE_PATH,
        # How often (in seconds) to check for the file.
        poke_interval=10
    )

    # Task 2: Trigger the target DAG and wait for it to complete.
    trigger_target_dag = TriggerDagRunOperator(
        task_id='trigger_target_dag',
        # The dag_id of the DAG to trigger.
        trigger_dag_id=TARGET_DAG_ID,
        # This is crucial: it makes this operator wait until the
        # triggered DAG has finished its run.
        wait_for_completion=True,
        # How often (in seconds) to check the status of the triggered DAG.
        poke_interval=20
    )

    # Task 3: Remove the trigger file after a successful run.
    # This makes the pipeline reusable for the next run.
    remove_trigger_file = BashOperator(
        task_id='remove_trigger_file',
        # Use -f (force) to prevent an error if the file is already gone.
        bash_command=f'rm -f {TRIGGER_FILE_PATH}'
    )

    # --- Task Dependencies ---
    # Defines the linear execution flow of the DAG.
    wait_for_trigger_file >> trigger_target_dag >> remove_trigger_file