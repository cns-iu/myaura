# coding=utf-8
# Author: Rion B Correia
# Date: Nov 11, 2017
# 
# Description: 
# Build a Mongo Collection of Social Media Co-Mentions from user timelines (data from the MongoDB made with `parse_<social-media>_mentions.py`)
#
from __future__ import division
# Add package folder location
import sys
sys.path.insert(0, '../../include')
sys.path.insert(0, '../../../include')
# DB - Mysql
import db_init as db
# General
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 40)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)
import time
import pymongo
from joblib import Parallel, delayed


def compute_comentions(uid):

    uinserts = {}

    # Reconnect
    mongo_mention, _ = db.connectToMongoDB(server='mongo_ddi', db=db_mention)

    qp = mongo_mention[mention_timeline_col].aggregate([{"$match": {"user_id": uid}}, {"$unwind": "$matches"}, {"$sort": {"created_time": 1}}])
    dfP = pd.DataFrame.from_records(list(qp))
    dfP['uid'] = np.arange(dfP.shape[0])
    dfP = dfP.set_index('created_time')

    #
    # Looping Posts for Co-Mention Creation
    #
    j = 0
    number_of_posts = dfP.shape[0]
    #
    for idx_source, t_source in dfP.iterrows():

        j += 1
        id_post_source = t_source['_id']
        token_source = t_source['matches']  # [{u'token': u'wheezy', u'id': 65328}, {...}, {...}]
        id_token_source = token_source['id']
        id_parent_token_source = token_source['id_parent']

        # Calculate the window (x days)
        aheadtime = idx_source + pd.Timedelta('%sD' % (window_size))
        dft = dfP.loc[idx_source:aheadtime, :]

        if len(dft) >= 2:
            for idx_target, t_target in dft[1:].iterrows():

                id_post_target = t_target['_id']
                token_target = t_target['matches']
                id_token_target = token_target['id']
                id_parent_token_target = token_target['id_parent']

                # Skip self-loops
                if id_parent_token_source == id_parent_token_target:
                    continue

                # Key to only add after all user posts have been processed
                key = (id_token_source, id_token_target)
                if key not in uinserts:
                    comention = {
                        'source': token_source,
                        'target': token_target,
                        'count': 0,
                        'evidences': list(),
                        'user_id': uid,
                    }

                else:
                    comention = uinserts[key]

                # Removing for the Temporal MultiLayer Network
                # If the window is too big (there are too many evidences, limit their number)
                """
                if (create_record) and (len(comention['evidences']) < max_tokenpair_timeline_evidences):
                    timedelta = idx_target - idx_source
                    evidence = {
                        'source':id_post_source,
                        'target':id_post_target,
                        'created_time': idx_target,
                        'timediff': {
                            "days": timedelta.days,
                            "hours": int(timedelta.seconds/60/60)
                        }
                    }
                    comention['evidences'].append( evidence )
                """
                if (create_record):
                    comention['evidences'].append((id_post_source, id_post_target))

                # Increase Counter
                comention['count'] += 1
                uinserts[key] = comention

    if len(uinserts.values()):
        inserts_list = uinserts.values()
        inserts_size = len(inserts_list)
        chunk_size = 100
        
        if inserts_size > chunk_size:
            # print 'chunking insert'
            for i in range(0, inserts_size, chunk_size):
                # print 'chunk {:d}'.format(i)
                inserts_chunk = inserts_list[i: i + chunk_size]
                
                # Try-Retry function for Mongo
                for t in range(10):
                    try:
                        mongo_mention[comention_timeline_col].insert_many(inserts_chunk, ordered=False)
                        break
                    except pymongo.errors.AutoReconnect:
                        # print '-- Insert failed : sleeping for %s seconds --' % (pow(2,t))
                        time.sleep(pow(2, t))

        else:
            mongo_mention[comention_timeline_col].insert_many(inserts_list, ordered=False)


if __name__ == '__main__':
    #
    # Init
    #
    dicttimestamp = '20180706'

    # window_size = 7 # in days
    # cohort = 'opioids' # (depression, epilepsy or opioids)
    # socialmedia = 'twitter' # (instagram or twitter)
    window_size = input("window_size [(int)]:")
    cohort = input("cohort [depression,epilepsy,opioids]:")
    socialmedia = input("socialmedia [instagram,twitter,facebook]:")

    # Removing this for the Temporal MultiLayer Networks
    # max_tokenpair_timeline_evidences = 5 # The max number of evidences to store, per token-pair, per timeline.

    # Consistency
    if window_size.isdigit():
        window_size = int(window_size)
    else:
        raise TypeError("'window_size' must be an integer")
    if cohort not in ['depression', 'epilepsy', 'opioids']:
        raise TypeError("Cohort could not be found. Must be either 'depression','epilepsy' or 'opioids'.")
    if socialmedia not in ['instagram', 'twitter','facebook']:
        raise TypeError("Socialmedia could not be found. Must be either 'instagram' or 'twitter'.")


    if socialmedia == 'facebook' and cohort != 'epilepsy':
        raise TypeError("The 'facebook' social media only has an 'epilepsy' cohort.")

    if int(window_size) <= 7:
        create_record = True
    else:
        create_record = False

    print('--- Building (window) CoMentions: {socialmedia:s} | {cohort:s} | {window_size:d} ---'.format(socialmedia=socialmedia, cohort=cohort, window_size=window_size))

    #
    # Mongo
    #
    print('--- Loading Mongo Data ---')
    db_mention = 'ddi_cohort_{cohort:s}_mentions'.format(cohort=cohort)
    mention_user_col = '{socialmedia:s}_user_mention_{dicttimestamp:s}'.format(socialmedia=socialmedia, dicttimestamp=dicttimestamp)
    mention_timeline_col = '{socialmedia:s}_timeline_mention_{dicttimestamp:s}'.format(socialmedia=socialmedia, dicttimestamp=dicttimestamp)
    # comention_user_col = '{socialmedia:s}_user_comention_{dicttimestamp:s}'.format(socialmedia=socialmedia, dicttimestamp=dicttimestamp)
    comention_timeline_col = '{socialmedia:s}_timeline_comention_{dicttimestamp:s}_{window_size:d}d' % (socialmedia, dicttimestamp, window_size)
    mongo_mention, _ = db.connectToMongoDB(server='mongo_ddi', db=db_mention)

    qu = mongo_mention[mention_user_col].find({'matched_posts': {'$gt': 0}}, {'matched_posts': 1, 'posts': 1})
    dfU = pd.DataFrame.from_records(list(qu))
    n_users = dfU.shape[0]

    skiplist = [
        179987667,  # "username" : "tdruggist", "full_name" : "The Druggist ™"
        1340735618,  # "username" : "infowarsteam", "full_name" : ""
        1552873970,  # "username" : "daroo_ha", "full_name" : "�●  داروها ●�"
        1485154027,  # "paw.in.hand", "full_name" : "Linda A"
    ]
    dfU = dfU.loc[~dfU['_id'].isin(skiplist), :]

    # Parallel
    results = Parallel(n_jobs=12, prefer="threads", verbose=10)(
        delayed(compute_comentions)(uid) for uid in dfU['_id'].tolist())

    print('Done.')

    print('> creating indexes')
    mongo_mention[comention_timeline_col].create_index("source.id", background=True)
    mongo_mention[comention_timeline_col].create_index("target.id", background=True)
    mongo_mention[comention_timeline_col].create_index("source.id_parent", background=True)
    mongo_mention[comention_timeline_col].create_index("target.id_parent", background=True)

    print('Done.')
