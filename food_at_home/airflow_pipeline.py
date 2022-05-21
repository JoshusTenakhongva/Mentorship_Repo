import json
import pandas as pd

from datetime import datetime
from airflow_functions import * 

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

with DAG( 
    dag_id= 'local_airflow_dag', 
    start_date= datetime( year=2022, month=2, day=1 ),
    schedule_interval= '* * * * *', 
    catchup= False
) as dag:  
    # Initialization 

    pass 
    # 1. Get info from API
    task_get_edamam_request= PythonOperator( 
        task_id= 'get_edamam_request', 
        python_callable= edamam_get, 
        do_xcom_push= True
    )

    # 2. Convert API request to Pandas DF
    task_parse_request= PythonOperator(
        task_id= 'parse_json_request', 
        python_callable= parse_json_request, 
        do_xcom_push= True
    )

    # 3. Insert DF into local MySQL database
    task_submit_mysql= PythonOperator( 
        task_id= 'submit_mysql', 
        python_callable= df_submit_mysql
    )

    # task_change_recipe_byday 

    task_get_edamam_request >> task_parse_request >> task_submit_mysql