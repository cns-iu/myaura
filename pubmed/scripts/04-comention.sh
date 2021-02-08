#!/bin/bash
set -ev

source ../db-config.sh

psql << EOF

DROP TABLE IF EXISTS mention_pubmed_epilepsy_20180706.comention;
CREATE TABLE mention_pubmed_epilepsy_20180706.comention (idx SERIAL, comention JSONB);

EOF

python src/parse_pubmed_comentions.py
