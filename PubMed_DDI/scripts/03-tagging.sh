#!/bin/bash
set -ev

source ../db-config.sh

psql << EOF

DROP TABLE IF EXISTS ddi.pubmed_abstract_mention_20180706;
CREATE TABLE ddi.pubmed_abstract_mention_20180706 (pmid INT, date_publication DATE, match JSONB);

EOF

python src/parse_pubmed_mentions.py
