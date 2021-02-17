-- Create the "query table" which just stores the NCT_IDs of 'all' epilepsy clinical trials
DROP MATERIALIZED VIEW IF EXISTS clinical_trials.view_clinical_trials_query;

CREATE MATERIALIZED VIEW clinical_trials.view_clinical_trials_query AS
SELECT DISTINCT nct_id FROM (
	-- Condition Mesh Terms
	SELECT nct_id FROM clinical_trials.ct_condition_browse WHERE mesh_term IN (
		'Epilepsy'
	)

	UNION

	-- Intervention Mesh Term
	SELECT nct_id FROM clinical_trials.ct_intervention_browse WHERE mesh_term IN (
		-- Drugs
		'Clobazam',
		'Levetiracetam',
		'Lamotrigine',
		'Lacosamide',
		'Carbamazepine',
		'Diazepam',
		'Oxcarbazepine'
	)

	UNION

	-- Keywords
	SELECT nct_id FROM clinical_trials.ct_keyword WHERE keyword IN (
		'Epilepsy',
		'Anti-epileptic drug',
		'Seizure'
	)

	UNION

	-- Words in brief_title
	SELECT nct_id FROM clinical_trials.ct_master WHERE
		lower(brief_title) SIMILAR TO '%([[:<:]]Levetiracetamum[[:>:]]|[[:<:]]valium[[:>:]]|[[:<:]]levetiracetam[[:>:]]|[[:<:]]diazepam[[:>:]]|[[:<:]]clobazam[[:>:]]|[[:<:]]keppra[[:>:]]|[[:<:]]oxcarbazepine[[:>:]]|[[:<:]]SPM927[[:>:]]|[[:<:]]carbamazepen[[:>:]]|[[:<:]]erlosamide[[:>:]]|[[:<:]]harkoseride[[:>:]]|[[:<:]]lamotriginum[[:>:]]|[[:<:]]lamotrigina[[:>:]]|[[:<:]]carbamazepina[[:>:]]|[[:<:]]lamotrigine[[:>:]]|[[:<:]]carbamazepinum[[:>:]]|[[:<:]]carbamazepine[[:>:]]|[[:<:]]diastat[[:>:]]|[[:<:]]carbamazépine[[:>:]]|[[:<:]]carbamazepin[[:>:]]|[[:<:]]vimpat[[:>:]]|[[:<:]]lamictal[[:>:]]|[[:<:]]lacosamide[[:>:]]|[[:<:]]onfi[[:>:]])%'

	UNION

	-- Words in title
	SELECT nct_id FROM clinical_trials.ct_master WHERE
		lower(official_title) SIMILAR TO '%([[:<:]]Levetiracetamum[[:>:]]|[[:<:]]valium[[:>:]]|[[:<:]]levetiracetam[[:>:]]|[[:<:]]diazepam[[:>:]]|[[:<:]]clobazam[[:>:]]|[[:<:]]keppra[[:>:]]|[[:<:]]oxcarbazepine[[:>:]]|[[:<:]]SPM927[[:>:]]|[[:<:]]carbamazepen[[:>:]]|[[:<:]]erlosamide[[:>:]]|[[:<:]]harkoseride[[:>:]]|[[:<:]]lamotriginum[[:>:]]|[[:<:]]lamotrigina[[:>:]]|[[:<:]]carbamazepina[[:>:]]|[[:<:]]lamotrigine[[:>:]]|[[:<:]]carbamazepinum[[:>:]]|[[:<:]]carbamazepine[[:>:]]|[[:<:]]diastat[[:>:]]|[[:<:]]carbamazépine[[:>:]]|[[:<:]]carbamazepin[[:>:]]|[[:<:]]vimpat[[:>:]]|[[:<:]]lamictal[[:>:]]|[[:<:]]lacosamide[[:>:]]|[[:<:]]onfi[[:>:]])%'

	UNION

	-- Words in summary
	SELECT nct_id FROM clinical_trials.ct_master WHERE		
		lower(brief_summary) SIMILAR TO '%([[:<:]]Levetiracetamum[[:>:]]|[[:<:]]valium[[:>:]]|[[:<:]]levetiracetam[[:>:]]|[[:<:]]diazepam[[:>:]]|[[:<:]]clobazam[[:>:]]|[[:<:]]keppra[[:>:]]|[[:<:]]oxcarbazepine[[:>:]]|[[:<:]]SPM927[[:>:]]|[[:<:]]carbamazepen[[:>:]]|[[:<:]]erlosamide[[:>:]]|[[:<:]]harkoseride[[:>:]]|[[:<:]]lamotriginum[[:>:]]|[[:<:]]lamotrigina[[:>:]]|[[:<:]]carbamazepina[[:>:]]|[[:<:]]lamotrigine[[:>:]]|[[:<:]]carbamazepinum[[:>:]]|[[:<:]]carbamazepine[[:>:]]|[[:<:]]diastat[[:>:]]|[[:<:]]carbamazépine[[:>:]]|[[:<:]]carbamazepin[[:>:]]|[[:<:]]vimpat[[:>:]]|[[:<:]]lamictal[[:>:]]|[[:<:]]lacosamide[[:>:]]|[[:<:]]onfi[[:>:]])%'

) AS q
ORDER BY nct_id;

--- Indexes
CREATE UNIQUE INDEX ON clinical_trials.view_clinical_trials_query(nct_id);

-- Permissions
GRANT ALL ON TABLE clinical_trials.view_clinical_trials_query TO bherr WITH GRANT OPTION;
GRANT ALL ON TABLE clinical_trials.view_clinical_trials_query TO gallantm WITH GRANT OPTION;
GRANT ALL ON TABLE clinical_trials.view_clinical_trials_query TO rionbr WITH GRANT OPTION;
GRANT ALL ON TABLE clinical_trials.view_clinical_trials_query TO larzhang WITH GRANT OPTION;
GRANT ALL ON TABLE clinical_trials.view_clinical_trials_query TO xw47 WITH GRANT OPTION;


-- Create the "data table" which has all the metadata we want for the corresponding "query table"
DROP MATERIALIZED VIEW IF EXISTS clinical_trials.view_clinical_trials;

CREATE MATERIALIZED VIEW clinical_trials.view_clinical_trials AS
SELECT
	m.nct_id,
	m.study_first_submitted,
	m.detailed_description,
	m.study_type,
	m.study_first_posted,
	m.brief_title,
	m.acronym,
	m.enrollment_type,
	m.overall_status,
	m.last_update_posted,
	m.verification_date,
	m.source,
	m.results_first_posted,
	m.completion_date,
	m.official_title,
	m.enrollment,
	m.brief_summary,
	m.phase,
	m.results_first_submitted,
	m.start_date,
	m.last_known_status,
	m.why_stopped
FROM clinical_trials.ct_master m
WHERE m.nct_id IN (SELECT nct_id FROM clinical_trials.view_clinical_trials_query);

-- Indexes
CREATE UNIQUE INDEX ON clinical_trials.view_clinical_trials(nct_id);

-- Permissions
GRANT ALL ON TABLE clinical_trials.view_clinical_trials TO bherr WITH GRANT OPTION;
GRANT ALL ON TABLE clinical_trials.view_clinical_trials TO gallantm WITH GRANT OPTION;
GRANT ALL ON TABLE clinical_trials.view_clinical_trials TO rionbr WITH GRANT OPTION;
GRANT ALL ON TABLE clinical_trials.view_clinical_trials TO larzhang WITH GRANT OPTION;
GRANT ALL ON TABLE clinical_trials.view_clinical_trials TO xw47 WITH GRANT OPTION;




