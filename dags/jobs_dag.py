from datetime import datetime
from airflow import DAG
from airflow.operators.dummy import DummyOperator

config = {
    'dag_id_1': {
        'schedule_interval': None,
        'start_date': datetime(2023, 1, 1)
    },
    'dag_id_2': {
        'schedule_interval': None,
        'start_date': datetime(2024, 6, 1)
    },
    'dag_id_3': {
        'schedule_interval': None,  # Only triggered manually
        'start_date': datetime(2025, 1, 1)
    }
}

for dag_id, dag_params in config.items():
    with DAG( 
        dag_id=dag_id,
        schedule_interval=dag_params['schedule_interval'],
        start_date=dag_params['start_date'],
        catchup=False,
        tags=["auto_generated"]
    ) as dag:
        start = DummyOperator(task_id='start')
    
    globals()[dag_id] = dag