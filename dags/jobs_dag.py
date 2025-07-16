from datetime import datetime
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

# Define the callable function for the PythonOperator
# It will receive dag_id and database from the 'op_kwargs' parameter
def log_processing_start(dag_id, database):
    """Prints a log message indicating the start of the process."""
    print(f"'{dag_id}' has started processing tables in the '{database}' database.")

# 1. Update the configuration dictionary
# - DAG IDs are now more descriptive.
# - Added 'table_name' and 'database' for each DAG configuration.
config = {
    'dag_1': {
        'schedule_interval': None,
        'start_date': datetime(2023, 1, 1),
        'table_name': 'table_1',
        'database': 'db_1'
    },
    'dag_2': {
        'schedule_interval': None,
        'start_date': datetime(2024, 6, 1),
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

# The main loop to generate the DAGs
for dag_id, dag_params in config.items():
    with DAG( 
        dag_id=dag_id,
        schedule_interval=dag_params['schedule_interval'],
        start_date=dag_params['start_date'],
        catchup=False
    ) as dag:
        
        # 2. Define the first task using PythonOperator
        # We pass arguments to our python function using op_kwargs
        start_processing = PythonOperator(
            task_id='start_processing_log',
            python_callable=log_processing_start,
            op_kwargs={'dag_id': dag_id, 'database': dag_params['database']}
        )

        # 3. Add the first dummy task
        insert_new_row = DummyOperator(task_id='insert_new_row')

        # 4. Add the second dummy task
        query_the_table = DummyOperator(task_id='query_the_table')

        # 5. Set the task dependencies
        start_processing >> insert_new_row >> query_the_table

    # This line ensures Airflow discovers the DAG in the global namespace
    globals()[dag_id] = dag