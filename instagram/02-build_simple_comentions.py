# coding=utf-8
# Author: Rion B Correia
# Date: Nov 11, 2017
#
# Description:
# Build a Mongo Collection on Social Media Co-Mentions on the same post (using data from the MongoDB made with `parse_<social-media>_mentions.py`)
#
# Add package folder location
import sys
sys.path.insert(0, '../../include')
sys.path.insert(0, '../../../include')
# DB - Mysql
import db_init as db
# General
# import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 40)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)
# import time
# import pymongo
from joblib import Parallel, delayed
from itertools import combinations


def compute_comentions(obj, datatype):

    inserts = []
    user_id = obj['user_id']

    # Combition of all matches in a comment
    comb = list(combinations(obj['matches'], 2))
    if len(comb):

        for source, target in comb:

            # Skip self-loops
            if source['id_parent'] == target['id_parent']:
                continue

            # Smaller id first (no direction)
            if source['id'] > target['id']:
                source, target = target, source

            comention = {
                'source': source,
                'target': target,
                'user_id': user_id,
            }
            if datatype == 'post':
                comention['post_id'] = obj['_id']
            if datatype == 'comment':
                comention['post_id'] = obj['post_id']
                comention['comment_id'] = obj['comment_id']

            inserts.append(comention)

        if len(inserts):
            mongo_mention[col_comention].insert_many(inserts, ordered=False)


if __name__ == '__main__':
    #
    # Init
    #
    dicttimestamp = '20180706'

    cohort = 'epilepsy'
    socialmedia = 'twitter'
    datatype = 'post'  # ['post','comment']
    # cohort = input("cohort [epilepsy]:")
    # socialmedia = input("socialmedia [facebook]:")

    # Consistency
    if cohort not in ['epilepsy']:
        raise TypeError("Cohort could not be found. Must be 'epilepsy'.")
    if socialmedia not in ['facebook', 'instagram', 'twitter']:
        raise TypeError("Socialmedia could not be found. Must be 'facebook', 'instagram', or 'twitter'.")
    if datatype not in ['comment', 'post']:
        raise TypeError("DataType could not be found. Must be 'comment' or 'post'.")

    if socialmedia == 'facebook' and cohort != 'comment':
        raise TypeError("Socialmedia 'facebook' must be of type 'comment'.")

    print('--- Building (same post) CoMentions: {socialmedia:s} | {cohort:s} | {datatype:s} ---'.format(socialmedia=socialmedia, cohort=cohort, datatype=datatype))

    #
    # Mongo
    #
    print('--- Loading Mongo Data ---')
    db_mention = 'ddi_cohort_{cohort:s}_mentions'.format(cohort=cohort)
    col_mention = '{socialmedia:s}_{datatype:s}_mention_{dicttimestamp:s}'.format(socialmedia=socialmedia, datatype=datatype, dicttimestamp=dicttimestamp)
    col_comention = '{socialmedia:s}_{datatype:s}_comention_{dicttimestamp:s}'.format(socialmedia=socialmedia, datatype=datatype, dicttimestamp=dicttimestamp)
    mongo_mention, _ = db.connectToMongoDB(server='mongo_ddi', db=db_mention)

    query = mongo_mention[col_mention].find()

    # Parallel
    results = Parallel(n_jobs=6, prefer="threads", verbose=10)(
        delayed(compute_comentions)(obj, datatype) for obj in query)

    print('Done.')

    print('> creating indexes')
    mongo_mention[col_comention].create_index("source.id", background=True)
    mongo_mention[col_comention].create_index("target.id", background=True)
    mongo_mention[col_comention].create_index("source.id_parent", background=True)
    mongo_mention[col_comention].create_index("target.id_parent", background=True)
    print('Done.')
