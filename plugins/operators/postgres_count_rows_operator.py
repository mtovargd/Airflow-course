from __future__ import annotations

from typing import Any

from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

class PostgreSQLCountRowsOperator(BaseOperator):
    """
    A custom operator to count rows in a PostgreSQL table and push the result to XComs.
    """

    # Tell Airflow that the 'table_name' field can be templated with Jinja
    template_fields = ('table_name',)

    def __init__(
        self,
        *,
        table_name: str,
        postgres_conn_id: str = "postgres_default",
        **kwargs,
    ) -> None:
        """
        :param table_name: The name of the table to count rows from.
        :param postgres_conn_id: The Airflow connection ID for the PostgreSQL database.
        """
        # Call the constructor of the parent class (BaseOperator)
        super().__init__(**kwargs)
        # Store the parameters as instance attributes
        self.postgres_conn_id = postgres_conn_id
        self.table_name = table_name

    def execute(self, context: Any) -> int:
        """
        This is the main method that Airflow runs.
        It connects to Postgres, runs the COUNT query, and returns the result.
        """
        # Create an instance of the PostgresHook
        pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)

        # Define the SQL query using the table_name attribute
        sql = f"SELECT COUNT(*) FROM {self.table_name};"

        self.log.info(f"Executing query: {sql}")
        
        # Use the hook to run the query and get the first result
        result = pg_hook.get_first(sql)
        
        # The result is a tuple, e.g., (123,). Extract the number.
        count = result[0] if result else 0

        self.log.info(f"Found {count} rows in table '{self.table_name}'.")

        # The return value of the execute method is automatically pushed to XComs
        return count