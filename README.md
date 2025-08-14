
# Airflow Capstone: Event-Driven Data Pipeline with Slack Notifications

This project demonstrates a robust Apache Airflow setup using Docker Compose. It features a main ETL pipeline with PostgreSQL, a controller DAG for event-driven orchestration, a custom Airflow operator, and Slack notifications.

---

## Project Structure

```
.
├── docker-compose.yml
├── .env
├── dags/
│   ├── jobs_dag.py                # Main ETL pipeline DAG
│   └── packaged_slack_dag.zip     # Controller DAG (zipped)
├── plugins/
│   └── operators/
│       └── postgres_count_rows_operator.py  # Custom operator
├── trigger_files/                 # Used for file-based triggering
└── config/
```

---

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM for Docker
- A Slack workspace and a valid Slack Bot/User OAuth token

---

## Setup & Running

### 1. Clone and Start Airflow

```bash
docker-compose up -d --build
```

Wait a few minutes for Airflow and Postgres to initialize.

---


### 2. Configure Airflow

#### a. Open the Airflow UI and Log In

1. Open your browser and go to [http://localhost:8080](http://localhost:8080)
2. Login with:
   - Username: `admin`
   - Password: `admin`

#### b. Set up the Postgres Connection

3. In the Airflow UI, go to **Admin → Connections**.
4. Add a new connection:
   - **Conn Id:** `postgres_default`
   - **Conn Type:** `Postgres`
   - **Host:** `postgres`
   - **Schema:** `airflow`
   - **Login:** `airflow`
   - **Password:** `airflow`
   - **Port:** `5432`
   - Click **Test** and then **Save**.



#### b. Set the Slack Channel ID (in Airflow UI)

1. In the Airflow UI, go to **Admin → Variables**.
2. Add a new variable:
   - **Key:** `slack_channel_id`
   - **Value:** (Your Slack channel's ID)
   - *Tip: To find your channel ID, open Slack, click the channel name, and look for the ID in the channel details or URL.*

#### c. Store the Slack Token in HashiCorp Vault (not in Airflow UI)

1. Make sure the Vault service is running (it is included in `docker-compose.yml`).
2. Open a shell in the Vault container:
   ```bash
   docker ps  # Find the Vault container ID or name
   docker exec -it <vault_container_id_or_name> sh
   ```
3. Log in to Vault:
   ```bash
   vault login ZyrP7NtNw0hbLUqu7N3IlTdO
   ```
4. Enable the secrets engine (if not already enabled):
   ```bash
   vault secrets enable -path=airflow -version=2 kv
   ```
5. Store your Slack token as a variable in Vault:
   ```bash
   vault kv put airflow/variables/slack_token value=YOUR_SLACK_TOKEN
   ```
   Replace `YOUR_SLACK_TOKEN` with your actual Slack Bot/User OAuth token (e.g. `xoxb-...`).

**Do NOT set the Slack token in the Airflow UI Variables page. Only set the channel ID as a variable.**

---

### 3. Unpause the DAGs

- In the Airflow UI, unpause:
  - `postgres_pipeline_example`
  - `packaged_controller_with_slack_and_vault`

---

### 4. Trigger the Pipeline

#### a. Create the trigger file (from your project folder):

```bash
touch trigger_files/run
```

- This will start the controller DAG, which will trigger the main pipeline DAG.

#### b. Monitor Progress

- In the Airflow UI, watch both DAGs as they run.
- When finished, you should receive a Slack notification in your specified channel.

---

## DAGs Overview

### Main Pipeline: `postgres_pipeline_example`

- **ETL pattern:**  
  - Checks/creates a table, inserts a row, and counts rows using a custom operator.
- **Idempotent:**  
  - Can be run repeatedly without error.
- **Custom Operator:**  
  - `PostgreSQLCountRowsOperator` (see `plugins/operators/`).


### Controller: `packaged_controller_with_slack_and_vault`

- **Event-driven:**  
  - Waits for a file (`trigger_files/run`), triggers the main DAG, and sends a Slack notification on completion.
- **Slack channel configurable:**
  - The Slack channel is set via the Airflow Variable `slack_channel_id`. No code changes are needed to use a different channel—just update the variable in the Airflow UI.

---

## Troubleshooting

- **DAG not visible?**  
  - Check for syntax errors in the Airflow UI.
- **FileSensor stuck?**  
  - Make sure `trigger_files/run` exists on your host and you are running the command from your project folder.
- **Slack notification fails?**  
  - Ensure the `slack_token` variable is set in Vault and the `slack_channel_id` variable is set in Airflow (must be a channel ID, not a URL).

---

## Stopping & Cleaning Up

```bash
docker-compose down         # Stop services
docker-compose down -v      # Stop and remove all data
docker-compose logs -f      # View logs
```

---
