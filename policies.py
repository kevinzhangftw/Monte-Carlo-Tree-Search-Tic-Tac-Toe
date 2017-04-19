"""
Game play policies can be defined here. Policies should inherit from the
abstract class Policy.
"""
from abc import ABCMeta, abstractmethod
import random
import numpy as np
import operator
import networkx as nx
import copy
from gamestate import GameState

EPSILON = 10e-6  # Prevents division by 0 in calculation of UCT


class Policy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def move(self, state):
        pass

class HumanPolicy(Policy):
    def move(self, gameStatus):
        legal_moves = gameStatus.legal_moves()
        print ('Available legal moves are:')
        for i in legal_moves:
            print i 
        gameStatus.printBoard()

        policyInput = input('Human, enter your next move: ')
        
        if policyInput < len(legal_moves):
            print ('move legal! please continue')
        else:
            print ('move not allowed! undefined state here')
        
        return legal_moves[policyInput]

class RandomPolicy(Policy):
    def move(self, state):
        """Chooses moves randomly from the legal moves in a given state"""
        legal_moves = state.legal_moves()
        idx = np.random.randint(len(legal_moves))
        return legal_moves[idx]
        # return np.random.choice(state.legal_moves())


class MCTSPolicy(Policy):

    def __init__(self, player):
        """
        Implementation of Monte Carlo Tree Search

        Creates a root of an MCTS tree to keep track of the information
        obtained throughout the course of the game in the form of a tree
        of MCTS nodes

        The data structure of a node consists of:
          - the game state which it corresponds to
          - w, the number of wins that have occurred at or below it in the tree
          - n, the number of plays that have occurred at or below it in the tree
          - expanded, whether all the children (legal moves) of the node have
            been added to the tree

        To access the node attributes, use the following format. For example,
        to access the attribute 'n' of the root node:
          policy = MCTSPolicy()
          current_node = policy.root
          policy.tree.node[current_node]['n']
        """
        self.digraph = nx.DiGraph()
        self.player = player
        self.num_simulations = 0
        # Constant parameter to weight exploration vs. exploitation for UCT
        self.uct_c = np.sqrt(2)

        self.node_counter = 0

        empty_board = GameState()
        self.digraph.add_node(self.node_counter, attr_dict={'w': 0,
                                                            'n': 0,
                                                            'uct': 0,
                                                            'expanded': False,
                                                            'state': empty_board})
        empty_board_node_id = self.node_counter
        self.node_counter += 1

        self.last_move = None

        if player is 'O':
            for successor in [empty_board.transition_function(*move) for move in empty_board.legal_moves()]:
                self.digraph.add_node(self.node_counter, attr_dict={'w': 0,
                                                                    'n': 0,
                                                                    'uct': 0,
                                                                    'expanded': False,
                                                                    'state': successor})
                self.digraph.add_edge(empty_board_node_id, self.node_counter)
                self.node_counter += 1

    def reset_game(self):
        self.last_move = None

    def move(self, starting_state):
        # Make a copy of the starting state so that the MCTS state can't be
        # modified later from the outside
        starting_state = copy.deepcopy(starting_state)
        # todo: is that copy needed?

        starting_node = None

        if self.last_move is not None:
            # Check if the starting state is already in the graph as a child of the last move that we made
            exists = False
            for child in self.digraph.successors(self.last_move):
                # Check if the child has the same state attribute as the starting state
                if self.digraph.node[child]['state'] == starting_state:
                    # If it does, then check if there is a link between the last move and this child state
                    if self.digraph.has_edge(self.last_move, child):
                        exists = True
                        starting_node = child
            if not exists:
                # If it wasn't found, then add the starting state and an edge to it from the last move
                self.digraph.add_node(self.node_counter,
                                      attr_dict={'w': 0,
                                                 'n': 0,
                                                 'uct': 0,
                                                 'expanded': False,
                                                 'state': starting_state})
                self.digraph.add_edge(self.last_move,
                                      self.node_counter)
                starting_node = self.node_counter
                self.node_counter += 1
        else:
            for node in self.digraph.nodes():
                if self.digraph.node[node]['state'] == starting_state:
                    starting_node = node

        computational_budget = 25

        for i in range(computational_budget):
            self.num_simulations += 1

            print("Running MCTS from this starting state with node id {}:\n{}".format(starting_node,
                                                                                      starting_state))

            # Until computational budget runs out, run simulated trials
            # through the tree:

            # Selection: Recursively pick the best node that maximizes UCT
            # until reaching an unvisited node
            print('================ ( selection ) ================')
            selected_node = self.selection(starting_node)
            print('selected:\n{}'.format(self.digraph.node[selected_node]['state']))

            # Check if the selected node is a terminal state, and if so, this
            # iteration is finished
            if self.digraph.node[selected_node]['state'].winner():
                break

            # Expansion: Add a child node where simulation will start
            print('================ ( expansion ) ================')
            new_child_node = self.expansion(selected_node)
            print('Node chosen for expansion:\n{}'.format(new_child_node))

            # Simulation: Conduct a light playout
            print('================ ( simulation ) ================')
            reward = self.simulation(new_child_node)
            print('Reward obtained: {}\n'.format(reward))

            # Backpropagation: Update the nodes on the path with the simulation results
            print('================ ( backpropagation ) ================')
            self.backpropagation(new_child_node, reward)

        move, resulting_node = self.best(starting_node)
        print('MCTS complete. Suggesting move: {}\n'.format(move))

        self.last_move = resulting_node

        # If we won, reset the last move to None for future games
        if self.digraph.node[resulting_node]['state'].winner():
            self.last_move = None

        return move

    def best(self, root):
        """
        Returns the action that results in the child with the highest UCT value
        (An alternative strategy could also be used, where the action leading to
        the child with the most number of visits is chosen
        """
        # Todo: explore various strategies for choosing the best action
        children = self.digraph.successors(root)

        # # Option 1: Choose the child with the highest 'n' value
        # num_visits = {}
        # for child_node in children:
        #     num_visits[child_node] = self.digraph.node[child_node]['n']
        # best_child = max(num_visits.items(), key=operator.itemgetter(1))[0]

        # Option 2: Choose the child with the highest UCT value
        uct_values = {}
        for child_node in children:
            uct_values[child_node] = self.uct(child_node)

        # Choose the child node that maximizes the expected value given by UCT
        # If more than one has the same UCT value then break ties randomly
        best_children = [key for key, val in uct_values.iteritems() if val == max(uct_values.values())]
        idx = np.random.randint(len(best_children))
        best_child = best_children[idx]

        # Determine which action leads to this child
        action = self.digraph.get_edge_data(root, best_child)['action']
        return action, best_child

    def selection(self, root):
        """
        Starting at root, recursively select the best node that maximizes UCT
        until a node is reached that has no explored children
        Keeps track of the path traversed by adding each node to path as
        it is visited
        :return: the node to expand
        """
        # In the case that the root node is not in the graph, add it
        if root not in self.digraph.nodes():
            self.digraph.add_node(self.node_counter,
                                  attr_dict={'w': 0,
                                             'n': 0,
                                             'uct': 0,
                                             'expanded': False,
                                             'state': root})
            self.node_counter += 1
            return root
        elif not self.digraph.node[root]['expanded']:
            print('root in digraph but not expanded')
            return root  # This is the node to expand
        else:
            print('root expanded, move on to a child')
            # Handle the general case
            children = self.digraph.successors(root)
            uct_values = {}
            for child_node in children:
                uct_values[child_node] = self.uct(state=child_node)

            # Choose the child node that maximizes the expected value given by UCT
            best_child_node = max(uct_values.items(), key=operator.itemgetter(1))[0]

            return self.selection(best_child_node)

    def expansion(self, node):
        # As long as this node has at least one unvisited child, choose a legal move
        children = self.digraph.successors(node)
        legal_moves = self.digraph.node[node]['state'].legal_moves()
        print('Legal moves: {}'.format(legal_moves))

        # Select the next unvisited child with uniform probability
        unvisited_children = []
        corresponding_actions = []
        print("legal moves: {}".format(legal_moves))
        for move in legal_moves:
            print('adding to expansion analysis with: {}'.format(move))
            child = self.digraph.node[node]['state'].transition_function(*move)

            in_children = False
            for child_node in children:
                if self.digraph.node[child_node]['state'] == child:
                    in_children = True

            if not in_children:
                unvisited_children.append(child)
                corresponding_actions.append(move)
        # Todo: why is it possible for there to be no unvisited children?
        print('unvisited children: {}'.format(len(unvisited_children)))
        if len(unvisited_children) > 0:
            idx = np.random.randint(len(unvisited_children))
            child, move = unvisited_children[idx], corresponding_actions[idx]

            self.digraph.add_node(self.node_counter,
                                  attr_dict={'w': 0,
                                             'n': 0,
                                             'uct': 0,
                                             'expanded': False,
                                             'state': child})
            self.digraph.add_edge(node, self.node_counter, attr_dict={'action': move})
            child_node_id = self.node_counter
            self.node_counter += 1
        else:
            # Todo:
            # Is this the correct behavior? The issue is, it was getting to the expansion
            # expansion method with nodes that were already expanded for an unknown reason,
            # so here we return the node that was passed. Maybe there is a case where a
            # node had been expanded but not yet marked as expanded until it got here.
            return node

        # If all legal moves are now children, mark this node as expanded.
        if len(children) + 1 == len(legal_moves):
            self.digraph.node[node]['expanded'] = True
            print('node is expanded')

        return child_node_id

    def simulation(self, node):
        """
        Conducts a light playout from the specified node
        :return: The reward obtained once a terminal state is reached
        """
        random_policy = RandomPolicy()
        current_state = self.digraph.node[node]['state']
        while not current_state.winner():
            move = random_policy.move(current_state)
            current_state = current_state.transition_function(*move)

        if current_state.winner() == self.player:
            return 1
        else:
            return 0

    def backpropagation(self, last_visited, reward):
        """
        Walk the path upwards to the root, incrementing the
        'n' and 'w' attributes of the nodes along the way
        """
        current = last_visited
        while True:
            self.digraph.node[current]['n'] += 1
            self.digraph.node[current]['w'] += reward

            print('Updating to n={} and w={}:\n{}'.format(self.digraph.node[current]['n'],
                                                          self.digraph.node[current]['w'],
                                                          self.digraph.node[current]['state']))

            # Terminate when we reach the empty board
            if self.digraph.node[current]['state'] == GameState():
                break
            # Todo:
            # Does this handle the necessary termination conditions for both 'X' and 'O'?
            # As far as we can tell, it does

            # Will throw an IndexError when we arrive at a node with no predecessors
            # Todo: see if this additional check is no longer necessary
            try:
                current = self.digraph.predecessors(current)[0]
            except IndexError:
                break

    def uct(self, state):
        """
        Returns the expected value of a state, calculated as a weighted sum of
        its exploitation value and exploration value
        """
        n = self.digraph.node[state]['n']  # Number of plays from this node
        w = self.digraph.node[state]['w']  # Number of wins from this node
        t = self.num_simulations
        c = self.uct_c
        epsilon = EPSILON

        exploitation_value = w / (n + epsilon)
        exploration_value = c * np.sqrt(np.log(t) / (n + epsilon))
        print('exploration_value: {}'.format(exploration_value))

        value = exploitation_value + exploration_value

        print('UCT value {:.3f} for state:\n{}'.format(value, state))

        self.digraph.node[state]['uct'] = value

        return value
