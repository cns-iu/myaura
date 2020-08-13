# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 11:00:41 2020

@author: Sikander
"""

from __future__ import division
# Add package folder location
import sys
sys.path.insert(0, '../ddi_project/include')
sys.path.insert(0, '../ddi_project/social/include')
# DB - Mysql
import db_init_ddi_project as db
# General
import numpy as np
import pandas as pd
import os
import pickle
from collections import Counter
from itertools import combinations
import networkx as nx
from distanceclosure.utils import _prox2dist as prox2dist
from distanceclosure.dijkstra import Dijkstra
# from distanceclosure._dijkstra import _py_single_source_shortest_distances
from distanceclosure.cython._dijkstra import _cy_single_source_shortest_distances
# import time
# from datetime import datetime
# from joblib import Parallel, delayed

#SWITCHES
COMENTIONS = 0
NETWORK = 1
SEPARATE = 0

def compute_comentions(qp): #Where qp is list of matched posts i.e. posts w/ mentions for one user
    uinserts = {} #dict of com-mentions with post-id as keys

    for post in qp:
        post_id = post['_id']
        tokens = post['matches']
        user_id = post['user_id']

        if len(tokens) >= 2:
            comention = {'uid': user_id, 'tokens': tokens, 'count': len(tokens)}
            uinserts[post_id] = comention

    pickle.dump(uinserts, open("comentions/user_{0}.pkl".format(user_id), 'wb'))

def tally(dct, key):
    if key in dct:
        dct[key] += 1
    else:
        dct[key] = 1

def get_network_layer(G, attr):
    H = nx.Graph()
    for (i, j, d) in G.edges.data():
        if attr in d:
            H.add_edge(i, j)
            H[i][j][attr] = d[attr]
    nd_types=nx.get_node_attributes(G, 'type')
    nx.set_node_attributes(H, nd_types, 'type')
    return H

if COMENTIONS == 1:
    count = 0
    for root, dirs, files in os.walk('tagging_results_users', topdown=True):
        for f in files:
            count += 1
            print str(count) + ' out of ' + str(len(files)) + ' users'
            if f[:7] == 'matches':
                ulst = pickle.load(open('tagging_results_users/{0}'.format(f), 'rb')) #list of matched posts i.e. posts w/ mentions for one user
                compute_comentions(ulst)

if NETWORK == 1:
    dicttimestamp = '20180706'
    print '> Loading MySQL master dictionary (%s)' % dicttimestamp
    engine = db.connectToMySQL(server='mysql_ddi_dictionaries')
    tablename = 'dict_%s' % (dicttimestamp)
    sql = """SELECT
			d.id,
			IFNULL(d.id_parent,d.id) AS id_parent,
			d.type, d.token,
			IFNULL(p.token, d.token) as parent,
			d.source, d.id_original,
			IFNULL(p.id_original, d.id_original) as id_original_parent
			FROM %s d
			LEFT JOIN %s p ON d.id_parent = p.id
			""" % (tablename, tablename)
    dfD = pd.read_sql(sql, engine, index_col='parent') #Was index_col='id' before
    dict_parent = dfD['token'].to_dict()
    dict_type = dfD['type'].to_dict()
    dict_id_original_parent = dfD['id_original_parent'].to_dict()

    #BUILD NETWORK
    network_name = 'Network: EF Forums'
    print '--- Building Network ---'
    G = nx.Graph(name=network_name)

    double_menchies = {} #Keys: tokens which appear more than once in a post, Vals: Number of posts in which token appears more than once
    for root, dirs, files in os.walk('comentions', topdown=True):
        count = 0
        for f in files:
            count += 1
            print str(count) + ' out of ' + str(len(files)) + ' users'
            u_posts = pickle.load(open('comentions/{0}'.format(f), 'rb'))
        	# dd = defaultdict(lambda: 0)
            for pid in u_posts:
                matches = u_posts[pid]['tokens']
                tokens = [m['parent'] for m in matches]
                cnt = Counter(tokens)
                double = [k for k in cnt if cnt[k] > 1]
                for d in double:
                    tally(double_menchies, d)
                combs = list(combinations(tokens, 2))
                for c in combs:
                    if G.has_edge(c[0], c[1]):
                        G[c[0]][c[1]]['count'] += 1 #At the moment this is double counting
                    else:
                        G.add_edge(c[0], c[1], count=1)
    G.remove_edges_from(nx.selfloop_edges(G)) #removing self-loops: try G.remove_edges_from(G.selfloop_edges()) if this doesnt work
    print 'NUMBER OF MATCHED TERMS: ' + str(len(G))
    noise_edges = []
    for (i, j, d) in G.edges.data():
        if d['count'] < 10:
            noise_edges.append((i, j))
    G.remove_edges_from(noise_edges)
    G.remove_nodes_from(['Convulsion', 'Epilepsy'])


    print '> Node Attributes'
    nx.set_node_attributes(G, name='type', values={i:dict_type[i] for i in G.nodes()})
    nx.set_node_attributes(G, name='IDOriginalParent', values={i:str(dict_id_original_parent[i]) for i in G.nodes()})
    print '--- Compute Normalized p_ij ---'
    print '> Edge Counts'
    counts = { k : sum([d['count'] for i,j,d in G.edges(nbunch=k, data=True)]) for k in G.nodes() }
    print '> Normalized Values'
    def normalize(i,j,d,min_support=10):
        r_ij = d['count']
        r_ii = counts[i]
        r_jj = counts[j]
        if (r_ii + r_jj - r_ij) >= min_support:
            return r_ij / (r_ii + r_jj - r_ij)
        else:
            return 0.
    P = [ normalize(i,j,d) for i,j,d in G.edges(data=True) ]
    P_dict = dict(zip( G.edges(), P))
    D_dict = dict(zip( G.edges(), map(prox2dist,P) ))

    nx.set_edge_attributes(G, name='proximity', values=P_dict)
    nx.set_edge_attributes(G, name='distance', values=D_dict)
    prox_net = get_network_layer(G, 'proximity')
    dist_net = get_network_layer(G, 'distance')

    print '--- Computing Dijkstra APSP ---'
    dij = Dijkstra.from_edgelist(D_dict, directed=False, verbose=10)
    poolresults = range(len(dij.N))
    for node in dij.N:
        print '> Dijkstra node %s of %s' % (node+1, len(dij.N))
        poolresults[node] = _cy_single_source_shortest_distances(node, dij.N, dij.E, dij.neighbours, ('min', 'sum'), verbose=10)
    shortest_distances, local_paths = map(list, zip(*poolresults))
    dij.shortest_distances = dict(zip(dij.N, shortest_distances))
    SD = dij.get_shortest_distances(format='dict', translate=True) #Dict of dicts with shortest distance as values
    print '> Done.'

    print '> Populating (G)raph'
    Cm = {(i,j):v for i,jv in SD.iteritems() for j, v in jv.iteritems()} #Dict of edge tuple as key and shortest distances as values
    edges_seen = set()
    for (i, j), cm in Cm.iteritems():
        # Knowledge Network is undirected. Small ids come first
        if (i,j) in edges_seen or (i==j):
            continue
        else:
            edges_seen.add( (i,j) )
            # New Edge?
            if not G.has_edge(i,j):
                # Self-loops have proximity 1, non-existent have 0
                proximity = 1 if i==j else 0
                G.add_edge(i,j, distance=np.inf, proximity=proximity, distanceMetricClosure=cm, metricBackbone=False)
            else:
                G[i][j]['distanceMetricClosure'] = cm
                G[i][j]['metricBackbone'] = True if ( (cm == G[i][j]['distance']) and (cm!=np.inf) ) else False

    print '--- Calculating S Values ---'
    S = {(i,j) : d['distance'] / d['distanceMetricClosure']
        for i,j,d in G.edges(data=True)
        if ( (d.get('distance')<np.inf) and (d.get('distanceMetricClosure')>0) )}
    nx.set_edge_attributes(G, name='S', values=S)

    print '--- Calculating B Values ---'
    mean_distance = {
			k : np.mean(
					[d['distance'] for i,j,d in G.edges(nbunch=k, data=True) if 'count' in d]
				)
		for k in G.nodes()}
    print '> b_ij'
    B_ij = {
		(i,j) : float( mean_distance[i] / d['distanceMetricClosure'] )
		for i,j,d in G.edges(data=True)
		if (d.get('distance')==np.inf)}
    nx.set_edge_attributes(G, name='Bij', values=B_ij)
    print '> b_ji'
    B_ji = {
		(i,j) : float( mean_distance[j] / d['distanceMetricClosure'] )
		for i,j,d in G.edges(data=True)
		if (d.get('distance')==np.inf)}
    nx.set_edge_attributes(G, name='Bji', values=B_ji)

    print '> Separating networks'
    co_net = get_network_layer(G, 'count')
    # prox_net = get_network_layer(G, 'proximity')
    # dist_net = get_network_layer(G, 'distance')
    metric_net = get_network_layer(G, 'distanceMetricClosure')
    backbone_net = nx.Graph()
    prox_backbone = nx.Graph()
    nd_typs=nx.get_node_attributes(G, 'type')
    for (i, j, d) in G.edges.data():
        if d['metricBackbone']:
            backbone_net.add_edge(i, j)
            backbone_net[i][j]['distanceMetricClosure'] = d['distanceMetricClosure']
            prox_backbone.add_edge(i, j)
            prox_backbone[i][j]['proximity'] = d['proximity']
            nx.set_node_attributes(backbone_net, nd_typs, 'type')
            nx.set_node_attributes(prox_backbone, nd_typs, 'type')
    s_net = get_network_layer(G, 'S')
    # b_net = nx.Graph()
    # for (i, j, d) in G.edges.data():
    #     b_net.add_edge(i, j, Bij=d['Bij'], Bji=d['Bji'])
        # b_net[i][j]['Bij'] = d['Bij']
        # b_net[i][j]['Bji'] = d['Bji']
    print '> Saving...'
    nx.write_gpickle(co_net, 'separate_networks/efw_comention_net.gpickle')
    nx.write_gpickle(prox_net, 'separate_networks/efw_prox_net.gpickle')
    nx.write_gpickle(dist_net, 'separate_networks/efw_dist_net.gpickle')
    nx.write_gpickle(metric_net, 'separate_networks/efw_metric_net.gpickle')
    nx.write_gpickle(backbone_net, 'separate_networks/efw_distance_backbone_net.gpickle')
    nx.write_gpickle(prox_backbone, 'separate_networks/efw_proximity_backbone_net.gpickle')
    nx.write_gpickle(s_net, 'separate_networks/efw_s_net.gpickle')
    # nx.write_gpickle(b_net, 'separate_networks/efw_b_net.gpickle')

    print '> Saving whole network'

    # print dict_type
    # nx.write_gexf(G, 'efw_comention_net.gexf')
    # nx.write_gpickle(G, 'efw_comention_net.gpickle')
    # pickle.dump(double_menchies, open('double_mentions.pkl', 'wb'))
    # nx.write_gml(G, 'efw_network.gml')
    # nx.write_graphml(G, 'efw_network.graphml')

    print '> Number of nodes'
    print 'G: ' + str(len(G.nodes()))
    print 'prox_net: ' + str(len(prox_net.nodes()))
    print 'dist_net: ' + str(len(dist_net.nodes()))
    print '> Number of edges'
    print 'G: ' + str(len(G.edges()))
    print 'prox_net: ' + str(len(prox_net.edges()))
    print 'dist_net: ' + str(len(dist_net.edges()))
    print '> File size'
    print 'prox_net: ' + str(sys.getsizeof(prox_net))
    print 'dist_net: ' + str(sys.getsizeof(dist_net))

if SEPARATE == 1:
    print '> Reading whole network'
    G = nx.read_gml('whole_networks/efw_network.gml')
    print '> Separating networks'
    co_net = get_network_layer(G, 'count')
    prox_net = get_network_layer(G, 'proximity')
    dist_net = get_network_layer(G, 'distance')
    metric_net = get_network_layer(G, 'distanceMetricClosure')
    backbone_net = nx.Graph()
    for (i, j, d) in G.edges.data():
        if d['metricBackbone']:
            backbone_net.add_edge(i, j)
            backbone_net[i][j]['distanceMetricClosure'] = d['distanceMetricClosure']
    s_net = get_network_layer(G, 'S')
    # b_net = nx.Graph()
    # for (i, j, d) in G.edges.data():
    #     b_net.add_edge(i, j)
    #     b_net[i][j]['Bij'] = d['Bij']
    #     b_net[i][j]['Bji'] = d['Bji']
    # print '> Saving...'
    # nx.write_gml(prox_net, 'separate_networks/efw_prox_net.gml')
    # nx.write_gml(dist_net, 'separate_networks/efw_dist_net.gml')
    # nx.write_gml(metric_net, 'separate_networks/efw_metric_net.gml')
    # nx.write_gml(backbone_net, 'separate_networks/efw_backbone_net.gml')
    # nx.write_gml(s_net, 'separate_networks/efw_s_net.gml')
    # nx.write_gml(b_net, 'separate_networks/efw_b_net.gml')
