# Epilepsy Foundation Website Dataset Instructions

The scripts below were designed for MySQL, some convertion may be needed for Postgres.


## Important Tables

- `dw_users` # Information on Users
- `dw_forums` # Information on Forums
- `dw_chats` # Information on Chats
- `users_social_media` # The link between uid and social media accounts

* `dw` stands for (D)ata (W)arehouse tables


## How to drop all tables in the database

Use the script `drop_all_tables.sh`

```bash
$ ./drop_all_tables.sh {MySQL-User-Name} {MySQL-User-Password} {MySQL-Database-Name}
```


## How to load the website .sql dump into the database

Use the following command to load the `.sql` dump into the database

```bash
$ mysql -u {user} -p -h {host} {database} < prod-ep_core-epilepsydb[id]-[year]-[month]-[day].sql
```


## Drop unused tables

Use the following command to drop the tables that are not needed.

```sql
DROP TABLE IF EXISTS accesslog, actions, advancedqueue, advancedqueue_tags, apachesolr_environment, apachesolr_environment_variable, apachesolr_index_bundles, apachesolr_index_entities, apachesolr_index_entities_node, apachesolr_search_page, authmap, backup_migrate_destinations, backup_migrate_profiles, backup_migrate_schedules, batch, blazemeter, block, block_current_search, block_custom, block_node_type, block_role, blocked_ips, cache, cache_admin_menu, cache_apachesolr, cache_block, cache_bootstrap, cache_entity_comment, cache_entity_field_collection_item, cache_entity_file, cache_entity_node, cache_entity_taxonomy_term, cache_entity_taxonomy_vocabulary, cache_entity_user, cache_field, cache_filter, cache_form, cache_image, cache_libraries, cache_mailchimp_user, cache_media_xml, cache_menu, cache_metatag, cache_page, cache_panels, cache_path, cache_pulled_tweets, cache_rules, cache_salesforce_object, cache_scald, cache_token, cache_update, cache_views, cache_views_data, ckeditor_input_format, ckeditor_settings, cometchat, cometchat_announcements, cometchat_block, cometchat_comethistory, cometchat_games, cometchat_guests, cometchat_messages_old, cometchat_status, cometchat_videochatsessions, countries_country, ctools_css_cache, ctools_object_cache, current_search, date_format_locale, date_format_type, date_formats, dfp_tags, drupalchat_msg, drupalchat_users, ds_field_settings, ds_fields, ds_layout_settings, ds_vd, ds_view_modes, facetapi, feature_pubmed, feature_yahoo_news, field_collection_item, field_collection_item_revision, field_config, field_config_instance, field_data_body, field_data_ct_age_max, field_data_ct_age_max_type, field_data_ct_age_min, field_data_ct_age_min_type, field_data_ct_cat_id, field_data_ct_contact_name, field_data_ct_contact_title, field_data_ct_date_created, field_data_ct_date_updated, field_data_ct_description, field_data_ct_duration, field_data_ct_duration_type, field_data_ct_eligibility, field_data_ct_email, field_data_ct_fax, field_data_ct_gender, field_data_ct_inout_facility, field_data_ct_location_name, field_data_ct_other, field_data_ct_phase, field_data_ct_phone, field_data_ct_sponsor, field_data_ct_title, field_data_ct_trial_id, field_data_ct_url, field_data_field_about_affiliate, field_data_field_accent_color, field_data_field_address, field_data_field_advanced_topic, field_data_field_affiliate_address, field_data_field_affiliate_id, field_data_field_affiliate_name, field_data_field_affiliate_zips, field_data_field_authored_by, field_data_field_authored_date, field_data_field_banner_image, field_data_field_basic_topic, field_data_field_blogtalk_description, field_data_field_blogtalk_pubdate, field_data_field_brand_desc_adv, field_data_field_caption, field_data_field_carousel, field_data_field_category, field_data_field_city, field_data_field_contact_email, field_data_field_contact_name, field_data_field_contact_phone, field_data_field_dateline, field_data_field_dfp_ad_categories, field_data_field_dmv_appeal, field_data_field_doctors_to_report, field_data_field_dosing_adv, field_data_field_dosing_basic, field_data_field_drivers_license, field_data_field_epilepsy_type, field_data_field_event_date, field_data_field_event_location, field_data_field_event_type, field_data_field_facebook_graph_id, field_data_field_feature_image, field_data_field_field_form_type_type_descr, field_data_field_file_image_alt_text, field_data_field_file_image_title_text, field_data_field_form_type, field_data_field_form_type_adv, field_data_field_form_type_description, field_data_field_form_type_img, field_data_field_form_type_name, field_data_field_forms_adv, field_data_field_forms_basic, field_data_field_gender, field_data_field_gigya_share_bar, field_data_field_header_icon, field_data_field_header_text, field_data_field_highlights, field_data_field_highlights_links, field_data_field_icon_image, field_data_field_identification_card, field_data_field_image_test, field_data_field_indications_adv, field_data_field_indications_basic, field_data_field_large_desc_adv, field_data_field_large_desc_basic, field_data_field_legacy_tid, field_data_field_license_reporting, field_data_field_link, field_data_field_link_description, field_data_field_link_url, field_data_field_med_brand_desc, field_data_field_med_compound, field_data_field_med_sheet, field_data_field_med_topic, field_data_field_med_topics, field_data_field_menu_image, field_data_field_newsletters, field_data_field_periodic_updates, field_data_field_publication_date, field_data_field_related_links, field_data_field_reviewed_by, field_data_field_reviewed_date, field_data_field_sc_image, field_data_field_section_image, field_data_field_section_tagline, field_data_field_seizure_free_period, field_data_field_seizure_type, field_data_field_sidebar_std, field_data_field_slide_header, field_data_field_slide_image, field_data_field_slide_link_title, field_data_field_slide_link_url, field_data_field_slide_multimedia, field_data_field_slides, field_data_field_small_desc_adv, field_data_field_small_desc_basic, field_data_field_source, field_data_field_speaker, field_data_field_state, field_data_field_subhead, field_data_field_subtitle, field_data_field_summary, field_data_field_tagline, field_data_field_teaser, field_data_field_term_section, field_data_field_therapy_type, field_data_field_title_color, field_data_field_toll_free_phone, field_data_field_topic, field_data_field_trial_address, field_data_field_trial_geolocation, field_data_field_twitter, field_data_field_video_type, field_data_field_web_site, field_data_field_weight, field_data_field_work_phone, field_data_filedepot_folder_desc, field_data_filedepot_folder_file, field_data_scald_author_url, field_data_scald_authors, field_data_scald_file, field_data_scald_tags, field_data_scald_thumbnail, field_deleted_data_3, field_deleted_data_4, field_deleted_revision_3, field_deleted_revision_4, field_group, field_revision_body, field_revision_comment_body, field_revision_ct_age_max, field_revision_ct_age_max_type, field_revision_ct_age_min, field_revision_ct_age_min_type, field_revision_ct_cat_id, field_revision_ct_contact_name, field_revision_ct_contact_title, field_revision_ct_date_created, field_revision_ct_date_updated, field_revision_ct_description, field_revision_ct_duration, field_revision_ct_duration_type, field_revision_ct_eligibility, field_revision_ct_email, field_revision_ct_fax, field_revision_ct_gender, field_revision_ct_inout_facility, field_revision_ct_location_name, field_revision_ct_other, field_revision_ct_phase, field_revision_ct_phone, field_revision_ct_sponsor, field_revision_ct_title, field_revision_ct_trial_id, field_revision_ct_url, field_revision_field_about_affiliate, field_revision_field_accent_color, field_revision_field_address, field_revision_field_advanced_topic, field_revision_field_affiliate_address, field_revision_field_affiliate_id, field_revision_field_affiliate_name, field_revision_field_affiliate_zips, field_revision_field_authored_by, field_revision_field_authored_date, field_revision_field_banner_image, field_revision_field_basic_topic, field_revision_field_blogtalk_description, field_revision_field_blogtalk_pubdate, field_revision_field_body, field_revision_field_brand_desc_adv, field_revision_field_caption, field_revision_field_carousel, field_revision_field_category, field_revision_field_city, field_revision_field_contact_email, field_revision_field_contact_name, field_revision_field_contact_phone, field_revision_field_dateline, field_revision_field_dfp_ad_categories, field_revision_field_dmv_appeal, field_revision_field_dob, field_revision_field_doctors_to_report, field_revision_field_dosing_adv, field_revision_field_dosing_basic, field_revision_field_drivers_license, field_revision_field_epilepsy_type, field_revision_field_event_date, field_revision_field_event_location, field_revision_field_event_type, field_revision_field_facebook_graph_id, field_revision_field_feature_image, field_revision_field_field_form_type_type_descr, field_revision_field_file_image_alt_text, field_revision_field_file_image_title_text, field_revision_field_first_name, field_revision_field_form_type, field_revision_field_form_type_adv, field_revision_field_form_type_description, field_revision_field_form_type_img, field_revision_field_form_type_name, field_revision_field_forms_adv, field_revision_field_forms_basic, field_revision_field_gender, field_revision_field_gigya_share_bar, field_revision_field_header_icon, field_revision_field_header_text, field_revision_field_highlights, field_revision_field_highlights_links, field_revision_field_icon_image, field_revision_field_identification_card, field_revision_field_image_test, field_revision_field_indications_adv, field_revision_field_indications_basic, field_revision_field_large_desc_adv, field_revision_field_large_desc_basic, field_revision_field_last_name, field_revision_field_legacy_tid, field_revision_field_license_reporting, field_revision_field_link, field_revision_field_link_description, field_revision_field_link_url, field_revision_field_location, field_revision_field_med_brand_desc, field_revision_field_med_compound, field_revision_field_med_sheet, field_revision_field_med_topic, field_revision_field_med_topics, field_revision_field_member_type, field_revision_field_menu_image, field_revision_field_my_epilepsy_control, field_revision_field_newsletters, field_revision_field_parent_topic, field_revision_field_periodic_updates, field_revision_field_publication_date, field_revision_field_related_links, field_revision_field_reviewed_by, field_revision_field_reviewed_date, field_revision_field_sc_image, field_revision_field_section_image, field_revision_field_section_tagline, field_revision_field_seizure_free_period, field_revision_field_seizure_type, field_revision_field_sidebar_std, field_revision_field_slide_header, field_revision_field_slide_image, field_revision_field_slide_link_title, field_revision_field_slide_link_url, field_revision_field_slide_multimedia, field_revision_field_slides, field_revision_field_small_desc_adv, field_revision_field_small_desc_basic, field_revision_field_source, field_revision_field_speaker, field_revision_field_state, field_revision_field_subhead, field_revision_field_subtitle, field_revision_field_summary, field_revision_field_tagline, field_revision_field_teaser, field_revision_field_term_section, field_revision_field_therapy_type, field_revision_field_title_color, field_revision_field_toll_free_phone, field_revision_field_topic, field_revision_field_trial_address, field_revision_field_trial_geolocation, field_revision_field_twitter, field_revision_field_video_type, field_revision_field_web_site, field_revision_field_weight, field_revision_field_work_phone, field_revision_filedepot_folder_desc, field_revision_filedepot_folder_file, field_revision_scald_author_url, field_revision_scald_authors, field_revision_scald_file, field_revision_scald_tags, field_revision_scald_thumbnail, file_display, file_managed, file_metadata, file_type, file_usage, filedepot_access, filedepot_categories, filedepot_downloads, filedepot_export_queue, filedepot_favorites, filedepot_files, filedepot_filesubmissions, filedepot_fileversions, filedepot_folderindex, filedepot_import_queue, filedepot_notificationlog, filedepot_notifications, filedepot_recentfolders, filedepot_usersettings, filter, filter_format, flood, gigya_default_token_field_settings, history, honeypot_user, image_effects, image_styles, mailchimp_activity_entity, mailchimp_campaigns, mailchimp_lists, mailchimp_signup, mediafront_preset, mee_resource, menu_custom, menu_links, menu_router, metatag, metatag_config, mollom, mollom_form, nextag_items, nextag_metrics, nextag_words, node_access, node_comment_statistics, node_counter, node_type, oauth_common_consumer, oauth_common_context, oauth_common_nonce, oauth_common_provider_consumer, oauth_common_provider_token, oauth_common_token, page_manager_handlers, page_manager_pages, page_manager_weights, panelizer_defaults, panelizer_entity, panels_display, panels_layout, panels_mini, panels_pane, panels_renderer_pipeline, password_policy, password_policy_expiration, password_policy_force_change, password_policy_history, password_policy_role, pathauto_state, queue, rdf_mapping, redirect, registry, registry_file, role, role_permission, rules_config, rules_dependencies, rules_tags, rules_trigger, salesforce_mapping, salesforce_mapping_object, scald_atoms, scald_context_config, scald_licenses, scald_types, scheduler, search_dataset, search_index, search_node_links, search_total, semaphore, sequences, services_endpoint, services_user, sessions, shortcut_set, shortcut_set_users, site_verify, solr_best_bets, system, taxonomy_index, taxonomy_term_hierarchy, taxonomy_vocabulary, themekey_properties, themekey_ui_author_theme, themekey_ui_node_theme, twitter, twitter_account, url_alias, variable, views_display, views_view, watchdog, webform, webform_component, webform_emails, webform_last_download, webform_roles, webform_submissions, webform_submitted_data, wysiwyg, wysiwyg_user, xmlsitemap, xmlsitemap_sitemap, zipdata;
```

