# coding=utf-8
# Author: Rion B Correia
# Date: July 01, 2015
# 
# Description: 
# Build Mention Tables (for network construction) on Instagram Timelines
#
import sys, os
from itertools import combinations
from collections import Counter
import pickle

import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from pandas import json_normalize

# Add package folder location
py_include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'py_include'))
sys.path.insert(0, py_include_path)

from termdictparser import Sentences, TermDictionaryParser
import db_init as db
from load_dictionary import load_dictionary
import utils
#



def get_users(mongo_raw):
    #
    # Get Users
    #
    d = mongo_raw['instagram_user'].find({}, {'_id': True, 'username': True, 'full_name': True})
    dfU = json_normalize(list(d))
    # bad idea, json_normalize doesn't guarantee column order
    # dfU.columns = ['id','full_name','username']
    dfU = dfU.rename(columns={'_id': 'id'})
    n_users = dfU.shape[0]
    return dfU, n_users

def get_mention(i, u, mongo_raw):
    print('> Parsing User: %s (id: %s) (%d of %d)' % (u['username'], u['id'], i + 1, n_users))
    user_id = u['id']

    q = mongo_raw['instagram_post'].find(
        {
            'user_id': user_id
        },
        {
            '_id': True,
            'created_time': True,
            'tags': True,
            'caption.text': True,
        }
    )

    if (q.count() > 0):
        df = json_normalize(list(q))
    else:
        return []

    # df.columns = ['id', 'caption', 'created_time', 'tags']
    df = df.rename(columns={'caption.text': 'caption', '_id': 'id'})
    df = df.set_index(pd.to_datetime(df['created_time'], unit='s'), drop=False)
    df = df.sort_index(ascending=True)
    df['caption'] = df['caption'].fillna('')

    n_posts = df.shape[0]
    n_posts_with_matches = 0

    list_post_mentions = []
    #
    # Find Mentions in Timeline
    #
    for created_time, p in df.iterrows():
        date = created_time.strftime('%Y-%m-%d')
        post_id = p['id']
        caption = utils.combineTagsAndText(p['caption'], p['tags'])
        caption = utils.removeRepostApp(caption)
        caption = utils.removeAtMention(caption)
        caption = utils.removeLinks(caption)
        caption = utils.removeHashtagSymbol(caption)

        # Parser
        s = Sentences(caption).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
        if s.has_match():
            n_posts_with_matches += 1
            mj = {
                '_id': post_id,
                'user_id': user_id,
                'created_time': created_time,
                'matches': []
            }
            for match in s.get_unique_matches():
                for mid in match.id:
                    mj['matches'].append({
                        'id': mid,
                        'id_parent': dict_id_parent[mid],
                        'token': dict_token[mid],
                        'parent': dict_parent[mid],
                        'type': dict_type[mid]
                    })
            list_post_mentions.append(mj)

    print('nr_posts: %s | nr_matched_posts: %s' % (n_posts, n_posts_with_matches))

    if n_posts_with_matches <= 0:
        print('> NO MATCHED POSTS, SKIPPING')
        return []

    return list_post_mentions

def get_comentions(l_mentions):
    l_comention = []
    for entry in l_mentions:
        for source, target in combinations(entry['matches'], 2):
            # Skip self-loops
            if source['id_parent'] == target['id_parent']:
                continue

            # didn't use id_parent yet
            comention = frozenset((source['id'], target['id']))
            l_comention.append(comention)
    return l_comention



if __name__ == '__main__':

    #
    # Init
    #
    #
    # cohort = 'opioids'
    dicttimestamp = '20180706'  # raw_input("dict timestamp [yyyymmdd]:") #'20171221' # datetime.today().strftime('%Y%m%d')
    cohort = 'epilepsy'
    # cohort = input("cohort:")
    #
    # if cohort not in ['depression','epilepsy','opioids']:
    # 	raise TypeError("'Cohort' not found. Should be either 'depression','epilepsy' or 'opioids'.")

    tdp, dfD = load_dictionary(dicttimestamp)

    dict_token = dfD['token'].to_dict()
    dict_id_parent = dfD['id_parent'].to_dict()
    dict_parent = dfD['parent'].to_dict()
    # dict_dictionary = dfD['dictionary'].to_dict()
    dict_type = dfD['type'].to_dict()
    # dict_source = dfD['source'].to_dict()

    comention_counter = Counter()

    #
    # Get Users from MongoDB
    #
    db_raw = 'ddi_cohort_%s' % (cohort)
    mongo_raw, _ = db.connectToMongoDB(server='mongo_ddi', db=db_raw)

    dfUser, n_users = get_users(mongo_raw)

    for i, u in dfUser.iterrows():
        l_mentions = get_mention(i, u, mongo_raw)
        comentions = get_comentions(l_mentions)
        comention_counter.update(comentions)

    with open('simple_comention.pkl','wb') as pklf:
        pickle.dump(comention_counter,pklf)