#%%

import os,csv
import sys
from scipy import stats
sys.path.append('../../include')
from load_dictionary import load_dictionary
import db_init as db
import pandas as pd
from collections import defaultdict

#%%


removed_id = set([8433,202468,211750,201798,201791,35150,174899,240710,8619,199415,170326,190790])

dicttimestamp = '20180706'
engine = db.connectToPostgreSQL(server='cns-postgres-myaura')
tablename = 'dictionaries.dict_%s' % (dicttimestamp)
sql = """
    SELECT
        d.id,
        COALESCE(d.id_parent,d.id) AS id_parent,
        d.dictionary,
        d.token,
        COALESCE(p.token, d.token) as parent,
        d.type,
        d.source,
        d.id_original,
        COALESCE(p.id_original, d.id_original) as id_original_parent
        FROM %s d
        LEFT JOIN %s p ON d.id_parent = p.id
        """ % (tablename, tablename)
dfD = pd.read_sql(sql, engine, index_col='id')

for before_file, after_file in [['tmp-data/04-instagram-epilepsy-network-20180706-samepost-edges.csv',
                                 'tmp-data/04-instagram-epilepsy-network-20210321-samepost-edges.csv'],
                                ['tmp-data/04-efwebsite-forums-network-20180706-samepost-edges.csv',
                                 'tmp-data/04-efwebsite-forums-network-20210321-samepost-edges.csv'],
                                ['tmp-data/04-pubmed-epilepsy-network-20180706-edges.csv',
                                 'tmp-data/04-pubmed-epilepsy-network-20210321-edges.csv'],
                                ['tmp-data/ct-epilepsy-network-20180706-edges.csv',
                                 'tmp-data/ct-epilepsy-network-20210321-edges.csv']]:
    print('-----------------------------')
    print(before_file)

    def read_csv(filepath):
        true_set = set()
        false_set = set()
        with open(filepath) as fp:
            for line in csv.DictReader(fp):
                source = int(line['source'])
                target = int(line['target'])
                if source in removed_id or target in removed_id:
                    continue
                if line['is_metric'] == 'True':
                    true_set.add(frozenset([source, target]))
                else:
                    false_set.add(frozenset([source, target]))
        return true_set,false_set

    #%%

    old_true, old_false = read_csv(before_file)
    new_true, new_false = read_csv(after_file)

    #%%

    print(len(old_true), len(old_false))
    print(len(new_true), len(new_false))
    print(len(new_true - old_true))
    print(len(old_true - new_true))

    #%%

    def get_token(idx):
        return dfD.loc[int(idx)]['token']
    def show_aggregate(pair_set):
        count = defaultdict(int)
        for a,b in pair_set:
            count[a] += 1
            count[b] += 1
        sorted_list = sorted(count.items(), key=lambda x:x[1], reverse=True)
        for i in range(10):
            tid = sorted_list[i][0]
            token = get_token(tid)
            print(tid, token, sorted_list[i][1])

    #%%

    show_aggregate(new_true-old_true)
    print('-----------')
    show_aggregate(old_true-new_true)
    print()

    #%%

    def find_token_pair(pair_set, tid):
        for a,b in pair_set:
            if a == tid or b == tid:
                print(a, get_token(a), b, get_token(b))

    #%%

    # find_token_pair(new_true - old_true, 815)
    find_token_pair(new_true - old_true, 175023)

    print()

    #%%

    # find_token_pair(old_true - new_true, 815)
    find_token_pair(old_true - new_true, 175023)

    #%%


