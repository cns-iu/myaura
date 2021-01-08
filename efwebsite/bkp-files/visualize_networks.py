# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:58:39 2020

@author: Sikander
"""
print '> Loading modules'
import numpy as np
import networkx as nx
#from wordcloud import WordCloud
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt
plt.switch_backend('agg')
print '> Modules loaded'


def unique_values(dct):
    seen = set()
    for key in dct:
        if dct[key] in seen:
            continue
        else:
            seen.add(dct[key])
    return seen

def princ_comp(net_type):
    H = nx.read_gpickle("separate_networks/efw_{0}_net.gpickle".format(net_type))
    print'> Node Attributes'
    node_types=nx.get_node_attributes(H, 'type')
    # print node_types
    uniq_nd_types = unique_values(node_types)
    print "Number of unique term types: " + str(len(uniq_nd_types))
    print uniq_nd_types
    colors =  ['royalblue','limegreen','salmon','gold'] #'c','y',
    edge_clrs = ['navy','darkgreen','darkred','darkorange'] #'cyan','olive',
    dict_map = {}
    edge_dict_map = {}
    for i, typ in enumerate(uniq_nd_types):
        dict_map[typ] = colors[i]
        edge_dict_map[typ] = edge_clrs[i]
    print dict_map
    print edge_dict_map
    dfG = pd.DataFrame(data={'type': [d.get('type', None) for n, d in H.nodes(data=True)]}, index=H.nodes)
    # print dfG.head()
    mat = nx.to_numpy_matrix(H)
    print 'Calculating PCA (sklearn) ' + net_type
    pca = PCA(n_components=None, svd_solver='full')
    res = pca.fit_transform(mat)
    df_PCA = pd.DataFrame(res[:, 0:9], columns=['1c', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c'], index=dfG.index)
    df_PCA = pd.concat([dfG, df_PCA], axis='columns')
    # print df_PCA.head()
    s_Var = pd.Series(pca.explained_variance_ratio_, index=range(1, (res.shape[1] + 1)), name='explained_variance_ratio')
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(figsize=(12, 10), nrows=3, ncols=3)
    fig.suptitle("PCA on {0} network".format(net_type.replace("_", " ")))
    s_cumsum = s_Var.cumsum()
    n_eigen_95 = s_cumsum[(s_cumsum < 0.95)].shape[0]
    n = 9
    ind = np.arange(n)
    height = s_Var.iloc[:n].values
    width = 0.60
    xticklabels = (ind + 1)
    cmap = mpl.cm.get_cmap('hsv_r')
    norm = mpl.colors.Normalize(vmin=0, vmax=n)
    tab20 = cm.get_cmap('tab20').colors
    s_colors = tab20[0::2]
    s_edgecolors = tab20[1::2]
    ax1.bar(ind, height, width, color=s_colors, edgecolor=s_edgecolors, zorder=9, lw=1)
    ax1.set_xticks(ind)
    ax1.set_xticklabels(xticklabels)
    ax1.set_title('Explained variance ratio')
    ax1.annotate('95% with {:,d}\nsingular vectors'.format(n_eigen_95), xy=(0.97, 0.97), xycoords="axes fraction", ha='right', va='top')
    ax1.set_xlabel('Components')
    ax1.set_ylabel('%')
    ax1.grid()
    for dim, ax in zip(range(1, 10), [ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]):
        print('- Dim: {:d}'.format(dim))
        col = str(dim) + 'c'
        x = str(dim) + 'c'
        y = str(dim + 1) + 'c'
        xs = df_PCA[x].tolist()
        ys = df_PCA[y].tolist()
        pca_colors = df_PCA['type'].map(lambda x: dict_map[x]) # dfPCA['color'].tolist()
        pca_edgecolors = df_PCA['type'].map(lambda x: edge_dict_map[x])
        ax.scatter(xs, ys, c=pca_colors, marker='o', edgecolor=pca_edgecolors, lw=0.5, s=30, zorder=5, rasterized=True)
        ax.plot(0,0, color='#2ca02c', marker='x', ms=16)
        ax.axhline(y=0, c='black', lw=0.75, ls='-.', zorder=2)
        ax.axvline(x=0, c='black', lw=0.75, ls='-.', zorder=2)
        ax.set_title('Components {dim1} and {dim2}'.format(dim1=dim, dim2=(dim + 1)) )
        ax.set_xlabel('Component {dim1:d}'.format(dim1=dim))
        ax.set_ylabel('Component {dim2:d}'.format(dim2=dim + 1))
        ax.grid()
        ax.axis('equal')
        ax.locator_params(axis='both', tight=True, nbins=6)
    plt.subplots_adjust(left=0.06, right=0.98, bottom=0.06, top=0.93, wspace=0.26, hspace=0.35)
    plt.savefig("pca_{0}.png".format(net_type))
    df_PCA.to_csv("pca_{0}.csv".format(net_type))

if __name__=='__main__':
#    G = nx.read_graphml("separate_networks/efw_comention_net.graphml")
#    wt_deg = {}
#    for nd in G.nodes():
#        no_space = nd.replace(" ", "")
#        wt_deg[no_space] = G.degree(nd, weight='count')
#    text = " ".join((" " + tag)*wt_deg[tag] for tag in wt_deg)
#    wordcloud = WordCloud(collocations=False, background_color="white").generate(text)
#    plt.imshow(wordcloud, interpolation='bilinear')
#    plt.axis("off")
#    plt.savefig("wordcloud.png")

    #COMENTION NETWORK DEGREE DISTRIBUTION
#    G = nx.read_graphml("separate_networks/efw_comention_net.graphml")
#    cnts = []
#    for i,j,d in G.edges.data():
#        cnts.append(d['count'])
#    plt.figure()
#    plt.hist(cnts, bins=np.arange(0, max(cnts), 10), log=True)
#    plt.title("Edge weight distribution in co-mention network")
#    plt.xlabel("Edge weight")
#    plt.ylabel("Count")
#    plt.savefig("edge_distr_comentions.png")


    netlist = ['comention', 'proximity_backbone', 'distance_backbone', 'metric', 's', 'prox', 'dist'] #'prox',
    for net in netlist:
        princ_comp(net)
