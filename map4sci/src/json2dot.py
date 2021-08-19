from collections import Counter
from json import load
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
from networkx.relabel import convert_node_labels_to_integers
from sys import argv

GRAPH = argv[1]
OUT = argv[2]

G = nx.Graph()
graph = load(open(GRAPH))

for row in graph['nodes']:
  G.add_node(row['id'], label=row['label'], weight=1)

for row in graph['edges']:
  G.add_edge(row['source'], row['target'], weight=row['weight'])

max_degree = max( degree for (_, degree) in G.degree() )
print('Max Degree:', max_degree, '# Nodes:', G.number_of_nodes(), '# Edges: ', G.number_of_edges())

for (n, centrality) in nx.betweenness_centrality(G, weight='weight', normalized=False).items():
  G.nodes[n]['weight'] = centrality

G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
H = convert_node_labels_to_integers(G, 1, 'decreasing degree', 'src_id')

print('Writing Network... Limited:', H.number_of_nodes(), H.number_of_edges())
write_dot(H, OUT)
