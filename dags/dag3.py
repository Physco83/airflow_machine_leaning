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
    week_difference = 57
    constant_cut = 5

    from timeit import default_timer as timer

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    import numpy as np
    import scipy.stats as sps
    import scipy.optimize as spo

    

    from sklearn import preprocessing, svm
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    from sklearn.metrics import mean_squared_error


    import matplotlib
    import math
    from scipy.stats import gamma
    import functools
    import itertools

    # import psycopg2
    # from sqlalchemy import create_engine
    # from psycopg2 import Error
    # from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    import pyspark
    from pyspark.sql import Row
    from datetime import datetime, date
    from pyspark.sql.functions import col,when, lit
    from pyspark.ml.regression import LinearRegression
    from pyspark.ml.feature import VectorAssembler
    from pyspark.ml.regression import GeneralizedLinearRegression
    from pyspark.ml.evaluation import RegressionEvaluator

    from pyspark.sql import SparkSession

    config = pyspark.SparkConf().setAll([("spark.jars", "/java/postgresql-42.6.0.jar"), ('spark.executor.memory', '8g'), ('spark.executor.cores', '4'), ('spark.cores.max', '4'), ('spark.driver.memory','8g')])
    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .config(conf=config) \
        .getOrCreate()

    # print("Hello")
    # print(spark.sparkContext.getConf().getAll())
    # print("Bye")

    
    print_plots = False

    # суммированные продаж за день каждого продукта каждого рассматриваемого дня 

    def make_df_by_date(product_name, df_merge):
      df_temp = df_merge.filter('product_name == "{}"'.format(product_name)).sort(df_merge.date.asc())
      temp  = df_temp.withColumn("revenue", col("sales_qty_base") * (col("sales_qty") * col("price"))).groupBy('date').sum('revenue')
      temp2 = df_temp.withColumn("sales_amount", col("sales_qty_base") * (col("sales_qty"))).groupBy('date').sum('sales_amount')
      temp3 =  temp.join(temp2, on=["date"])
      temp3 = temp3.toDF('date', 'revenue', 'sales_amount')

      df_binary = temp3.withColumn("price", col("revenue") / (col("sales_amount"))).select(['price','sales_amount'])
      df_binary = df_binary.withColumn('product_name', lit(product_name))
      
      return df_binary

    # Generate a set of hypothesis. I use linear demand functions 
    # for the sake of illustration, although it is reasonable 
    # choice for production as well
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

    def logx(x, n): 
        for i in range(0, n):
            x = math.log(x) if x>0 else 0
        return x

    def rounds(m, T, scale):
        mask = []
        for i in range(1, m):
            mask.extend( np.full(scale * math.ceil(logx(T, m - i)), i-1) )
        return np.append(mask, np.full(T - len(mask), m-1))


    def print_return_lin_hypothesisies(df_binary):
      vectorAssembler = VectorAssembler(inputCols = ['price'], outputCol = 'features')
      vhouse_df = vectorAssembler.transform(df_binary)

      splits = vhouse_df.randomSplit([0.7, 0.3])
      train_df = splits[0]
      test_df = splits[1]

      glr = GeneralizedLinearRegression(featuresCol = 'features', labelCol='sales_amount', family="poisson", link="identity", maxIter=10, regParam=0.3)

      # Fit the model
      model = glr.fit(train_df)

    # вычисление отклонений при линейной регресии по истории рассматриваемого продукта
      summary = model.summary
      k = model.coefficients[0]
      b = model.intercept
      k_err, b_err = summary.coefficientStandardErrors
      # Summarize the model over the training set and print out some metrics
      if print_plots:
        print(f"k = {k:0.4f} ± {k_err:0.4f}")
        print(f"b = {b:0.4f} ± {b_err:0.4f}")

    # отображение линий гипотез вместе с историческими данными рассматриваемого продукта
      start = k-k_err
      end = k+k_err
      startb = b-b_err
      endb = b+b_err
      # A list of demand function hypotheses and corresponding optimal prices
      h_vec = list(demand_hypotheses(np.linspace(start, end, 4), np.linspace(startb, endb, 5)))
      if print_plots:

        price_min = df_binary.agg({"price": "min"}).collect()[0][0]
        price_max = df_binary.agg({"price": "max"}).collect()[0][0]
        continuation = price_max - price_min
        prices = np.linspace(price_min - 3*continuation, price_max + 3*continuation, 100)

        fig = plt.figure(figsize=(10, 8))
        plt.xlabel('Цена (руб за кг/литр)')
        plt.ylabel('Количество продаж (кг/литры)')
        product_name = df_binary.rdd.map(lambda x: x['product_name']).collect()[0]
        plt.title('График гипотез функций зависимости цены от спроса продукта ' + str(product_name))
        plt.grid(True)

      # x = [row.price for row in df_binary.select('price').collect()]
      # y = [row.sales_amount for row in df_binary.select('sales_amount').collect()]
        x = df_binary.rdd.map(lambda x: x['price']).collect()
        y = df_binary.rdd.map(lambda x: x['sales_amount']).collect()
        plt.scatter(x,y)
      # df_binary.toPandas().set_index('price').plot()
        for d in h_vec:
            plt.plot(prices, list(map(d['d'], prices)), 'r-')
            plt.plot([d['p_opt']], d['d'](d['p_opt']), 'kx', linewidth=2)

        plt.show()
      return h_vec


    # самая главная функция, выполняющая вычисление и предсказывания цены на новой временной период
    def optimization_reinforced_learning(df_binary, h_vec):
      time11= timer()
      print(type(df_binary))
      # df_binary.show()

      actual_demand = [data[0] for data in df_binary.select('sales_amount').collect()]

      # actual_demand = df_binary.rdd.map(lambda x: x['sales_amount']).collect()

      # actual_demand = df_binary.select(col("sales_amount").map(f=>f.getString(0)).collect.toList
      # actual_demand = df_binary.select(['sales_amount']).rdd.map(r => r(0)).collect()
      


      T = df_binary.count() + 1  # time step is one hour, 10 days total 
      print(timer()-time11)
      m = 4       # not more than 4 price updates

      tau = 0
      d = h_vec[0]['d']
      p = h_vec[0]['p_opt']

      t_mask = rounds(m, T, 2)                      # generate the price change schedule in advance
      prev_demand = actual_demand[0]
      history = []
      for t in range(0, T-1):  
          # print(t_mask)                     # simulation loop
          # realized_d = sample_actual_demand(p)
          realized_d = actual_demand[t]
          # print(tau, t + 1)
          
          history.append([p, realized_d, d, p])
          # if( t_mask[t] != t_mask[t + 1] ):         # it's time to re-optimize the price
          demand_change = abs(prev_demand / realized_d - 1)
          if( demand_change > 0.05 ):         # it's time to re-optimize the price
              interval_demands = np.array(history)[tau : t + 1, 1]
              # print(interval_demands)
              interval_avg_demand = np.mean(interval_demands)
              
              min_error = float("inf")
              for i, h in enumerate(h_vec):                      # look for a hypothesis that explains 
                  error = abs(interval_avg_demand - h['d'](p))   # the observed data with a minimal error
                  if(error < min_error):
                      min_error = error
                      h_opt = h
              # print("-----------")   
              p = h_opt['p_opt']                    # optimal price for the next price period 

              d = h_opt['d']
              prev_demand = realized_d
              # print( np.array(history)[:, 1])
              tau = t+1  
              
      history = np.array(history)
      if print_plots:

        t = len(history)-1
        product_name = df_binary.rdd.map(lambda x: x['product_name']).collect()[0]
        plt.title('График изменения цены продукта ' + str(product_name))
        plt.plot(range(0, t+1), history[0:t+1,0], 'r-', label='Price') 
        print(history[0:t+1,0])
      # history[-1,0] есть предсказанная цена на новой временной период
      return history








    url = "jdbc:postgresql://postgres:5432/abt"

    
    date_finish =   datetime.today() -  timedelta(weeks=week_difference)
    date_start = date_finish - timedelta(weeks=5)
    
    df_merge = spark.read \
        .format("jdbc") \
        .option("url", url) \
        .option("query", '''
                           select price_history.*, product.product_name from price_history inner join product on price_history.product_id=product.product_id where date >='{}' and date<'{}'
                         '''.format(date_start, date_finish)) \
        .option("user", "airflow") \
        .option("password", "airflow") \
        .option("driver", "org.postgresql.Driver") \
        .load()

    # df.show()

    # поиск всех уникальных позиций и количество их продаж
    product_all_sales = df_merge.groupBy('product_name').count().orderBy('count', ascending=False)


    df_time = pd.DataFrame(columns=['df_binary', 'h_vec', 'optimization', 'sum'])

    index = 0
    parame = 4
    # df_binary = spark.read.option('header', 'true').csv('merge.csv', inferSchema=True)
    for row in product_all_sales.rdd.collect():
      print(index)
      time1 = timer()
      df_binary = make_df_by_date(row['product_name'], df_merge)
      time2 = timer() - time1
      # df_binary.show()
      h_vec = print_return_lin_hypothesisies(df_binary)
      time3 = timer()- time1
      optimization_reinforced_learning(df_binary, h_vec)
      time4 = timer()- time1
      # print([time2,time3,time4])
      df_time.loc[index] = [time2,time3,time4, time2+time3+time4]
      index = index + 1
      if (index == parame):
        break

    print(df_time['sum'].sum())
    print(df_time)





    

    return 2


