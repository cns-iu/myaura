#!/bin/bash
set -ev

source ../db-config.sh
source scripts/var.sh

SCHEMA=mention_pubmed_epilepsy_$DICT_VERSION

TABLE=comention

echo $SCHEMA.$TABLE

psql << EOF

DROP TABLE IF EXISTS $SCHEMA.$TABLE;
CREATE TABLE $SCHEMA.$TABLE (source INT, target INT, comention JSONB, PRIMARY KEY (source, target));

EOF

TABLE=mention_count

echo $SCHEMA.$TABLE

psql << EOF

DROP TABLE IF EXISTS $SCHEMA.$TABLE;
CREATE TABLE $SCHEMA.$TABLE (id_parent INT, mention_count INT, PRIMARY KEY (id_parent));

EOF

python src/parse_comentions.py

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
