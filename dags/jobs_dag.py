from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule

# --- Callable Functions ---
# These functions are called by our Python-based operators.

def log_processing_start():
    """Prints a generic log message."""
    print("Starting the data processing pipeline.")

def check_table_exist():
    """
    A dummy branching function. It always chooses the 'insert_row' path.
    It MUST return the task_id of the next task to run.
    """
    return 'insert_row'


# --- DAG Definition ---
# All the logic for our single pipeline is defined here.
with DAG(
    dag_id='dag_1',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    # Task 1: A PythonOperator to log the start of the process.
    print_process_start = PythonOperator(
        task_id='print_process_start',
        python_callable=log_processing_start
    )

    # Task 2: A BashOperator to execute the 'whoami' shell command.
    get_current_user = BashOperator(
        task_id='get_current_user',
        bash_command='echo "Running as user: $(whoami)"'
    )

    # Task 3: The Branching task to decide which path to take.
    check_table_exists = BranchPythonOperator(
        task_id='check_table_exists',
        python_callable=check_table_exist
    )

    # Task 4a: The "False" branch (if the table doesn't exist).
    create_table = EmptyOperator(task_id='create_table')

    # Task 4b: The "True" branch (if the table exists).
    insert_row = EmptyOperator(task_id='insert_row')

    # Task 5: The final task that merges the branches.
    # We add the trigger_rule here to fix the skipping issue.
    query_table = EmptyOperator(
        task_id='query_table',
        # This rule allows the task to run if its parents were skipped.
        trigger_rule=TriggerRule.NONE_FAILED
    )

    # --- Task Dependencies ---
    # This defines the execution order and structure of the DAG.
    print_process_start >> get_current_user >> check_table_exists
    check_table_exists >> [create_table, insert_row]
    [create_table, insert_row] >> query_table