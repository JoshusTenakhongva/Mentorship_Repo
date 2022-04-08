# Regular Python libraries
import requests, json, csv, os

# Downloaded libraries
import pandas as pd
import mysql.connector
from functions import * 
from IPython.display import display 

# Imports environmental variables from the .env file in this directory
## python-dotenv
from dotenv import dotenv_values

def main(): 
    # Initialize variables 
    query = 'chicken'

    # Connect to Edamam and send them our GET query 
    edamam_get( query, write_raw=True )

    # Open the raw data we received from the API call
    with open( 'raw_data.json' ) as raw_json_file: 
        raw_json = json.load( raw_json_file )

    # Convert the raw data into a parased csv
    df = parse_json( raw_json, return_type='df')
    # Now we can access the data very easily 

    table_name = 'testing'
    
    # Insert the dataframe into the local mysql database (for practice [all right reserved on the API data {Let's be real, if you're checking this. The database will basically have 100 versions of the 'chicken' query, useless for anything other than practice}])
    df_submit_mysql( df, 'sm_db_1', table_name )

if __name__ == '__main__': 
    main()