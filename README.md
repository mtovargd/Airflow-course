# Airflow Course - Docker Setup

This project contains an Apache Airflow setup using Docker Compose to run your DAGs.

## Files Structure

```
.
├── docker-compose.yml    # Docker Compose configuration
├── .env                 # Environment variables
├── dags/               # Directory for DAG files
│   └── jobs_dag.py     # Your DAG file
├── logs/               # Airflow logs
├── plugins/            # Custom plugins
└── config/             # Configuration files
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

### Your DAG Details

Your `jobs_dag.py` creates three separate DAGs:
- `dag_1`: Processes `table_name_1`
- `dag_2`: Processes `table_name_2`
- `dag_3`: Processes `table_name_3`

Each DAG has three tasks:
1. `print_info`: Prints information about the DAG and table
2. `insert_new_row`: Dummy task simulating row insertion
3. `query_the_table`: Dummy task simulating table query

Tasks run in sequence: print_info → insert_new_row → query_the_table

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

4. **Ensure proper permissions:**
   ```bash
   sudo chown -R $USER:$USER logs dags plugins
   ```
