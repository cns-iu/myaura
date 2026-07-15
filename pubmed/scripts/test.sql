DROP MATERIALIZED VIEW IF EXISTS mention_pubmed_epilepsy_20180706.mention_and_title;

CREATE MATERIALIZED VIEW mention_pubmed_epilepsy_20180706.mention_and_title AS
SELECT
    m.pmid,
    e.year_publication,
    m.article_title,
    e.match
FROM pubmed.view_epilepsy m INNER JOIN mention_pubmed_epilepsy_20180706.mention e
ON CAST (m.pmid AS INT) = e.pmid;

-- Indexes
CREATE UNIQUE INDEX ON mention_pubmed_epilepsy_20180706.mention_and_title(pmid);
CREATE INDEX ON mention_pubmed_epilepsy_20180706.mention_and_title(year_publication);

-- Permissions
GRANT ALL ON TABLE mention_pubmed_epilepsy_20180706.mention_and_title TO bherr WITH GRANT OPTION;
GRANT ALL ON TABLE mention_pubmed_epilepsy_20180706.mention_and_title TO gallantm WITH GRANT OPTION;
GRANT ALL ON TABLE mention_pubmed_epilepsy_20180706.mention_and_title TO rionbr WITH GRANT OPTION;
GRANT ALL ON TABLE mention_pubmed_epilepsy_20180706.mention_and_title TO larzhang WITH GRANT OPTION;
GRANT ALL ON TABLE mention_pubmed_epilepsy_20180706.mention_and_title TO xw47 WITH GRANT OPTION;
