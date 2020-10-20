# coding=utf-8
# Author: Rion Brattig Correia
# Date: January 12, 2015
#
# Description: Match dictionaries against TweetLine (Johan's tweet timelines). Exports all matched Tweets to .csv file.
#
#
import sys
sys.path.insert(0, '../../include')
sys.path.insert(0, '../../../include')
#
import db_init as db
import pandas as pd
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from datetime import datetime
from dateutil.relativedelta import relativedelta
from termdictparser import Sentences, TermDictionaryParser

if __name__ == '__main__':
	
	BASE_RESU_DIR = 'results_twitter/'
	cohort = raw_input("cohort:")
	file_tweets = BASE_RESU_DIR + 'db_matches-%s.csv' % (cohort)
	#
	# Dictionary
	#

	if cohort == 'depression':
		# Drugs of Depression
		data = [u'sertraline',u'sertralina',
				 u'fluoxetine',u'fluoxetin',u'fluoxetina',u'fluoxetinum',u'fluoxétine',u'prozac',
				 u'citalopram',u'citadur',u'nitalapram',
				 u'escitalopram',u'escitalopramum',u'esertia',
				 u'paroxetine',u'paroxetina',u'paroxetinum',
				 u'fluvoxamine',u'fluvoxamina',u'fluvoxaminum',
				 u'trazodone',u'trazodona',u'trazodonum']
	
	elif cohort == 'epilepsy':
		# Drugs of Epilepsy
		data = [u'clobazam', u'onfi',
				u'levetiracetam',u'keppra',u'Levetiracetamum',
				u'lamotrigine',u'lamictal',u'lamotrigina',u'lamotrigine',u'lamotriginum',
				u'lacosamide',u'vimpat',u'SPM927',u'erlosamide',u'harkoseride',
				u'carbamazepine',u'carbamazepen',u'carbamazepin',u'carbamazepina',u'carbamazepinum',u'carbamazépine',
				u'diazepam',u'valium',u'diastat',
				u'oxcarbazepine',
				u'seizuremeds',
				]

	elif cohort == 'opioids':
		# Drugs of opioids ;)
		data = [u'fentanyl', u'oxycodone']
	
	elif cohort == 'heartburn':
		# Drugs of heartburn
		data = [
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
			]

	dfD = pd.DataFrame(
		{'token': data })

	# Build Term Parser
	tdp = TermDictionaryParser()
	list_tuples = list(dfD['token'].items())
	tdp.build_vocabulary(list_tuples)


	# Connect to DB
	cnxmongo, cnxmongoclient = db.connectToMongoDB(server='mongo_tweetline', db='tweetline')

	#
	# Query Mongo
	#
	print '- Creating MongoDB cursor'
	cursor = cnxmongo.tweet.find()

	#
	# Iterating Cursor
	#
	print '- Iterating (this might take a while):'
	results = []
	i = 0
	time_start = datetime.now()
	
	# Twitter Launch Date
	mindatetime = datetime.strptime('2006-07-15 00:00:00', "%Y-%m-%d %H:%M:%S")
	# Loop All DataBase
	for r in cursor:
		
		# Assignment
		_id = r['_id']
		datetime = datetime.strptime(r['datetime'], "%Y-%m-%d %H:%M:%S")
		if datetime < mindatetime:
			continue
		text = r['text']
		# Remove breakline
		text = text.replace('\n',' ')
		text = text.replace('\r',' ')

		user_id = r['user_id']

		s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
		if s.has_match():
			results.append( (user_id, _id, r['datetime'], text) )

		# Print a screen flush so we can check up on progress
		if (i%100000 == 0):
			print '%0.2fM,' % (i/10000000.),
			sys.stdout.flush()
		
		i += 1

	print '--- Finished iteration ---'

	time_end = datetime.datetime.now()
	time_diff = relativedelta(time_end, time_start)
	print "Elapsed Time: %d year %d month %d days %d hours %d minutes %d seconds %d microseconds" % (time_diff.years, time_diff.months, time_diff.days, time_diff.hours, time_diff.minutes, time_diff.seconds, time_diff.microseconds)

	print '--- Create DataFrame with Results ---'
	dfR = pd.DataFrame(results, columns=['user_id','_id','datetime','text'])

	print '- Export DataFrame'
	dfR.to_csv(file_tweets, encoding='utf-8')


