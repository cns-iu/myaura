# coding=utf-8
# Author: Rion B Correia & Xuan Wang
# Date: Jan 06, 2021
#
# Description: Parse Epilepsy Foundation Forums and extract dictionary matches
#
import os
import sys
#
#include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
include_path = '/nfs/nfs7/home/rionbr/myaura/include'
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
    # Connect to MySQL
    #
    engine = db.connectToMySQL(server='etrash-mysql-epilepsy')

    #
    # Get Users
    #
    sql = """  
        SELECT
            pid,
            uid,
            topicid,
            created,
            title,
            text_clean
        FROM dw_forums
    """
    df = pd.read_sql(sql, con=engine)

    # Convert date
    df['created'] = pd.to_datetime(df['created'], unit='s')

    n_posts = df.shape[0]
    n_posts_with_matches = 0
    #
    # Parse Users
    #
    list_post_mentions = []
    #
    for idx, row in df.iterrows():
        #
        i = idx + 1
        if (i % 500 == 0):
            per = i / n_posts
            print("> Parsing Post: {i:d} of {n:d} ({per:.2%})".format(i=i, n=n_posts, per=per))

        created_time = row['created']
        id_user = row['uid']
        id_topic = row['topicid']
        id_post = row['pid']
        #
        text = row['title'] + ' ' + row['text_clean']

        # Parser
        s = Sentences(text).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
        if s.has_match():
            n_posts_with_matches += 1
            mj = {
                'id_post': id_post,
                'id_user': id_user,
                'id_topic': id_topic,
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

        #print('nr_posts: {n_posts:d} | nr_matched_posts: {n_posts_with_matches:d}'.format(n_posts=n_posts, n_posts_with_matches=n_posts_with_matches))

        if n_posts_with_matches <= 0:
            print('> NO MATCHED POSTS, SKIPPING')
            continue

    # to DataFrame
    dfR = pd.DataFrame(list_post_mentions)

    # Export
    wCSVfile = '../tmp-data/01-efwebsite-forums-mentions-{dicttimestamp:s}.csv.gz'.format(dicttimestamp=dicttimestamp)
    utils.ensurePathExists(wCSVfile)
    dfR.to_csv(wCSVfile)
