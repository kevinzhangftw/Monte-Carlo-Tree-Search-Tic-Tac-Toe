from gameplay import play_game
from policies import RandomPolicy, MCTSPolicy
import numpy as np
import networkx as nx

player_policies = [MCTSPolicy(), RandomPolicy()]

# For reproducibility
np.random.seed(0)

games = []
for i in range(100):
    games.append(play_game(player_policies))

graphs = [game[0] for game in games]
dot_graph_combined = nx.compose_all(graphs)
dot_graph = nx.to_pydot(dot_graph_combined)
dot_graph.set_graph_defaults(fontname='Courier')
dot_graph.write_png('multiple_game_graph.png')
