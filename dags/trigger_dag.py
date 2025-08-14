
# Controller DAG: Triggers a target DAG when a file appears, waits for completion, and cleans up.
# Uses XCom to pull results from the target DAG.

from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup


# The DAG ID to trigger (should match your main pipeline DAG)
TARGET_DAG_ID = 'dag_1'
# Path to the trigger file (can be set via Airflow Variable)
TRIGGER_FILE_PATH = Variable.get('trigger_file_path_var', default_var='/opt/airflow/trigger_files/run')


# Pulls the XCom result from the target DAG's 'query_table' task and prints it
def pull_and_print_xcom_result(**context):
    """
    Pulls the XCom from the triggered DAG run that has the same
    logical date as this DAG.
    """
    execution_date_to_check = context['ds']
    print(f"Attempting to pull XCom from {TARGET_DAG_ID} for execution_date: {execution_date_to_check}")

    pulled_message = context['ti'].xcom_pull(
        dag_id=TARGET_DAG_ID,
        task_ids='query_table'
    )

    print(f"Message pulled from {TARGET_DAG_ID}: '{pulled_message}'")
    print("--- Full Task Context ---")
    print(context)

with DAG(
    dag_id='dag_controller_and_file_trigger',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['controller-dag', 'sensor-example'],
    render_template_as_native_obj=True
) as dag:

    # Wait for the trigger file to appear
    wait_for_trigger_file = FileSensor(
        task_id='wait_for_trigger_file',
        fs_conn_id='fs_default',
        filepath=TRIGGER_FILE_PATH,
        poke_interval=10
    )

    # Trigger the target DAG when the file is detected
    trigger_target_dag = TriggerDagRunOperator(
        task_id='trigger_target_dag',
        trigger_dag_id=TARGET_DAG_ID,
        execution_date="{{ ds }}",
        wait_for_completion=False
    )

    # Group result processing tasks
    with TaskGroup('process_results') as process_results:
        # Wait for the target DAG to finish (any task)
        check_dag_status = ExternalTaskSensor(
            task_id='check_dag_status',
            external_dag_id=TARGET_DAG_ID,
            external_task_id=None,
            execution_date_fn=lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0),
            mode='reschedule',
            poke_interval=15
        )

        # Print the XCom result from the target DAG
        print_result = PythonOperator(
            task_id='print_result',
            python_callable=pull_and_print_xcom_result
        )

        # Remove the trigger file
        remove_run_file = BashOperator(
            task_id='remove_run_file',
            bash_command=f'rm -f {TRIGGER_FILE_PATH}'
        )

        # Create a finished marker file
        create_finished_file = BashOperator(
            task_id='create_finished_file',
            bash_command=f'touch /opt/airflow/trigger_files/finished_{{{{ ts_nodash }}}}.txt'
        )

        # Set dependencies within the group
        check_dag_status >> print_result >> [remove_run_file, create_finished_file]

    # Main DAG flow
    wait_for_trigger_file >> trigger_target_dag >> process_results

from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

TARGET_DAG_ID = 'dag_1'
TRIGGER_FILE_PATH = Variable.get('trigger_file_path_var', default_var='/opt/airflow/trigger_files/run')

def pull_and_print_xcom_result(**context):
    """
    Pulls the XCom from the triggered DAG run that has the same
    logical date as this DAG.
    """
    execution_date_to_check = context['ds']
    print(f"Attempting to pull XCom from {TARGET_DAG_ID} for execution_date: {execution_date_to_check}")

    pulled_message = context['ti'].xcom_pull(
        dag_id=TARGET_DAG_ID,
        task_ids='query_table'
    )

    print(f"Message pulled from {TARGET_DAG_ID}: '{pulled_message}'")
    print("--- Full Task Context ---")
    print(context)

with DAG(
    dag_id='dag_controller_and_file_trigger',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['controller-dag', 'sensor-example'],
    render_template_as_native_obj=True
) as dag:

    wait_for_trigger_file = FileSensor(
        task_id='wait_for_trigger_file',
        fs_conn_id='fs_default',
        filepath=TRIGGER_FILE_PATH,
        poke_interval=10
    )

    trigger_target_dag = TriggerDagRunOperator(
        task_id='trigger_target_dag',
        trigger_dag_id=TARGET_DAG_ID,
        execution_date="{{ ds }}",
        wait_for_completion=False
    )

    with TaskGroup('process_results') as process_results:
        check_dag_status = ExternalTaskSensor(
            task_id='check_dag_status',
            external_dag_id=TARGET_DAG_ID,
            external_task_id=None,
            execution_date_fn=lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0),
            mode='reschedule',
            poke_interval=15
        )

        print_result = PythonOperator(
            task_id='print_result',
            python_callable=pull_and_print_xcom_result
        )

        remove_run_file = BashOperator(
            task_id='remove_run_file',
            bash_command=f'rm -f {TRIGGER_FILE_PATH}'
        )

        create_finished_file = BashOperator(
            task_id='create_finished_file',
            bash_command=f'touch /opt/airflow/trigger_files/finished_{{{{ ts_nodash }}}}.txt'
        )

