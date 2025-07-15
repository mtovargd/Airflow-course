from datetime import datetime
from airflow import DAG
from datetime import datetime

config = {
    'dag_id_1': {'schedule_interval': None, "start_date": datetime(2025, 7, 11)},  
    'dag_id_2': {'schedule_interval': None, "start_date": datetime(2025, 7, 11)},  
    'dag_id_3': {'schedule_interval': None, "start_date": datetime(2025 7, 11)}}

for dag in config:
    with DAG(dag_id = dag, start_date = dag.start_date, schedule = dag.schedule):
        print(dag)