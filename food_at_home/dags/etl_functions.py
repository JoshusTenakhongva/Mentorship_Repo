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
    """Connect to edamam API, run query, and save raw data to postgres DB
    """
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

    # Write to the docker volume the raw json data
    write_json(query_results, f"{dag_path}/raw_data/chicken_query.json")

    # Convert json to a pandas data frame
    df = json_to_df(query_results)

    # Upload the dataframe to the postgres container
    run_pg_query(df)

    # Write the dataframe to our cleaned up docker volume
    df.to_csv(f"{dag_path}/processed_data/chicken_query.csv")

def write_json(json_txt, path='new_json.json'): 
    # [TODO] Initialize filename with date and time 

    # push file to XCom
	with open(path, 'w') as outfile: 
		json.dump(json_txt, outfile)

def json_to_df(json_data): 

    # Loop through json indexes and flatten them to fit into our dataframe
    for index in range( len( json_data )): 
        json_data[index] = flatten( json_data[index] )
    
    return pd.json_normalize( json_data )

def run_pg_query(df): 
    """Master function for running queries to the Postgres database. 
    """
    # Initialization 
    conn_string = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

    # Connect to database
    engine = create_alchemy_engine_pg("postgresql+psycopg2://airflow:airflow@postgres:5432/airflow") 

    df.to_sql('raw_data', engine)

    # Run query

    # Return output

def create_alchemy_engine_pg(conn_string="postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"): 
    """Helper function for run_pg_query(). Returns the credentials to connect to the database
    """
    Base = declarative_base()
    return create_engine(conn_string, echo=True) 
    

def create_pg_table( columns ): 
    """Connect to postgres server and 
    """
    pass