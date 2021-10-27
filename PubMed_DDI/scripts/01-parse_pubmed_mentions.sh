#!/bin/bash
set -ev

source ../db-config.sh
source scripts/var.sh

for SCHEMA in mention_pubmed_ddi_invivo_$DICT_VERSION mention_pubmed_ddi_invitro_$DICT_VERSION mention_pubmed_ddi_clinical_$DICT_VERSION;
do

TABLE=mention

psql << EOF

CREATE SCHEMA IF NOT EXISTS $SCHEMA;

DROP TABLE IF EXISTS $SCHEMA.$TABLE;
CREATE TABLE $SCHEMA.$TABLE (pmid INT, year_publication INT, match JSONB);

EOF

done

python src/parse_pubmed_mentions.py

for SCHEMA in mention_pubmed_ddi_invivo_$DICT_VERSION mention_pubmed_ddi_invitro_$DICT_VERSION mention_pubmed_ddi_clinical_$DICT_VERSION;
do

psql << EOF

CREATE UNIQUE INDEX ON $SCHEMA.$TABLE(pmid);
CREATE INDEX ON $SCHEMA.$TABLE(year_publication);

EOF
#
# SQL command to grant permissions to users on the new schema and tables
#
USERS="rionbr xw47 gallantm bherr"
for USER in $USERS
do
	echo "-- Granting permissons to schema and tables to user '$USER'"
    psql -c "GRANT ALL ON SCHEMA $SCHEMA TO $USER WITH GRANT OPTION;"
    psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA $SCHEMA TO $USER WITH GRANT OPTION;"
done

done
