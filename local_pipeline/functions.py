import requests, json, csv, os

import pandas as pd
from dotenv import dotenv_values
from datetime import date

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
    df.columns = df.columns.str.replace('recipe.', '')
    return df

def write_json( json_txt ): 
    # [TODO] Initialize filename with date and time 

    # Open file
	with open( 'raw_data.json', 'w' ) as outfile: 
		json.dump( json_txt, outfile )