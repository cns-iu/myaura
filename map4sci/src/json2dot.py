from time import perf_counter
from json import load
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
from networkx.relabel import convert_node_labels_to_integers
from sys import argv

class Timer:
  def __init__(self) -> None:
    self._starts = {}
  
  def start(self, measure):
    self._starts[measure] = perf_counter()
  
  def stop(self, measure):
    if measure in self._starts:
      timing = perf_counter() - self._starts[measure]
      print(f'{measure}, {timing}')
      return timing
    else:
      return 0

timer = Timer()

GRAPH = argv[1]
OUT = argv[2]

timer.start('Original Network: Loading time')
G = nx.Graph()
graph = load(open(GRAPH))

for row in graph['nodes']:
  G.add_node(row['id'], label=row['label'], weight=1)

for row in graph['edges']:
  G.add_edge(row['source'], row['target'], weight=row['weight'])

timer.stop('Original Network: Loading time')

max_degree = max( degree for (_, degree) in G.degree() )
print('Original Network: Max Degree,', max_degree, '\nOriginal Network: # Nodes,', G.number_of_nodes(), '\nOriginal Network: # Edges,', G.number_of_edges())

# timer.start('Original Network: Node Betweenness Centrality time')
# for (n, centrality) in nx.betweenness_centrality(G, weight='weight', normalized=False).items():
#   G.nodes[n]['weight'] = centrality
# timer.stop('Original Network: Node Betweenness Centrality time')

timer.start('Original Network: Node PageRank time')
for (n, rank) in nx.pagerank(G, weight='weight').items():
  G.nodes[n]['weight'] = rank
timer.stop('Original Network: Node PageRank time')


timer.start('Largest Component: Computing time')
G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
H = convert_node_labels_to_integers(G, 1, 'decreasing degree', 'src_id')
timer.stop('Largest Component: Computing time')

print('Largest Component: # Nodes,', H.number_of_nodes(), '\nLargest Component: # Edges,', H.number_of_edges())
write_dot(H, OUT)
