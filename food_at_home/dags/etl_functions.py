import requests, json
import pandas as pd
import os
import sqlalchemy as db

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
    try: 
        # Send a GET request to Edamam API
        with requests.get(url, params=payload) as response: 
            full_response = response.json()
            query_results = full_response['hits']
            query_next_page = full_response['_links']

    except AttributeError: 
        print("API request returned bad data")

    write_json(query_results, f"{dag_path}/raw_data/full_query.json")

    # Convert json to a pandas data frame
    df = json_to_df(query_results)

    # Upload the dataframe to the postgres container
    upload_df_psql(df, table='raw_data', if_exists='replace')

    # Write the dataframe to our cleaned up docker volume
    df.to_csv(f"{dag_path}/raw_data/chicken_query.csv")

def write_json(json_txt, path='new_json.json'): 
    '''Write json data as file'''

    # push file to XCom
    with open(path, 'w') as outfile: 
        json.dump(json_txt, outfile)

def json_to_df(json_data, addition=None): 
    '''Convert our recipe json data into a pandas dataframe'''

    # Loop through json indexes and flatten them to fit into our dataframe
    json_data = [flatten(row) for row in json_data]
    
    return pd.json_normalize( json_data )

def upload_df_psql(df, table, if_exists='replace'): 
    """Master function for running queries to the Postgres database. 
    """
    # Connect to postgres container
    engine = connect_psql_engine() 

    # Upload the dataframe to the postgres container
    df.to_sql(table, engine, if_exists=if_exists)

    # Close our engine connection
    engine.dispose()

def get_table_psql(table): 
    """Read a table from the psql db into a pandas df"""
    # Connect to postgres container
    engine = connect_psql_engine()

    # Read the table we're looking for 
    df = pd.read_sql_table(table, engine)

    # Return the table as a dataframe
    engine.dispose()
    return df

def run_postgres_query(query): 
    # connect to database

    # Run Query

    # Close database
    pass
    

def connect_psql_engine(conn_string=Variable.get('PSQL_DB')): 
    """Returns a SQLAlchemy engine connecting to the psql database
    """
    try: 
        Base = declarative_base()
        return create_engine(conn_string, echo=True) 
    except AttributeError: 
        print("SQLAlchemy conn to Postgres conatiner failed")
    

"""Clean Json Request Functions"""
def clean_edamam_data(ti): 
    # Initialization 
    dag_path = os.getcwd()
    drop_cols = []

    # Read from postgres to get the raw data
    df = get_table_psql('raw_data')

    # Get a list of the columns we want to drop
    drop_cols_categories=('digest', 'image', 'totalDaily', 'image')
    columns = list(df.columns.values)
    
    # Loop through the columsn and get the names of the columns we don't want
    for col in columns: 
        for drop_col in drop_cols_categories: 
            if drop_col in col: 
                drop_cols.append(col)

    # Drop the columns from our data frame
    cleaned_df = df.drop(drop_cols, axis=1)

    # Upload code to the processed data table
    upload_df_psql(cleaned_df, 'processed_data', if_exists='replace')

    # Upload the csv to our docker volume
    cleaned_df.to_csv(f"{dag_path}/processed_data/new_query.csv")

# Function to read a single ingredient and return a list of recipes with common ingredients 
def find_recipes(ingredient): 
    pass

def create_ingredient_query(user_id): 
    """Function that read's a user's list of ingredients and returns a """