#!/bin/bash
source db-config.sh
set -ev

SCHEMAS="clinical_trials pubmed uspto wos"
USERS="rionbr xw47 larzhang gallantm"

# For each new server:
# CREATE SERVER uspto_server FOREIGN DATA WRAPPER postgres_fdw OPTIONS (dbname 'uspto', host 'dbr.cns.iu.edu', port '5433');
# CREATE USER MAPPING FOR bherr SERVER uspto_server OPTIONS ("user" 'uuuu', password 'pppp');
# DROP SCHEMA IF EXISTS uspto CASCADE;
# CREATE SCHEMA uspto;
# IMPORT FOREIGN SCHEMA public FROM SERVER uspto_server INTO uspto;

## To update the dbname
# ALTER SERVER wos_server OPTIONS (SET dbname 'wos_2019');

for user in $USERS
do
  for schema in $SCHEMAS
  do
    echo "GRANT USAGE ON FOREIGN SERVER ${schema}_server TO $user;"
    echo "GRANT ALL ON SCHEMA $schema TO $user;"
    echo "GRANT SELECT ON ALL TABLES IN SCHEMA $schema TO $user;"
  done
done
