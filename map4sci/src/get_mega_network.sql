\set dictionary dict_20180706
\set edges net_mega_20180706
\set out_json ../../tripods/map4sci/datasets/myaura/net_mega_20180706/network.json

-- \set dictionary dict_20210321
-- \set edges net_mega_20210321
-- \set out_json ../../tripods/map4sci/datasets/myaura/net_mega_20210321/network.json

CREATE TEMP TABLE net_mega_20180706 AS
  SELECT source, target, max(proximity) AS proximity, TRUE AS is_metric
  FROM (
    SELECT source, target, proximity FROM net_clinical_trials_20180706.edges WHERE is_metric IS TRUE
    UNION ALL
    SELECT source, target, proximity FROM net_efwebsite_forums_20180706.edges WHERE is_metric IS TRUE
    UNION ALL
    SELECT source, target, proximity FROM net_instagram_20180706.edges WHERE is_metric IS TRUE
    UNION ALL
    SELECT source, target, proximity FROM net_pubmed_epilepsy_20180706.edges WHERE is_metric IS TRUE
    UNION ALL
    SELECT source, target, proximity FROM net_twitter_20180706.edges WHERE is_metric IS TRUE
  ) AS a
  GROUP BY source, target;

CREATE TEMP TABLE net_mega_20210321 AS
  SELECT source, target, max(proximity) AS proximity, TRUE AS is_metric
  FROM (
    SELECT source, target, proximity FROM net_clinical_trials_20210321.edges WHERE is_metric IS TRUE
    UNION ALL
    SELECT source, target, proximity FROM net_efwebsite_forums_20210321.edges WHERE is_metric IS TRUE
    UNION ALL
    SELECT source, target, proximity FROM net_instagram_20210321.edges WHERE is_metric IS TRUE
    UNION ALL
    SELECT source, target, proximity FROM net_pubmed_epilepsy_20210321.edges WHERE is_metric IS TRUE
  ) AS a
  GROUP BY source, target;

\t
\a
\o :out_json

WITH edges AS (
  SELECT source, target,
    -- normalize the proximity to 1 - 1,000 (1,000 being the highest)
    ROUND((
      1 + proximity / (SELECT max(proximity) FROM :edges) * 999
    )::NUMERIC, 2) as weight
  FROM :edges
), nodes AS (
  SELECT id, token as label
  FROM dictionaries.:dictionary
  WHERE id IN (SELECT source FROM edges UNION SELECT target FROM edges)
  ORDER BY id
)
-- Compile nodes and edges into a JSON object for use in map4sci
SELECT jsonb_pretty(jsonb_object_agg(field, val))
FROM (
  (SELECT 'nodes' AS field, jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
    'id', id, 'label', label
  ))) AS val FROM nodes)
  UNION ALL
  (SELECT 'edges' AS field, jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
    'source', source, 'target', target, 'weight', weight
  ))) AS val FROM edges)
) AS a;
