#!/bin/bash
set -e 

#cd docker-entrypoint-initdb.d
#psql -U $POSTGRES_USER -d food_at_home -f init.sql
 
psql -U $POSTGRES_USER -d food_at_home -f init.sql 