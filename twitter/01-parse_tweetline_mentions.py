# coding=utf-8
# Author: Rion B Correia
# Date: July 01, 2015
# 
# Description: 
# Build Mention Mongo Collection (for network construction) on Tweetline Timelines
# Requires `results_twitter/db_matches-<cohort>.csv`
#
# Add package folder location
import sys
sys.path.insert(0, '../../include')
sys.path.insert(0, '../../../include')
#
import db_init_ddi_project as db
import re

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

# Mongo Command to remove everything before Twitter existed:
# db.twitter_post_mention_20180706.remove({'created_time':{$lte:new ISODate("2006-03-21T00:00:00Z")}})

if __name__ == '__main__':
	
	#
	# Init
	#
	dicttimestamp = '20180706' # raw_input("dict timestamp [yyyymmdd]:") # datetime.today().strftime('%Y%m%d')
	cohort = raw_input("cohort:")

	if cohort not in ['depression','epilepsy','opioids','heartburn']:
		raise TypeError("'Cohort' not found. Should be either 'depression','epilepsy' or 'opioids'.")
	
	if cohort == 'depression':
		# Drugs of Depression
		data = set([u'sertraline',u'sertralina',
				 u'fluoxetine',u'fluoxetin',u'fluoxetina',u'fluoxetinum',u'fluoxétine',u'prozac',
				 u'citalopram',u'citadur',u'nitalapram',
				 u'escitalopram',u'escitalopramum',u'esertia',
				 u'paroxetine',u'paroxetina',u'paroxetinum',
				 u'fluvoxamine',u'fluvoxamina',u'fluvoxaminum',
				 u'trazodone',u'trazodona',u'trazodonum'])
	
	elif cohort == 'epilepsy':
		# Drugs of Epilepsy
		data = set([u'clobazam', u'onfi',
				u'levetiracetam',u'keppra',u'Levetiracetamum',
				u'lamotrigine',u'lamictal',u'lamotrigina',u'lamotrigine',u'lamotriginum',
				u'lacosamide',u'vimpat',u'SPM927',u'erlosamide',u'harkoseride',
				u'carbamazepine',u'carbamazepen',u'carbamazepin',u'carbamazepina',u'carbamazepinum',u'carbamazépine',
				u'diazepam',u'valium',u'diastat',
				u'oxcarbazepine',
				u'seizuremeds',
				])

	elif cohort == 'opioids':
		# Drugs of opioids ;)
		data = set([u'fentanyl', u'oxycodone'])

	elif cohort == 'heartburn':
		# Drugs of heartburn ;)
		data = set([
				# Proton-pump inhibitors
				u'omeprazole',u'omeprazol',u'omeprazolum',u'losec','prilosec',u'acid reducer',u'heartburn control',u'omesec',u'yosprala',u'zegerid',
				u'lansoprazole',u'prevacid',u'bamalite',u'lasonprazol',u'lansoprazolum',u'lanzol',u'lanzopral',u'lanzul',u'limpidex',u'monolitum',u'ogastro',u'opiren',
				u'rabeprazole',u'clofezone',u'aciphex',
				u'pantoprazole',u'protonix',u'pantoprazol',u'pantoprazolum',
				u'esomeprazole',u'ésoméprazole',u'esomeprazol',u'esomeprazolum',u'perprazole',u'nexium',
				# H2-blockers
				u'nizatidine',u'nizatidina',u'nizatidinum',u'axid',
				u'famotidine',u'famotidina',u'famotidinum',u'pepcid',
				u'cimetidine',u'cimetag',u'cimetidin',u'cimetidina',u'cimétidine',u'cimetidinum',u'peptol',u'tagamet',
				u'ranitidine',u'ranitidina',u'ranitidinum',u'zantac',
				# Peptol-bismol
				u'bismuth subsalicylate',u'bismuth oxysalicylate',u'pink bismuth',u'wismutsubsalicylat',u'bismatrol',
				u'pepto bismol',u'pepto-bismol',u'bismatrol',u'bismol',u'bismuth',u'bismutina',u'estomax',u'peptic relief',u'stomach relief'
			])
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
	# Load Selected Timelines
	#
	dfPosts = pd.read_csv('results_twitter/db_matches-%s.csv' % (cohort), sep=',', header=0, index_col=0, encoding='utf-8')

	# Remove everything after a ReTweet
	dfPosts['text'] = dfPosts['text'].str.replace(r'rt @[a-z0-9_]+.+', '', flags=re.IGNORECASE)
	
	re_tokenizer = re.compile(r"[\w']+", re.UNICODE)
	re_retweet = re.compile(r"rt @[a-z0-9_]+.+", re.IGNORECASE|re.UNICODE)
	def contains_match(x):
		tokens = set( re_tokenizer.findall(x) )
		return any(tokens.intersection(data))

	# Remove everything after a ReTweet
	dfPosts['text'] = dfPosts['text'].str.replace(re_retweet, '')
	# Post contains drug match
	dfPosts['contains'] = dfPosts['text'].apply(contains_match)
	# Keep only posts with mentions
	dfPosts = dfPosts.loc[ (dfPosts['contains']==True) , : ]

	#### TODO
	dfUsers = dfPosts.groupby('user_id').agg({'_id':'count'}).rename(columns={'_id':'n_matched_posts'}).reset_index()

	#
	# Get Users from MongoDB
	#
	db_raw = 'tweetline'
	db_mention = 'ddi_cohort_%s_mentions' % (cohort)
	mention_user_col = 'twitter_user_mention_%s' % (dicttimestamp)
	mention_post_col = 'twitter_post_mention_%s' % (dicttimestamp)
	mongo_raw, _ = db.connectToMongoDB(server='mongo_tweetline', db=db_raw)
	mongo_mention, _ = db.connectToMongoDB(server='mongo_ddi', db=db_mention)

	#
	#
	#
	results = []
	#
	# Get User Timelines
	#
	print '--- Requesting Mongo Data: `tweetline` ---'

	n_users = dfUsers.shape[0]
	for i, u in dfUsers.iterrows():
		user_id = u['user_id']
		print '> Parsing User: %s (%d of %d)' % (user_id, i+1, n_users)
		#print 'Querying User: (id: `%d`) (%d of %d)' % (user_id, i, n_users)

		dfA = pd.DataFrame()

		d = mongo_raw.tweet.find(
			{
				'user_id': user_id
			},
			{
				'_id':True,
				'datetime':True,
				'user_id':True,
				'text':True,
			}
		)

		df = pd.DataFrame.from_records(d)

		df = df[['_id','datetime','user_id','text']]
		df.columns = ['id','created_time','user_id','text']
		df['created_time'] = pd.to_datetime(df['created_time'], format='%Y-%m-%d %H:%M:%S')
		df = df.set_index('id', drop=True)
		df['user_id'] = df['user_id'].astype(np.int64)
		df['text'] = df['text'].fillna('')
		#
		n_posts = df.shape[0]

		# Remove everything from before Twitter existed, to be sure.
		df = df.loc[ df['created_time']>'2006-03-21', : ]

		# Remove everything after a ReTweet mention
		df['text'] = df['text'].str.replace(re_retweet, '')
		
		n_posts = df.shape[0]
		n_posts_with_matches = 0

		inserts = []
		#
		# Find Mentions in Timeline
		#
		for tweet_id, row in df.iterrows():
			created_time = row['created_time']
			user_id = row['user_id']
			text = row['text']

			#
			# Drug
			#
			s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
			if s.has_match():
				n_posts_with_matches += 1

				mj = {
					'_id' : tweet_id,
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
		except:
			pass

			



