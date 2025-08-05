# Airflow Course - Docker Setup

This project contains an Apache Airflow setup using Docker Compose to run your DAGs. It demonstrates a complete data pipeline that interacts with a PostgreSQL database, as well as a controller DAG pattern for event-driven workflows.

## Files Structure

```
.
├── docker-compose.yml         # Docker Compose configuration
├── .env                      # Environment variables
├── dags/                     # Directory for DAG files
│   ├── jobs_dag.py          # Main Postgres data pipeline
│   └── trigger_dag.py       # Controller DAG with FileSensor and DAG triggering
├── logs/                     # Airflow logs
├── plugins/                  # Custom plugins (including custom operators)
├── trigger_files/           # The trigger file appears here for the controller DAG
└── config/                   # Configuration files```
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system
- At least 4GB of RAM available for Docker

### Running Airflow

1.  **Start the services:**
    ```bash
    docker-compose up -d
    ```

2.  **Wait for initialization:**
    The first time you run this, it will take a few minutes to:
    - Download the Docker images
    - Initialize the database
    - Create the admin user

3.  **Configure the Airflow Connection:**
    Before the main DAG can run, you must tell Airflow how to connect to the PostgreSQL database.
    - Open the Airflow UI and go to **Admin** -> **Connections**.
    - Click the **`+`** button to add a new connection.
    - Fill out the form with these exact details:
      - **Connection Id:** `postgres_default`
      - **Connection Type:** `Postgres`
      - **Host:** `postgres`
      - **Schema:** `airflow`
      - **Login:** `airflow`
      - **Password:** `airflow`
      - **Port:** `5432`
    - Click **Test**. You should see a "Connection successfully tested" message.
    - Click **Save**.

4.  **Access the Airflow UI:**
    - Open your browser and go to: `http://localhost:8080`
    - Login with:
      - **Username:** `admin`
      - **Password:** `admin`

5.  **View your DAGs:**
    - Once logged in, you should see two DAGs:
      - `postgres_pipeline_example`: The main data processing pipeline.
      - `dag_controller_and_file_trigger`: The controller DAG that triggers the main pipeline.
    - Click on either DAG to view its structure and run it.

### Managing the Setup

**Stop the services:**
```bash
docker-compose down
```

**Stop and remove all data (including the database):**
```bash
docker-compose down -v
```

**View logs:**
```bash
docker-compose logs -f
```

## DAG Architecture


### Postgres Pipeline DAG (`postgres_pipeline_example`)

The `dags/jobs_dag.py` file contains the primary data pipeline (`postgres_pipeline_example`). This DAG demonstrates a full ETL (Extract, Transform, Load) pattern by connecting to a PostgreSQL database, creating a table if it doesn't exist, inserting new data, and querying the result. It now uses a **custom operator** for counting rows in the table.

#### DAG Details

The `postgres_pipeline_example` DAG includes:
- **Start Date**: 2023-01-01
- **Schedule**: Manual trigger only (`schedule_interval=None`)
- **Catchup**: Disabled
- **Key Operators**: `PostgresOperator`, `BashOperator`, `BranchPythonOperator`, `PostgreSQLCountRowsOperator` (custom)
- **Key Hooks**: `PostgresHook` for custom Python-to-Postgres interaction.
- **Key Features**: XComs for inter-task communication, dynamic branching, idempotent design, and a reusable custom operator for row counting.

#### DAG Structure with Real Database Logic

The DAG follows this robust, idempotent execution pattern:

1.  **`get_current_user`**: A `BashOperator` that runs `whoami`. Its last line of output (`airflow`) is automatically **pushed to XComs**.

2.  **`check_table_exists`**: A `BranchPythonOperator` that uses `PostgresHook` to connect to the database and check if the target table exists. It returns the ID of the next task to run.

