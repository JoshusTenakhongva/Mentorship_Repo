import requests, json
import pandas as pd
import os

from datetime import date
#from mysql.connector import connect, Error
from flatten_json import flatten

from sqlalchemy import Table, Column, MetaData, Integer, Computed, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 

from airflow.models import Variable

'''
Connects to the edamam API and sends a request
Return: The response object from the API query
'''
def airflow_var_test( ti ): 
    print( Variable.get('EDAMAM_ID') )

def edamam_get(ti): 
    # Initialize Variables
    dag_path = os.getcwd()
    host = 'https://api.edamam.com/'
    recipe_base = 'api/recipes/v2' 
    url = host + recipe_base

    # Xcom Pulls
    query= "chicken"

    # Initialize our config for the query 
    payload = {'type': 'public', 
			    'q': query, 
				'app_id': Variable.get('EDAMAM_ID'), 
				'app_key': Variable.get('EDAMAM_KEY')
                } 

    # Send a GET request to Edamam API
    with requests.get(url, params=payload) as response: 
        query_results = response.json()['hits']

    # Return the response
    write_json(query_results, f"{dag_path}/raw_data/chicken_query.json")

def write_json(json_txt, path='new_json.json'): 
    # [TODO] Initialize filename with date and time 

    # push file to XCom
	with open(path, 'w') as outfile: 
		json.dump(json_txt, outfile)

def run_pg_query(): 
    """Master function for running queries to the Postgres database. 
    """
    # Initialization 
    conn_string = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

    # Connect to database
    with create_alchemy_engine_pg("postgresql+psycopg2://airflow:airflow@postgres:5432/airflow") as engine: 
        pass

    # Run query

    # Return output
    pass

def create_alchemy_engine_pg(conn_string="postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"): 
    """Helper function for run_pg_query(). Returns the credentials to connect to the database
    """
    Base = declarative_base()
    return create_engine(conn_string, echo=True) 
    

def create_pg_table( columns ): 
    """Connect to postgres server and 
    """
    pass