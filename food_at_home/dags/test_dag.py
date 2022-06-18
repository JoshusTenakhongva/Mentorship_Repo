import json
import pandas as pd

from datetime import datetime
from etl_functions import * 

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

with DAG( 
    dag_id= 'test_dag', 
    start_date= datetime( year=2022, month=2, day=1 ),
    schedule_interval= '0 0 * * *', 
    catchup= False
) as dag:  
    # Initialization

    # If this crashes, then it's a problem with airflow itself
    task_airflow_test= PythonOperator( 
        task_id= 'test', 
        python_callable= test
    )

    task_airflow_test