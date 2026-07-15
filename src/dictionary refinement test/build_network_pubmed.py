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
# include_path = '/nfs/nfs7/home/rionbr/myaura/include'
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
import db_init as db
from dijkstra import all_pairs_dijkstra_path_length
#from distanceclosure.utils import _prox2dist as prox2dist
#from distanceclosure.dijkstra import Dijkstra
#from distanceclosure.cython._dijkstra import _cy_single_source_shortest_distances
from build_network_common import load_comention, metric_backbone

if __name__ == '__main__':

    dicttimestamp1 = '20180706'
    dicttimestamp2 = '20210321'

    comention_table1 = 'mention_pubmed_epilepsy_%s.comention' % (dicttimestamp1)
    comention_table2 = 'mention_pubmed_epilepsy_%s.comention' % (dicttimestamp2)
    network_name1 = 'Network (PubMed : Epilepsy : {dicttimestamp:s})'.format(dicttimestamp=dicttimestamp1)
    network_name2 = 'Network (PubMed : Epilepsy : {dicttimestamp:s})'.format(dicttimestamp=dicttimestamp2)

    G1 = load_comention(comention_table1, network_name1)
    G2 = load_comention(comention_table2, network_name2)

    print(G1.number_of_nodes(), G2.number_of_nodes())

    common_nodes = set(G1.nodes) & set(G2.nodes)

    print("common nodes", len(common_nodes))

    G1.remove_nodes_from(set(G1.nodes)-common_nodes)
    G2.remove_nodes_from(set(G2.nodes)-common_nodes)

    print("common nodes", len(common_nodes))

    wGfile1 = 'tmp-data/04-pubmed-epilepsy-network-{dicttimestamp:s}'.format(dicttimestamp=dicttimestamp1)
    wGfile2 = 'tmp-data/04-pubmed-epilepsy-network-{dicttimestamp:s}'.format(dicttimestamp=dicttimestamp2)

    metric_backbone(G1, wGfile1)
    metric_backbone(G2, wGfile2)
