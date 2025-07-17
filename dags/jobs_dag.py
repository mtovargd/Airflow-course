from datetime import datetime
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

# --- Callable Functions ---
# These functions will be used by the tasks in our DAGs.

def log_processing_start(dag_id, database):
    """Prints a log message indicating the start of the process."""
    print(f"'{dag_id}' has started processing tables in the '{database}' database.")

def check_table_exist():
    """
    A dummy branching function. As required by the exercise, it always
    chooses the 'insert_new_row' path.
    
    In a real DAG, this function would connect to a DB to check for a table.
    It MUST return the task_id of the next task(s) to run.
    """
    return 'insert_new_row'


# --- DAG Configuration ---
# A dictionary defining the parameters for each DAG we want to create.
# We are using the 'dag_1', 'table_1' naming you requested.
config = {
    'dag_1': {
        'schedule_interval': None,
        'start_date': datetime(2023, 1, 1),
        'table_name': 'table_1',
        'database': 'db_1'
    },
    'dag_2': {
        'schedule_interval': None,
        'start_date': datetime(2024, 1, 1),
        'table_name': 'table_2',
        'database': 'db_2'
    },
    'dag_3': {
        'schedule_interval': None,
        'start_date': datetime(2025, 1, 1),
        'table_name': 'table_3',
        'database': 'db_3'
    }
}


# --- Dynamic DAG Generation Loop ---
# This loop iterates through the config dictionary and creates a DAG for each entry.

for dag_id, dag_params in config.items():
    with DAG( 
        dag_id=dag_id,
        schedule_interval=dag_params['schedule_interval'],
        start_date=dag_params['start_date'],
        catchup=False,
        tags=["dynamic_branching"]
    ) as dag:
        
        start_processing = PythonOperator(
            task_id='start_processing_log',
            python_callable=log_processing_start,
            op_kwargs={'dag_id': dag_id, 'database': dag_params['database']}
        )

        # The Branching Task that decides which path to take.
        check_if_table_exists = BranchPythonOperator(
            task_id='check_if_table_exists',
            python_callable=check_table_exist
        )

        # The "False" branch task (if the table doesn't exist).
        create_the_table = DummyOperator(task_id='create_the_table')

        # The "True" branch task (if the table already exists).
        insert_new_row = DummyOperator(task_id='insert_new_row')

        # The downstream task that should run after either branch.
        # This is the task that will be skipped.
        query_the_table = DummyOperator(task_id='query_the_table')

        # --- Task Dependencies ---
        start_processing >> check_if_table_exists
        check_if_table_exists >> [create_the_table, insert_new_row]
        [create_the_table, insert_new_row] >> query_the_table

    # This crucial line makes each dynamically generated DAG visible to Airflow.
    globals()[dag_id] = dag