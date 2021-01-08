# coding=utf-8
# Author: Rion B Correia & Xuan Wang
# Date: Jan 06, 2021
#
# Description: Parse Instagram timelines and extract dictionary matches
#
import os
import sys
#
# include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
include_path = '/nfs/nfs7/home/rionbr/myaura/include'
sys.path.insert(0, include_path)
#
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import re
#
import db_init as db
import utils
from load_dictionary import load_dictionary, build_term_parser
from termdictparser import Sentences


if __name__ == '__main__':

    #
    # Init
    #
    dicttimestamp = '20180706'

    data = set([
        'clobazam', 'onfi',
        'levetiracetam', 'keppra', 'Levetiracetamum',
        'lamotrigine', 'lamictal', 'lamotrigina', 'lamotrigine', 'lamotriginum',
        'lacosamide', 'vimpat', 'SPM927', 'erlosamide', 'harkoseride',
        'carbamazepine', 'carbamazepen', 'carbamazepin', 'carbamazepina', 'carbamazepinum', 'carbamazépine',
        'diazepam', 'valium', 'diastat',
        'oxcarbazepine',
        'seizuremeds',
    ])

    # Load Dictionary
    dfD = load_dictionary(dicttimestamp=dicttimestamp, server='mysql-ddi-dictionaries')
    # Build Parser Vocabulary
    tdp = build_term_parser(dfD)

    #
    dict_token = dfD['token'].to_dict()
    dict_id_parent = dfD['id_parent'].to_dict()
    dict_parent = dfD['parent'].to_dict()
    # dict_dictionary = dfD['dictionary'].to_dict()
    dict_type = dfD['type'].to_dict()
    # dict_source = dfD['source'].to_dict()

    #
    # Get Users from MongoDB
    #
    db_raw = 'ddi_cohort_epilepsy'
    mongo_raw, _ = db.connectToMongoDB(server='mongo-tweetline', db=db_raw)

    #
    # Load Selected Timelines
    #
    dfP = pd.read_csv('../tmp-data/db-matches-epilepsy.csv', header=0, index_col=0)

    # Remove everything after a ReTweet
    dfP['text'] = dfP['text'].str.replace(r'rt @[a-z0-9_]+.+', '', flags=re.IGNORECASE)

    # Remove everything after a ReTweet
    re_retweet = re.compile(r"rt @[a-z0-9_]+.+", re.IGNORECASE|re.UNICODE)
    dfP['text'] = dfP['text'].str.replace(re_retweet, '')

    re_tokenizer = re.compile(r"[\w']+", re.UNICODE)

    def contains_match(x):
        tokens = set(re_tokenizer.findall(x))
        return any(tokens.intersection(data))

    # Post contains drug match
    dfP['contains'] = dfP['text'].apply(contains_match)

    # Keep only posts with mentions
    dfP = dfP.loc[(dfP['contains'] == True), :]
    #
    dfU = dfP.groupby('user_id').agg({'_id': 'count'}).rename(columns={'_id': 'n-matched-posts'}).reset_index()

    #
    # Get Users Timelines
    #
    print('--- Requesting Mongo Data: `tweetline` ---')
    mongo_raw, _ = db.connectToMongoDB(server='mongo-tweetline', db='tweetline')
    #
    n_users = dfU.shape[0]
    #
    # Parse Users
    #
    list_post_mentions = []
    #
    for idx, row in dfU.iterrows():
        #
        i = idx + 1
        per = i / n_users
        id_user = int(row['user_id'])
        print("> Parsing User '{id_user:d}': {i:d} of {n:d} ({per:.2%})".format(id_user=id_user, i=i, n=n_users, per=per))

        q = mongo_raw.tweet.find(
            {
                'user_id': id_user
            },
            {
                '_id': True,
                'datetime': True,
                'user_id': True,
                'text': True,
            }
        )

        df = pd.json_normalize(list(q))

        df = df[['_id', 'datetime', 'user_id', 'text']]
        df.columns = ['id', 'created_time', 'user_id', 'text']
        df['created_time'] = pd.to_datetime(df['created_time'], format='%Y-%m-%d %H:%M:%S')
        df = df.set_index('id', drop=True)
        df['user_id'] = df['user_id'].astype(np.int64)
        df['text'] = df['text'].fillna('')

        # Remove everything from before Twitter existed, to be sure.
        df = df.loc[(df['created_time'] > '2006-03-21'), :]

        # Remove everything after a ReTweet mention
        df['text'] = df['text'].str.replace(re_retweet, '')

        n_posts = df.shape[0]
        n_posts_with_matches = 0

        #
        # Parse Mentions in Timeline
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
                    'id_post': tweet_id,
                    'id_user': id_user,
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

        print('nr_posts: {n_posts:d} | nr_matched_posts: {n_posts_with_matches:d}'.format(n_posts=n_posts, n_posts_with_matches=n_posts_with_matches))

        if n_posts_with_matches == 0:
            print('> NO MATCHED POSTS, SKIPPING')
            continue

    # to DataFrame
    dfR = pd.DataFrame(list_post_mentions)

    # Export
    wCSVfile = '../tmp-data/01-twitter-epilepsy-mentions-{dicttimestamp:s}.csv.gz'.format(dicttimestamp=dicttimestamp)
    utils.ensurePathExists(wCSVfile)
    dfR.to_csv(wCSVfile)
