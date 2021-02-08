#!/bin/bash
set -ev

source ../db-config.sh

psql << EOF

DROP TABLE IF EXISTS mention_pubmed_epilepsy_20180706.mention;
CREATE TABLE mention_pubmed_epilepsy_20180706.mention (pmid INT, year_publication INT, match JSONB);

EOF

python src/parse_pubmed_mentions.py
