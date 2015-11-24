"""
Function to play a game given a policy for each player and keep track of
the game as a NetworkX game tree.

Requires the NetworkX graph package, which is included in Anaconda
"""
import networkx as nx
from gamestate import GameState


class StateNode(object):
    def __init__(self, board):
        self.state = board
        self.parent = None
        self.child = None


def play_game(player_policies):
    """
    :param player_policies: List of policy functions for players X and O
     which determine how each player moves given a particular state
    :return: Returns a NetworkX Graph object describing the game
    """
    game = GameState()

    # Keep track of the game tree
    G = nx.DiGraph()
    G.add_node(str(game))
    root = str(game)
    current = root

    while game.winner() is None:
        plies = 0
        for player_policy in player_policies:
            plies += 1
            print("\nPly #{}. It is {}'s move.".format(plies, game.turn))

            game.move(*player_policy(game))

            previous = current
            G.add_node(str(game))
            current = str(game)
            G.add_edge(previous, current)

            print('New game state:\n{}'.format(game))

            if game.winner() is not None:
                break

    print('Game over. Winner is {}.'.format(game.winner()))

    return G
