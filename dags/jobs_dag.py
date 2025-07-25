from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule

# --- Callable Functions ---

def log_processing_start():
    """Prints a generic log message."""
    print("Starting the data processing pipeline.")

def check_table_exist():
    """Dummy branching function that always chooses the 'insert_row' path."""
    return 'insert_row'

def push_completion_message(**context):
    """Pushes a custom XCom message with the run_id."""
    run_id = context['run_id']
    message = f"{run_id} ended"
    print(f"Pushing XCom message: '{message}'")
    return message

# --- DAG Definition ---

with DAG(
    dag_id='dag_1',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['worker-dag']
) as dag:

    print_process_start = PythonOperator(
        task_id='print_process_start',
        python_callable=log_processing_start
    )
    get_current_user = BashOperator(
        task_id='get_current_user',
        bash_command='echo "Running as user: $(whoami)"'
    )
    check_table_exists = BranchPythonOperator(
        task_id='check_table_exists',
        python_callable=check_table_exist
    )
    create_table = EmptyOperator(task_id='create_table')
    insert_row = EmptyOperator(task_id='insert_row')

    # MODIFIED TASK: Changed to PythonOperator to push a custom XCom
    query_table = PythonOperator(
        task_id='query_table',
        python_callable=push_completion_message,
        trigger_rule=TriggerRule.NONE_FAILED
    )

    # --- Dependencies ---
    print_process_start >> get_current_user >> check_table_exists
    check_table_exists >> [create_table, insert_row]
    [create_table, insert_row] >> query_table