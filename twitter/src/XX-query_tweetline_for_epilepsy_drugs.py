# coding=utf-8
# Author: Rion Brattig Correia
# Date: January 08, 2021
#
# Description: Match epilepsy drug mentions against TweetLine (Johan's tweet timelines). Exports all matched Tweets to .csv file.
#
#
import os
import sys
#
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
# include_path = '/nfs/nfs7/home/rionbr/myaura/include'
sys.path.insert(0, include_path)
#
import pandas as pd
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from datetime import datetime
from dateutil.relativedelta import relativedelta
#
import db_init as db
from termdictparser import TermDictionaryParser, Sentences


if __name__ == '__main__':

    #
    # Drugs of Epilepsy
    #
    data = [
        'clobazam', 'onfi',
        'levetiracetam', 'keppra', 'Levetiracetamum',
        'lamotrigine', 'lamictal', 'lamotrigina', 'lamotrigine', 'lamotriginum',
        'lacosamide', 'vimpat', 'SPM927', 'erlosamide', 'harkoseride',
        'carbamazepine', 'carbamazepen', 'carbamazepin', 'carbamazepina', 'carbamazepinum', 'carbamazépine',
        'diazepam', 'valium', 'diastat',
        'oxcarbazepine',
        'seizuremeds'
    ]

    dfD = pd.DataFrame({'token': data})

    # Build Term Parser
    tdp = TermDictionaryParser()
    list_tuples = list(dfD['token'].items())
    tdp.build_vocabulary(list_tuples)

    # Connect to DB
    cnxmongo, _ = db.connectToMongoDB(server='mongo_tweetline', db='tweetline')

    #
    # Query Mongo
    #
    print('--- Creating MongoDB cursor ---')
    cursor = cnxmongo.tweet.find()

    #
    # Iterating Cursor
    #
    print('--- Iterating (this will take a long while) ---')
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
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')

        user_id = r['user_id']

        s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
        if s.has_match():
            results.append((user_id, _id, r['datetime'], text))

        # Print a screen flush so we can check up on progress
        if (i % 100000 == 0):
            print '%0.2fM,' % (i / 10000000.),
            sys.stdout.flush()
        #
        i += 1

    print('--- Finished iteration ---')

    time_end = datetime.datetime.now()
    time_diff = relativedelta(time_end, time_start)
    print "Elapsed Time: %d year %d month %d days %d hours %d minutes %d seconds %d microseconds" % (time_diff.years, time_diff.months, time_diff.days, time_diff.hours, time_diff.minutes, time_diff.seconds, time_diff.microseconds)

    print '--- Create DataFrame with Results ---'
    dfR = pd.DataFrame(results, columns=['user_id', '_id', 'datetime', 'text'])

    print '- Export DataFrame'
    dfR.to_csv('../tmp-data/db-matches-epilepsy.csv.gz')
