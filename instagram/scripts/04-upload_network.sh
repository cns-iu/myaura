#!/bin/bash
source ../../db-config.sh

# echo all the commands and stops if something breaks
set -ev

#
# Init variables
#
SCHEMA=net_instagram_20180706
CSVNODES=../tmp-data/04-instagram-epilepsy-network-20180706-samepost-nodes.csv
CSVEDGES=../tmp-data/04-instagram-epilepsy-network-20180706-samepost-edges.csv

#
# SQL command to create schema, tables and populate the tables.
#
echo "-- Create schema '$SCHEMA' and tables 'nodes' and 'edges'."
psql << EOF

CREATE SCHEMA IF NOT EXISTS $SCHEMA;

DROP TABLE IF EXISTS $SCHEMA.edges;
DROP TABLE IF EXISTS $SCHEMA.nodes;

CREATE TABLE IF NOT EXISTS $SCHEMA.nodes
(
    id_node INTEGER NOT NULL,
    CONSTRAINT pk_id_node PRIMARY KEY (id_node)
);

CREATE TABLE IF NOT EXISTS $SCHEMA.edges (
    source INTEGER REFERENCES $SCHEMA.nodes(id_node),
    target INTEGER REFERENCES $SCHEMA.nodes(id_node),
    count INTEGER,
    proximity DOUBLE PRECISION,
    distance DOUBLE PRECISION,
    is_original BOOLEAN,
    metric_distance DOUBLE PRECISION,
    is_metric BOOLEAN,
    s_value DOUBLE PRECISION,
    CONSTRAINT pk_source_target PRIMARY KEY (source, target)
);
EOF

#
# SQL command to insert data from csv files into tables
#
echo "-- Populating tables from CSV files."
psql << EOF

\COPY $SCHEMA.nodes (id_node) FROM $CSVNODES DELIMITER ',' CSV HEADER;
\COPY $SCHEMA.edges FROM $CSVEDGES DELIMITER ',' CSV HEADER;

EOF

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
