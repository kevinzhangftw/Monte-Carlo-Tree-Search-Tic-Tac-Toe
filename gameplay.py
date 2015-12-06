"""
Function to play a game given a policy for each player and keep track of
the game as a NetworkX game tree.

Requires the NetworkX graph package, which is included in Anaconda
"""
import networkx as nx
from gamestate import GameState
from policies import MCTSPolicy


class StateNode(object):
    def __init__(self, board):
        self.state = board
        self.parent = None
        self.child = None


def play_game(player_policies):
    """
    :param player_policies: List of policy classes for players X and O
     which determine how each player moves given a particular state. Each
     policy class should inherit from Policy.
    :return: Returns a NetworkX Graph object describing the game
    """
    game = GameState()

    # Keep track of the game tree
    G = nx.DiGraph()
    # Todo: use the newly implemented hashing method
    G.add_node(str(game))
    root = str(game)
    current = root

    plies = 0

    # Inform the player policies that a new game is starting (so they can reset their current move pointers)
    for player_policy in player_policies:
        if type(player_policy) is MCTSPolicy:
            player_policy.reset_game()

    while game.winner() is None:
        for player_policy in player_policies:
            plies += 1
            print("\n================ ( Ply #{}. It is {}'s move. ) ================".format(plies, game.turn()))

            game.move(*player_policy.move(game))

            previous = current
            G.add_node(str(game))
            current = str(game)
            G.add_edge(previous, current)

            if game.winner() is not None:
                break

    print('Game over. Winner is {}.'.format(game.winner()))

    return G, game.winner()
