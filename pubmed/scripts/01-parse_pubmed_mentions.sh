#!/bin/bash
set -ev

source ../db-config.sh
source scripts/var.sh

SCHEMA=mention_pubmed_epilepsy_$DICT_VERSION

TABLE=mention

psql << EOF

CREATE SCHEMA IF NOT EXISTS $SCHEMA;

DROP TABLE IF EXISTS $SCHEMA.$TABLE;
CREATE TABLE $SCHEMA.$TABLE (pmid INT, year_publication INT, match JSONB);

EOF

python src/parse_pubmed_mentions.py

psql << EOF

CREATE UNIQUE INDEX ON $SCHEMA.$TABLE(pmid);
CREATE INDEX ON $SCHEMA.$TABLE(year_publication);

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


## set another view adding article title per Larry's request
## Larry doesn't need this view any more. Leave here in case needed in the future.

#MERGED_TABLE=mention_and_title
#
#psql << EOF
#DROP MATERIALIZED VIEW IF EXISTS $SCHEMA.$MERGED_TABLE;
#
#CREATE MATERIALIZED VIEW $SCHEMA.$MERGED_TABLE AS
#SELECT
#    m.pmid,
#    m.pub_year,
#    m.article_title,
#    e.match
#FROM pubmed.view_epilepsy m INNER JOIN $SCHEMA.$TABLE e
#ON CAST (m.pmid AS INT) = e.pmid;
#
#-- Indexes
#CREATE UNIQUE INDEX ON $SCHEMA.$MERGED_TABLE(pmid);
#CREATE INDEX ON $SCHEMA.$MERGED_TABLE(pub_year);
#
#-- Permissions
#GRANT ALL ON TABLE $SCHEMA.$MERGED_TABLE TO bherr WITH GRANT OPTION;
#GRANT ALL ON TABLE $SCHEMA.$MERGED_TABLE TO gallantm WITH GRANT OPTION;
#GRANT ALL ON TABLE $SCHEMA.$MERGED_TABLE TO rionbr WITH GRANT OPTION;
#GRANT ALL ON TABLE $SCHEMA.$MERGED_TABLE TO larzhang WITH GRANT OPTION;
#GRANT ALL ON TABLE $SCHEMA.$MERGED_TABLE TO xw47 WITH GRANT OPTION;
#
#EOF