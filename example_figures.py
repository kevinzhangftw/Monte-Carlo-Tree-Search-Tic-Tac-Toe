"""
Generates sample figures visualizing game trees.

First, it generates one game graph and saves it to 'game_graph.png'

Then, it plays multiple games, and composes their graphs and saves it to
'multiple_game_graph.png'

Requires the NetworkX graph package and GraphViz, which are included in
Anaconda
"""
from gameplay import play_game
from policies import RandomPolicy
import networkx as nx

player_policies = [RandomPolicy(), RandomPolicy()]
G = play_game(player_policies)

dot_graph = nx.to_pydot(G)
dot_graph.set_graph_defaults(fontname='Courier')
dot_graph.write_png('game_graph.png')

games = []

for i in range(30):
    games.append(play_game(player_policies))

dot_graph_combined = nx.compose_all(games)
dot_graph = nx.to_pydot(dot_graph_combined)
dot_graph.set_graph_defaults(fontname='Courier')
dot_graph.write_png('multiple_game_graph.png')
