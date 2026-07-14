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
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

common_element_ratio_dict = defaultdict(list)
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

    # common_nodes = set_nodes_old.intersection(set_nodes_new)
    # another version, don't use common_nodes
    common_nodes = set_nodes_old | set_nodes_new

    # get the common nodes from old and new network
    df_eigen_old_common = df_eigen_old[df_eigen_old['id'].isin(common_nodes)]
    df_eigen_new_common = df_eigen_new[df_eigen_new['id'].isin(common_nodes)]

    # get the centrality in np.array
    centrality_old = df_eigen_old_common['centrality'].values
    centrality_new = df_eigen_new_common['centrality'].values

    # get a list of node, in the order of centrality for old network
    top_nodes_old = df_eigen_old_common.sort_values(by='centrality', ascending=False)['id'].values
    # get a list of node, in the order of centrality for new network
    top_nodes_new = df_eigen_new_common.sort_values(by='centrality', ascending=False)['id'].values

    l_top_nodes_old = [node for node in top_nodes_old if node in common_nodes]
    l_top_nodes_new = [node for node in top_nodes_new if node in common_nodes]

    limit = 500
    for k in range(10, limit + 1):
        common_element_ratio = len(set(l_top_nodes_old[:k]) & set(l_top_nodes_new[:k])) / k
        common_element_ratio_dict[k].append(common_element_ratio)

df_common_element_ratio_stat = pd.DataFrame()
for k,v in common_element_ratio_dict.items():
    df_common_element_ratio_stat.loc[k, 'mean'] = np.mean(v)
    df_common_element_ratio_stat.loc[k, 'std'] = np.std(v)
    df_common_element_ratio_stat.loc[k, 'min'] = np.min(v)
    df_common_element_ratio_stat.loc[k, 'max'] = np.max(v)

df_common_element_ratio_stat.to_csv('common_element_ratio_stat.csv')

#%%

# now we get the reference curve for the common element ratio

reference_network_file = '../../instagram/tmp-data/04-instagram-epilepsy-network-20231116-samepost.graphml'
reference_net = nx.read_graphml(reference_network_file)

eigen_reference = nx.eigenvector_centrality_numpy(reference_net, weight='count')
# common_nodes = set(eigen_old.keys()) & set(eigen_reference.keys())
common_nodes = set(eigen_old.keys()) | set(eigen_reference.keys())
df_eigen_reference = pd.DataFrame(eigen_reference.items(), columns=['id', 'centrality'])
l_top_nodes_reference = df_eigen_reference.sort_values(by='centrality', ascending=False)['id'].values
l_top_nodes_reference = [int(node) for node in l_top_nodes_reference]
reference_common_element_ratio_dict = {}
for k in range(10, limit + 1):
    common_element_ratio = len(set(l_top_nodes_old[:k]) & set(l_top_nodes_reference[:k])) / k
    reference_common_element_ratio_dict[k] = common_element_ratio

df_common_element_ratio_reference = pd.DataFrame(reference_common_element_ratio_dict.items(), columns=['k', 'common_element_ratio'])


#%%

fig, ax = plt.subplots()

random_mean, = ax.plot(df_common_element_ratio_stat.index, df_common_element_ratio_stat['mean']) #, label='Mean CER After Removing Random 8 Terms')
random_std = ax.fill_between(df_common_element_ratio_stat.index, df_common_element_ratio_stat['mean'] - df_common_element_ratio_stat['std'],
                 df_common_element_ratio_stat['mean'] + df_common_element_ratio_stat['std'], alpha=0.2) #, label='±1 STD of CER After Removing Random 8 Terms')
selected_8, = ax.plot(df_common_element_ratio_reference['k'], df_common_element_ratio_reference['common_element_ratio']) #, label='CER After Removing Selected 8 Terms')
handles = [random_mean, random_std, selected_8]
labels = ['Mean CER After Removing Random 8 Terms', '±1 STD of CER After Removing Random 8 Terms', 'CER After Removing Selected 8 Terms']
ax.legend(handles=handles, labels=labels, loc='lower right')
ax.set_xlabel('k')
ax.set_ylabel('Common Element Ratio')
# set y limit
ax.set_ylim(0, 1)
fig.show()

