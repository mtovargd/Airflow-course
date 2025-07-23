# Airflow Course - Docker Setup

This project contains an Apache Airflow setup using Docker Compose to run your DAGs.

## Files Structure

```
.
├── docker-compose.yml         # Docker Compose configuration
├── .env                      # Environment variables
├── dags/                     # Directory for DAG files
│   ├── jobs_dag.py          # Main DAG with branching logic and mixed operators
│   └── trigger_dag.py       # Controller DAG with FileSensor and DAG triggering
├── logs/                     # Airflow logs
├── plugins/                  # Custom plugins
└── config/                   # Configuration files
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system
- At least 4GB of RAM available for Docker

### Running Airflow

1. **Start the services:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for initialization:**
   The first time you run this, it will take a few minutes to:
   - Download the Docker images
   - Initialize the database
   - Create the admin user

3. **Access the Airflow UI:**
   - Open your browser and go to: http://localhost:8080
   - Login with:
     - Username: `admin`
     - Password: `admin`

4. **View your DAGs:**
   - Once logged in, you should see two DAGs:
     - `dag_1`: The main data processing pipeline
     - `dag_controller_and_file_trigger`: The controller DAG that triggers the main DAG via file sensing
   - Click on either DAG to view its structure and run it

### Managing the Setup

**Stop the services:**
```bash
docker-compose down
```

**Stop and remove all data:**
```bash
docker-compose down -v
```

**View logs:**
```bash
docker-compose logs -f
```

**Check service status:**
```bash
docker-compose ps
```

## DAG Architecture

### Single DAG Implementation

The `dags/jobs_dag.py` file contains a single DAG (`dag_1`) that demonstrates various Airflow concepts including:
- Mixed operator types (Python, Bash, Empty)
- Conditional branching logic
- Proper trigger rules to handle skipped tasks
- Sequential and parallel task execution

### DAG Details

The single DAG `dag_1` includes:
- **Start Date**: 2023-01-01
- **Schedule**: Manual trigger only (`schedule_interval=None`)
- **Catchup**: Disabled
- **Mixed Operators**: PythonOperator, BashOperator, EmptyOperator, BranchPythonOperator

### DAG Structure with Branching Logic

The DAG follows this execution pattern:

1. **`print_process_start`**: PythonOperator that logs the start of processing
   - Prints: "Starting the data processing pipeline."
   
2. **`get_current_user`**: BashOperator that executes a shell command
   - Runs: `echo "Running as user: $(whoami)"`
   
3. **`check_table_exists`**: BranchPythonOperator that determines the next path
   - Currently always returns 'insert_row' (simulating table exists)
   - In production, this would check if the table exists in the database
   
4. **Branching paths**:
   - **`create_table`**: EmptyOperator (runs if table doesn't exist)
   - **`insert_row`**: EmptyOperator (runs if table exists)
   
5. **`query_table`**: Final EmptyOperator that runs after either branch
   - Uses `TriggerRule.NONE_FAILED` to run even when upstream tasks are skipped

### Task Flow Diagram

```
print_process_start
        │
        ▼
get_current_user
        │
        ▼
check_table_exists
        │
        ├─── create_table ───┐
        │                    │
        └─── insert_row ─────┤
                             │
                             ▼
                      query_table
                   (NONE_FAILED)
```

### Key Features

- **Mixed Operators**: Demonstrates PythonOperator, BashOperator, and EmptyOperator usage
- **Branching Logic**: Uses `BranchPythonOperator` to conditionally execute tasks
- **Trigger Rules**: Implements `TriggerRule.NONE_FAILED` to handle skipped tasks properly
- **Sequential and Parallel Flow**: Shows both linear task progression and parallel branching
- **Shell Integration**: Includes system command execution with BashOperator

## Controller DAG Implementation

The `dags/trigger_dag.py` file contains a controller DAG (`dag_controller_and_file_trigger`) that demonstrates advanced Airflow concepts including:
- File-based triggering with FileSensor
- Cross-DAG communication with TriggerDagRunOperator
- Event-driven pipeline orchestration
- Automated cleanup operations

### Controller DAG Details

The controller DAG `dag_controller_and_file_trigger` includes:
- **Start Date**: 2023-01-01
- **Schedule**: Manual trigger only (`schedule_interval=None`)
- **Catchup**: Disabled
- **Tags**: `['controller-dag', 'sensor-example']` for better UI organization
- **Key Operators**: FileSensor, TriggerDagRunOperator, BashOperator

### Controller DAG Structure

The controller DAG follows this execution pattern:

1. **`wait_for_trigger_file`**: FileSensor that monitors for a trigger file
   - **File Path**: `/opt/airflow/trigger_files/run`
   - **Connection**: `fs_default` (local filesystem)
   - **Poke Interval**: 10 seconds (how often it checks for the file)
   - **Behavior**: Continuously polls until the trigger file appears
   
2. **`trigger_target_dag`**: TriggerDagRunOperator that launches the main pipeline
   - **Target DAG**: `dag_1` (the main data processing pipeline)
   - **Wait for Completion**: `True` (waits for the triggered DAG to finish)
   - **Poke Interval**: 20 seconds (how often it checks the triggered DAG's status)
   - **Behavior**: Triggers `dag_1` and monitors its execution until completion
   
3. **`remove_trigger_file`**: BashOperator that cleans up the trigger file
   - **Command**: `rm -f /opt/airflow/trigger_files/run`
   - **Behavior**: Removes the trigger file to prepare for the next run
   - **Flag**: Uses `-f` to prevent errors if the file is already gone

### Controller Task Flow Diagram

```
wait_for_trigger_file
        │
        ▼ (file detected)
