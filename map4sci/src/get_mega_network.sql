-- Create mega network from 20180706 dictionary
CREATE TEMP TABLE net_mega_20180706 AS
  SELECT source, target, avg(proximity) AS proximity, is_original, is_metric, is_ultrametric
  FROM (
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_clinical_trials_20180706.edges
    UNION ALL
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_efwebsite_forums_20180706.edges
    UNION ALL
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_instagram_20180706.edges
    UNION ALL
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_pubmed_epilepsy_20180706.edges
    UNION ALL
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_twitter_20180706.edges
  ) AS a
  GROUP BY source, target, is_original, is_metric, is_ultrametric;

-- Create mega network from 20210321 dictionary
CREATE TEMP TABLE net_mega_20210321 AS
  SELECT source, target, avg(proximity) AS proximity, is_original, is_metric, is_ultrametric
  FROM (
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_clinical_trials_20210321.edges
    UNION ALL
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_efwebsite_forums_20210321.edges
    UNION ALL
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_instagram_20210321.edges
    UNION ALL
    SELECT source, target, proximity, is_original, is_metric, is_ultrametric FROM net_pubmed_epilepsy_20210321.edges
  ) AS a
  GROUP BY source, target, is_original, is_metric, is_ultrametric;

\t
\a
\o :out_json
