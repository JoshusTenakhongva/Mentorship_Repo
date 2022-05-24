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

def write_json( json_txt, path='new_json.json' ): 
    # [TODO] Initialize filename with date and time 

    # push file to XCom
	with open( path, 'w' ) as outfile: 
		json.dump( json_txt, outfile )