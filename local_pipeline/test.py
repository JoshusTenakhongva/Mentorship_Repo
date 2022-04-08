import json

import pandas as pd
import numpy as np

from airflow_functions import * 
from flatten_json import flatten

def main(): 
	# Init
	table_name= 'hamilton'
	
	# Read the 'hits.json' file
	with open( 'raw_data.json', 'r' ) as read_content: 
		df= json.load( read_content )['hits']

		clean_json= edamam_json_cleanup( df )

		'''
		index = 0
		for index in range(0, 5): 
			print( clean_json[index] )
			print()
		'''
		# Turn out flattened json into a pandas df
		df = pd.json_normalize( clean_json )

		print( df )


if __name__ == '__main__': 
	main()