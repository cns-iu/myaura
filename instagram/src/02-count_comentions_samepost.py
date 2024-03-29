# coding=utf-8
# Author: Rion B Correia & Wuan Wang
# Date: Jan 07, 2021
#
# Description: Loads the Mention file and builds Co-Mentions over the same post
#
import os
import sys
#
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
#include_path = '/nfs/nfs7/home/rionbr/myaura/include'
sys.path.insert(0, include_path)
#
from ast import literal_eval
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from joblib import Parallel, delayed
from itertools import combinations
from collections import Counter, namedtuple
import utils


def compute_comentions(row):

    list_post_comentions = []
    id_user = row['id_user']

    # Combition of all matches in a post
    comb = list(combinations(row['matches'], 2))
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
                'id_user': id_user,
            }
            comention['id_post'] = row['id_post']

            list_post_comentions.append(comention)

    return list_post_comentions


if __name__ == '__main__':
    #
    # Init
    #
    dicttimestamp = '20180706'
    # dicttimestamp = '20210321'

    print('--- Building (same post) CoMentions ---')

    print('--- Loading Mention Data ---')

    rCSVfile = '../tmp-data/01-instagram-epilepsy-mentions-{dicttimestamp:s}.csv.gz'.format(dicttimestamp=dicttimestamp)
    df = pd.read_csv(rCSVfile, index_col=0, converters={'matches': literal_eval})

    print('--- CoMention count ---')

    i = 0
    n = len(df)
    # The co-mention counter 
    counter = Counter()
    # The mention counter
    mention_count = Counter()
    # A hashable object to use in the frozenset counter
    #match = namedtuple('Match', ['id_match', 'id_parent', 'token', 'parent', 'type'])
    matchparent = namedtuple('Match', ['id_parent', 'parent', 'type'])
    #
    for idx, row in df.iterrows():
        if i % 10000 == 0:
            print('> Computing comentions. Row {i:,d} of {n:,d} ({per:.2%})'.format(i=i, n=n, per=(i / n)))
        #
        matches = row['matches']
        list_user_comentions = []
        unique_id_parent = set([m['id_parent'] for m in row['matches']])
        mention_count.update(unique_id_parent)

        unique_parent_rich = [matchparent(m['id_parent'], m['parent'], m['type']) for m in row['matches']]
        unique_parent_rich = list(set(unique_parent_rich))
        for source, target in combinations(unique_parent_rich, 2):

            # Skip self-loops
            # if source['id_parent'] == target['id_parent']:
            #     continue
            # if source.id_parent == target.id_parent:
            #     continue

            #msource = match(source['id'], source['id_parent'], source['token'], source['parent'], source['type'])
            #mtarget = match(target['id'], target['id_parent'], target['token'], target['parent'], target['type'])
            # msource = matchparent(source['id_parent'], source['parent'], source['type'])
            # mtarget = matchparent(target['id_parent'], target['parent'], target['type'])

            # didn't use id_parent yet
            comention = frozenset((source, target))
            list_user_comentions.append(comention)
        #
        counter.update(list_user_comentions)
        #
        i += 1

    print('Done.')

    print('--- Convert to DataFrame and Export ---')
    # Convert counter to Pandas DataFrame
    records = [(s.id_parent, s.parent, s.type, t.id_parent, t.parent, t.type, c) for (s, t), c in counter.items()]
    columns = pd.MultiIndex.from_tuples([(level, field) for level in ['source', 'target'] for field in ['id_parent', 'parent', 'type']] + [('comention', 'count')])
    dfR = pd.DataFrame(records, columns=columns)

    mention_count_df = pd.DataFrame(mention_count.items(), columns=('id_parent', 'mention_count'))

    # Export
    wCSVfile = '../tmp-data/02-instagram-epilepsy-comentions-{dicttimestamp:s}-samepost.csv.gz'.format(dicttimestamp=dicttimestamp)
    utils.ensurePathExists(wCSVfile)
    dfR.to_csv(wCSVfile)


    mention_count_CSVfile = '../tmp-data/02-instagram-epilepsy-mentions-counts-{dicttimestamp:s}-samepost.csv.gz'.format(dicttimestamp=dicttimestamp)
    utils.ensurePathExists(mention_count_CSVfile)
    mention_count_df.to_csv(mention_count_CSVfile)

    print('Done.')
