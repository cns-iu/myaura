#!/bin/bash
set -ev

source ../db-config.sh

psql << EOF

DROP TABLE IF EXISTS ddi.ddi_pubmed_mentions;
CREATE TABLE ddi.ddi_pubmed_mentions (pmid INT, match JSONB);

EOF

python src/parse_pubmed_mentions.py
