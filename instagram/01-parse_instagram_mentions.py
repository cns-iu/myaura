# coding=utf-8
# Author: Rion B Correia
# Date: July 01, 2015
# 
# Description: 
# Build Mention Tables (for network construction) on Instagram Timelines
#
# Add package folder location
import sys
sys.path.insert(0, '../../include')
sys.path.insert(0, '../../../include')
#
import db_init_ddi_project as db

import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from pandas.io.json import json_normalize
from datetime import datetime
from termdictparser import Sentences, TermDictionaryParser
#
import utils



if __name__ == '__main__':

	#
	# Init
	#
	#
	#cohort = 'opioids'
	dicttimestamp = '20180706' # raw_input("dict timestamp [yyyymmdd]:") #'20171221' # datetime.today().strftime('%Y%m%d')
	cohort = raw_input("cohort:")
	
	if cohort not in ['depression','epilepsy','opioids']:
		raise TypeError("'Cohort' not found. Should be either 'depression','epilepsy' or 'opioids'.")
	
	#
	# Load Dictionary from MySQL
	#
	print '--- Loading MySQL dictionary (%s)---' % dicttimestamp
	engine = db.connectToMySQL(server='mysql_ddi_dictionaries')
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
	dfD = pd.read_sql(sql, engine, index_col='id')

	# Some tokens have multiple hits (Drug products with multiple compounds)
	dfDg = dfD.reset_index(drop=False).groupby('token').agg({
		'id':lambda x:tuple(x)
	})
	dfDg = dfDg.reset_index().set_index('id')

	dict_token = dfD['token'].to_dict()
	dict_id_parent = dfD['id_parent'].to_dict()
	dict_parent = dfD['parent'].to_dict()
	#dict_dictionary = dfD['dictionary'].to_dict()
	dict_type = dfD['type'].to_dict()
	#dict_source = dfD['source'].to_dict()

	# Build Term Parser
	print '--- Building Term Parser ---'
	tdp = TermDictionaryParser()
	
	# Select columns to pass to parser
	list_tuples = list(dfDg['token'].str.lower().items())

	# Build Parser Vocabulary
	tdp.build_vocabulary(list_tuples)

	#
	# Get Users from MongoDB
	#
	db_raw = 'ddi_cohort_%s' % (cohort)
	db_mention = 'ddi_cohort_%s_mentions' % (cohort)
	mention_user_col = 'instagram_user_mention_%s' % (dicttimestamp)
	mention_post_col = 'instagram_post_mention_%s' % (dicttimestamp)
	mongo_raw, _ = db.connectToMongoDB(server='mongo_ddi', db=db_raw)
	mongo_mention, _ = db.connectToMongoDB(server='mongo_ddi', db=db_mention)

	#
	# Get Users
	#
	d = mongo_raw['instagram_user'].find({},{'_id':True,'username':True,'full_name':True})
	dfU = json_normalize(list(d))
	dfU.columns = ['id','full_name','username']
	n_users = dfU.shape[0]

	for i, u in dfU.iterrows():
		print '> Parsing User: %s (id: %s) (%d of %d)' % (u['username'], u['id'], i+1, n_users)
		user_id = u['id']

		q = mongo_raw['instagram_post'].find(
			{
				'user_id': user_id
			},
			{
				'_id':True,
				'created_time':True,
				'tags':True,
				'caption.text':True,
			}
		)

		if (q.count() > 0):
			df = json_normalize(list(q))
		else:
			continue

		df.columns = ['id','caption','created_time','tags']
		df = df.set_index(pd.to_datetime(df['created_time'], unit='s'), drop=False)
		df = df.sort_index(ascending=True)
		df['caption'] = df['caption'].fillna('')

		n_posts = df.shape[0]
		n_posts_with_matches = 0
		
		inserts = []
		#
		# Find Mentions in Timeline
		#
		for created_time, p in df.iterrows():
			date = created_time.strftime('%Y-%m-%d')
			post_id = p['id']
			caption = utils.combineTagsAndText( p['caption'] , p['tags'] )
			caption = utils.removeRepostApp(caption)
			caption = utils.removeAtMention(caption)
			caption = utils.removeLinks(caption)
			caption = utils.removeHashtagSymbol(caption)

			# Parser
			s = Sentences(caption).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
			if s.has_match():
				n_posts_with_matches += 1
				mj = {
					'_id' : post_id,
					'user_id' : user_id,
					'created_time' : created_time,
					'matches' : []
				}
				for match in s.get_unique_matches():
					for mid in match.id:
						mj['matches'].append({
							'id' : mid,
							'id_parent' : dict_id_parent[mid],
							'token' : dict_token[mid],
							'parent' : dict_parent[mid],
							'type' : dict_type[mid]
						})
				inserts.append( mj )

		print 'nr_posts: %s | nr_matched_posts: %s' % (n_posts, n_posts_with_matches)

		if n_posts_with_matches <= 0:
			print '> NO MATCHED POSTS, SKIPPING'
			continue
			
		uj = {
			'_id' : user_id,
			'posts' : n_posts,
			'matched_posts' : n_posts_with_matches

		}
		try:
			mongo_mention[mention_user_col].insert_one(uj)
			mongo_mention[mention_post_col].insert_many(inserts, ordered=False)
		except ValueError as error:
			print "Error! Args: '{:s}'".format(error.args)

			

