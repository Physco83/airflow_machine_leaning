from datetime import datetime
import os
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
DAG_ID = "postgres_operator_dag"


def _get_new_data():
    return 2

def _calculate_optimal_prices():
    return 4

def _send_optimal_prices():
    return 3


def _save_new_data():
    return 5

def _save_optimal_data():
    return 6    

# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="my_first_dag", start_date=datetime(2022, 1, 1), schedule_interval="@weekly", catchup=False) as dag:

    get_new_data = PythonOperator(
        task_id="get_new_data",
        python_callable = _get_new_data

    )

    save_new_data = PostgresOperator( #postgresOperator??
        task_id="save_new_data",
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS pet (
            pet_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            pet_type VARCHAR NOT NULL,
            birth_date DATE NOT NULL,
            OWNER VARCHAR NOT NULL);
          """,

    )

    calculate_optimal_prices = PythonOperator(
        task_id="calculate_optimal_prices",
        python_callable = _calculate_optimal_prices

    )

    save_optimal_data = PythonOperator( #postgresOperator??
        task_id="save_optimal_data",
        python_callable = _save_optimal_data

    )

    send_optimal_prices = PythonOperator(
        task_id="send_optimal_prices",
        python_callable = _send_optimal_prices

    )



    # Tasks are represented as operators
    hello = BashOperator(task_id="hello", bash_command="echo hello")

    @task()
    def airflow():
        print("airflow")

    # Set dependencies between tasks
    get_new_data  >> save_new_data >> calculate_optimal_prices >> [save_optimal_data, send_optimal_prices]
    #>> hello >> airflow()