Note you will be prompted for the db password.


## Create `dw_users` table

```sql
DROP TABLE IF EXISTS dw_users;
CREATE TABLE dw_users
(
    uid INT(10) UNSIGNED NOT NULL PRIMARY KEY,
    realname VARCHAR(255),
    username VARCHAR(150) UNIQUE NOT NULL,
    mail VARCHAR(100),
    created INT(11) UNSIGNED,
    status TINYINT(4),
    language VARCHAR(12),
    dob INT(11) DEFAULT 0,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    member_type VARCHAR(50),
    my_epilepsy_control VARCHAR(255),
    country VARCHAR(2),
    state VARCHAR(255)
)
CHARACTER SET utf8 COLLATE utf8_general_ci;
```


## Populate `dw_users` table

This is the ETL command that populates the users table.

```sql
INSERT INTO dw_users (uid, username, realname, mail, created, status, language, dob, first_name, last_name, member_type, my_epilepsy_control, country, state)

SELECT u.uid, u.name, rn.realname, u.mail, u.created, u.status, u.language,
    dob.field_dob_value as DOB,
    fn.field_first_name_value as first_name,
    ln.field_last_name_value as last_name,
    (SELECT name FROM taxonomy_term_data WHERE tid = mt.field_member_type_tid) as member_type,
    ec.field_my_epilepsy_control_value as my_epilepsy_control,
    loc.field_location_country as country,
    loc.field_location_administrative_area as adm_area
    
FROM users u
LEFT JOIN realname rn ON rn.uid = u.uid
LEFT JOIN field_data_field_dob dob ON dob.entity_id = u.uid
LEFT JOIN field_data_field_first_name fn ON fn.entity_id = u.uid
LEFT JOIN field_data_field_last_name ln ON ln.entity_id = u.uid
LEFT JOIN field_data_field_member_type mt ON mt.entity_id = u.uid
LEFT JOIN field_data_field_my_epilepsy_control ec on ec.entity_id = u.uid
LEFT JOIN field_data_field_location loc on loc.entity_id = u.uid
;
```

