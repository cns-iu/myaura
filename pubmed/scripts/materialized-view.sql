-- Create the "query table" which just stores the PMIDs of 'all' epilepsy articles
DROP MATERIALIZED VIEW IF EXISTS pubmed.view_epilepsy_query;

CREATE MATERIALIZED VIEW pubmed.view_epilepsy_query AS
SELECT DISTINCT pmid FROM (
	SELECT pmid FROM pubmed.medline_master WHERE journal_title IN (
		'Clinical nursing practice in epilepsy',
		'Epilepsia',
		'Epilepsia open',
		'Epilepsy & behavior case reports',
		'Epilepsy & behavior : E&B',
		'Epilepsy & behavior reports',
		'Epilepsy currents',
		'Epilepsy journal',
		'Epilepsy research',
		'Epilepsy research and treatment',
		'Epilepsy research. Supplement',
		'Epileptic disorders : international epilepsy journal with videotape',
		'Journal of epilepsy',
		'Journal of epilepsy research',
		'Journal of pediatric epilepsy',
		'Molecular & cellular epilepsy',
		'Newsletter. American Epilepsy League',
		'North African and Middle East epilepsy journal'
	)
	UNION
	SELECT pmid FROM pubmed.medline_mesh_heading WHERE ui IN (
		'D012640', -- Seizures
		'D004827', -- Epilepsy
		'D000069279', -- Drug Resistant Epilepsy
		'D004828', -- Epilepsies, Partial
		'D020936', -- Epilepsy, Benign Neonatal
		'D004829', -- Epilepsy, Generalized
		'D004834', -- Epilepsy, Post-Traumatic
		'D020195', -- Epilepsy, Reflex
		'D000073376', -- Epileptic Syndromes
		'D000080485', -- Sudden Unexpected Death in Epilepsy
		-- drugs knonw to be used to treat epilepsy
		'D000078306', -- clobazam (onfi)
		'D000077287', -- levetiracetam (keppra)
		'D000077213', -- lamotrigine
		'D000078334', -- lacosamide
		'D002220', -- carbamazepine
		'D003975', -- diazepam (valium)
		'D000078330' -- oxcarbazepine
	)
	UNION
	SELECT pmid FROM pubmed.medline_master WHERE		
		lower(article_title) SIMILAR TO '%([[:<:]]Levetiracetamum[[:>:]]|[[:<:]]valium[[:>:]]|[[:<:]]levetiracetam[[:>:]]|[[:<:]]diazepam[[:>:]]|[[:<:]]clobazam[[:>:]]|[[:<:]]keppra[[:>:]]|[[:<:]]oxcarbazepine[[:>:]]|[[:<:]]SPM927[[:>:]]|[[:<:]]carbamazepen[[:>:]]|[[:<:]]erlosamide[[:>:]]|[[:<:]]harkoseride[[:>:]]|[[:<:]]lamotriginum[[:>:]]|[[:<:]]lamotrigina[[:>:]]|[[:<:]]carbamazepina[[:>:]]|[[:<:]]lamotrigine[[:>:]]|[[:<:]]carbamazepinum[[:>:]]|[[:<:]]carbamazepine[[:>:]]|[[:<:]]diastat[[:>:]]|[[:<:]]carbamazépine[[:>:]]|[[:<:]]carbamazepin[[:>:]]|[[:<:]]vimpat[[:>:]]|[[:<:]]lamictal[[:>:]]|[[:<:]]lacosamide[[:>:]]|[[:<:]]onfi[[:>:]])%'
	UNION
	SELECT pmid FROM pubmed.medline_abstract_text WHERE
		lower(abstract_text) SIMILAR TO '%([[:<:]]Levetiracetamum[[:>:]]|[[:<:]]valium[[:>:]]|[[:<:]]levetiracetam[[:>:]]|[[:<:]]diazepam[[:>:]]|[[:<:]]clobazam[[:>:]]|[[:<:]]keppra[[:>:]]|[[:<:]]oxcarbazepine[[:>:]]|[[:<:]]SPM927[[:>:]]|[[:<:]]carbamazepen[[:>:]]|[[:<:]]erlosamide[[:>:]]|[[:<:]]harkoseride[[:>:]]|[[:<:]]lamotriginum[[:>:]]|[[:<:]]lamotrigina[[:>:]]|[[:<:]]carbamazepina[[:>:]]|[[:<:]]lamotrigine[[:>:]]|[[:<:]]carbamazepinum[[:>:]]|[[:<:]]carbamazepine[[:>:]]|[[:<:]]diastat[[:>:]]|[[:<:]]carbamazépine[[:>:]]|[[:<:]]carbamazepin[[:>:]]|[[:<:]]vimpat[[:>:]]|[[:<:]]lamictal[[:>:]]|[[:<:]]lacosamide[[:>:]]|[[:<:]]onfi[[:>:]])%'
) AS q
ORDER BY pmid;

CREATE UNIQUE INDEX ON pubmed.view_epilepsy_query(pmid);


-- Create the "data table" which has all the metadata we want for the corresponding "query table"
DROP MATERIALIZED VIEW IF EXISTS pubmed.view_epilepsy;

CREATE MATERIALIZED VIEW pubmed.view_epilepsy AS
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
	WHERE pmid IN (SELECT pmid FROM pubmed.view_epilepsy_query)
	GROUP BY pmid
) a ON m.pmid = a.pmid
WHERE m.pmid IN (SELECT pmid FROM pubmed.view_epilepsy_query);

CREATE UNIQUE INDEX ON pubmed.view_epilepsy(pmid);
CREATE INDEX ON pubmed.view_epilepsy(pub_year);

