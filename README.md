# Airflow Course - Docker Setup

This project contains an Apache Airflow setup using Docker Compose to run your DAGs.

## Files Structure

```
.
├── docker-compose.yml         # Docker Compose configuration
├── .env                      # Environment variables
├── dags/                     # Directory for DAG files
│   └── jobs_dag.py          # Single DAG with branching logic and mixed operators
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

4. **View your DAG:**
   - Once logged in, you should see your single DAG: `dag_1`
   - Click on the DAG to view its structure and run it

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