In case anything goes wrong, truncate the table:

```sql
TRUNCATE TABLE dw_users;
```


## Create `dw_forums` table

```sql
DROP TABLE IF EXISTS dw_forums;
CREATE TABLE dw_forums
(
    pid VARCHAR(25) PRIMARY KEY,
    type VARCHAR(32) NOT NULL,
    parentid INT(10) UNSIGNED,
    topicid  INT(10) UNSIGNED,
    topic VARCHAR(255) NOT NULL,
    uid INT(10) UNSIGNED,
    title VARCHAR(255) NULL,
    created INT(11) UNSIGNED,
    text_original LONGTEXT,
    text_clean LONGTEXT,
    text_lemmed LONGTEXT,
    text_stemmed LONGTEXT
)
CHARACTER SET utf8 COLLATE utf8_general_ci;
```


## Populate `dw_forums` table

This is the ETL command that populates the posts DW table.

The `dw_forums` comes from different tables. 
1. the `node` table along with two others; and
2. the `comments` table

As of now, we are only considering nodes from `forum_posts`.

```sql
INSERT INTO dw_forums (pid, type, parentid, topicid, topic, uid, title, created, text_original)

#
# Get forum_post nodes

SELECT CONCAT('pid-',n.nid), 'forum-post', NULL,
    n2.nid, n2.title,
    n.uid, n.title, n.created,
    b.field_body_value
FROM node n
LEFT JOIN node_revision nr ON n.vid = nr.vid
RIGHT JOIN field_data_field_body b ON n.nid = b.entity_id
RIGHT JOIN field_data_field_parent_topic t ON n.nid = t.entity_id
RIGHT JOIN node n2 ON n2.nid = t.field_parent_topic_target_id
WHERE n.type IN ('forum_post')
AND n2.status = 1 # only active topics

UNION

#
# Get forum_post comments
#
SELECT CONCAT('pid-',n.nid,'|cid-', c.cid), 'forum-comment', c.pid,
    n2.nid, n2.title,
    c.uid, c.subject, c.created, cb.comment_body_value
FROM comment c
LEFT JOIN field_data_comment_body cb ON c.cid = cb.entity_id
LEFT JOIN node n ON c.nid = n.nid
RIGHT JOIN field_data_field_parent_topic t ON n.nid = t.entity_id
RIGHT JOIN node n2 ON n2.nid = t.field_parent_topic_target_id
WHERE n.type IN ('forum_post')
AND n2.status = 1 # only active topics
;
```

