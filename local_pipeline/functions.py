import requests, json, csv, os
import pandas as pd

from dotenv import dotenv_values
from datetime import date
from mysql.connector import connect, Error

'''
Def: Connects to the edamam API and sends a request
Return: The response object from the API query
'''
def edamam_get( query='chicken', write_raw=False ): 
    # Initialize Variables
    env_var = dotenv_values( '.env' )
    host = 'https://api.edamam.com/'
    recipe_base = 'api/recipes/v2' 
    url = host + recipe_base
    # Initialize our config for the query 
    payload = { 'type': 'public', 
				'q': query, 
				'app_id': env_var['edamam_app_id'], 
				'app_key': env_var['edamam_app_key']}

    # Send a GET request to Edamam API
    response = requests.get( url, params=payload )

    # Close the connection
    response.close() 

    # Write the raw data if prompted
    if write_raw: 
        write_json( response.json() )

    # Return the response
    return response

def parse_json( raw_json, return_type='df' ): 
    # Initialize variables
    return edamam_to_df( raw_json )

    #[TODO] This is a redirecting function to other helper functions
    # Have the return type be important for picking which filetype to convert to 

def edamam_to_df( raw_json ): 
    # Initialization 

    # Isolate the hits and discard the metadata
    hits_data = raw_json['hits']
    hits_df = pd.json_normalize( hits_data )

    # Clean up column titles
    clean_df = edamam_df_rename_cols( hits_df )

    # Write the CSV
    return clean_df

def edamam_df_rename_cols( df ): 
    df.columns = df.columns.str.replace('recipe.', '', regex=True)
    return df

def write_json( json_txt ): 
    # [TODO] Initialize filename with date and time 

    # Open file
	with open( 'raw_data.json', 'w' ) as outfile: 
		json.dump( json_txt, outfile )

''' #########
Submission Function
''' #########
def df_submit_mysql( df, db ): 
    # Initialization 
    env_var = dotenv_values('.env' ) 
    table_name = "query_results"

    # Write CREATE TABLE query using our dataframe
    # Create the table query
    table_query = df_create_table( table_name, df )
    # Insert the information query 
    insert_queries = df_insert( df, table_name )

    # Connect to local mysql 
    with connect( host='127.0.0.1', user=env_var['mysql_user'], password=env_var['mysql_pw'], database=db) \
        as connection: 

        cursor = connection.cursor()

        # Submit the CREATE TABLE query to the database
        cursor.execute( table_query )
        connection.commit()

        # Submit our INSERT queries into our newly CREATED TABLE
        
        for query in insert_queries:
            cursor.execute( query )
            connection.commit()
            print( 'successful' )
        
        print( cursor.rowcount, ": worked'" )

        # Close our connection
        cursor.close()
        connection.close()

    print( 'successful' )
    return True

def df_create_table( table_name, df ): 
    # Initialization 
    query = f'CREATE TABLE IF NOT EXISTS {table_name}( id INT AUTO_INCREMENT PRIMARY KEY'

    # Create column types (for this exercise, it'll all be strings)
    table_cols = create_table_columns( df )

    # Add our table columns to our query string
    query += table_cols + ' )'

    return query

def create_table_columns( df ): 
    # Initialization
    col_string = ""
    index = 0

    # Loop through the columns of a dataframe to create a table query 
    for col in df.columns: 
        col_ = col.replace( '.', '_')
        col_string += f',\n{col_} VARCHAR(255)'

        index += 1
        if index >= 30: 
            return col_string 
    
    return col_string

def df_insert( df, table ): 
    # Initialization 
    df_cols = create_table_columns( df )[2:].replace( ' VARCHAR(255)', '')
    queries = []
    row = 0

    # Create template query string 
    insert_query= f'INSERT INTO {table} ({df_cols})\
                    VALUES ($val)'

    # Add df info to the query 
    while row < 10: 
        row_info = list( df.iloc[row, 0:30] )

        # Convert our list to a string that REPLACE can use
        row_values = f'\"{row_info[0]}\" '

        for value in row_info[1:]: 
            row_values += f', \n\"{str(value)[:254]}\"'

        queries.append( insert_query.replace('$val', row_values))
        row += 1

    # Return the string 
    print( len( queries ))
    return queries