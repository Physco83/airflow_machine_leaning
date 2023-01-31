from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator

import airflow.models.taskinstance as ti

#ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
#DAG_ID = "postgres_operator_dag"

default_args = {
    'owner': 'stas1',
    'retries': 5, 
    'retry_delay': timedelta(minutes=5)

}

def foo1():
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    import sklearn
    df = pd.DataFrame()
    print(df)
    return 2


#dag_id = "dag is dag not a dag"
ds = datetime(2022,2,15)
# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="my_third_dagV1", start_date=datetime(2022, 1, 1), schedule_interval="@weekly", catchup=False) as dag:

     
    fo = PythonOperator(
        task_id="fo",
        python_callable = foo1

    )


    fo




