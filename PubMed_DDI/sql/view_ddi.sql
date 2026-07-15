
-- Create the "data table" which has all the metadata we want for the corresponding "query table"
DROP MATERIALIZED VIEW IF EXISTS pubmed_ddi_classification.view_text_invivo;

CREATE MATERIALIZED VIEW pubmed_ddi_classification.view_text_invivo AS
SELECT
    m.pmid,
    m.pub_year,
    m.journal_title,
    m.iso_abbrev,
    m.medium,
    m.volume,
    m.issue,
    m.pub_medlinedate,
    m.article_title,
    m.revised_year,
    m.completed_year,
    coalesce(abstract_text, '') as abstract_text
FROM pubmed.medline_master m
         LEFT OUTER JOIN (
    SELECT
        pmid,
        STRING_AGG(abstract_text, ' ') as abstract_text
    FROM pubmed.medline_abstract_text
    WHERE CAST (pmid AS INT) IN (SELECT id_pm FROM pubmed_ddi_classification.abstract_classification_invivo)
    GROUP BY pmid
) a ON m.pmid = a.pmid
WHERE CAST (m.pmid AS INT) IN (SELECT id_pm FROM pubmed_ddi_classification.abstract_classification_invivo);

-- Indexes
CREATE UNIQUE INDEX ON pubmed_ddi_classification.view_text_invivo(pmid);
CREATE INDEX ON pubmed_ddi_classification.view_text_invivo(pub_year);

-- Permissions
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_invivo TO bherr WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_invivo TO gallantm WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_invivo TO rionbr WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_invivo TO xw47 WITH GRANT OPTION;


-- Create the "data table" which has all the metadata we want for the corresponding "query table"
DROP MATERIALIZED VIEW IF EXISTS pubmed_ddi_classification.view_text_invitro;

CREATE MATERIALIZED VIEW pubmed_ddi_classification.view_text_invitro AS
SELECT
    m.pmid,
    m.pub_year,
    m.journal_title,
    m.iso_abbrev,
    m.medium,
    m.volume,
    m.issue,
    m.pub_medlinedate,
    m.article_title,
    m.revised_year,
    m.completed_year,
    coalesce(abstract_text, '') as abstract_text
FROM pubmed.medline_master m
         LEFT OUTER JOIN (
    SELECT
        pmid,
        STRING_AGG(abstract_text, ' ') as abstract_text
    FROM pubmed.medline_abstract_text
    WHERE CAST (pmid AS INT) IN (SELECT id_pm FROM pubmed_ddi_classification.abstract_classification_invitro)
    GROUP BY pmid
) a ON m.pmid = a.pmid
WHERE CAST (m.pmid AS INT) IN (SELECT id_pm FROM pubmed_ddi_classification.abstract_classification_invitro);

-- Indexes
CREATE UNIQUE INDEX ON pubmed_ddi_classification.view_text_invitro(pmid);
CREATE INDEX ON pubmed_ddi_classification.view_text_invitro(pub_year);

-- Permissions
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_invitro TO bherr WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_invitro TO gallantm WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_invitro TO rionbr WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_invitro TO xw47 WITH GRANT OPTION;


-- Create the "data table" which has all the metadata we want for the corresponding "query table"
DROP MATERIALIZED VIEW IF EXISTS pubmed_ddi_classification.view_text_clinical;

CREATE MATERIALIZED VIEW pubmed_ddi_classification.view_text_clinical AS
SELECT
    m.pmid,
    m.pub_year,
    m.journal_title,
    m.iso_abbrev,
    m.medium,
    m.volume,
    m.issue,
    m.pub_medlinedate,
    m.article_title,
    m.revised_year,
    m.completed_year,
    coalesce(abstract_text, '') as abstract_text
FROM pubmed.medline_master m
         LEFT OUTER JOIN (
    SELECT
        pmid,
        STRING_AGG(abstract_text, ' ') as abstract_text
    FROM pubmed.medline_abstract_text
    WHERE CAST (pmid AS INT) IN (SELECT id_pm FROM pubmed_ddi_classification.abstract_classification_clinical)
    GROUP BY pmid
) a ON m.pmid = a.pmid
WHERE CAST (m.pmid AS INT) IN (SELECT id_pm FROM pubmed_ddi_classification.abstract_classification_clinical);

-- Indexes
CREATE UNIQUE INDEX ON pubmed_ddi_classification.view_text_clinical(pmid);
CREATE INDEX ON pubmed_ddi_classification.view_text_clinical(pub_year);

-- Permissions
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_clinical TO bherr WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_clinical TO gallantm WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_clinical TO rionbr WITH GRANT OPTION;
GRANT ALL ON TABLE pubmed_ddi_classification.view_text_clinical TO xw47 WITH GRANT OPTION;