def pull_and_print_xcom_result(**context):
    """
    Pulls the XCom from the triggered DAG run that has the same
    logical date as this DAG.
    """
    execution_date_to_check = context['ds']
    print(f"Attempting to pull XCom from {TARGET_DAG_ID} for execution_date: {execution_date_to_check}")

    pulled_message = context['ti'].xcom_pull(
        dag_id=TARGET_DAG_ID,
        task_ids='query_table'
    )

    print(f"Message pulled from {TARGET_DAG_ID}: '{pulled_message}'")
    print("--- Full Task Context ---")
    print(context)

with DAG(
    dag_id='dag_controller_and_file_trigger',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['controller-dag', 'sensor-example'],
    render_template_as_native_obj=True
) as dag:

    wait_for_trigger_file = FileSensor(
        task_id='wait_for_trigger_file',
        fs_conn_id='fs_default',
        filepath=TRIGGER_FILE_PATH,
        poke_interval=10
    )

    trigger_target_dag = TriggerDagRunOperator(
        task_id='trigger_target_dag',
        trigger_dag_id=TARGET_DAG_ID,
        execution_date="{{ ds }}",
        wait_for_completion=False
    )

    with TaskGroup('process_results') as process_results:
        check_dag_status = ExternalTaskSensor(
            task_id='check_dag_status',
            external_dag_id=TARGET_DAG_ID,
            external_task_id=None,
            execution_date_fn=lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0),
            mode='reschedule',
            poke_interval=15
        )

        print_result = PythonOperator(
            task_id='print_result',
            python_callable=pull_and_print_xcom_result
        )

        remove_run_file = BashOperator(
            task_id='remove_run_file',
            bash_command=f'rm -f {TRIGGER_FILE_PATH}'
        )

        create_finished_file = BashOperator(
            task_id='create_finished_file',
            bash_command=f'touch /opt/airflow/trigger_files/finished_{{{{ ts_nodash }}}}.txt'
        )

        check_dag_status >> print_result >> [remove_run_file, create_finished_file]

    wait_for_trigger_file >> trigger_target_dag >> process_results
TARGET_DAG_ID = 'dag_1'
TRIGGER_FILE_PATH = Variable.get('trigger_file_path_var', default_var='/opt/airflow/trigger_files/run')

def pull_and_print_xcom_result(**context):
    """
    Pulls the XCom from the triggered DAG run that has the same
    logical date as this DAG.
    """
    execution_date_to_check = context['ds']
    print(f"Attempting to pull XCom from {TARGET_DAG_ID} for execution_date: {execution_date_to_check}")

    pulled_message = context['ti'].xcom_pull(
        dag_id=TARGET_DAG_ID,
        task_ids='query_table'
    )

    print(f"Message pulled from {TARGET_DAG_ID}: '{pulled_message}'")
    print("--- Full Task Context ---")
    print(context)

with DAG(
    dag_id='dag_controller_and_file_trigger',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['controller-dag', 'sensor-example'],
    render_template_as_native_obj=True
) as dag:

    wait_for_trigger_file = FileSensor(
        task_id='wait_for_trigger_file',
        fs_conn_id='fs_default',
        filepath=TRIGGER_FILE_PATH,
        poke_interval=10
    )

    trigger_target_dag = TriggerDagRunOperator(
        task_id='trigger_target_dag',
        trigger_dag_id=TARGET_DAG_ID,
        execution_date="{{ ds }}",
        wait_for_completion=False
    )

    with TaskGroup('process_results') as process_results:
        check_dag_status = ExternalTaskSensor(
            task_id='check_dag_status',
            external_dag_id=TARGET_DAG_ID,
            external_task_id=None,
            execution_date_fn=lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0),
            mode='reschedule',
            poke_interval=15
        )

        print_result = PythonOperator(
            task_id='print_result',
            python_callable=pull_and_print_xcom_result
        )

        remove_run_file = BashOperator(
            task_id='remove_run_file',
            bash_command=f'rm -f {TRIGGER_FILE_PATH}'
        )

        create_finished_file = BashOperator(
            task_id='create_finished_file',
            bash_command=f'touch /opt/airflow/trigger_files/finished_{{{{ ts_nodash }}}}.txt'
        )

        check_dag_status >> print_result >> [remove_run_file, create_finished_file]

    wait_for_trigger_file >> trigger_target_dag >> process_results