In case anything goes wrong, truncate the table:

```sql
TRUNCATE TABLE dw_forums;
```

Now since there many posts that contain spam (or viruses), we need to remove a few here and there.

```sql
DELETE FROM dw_forums WHERE text_original LIKE '%amoxil%' AND text_original LIKE '%phentermine%' AND text_original LIKE '%viagra%' AND text_original LIKE '%lexapro%' AND text_original LIKE '%cialis%';
DELETE FROM dw_forums WHERE text_original LIKE '%Cialis online%' AND text_original LIKE '%buy cialis%' AND text_original LIKE '%levitra%' AND text_original LIKE '%natural viagra%' AND text_original LIKE '%discount viagra%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://jonhandhisdog.com/forum/html/emoticons/sup/index.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://download.aaa.edu/cp/images/Extropia/.@Tut/.~Dobro/free-online-shooting-game.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.sbuniv.edu/athletics/golf/05/.~1/nokia-mp3-ringtones.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.ssw.uga.edu/social/temp/newstuff/public_html/sections/announcements/cache/.xp/.@pro/Lipitor.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://landval.gsfc.nasa.gov/images/_vti_cnf/.info/~@more/Clarinex.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://nyci.edu/admissions/.~@ebababta/.~n/Cyclobenzaprine.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://mech.sharif.edu/~h_tamaddoni/files/doc.php?1.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://lcvx.xshourt.net/Viagra-Drug-Test%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://winter.eecs.umich.edu/soarwiki/images/thumb/c/cf/wp-slider/.cache455546~4/driving/.~farmacy/Mircette.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.veromaxx.com/%' AND text_original LIKE '%viagra%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.fxdo.us/imgsearch/8/Viagra/1.php%';
DELETE FROM dw_forums WHERE text_original LIKE '%jjameshood10@outlook.com%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.sleep-safe.co.uk/buynowna.htm%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.ehealthinsurance.com/low-cost-health-insurance%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.anyincn.com/%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.orientalpearls.net/%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.uklondons.com/%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://p1ring.xshorturl.org/3/free-ringtones-upload.html%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.cheap-discount-cigarettes.biz%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://www.wowatm.com%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://bit.ly/1jP6zRI%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://camaraourense.com/includes/oakley-7.php%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://xshorturl.info/g3/%';
DELETE FROM dw_forums WHERE text_original LIKE '%http://uk.virginmoneygiving.com/Ia%';
DELETE FROM dw_forums WHERE text_original LIKE '%shes indian shes indian shes indianshes%';
DELETE FROM dw_forums WHERE uid IN (152156, 152146, 152141, 165321); # Trolls
```


