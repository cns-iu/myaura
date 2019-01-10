
CREATE TABLE ct_master (
	id varchar(15) NOT NULL PRIMARY KEY, 
	org_study_id VARCHAR,
	nct_id varchar(15),
	brief_title VARCHAR,
	acronym VARCHAR,
	official_title VARCHAR,
	source VARCHAR,
	brief_summary text,
	detailed_description text,
	overall_status VARCHAR,
	last_known_status varchar,
	why_stopped VARCHAR,
	start_date_type VARCHAR,
	start_date VARCHAR,
	completion_date_type VARCHAR,
	completion_date VARCHAR,
	primary_completion_date_type VARCHAR,
        primary_completion_date VARCHAR,
	phase VARCHAR,
	study_type VARCHAR,
	has_expanded_access varchar,
	target_duration VARCHAR,
	number_of_arms VARCHAR,
	number_of_groups VARCHAR,
	enrollment varchar,
	enrollment_type varchar,
	biospec_retention VARCHAR,
	biospec_desc VARCHAR,
	verification_date VARCHAR,
	study_first_submitted VARCHAR,
	study_first_submitted_qc VARCHAR,
	study_first_posted VARCHAR,
	study_first_posted_type VARCHAR,
	results_first_submitted VARCHAR,
	results_first_submitted_qc VARCHAR,
	results_first_posted VARCHAR,
	results_first_posted_type VARCHAR,
	disposition_first_submitted VARCHAR,
	disposition_first_submitted_qc VARCHAR,
	disposition_first_posted VARCHAR,
	disposition_first_posted_type VARCHAR,
	last_update_submitted VARCHAR,
	last_update_submitted_qc VARCHAR,
	last_update_posted VARCHAR,
	last_update_posted_type VARCHAR
);

create table ct_required_header (
	id varchar(15) not null,
	rh_ctr int not null,
	download_date varchar,
	link_text varchar,
	url varchar
);

CREATE TABLE ct_id_info (
	id VARCHAR(15) NOT NULL,
	id_info_ctr int NOT NULL,
	org_study_id VARCHAR NOT NULL,
	nct_id VARCHAR
);

CREATE TABLE ct_nct_aliases (
        id VARCHAR(15) NOT NULL,
        id_info_ctr int not null,
        nct_alias_ctr INT NOT NULL,
        nct_alias varchar
);

CREATE TABLE ct_secondary_id (
        id VARCHAR(15) NOT NULL,
        id_info_ctr int not null,
        sec_id_ctr INT NOT NULL,
        secondary_id varchar 
);

CREATE TABLE ct_lead_sponsors (
        id VARCHAR(15) NOT NULL,
        lead_id_ctr INT NOT NULL,
        agency VARCHAR,
	agency_class VARCHAR
);

CREATE TABLE ct_collaborator_sponsors (
        id VARCHAR(15) NOT NULL,
        lead_coll_id_ctr INT NOT NULL,
        agency VARCHAR,
        agency_class VARCHAR
);

create table ct_oversight_info (
        id VARCHAR(15) NOT NULL,
        oversight_id_ctr INT NOT NULL,
	has_dmc varchar,
	is_fda_regulated_drug varchar,
	is_fda_regulated_device varchar,
	is_unapproved_device varchar,
	is_ppsd varchar,
	is_us_export varchar
);

create table ct_expanded_access (
	id varchar(15) not null,
	exp_acc_id_ctr int not null,
	type_individual varchar,
	type_intermediate varchar,
	type_treatment varchar
);

create table ct_study_design_info (
	id varchar(15) not null,
	study_design_id_ctr int not null,
	allocation VARCHAR,
	primary_purpose VARCHAR,
	intervention_model VARCHAR,
	intervention_mode_description VARCHAR,
	observational_model VARCHAR,
	time_perspective VARCHAR,
	masking VARCHAR,
	masking_description VARCHAR
);

CREATE TABLE ct_primary_outcome (
        id VARCHAR(15) NOT NULL,
        pri_out_id_ctr INT NOT NULL,
	measure VARCHAR,
        time_frame VARCHAR,
	description VARCHAR
);

CREATE TABLE ct_secondary_outcome (
        id VARCHAR(15) NOT NULL,
        sec_out_id_ctr INT NOT NULL,
        measure VARCHAR,
        time_frame VARCHAR,
        description VARCHAR
);

CREATE TABLE ct_other_outcome (
        id VARCHAR(15) NOT NULL,
        oth_out_id_ctr INT NOT NULL,
        measure VARCHAR,
        time_frame VARCHAR,
        description VARCHAR
);


