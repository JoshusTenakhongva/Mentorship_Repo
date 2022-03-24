import requests
import json
import csv
import pandas as pd

sparking = False
try: 
	from pyspark.sql import SparkSession
	from pyspark import SparkContext 
	from pyspark.sql import SQLContext
	sparking = True
except: 
	print( 'no spark' ) 

def start_spark():
	ss = SparkSession\
		.builder\
		.appName( 'Food Database Reading' )\
		.config( 'spark.driver.extraClassPath', '/$SPARK_HOME.jars/mysql-connector-java-8.0.16.jar')\
		.getOrCreate()
	return ss

def edamam_connect( write_data=False, ss=None ): 
	host = 'https://api.edamam.com/'
	recipe_base = 'api/recipes/v2' 

	payload = { 'type': 'public', 
				'q': 'chicken', 
				'app_id': '88b7dfb7', 
				'app_key': '5612262fe977b4107a24dcc1c6526fc4'}

	url = host + recipe_base
	print( url )

	response = requests.get( url, params=payload )

	if write_data and ss!=None: 
		write_json( response, ss )

	response.close() 

def write_json( response, ss ): 
	with open( 'data.json', 'w' ) as outfile: 
		json.dump( response.json(), outfile )

def write_csv( response, ss ): 

	with open( 'data.csv', 'w', newline='' ) as csvfile: 
		csvwriter = csv.writer( csvfile, delimiter=' ' )
		csvwriter.writerow( fields )
		csvwriter.writerow( rows )

def main():

	### Extraction
	'''
	print( edamam_connect( ) )
	'''
	### Transformation 	

	with open( 'data.json' ) as project_file: 
		overall_data = json.load( project_file )
		hits_data = overall_data['hits']		

	pd_df = pd.json_normalize( hits_data )
	#pd_df = pd.read_json( 'hits_data.json', orient='columns')
	pd_df.to_csv( 'hits.csv' )
	print( pd_df.head() )
	print( pd_df.dtypes ) 
	print( pd_df.select_dtypes( 'double' ) )

	if sparking: 
		ss = start_spark()
		ss_df = ss.createDataFrame( pd_df )
		ss_df.printSchema()
		ss_df.show().take(5)

if __name__ == "__main__": 
	main()




'''
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext

if __name__ == '__main__': 
    scSpark = SparkSession\
        .builder\
        .appName( 'reading csv' )\
        .config( 'spark.driver.extraClassPath', '/$SPARK_HOME.jars/mysql-connector-java-8.0.16.jar')\
        .getOrCreate()

data_file = 'supermarket_sales.csv'
sdfData = scSpark.read.csv( data_file, header=True, sep=',').cache()

sdfData.registerTempTable("sales" )
output = scSpark.sql( 'SELECT COUNT(*) as total, City from sales GROUP BY City' )
output.show()
'''

