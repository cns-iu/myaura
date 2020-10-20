# coding=utf-8
# Author: Rion B Correia
# Date: Nov 11, 2017
# 
# Description: 
# Build a Network of co-mention straight from the MongoDB
#
from __future__ import division
# Add package folder location
import sys
sys.path.insert(0, '../../include')
sys.path.insert(0, '../../../include')
# DB - Mysql
import db_init as db
# General
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
pd.set_option('display.max_rows', 40)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)
from collections import defaultdict
import networkx as nx
from distanceclosure.utils import _prox2dist as prox2dist
from distanceclosure.dijkstra import Dijkstra
from distanceclosure.cython._dijkstra import _cy_single_source_shortest_distances
# MultiProcessing


if __name__ == '__main__':

	#
	# Init
	#
	dicttimestamp = '20180706'
	
	#window_size = 7 # in days
	#cohort = 'opioids' # (depression, epilepsy or opioids)
	#socialmedia = 'twitter' # (instagram or twitter)
	window_size = raw_input("window_size [(int)]:")
	cohort = raw_input("cohort [depression,epilepsy,opioids]:")
	socialmedia = raw_input("socialmedia [instagram,twitter]:")

	# Consistency
	if window_size.isdigit():
		window_size = int(window_size)
	else:
		raise TypeError ("'window_size' must be int.")
	if cohort not in ['depression','epilepsy','opioids']:
		raise TypeError ("Cohort could not be found. Must be either 'depression','epilepsy' or 'opioids'.")
	if socialmedia not in ['instagram','twitter']:
		raise TypeError ("Socialmedia could not be found. Must be either 'instagram' or 'twitter'.")

	network_name = 'Network (%s : %s : %s : %sD)' % (cohort, socialmedia, dicttimestamp, window_size)
	
	print '--- Loading Dictionaries ---'
	#
	# Load Dictionary from MySQL
	#
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
	dfD = pd.read_sql(sql, engine, index_col='id')
	print dfD.head()
	dict_parent = dfD['token'].to_dict()
	dict_type = dfD['type'].to_dict()
	dict_id_original_parent = dfD['id_original_parent'].to_dict()

	#
	# Load DDI
	#
	print '> Loading MySQL interaction dictionary'
	sql = "SELECT id_drugbank_1, id_drugbank_2, text FROM drugbank510_interaction"
	dfDDI = pd.read_sql(sql, engine)
	dict_ddi_text = dfDDI.set_index(['id_drugbank_1','id_drugbank_2'])['text'].to_dict()
	dict_ddi_text = { frozenset((k)):v for k,v in dict_ddi_text.items() }

	#
	# Load ADR
	#
	print '> Loading MySQL adverse-reaction dictionary'
	sql = "SELECT id_drugbank, pt_code, placebos, frequencies, lowers, uppers FROM sider41_drug_has_sideeffect"
	dfADR = pd.read_sql(sql, engine)
	dfADR['pt_code'] = dfADR['pt_code'].astype(unicode)
	dict_adr_freq = dfADR.set_index(['id_drugbank','pt_code'])['frequencies'].to_dict()
	dict_adr_freq = { frozenset((k)):v for k,v in dict_adr_freq.items() }

	#
	# Load DI
	#
	print '> Loading MySQL drug-indication dictionary'
	sql = "SELECT id_drugbank, pt_code, methods FROM sider41_drug_has_indication"
	dfDI = pd.read_sql(sql, engine)
	dict_di_meth = dfDI.set_index(['id_drugbank','pt_code'])['methods'].to_dict()
	dict_di_meth = { frozenset((k)):v for k,v in dict_di_meth.items()}

	#
	# Mongo
	#
	print ' --- Loading MongoDB Co-Mention Counts ---'
	db_mention = 'ddi_cohort_%s_mentions' % (cohort)
	comention_col = '%s_post_comention_%s_%dd' % (socialmedia, dicttimestamp, window_size)
	db_network = 'ddi_cohort_%s_networks' % (cohort)
	network_col_node = '%s_network_%s_%dd_node' % (socialmedia, dicttimestamp, window_size)
	network_col_edge = '%s_network_%s_%dd_edge' % (socialmedia, dicttimestamp, window_size)
	mongo_mention, _ = db.connectToMongoDB(server='mongo_ddi', db=db_mention)
	mongo_network, _ = db.connectToMongoDB(server='mongo_ddi', db=db_network)


	# Don't count the evidence fields because we only store MAX number of evidences. Instead, sum the "count" field.
	pipeline = [
		{ '$group': { '_id' : { 'source': "$source.id_parent", 'target': "$target.id_parent" },
			'count' : { '$sum': "$count" },
			}
		},
		{ '$sort' : { 'count' : -1 } },
		#{ '$limit' : 100 }
	]
	print '> Mongo Aggregate Query'
	qn = mongo_mention[comention_col].aggregate(pipeline, allowDiskUse=True)
	df = json_normalize(list(qn))
	df.rename(columns={'_id.source':'source','_id.target':'target'}, inplace=True)
	n_tokens = df.shape[0]
	print df.head()
	#
	# build network
	#
	print '--- Building Network ---'
	G = nx.Graph(name=network_name)

	# Adding Nodes
	print '> Nodes'
	G.add_nodes_from([ k for k in np.unique(df[['source','target']].values) ] )
	
	print '> Counting Symmetric Co-Mentions ---'
	dd = defaultdict(lambda: 0)
	for _, r in df.iterrows():
		source, target, count = r['source'], r['target'], r['count']
		#
		if source > target:
			source, target = target, source
		#
		dd[(source,target)] += count

	print '> Edges'
	G.add_edges_from([
		(i,j, {'count':v, 'original':True})
		for (i,j),v in dd.items()
	])
		
	print '> Node Attributes'
	nx.set_node_attributes(G, name='type', values={i:dict_type[i] for i in G.nodes()} )
	nx.set_node_attributes(G, name='id_original_parent', values={i:str(dict_id_original_parent[i]) for i in G.nodes()} )

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
	
	#nx.set_edge_attributes(G, name='weight', values=P_dict) # weight = proximity
	nx.set_edge_attributes(G, name='proximity', values=P_dict)
	nx.set_edge_attributes(G, name='distance', values=D_dict)

	# Compute closure (Using the Dijkstra Class directly)
	print '--- Computing Dijkstra APSP ---'
	dij = Dijkstra.from_edgelist(D_dict, directed=False, verbose=10)
	
	# PARALLEL
	"""
	cpu_count = multiprocessing.cpu_count()
	verbose = 10
	poolresults = Parallel(n_jobs=cpu_count, verbose=verbose)(delayed(_cy_single_source_shortest_distances)(node, dij.N, dij.E, dij.neighbours, ('min','sum'), verbose=None) for node in dij.N)
	shortest_distances, local_paths = map(list, zip(*poolresults))
	dij.shortest_distances = dict(zip(dij.N, shortest_distances))
	SD = dij.get_shortest_distances(format='dict', translate=True)
	"""
	
	# SERIAL
	poolresults = range(len(dij.N))
	for node in dij.N:
		print '> Dijkstra node %s of %s' % (node+1, len(dij.N))
		poolresults[node] = _cy_single_source_shortest_distances(node, dij.N, dij.E, dij.neighbours, ('min','sum'), verbose=10)
	shortest_distances, local_paths = map(list, zip(*poolresults))
	dij.shortest_distances = dict(zip(dij.N, shortest_distances))
	SD = dij.get_shortest_distances(format='dict', translate=True)
	
	print '> Done.'

	print '> Populating (G)raph'
	Cm = {(i,j):v for i,jv in SD.iteritems() for j, v in jv.iteritems()} # Convert Dict-of-Dicts to Dict

	# Cm contains two edges of each. Make sure we are only inserting one
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
				G.add_edge(i,j, distance=np.inf, proximity=proximity, distance_metric_closure=cm, metric_backbone=False)
			else:
				G[i][j]['distance_metric_closure'] = cm
				G[i][j]['metric_backbone'] = True if ( (cm == G[i][j]['distance']) and (cm!=np.inf) ) else False
	
	print '--- Calculating S Values ---'

	S = {
		(i,j) : d['distance'] / d['distance_metric_closure']
		for i,j,d in G.edges(data=True)
		if ( (d.get('distance')<np.inf) and (d.get('distance_metric_closure')>0) )
	}
	nx.set_edge_attributes(G, name='s_value', values=S)

	print '--- Calculating B Values ---'
	mean_distance = {
			k : np.mean(
					[d['distance'] for i,j,d in G.edges(nbunch=k, data=True) if 'count' in d]
				)
		for k in G.nodes()
	}
	print '> b_ij'
	B_ij = {
		(i,j) : float( mean_distance[i] / d['distance_metric_closure'] )
		for i,j,d in G.edges(data=True)
		if (d.get('distance')==np.inf)
	}
	nx.set_edge_attributes(G, name='b_ij_value', values=B_ij)
	
	print '> b_ji'
	B_ji = {
		(i,j) : float( mean_distance[j] / d['distance_metric_closure'] )
		for i,j,d in G.edges(data=True)
		if (d.get('distance')==np.inf)
	}
	nx.set_edge_attributes(G, name='b_ji_value', values=B_ji)


	print '--- Validating DDI/ADR/DI edges ---'
	nr_ddi = 0
	nr_adr = 0
	nr_di = 0
	for z,(i,j,d) in enumerate(G.edges(data=True), start=0):
		#if (z % 10000==0):
		#	print 'Validating DDI/ADR edge: %d of %d' % (z, G.number_of_edges() )

		i_type = G.node[i]['type']
		j_type = G.node[j]['type']
		i_id_original_parent = G.node[i]['id_original_parent']
		j_id_original_parent = G.node[j]['id_original_parent']

		if (i_type in ['Drug','Allergen'] and j_type in ['Allergen','Drug']):
			# DDI
			if frozenset((i_id_original_parent, j_id_original_parent)) in dict_ddi_text:
				G[i][j]['DDI'] = { 'description': dict_ddi_text[frozenset((i_id_original_parent,j_id_original_parent))] }
				nr_ddi += 1
				print '> DDI found (%s so far)' % nr_ddi

		# ADR or DI?s
		elif ( (i_type in ['Drug','Allergen'] and j_type == 'Medical term') or (i_type == 'Medical term' and j_type in ['Drug','Allergen']) ):

			# ADR
			if frozenset((i_id_original_parent, j_id_original_parent)) in dict_adr_freq:
				G[i][j]['ADR'] = { 'frequency': dict_adr_freq[frozenset((i_id_original_parent, j_id_original_parent))] }
				nr_adr += 1
				print '> ADR found (%s so far)' % nr_adr

			# DI list
			if frozenset((i_id_original_parent, j_id_original_parent)) in dict_di_meth:
				G[i][j]['DI'] = { 'method': dict_di_meth[frozenset((i_id_original_parent, j_id_original_parent))] }
				nr_di += 1
				print '> DI found (%s so far)' % nr_di

	print '--- Saving to MongoDB ---'
	node_inserts = []
	print '> looping nodes'
	
	for i,d in G.nodes(data=True):
		node = {
			'_id':i,
			'token': dict_parent[i],
			'type': dict_type[i],
			'id_original': dict_id_original_parent[i]
		}
		node_inserts.append(node)
	print '> inserting nodes to MongoDB'
	mongo_network[network_col_node].insert_many(node_inserts, ordered=False)

	print '> looping edges'
	edge_inserts = []
	for i,j,d in G.edges(data=True):
		edge = {
			'_id':'{i:d}-{j:d}'.format(i=i,j=j),
			'i': i,
			'j': j,
		}
		# Add Properties
		for key,value in d.items():
			if key in ['b_ij_value','b_ji_value']:
				if not 'b_value' in edge:
					edge['b_value'] = dict()
				edge['b_value'][ key[2:] ] = value
			else:
				edge[key] = value
		
		edge_inserts.append(edge)
	
	print '> inserting edges to MongoDB'
	mongo_network[network_col_edge].insert_many(edge_inserts, ordered=False)

	print '> creating indexes'
	mongo_network[network_col_node].create_index("token", background=True)
	mongo_network[network_col_edge].create_index("i", background=True)
	mongo_network[network_col_edge].create_index("j", background=True)
	mongo_network[network_col_edge].create_index("metric_backbone", background=True, sparse=True)
	mongo_network[network_col_edge].create_index("original", background=True, sparse=True)

	print '> done.'


