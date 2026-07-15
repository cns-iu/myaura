#%%

import networkx as nx
import os,pickle
import sys
from scipy import stats
sys.path.append('../../include')
from load_dictionary import load_dictionary
import db_init as db
import pandas as pd
from kendall import kendall_top_k
import numpy as np

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

# for old_network_file, new_network_file in [['random-control/04-instagram-epilepsy-network-20180706-samepost.graphml',
#                                             'random-control/04-instagram-epilepsy-network-random12-samepost.graphml'],
#                                            ['random-control/04-efwebsite-forums-network-20180706-samepost.graphml',
#                                             'random-control/04-efwebsite-forums-network-random12-samepost.graphml']]:
                                           # ['random-control/04-pubmed-epilepsy-network-20180706.graphml',
                                           #  'random-control/04-pubmed-epilepsy-network-20210321.graphml'],
                                           # ['random-control/ct-epilepsy-network-20180706.graphml',
                                           #  'random-control/ct-epilepsy-network-20210321.graphml']]:

# for old_network_file, new_network_file in [['tmp-data/04-instagram-epilepsy-network-20180706-samepost.graphml',
#                                             'tmp-data/04-instagram-epilepsy-network-20210321-samepost.graphml'],
#                                            ['tmp-data/04-efwebsite-forums-network-20180706-samepost.graphml',
#                                             'tmp-data/04-efwebsite-forums-network-20210321-samepost.graphml'],
#                                            ['tmp-data/04-pubmed-epilepsy-network-20180706.graphml',
#                                             'tmp-data/04-pubmed-epilepsy-network-20210321.graphml'],
#                                            ['tmp-data/04-twitter-epilepsy-network-20180706-samepost.graphml',
#                                             'tmp-data/04-twitter-epilepsy-network-20210321-samepost.graphml'],
#                                            ['tmp-data/ct-epilepsy-network-20180706.graphml',
#                                             'tmp-data/ct-epilepsy-network-20210321.graphml']]:

