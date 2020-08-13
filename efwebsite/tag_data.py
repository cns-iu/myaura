# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 09:45:57 2019

@author: Sikander
"""

import sys
sys.path.insert(0, '../ddi_project/include')
sys.path.insert(0, '../ddi_project/social/include')

import db_init_ddi_project as db
import numpy as np
import pandas as pd
from datetime import datetime
from termdictparser import Sentences, TermDictionaryParser
import pickle
import os

USERS = 0
TOPICS = 0
THREADS = 0
VIEW_USERS = 0
VIEW_TOPICS = 0
CHATS = 1

################################################################################
#################               USER TIMELINES             #####################
################################################################################
if USERS == 1:
	dicttimestamp = '20180706'
	print '--- Loading MySQL dictionary (%s)---' % dicttimestamp
	engineD = db.connectToMySQL(server='mysql_ddi_dictionaries')
	tablename = 'dict_%s' % (dicttimestamp)
	sql = """SELECT
			d.id,
			IFNULL(d.id_parent,d.id) AS id_parent,
			d.dictionary,
			d.token,
			IFNULL(p.token, d.token) as parent,
			d.type,
			d.source,
			d.id_original,
			IFNULL(p.id_original, d.id_original) as id_original_parent
			FROM %s d
			LEFT JOIN %s p ON d.id_parent = p.id
			WHERE d.enabled = True""" % (tablename, tablename)
	dfD = pd.read_sql(sql, engineD, index_col='id')

	print "dfD head: \n" + str(dfD.head())

	dfDg = dfD.reset_index(drop=False).groupby('token').agg({
		'id':lambda x:tuple(x)})
	dfDg = dfDg.reset_index().set_index('id')

	print "dfDg head: \n" + str(dfDg.head())

	dict_token = dfD['token'].to_dict()
	dict_id_parent = dfD['id_parent'].to_dict()
	dict_parent = dfD['parent'].to_dict()
	dict_type = dfD['type'].to_dict()

	#Build Term Parser
	print '--- Building Term Parser ---'
	tdp = TermDictionaryParser()

	# Select columns to pass to parser
	list_tuples =  list(dfDg['token'].str.lower().items())

	#Build Parser Vocabulary
	tdp.build_vocabulary(list_tuples)

	engineE = db.connectToMySQL(server='mysql_epilepsy')

	print '--- Loading MySQL table dw_forums ---'
	forums = """SELECT f.pid, f.parentid, f.uid, f.type, f.topic, f.created, f.text_original
	            FROM dw_forums f;"""
	dfF = pd.read_sql(forums, engineE)

	gbF = dfF.groupby('uid')
	grouplistF = [gbF.get_group(grp) for grp in gbF.groups]

	n_users = len(grouplistF)
	current = 1
	for user in grouplistF:
		user_id = user.iloc[0]['uid']
		print '> Parsing user {0} ({1} of {2})'.format(user_id, current, n_users)
		current += 1
		user = user.set_index(pd.to_datetime(user['created'], unit='s'), drop=False) #Do we need parameter drop=False?
		user = user.sort_index(ascending=True)
		n_posts = user.shape[0]
		n_posts_with_matches = 0
		inserts = []
		for creat_time, post in user.iterrows():
			#date = created_time.strftime('%Y-%m-%d')
			post_id = post['pid']
			text = post['text_original']
			s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
			if s.has_match():
				n_posts_with_matches += 1
				mj = {
					'_id' : post_id,
					'user_id' : user_id,
					'created_time' : creat_time,
					'matches' : []}
				for match in s.get_unique_matches():
					for mid in match.id:
						mj['matches'].append({
							'id' : mid,
							'id_parent' : dict_id_parent[mid],
							'token' : dict_token[mid],
							'parent' : dict_parent[mid],
							'type' : dict_type[mid]})
				inserts.append(mj)
		print '\tNumber of posts: {0} | Number of matched posts: {1}'.format(n_posts, n_posts_with_matches)

		if n_posts_with_matches <= 0:
			print '> NO MATCHED POSTS, SKIPPING'
			continue
		uj = {
			'_id' : user_id,
			'posts' : n_posts,
			'matched_posts' : n_posts_with_matches}

		pickle.dump(uj, open("tagging_results_users/user_{0}.pkl".format(user_id), 'wb'))
		pickle.dump(inserts, open("tagging_results_users/matches_user_{0}.pkl".format(user_id), 'wb'))

	# for user in grouplistC:
	# 	user = user.sort_values(by=['created'])

if VIEW_USERS == 1:
	for (root, dirs, files) in os.walk('tagging_results_users', topdown=True):
		timelines = 0
		posts = 0
		comments = 0
		mentions = 0
		for f in files:
			if f[:7] == 'matches':
				timelines += 1
				matched_posts = pickle.load(open("tagging_results_users/" + f, 'rb'))
				for post in matched_posts:
					mentions += len(post['matches'])
					if 'cid' in post['_id']:
						comments += 1
					else:
						posts += 1

		engineE = db.connectToMySQL(server='mysql_epilepsy')

		print '--- Loading MySQL table dw_forums ---'
		forums = """SELECT f.pid, f.parentid, f.uid, f.type FROM dw_forums f;"""
		dfF = pd.read_sql(forums, engineE)
		gbF = dfF.groupby('uid')
		grouplistF = [gbF.get_group(grp) for grp in gbF.groups]
		tl = len(grouplistF)
		p = 0
		c = 0
		for ind, row in dfF.iterrows():
			if 'cid' in row['pid']:
				c += 1
			else:
				p += 1

		print "Timelines (with mentions): {0} ({1})".format(tl, timelines)
		print "Posts (with mentions): {0} ({1})".format(p, posts)
		print "Comments (with mentions): {0} ({1})".format(c, comments)
		print "Mentions: " + str(mentions)

############################### #################################################
#################              TOPIC TIMELINES              ####################
################################################################################
if TOPICS == 1:
	dicttimestamp = '20180706'
	print '--- Loading MySQL dictionary (%s)---' % dicttimestamp
	engineD = db.connectToMySQL(server='mysql_ddi_dictionaries')
	tablename = 'dict_%s' % (dicttimestamp)
	sql = """SELECT
			d.id,
			IFNULL(d.id_parent,d.id) AS id_parent,
			d.dictionary,
			d.token,
			IFNULL(p.token, d.token) as parent,
			d.type,
			d.source,
			d.id_original,
			IFNULL(p.id_original, d.id_original) as id_original_parent
			FROM %s d
			LEFT JOIN %s p ON d.id_parent = p.id
			WHERE d.enabled = True""" % (tablename, tablename)
	dfD = pd.read_sql(sql, engineD, index_col='id')

	dfDg = dfD.reset_index(drop=False).groupby('token').agg({
		'id':lambda x:tuple(x)})
	dfDg = dfDg.reset_index().set_index('id')

	dict_token = dfD['token'].to_dict()
	dict_id_parent = dfD['id_parent'].to_dict()
	dict_parent = dfD['parent'].to_dict()
	dict_type = dfD['type'].to_dict()

	#Build Term Parser
	print '--- Building Term Parser ---'
	tdp = TermDictionaryParser()

	# Select columns to pass to parser
	list_tuples =  list(dfDg['token'].str.lower().items())

	#Build Parser Vocabulary
	tdp.build_vocabulary(list_tuples)

	engineE = db.connectToMySQL(server='mysql_epilepsy')

	print '--- Loading MySQL table dw_forums ---'
	forums = """SELECT f.pid, f.parentid, f.uid, f.type, f.topicid, f.topic, f.created, f.text_original
	            FROM dw_forums f;"""
	dfF = pd.read_sql(forums, engineE)

	gbF = dfF.groupby('topic')
	grouplistF = [gbF.get_group(grp) for grp in gbF.groups]
	# gbC = dfC.groupby('uid')
	# grouplistC = [gbC.get_group(grp) for grp in gbC.groups]
	n_topics = len(grouplistF)
	current = 1
	for topic in grouplistF:
		topic_name = topic.iloc[0]['topic']
		topicid = topic.iloc[0]['topicid']
		print '> Parsing topic {0}, topic_id {1} ({2} of {3})'.format(topic_name, topicid, current, n_topics)
		current += 1
		topic = topic.set_index(pd.to_datetime(topic['created'], unit='s'), drop=False) #Do we need parameter drop=False?
		topic = topic.sort_index(ascending=True)
		n_posts = topic.shape[0]
		n_posts_with_matches = 0
		inserts = []
		for creat_time, post in topic.iterrows():
			#date = created_time.strftime('%Y-%m-%d')
			post_id = post['pid']
			text = post['text_original']
			s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
			if s.has_match():
				n_posts_with_matches += 1
				mj = {
					'_id' : post_id,
					'topic_name' : topic_name,
					'created_time' : creat_time,
					'matches' : []}
				for match in s.get_unique_matches():
					for mid in match.id:
						mj['matches'].append({
							'id' : mid,
							'id_parent' : dict_id_parent[mid],
							'token' : dict_token[mid],
							'parent' : dict_parent[mid],
							'type' : dict_type[mid]})
				inserts.append(mj)
		print '\t> Number of posts: {0} | Number of matched posts: {1}'.format(n_posts, n_posts_with_matches)

		if n_posts_with_matches <= 0:
			print '\t> NO MATCHED POSTS, SKIPPING'
			continue
		uj = {
			'_id' : topic_name,
			'posts' : n_posts,
			'matched_posts' : n_posts_with_matches}
		print '\t> SAVING MATCHES'
		pickle.dump(uj, open("tagging_results_topics/topic_{0}.pkl".format(topicid), 'wb'))
		pickle.dump(inserts, open("tagging_results_topics/matched_posts_{0}.pkl".format(topicid), 'wb'))
#Topic IDs
topics_dct = {'Fundraising and Awareness': 2003194, 'Products, Resources, Helpful Links': 2003130,
				'Women With Epilepsy': 2003119, 'Teens Speak Up!': 2010661, 'Insurance Issues': 2003133,
				'Medication Issues': 2003121, 'Insights & Strategies': 2003197,
				'Share Your #DareTo Go The Distance Story': 2036596, 'Living With Epilepsy - Adults': 2003117,
				'Men With Epilepsy': 2003129, 'Surgery and Devices': 2003122, 'Lennox Gastaut Syndrome': 2008441,
				'Veterans with seizures': 2003180, 'Family & Friends': 2003118, 'Corner Booth': 2003123,
				'Parents & Caregivers': 2003131, 'Epilepsy.com Help': 2003127, 'Athletes vs Epilepsy Goal Posts': 2044536,
				'Epilepsy and College': 2003304, 'New to Epilepsy.com': 2003125, 'Living With Epilepsy - Youth': 2003128,
				'Creative Corner': 2003134, 'Diagnostic Dilemmas and Testing': 2003126, 'Complementary Therapies': 2003124,
				'Teen Zone': 2003120, 'My Epilepsy Diary': 2003228, 'In Memoriam': 2014491, 'Advocate for Epilepsy': 2003132,
				'Infantile Spasms & Tuberous Sclerosis': 2008446}

if VIEW_TOPICS == 1:
	mp = {}
	for t in topics_dct:
		tdct = pickle.load(open('tagging_results_topics/{0}.pkl'.format(topics_dct[t]), 'rb'))
	# 	#mdct = pickle.load(open('tagging_results_topics/matched_posts_{0}.pkl'.format(topics_dct[t]), 'rb'))
	# 	print 'For topic -- ' + t + ':'
	# 	print udct
	# 	#print mdct
		mp[t] = (tdct['matched_posts'], tdct['posts'])
	print mp

################################################################################
################              THREAD TIMELINES              ####################
################################################################################

#In order to find a thread on the MySQL table, write comand:
#SELECT p.pid, p.parentid FROM dw_forums p WHERE p.pid LIKE "pid-816486%";

if THREADS == 1:
	dicttimestamp = '20180706'
	print '--- Loading MySQL dictionary (%s)---' % dicttimestamp
	engineD = db.connectToMySQL(server='mysql_ddi_dictionaries')
	tablename = 'dict_%s' % (dicttimestamp)
	sql = """SELECT
			d.id,
			IFNULL(d.id_parent,d.id) AS id_parent,
			d.dictionary,
			d.token,
			IFNULL(p.token, d.token) as parent,
			d.type,
			d.source,
			d.id_original,
			IFNULL(p.id_original, d.id_original) as id_original_parent
			FROM %s d
			LEFT JOIN %s p ON d.id_parent = p.id
			WHERE d.enabled = True""" % (tablename, tablename)
	dfD = pd.read_sql(sql, engineD, index_col='id')

	dfDg = dfD.reset_index(drop=False).groupby('token').agg({
		'id':lambda x:tuple(x)})
	dfDg = dfDg.reset_index().set_index('id')

	dict_token = dfD['token'].to_dict()
	dict_id_parent = dfD['id_parent'].to_dict()
	dict_parent = dfD['parent'].to_dict()
	dict_type = dfD['type'].to_dict()

	#Build Term Parser
	print '--- Building Term Parser ---'
	tdp = TermDictionaryParser()

	# Select columns to pass to parser
	list_tuples =  list(dfDg['token'].str.lower().items())

	#Build Parser Vocabulary
	tdp.build_vocabulary(list_tuples)

	engineE = db.connectToMySQL(server='mysql_epilepsy')

	print '--- Loading MySQL table dw_forums ---'
	forums = """SELECT f.pid, SUBSTRING_INDEX(f.pid, "|", 1) AS onlypid,
				f.parentid, f.uid, f.type, f.topicid, f.topic, f.created, f.text_original
	            FROM dw_forums f;"""
	dfF = pd.read_sql(forums, engineE)

	gbF = dfF.groupby('onlypid')
	threadlist = [gbF.get_group(grp) for grp in gbF.groups]

	n_threads = len(threadlist)
	current = 1
	for thread in threadlist:
		thread_name = thread.iloc[0]['onlypid']
		print '> Parsing thread {0} ({1} of {2})'.format(thread_name, current, n_threads)
		current += 1
		thread = thread.set_index(pd.to_datetime(thread['created'], unit='s'), drop=False) #Do we need parameter drop=False?
		thread = thread.sort_index(ascending=True)
		n_posts = thread.shape[0]
		n_posts_with_matches = 0
		inserts = []
		for creat_time, post in thread.iterrows():
			#date = created_time.strftime('%Y-%m-%d')
			post_id = post['pid']
			text = post['text_original']
			s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
			if s.has_match():
				n_posts_with_matches += 1
				mj = {
					'_id' : post_id,
					'topic_name' : thread_name,
					'created_time' : creat_time,
					'matches' : []}
				for match in s.get_unique_matches():
					for mid in match.id:
						mj['matches'].append({
							'id' : mid,
							'id_parent' : dict_id_parent[mid],
							'token' : dict_token[mid],
							'parent' : dict_parent[mid],
							'type' : dict_type[mid]})
				inserts.append(mj)
		print '\t> Number of posts: {0} | Number of matched posts: {1}'.format(n_posts, n_posts_with_matches)

		if n_posts_with_matches <= 0:
			print '\t> NO MATCHED POSTS, SKIPPING'
			continue
		uj = {
			'_id' : thread_name,
			'posts' : n_posts,
			'matched_posts' : n_posts_with_matches}
		print '\t> SAVING MATCHES'
		pickle.dump(uj, open("tagging_results_threads/thread_{0}.pkl".format(thread_name), 'wb'))
		pickle.dump(inserts, open("tagging_results_threads/matched_posts_{0}.pkl".format(thread_name), 'wb'))

################################################################################
#################              CHAT TIMELINES              #####################
################################################################################

if CHATS == 1:
	dicttimestamp = '20180706'
	print '--- Loading MySQL dictionary (%s)---' % dicttimestamp
	engineD = db.connectToMySQL(server='mysql_ddi_dictionaries')
	tablename = 'dict_%s' % (dicttimestamp)
	sql = """SELECT
			d.id,
			IFNULL(d.id_parent,d.id) AS id_parent,
			d.dictionary,
			d.token,
			IFNULL(p.token, d.token) as parent,
			d.type,
			d.source,
			d.id_original,
			IFNULL(p.id_original, d.id_original) as id_original_parent
			FROM %s d
			LEFT JOIN %s p ON d.id_parent = p.id
			WHERE d.enabled = True""" % (tablename, tablename)
	dfD = pd.read_sql(sql, engineD, index_col='id')
	dfDg = dfD.reset_index(drop=False).groupby('token').agg({
		'id':lambda x:tuple(x)})
	dfDg = dfDg.reset_index().set_index('id')
	dict_token = dfD['token'].to_dict()
	dict_id_parent = dfD['id_parent'].to_dict()
	dict_parent = dfD['parent'].to_dict()
	dict_type = dfD['type'].to_dict()

	print '--- Building Term Parser ---'
	tdp = TermDictionaryParser()
	# Select columns to pass to parser
	list_tuples =  list(dfDg['token'].str.lower().items())
	#Build Parser Vocabulary
	tdp.build_vocabulary(list_tuples)

	engineE = db.connectToMySQL(server='mysql_epilepsy')

	print '--- Loading MySQL table dw_chats ---'
	forums = """SELECT c.cid, c.uid, c.touid, c.type, c.chatroom, c.created, c.text_original
	            FROM dw_chats c;"""
	dfF = pd.read_sql(forums, engineE)
	gbF = dfF.groupby('uid')
	grouplistF = [gbF.get_group(grp) for grp in gbF.groups]

	chats = len(dfF)
	chats_m = 0
	n_users = len(grouplistF)
	users_m = 0
	mentions = 0
	current = 1
	for user in grouplistF:
		user_id = user.iloc[0]['uid']
		print '> Parsing user {0} ({1} of {2})'.format(user_id, current, n_users)
		current += 1
		user = user.set_index(pd.to_datetime(user['created'], unit='s'), drop=False) #Do we need parameter drop=False?
		user = user.sort_index(ascending=True)
		n_chats = user.shape[0]
		n_chats_with_matches = 0
		inserts = []
		for creat_time, chat in user.iterrows():
			#date = created_time.strftime('%Y-%m-%d')
			chat_id = chat['cid']
			text = chat['text_original']
			s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
			if s.has_match():
				n_chats_with_matches += 1
				mj = {
					'_id' : chat_id,
					'user_id' : user_id,
					'created_time' : creat_time,
					'matches' : []}
				for match in s.get_unique_matches():
					for mid in match.id:
						mj['matches'].append({
							'id' : mid,
							'id_parent' : dict_id_parent[mid],
							'token' : dict_token[mid],
							'parent' : dict_parent[mid],
							'type' : dict_type[mid]})
				mentions += len(mj['matches'])
				inserts.append(mj)
		print '\tNumber of posts: {0} | Number of matched posts: {1}'.format(n_chats, n_chats_with_matches)
		chats_m += n_chats_with_matches
		if n_chats_with_matches > 0:
			users_m += 1

		if n_chats_with_matches <= 0:
			print '> NO MATCHED POSTS, SKIPPING'
			continue
		uj = {
			'_id' : user_id,
			'posts' : n_chats,
			'matched_posts' : n_chats_with_matches}

		pickle.dump(uj, open("tagging_results_chats/user_{0}.pkl".format(user_id), 'wb'))
		pickle.dump(inserts, open("tagging_results_chats/matches_user_{0}.pkl".format(user_id), 'wb'))

	pickle.dump(inserts, open("tagging_results_chats/chats/matched_chats_list.pkl", 'wb'))

	print "Users: " + str(n_users)
	print "Chats (with mentions): {0} ({1})".format(n_chats, n_chats_with_matches)
	print "Mentions: " + str(mentions)