## Create `iflychat` table

```sql
DROP TABLE IF EXISTS iflychat;
CREATE TABLE iflychat
(
    time DATETIME,
    from_id INT(10) UNSIGNED NOT NULL,
    to_id INT(10) UNSIGNED,
    room_id INT(10) UNSIGNED DEFAULT NULL,
    from_name VARCHAR(50) NOT NULL,
    to_name VARCHAR(50),
    room_name VARCHAR(50) DEFAULT NULL,
    message_id VARCHAR(35) PRIMARY KEY,
    message TEXT,
    color VARCHAR(10),
    role VARCHAR(255),
    picture_url VARCHAR(255),
    profile_url VARCHAR(255),
    `like` INT(1) UNSIGNED
)
CHARACTER SET utf8 COLLATE utf8_general_ci;
```


## Populate `iflychat` table

First you need to use some Regular Expression to change the hour number from 0:00 to 12:00.
Just copy the RE below and use in a text replacement software:

> Find: (\d{2}\/\d{2}\/\d{2},) (0)(:\d{2})
> Replace: \1 12\3


```sql
SHOW WARNINGS;
LOAD DATA LOCAL INFILE '<path>/chat-log-05-05-16.csv' INTO TABLE epilepsy.iflychat FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES (@var_time, from_id, @var_to_id, @var_room_id, from_name, to_name, @var_room_name, message_id, message, color, role, picture_url, profile_url, `like`)
    SET time = STR_TO_DATE(@var_time, '%m/%d/%y, %l:%i %p')
    , room_id = IF(@var_room_id = '', Null, @var_room_id)
    , room_name = IF(@var_room_name = '', Null, @var_room_name)
    , to_id = IF(@var_to_id = '', Null, @var_to_id)
;
```

