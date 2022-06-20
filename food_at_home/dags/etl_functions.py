import requests, json
import pandas as pd
import os

from datetime import datetime, date

from flatten_json import flatten

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text

from airflow.models import Variable

# constants 
FOOD_AT_HOME = Variable.get('PSQL_DB_FOODATHOME')
SEARCH_METADATA = Variable.get('PSQL_DB_SEARCHMETADATA')


"""
====================
Chapter 1: The Airflow Tasks
====================
"""
def test( ti ): 
    '''
    Connects to the edamam API and sends a request
    Return: The response object from the API query
    '''
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

    write_search_history_psql({
                'search_term': search_item, 
                'page_number': int(full_response['from']) // 20, 
                'next_page': links_results['next']['href']
            })

    write_json(full_response, f"{dag_path}/raw_data/full_query.json")

    # Convert json to a pandas data frame
    df = json_to_df(query_results)

    # Upload the dataframe to the postgres container
    upload_df_psql(df, table='raw_data', conn_url=FOOD_AT_HOME, if_exists='replace')

    # Write the dataframe to our cleaned up docker volume
    df.to_csv(f"{dag_path}/raw_data/{search_item}_query.csv")

def clean_edamam_data(ti): 
    # Initialization 
    dag_path = os.getcwd()
    drop_cols = []

    # Read from postgres to get the raw data
    df = get_table_psql('raw_data', FOOD_AT_HOME)

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
    upload_df_psql(cleaned_df, 'processed_data', FOOD_AT_HOME, if_exists='replace')

    # Upload the csv to our docker volume
    cleaned_df.to_csv(f"{dag_path}/processed_data/new_query.csv")

def transform_edamam_data(ti): 
    # Initialization 
    

    # Get our cleaned up data from the database
    df = get_table_psql('processed_data', FOOD_AT_HOME)

    # [TODO] put Write to the search history here

    # Write to the recipe table
    write_recipe_psql(df)

    # Write to the ingreients table 

    # Write to the pantry table 

    

"""
======================
Chapter 2: JSON Functions
======================
"""
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

"""
======================
Chapter 3: PSQL Get Functions
======================
"""

def connect_psql_engine(conn_url): 
    """Returns a SQLAlchemy engine connecting to the psql database
    """
    try: 
        Base = declarative_base()
        return create_engine(conn_url, echo=True) 
    except AttributeError: 
        print("SQLAlchemy conn to Postgres conatiner failed")

def get_table_psql(table, conn_url): 
    """Read a table from the psql db into a pandas df"""
    # Connect to postgres container
    engine = connect_psql_engine(conn_url)

    # Read the table we're looking for 
    df = pd.read_sql_table(table, engine)

    # Return the table as a dataframe
    engine.dispose()
    return df

def get_next_query():
    """Get the next query we want to run"""
    # Connect to the database 
    history_df = get_table_psql('search_history', SEARCH_METADATA)

    # If the search_history is empty, return a default query, chicken
    if len(history_df) == 0: 
        return [None, None, 'Chicken', None, 'https://api.edamam.com/api/recipes/v2']

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
======================
Chapter 3: PSQL Write Functions
======================
"""

def upload_df_psql(df, table, conn_url, if_exists='replace', index=True): 
    """Master function for running queries to the Postgres database. 
    """
    # Connect to postgres container
    engine = connect_psql_engine(conn_url) 

    # Upload the dataframe to the postgres container
    df.to_sql(table, engine, if_exists=if_exists, index=index)

    # Close our engine connection
    engine.dispose()

def write_recipe_psql(df): 
    """Takes in a dataframe and uploads the recipe info to the recipe table in the database"""
    """Initialization"""
    # Query to get all of the recipe IDs from our recipe database
    sql_query = '''
        SELECT recipe_url
        FROM recipe_dim'''
    engine = connect_psql_engine(FOOD_AT_HOME)

    """Trim our dataframe of unnecessary information"""
    # Process the data further into only what we need for the recipe_dim table
    recipe_df = df[[
        'recipe_url', 
        'recipe_yield',

        'recipe_totalNutrients_ENERC_KCAL_quantity', 
        'recipe_totalNutrients_FAT_quantity',
        'recipe_totalNutrients_PROCNT_quantity',  
        'recipe_totalNutrients_CHOCDF_quantity', 

        'recipe_cuisineType_0', 
        'recipe_totalTime', 
        'recipe_cuisineType_0'
        ]]
    # Also change the names to what they are in the database
    recipe_df = recipe_df.rename(columns={
        'recipe_totalNutrients_ENERC_KCAL_quantity':'calories_k', 
        'recipe_totalNutrients_FAT_quantity': 'fat_g', 
        'recipe_totalNutrients_PROCNT_quantity': 'protein_g', 
        'recipe_totalNutrients_CHOCDF_quantity': 'carbs_g', 
        'recipe_cuisineType_0': 'cuisine_type', 
        'recipe_totalTime': 'cooktime_minutes', 
        'recipe_cuisineType_0': 'meal_time'
        })

    """Get the urls of all recipes currently in the database
    We will use these to check for duplicates since they're the only 
    unique identifier for Edamam recipes"""
    # Run search query to get a list of all recipe IDs from the database
    with engine.connect().execution_options(autocommit=True) as conn: 
        # Run our query
        recipe_urls = pd.read_sql(sql_query, con=conn)
        # Transform out column into a single list
        recipe_urls = recipe_urls.squeeze().to_list()    
    engine.dispose()

    """Drop any duplicates and upload to the database"""
    # Drop any duplicates already in the database
    recipe_df = recipe_df[ ~recipe_df['recipe_url'].isin(recipe_urls) ]
    # Append our new dataframe to the recipe_dim table
    upload_df_psql(
        recipe_df, 
        table='recipe_dim', 
        conn_url=FOOD_AT_HOME, 
        if_exists='append', 
        index=False)

def write_ingredient_psql(df): 
    # Get cleaned data from the database
    df = get_table_psql('processed_data', FOOD_AT_HOME)

    # Check if the ingredient ids already exist in the database

    # Remove all information not related to our recipe schema

    # Push new dataframe to the database
    pass

    
def write_search_history_psql(query_info): 
    """Write the current search query to the search_history and search_queue database"""

    # Create dataframe to upload to the postgres database datetime.datetime.now()
    query_df = pd.DataFrame({
        'search_timestamp': [datetime.now()], 
        'search_term': [query_info['search_term']],
        'page_number': [query_info['page_number'] + 1], 
        'next_page': [query_info['next_page']], 
        'finished': [10000 - int(query_info['page_number']) < 20]
    })
    
    upload_df_psql(
        query_df, 
        table='search_history', 
        conn_url=SEARCH_METADATA, 
        if_exists='append', 
        index=False)

"""
======================
Chapter 3.5: PSQL Write Helper Functions
======================
"""



"""
Struggles: 
- Designing the data model 
- Finding a way to automate what query to run on the API 
"""