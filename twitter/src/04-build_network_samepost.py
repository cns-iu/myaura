# coding=utf-8
# Author: Rion B Correia & Xuan Wang
# Date: Jan 07, 2021
#
# Description: Build the Network from co-mentions
#
import os
import sys
#
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
#include_path = '/nfs/nfs7/home/rionbr/myaura/include'
sys.path.insert(0, include_path)
#
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 40)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)
import networkx as nx
#
import utils
from dijkstra import all_pairs_dijkstra_path_length
#from distanceclosure.utils import _prox2dist as prox2dist
#from distanceclosure.dijkstra import Dijkstra
#from distanceclosure.cython._dijkstra import _cy_single_source_shortest_distances


if __name__ == '__main__':

    # Init
    dicttimestamp = '20180706'
    # dicttimestamp = '20210321'
    #window_size = '7'  # in days

    """
    #
    # Load DDI
    #
    engine = db.connectToMySQL(server='mysql_ddi_dictionaries')
    print('> Loading MySQL interaction dictionary')
    sql = "SELECT id_drugbank_1, id_drugbank_2, text FROM drugbank510_interaction"
    dfDDI = pd.read_sql(sql, engine)
    dict_ddi_text = dfDDI.set_index(['id_drugbank_1', 'id_drugbank_2'])['text'].to_dict()
    dict_ddi_text = {frozenset((k)): v for k, v in list(dict_ddi_text.items())}

    #
    # Load ADR
    #
    print('> Loading MySQL adverse-reaction dictionary')
    sql = "SELECT id_drugbank, pt_code, placebos, frequencies, lowers, uppers FROM sider41_drug_has_sideeffect"
    dfADR = pd.read_sql(sql, engine)
    dfADR['pt_code'] = dfADR['pt_code'].astype(str)
    dict_adr_freq = dfADR.set_index(['id_drugbank', 'pt_code'])['frequencies'].to_dict()
    dict_adr_freq = {frozenset((k)): v for k, v in list(dict_adr_freq.items())}

    #
    # Load DI
    #
    print('> Loading MySQL drug-indication dictionary')
    sql = "SELECT id_drugbank, pt_code, methods FROM sider41_drug_has_indication"
    dfDI = pd.read_sql(sql, engine)
    dict_di_meth = dfDI.set_index(['id_drugbank', 'pt_code'])['methods'].to_dict()
    dict_di_meth = {frozenset((k)): v for k, v in list(dict_di_meth.items())}
    """
    #
    # Load CoMention counts
    #
    rCSVfile = '../tmp-data/02-twitter-epilepsy-comentions-{dicttimestamp:s}-samepost.csv.gz'.format(dicttimestamp=dicttimestamp)
    df = pd.read_csv(rCSVfile, index_col=0, header=[0, 1])

    mention_count_CSVfile = '../tmp-data/02-twitter-epilepsy-mentions-counts-{dicttimestamp:s}-samepost.csv.gz'.format(dicttimestamp=dicttimestamp)
    mention_count_df = pd.read_csv(mention_count_CSVfile, index_col=0)
    mention_count_dict = {}
    for _, row in mention_count_df.iterrows():
        mention_count_dict[int(row['id_parent'])] = int(row['mention_count'])

    # Filter
    df = df.loc[df[('comention', 'count')] >= 3, :]

    #
    # build network
    #
    print('--- Building Network ---')
    network_name = 'Network (Twitter : Epilepsy : {dicttimestamp:s})'.format(dicttimestamp=dicttimestamp)
    G = nx.Graph(name=network_name)

    # Adding Nodes/Edges
    i = 0
    n = len(df)
    for _, row in df.iterrows():
        if i % 1000 == 0:
            print('> Parsing comentions. Row {i:,d} of {n:,d} ({per:.2%})'.format(i=i, n=n, per=(i / n)))
        source = row['source']
        target = row['target']
        count = row['comention']['count']
        #
        if not G.has_node(source['id_parent']):
            G.add_node(source['id_parent'], **{'parent': source['parent'], 'type': source['type']})
        if not G.has_node(target['id_parent']):
            G.add_node(target['id_parent'], **{'parent': target['parent'], 'type': target['type']})

        G.add_edge(source['id_parent'], target['id_parent'], **{'count': count, 'is_original': True})
        #
        i += 1


    print('--- Compute Normalized p_ij ---')

    min_support = 10
    print('> Normalized Values (min_support: {min_support:d}'.format(min_support=min_support))

    def normalize(i, j, d, min_support=10):
        r_ij = d['count']
        r_ii = mention_count_dict[i]
        r_jj = mention_count_dict[j]
        if (r_ii + r_jj - r_ij) >= min_support:
            return r_ij / (r_ii + r_jj - r_ij)
        else:
            return 0.

    P = [normalize(i, j, d, min_support) for i, j, d in G.edges(data=True)]
    P_dict = dict(list(zip(G.edges(), P)))
    D_dict = dict(list(zip(G.edges(), list(map(utils.prox2dist, P)))))

    # nx.set_edge_attributes(G, name='weight', values=P_dict) # weight = proximity
    nx.set_edge_attributes(G, name='proximity', values=P_dict)
    nx.set_edge_attributes(G, name='distance', values=D_dict)

    # Compute closure (Using the Dijkstra Class directly)
    print('--- Computing Dijkstra APSP ---')

    n = G.number_of_nodes()
    i = 0
    edges_seen = set()
    for u, shortest_path_lenghts in all_pairs_dijkstra_path_length(G, weight='distance', disjunction=sum):
        if (i % 50 == 0):
            print('> Dijkstra: {i:d} of {n:d} ({per:.2%})'.format(i=i, n=n, per=(i / n)))
        #
        for v, shortest_path_legth in shortest_path_lenghts.items():
            # Skip ij == ji and self-loops
            if (u, v) in edges_seen or (u == v):
                continue

            if not G.has_edge(u, v):
                # For now, don't add edges that do not exist in the original graph.
                # G.add_edge(u, v, **{'proximity': np.inf, 'distance': shortest_path_legth})
                pass
            else:
                G[u][v]['metric_distance'] = shortest_path_legth
                G[u][v]['is_metric'] = True if ((shortest_path_legth == G[u][v]['distance']) and (shortest_path_legth != np.inf)) else False
        #
        i += 1


    i = 0
    edges_seen = set()
    for u, shortest_path_lenghts in all_pairs_dijkstra_path_length(G, weight='distance', disjunction=max):
        if (i % 50 == 0):
            print('> Dijkstra: {i:d} of {n:d} ({per:.2%})'.format(i=i, n=n, per=(i / n)))
        #
        for v, shortest_path_legth in shortest_path_lenghts.items():
            # Skip ij == ji and self-loops
            if (u, v) in edges_seen or (u == v):
                continue

            if not G.has_edge(u, v):
                # For now, don't add edges that do not exist in the original graph.
                # G.add_edge(u, v, **{'proximity': np.inf, 'distance': shortest_path_legth})
                pass
            else:
                G[u][v]['ultrametric_distance'] = shortest_path_legth
                G[u][v]['is_ultrametric'] = True if ((shortest_path_legth == G[u][v]['distance']) and (shortest_path_legth != np.inf)) else False
        #
        i += 1

    print('> Done.')

    print('--- Calculating S Values ---')

    S = {
        (i, j): d['distance'] / d['metric_distance']
        for i, j, d in G.edges(data=True)
        if ((d.get('distance') < np.inf) and (d.get('metric_distance') > 0))
    }
    nx.set_edge_attributes(G, name='s_value', values=S)

    """
    print('--- Validating DDI/ADR/DI edges ---')
    nr_ddi = 0
    nr_adr = 0
    nr_di = 0
    for z, (i, j, d) in enumerate(G.edges(data=True), start=0):
        # if (z % 10000==0):
        #	print 'Validating DDI/ADR edge: %d of %d' % (z, G.number_of_edges() )

        i_type = G.nodes[i]['type']
        j_type = G.nodes[j]['type']
        i_id_original_parent = G.nodes[i]['id_original_parent']
        j_id_original_parent = G.nodes[j]['id_original_parent']

        if (i_type in ['Drug', 'Allergen'] and j_type in ['Allergen', 'Drug']):
            # DDI
            if frozenset((i_id_original_parent, j_id_original_parent)) in dict_ddi_text:
                G[i][j]['DDI'] = {'description': dict_ddi_text[frozenset((i_id_original_parent, j_id_original_parent))]}
                nr_ddi += 1
                print('> DDI found (%s so far)' % nr_ddi)

        # ADR or DI?s
        elif ((i_type in ['Drug', 'Allergen'] and j_type == 'Medical term') or (
                i_type == 'Medical term' and j_type in ['Drug', 'Allergen'])):

            # ADR
            if frozenset((i_id_original_parent, j_id_original_parent)) in dict_adr_freq:
                G[i][j]['ADR'] = {'frequency': dict_adr_freq[frozenset((i_id_original_parent, j_id_original_parent))]}
                nr_adr += 1
                print('> ADR found (%s so far)' % nr_adr)

            # DI list
            if frozenset((i_id_original_parent, j_id_original_parent)) in dict_di_meth:
                G[i][j]['DI'] = {'method': dict_di_meth[frozenset((i_id_original_parent, j_id_original_parent))]}
                nr_di += 1
                print('> DI found (%s so far)' % nr_di)

    print('> done.')
    """
    print('--- Exporting ---')
    # Graph gormat
    wGfile = '../tmp-data/04-twitter-epilepsy-network-{dicttimestamp:s}-samepost'.format(dicttimestamp=dicttimestamp)
    print('> gpickle')
    nx.write_gpickle(G, wGfile + '.gpickle')
    print('> graphml')
    nx.write_graphml(G, wGfile + '.graphml')

    # Nodes / Edges format
    print('> edgelist (csv.gz)')
    dfN = pd.DataFrame.from_dict(dict(G.nodes(data=True)), orient='index')
    dfN.index.name = 'id_node'
    sN = dfN.reset_index()['id_node']
    sN.to_csv(wGfile + '-nodes.csv', index=False)
    #
    dfE = nx.to_pandas_edgelist(G)
    cols = ['source', 'target', 'count', 'proximity', 'distance', 'is_original', 'metric_distance', 'is_metric',
            's_value', 'ultrametric_distance', 'is_ultrametric']
    dfE = dfE[cols]
    dfE.to_csv(wGfile + '-edges.csv', index=False)

    print('Done.')