In case anything goes wrong, truncate the table:


```sql
TRUNCATE TABLE iflychat;
```


## Create `dw_chats` table

```sql
DROP TABLE IF EXISTS dw_chats;
CREATE TABLE dw_chats
(
    cid VARCHAR(35) PRIMARY KEY,
    type VARCHAR(32) NOT NULL,
    chatroomid INT(10) UNSIGNED,
    chatroom VARCHAR(64),
    uid INT(10) UNSIGNED,
    touid INT(10) UNSIGNED,
    created INT(11) UNSIGNED,
    text_original LONGTEXT,
    text_clean LONGTEXT,
    text_lemmed LONGTEXT,
    text_stemmed LONGTEXT
)
CHARACTER SET utf8 COLLATE utf8_general_ci;
```


## Populate `dw_chats` table

This is the ETL command that populates the chats DW table.

The `dw_chats` comes from different tables. 
1. the `cometchat_chatroommessages` public chatroom table; and
2. the `cometchat` private chat messages table.

* NOTE: There are several orfan `chatroom_messages`. They have no link to the `chatrooms` table.
* NOTE: There are two databases of chats. One is called 'Comet Chat', and it is stored within the Website MySQL dump.
The other is from 'iFlyChat', a third-party service that was implmemented post March 2015.

