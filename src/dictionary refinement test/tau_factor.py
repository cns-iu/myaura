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

eigen_old = nx.eigenvector_centrality_numpy(old_net, weight='count')
# eigen_old = nx.pagerank_numpy(old_net, alpha=0.99, weight='count')
# eigen_old = nx.eigenvector_centrality_numpy(old_net, weight='proximity')
# eigen_old = nx.pagerank_numpy(old_net, alpha=0.99, weight='proximity')

df_eigen_old = pd.DataFrame(eigen_old.items(), columns=['id', 'centrality'])
# convert id into int
df_eigen_old['id'] = df_eigen_old['id'].astype(int)

for key in id_dict:
    network_name = key
    removed_id = id_dict[key]

    df_eigen_new = pd.read_csv(os.path.join('network', network_name, 'eigen_count_nodes.csv'))
    # eigen_new = nx.pagerank_numpy(new_net, alpha=0.99, weight='count')
    # eigen_new = nx.eigenvector_centrality_numpy(new_net, weight='proximity')
    # eigen_new = nx.pagerank_numpy(new_net, alpha=0.99, weight='proximity')

    # get the set of id from old and new network
    set_nodes_old = set(df_eigen_old['id'])
    set_nodes_new = set(df_eigen_new['id'])

    common_nodes = set_nodes_old.intersection(set_nodes_new)

    # get the common nodes from old and new network
    df_eigen_old_common = df_eigen_old[df_eigen_old['id'].isin(common_nodes)]
    df_eigen_new_common = df_eigen_new[df_eigen_new['id'].isin(common_nodes)]

    # get the centrality in np.array
    centrality_old = df_eigen_old_common['centrality'].values
    centrality_new = df_eigen_new_common['centrality'].values

    for k in range(10, 501):
        tau_sum_0, tau_norm_0 = kendall_top_k(centrality_old, centrality_new, k, p=0, reverse=True)
        tau_sum_1, tau_norm_1 = kendall_top_k(centrality_old, centrality_new, k, p=1, reverse=True)

        sum_diff = tau_sum_1 - tau_sum_0
        norm_factor = k * (k - 1) / 2
