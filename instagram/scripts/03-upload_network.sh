#!/bin/bash
source ../db-config.sh

# echo all the commands and stops if something breaks
set -ev

# variables
SCHEMA=net_instagram_20180706
CSVNODES=04-instagram-epilepsy-network-20180706-samepost-nodes.csv
CSVEDGES=04-instagram-epilepsy-network-20180706-samepost-edges.csv

# sql command
psql << EOF

CREATE SCHEMA IF NOT EXISTS $SCHEMA;

DROP TABLE IF EXISTS $SCHEMA.edges;
DROP TABLE IF EXISTS $SCHEMA.nodes;

CREATE TABLE IF NOT EXISTS $SCHEMA.nodes
(
    id_node INTEGER NOT NULL,
    CONSTRAINT pk_id_node PRIMARY KEY (id_node)
);

\COPY $SCHEMA.nodes (id_node) FROM $CSVNODES DELIMITER ',' CSV HEADER;

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

\COPY $SCHEMA.edges FROM $CSVEDGES DELIMITER ',' CSV HEADER;

EOF