3.  **Branching paths**:
    -   **`create_table`**: A `PostgresOperator` that runs a `CREATE TABLE` script. This path is only taken if the table does not exist.
    -   **`insert_row`**: A `PostgresOperator` that runs an `INSERT` script. It pulls the username from XComs (`get_current_user` task), generates a random ID, and adds the current timestamp.

4.  **`query_table`**: A **custom operator** (`PostgreSQLCountRowsOperator`) that runs a `SELECT COUNT(*)` query on the table and pushes the row count to XComs. It ensures it runs after either branch by using `TriggerRule.NONE_FAILED`.

#### Task Flow Diagram

```
get_current_user
        │
        ▼ (pushes 'airflow' to XCom)
check_table_exists
        │
        ├─── create_table (PostgresOperator) ───┐
        │                                       │
        └─── insert_row (PostgresOperator) ─────┤
             (pulls from XCom)                  │
                                                ▼
                                  query_table (PostgreSQLCountRowsOperator)
                                       (pushes row count to XCom)
                                          (NONE_FAILED)
```

#### Key Features

- **Database Integration**: Demonstrates creating tables and inserting data with `PostgresOperator`.
- **Custom DB Logic**: Uses `PostgresHook` within a `BranchPythonOperator` for checking table existence, and a **custom operator** for querying results.
- **XComs for Data Sharing**: Pushes data from a `BashOperator` and a `PythonOperator`, and pulls that data into a `PostgresOperator` for use in a query.
- **Idempotent Design**: The "check-then-act" pattern ensures the DAG can be run repeatedly without errors.
- **Dynamic SQL with Parameters**: Safely injects parameters into SQL queries to prevent injection attacks.


## Controller DAG Implementation

The `dags/trigger_dag.py` file contains a controller DAG (`dag_controller_and_file_trigger`) that demonstrates file-based, event-driven orchestration. **Note:** The controller DAG's target DAG id is set by the `TARGET_DAG_ID` variable in the code (default: `'dag_1'`). Update this to match your main pipeline DAG id if needed (e.g., `'postgres_pipeline_example'`).

### Controller DAG Details

The controller DAG waits for a file to appear, triggers the `postgres_pipeline_example` DAG, waits for it to finish, and then cleans up the file.

- **Target DAG**: `postgres_pipeline_example`
- **Trigger**: Appearance of `/opt/airflow/trigger_files/run`

### Using the Controller DAG

To trigger the data processing pipeline via the controller DAG:

1.  **Create the trigger directory** (one-time setup):
    ```bash
    docker exec airflow-scheduler mkdir -p /opt/airflow/trigger_files
    ```
2.  **Unpause and trigger the `dag_controller_and_file_trigger`**. The first task will start "sensing".

3.  **Create the trigger file** to start the pipeline:
    ```bash
    docker exec airflow-scheduler touch /opt/airflow/trigger_files/run
    ```
4.  **Monitor the pipeline**:
    - The sensor will succeed and trigger a new run of the target DAG (see `TARGET_DAG_ID` in `trigger_dag.py`).
    - When that DAG run completes, the controller will proceed to its final step, removing the `run` file and creating a `finished_*.txt` file.
## Custom Operator: PostgreSQLCountRowsOperator

This project includes a custom Airflow operator: `PostgreSQLCountRowsOperator` (see `plugins/operators/postgres_count_rows_operator.py`).

- **Purpose:** Counts the number of rows in a specified PostgreSQL table and pushes the result to XComs.
- **Usage:** Used as the `query_table` task in the main pipeline DAG.
- **Benefits:** Clean, reusable, and demonstrates how to extend Airflow with custom operators.


## Troubleshooting

If you encounter issues:

1.  **PostgresOperator tasks failing:**
    - Go to **Admin -> Connections** in the Airflow UI.
    - Ensure a connection with the ID `postgres_default` exists.
    - Click to edit it, verify all credentials are correct, and use the **Test** button.

2.  **FileSensor not detecting files:**
    ```bash
    # Verify the trigger directory exists inside the container
    docker exec airflow-scheduler ls -la /opt/airflow/trigger_files/
    ```
