from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
DAG_ID = "postgres_operator_dag"



default_args = {
    'owner': 'stas1',
    'retries': 5, 
    'retry_delay': timedelta(minutes=5)

}

def _get_new_data():
    return 2

def _calculate_optimal_prices():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import datetime

    constant_cut = 5
    import numpy as np
    import scipy.stats as sps
    import scipy.optimize as spo

    import matplotlib
    import math
    from scipy.stats import gamma
    import functools
    import itertools


    import matplotlib.pyplot as plt


    from sklearn import preprocessing, svm
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    from sklearn.metrics import mean_squared_error
    
    import psycopg2
    from sqlalchemy import create_engine
    from psycopg2 import Error
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    pd.options.mode.chained_assignment = None

    def make_product_df(product_name):
      df_temp = df_merge.loc[df_merge['product_name'] == product_name].sort_values(by=['date'])

      temp = df_temp.groupby('date').apply(lambda x: x['sales_qty_base']*x['sales_qty']*x['price'])
      temp2 = df_temp.groupby('date').apply(lambda x: x['sales_qty_base']*x['sales_qty'])

      temp3 = pd.DataFrame([temp.groupby(level=[0]).sum(), temp2.groupby(level=[0]).sum()]).transpose()
      temp3.columns=['revenue','sales_amount']
      temp3 = temp3.reset_index()
      temp3['price'] = temp3['revenue']/temp3['sales_amount']

      df_binary = temp3[['price', 'sales_amount']]
      df_binary['product_name'] = [product_name]*df_binary.shape[0]
      
      return df_binary


    def linear(a, b, x):
        return b + a*x

    # A linear demand function is generated for every 
    # pair of coefficients in vectors a_vec and b_vec 
    def demand_hypotheses(a_vec, b_vec):
        for a, b in itertools.product(a_vec, b_vec):
            yield {
                'd': functools.partial(linear, a, b),   # price-demand function
                'p_opt': -b/(2*a)                      # corresponding optimal price 
            }


    def calc_metric(df_binary):
      x = df_binary['price'].values.tolist()
      y = df_binary['sales_amount'].values.tolist()
      n = len(x)
      lin_model = sps.linregress(x, y)
      a,b = lin_model.slope, lin_model.intercept
      a_err, b_err = lin_model.stderr, lin_model.intercept_stderr
      a_conf = sps.t.interval(0.95, df = n-2, loc=a, scale=a_err)
      b_conf = sps.t.interval(0.95, df = n-2, loc=b, scale=b_err)
      print(f"a = {a:0.4f} ± {a_err:0.4f}, доверительный интервал α=5% [{a_conf[0]:0.4f} ; {a_conf[1]:0.4f}]")
      print(f"b = {b:0.4f} ± {b_err:0.4f}, доверительный интервал α=5% [{b_conf[0]:0.4f} ; {b_conf[1]:0.4f}]")
      start = a-a_err
      end = a+a_err
      startb = b-b_err
      endb = b+b_err
      return list(demand_hypotheses(np.linspace(start, end, 4), np.linspace(startb, endb, 5)))

    
    # Simulation of dynamic price optimization
    def simulation_din_price(df_binary):
      actual_demand = df_binary['sales_amount'].values.tolist()

      def logx(x, n): 
          for i in range(0, n):
              x = math.log(x) if x>0 else 0
          return x

      def rounds(m, T, scale):
          mask = []
          for i in range(1, m):
              mask.extend( np.full(scale * math.ceil(logx(T, m - i)), i-1) )
          return np.append(mask, np.full(T - len(mask), m-1))

      T = df_binary.shape[0]+1  # time step is one hour
      m = 4       # not more than 4 price updates

      tau = 0
      d = h_vec[0]['d']
      p = h_vec[0]['p_opt']

      t_mask = rounds(m, T, 2)                      # generate the price change schedule in advance
      prev_demand = actual_demand[0]
      history = []
      for t in range(0, T-1):  
          realized_d = actual_demand[t]
          
          history.append([p, realized_d, d, p])

          demand_change = abs(prev_demand / realized_d - 1)
          if( demand_change > 0.05 ):         # it's time to re-optimize the price
              interval_demands = np.array(history)[tau : t + 1, 1]
              interval_avg_demand = np.mean(interval_demands)
              
              min_error = float("inf")
              for i, h in enumerate(h_vec):                      # look for a hypothesis that explains 
                  error = abs(interval_avg_demand - h['d'](p))   # the observed data with a minimal error
                  if(error < min_error):
                      min_error = error
                      h_opt = h
              p = h_opt['p_opt']                    # optimal price for the next price period 
              d = h_opt['d']
              prev_demand = realized_d
              tau = t+1  
      return history





    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres:5432/abt")
    # Connect to PostgreSQL serve
    dbConnection    = engine.connect();
    # Read data from PostgreSQL database table and load into a DataFrame instance
    week_difference = 43
    date_finish =   datetime.datetime.today() -  timedelta(weeks=week_difference)
    date_start = date_finish - timedelta(weeks=5)
    df_merge = pd.read_sql('''
             select * from price_history inner join product on price_history.product_id=product.product_id where date >='{}' and date<'{}'
         '''.format(date_start, date_finish), dbConnection);

    
    temp6 = pd.value_counts(df_merge['product_name'].values.ravel())
    temp6 = temp6.reset_index()
    temp6.columns = ['product_name', 'sales_amount']
    

    df_pph = pd.DataFrame()
    for index, row in temp6.iterrows():
        # print(index)
        df_binary = make_product_df(row['product_name'])
        # print_graphic_and_show_metrics(df_binary)
        h_vec = calc_metric(df_binary)
        history = np.array(simulation_din_price(df_binary))
        df_pph = df_pph.append(pd.DataFrame([[datetime.datetime.today(), history[-1,0], row['product_name']]], columns=['date', 'price', 'product_id']))
        if (index == 2):
            break


    df_pph.to_sql('price_prediction_history', dbConnection, if_exists='append', index=False)

    return 2

def _send_optimal_prices():
    # step 1 connect to db and read from price_prediction_history
    # send predictions to the client
    return 3


# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="my_first_dagV2", start_date=datetime(2022, 1, 1), schedule_interval="@weekly", catchup=False) as dag:

    get_save_new_data = PythonOperator(
        task_id="get_save_new_data",
        python_callable = _get_new_data

    )

    # save_new_data = PostgresOperator( #postgresOperator??
    #     task_id="save_new_data",
    #     postgres_conn_id='postgres_localhost',
    #     sql="""
    #         CREATE TABLE IF NOT EXISTS pet (
    #         pet_id SERIAL PRIMARY KEY,
    #         name VARCHAR NOT NULL,
    #         pet_type VARCHAR NOT NULL,
    #         birth_date DATE NOT NULL,
    #         OWNER VARCHAR NOT NULL);
    #       """,

    # )

    calculate_save_optimal_prices = PythonOperator(
        task_id="calculate_save_optimal_prices",
        python_callable = _calculate_optimal_prices

    )

    

    send_optimal_prices = PythonOperator(
        task_id="send_optimal_prices",
        python_callable = _send_optimal_prices

    )



    # Tasks are represented as operators
    # hello = BashOperator(task_id="hello", bash_command="echo hello")

    # @task()
    # def airflow():
    #     print("airflow")

    # Set dependencies between tasks
    get_save_new_data  >> calculate_save_optimal_prices >>  send_optimal_prices