CREATE TABLE ct_condition (
        id VARCHAR(15) NOT NULL,
        condition_id_ctr INT NOT NULL,
        condition VARCHAR
);

CREATE TABLE ct_arm_group (
        id VARCHAR(15) NOT NULL,
        arm_grp_id_ctr INT NOT NULL,
        arm_group_label VARCHAR,
	arm_group_type VARCHAR,
	description VARCHAR
);

CREATE TABLE ct_intervention (
        id VARCHAR(15) NOT NULL,
        intervention_id_ctr INT NOT NULL,
        intervention_type VARCHAR,
        intervention_name VARCHAR,
        description VARCHAR
);

create table ct_intervention_agl (
        id VARCHAR(15) NOT NULL,
        intervention_id_ctr INT NOT NULL,
        iagl_ctr int not null,
	arm_group_label varchar
);


CREATE TABLE ct_intervention_other_name (
        id VARCHAR(15) NOT NULL,
        intervention_id_ctr INT NOT NULL,
        cion_ctr INT NOT NULL,
        other_name VARCHAR
);

CREATE TABLE ct_eligibility (
        id VARCHAR(15) NOT NULL,
        eligibility_id_ctr INT NOT NULL,
	study_pop varchar,
	sampling_method VARCHAR,
	criteria TEXT,
	gender VARCHAR,
	gender_based VARCHAR,
	gender_description VARCHAR,
	minimum_age VARCHAR,
	maximum_age VARCHAR,
	healthy_volunteers VARCHAR
);

CREATE TABLE ct_overall_official (
        id VARCHAR(15) NOT NULL,
        over_off_id_ctr INT NOT NULL,
        first_name VARCHAR,
        middle_name VARCHAR,
        last_name VARCHAR,
	degrees VARCHAR,
	role VARCHAR,
	affiliation VARCHAR
);

CREATE TABLE ct_overall_contact (
        id VARCHAR(15) NOT NULL,
        over_cont_id_ctr INT NOT NULL,
        first_name VARCHAR,
        middle_name VARCHAR,
        last_name VARCHAR,
	degrees VARCHAR,
	phone VARCHAR,
	phone_ext VARCHAR,
	email VARCHAR
);

CREATE TABLE ct_overall_contact_backup (
        id VARCHAR(15) NOT NULL,
        over_cont_bck_id_ctr INT NOT NULL,
        first_name VARCHAR,
        middle_name VARCHAR,
        last_name VARCHAR,
	degrees VARCHAR,
	phone VARCHAR,
	phone_ext VARCHAR,
	email VARCHAR
);

CREATE TABLE ct_location (
        id VARCHAR(15) NOT NULL,
        loc_ctr INT NOT NULL,
	status varchar
);

CREATE TABLE ct_facility (
        id VARCHAR(15) NOT NULL,
        loc_ctr INT NOT NULL,
        fid_ctr INT NOT NULL,
        name varchar,
	status varchar
);

create table ct_fac_address (
        id VARCHAR(15) NOT NULL,
        loc_ctr INT NOT NULL,
        fid_ctr INT NOT NULL,
        faid_ctr INT NOT NULL,
	city varchar,
	state varchar,
	zip varchar,
	country varchar
);
	
create table ct_location_contact (
        id VARCHAR(15) NOT NULL,
        loc_ctr INT NOT NULL,
        loc_cont_id_ctr INT NOT NULL,
        first_name VARCHAR,
        middle_name VARCHAR,
        last_name VARCHAR,
        degrees VARCHAR,
        phone VARCHAR,
        phone_ext VARCHAR,
        email VARCHAR
);

create table ct_location_contact_backup (
        id VARCHAR(15) NOT NULL,
        loc_ctr INT NOT NULL,
        loc_cont_bck_id_ctr INT NOT NULL,
        first_name VARCHAR,
        middle_name VARCHAR,
        last_name VARCHAR,
        degrees VARCHAR,
        phone VARCHAR,
        phone_ext VARCHAR,
        email VARCHAR
);

CREATE TABLE ct_location_investigator (
        id VARCHAR(15) NOT NULL,
        loc_ctr INT NOT NULL,
	loc_invest_id_ctr INT NOT NULL,
	first_name VARCHAR,
        middle_name VARCHAR,
        last_name VARCHAR,
        degrees VARCHAR,
        role VARCHAR,
        affiliation VARCHAR
);

