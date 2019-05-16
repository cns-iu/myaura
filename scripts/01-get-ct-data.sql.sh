#!/bin/bash
source constants.sh
source db-config.sh
set -ev

psql << EOF

CREATE TEMPORARY VIEW ctx_locations AS
  SELECT K.id, official_title as name, acronym, coalesce(start_date_year, 'Unknown') AS year, 
    RIGHT(completion_date, '4') AS completion_year, keywords, FF.name AS facility, city, state, zip
  FROM (
    SELECT id, string_agg(keyword, '|') AS keywords
    FROM ct_keyword 
    WHERE keyword ILIKE '%epilepsy%' OR keyword ILIKE '%seizure%'
    GROUP BY id
  ) AS K 
    JOIN ct_fac_address AS F ON (K.id = F.id)
    JOIN ct_facility AS FF ON (F.id = FF.id AND F.loc_ctr = FF.loc_ctr AND F.fid_ctr = FF.fid_ctr)
    JOIN ct_master AS M ON (K.id = M.id)
  WHERE country = 'United States' AND coalesce(start_date_year, '0')::integer >= ${MINYEAR};

\COPY (SELECT * FROM ctx_locations) TO '${OUT}/ct-locations.raw.csv' Delimiter ',' CSV HEADER Encoding 'SQL-ASCII'

EOF
