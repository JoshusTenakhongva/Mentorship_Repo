import json
import pandas as pd

from datetime import datetime, timedelta
from etl_functions import * 

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

with DAG( 
    dag_id= 'local_airflow_dag', 
    start_date= datetime( year=2022, month=2, day=1 ),
    schedule_interval= '*/2 * * * *', 
    catchup= False, 
    dagrun_timeout=timedelta(seconds=60)
) as dag:  
    # Initialization

       
    # 2. Get info from API
    task_get_edamam_request = PythonOperator( 
        task_id = 'get_edamam_request', 
        python_callable = edamam_request
    )

    # 3. Convert API request to Pandas DF
    task_clean_data = PythonOperator(
        task_id = 'clean_edamam_data', 
        python_callable = clean_edamam_data
    )
    

    task_transform_data = PythonOperator( 
        task_id = 'transform_edamam_data', 
        python_callable = transform_edamam_data
    )
    

    # task_change_recipe_byday 
    task_get_edamam_request >> task_clean_data >> task_transform_data