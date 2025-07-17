# Airflow Course - Docker Setup

This project contains an Apache Airflow setup using Docker Compose to run your DAGs.

## Files Structure

```
.
├── docker-compose.yml         # Docker Compose configuration
├── .env                      # Environment variables
├── dags/                     # Directory for DAG files
│   ├── jobs_dag.py          # Dynamic DAG generator with branching logic
│   └── tutorial_example.py  # Example DAG (commented out)
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
   - Once logged in, you should see your three DAGs: `dag_1`, `dag_2`, and `dag_3`
   - Click on any DAG to view its structure and run it

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

### Dynamic DAG Generation

The `dags/jobs_dag.py` file uses a configuration-driven approach to dynamically generate multiple DAGs from a single Python file. This approach provides:
- Centralized DAG configuration
- Easy scaling to multiple DAGs
- Consistent branching logic across all DAGs
- Reduced code duplication

### Your DAG Details

Three DAGs are automatically generated from the configuration dictionary:

- **`dag_1`**: Processes `table_1` in `db_1` database (Start: 2023-01-01)
- **`dag_2`**: Processes `table_2` in `db_2` database (Start: 2024-01-01)
- **`dag_3`**: Processes `table_3` in `db_3` database (Start: 2025-01-01)

### DAG Structure with Branching Logic

Each DAG follows the same pattern with **conditional branching**:

1. **`start_processing_log`**: Python task that logs the start of processing
   - Prints: "'{dag_id}' has started processing tables in the '{database}' database."
   
2. **`check_if_table_exists`**: BranchPythonOperator that determines the next path
   - Currently always returns 'insert_new_row' (simulating table exists)
   - In production, this would check if the table exists in the database
   
3. **Branching paths**:
   - **`create_the_table`**: Dummy task (runs if table doesn't exist)
   - **`insert_new_row`**: Dummy task (runs if table exists)
   
4. **`query_the_table`**: Final dummy task that runs after either branch

### Task Flow Diagram

```
start_processing_log
        │
        ▼
check_if_table_exists
        │
        ├─── create_the_table ───┐
        │                        │
        └─── insert_new_row ─────┤
                                 │
                                 ▼
                         query_the_table
```

### DAG Configuration

Each DAG uses a configuration dictionary with:
- **Schedule**: Manual trigger only (`schedule_interval=None`)
- **Start Date**: Different years (2023, 2024, 2025)
- **Catchup**: Disabled
- **Tags**: `["dynamic_branching"]`
- **Database and Table**: Specific to each DAG

### Key Features

- **Branching Logic**: Uses `BranchPythonOperator` to conditionally execute tasks
- **Dynamic Generation**: Single configuration change creates/modifies all DAGs
- **Proper Task Dependencies**: Handles parallel branches that converge to a final task
- **Global Registration**: Each generated DAG is registered in the global namespace

### Additional Files

- **`tutorial_example.py`**: Contains a commented-out weekday branching example DAG for reference

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