for old_network_file, new_network_file in [['../../instagram/tmp-data/04-instagram-epilepsy-network-20180706-samepost.graphml',
                                            '../../instagram/tmp-data/04-instagram-epilepsy-network-20210321-samepost.graphml'],
                                           ['../../efwebsite/tmp-data/04-efwebsite-forums-network-20180706-samepost.graphml',
                                            '../../efwebsite/tmp-data/04-efwebsite-forums-network-20210321-samepost.graphml'],
                                           ['../../pubmed/tmp-data/04-pubmed-epilepsy-network-20180706.graphml',
                                            '../../pubmed/tmp-data/04-pubmed-epilepsy-network-20210321.graphml'],
                                           ['../../twitter/tmp-data/04-twitter-epilepsy-network-20180706-samepost.graphml',
                                            '../../twitter/tmp-data/04-twitter-epilepsy-network-20210321-samepost.graphml'],
                                           ['../../clinicaltrials/tmp-data/04-pubmed-epilepsy-network-20180706.graphml',
                                            '../../clinicaltrials/tmp-data/04-pubmed-epilepsy-network-20210321.graphml']]:
    print('-----------------------------------')
    print(old_network_file)
    old_net = nx.read_graphml(old_network_file)
    new_net = nx.read_graphml(new_network_file)

    print(old_net.number_of_nodes(), new_net.number_of_nodes())

    #%%

    # new 8 from children terms
    removed_id = [8433, 202468, 211750, 201791, 35150, 174899, 240710, 8619]
    # original 12
    # removed_id = [8433,202468,211750,201798,201791,35150,174899,240710,8619,199415,170326,190790]
    # random 12
    # removed_id = [240710, 146507, 25536, 8593, 182630, 8619, 240925, 188818, 16726, 8582, 206783, 8628]


    def get_parent(idx):
        return dfD.loc[idx]['id_parent']

    removed_parent = [get_parent(i) for i in removed_id]

    #%%

    # eigen_old = nx.eigenvector_centrality_numpy(old_net, weight='count')
    # eigen_new = nx.eigenvector_centrality_numpy(new_net, weight='count')
    # eigen_old = nx.pagerank_numpy(old_net, alpha=0.85, weight='count')
    # eigen_new = nx.pagerank_numpy(new_net, alpha=0.85, weight='count')

    # remove edges with zero proximity
    edge_to_removed = []
    for i, j, d in old_net.edges(data=True):
        if d['proximity'] == 0:
            edge_to_removed.append((i,j))
    for i, j in edge_to_removed:
        old_net.remove_edge(i,j)
    edge_to_removed = []
    for i, j, d in new_net.edges(data=True):
        if d['proximity'] == 0:
            edge_to_removed.append((i,j))
    for i, j in edge_to_removed:
        new_net.remove_edge(i,j)
    old_net_lcc = old_net.subgraph(max(nx.connected_components(old_net), key=len))
    new_net_lcc = new_net.subgraph(max(nx.connected_components(new_net), key=len))
    # eigen_old = nx.eigenvector_centrality_numpy(old_net_lcc, weight='proximity')
    # eigen_new = nx.eigenvector_centrality_numpy(new_net_lcc, weight='proximity')
    # eigen_old = nx.eigenvector_centrality_numpy(old_net, weight='proximity')
    # eigen_new = nx.eigenvector_centrality_numpy(new_net, weight='proximity')
    # eigen_old = nx.pagerank_numpy(old_net, alpha=0.85, weight='proximity')
    # eigen_new = nx.pagerank_numpy(new_net, alpha=0.85, weight='proximity')
    eigen_old = nx.pagerank_numpy(old_net, alpha=0.99, weight='proximity')
    eigen_new = nx.pagerank_numpy(new_net, alpha=0.99, weight='proximity')


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
    print('before')
    describe_list(top_nodes_old[:20], eigen_old)

    #%%

    top_nodes_new = sorted(eigen_new, key=eigen_new.get, reverse=True)
    print('after')
    describe_list(top_nodes_new[:20], eigen_new)

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
    print(rg1[:20])
    print(rg2[:20])

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

    print('-----spearman old vs new---------')
    for i in [10, 20, 50, 100, 200, 500]:
        rho, p = stats.spearmanr(rg1[:i], rg2[:i])
        print('|', '|'.join([str(x) for x in [i,rho,p]] ), '|')
    print()

    print('-----spearman new vs old---------')
    for i in [10, 20, 50, 100, 200, 500]:
        rho, p = stats.spearmanr(rgg1[:i], rgg2[:i])
        print('|', '|'.join([str(x) for x in [i,rho,p]] ), '|')
    print()
    #%%

    print('-----kandall old vs new---------')
    for i in [10, 20, 50, 100, 200, 500]:
        rho, p = stats.kendalltau(rg1[:i], rg2[:i])
        print('|', '|'.join([str(x) for x in [i,rho,p]] ), '|')
    print()

    print('-----kandall new vs old---------')
    for i in [10, 20, 50, 100, 200, 500]:
        rho, p = stats.kendalltau(rgg1[:i], rgg2[:i])
        print('|', '|'.join([str(x) for x in [i,rho,p]] ), '|')
    print()

    print('-----kandall top k ---------')
    rga1 = np.array(score_list_full_old)
    rga2 = np.array(score_list_full_new)
    for i in [10, 20, 50, 100, 200, 500]:
        rho, n_tau = kendall_top_k(rga1, rga2, k=i, p=0.5, reverse=True)
        print('|', '|'.join([str(x) for x in [i, rho, n_tau]]), '|')
    print()

    #%%

    print("----- top nodes' top neighbors ---------")
    for term in top_nodes_new[:10]:
        print(term, get_token(term))
        prox_l = []
        for to_node in old_net[term]:
            prox_l.append([get_token(to_node), old_net[term][to_node]['proximity']])
        prox_l.sort(key=lambda x:x[1],reverse=True)
        print_list(prox_l[:5])
        print('--------------')
        prox_l = []
        for to_node in new_net[term]:
            prox_l.append([get_token(to_node), new_net[term][to_node]['proximity']])
        prox_l.sort(key=lambda x:x[1],reverse=True)
        print_list(prox_l[:5])
        print()

    #%%

    for term in top_nodes_old[:10]:
        if term in new_net:
            print(term, get_token(term))
            prox_l = []
            for to_node in old_net[term]:
                prox_l.append([get_token(to_node), old_net[term][to_node]['proximity']])
            prox_l.sort(key=lambda x:x[1],reverse=True)
            print_list(prox_l[:5])
            print('--------------')
            prox_l = []
            for to_node in new_net[term]:
                prox_l.append([get_token(to_node), new_net[term][to_node]['proximity']])
            prox_l.sort(key=lambda x:x[1],reverse=True)
            print_list(prox_l[:5])
            print()