trigger_target_dag
        │
        ▼ (dag_1 completed)
remove_trigger_file
```

### Key Controller Features

- **File-Based Triggering**: Uses FileSensor to create event-driven workflows
- **Cross-DAG Orchestration**: Demonstrates how one DAG can control another
- **Synchronous Execution**: Waits for the triggered DAG to complete before proceeding
- **Automatic Cleanup**: Removes trigger files to enable reusable workflows
- **Error Handling**: Uses safe file removal to prevent pipeline failures

### Using the Controller DAG

To trigger the data processing pipeline via the controller DAG:

1. **Create the trigger directory** (if it doesn't exist):
   ```bash
   docker-compose exec airflow-webserver mkdir -p /opt/airflow/trigger_files
   ```
2. **Unpause and trigger the dag_controller_and_file_trigger** 
   First task turns green, it's waiting for the trigger file

3. **Create the trigger file** to start the pipeline:
   ```bash
   docker-compose exec airflow-webserver touch /opt/airflow/trigger_files/run
   ```

4. **Monitor the controller DAG** in the Airflow UI:
   - The `wait_for_trigger_file` task will detect the file
   - The `trigger_target_dag` task will launch `dag_1` and wait for completion
   - The `remove_trigger_file` task will clean up the trigger file

5. **Check the triggered DAG**:
   - Navigate to `dag_1` in the UI to see the triggered run
   - Both DAGs will show their execution status and logs

### Multi-DAG Architecture Benefits

- **Separation of Concerns**: Controller logic is separate from business logic
- **Reusability**: The same controller pattern can trigger multiple different DAGs
- **Event-Driven**: Enables external systems to trigger Airflow pipelines
- **Monitoring**: Clear visibility into both trigger events and pipeline execution
- **Flexibility**: Easy to modify trigger conditions without changing the main pipeline

## Troubleshooting

If you encounter issues:

1. **Check if ports are available:**
   ```bash
   lsof -i :8080
   ```

2. **Restart the services:**
   ```bash
   docker-compose restart
   ```

3. **Check service logs:**
   ```bash
   docker-compose logs airflow-webserver
   docker-compose logs airflow-scheduler
   ```

4. **View DAG parsing errors:**
   ```bash
   docker-compose logs airflow-scheduler | grep -i error
   ```

### Controller DAG Specific Issues

5. **FileSensor not detecting files:**
   ```bash
   # Check if the trigger directory exists
   docker-compose exec airflow-webserver ls -la /opt/airflow/trigger_files/
   
   # Create the directory if it doesn't exist
   docker-compose exec airflow-webserver mkdir -p /opt/airflow/trigger_files
   ```

6. **Check FileSensor task logs:**
   ```bash
   # View FileSensor specific logs
   docker-compose logs airflow-scheduler | grep -i "wait_for_trigger_file"
   ```

7. **Verify trigger file creation:**
   ```bash
   # Create trigger file manually for testing
   docker-compose exec airflow-webserver touch /opt/airflow/trigger_files/run
   
   # Verify the file exists
   docker-compose exec airflow-webserver ls -la /opt/airflow/trigger_files/run
   ```

8. **Monitor cross-DAG triggering:**
   ```bash
   # Check TriggerDagRunOperator logs
   docker-compose logs airflow-scheduler | grep -i "trigger_target_dag"
   ```

