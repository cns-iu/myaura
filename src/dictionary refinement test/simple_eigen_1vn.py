#%%

import networkx as nx
import os,pickle, json
import sys
from scipy import stats
sys.path.append('../../include')
from load_dictionary import load_dictionary
import db_init as db
import pandas as pd
from kendall import kendall_top_k
import numpy as np
from tabulate import tabulate

#%%

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

#%%

# load know_ids.json
with open('known_ids.json', 'r') as f:
    know_ids = json.load(f)
name_root = 'thR_8_1000'
with open(name_root + '_id.json', 'r') as f:
    batch_ids = json.load(f)


id_dict = batch_ids

list_tau = []

old_network_file = '../../instagram/tmp-data/04-instagram-epilepsy-network-20180706-samepost.graphml'
old_net = nx.read_graphml(old_network_file)

for key in id_dict:
    network_name = key
    removed_id = id_dict[key]

    new_network_file = os.path.join('network', network_name,'04-instagram-epilepsy-network-20180706-samepost.graphml')


    print('-----------------------------------')
    print(new_network_file)
    new_net = nx.read_graphml(new_network_file)

    print(old_net.number_of_nodes(), new_net.number_of_nodes())

    #%%

    def get_parent(idx):
        return dfD.loc[idx]['id_parent']

    removed_parent = [get_parent(i) for i in removed_id]

    #%%

    eigen_old = nx.eigenvector_centrality_numpy(old_net, weight='count')
    eigen_new = nx.eigenvector_centrality_numpy(new_net, weight='count')
    # eigen_old = nx.pagerank_numpy(old_net, alpha=0.99, weight='count')
    # eigen_new = nx.pagerank_numpy(new_net, alpha=0.99, weight='count')
    # eigen_old = nx.eigenvector_centrality_numpy(old_net, weight='proximity')
    # eigen_new = nx.eigenvector_centrality_numpy(new_net, weight='proximity')
    # eigen_old = nx.pagerank_numpy(old_net, alpha=0.99, weight='proximity')
    # eigen_new = nx.pagerank_numpy(new_net, alpha=0.99, weight='proximity')


    #%%

    def get_token(idx):
        return dfD.loc[int(idx)]['token']
    def print_list(l):
        for line in l:
            print('|'+'|'.join([str(i) for i in line])+'|')
    def describe_list(l, d):
        for item in l:
            token = get_token(item)
            print('|', item,'|',  token,'|',  d[item], '|' )

    #%%

    top_nodes_old = sorted(eigen_old, key=eigen_old.get, reverse=True)
    # print('before')
    # describe_list(top_nodes_old[:20], eigen_old)

    #%%

    top_nodes_new = sorted(eigen_new, key=eigen_new.get, reverse=True)
    # print('after')
    # describe_list(top_nodes_new[:20], eigen_new)

    #%%

    # no need for this, since now two networks have same nodes, but we need to be tolerant to old code
    common_id = set(top_nodes_new) & set(top_nodes_old)
    # remove parent terms of removed tokens. Need this? Not for generalized kendall tau
    legit_id = common_id - set([str(i) for i in removed_parent])

    limit = 500
    count = 0
    rg1 = []
    idl = []
    rg2 = []
    for i, idd in enumerate(top_nodes_old):
        if idd in legit_id:
            count += 1
            if count > limit:
                break
            rg1.append(i)
            idl.append(idd)
    for idd in idl:
        rg2.append(top_nodes_new.index(idd))
    # print(rg1[:20])
    # print(rg2[:20])

    rgg1, rgg2, iddl = [],[],[]
    count = 0
    for i, idd in enumerate(top_nodes_new):
        if idd in legit_id:
            count += 1
            if count > limit:
                break
            rgg1.append(i)
            iddl.append(idd)
    for idd in iddl:
        rgg2.append(top_nodes_old.index(idd))
    #%%

    # new code for ranking coefficient. old code might be wrong, because not symmetric
    # don't use original value so that top k is meaning
    # rank_old = {}
    # rank_new = {}
    # super_id_set = set(top_nodes_new) & set(top_nodes_old)
    # for i, idd in enumerate(top_nodes_old):
    #     rank_old[idd] = i
    # for i, idd in enumerate(top_nodes_new):
    #     rank_new[idd] = i
    # rank_list_full_old, rank_list_full_new = [], []
    # for idd in common_id:
    #     rank_list_full_old.append(rank_old[idd])
    #     rank_list_full_new.append(rank_new[idd])
    score_list_full_old, score_list_full_new = [], []
    for idd in common_id:
        score_list_full_old.append(eigen_old[idd])
        score_list_full_new.append(eigen_new[idd])

    # print('-----spearman old vs new---------')
    # for i in [10, 20, 50, 100, 200, 500]:
    #     rho, p = stats.spearmanr(rg1[:i], rg2[:i])
    #     print('|', '|'.join([str(x) for x in [i,rho,p]] ), '|')
    # print()
    #
    # print('-----spearman new vs old---------')
    # for i in [10, 20, 50, 100, 200, 500]:
    #     rho, p = stats.spearmanr(rgg1[:i], rgg2[:i])
    #     print('|', '|'.join([str(x) for x in [i,rho,p]] ), '|')
    # print()
    # #%%
    #
    # print('-----kandall old vs new---------')
    # for i in [10, 20, 50, 100, 200, 500]:
    #     rho, p = stats.kendalltau(rg1[:i], rg2[:i])
    #     print('|', '|'.join([str(x) for x in [i,rho,p]] ), '|')
    # print()
    #
    # print('-----kandall new vs old---------')
    # for i in [10, 20, 50, 100, 200, 500]:
    #     rho, p = stats.kendalltau(rgg1[:i], rgg2[:i])
    #     print('|', '|'.join([str(x) for x in [i,rho,p]] ), '|')
    # print()

    print('-----kandall top k ---------')
    rga1 = np.array(score_list_full_old)
    rga2 = np.array(score_list_full_new)
    net_tau = []
    for i in [10, 20, 50, 100, 200, 500]:
        rho, n_tau = kendall_top_k(rga1, rga2, k=i, p=0.5, reverse=True)
        net_tau.append(n_tau)
        print('|', '|'.join([str(x) for x in [i, rho, n_tau]]), '|')
    print()
    list_tau.append(net_tau)


# [10, 20, 50, 100, 200, 500]
# create a data.frame with columns named as top_10, top_20, top_50, top_100, top_200, top_500
# every cell is a float number, which is the tau value
# get the value from list_tau
df_tau = pd.DataFrame(list_tau, columns=['top_10', 'top_20', 'top_50', 'top_100', 'top_200', 'top_500'])
df_tau.to_csv(name_root + '_tau.csv', index=False)

# for each column of df_tau, calculate the mean and std
print('printing mean and std')
for col in df_tau.columns:
    print(col, df_tau[col].mean(), df_tau[col].std())

# print this to org-mode table, transpose the table
# keep only two decimal places
tbl = tabulate(df_tau.describe().T, headers='keys', tablefmt='orgtbl', floatfmt='.3f')
print(tbl)

# save df_tau to csv file
df_tau.to_csv(name_root + '_tau.csv', index=False)
