# Airflow Course - Docker Setup

This project contains an Apache Airflow setup using Docker Compose to run your DAGs.

## Files Structure

```
.
├── docker-compose.yml         # Docker Compose configuration
├── .env                      # Environment variables
├── dags/                     # Directory for DAG files
│   ├── jobs_dag.py          # Dynamic DAG loader
│   └── tutorial_example.py  # Example DAG (commented out)
├── dag_sources/              # Source DAG definitions
│   ├── source_1/
│   │   └── source_1.py      # DAG 1 definition
│   └── source_2/
│       ├── source_2.py      # DAG 2 definition
│       └── source_3.py      # DAG 3 definition
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

### Dynamic DAG Loading

The `dags/jobs_dag.py` file uses Airflow's `DagBag` to dynamically load DAGs from the `dag_sources/` directory structure. This approach allows for:
- Modular DAG organization
- Easy addition of new DAGs
- Separation of concerns between DAG loading and DAG definition

### Your DAG Details

Three DAGs are automatically loaded from the source directories:

- **`dag_1`**: Processes `table_1` in `db_1` database
- **`dag_2`**: Processes `table_2` in `db_2` database  
- **`dag_3`**: Processes `table_3` in `db_3` database

### DAG Structure

Each DAG follows the same pattern with three sequential tasks:

1. **`start_processing_log`**: Python task that logs the start of processing
   - Prints: "'{dag_id}' has started processing tables in the '{database}' database."
2. **`insert_new_row`**: Dummy task simulating row insertion
3. **`query_the_table`**: Dummy task simulating table query

**Task Flow**: `start_processing_log` → `insert_new_row` → `query_the_table`

### DAG Configuration

Each DAG uses a configuration dictionary with:
- **Schedule**: Manual trigger only (`schedule_interval=None`)
- **Start Date**: January 1, 2023
- **Catchup**: Disabled
- **Database and Table**: Specific to each DAG

### Troubleshooting

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

