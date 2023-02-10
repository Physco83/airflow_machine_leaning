from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import airflow.models.taskinstance as ti



#ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
#DAG_ID = "postgres_operator_dag"

default_args = {
    'owner': 'stas1',
    'retries': 5, 
    'retry_delay': timedelta(minutes=5)

}


def _calculate_optimal_prices(**kwargs):
    #ti = kwargs['ti']
   
    return "dag is dag not a dag22"


#dag_id = "dag is dag not a dag"
ds = datetime(2022,2,16)
# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="my_second_dagV6", 
    start_date=datetime(2022, 1, 1), 
    schedule_interval="@weekly", 
    catchup=False) as dag:

     
    save_new_data = PostgresOperator( #postgresOperator??
        task_id="save_new_data",
        postgres_conn_id='postgres_localhost',
        sql="""
            CREATE TABLE IF NOT EXISTS tutor (
                tutor_id serial primary key, 
                name VARCHAR(20),
                speciality VARCHAR(20)
            )
          """,

    )


    calculate_optimal_prices = PythonOperator(
        task_id="calculate_optimal_prices",
        python_callable = _calculate_optimal_prices

    )

    insert_task = PostgresOperator(
        task_id="insert_task",
        postgres_conn_id='postgres_localhost',
        sql='''
            insert into tutor (tutor_id, name, speciality) VALUES (default, 'Vinok', 'dag_id')
        ''',
        #parameters={"dag_id": "{{ti.xcom_pull('calculate_optimal_prices')}}", "ds": ds},
        #parameters={"ds": ds},

    )

    [calculate_optimal_prices, save_new_data] >> insert_task