```sql
INSERT INTO dw_chats (cid, type, chatroomid, chatroom, uid, touid, created, text_original)

#
# Comet Chatroom messages
#
SELECT CONCAT('rid-', m.chatroomid,'-mid-',m.id), 'comet-chat-room', m.chatroomid,
    IFNULL(c.name, 'No name (orfan record)'),
    m.userid, m.chatroomid, m.sent, m.message
FROM cometchat_chatroommessages m
LEFT JOIN cometchat_chatrooms c ON c.id = m.chatroomid


UNION

#
# Comet Private chat messages
#
SELECT CONCAT('mid-', m.id), 'comet-chat-private', NULL, NULL, m.from, m.to, m.sent, m.message
FROM cometchat m

UNION

#
# iFlyChat chatroom messages
#
SELECT message_id, 'iflychat-chat-room', room_id, room_name, from_id, room_id, time, message
FROM iflychat
WHERE room_id IS NOT NULL

UNION
#
# iFlyChat private messages
#
SELECT message_id, 'iflychat-chat-private', room_id, room_name, from_id, to_id, time, message
FROM iflychat
WHERE room_id IS NULL
;
```

In case anything goes wrong, truncate the table:

```sql
TRUNCATE TABLE dw_chats;
```

The following commands removes some messages, description within:

```sql
# Delete invites
DELETE FROM dw_chats WHERE text_original LIKE '%has invited you to join a chatroom.%';
# Delete messages with less or equal than 3 chars
DELETE FROM dw_chats WHERE LENGTH(text_original) <= 3;
# Delete chat from chatrooms with fewer than 10 messages
DELETE FROM dw_chats WHERE touid IN (
    SELECT * FROM (
        SELECT touid FROM dw_chats WHERE type = 'comet-chat-room' GROUP BY touid HAVING count(*) < 10
        ) AS a
    );
```


## Create `users_social_media` table

```sql
DROP TABLE IF EXISTS users_social_media;
CREATE TABLE users_social_media
(
	uid INT(10) UNSIGNED,
	social_media VARCHAR(30) NOT NULL,
	id_social_media VARCHAR(30) NOT NULL
)
CHARACTER SET utf8 COLLATE utf8_general_ci;
```

## Populate `users_social_media` table

The social media ids are not in the database dump. You have to export a CSV file from Gigya and import it into a new table.
Here is the command to import the file:

```sql
SHOW WARNINGS;
LOAD DATA LOCAL INFILE '<path>/export-gigya-epilepsy-2016-05-04.csv' INTO TABLE epilepsy.users_social_media FIELDS TERMINATED BY ','
	ENCLOSED BY '"'
	LINES TERMINATED BY '\r\n'
	IGNORE 1 LINES;
```

In case anything goes wrong, truncate (empty) the table:

```sql
TRUNCATE TABLE users_social_media;
```

There are some users that have the wrong `uid` associated, here is a list. Correct the .sql file first and then import

```sql
"143506","facebook","1229472221"
"143506","googleplus","112938335105834714629"
```

## Fix text on database by removing html tags

run the script [01-preprocess-fix-db-text.py](01-preprocess-fix-db-text.py)
