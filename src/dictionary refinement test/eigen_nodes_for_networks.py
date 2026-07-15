#%%

import networkx as nx
import os, pickle, json
import sys
sys.path.append('../../include')
import pandas as pd
import numpy as np


#%%

# load know_ids.json
with open('known_ids.json', 'r') as f:
    know_ids = json.load(f)
name_root = 'thR_8_1000'
with open(name_root + '_id.json', 'r') as f:
    batch_ids = json.load(f)


id_dict = batch_ids

# old_network_file = '../../instagram/tmp-data/04-instagram-epilepsy-network-20180706-samepost.graphml'
# old_net = nx.read_graphml(old_network_file)

for key in id_dict:
    print(key)
    network_name = key
    removed_id = id_dict[key]

    new_network_file = os.path.join('network', network_name, '04-instagram-epilepsy-network-20180706-samepost.graphml')

    new_net = nx.read_graphml(new_network_file)

    # eigen_old = nx.eigenvector_centrality_numpy(old_net, weight='count')
    eigen_new = nx.eigenvector_centrality_numpy(new_net, weight='count')
    eigen_data_file_name = os.path.join('network', network_name, 'eigen_count_nodes.csv')

    # eigen_old = nx.pagerank_numpy(old_net, alpha=0.99, weight='count')
    # eigen_new = nx.pagerank_numpy(new_net, alpha=0.99, weight='count')
    # eigen_old = nx.eigenvector_centrality_numpy(old_net, weight='proximity')
    # eigen_new = nx.eigenvector_centrality_numpy(new_net, weight='proximity')
    # eigen_old = nx.pagerank_numpy(old_net, alpha=0.99, weight='proximity')
    # eigen_new = nx.pagerank_numpy(new_net, alpha=0.99, weight='proximity')

    df_eigen_new = pd.DataFrame(eigen_new.items(), columns=['id', 'centrality'])

    # save into csv
    df_eigen_new.to_csv(eigen_data_file_name, index=False)

