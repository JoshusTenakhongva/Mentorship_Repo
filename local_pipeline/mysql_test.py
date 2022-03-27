import mysql.connector

# Imports environmental variables from the .env file in this directory
## python-dotenv
from dotenv import dotenv_values
env_var = dotenv_values('.env' ) 

mysql.connector.connect( 
    host='127.0.0.1', 
    database='sm_db_1', 
    user=env_var['mysql_user'], 
    password=env_var['mysql_pw'] )