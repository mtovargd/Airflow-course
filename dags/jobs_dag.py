from __future__ import annotations

import random
from datetime import datetime

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.trigger_rule import TriggerRule

# Import our custom operator from the plugins/operators directory
from operators.postgres_count_rows_operator import PostgreSQLCountRowsOperator

# --- Constants ---
POSTGRES_CONN_ID = "postgres_default"
TABLE_NAME = "user_processing_data"

# --- Callable Functions ---
def check_if_table_exists_callable(table_name: str) -> str:
    """
    Checks if the target table exists and returns the next task_id.
    This logic remains in a callable because it's for a BranchPythonOperator.
    """
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    sql = "SELECT 1 FROM information_schema.tables WHERE table_name = %s"
    result = pg_hook.get_first(sql, parameters=[table_name])
    if result:
        return "insert_row"
    return "create_table"

# The query_table_callable function has been REMOVED. Its logic is now in the custom operator.

# --- DAG Definition ---
with DAG(
    dag_id="postgres_pipeline_example",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["postgres_example", "custom_operator"],
) as dag:

    get_current_user = BashOperator(
        task_id="get_current_user",
        bash_command='echo "Running as user: $(whoami)" && whoami',
    )

    check_table_exists = BranchPythonOperator(
        task_id="check_table_exists",
        python_callable=check_if_table_exists_callable,
        op_kwargs={"table_name": TABLE_NAME},
    )

    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql="sql/create_user_processing_table.sql", # Example of using an external SQL file
        params={"table_name": TABLE_NAME},
    )

    insert_row = PostgresOperator(
        task_id="insert_row",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql="""
            INSERT INTO {{ params.table_name }} (custom_id, user_name, timestamp)
            VALUES (%(custom_id)s, %(user_name)s, %(timestamp)s);
        """,
        params={"table_name": TABLE_NAME},
        parameters={
            "custom_id": random.randint(1, 100000),
            "user_name": "{{ ti.xcom_pull(task_ids='get_current_user') }}",
            "timestamp": datetime.now().isoformat(),
        },
    )

    # This task now uses our clean, reusable custom operator
    query_table = PostgreSQLCountRowsOperator(
        task_id="query_table",
        table_name=TABLE_NAME,
        postgres_conn_id=POSTGRES_CONN_ID,
        trigger_rule=TriggerRule.NONE_FAILED,
    )

    # --- Task Dependencies ---
    get_current_user >> check_table_exists
    check_table_exists >> [create_table, insert_row]
    [create_table, insert_row] >> query_table