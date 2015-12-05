"""
Plays many games and then plots the cumulative win rates of the players.

The player policies can be chosen from MCTS and Random.
"""

from gameplay import play_game
from policies import RandomPolicy, MCTSPolicy
from visualization import visualize_mcts_tree
import networkx as nx
import numpy as np

# Choose the player policies here:
MCTS_vs_Random = [MCTSPolicy(player='X'), RandomPolicy()]
Random_vs_MCTS = [RandomPolicy(), MCTSPolicy(player='O')]
MCTS_vs_MCTS = [MCTSPolicy(player='X'), MCTSPolicy(player='O')]
Random_vs_Random = [RandomPolicy(), RandomPolicy()]

experiments = [[MCTSPolicy(player='X'), RandomPolicy()],
               [MCTSPolicy(player='X'), RandomPolicy()],
               [RandomPolicy(), MCTSPolicy(player='O')],
               [RandomPolicy(), MCTSPolicy(player='O')],
               [MCTSPolicy(player='X'), MCTSPolicy(player='O')],
               [MCTSPolicy(player='X'), MCTSPolicy(player='O')],
               [RandomPolicy(), RandomPolicy()],
               [RandomPolicy(), RandomPolicy()]]

names = ['x_mcts_vs_o_random_1',
         'x_mcts_vs_o_random_2',
         'x_random_vs_o_mcts_1',
         'x_random_vs_o_mcts_2',
         'x_mcts_vs_o_mcts_1',
         'x_mcts_vs_o_mcts_2',
         'x_random_vs_o_random_1',
         'x_random_vs_o_random_2']


def run_experiment(player_policies, experiment_name, n):
    # For reproducibility
    np.random.seed(0)

    games = []
    winners = []
    X_wins = np.zeros(n)
    O_wins = np.zeros(n)
    X_win_rate = np.zeros(n)
    O_win_rate = np.zeros(n)

    for i in range(n):
        G, winner = play_game(player_policies)
        games.append(G)
        winners.append(winner)

        # Copy cumulative totals from previous timestep
        if i > 0:
            X_wins[i] = X_wins[i - 1]
            O_wins[i] = O_wins[i - 1]

        if winner == 'X':
            X_wins[i] += 1
        elif winner == 'O':
            O_wins[i] += 1

        X_win_rate[i] = X_wins[i] / (i + 1)
        O_win_rate[i] = O_wins[i] / (i + 1)

    from collections import Counter
    c = Counter(winners)
    print(c.items())
    print(X_win_rate)
    print(X_wins)

    from matplotlib import pyplot as plt

    # Plot cumulative win count over time
    # plt.plot(X_wins)
    # plt.plot(O_wins)
    # plt.legend(['X wins', 'O wins'])

    # Plot cumulative win rate over time
    plt.plot(X_win_rate)
    plt.plot(O_win_rate)
    plt.legend(['X', 'O'])
    plt.xlabel('simulation')
    plt.ylabel('cumulative win rate')
    plt.ylim([-0.1, 1.1])
    plt.title('Experiment ID: {}'.format(name.replace('_', ' ').upper()))

    # Save figure to disk with a unique identifier
    plt.savefig('simulation_time_' + str(simulation_time) + '_' + '{}.png'.format(experiment_name))
    plt.cla()

    # Save a visualization of the first n levels of
    # the MCTS trees used by each player that used MCTS
    for policy in player_policies:
        if type(policy) is MCTSPolicy:
            visualize_mcts_tree(mcts=policy,
                                depth=0,
                                filename='{}_{}'.format(name, policy.player))

    # # Analyze the opening moves (todo)
    # policy = player_policies[0]
    # from gamestate import GameState
    # opening_moves = policy.digraph.successors(GameState())
    #
    # for node in opening_moves:
    #     print('=======================')
    #     print(node)
    #     print('{} / {} = {}'.format(policy.digraph.node[node]['w'],
    #                                 policy.digraph.node[node]['n'],
    #                                 policy.digraph.node[node]['w'] / policy.digraph.node[node]['n']))
    #     print()

    # Generate visual game trees
    # dot_graph_combined = nx.compose_all(games)
    # dot_graph = nx.to_pydot(dot_graph_combined)
    # dot_graph.set_graph_defaults(fontname='Courier')
    # dot_graph.write_png('multiple_game_graph_mcts_vs_random.png')

for experiment, name in zip(experiments, names):
    # Different number of games to play per experiment
    n = [10, 20, 50, 100, 150, 200]
    for simulation_time in n:
        run_experiment(experiment, name, simulation_time)