CREATE TABLE ct_location_countries (
        id VARCHAR(15) NOT NULL,
        loc_country_id_ctr INT NOT NULL,
        country VARCHAR
);

CREATE TABLE ct_removed_countries (
        id VARCHAR(15) NOT NULL,
        rm_country_id_ctr INT NOT NULL,
        country VARCHAR
);

CREATE TABLE ct_links (
        id VARCHAR(15) NOT NULL,
        links_id_ctr INT NOT NULL,
        url VARCHAR,
	link_desc VARCHAR
);

CREATE TABLE ct_references (
        id VARCHAR(15) NOT NULL,
        ref_id_ctr INT NOT NULL,
        citation VARCHAR,
        pmid VARCHAR
);

CREATE TABLE ct_results_references (
        id VARCHAR(15) NOT NULL,
        results_ref_id_ctr INT NOT NULL,
        citation VARCHAR,
        pmid VARCHAR
);

CREATE TABLE ct_responsible_party (
        id VARCHAR(15) NOT NULL,
        ref_party_id_ctr INT NOT NULL,
        name_title VARCHAR,
        organization VARCHAR,
	responsible_party_type VARCHAR,
	investigator_affiliation VARCHAR,
	investigator_full_name VARCHAR,
	investigator_title VARCHAR
);

CREATE TABLE ct_keyword (
        id VARCHAR(15) NOT NULL,
        keyword_id_ctr INT NOT NULL,
        keyword VARCHAR
);

CREATE TABLE ct_condition_browse (
        id VARCHAR(15) NOT NULL,
        cond_brow_id_ctr INT NOT NULL,
        mesh_term VARCHAR
);

CREATE TABLE ct_intervention_browse (
        id VARCHAR(15) NOT NULL,
        intervention_brow_id_ctr INT NOT NULL,
        mesh_term VARCHAR
);

create table ct_patient_data (
	id varchar(15) not null,
	patient_id_ctr int not null,
	sharing_ipd varchar,
	ipd_description varchar,
	ipd_time_frame varchar,
	ipd_access_criteria varchar,
	ipd_url varchar
);

create table ct_patient_data_info_type (
	id varchar(15) not null,
	patient_id_ctr int not null,
	ipd_info_ctr int not null,
	ipd_info_type varchar
);	

create table ct_study_doc (
	id varchar(15) not null,
	study_doc_id_ctr int not null,
	doc_id varchar,
	doc_type varchar,
	doc_url varchar,
	doc_comment varchar
);

create table ct_pending_results_submitted (
	id varchar(15) not null,
	pend_result_sub_id_ctr int not null,
	submitted_date varchar
);

create table ct_pending_results_returned (
	id varchar(15) not null,
	pend_result_return_id_ctr int not null,
	returned_date varchar
);

create table ct_pending_results_submission_canceled (
	id varchar(15) not null,
	pend_result_sub_can_id_ctr int not null,
	submission_canceled_date varchar
);

CREATE TABLE ct_results (
	id VARCHAR(15) NOT NULL,
	cr_id_ctr INT NOT NULL,
	   recruitment_details VARCHAR,
	   pre_assignment_details VARCHAR,
	events_timeframe VARCHAR,
	events_desc VARCHAR,
	pi_employee VARCHAR,
	restrictive_agreement VARCHAR,
	limitations_and_caveats VARCHAR,
	poc_name_or_title VARCHAR,
	poc_organization VARCHAR,
	poc_phone VARCHAR,
	poc_email VARCHAR
);

CREATE TABLE ct_results_group (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
	ctg_ctr INT NOT NULL,
        group_id VARCHAR,
        title VARCHAR,
        description VARCHAR
);

CREATE TABLE ct_results_period (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        ctp_ctr INT NOT NULL,
        title VARCHAR
);

CREATE TABLE ct_results_period_milestones (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        ctp_ctr INT NOT NULL,
	ctpm_ctr INT NOT NULL,
        title VARCHAR
);

CREATE TABLE ct_results_period_participants (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        ctp_ctr INT NOT NULL,
        ctpm_ctr INT NOT NULL,
	ctpmp_ctr INT NOT NULL,
        group_id VARCHAR,
	count VARCHAR
);

CREATE TABLE ct_results_period_drops (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        ctp_ctr INT NOT NULL,
        ctpd_ctr INT NOT NULL,
        title VARCHAR
);

CREATE TABLE ct_results_period_drops_participants (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        ctp_ctr INT NOT NULL,
        ctpd_ctr INT NOT NULL,
        ctpdp_ctr INT NOT NULL,
        group_id VARCHAR,
        count VARCHAR
);

