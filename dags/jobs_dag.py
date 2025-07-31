from __future__ import annotations

import random
from datetime import datetime

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.trigger_rule import TriggerRule

POSTGRES_CONN_ID = "postgres_default"
TABLE_NAME = "user_processing_data"


def check_if_table_exists_callable(table_name: str) -> str:
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    sql = "SELECT 1 FROM information_schema.tables WHERE table_name = %s"
    result = pg_hook.get_first(sql, parameters=[table_name])
    print(f"Table check for '{table_name}' returned: {result}")
    if result:
        return "insert_row"
    return "create_table"


def query_table_callable(table_name: str) -> int:
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    sql = f"SELECT COUNT(*) FROM {table_name};"
    result = pg_hook.get_first(sql)
    count = result[0] if result else 0
    print(f"Table '{table_name}' has {count} rows.")
    return count


with DAG(
    dag_id="postgres_pipeline_example",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["postgres_example", "xcom_example"],
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
        sql="""
            CREATE TABLE IF NOT EXISTS {{ params.table_name }} (
                custom_id INTEGER NOT NULL,
                user_name VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL
            );
        """,
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
        # The 'parameters' dictionary is for the database driver.
        parameters={
            "custom_id": random.randint(1, 100000),
            "user_name": "{{ ti.xcom_pull(task_ids='get_current_user') }}",
            "timestamp": datetime.now().isoformat(),
        },
    )

    query_table = PythonOperator(
        task_id="query_table",
        python_callable=query_table_callable,
        op_kwargs={"table_name": TABLE_NAME},
        trigger_rule=TriggerRule.NONE_FAILED,
    )

    get_current_user >> check_table_exists
    check_table_exists >> [create_table, insert_row]
    [create_table, insert_row] >> query_table