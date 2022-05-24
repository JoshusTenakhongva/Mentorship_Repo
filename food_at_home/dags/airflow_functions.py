import requests, json
import pandas as pd
import os

from datetime import date
#from mysql.connector import connect, Error
from flatten_json import flatten

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

def parse_json_request( ti ): 
    # Initialize variables
    hits_list= ti.xcom_pull( task_ids=['get_edamam_request'][0] )
    if not hits_list: 
        raise ValueError( 'no value currently in XComs.')

    # Return our cleaned up search results
    return edamam_json_cleanup( hits_list )

    #[TODO] This is a redirecting function to other helper functions
    # Have the return type be important for picking which filetype to convert to 

def edamam_json_cleanup( json_list ): 
    # Initialization 

    # Isolate the hits and discard the metadata
    hits_data = json_list

    # Flatten the data from our hits
    # Make the json data relational
    return edamam_json_flatten( hits_data )

def edamam_json_flatten( json_list ): 
    # Init
    index = 0

    for index in range( len( json_list )): 
        json_list[index] = flatten( json_list[index] )

    return json_list


def edamam_json_rename_cols( jason ): 
    jason.columns = jason.columns.str.replace('recipe_', '', regex=True)
    return jason

def write_json( json_txt, path='new_json.json' ): 
    # [TODO] Initialize filename with date and time 

    # push file to XCom
	with open( path, 'w' ) as outfile: 
		json.dump( json_txt, outfile )



''' #########
Submission Function
''' #########
def df_submit_mysql( ti ): 
    # Initialization 
    table_name = "testing_1"

    ########################################################
    df= pd.json_normalize( ti.xcom_pull(task_ids=['parse_json_request']) )

    # Write CREATE TABLE query using our dataframe
    # Create the table query
    table_query = df_create_table( table_name, df )
    # Insert the information query 
    insert_queries = df_insert( df, table_name )

    # Connect to local mysql 
    with connect( host='127.0.0.1', user=Variable.get('MYSQL_USER'), password=Variable.get('MYSQL_PW'), database=Variable.get('MYSQL_DB')) \
        as connection: 

        cursor = connection.cursor()

        # Submit the CREATE TABLE query to the database
        cursor.execute( table_query )
        connection.commit()

        # Submit our INSERT queries into our newly CREATED TABLE
        
        for query in insert_queries:
            cursor.execute( query )

        connection.commit()
        
        print( cursor.rowcount, ": worked'" )

        # Close our connection
        cursor.close()
        connection.close()

    print( 'successful' )
    return True

def df_create_table( table_name, df ): 
    # Initialization 
    query = f'CREATE TABLE IF NOT EXISTS {table_name} ( id INT AUTO_INCREMENT PRIMARY KEY, \n'

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

        # Skip the first one for this example pipeline
        if index==0: 
            index+=1
            continue
        
        col_string += f'{col} VARCHAR(255)'

        index += 1
        if index > 30: 
            return col_string 
        else: 
            col_string+= ',\n'
    
    return col_string

def df_insert( df, table ): 
    # Initialization 
    df_cols = create_table_columns( df ).replace( ' VARCHAR(255)', '')
    queries = []
    row_limit = 10
    row = 0
    row_list = df.iloc[0: row_limit]

    # Create template query string 
    insert_query= f'INSERT INTO {table} ({df_cols})\
                    VALUES ($val)'

    # Add df info to the query 
    for row in row_list: 
        row_info = row[1:31]

        # Convert our list to a string that REPLACE can use
        row_values = f'\"{row_info[0]}\" '

        for value in row_info[1:]: 
            row_values += f', \n\"{str(value)[:254]}\"'

        queries.append( insert_query.replace('$val', row_values))

    # Return the string 
    return queries