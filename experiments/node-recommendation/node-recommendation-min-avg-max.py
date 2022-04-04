# coding: utf-8
# Author: Rion B Correia
# Date: 01 April 2022
#
# Description:
# Methods to load a particular network
#
import os, sys
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
#include_path = '/nfs/nfs7/home/rionbr/myaura/include'
sys.path.insert(0, include_path)
#
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import networkx as nx
#
import db_init as db
import utils


if __name__ == '__main__':

    dicttimestamp = '20210321'

    # Database connection
    engine = db.connectToPostgreSQL(server='cns-postgres-myaura')
    
    #
    # Load Network
    #

    # Nodes
    sql_nodes = """
        SELECT d.id, d.token, d.type
        FROM net_efwebsite_forums_{dicttimestamp:s}.nodes n
        JOIN dictionaries.dict_{dicttimestamp:s} d ON d.id = n.id_node
    """.format(dicttimestamp=dicttimestamp)
    dfN = pd.read_sql(sql_nodes, con=engine, index_col='id')

    # Edges
    sql_edges = """
        SELECT e.source, e.target, e.proximity, e.is_metric, e.s_value
        FROM net_efwebsite_forums_{dicttimestamp:s}.edges e
        WHERE e.proximity > 0
    """.format(dicttimestamp=dicttimestamp)
    dfE = pd.read_sql(sql_edges, con=engine)

    # Build Network
    G = nx.from_pandas_edgelist(dfE, source='source', target='target', edge_attr=['proximity', 'is_metric', 's_value'])
    nx.set_node_attributes(G, name='type', values=dfN['type'].to_dict())
    nx.set_node_attributes(G, name='token', values=dfN['token'].to_dict())

    #
    # Query
    #
    alpha = 0.1

    # 461 = Fluoxetine
    # 177790 = Headache
    query = {
        461,  # Fluoxetine
        177790,  # Headache
    }
    #
    query = {
        339,  # Clobazam
        1186,  # Levetiracetam
        542,  # Lamotrigine
        5491,  # Lacosamide
        551,  # Carbamazepine
        815, # Diazepam
        762,  # Oxcarbazepine
    }

    r = [{'i': i, 'j': j, **G[i][j], **G.nodes[j]} for i in query for j in G.neighbors(i)]
    dfQ = pd.DataFrame(r)
    # Remove query terms
    dfQ = dfQ.loc[~(dfQ['i'].isin(query)) | ~(dfQ['j'].isin(query)), :]
    # Metric Backbone
    dfQB = dfQ.loc[(dfQ['is_metric'] == True), :].copy()

    agg = {'proximity': 'mean', 'token': 'first', 'type': 'first'}    

    # Query Proximity Network
    dfQ.groupby('j').agg(agg).sort_values('proximity', ascending=False)[:10]

    # Query Metric Backbone
    dfQB.groupby('j').agg(agg).sort_values('proximity', ascending=False)[:10]

"""
In [211]: dfQ.groupby('j').agg(agg).sort_values('proximity', ascending=False)[:10]
Out[211]: 
        proximity                 token          type
j                                                    
304      0.052379         Valproic Acid          Drug
174366   0.049956            Convulsion  Medical term
243      0.046613             Phenytoin          Drug
264      0.045422            Topiramate          Drug
177516   0.036897  Grand mal convulsion  Medical term
176107   0.035380              Epilepsy  Medical term
184014   0.034649             Pregnancy  Medical term
895      0.032527            Zonisamide          Drug
175720   0.030030  Electroencephalogram  Medical term
1158     0.029305         Phenobarbital          Drug

In [212]: dfQB.groupby('j').agg(agg).sort_values('proximity', ascending=False)[:10]
Out[212]: 
        proximity                 token          type
j                                                    
174366   0.118584            Convulsion  Medical term
304      0.076717         Valproic Acid          Drug
184014   0.070608             Pregnancy  Medical term
177516   0.068650  Grand mal convulsion  Medical term
264      0.066840            Topiramate          Drug
243      0.060898             Phenytoin          Drug
172362   0.060606          Blood sodium  Medical term
170661   0.048459               Anxiety  Medical term
186374   0.047791    Status epilepticus  Medical term
175023   0.047072            Depression  Medical term
"""