from airflow.models import DagBag

# The list of directories to scan for DAGs
dags_dirs = ['/opt/airflow/dag_sources/source_1', 
             '/opt/airflow/dag_sources/source_2']

# Loop through each specified directory path
for dir in dags_dirs:

    # Use DagBag to parse all files in the CURRENT directory
    dag_bag = DagBag(dir, include_examples=False)

    # If the DagBag found any DAGs, add them to the global namespace
    if dag_bag:
        for dag_id, dag in dag_bag.dags.items(): 
            globals()[dag_id] = dag