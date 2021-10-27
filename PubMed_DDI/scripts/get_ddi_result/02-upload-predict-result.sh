#!/bin/bash
source ../db-config.sh
set -ev


psql << EOF

CREATE TABLE IF NOT EXISTS pubmed_ddi_classification.abstract_classification_clinical (
id_pm INT,
classifier VARCHAR(20),
prediction INT,
prediction_conf real,
PRIMARY KEY (id_pm, classifier));

CREATE TABLE IF NOT EXISTS pubmed_ddi_classification.abstract_classification_invivo (
id_pm INT,
classifier VARCHAR(20),
prediction INT,
prediction_conf real,
PRIMARY KEY (id_pm, classifier));

CREATE TABLE IF NOT EXISTS pubmed_ddi_classification.abstract_classification_invitro (
id_pm INT,
classifier VARCHAR(20),
prediction INT,
prediction_conf real,
PRIMARY KEY (id_pm, classifier));

\COPY pubmed_ddi_classification.abstract_classification_clinical FROM 'data/clinical_all_conf.txt' WITH DELIMITER E'\t' CSV HEADER;
\COPY pubmed_ddi_classification.abstract_classification_invivo FROM 'data/invivo_all_conf.txt' WITH DELIMITER E'\t' CSV HEADER;
\COPY pubmed_ddi_classification.abstract_classification_invitro FROM 'data/invitro_all_conf.txt' WITH DELIMITER E'\t' CSV HEADER;


EOF
