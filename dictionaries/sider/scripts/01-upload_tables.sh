#!/bin/bash
source ../../../db-config.sh

# echo all the commands and stops if something breaks
set -ev

#
# Init variables
#
VERSION=41
SCHEMA=dictionaries

#
# SQL command to drop tables if exists
#
echo "-- Drop '$SCHEMA' tables if they exist."
psql << EOF

DROP TABLE IF EXISTS ${SCHEMA}.sider_${VERSION}_drug_has_indication;
DROP TABLE IF EXISTS ${SCHEMA}.sider_${VERSION}_drug_has_sideeffect;

EOF

#
# SQL command to create schema, tables and populate the tables.
#
echo "-- Create '$SCHEMA' tables."
psql << EOF

CREATE TABLE $SCHEMA.sider_${VERSION}_drug_has_sideeffect
(
   id_drugbank         VARCHAR(8),
   id_meddra_pt_code   INT NOT NULL,
   placebo             JSON,
   frequency           JSON,
   meddra_type         VARCHAR(3),
   meddra_pt_name      TEXT
);

CREATE INDEX idx_sider_sideeffect_id_db ON $SCHEMA.sider_${VERSION}_drug_has_sideeffect (id_drugbank);
CREATE INDEX idx_sider_sideeffect_id_meddra ON $SCHEMA.meddra_${VERSION}_drug_has_sideeffect (id_meddra_pt_code);

CREATE TABLE $SCHEMA.sider_${VERSION}_drug_has_indication
(
   id_drugbank         VARCHAR(8),
   id_meddra_pt_code   INT NOT NULL,
   meddra_type         VARCHAR(3),
   meddra_pt_name      TEXT
);

CREATE INDEX idx_sider_indication_id_db ON $SCHEMA.sider_${VERSION}_drug_has_indication (id_drugbank);
CREATE INDEX idx_sider_indication_id_meddra ON $SCHEMA.meddra_${VERSION}_drug_has_indication (id_meddra_pt_code);

EOF

#
# SQL command to insert data from csv files into tables
#
echo "-- Populating tables from CSV files."
psql << EOF

\COPY ${SCHEMA}.sider_${VERSION}_drug_has_sideeffect FROM PROGRAM 'gzip -dc ../tmp-data/sider-drug-sideeffect.csv.gz' DELIMITER ',' CSV HEADER;
\COPY ${SCHEMA}.sider_${VERSION}_drug_has_indication FROM PROGRAM 'gzip -dc ../tmp-data/sider-drug-indication.csv.gz' DELIMITER ',' CSV HEADER;

EOF


#
# SQL command to grant permissions to users on the new schema and tables
#
echo "-- Granting permissions."
USERS="rionbr xw47 gallantm bherr"
for USER in $USERS
do
	echo "-- Granting permissons to schema and tables to user '$USER'"
    psql -c "GRANT ALL ON SCHEMA ${SCHEMA} TO $USER WITH GRANT OPTION;"
    psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ${SCHEMA} TO $USER WITH GRANT OPTION;"
done