#%%

# Initialize the matplotlib figure
plt.figure(figsize=(6.5, 4.5))

sns.set(font_scale=0.83)
plt.rcParams['font.family'] = 'stix'
plt.rcParams['mathtext.fontset'] = 'stix'
# Create a color palette
palette = sns.color_palette("mako_r", 2)

# Main line plot for the mean CER after removing random terms
sns.lineplot(x=df_common_element_ratio_stat.index, y='mean', data=df_common_element_ratio_stat, label='Mean CER After Removing Random 8 Terms', color=palette[0])

# Add the fill between for standard deviation
plt.fill_between(df_common_element_ratio_stat.index,
                 df_common_element_ratio_stat['mean'] - df_common_element_ratio_stat['std'],
                 df_common_element_ratio_stat['mean'] + df_common_element_ratio_stat['std'],
                 color=palette[0], alpha=0.2, label='±1 STD of CER After Removing Random 8 Terms')

# Additional line plot for the selected terms impact
sns.lineplot(x='k', y='common_element_ratio', data=df_common_element_ratio_reference, label='CER After Removing Selected 8 Terms', color=palette[1])

# Enhancing the plot
plt.xlabel(r'$\mathit{k}$')
plt.ylabel('Common Element Ratio (CER)')
# plt.title('Impact of Term Removal on CER')
plt.ylim(0, 1)
plt.legend(loc='lower right')

plt.tight_layout()
# Show the plot
plt.savefig('results/plot/common_element_ratio.pdf')
plt.show()

#%%
# the same figure, with log scale x axis
# discussion: the y axis is limited to [0,1], not a good idea to get the log scale
# however, it is common to see scale law on ranking

# Initialize the matplotlib figure
plt.figure(figsize=(6.5, 4.5))
# Initialize the matplotlib figure
plt.figure(figsize=(6.5, 4.5))

sns.set(font_scale=0.83)
plt.rcParams['font.family'] = 'stix'
plt.rcParams['mathtext.fontset'] = 'stix'
# Create a color palette
palette = sns.color_palette("mako_r", 2)

# Main line plot for the mean CER after removing random terms
sns.lineplot(x=df_common_element_ratio_stat.index, y='mean', data=df_common_element_ratio_stat, label='Mean CER After Removing Random 8 Terms', color=palette[0])

# this doesn't work well
# plot 1-mean for better visualization
# sns.lineplot(x=df_common_element_ratio_stat.index, y=1-df_common_element_ratio_stat['mean'], label='1 - Mean CER After Removing Random 8 Terms', color=palette[0])

# Add the fill between for standard deviation
plt.fill_between(df_common_element_ratio_stat.index,
                 df_common_element_ratio_stat['mean'] - df_common_element_ratio_stat['std'],
                 df_common_element_ratio_stat['mean'] + df_common_element_ratio_stat['std'],
                 color=palette[0], alpha=0.2, label='±1 STD of CER After Removing Random 8 Terms')

# Additional line plot for the selected terms impact
sns.lineplot(x='k', y='common_element_ratio', data=df_common_element_ratio_reference, label='CER After Removing Selected 8 Terms', color=palette[1])

# this doesn't work well
# 1- for better visualization
# sns.lineplot(x=df_common_element_ratio_reference['k'], y=1-df_common_element_ratio_reference['common_element_ratio'], label='1 - CER After Removing Selected 8 Terms', color=palette[1])

# Enhancing the plot
plt.xlabel(r'$\mathit{k}$')
plt.ylabel('Common Element Ratio (CER)')
# plt.title('Impact of Term Removal on CER')
# plt.ylim(0, 1)
plt.legend(loc='lower right')

plt.tight_layout()

plt.xscale('log')
# plt.yscale('log')

plt.show()