create table ct_results_baseline (
	id varchar(15) not null,
	cr_id_ctr int not null,
	population varchar
);

CREATE TABLE ct_results_baseline_groups (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        ctbg_ctr INT NOT NULL,
	title VARCHAR,
	description VARCHAR,
	group_id VARCHAR
);

create table ct_results_baseline_analyzed (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        ctba_ctr INT NOT NULL,
	units VARCHAR,
	scope VARCHAR
);

create table ct_results_baseline_analyzed_count (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        analyzed_ctr INT NOT NULL,
	bac_ctr int not null,
	group_id varchar,
	value varchar
);

CREATE TABLE ct_results_baseline_measures (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        bm_ctr INT NOT NULL,
        title VARCHAR,
        description VARCHAR,
	population varchar,
        units VARCHAR,
	params VARCHAR,
	dispersion VARCHAR,
        unit_analyzed VARCHAR
);

create table ct_results_baseline_measure_analyzed (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        bm_ctr INT NOT NULL,
        bma_ctr INT NOT NULL,
	units VARCHAR,
	scope VARCHAR
);

create table ct_results_baseline_measure_analyzed_count (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        bm_ctr INT NOT NULL,
        bma_ctr INT NOT NULL,
	bmac_ctr int not null,
	group_id varchar,
	value varchar
);

create table ct_results_baseline_measure_class (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        bm_ctr INT NOT NULL,
        bmc_ctr INT NOT NULL,
	title varchar
);

create table ct_results_baseline_measure_class_analyzed (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        bm_ctr INT NOT NULL,
        bmc_ctr INT NOT NULL,
	bmca_ctr int not null,
	units VARCHAR,
	scope VARCHAR
);

create table ct_results_baseline_measure_class_analyzed_count (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        bm_ctr INT NOT NULL,
        bmc_ctr INT NOT NULL,
        bmca_ctr INT NOT NULL,
	bmcac_ctr int not null,
	group_id VARCHAR,
	value VARCHAR
);

CREATE TABLE ct_results_baseline_measure_categories (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        bm_ctr INT NOT NULL,
        bmc_ctr INT NOT NULL,
        bmcc_ctr INT NOT NULL,
        title VARCHAR
);

CREATE TABLE ct_results_baseline_measure_values (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        bm_ctr INT NOT NULL,
        bmc_ctr INT NOT NULL,
	bmcc_ctr INT NOT NULL,
	bmccm_ctr INT NOT NULL,
	group_id VARCHAR,
	lower_limit VARCHAR,
	spread VARCHAR,
	upper_limit VARCHAR,
	value VARCHAR,
	value_note VARCHAR
);

CREATE TABLE ct_results_outcomes (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
	type VARCHAR,
	title VARCHAR,
	description VARCHAR,
	time_frame VARCHAR,
	safety_issue VARCHAR,
	posting_date VARCHAR,
	population VARCHAR
);

CREATE TABLE ct_results_outcomes_groups (
        id VARCHAR(15) NOT NULL,
	cr_id_ctr int not null,
        oc_ctr INT NOT NULL,
        ocg_ctr INT NOT NULL,
        group_id VARCHAR,
        title VARCHAR,
        description VARCHAR
);

CREATE TABLE ct_results_outcome_measures (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
        ocm_ctr INT NOT NULL,
        title VARCHAR,
        description VARCHAR,
        population VARCHAR,
        units VARCHAR,
        params VARCHAR,
        dispersion VARCHAR,
	units_analyzed varchar
);

create table ct_results_outcome_measure_analyzed (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
        ocm_ctr INT NOT NULL,
        ocma_ctr INT NOT NULL,
	units VARCHAR,
	scope VARCHAR
);

create table ct_results_outcome_measure_analyzed_count (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
        ocm_ctr INT NOT NULL,
	ocma_ctr int not null,
	ocmac_ctr int not null,
	group_id varchar,
	value varchar
);

create table ct_results_outcome_measure_class (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
        ocm_ctr INT NOT NULL,
        occ_ctr INT NOT NULL,
	title varchar
);

create table ct_results_outcome_measure_class_analyzed (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
        ocm_ctr INT NOT NULL,
	occ_ctr int not null,
	occa_ctr int not null,
	units VARCHAR,
	scope VARCHAR
);

create table ct_results_outcome_measure_class_analyzed_count (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
	oc_ctr int not null,
	occ_ctr int not null,
	occa_ctr int not null,
	occac_ctr int not null,
	group_id varchar,
	value varchar
);

