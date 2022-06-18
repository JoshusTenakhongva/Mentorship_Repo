import requests, json
import pandas as pd
import os
import sqlalchemy as db
from datetime import datetime

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
def test( ti ): 
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
            query_results = full_response

    except AttributeError: 
        print("API request returned bad data")

    write_json(query_results, f"{dag_path}/raw_data/full_query.json")

def edamam_request(ti): 
    """Connect to edamam API, run query, and save raw data to postgres DB
    """
    # Initialize Variables
    dag_path = os.getcwd()
    host = 'https://api.edamam.com/'
    recipe_base = 'api/recipes/v2' 
    url = host + recipe_base

    # Xcom Pulls
    query = get_next_query()
    search_item = query[2]
    url = query[4]

    # Initialize our config for the query 
    payload = {'type': 'public', 
			    'q': search_item, 
				'app_id': Variable.get('EDAMAM_ID'), 
				'app_key': Variable.get('EDAMAM_KEY')
                } 
    try: 
        # Send a GET request to Edamam API
        with requests.get(url, params=payload) as response: 
            full_response = response.json()
            links_results = full_response['_links']
            query_results = full_response['hits']

    except AttributeError: 
        print("API request returned bad data")

    write_query_psql({
                'search_term': search_item, 
                'page_number': int(full_response['from']) // 20, 
                'next_page': links_results['next']['href']
            })

    write_json(full_response, f"{dag_path}/raw_data/full_query.json")

    # Convert json to a pandas data frame
    df = json_to_df(query_results)

    # Upload the dataframe to the postgres container
    upload_df_psql(df, table='raw_data', conn_string=Variable.get('PSQL_DB_FOODATHOME'), if_exists='replace')

    # Write the dataframe to our cleaned up docker volume
    df.to_csv(f"{dag_path}/raw_data/{search_item}_query.csv")



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

def upload_df_psql(df, table, conn_string, if_exists='replace', index=True): 
    """Master function for running queries to the Postgres database. 
    """
    # Connect to postgres container
    engine = connect_psql_engine(conn_string) 

    # Upload the dataframe to the postgres container
    df.to_sql(table, engine, if_exists=if_exists, index=index)

    # Close our engine connection
    engine.dispose()

def get_table_psql(table, database): 
    """Read a table from the psql db into a pandas df"""
    # Connect to postgres container
    engine = connect_psql_engine(database)

    # Read the table we're looking for 
    df = pd.read_sql_table(table, engine)

    # Return the table as a dataframe
    engine.dispose()
    return df

def connect_psql_engine(conn_string): 
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
    df = get_table_psql('raw_data', Variable.get('PSQL_DB_FOODATHOME'))

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
    upload_df_psql(cleaned_df, 'processed_data', Variable.get('PSQL_DB_FOODATHOME'), if_exists='replace')

    # Upload the csv to our docker volume
    cleaned_df.to_csv(f"{dag_path}/processed_data/new_query.csv")


def write_recipe_psql(df): 
    """Takes in a dataframe and uploads the recipe info to the recipe table in the database"""
    # Read processed data

    # Get recipe information

    # 
    pass

    
def write_query_psql(query_info): 
    """Write the current search query to the search_history and search_queue database"""

    # Create dataframe to upload to the postgres database datetime.datetime.now()
    query_df = pd.DataFrame({
        'search_timestamp': [datetime.now()], 
        'search_term': [query_info['search_term']],
        'page_number': [query_info['page_number'] + 1], 
        'next_page': [query_info['next_page']], 
        'finished': [10000 - int(query_info['page_number']) < 20]
    })
    
    upload_df_psql(query_df, 
        table='search_history', 
        conn_string=Variable.get('PSQL_DB_SEARCHMETADATA'), 
        if_exists='append', 
        index=False)

def write_ingredient_psql(df): 
    # Get cleaned data from the database
    df = get_table_psql('processed_data', Variable.get('PSQL_DB_FOODATHOME'))

    # Check if the ingredient ids already exist in the database

    # Remove all information not related to our recipe schema

    # Push new dataframe to the database
    pass

def get_next_query():
    """Get the next query we want to run"""
    # Connect to the database 
    history_df = get_table_psql('search_history', Variable.get('PSQL_DB_SEARCHMETADATA'))

    '''Find the next query '''
    # Get the last query run 
    prev_query = history_df.iloc[-1]

    # Check if the query is finished
    if prev_query['finished']: 

        '''If so, open a new query'''
        # Get a dataframe of all the ingredients that are not finished
        prospects_df = history_df.loc[history_df['finished'] == True]

        # Return the top one as our next ingredient to search for 
        return prospects_df.iloc[0]

    # If the query is unfinished, continue with it and return the query 
    return prev_query.to_list() 
        


"""
Struggles: 
- Designing the data model 
- Finding a way to automate what query to run on the API 
"""