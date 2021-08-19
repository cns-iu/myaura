-- \set dictionary dict_20180706
-- \set edges net_pubmed_epilepsy_20180706

WITH edges AS (
  SELECT source, target,
    -- normalize the proximity to 1 - 1,000 (1,000 being the highest)
    ROUND((
      1 + proximity / (SELECT max(proximity) FROM :edges.edges) * 999
    )::NUMERIC, 2) as weight
  FROM :edges.edges
  WHERE is_metric IS TRUE
), nodes AS (
  SELECT id, token as label, id_parent as parent
  FROM dictionaries.:dictionary
  WHERE id IN (SELECT source FROM edges UNION SELECT target FROM edges)
  ORDER BY id
)
-- Compile nodes and edges into a JSON object for use in map4sci
SELECT jsonb_pretty(jsonb_object_agg(field, val))
FROM (
  (SELECT 'nodes' AS field, jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
    'id', id, 'label', label, 'parent', parent
  ))) AS val FROM nodes)
  UNION ALL
  (SELECT 'edges' AS field, jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
    'source', source, 'target', target, 'weight', weight
  ))) AS val FROM edges)
) AS a;