#dag_id = "dag is dag not a dag"
ds = datetime(2022,2,15)
# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="my_third_dagV5", start_date=datetime(2022, 1, 1), schedule_interval="@weekly", catchup=False) as dag:

     
    fo = PythonOperator(
        task_id="fo",
        python_callable = foo1
    )


    fo




 # try:
    #     # Подключение к существующей базе данных
    #     connection = psycopg2.connect(user="airflow",
    #                                   # пароль, который указали при установке PostgreSQL
    #                                   password="airflow",
    #                                   host="postgres",
    #                                   port="5432",
    #                                   dbname="abt")
    #     connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    #     cursor = connection.cursor()
        
    #     date_finish =   datetime.today() -  timedelta(weeks=week_difference)
    #     date_start = date_finish - timedelta(weeks=1)
    #     sql_weekly_price_history = '''
    #         select * from price_history ph where ph."date" >='{}' and ph."date" <='{}' 
    #     '''.format(date_start, date_finish)
    #     # print(sql_weekly_price_history)
    #     cursor.execute(sql_weekly_price_history)
        
    #     record = cursor.fetchall()
    #     print("SQL result - ", record, "\n")

    # except (Exception, Error) as error:
    #     print("Ошибка при работе с PostgreSQL", error)
    # finally:
    #     if connection:
    #         cursor.close()
    #         connection.close()
    #         print("Соединение с PostgreSQL закрыто")