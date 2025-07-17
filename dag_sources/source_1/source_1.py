from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator

DAG_CONFIG = {
    'dag_id': 'dag_1',
    'schedule_interval': None,
    'start_date': datetime(2023, 1, 1),
    'table_name': 'table_1',
    'database': 'db_1'
}

# Define the callable function for the PythonOperator
def log_processing_start(dag_id, database):
    """Prints a log message indicating the start of the process."""
    print(f"'{dag_id}' has started processing tables in the '{database}' database.")


# Define the DAG using the configuration dictionary
with DAG(
    dag_id=DAG_CONFIG['dag_id'],
    start_date=DAG_CONFIG['start_date'],
    schedule_interval=DAG_CONFIG['schedule_interval'],
    catchup=False
) as dag:

    # Define the first task using PythonOperator
    start_processing = PythonOperator(
        task_id='start_processing_log',
        python_callable=log_processing_start,
        op_kwargs={'dag_id': DAG_CONFIG['dag_id'], 'database': DAG_CONFIG['database']}
    )

    # Add the dummy task for insertion
    insert_new_row = DummyOperator(task_id='insert_new_row')

    # Add the dummy task for querying
    query_the_table = DummyOperator(task_id='query_the_table')

    # Set the task dependencies
    start_processing >> insert_new_row >> query_the_table