CREATE TABLE ct_results_outcome_measure_class_categories (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
        ocm_ctr INT NOT NULL,
        occ_ctr INT NOT NULL,
        occc_ctr INT NOT NULL,
        title VARCHAR
);

CREATE TABLE ct_results_outcome_measure_class_categories_measurement (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
	oc_ctr INT NOT NULL,
        ocm_ctr INT NOT NULL,
        occ_ctr INT NOT NULL,
        occc_ctr INT NOT NULL,
        occcm_ctr INT NOT NULL,
        group_id VARCHAR,
        value VARCHAR,
        spread VARCHAR,
        lower_limit VARCHAR,
        upper_limit VARCHAR,
        value_note VARCHAR
);

CREATE TABLE ct_results_outcome_analysis_group (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
        oa_ctr INT NOT NULL,
        oag_ctr INT NOT NULL,
        group_id VARCHAR
);

CREATE TABLE ct_results_outcome_analysis (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        oc_ctr INT NOT NULL,
        oa_ctr INT NOT NULL,
        groups_desc VARCHAR,
        non_inferiority_type VARCHAR,
        non_inferiority_desc VARCHAR,
        p_value VARCHAR,
	p_value_desc VARCHAR,
	method VARCHAR,
        method_desc VARCHAR,
        param_type VARCHAR,
        param_value VARCHAR,
        dispersion_type VARCHAR,
        dispersion_value VARCHAR,
        ci_percent VARCHAR,
        ci_n_sides VARCHAR,
        ci_lower_limit VARCHAR,
        ci_upper_limit VARCHAR,
        ci_upper_limit_na_comment VARCHAR,
        estimate_desc VARCHAR,
	other_analysis_desc text
);

CREATE TABLE ct_results_outcome_group (
        id VARCHAR(15) NOT NULL,
        results_ctr INT NOT NULL,
        outcome_ctr INT NOT NULL,
	oag_ctr INT NOT NULL,
	group_id VARCHAR
);

create table ct_results_reported_events (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
	time_frame VARCHAR,
	description varchar
);

CREATE TABLE ct_results_reported_events_groups (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
        reg_ctr INT NOT NULL,
	title VARCHAR,
	description VARCHAR,
        group_id VARCHAR
); 

CREATE TABLE ct_results_events_serious (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
	res_ctr INT NOT NULL,
	frequency_threshold VARCHAR,
	default_vocab VARCHAR,
	default_assessment VARCHAR
);

CREATE TABLE ct_results_events_serious_categories (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
	res_ctr INT NOT NULL,
	resc_ctr INT NOT NULL,
        title VARCHAR
);

CREATE TABLE ct_results_events_serious_categories_events (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
	res_ctr INT NOT NULL,
	resc_ctr INT NOT NULL,
	resce_ctr INT NOT NULL,
        vocab VARCHAR,
        sub_title VARCHAR,
	assessment VARCHAR,
	event_desc VARCHAR
);

CREATE TABLE ct_results_events_serious_categories_events_counts (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
	res_ctr INT NOT NULL,
	resc_ctr INT NOT NULL,
	resce_ctr INT NOT NULL,
	rescec_ctr INT NOT NULL,
        group_id VARCHAR,
        subjects_affected VARCHAR,
        subjects_at_risk VARCHAR,
	event_count VARCHAR
);

CREATE TABLE ct_results_events_other (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
        reo_ctr INT NOT NULL,
        frequency_threshold VARCHAR,
        default_vocab VARCHAR,
        default_assessment VARCHAR
);

CREATE TABLE ct_results_events_other_categories (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
        reo_ctr INT NOT NULL,
        reoc_ctr INT NOT NULL,
        title VARCHAR
);

CREATE TABLE ct_results_events_other_categories_events (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
        reo_ctr INT NOT NULL,
        reoc_ctr INT NOT NULL,
        reoce_ctr INT NOT NULL,
        vocab VARCHAR,
        sub_title VARCHAR,
        assessment VARCHAR,
        description VARCHAR
);

CREATE TABLE ct_results_events_other_categories_events_counts (
        id VARCHAR(15) NOT NULL,
        cr_id_ctr INT NOT NULL,
        re_ctr INT NOT NULL,
        reo_ctr INT NOT NULL,
        reoc_ctr INT NOT NULL,
        reoce_ctr INT NOT NULL,
        reocec_ctr INT NOT NULL,
        group_id VARCHAR,
        subjects_affected VARCHAR,
        subjects_at_risk VARCHAR,
        events VARCHAR
);



