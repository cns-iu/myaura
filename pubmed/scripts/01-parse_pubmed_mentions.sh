#!/bin/bash
set -ev

source ../db-config.sh
source scripts/var.sh

SCHEMA=mention_pubmed_epilepsy_$DICT_VERSION

TABLE=mention

psql << EOF

CREATE SCHEMA IF NOT EXISTS $SCHEMA;

DROP TABLE IF EXISTS $SCHEMA.$TABLE;
CREATE TABLE $SCHEMA.$TABLE (pmid INT, year_publication INT, match JSONB);

EOF

python src/parse_pubmed_mentions.py

#
# SQL command to grant permissions to users on the new schema and tables
#
USERS="rionbr xw47 larzhang gallantm bherr"
for USER in $USERS
do
	echo "-- Granting permissons to schema and tables to user '$USER'"
    psql -c "GRANT ALL ON SCHEMA $SCHEMA TO $USER WITH GRANT OPTION;"
    psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA $SCHEMA TO $USER WITH GRANT OPTION;"
done
