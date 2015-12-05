"""
Generates sample figures visualizing game trees.

First, it generates one game graph and saves it to 'game_graph.png'

Then, it plays multiple games, and composes their graphs and saves it to
'multiple_game_graph.png'

Requires the NetworkX graph package and GraphViz, which are included in
Anaconda
"""
from gameplay import play_game
from policies import RandomPolicy, MCTSPolicy
import networkx as nx

# player_policies = [RandomPolicy(), RandomPolicy()]
player_policies = [MCTSPolicy(player='X'), RandomPolicy()]
G = play_game(player_policies)
# import IPython; IPython.embed()
dot_graph = nx.to_pydot(G[0])
dot_graph.set_graph_defaults(fontname='Courier')
dot_graph.write_png('game_graph.png')

games = []

seed(0)

for i in range(100):
    games.append(play_game(player_policies))

# Visualize a game graph without values
# graphs = [game[0] for game in games]
# dot_graph_combined = nx.compose_all(graphs)
# dot_graph = nx.to_pydot(dot_graph_combined)
# dot_graph.set_graph_defaults(fontname='Courier')
# dot_graph.write_png('multiple_game_graph.png')

# Create a small subgraph for visualization with MCTS values
mcts = player_policies[0]
from gamestate import GameState
overallroot = GameState()
root = overallroot
depth = 2

subgraph = nx.DiGraph()


def add_edges(graph, subgraph, parent, depth):
    for child in mcts.digraph.successors(parent):
        if depth:
            add_edges(graph, subgraph, child, depth - 1)

        subgraph.add_node(parent)
        subgraph.add_node(child)
        for node in [parent, child]:
            subgraph.node[node]['n'] = mcts.digraph.node[node]['n']
            subgraph.node[node]['w'] = mcts.digraph.node[node]['w']
        subgraph.add_edge(parent, child)

# Don't include the empty board (the root) in the graphs
for first_move in mcts.digraph.successors(root):
    add_edges(mcts.digraph, subgraph, first_move, 0)
dot_graph = nx.to_pydot(subgraph)

for node in dot_graph.get_nodes():
    attr = node.get_attributes()
    try:
        node.set_label('{}{:.2f}'.format(node.get_name().replace('"', ''),
                                         float(attr['w']) / float(attr['n'])))
    except KeyError:
        pass

dot_graph.set_graph_defaults(fontname='Courier')
dot_graph.set_rankdir('LR')
dot_graph.write_png('mcts_values.png')
