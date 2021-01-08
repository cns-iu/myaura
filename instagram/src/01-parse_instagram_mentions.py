# coding=utf-8
# Author: Rion B Correia & Xuan Wang
# Date: Jan 06, 2021
#
# Description: Parse Instagram timelines and extract dictionary matches
#
import os
import sys
#
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
# include_path = '/nfs/nfs7/home/rionbr/myaura/include'
sys.path.insert(0, include_path)
#
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
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

    # Load Dictionary
    dfD = load_dictionary(dicttimestamp=dicttimestamp, server='etrash-mysql-ddi-dictionaries')
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
    mongo_raw, _ = db.connectToMongoDB(server='mongo-ddi', db=db_raw)

    #
    # Get Users
    #
    d = mongo_raw['instagram_user'].find({}, {'_id': True, 'username': True})
    dfU = pd.json_normalize(list(d))
    dfU = dfU.rename(columns={'_id': 'id'})
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
        id_user = row['id']
        print("> Parsing User '{id_user:d}': {i:d} of {n:d} ({per:.2%})".format(id_user=id_user, i=i, n=n_users, per=per))

        q = mongo_raw['instagram_post'].find(
            {
                'user_id': id_user
            },
            {
                '_id': True,
                'created_time': True,
                'tags': True,
                'caption.text': True,
            }
        )

        df = pd.json_normalize(list(q))
        #
        df = df.rename(columns={'caption.text': 'caption', '_id': 'id'})
        df = df.set_index(pd.to_datetime(df['created_time'], unit='s'), drop=False)
        df = df.sort_index(ascending=True)
        df['caption'] = df['caption'].fillna('')

        n_posts = df.shape[0]
        n_posts_with_matches = 0

        #
        # Parse Mentions in Timeline
        #
        for created_time, p in df.iterrows():
            date = created_time.strftime('%Y-%m-%d')
            id_post = p['id']
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
                    'id_post': id_post,
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

        if n_posts_with_matches <= 0:
            print('> NO MATCHED POSTS, SKIPPING')
            continue

    # to DataFrame
    dfR = pd.DataFrame(list_post_mentions)

    # Export
    wCSVfile = '../tmp-data/01-instagram-epilepsy-mentions-{dicttimestamp:s}.csv.gz'.format(dicttimestamp=dicttimestamp)
    utils.ensurePathExists(wCSVfile)
    dfR.to_csv(wCSVfile)
