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
    week_difference = 43

    
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import datetime

    constant_cut = 5
    import numpy as np
    import scipy.stats as sps
    import scipy.optimize as spo

    

    from sklearn import preprocessing, svm
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    # import seaborn as sns
    from sklearn.metrics import r2_score
    from sklearn.metrics import mean_squared_error


    import matplotlib
    import math
    from scipy.stats import gamma
    import functools
    import itertools

    import psycopg2
    from sqlalchemy import create_engine
    from psycopg2 import Error
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT



    def lin_reg(df_binary):
      # sns.lmplot(x ="price", y ="sales_amount", data = df_binary, order = 1, ci = None)

      X = np.array(df_binary['price']).reshape(-1, 1)
      y = np.array(df_binary['sales_amount']).reshape(-1, 1)

      # Separating the data into independent and dependent variables
      # Converting each dataframe into a numpy array 
      # since each dataframe contains only one column
      df_binary.dropna(inplace = True)

      # Dropping any rows with Nan values
      #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25)

      # Splitting the data into training and testing data
      regr = LinearRegression()

      regr.fit(X, y)
      print(regr.score(X, y))
      #y = kx+b
      k = regr.coef_.round(3)[0][0]
      b = regr.intercept_.round(1)[0]
      if (regr.intercept_.round(1)[0] > 0):
        print('y = {}*x+{}'.format(k, b))
      else: 
        print('y = {}*x{}'.format(k, b))
      x_predict = np.linspace( np.array(df_binary['price']).reshape(-1, 1).min(), np.array(df_binary['price']).reshape(-1, 1).max(), 10)
      y_predict = k*x_predict + b
      plt.scatter(X, y, color ='b')
      plt.plot(x_predict, y_predict, color ='r')
      plt.show()

    df_binary = pd.DataFrame()
    def print_graphic_and_show_metrics(product_name):
      df_temp = df_merge.loc[df_merge['product_name'] == product_name].sort_values(by=['date'])

      temp = df_temp.groupby('date').apply(lambda x: x['sales_qty_base']*x['sales_qty']*x['price'])
      temp2 = df_temp.groupby('date').apply(lambda x: x['sales_qty_base']*x['sales_qty'])

      temp3 = pd.DataFrame([temp.groupby(level=[0]).sum(), temp2.groupby(level=[0]).sum()]).transpose()
      temp3.columns=['revenue','sales_amount']

      temp3 = temp3.reset_index()
      temp3['price'] = temp3['revenue']/temp3['sales_amount']

      df_binary = temp3[['price', 'sales_amount']]
      df_binary['product_name'] = pd.Series([product_name]*df_binary.shape[0])
      
      lin_reg(df_binary)
      return df_binary



    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres:5432/abt")
    # Connect to PostgreSQL serve
    dbConnection    = engine.connect();
    # Read data from PostgreSQL database table and load into a DataFrame instance
    date_finish =   datetime.datetime.today() -  timedelta(weeks=week_difference)
    date_start = date_finish - timedelta(weeks=5)
    df_merge = pd.read_sql('''
             select * from price_history inner join product on price_history.product_id=product.product_id where date >='{}' and date<'{}'
         '''.format(date_start, date_finish), dbConnection);
    # print(df_merge)
   
    temp6 = pd.value_counts(df_merge['product_name'].values.ravel())
    temp6 = temp6.reset_index()
    temp6.columns = ['product_name', 'sales_amount']

    for index, row in temp6.iterrows():
    # print(index)
      df_binary = print_graphic_and_show_metrics(row['product_name'])
      if (index == 1):
        break


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

    start = a-a_err
    end = a+a_err
    startb = b-b_err
    endb = b+b_err
    # A list of demand function hypotheses and corresponding optimal prices
    h_vec = list(demand_hypotheses(np.linspace(start, end, 4), np.linspace(startb, endb, 5)))

    prices = np.linspace(0, 100, 100)
    fig = plt.figure(figsize=(10, 8))
    plt.xlabel('Цена (руб за кг/литр)')
    plt.ylabel('Количество продаж (кг/литры)')
    # plt.ylim(0, 380)
    plt.title('График гипотез функций зависимости цены от спроса')
    plt.grid(True)
    plt.scatter(x,y)
    for d in h_vec:
        plt.plot(prices, list(map(d['d'], prices)), 'r-')
        plt.plot([d['p_opt']], d['d'](d['p_opt']), 'kx', linewidth=2)
    # x = np.arange(0, 1600)
    # plt.plot(x, 300 -0.16*x)
    plt.show()





    actual_demand = df_binary['sales_amount'].values.tolist()

    def sample_actual_demand(price): 
        avg_demand = a + b * price
        theta = 0.1/4
        k = avg_demand / theta
        # print(k*theta)
        return np.random.gamma(k*theta, k*theta**2, 1)[0]

    def emperical_mean(sampler, n): 
        mean = 0 
        for i in range(1, n): 
            mean = mean + sampler() 
        return mean/n

    def emperical_demand_curve(min_price, max_price, n): 
        prices = np.linspace(min_price, max_price, n) 
        sampling = 5000 
        demands = map(lambda p: emperical_mean(functools.partial(sample_actual_demand, p), sampling), prices) 
        return np.dstack((prices, list(demands)))[0]

    curve = np.transpose(emperical_demand_curve(50, 100, 20))

    fig = plt.figure(figsize=(10, 8))
    for i, d in enumerate(h_vec):
        plt.plot(prices, list(map(d['d'], prices)), '-', color='#555555');
        plt.plot([d['p_opt']], d['d'](d['p_opt']), 'ko', markeredgewidth=1.5, markerfacecolor='w', markersize=10)

    # price = np.linspace(1000, 1800, 21)    
    # plt.plot(curve[0], curve[1], 'r--', linewidth=3.0, label='True demand function')
    # plt.plot(price, 65 + (-0.8) * price, color = 'blue', linewidth=3.0, label='Fuck demand function')
    plt.xlabel('Price ($)')
    plt.ylabel('Demand (Units)')
    # plt.ylim(0, 72)
    plt.grid(True)
    plt.legend()
    plt.savefig('hypoteses.pdf')

    plt.show()






    # Simulation of dynamic price optimization

    def logx(x, n): 
        for i in range(0, n):
            x = math.log(x) if x>0 else 0
        return x

    def rounds(m, T, scale):
        mask = []
        for i in range(1, m):
            mask.extend( np.full(scale * math.ceil(logx(T, m - i)), i-1) )
        return np.append(mask, np.full(T - len(mask), m-1))

    T = df_binary.shape[0]+1  # time step is one hour, 10 days total 
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

    t = len(history)-1

    # plt.plot(range(0, t+1), history[0:t+1,0], 'r-', label='Price') 
    print(history[0:t+1,0])

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