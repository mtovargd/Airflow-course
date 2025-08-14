FROM apache/airflow:2.7.1

USER airflow
RUN pip install --no-cache-dir apache-airflow-providers-postgres apache-airflow-providers-hashicorp slack-sdk
