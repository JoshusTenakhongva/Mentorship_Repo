import json
import pandas as pd

from datetime import datetime
from etl_functions import * 

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

with DAG( 
    dag_id= 'local_airflow_dag', 
    start_date= datetime( year=2022, month=2, day=1 ),
    schedule_interval= '0 0 * * *', 
    catchup= False
) as dag:  
    # Initialization

    # 0. Just test if airflow is working.
    # If this crashes, then it's a problem with airflow itself
    task_airflow_test= PythonOperator( 
        task_id= 'test', 
        python_callable= airflow_var_test
    )

    # 1. Decide on what query to look into 
    
    
    # 2. Get info from API
    task_get_edamam_request= PythonOperator( 
        task_id= 'get_edamam_request', 
        python_callable= edamam_get
    )

    # 3. Convert API request to Pandas DF
    task_clean_data= PythonOperator(
        task_id= 'clean_edamam_data', 
        python_callable= clean_edamam_data
    )
    
    

    # task_change_recipe_byday 
    task_airflow_test >> task_get_edamam_request >> task_clean_data

    
    
    '''
    # 3. Insert DF into local MySQL database
    task_submit_mysql= PythonOperator( 
        task_id= 'submit_mysql', 
        python_callable= df_submit_mysql
    )
    '''