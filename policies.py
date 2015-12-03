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

EPSILON = 10e-6  # Prevents division by 0 in calculation of UCT


class Policy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def move(self, state):
        pass


class RandomPolicy(Policy):
    def move(self, state):
        """Chooses moves randomly from the legal moves in a given state"""
        return random.choice(state.legal_moves())


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
        # Constant parameter to weight exploration vs. exploitation for UCT
        self.uct_c = np.sqrt(2)

        self.root = None

    def move(self, root):
        # Make a copy of the starting state so that the MCTS state can't be
        # modified later from the outside
        root = copy.deepcopy(root)
        self.root = root

        computational_budget = 25
        for i in range(computational_budget):
            print("Running MCTS from this starting state:\n{}".format(root))

            # Keep track of the path so that we can do backpropagation later
            path = nx.DiGraph()

            # Until computational budget runs out, run simulated trials
            # through the tree:

            # Selection: Recursively pick the best node that maximizes UCT
            # until reaching an unvisited node
            print('================ ( selection ) ================')
            selected_node = self.selection(self.root, path)
            print('selected:\n{}'.format(selected_node))

            # Check if the selected node is a terminal state, and if so, this
            # iteration is finished
            if selected_node.winner():
                break

            # Expansion: Add a child node where simulation will start
            print('================ ( expansion ) ================')
            new_child_node = self.expansion(selected_node)
            print('Node chosen for expansion:\n{}'.format(new_child_node))
            path.add_edge(selected_node, new_child_node)

            # Simulation: Conduct a light playout
            print('================ ( simulation ) ================')
            reward = self.simulation(new_child_node)
            print('Reward obtained: {}\n'.format(reward))

            # Backpropagation: Update the nodes on the path with the simulation results
            print('================ ( backpropagation ) ================')
            self.backpropagation(path, new_child_node, reward)

        move = self.best(root)
        print('MCTS complete. Suggesting move: {}\n'.format(move))
        return move

    def best(self, root):
        """
        Returns the action that results in the child with the most number of visits
        """
        # Todo: explore various strategies for choosing the best action
        children = self.digraph.successors(root)
        num_visits = {}
        for child_node in children:
            num_visits[child_node] = self.digraph.node[child_node]['n']

        # Choose the child node that maximizes the expected value given by UCT
        best_child = max(num_visits.items(), key=operator.itemgetter(1))[0]

        # Determine which action leads to this child
        action = self.digraph.get_edge_data(root, best_child)['action']
        return action

    def selection(self, root, path):
        """
        Starting at root, recursively select the best node that maximizes UCT
        until a node is reached that has no explored children
        Keeps track of the path traversed by adding each node to path as
        it is visited
        :return: the node to expand
        """
        # In the case that the root node is not in the graph, add it
        if root not in self.digraph.nodes():
            self.digraph.add_node(root, attr_dict={'w': 0, 'n': 0, 'expanded': False})
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
                uct_values[child_node] = self.uct(state=child_node, parent_state=root)

            # Choose the child node that maximizes the expected value given by UCT
            best_child_node = max(uct_values.items(), key=operator.itemgetter(1))[0]

            selected_node = best_child_node
            path.add_edge(root, selected_node)

            return self.selection(selected_node, path)

    def expansion(self, node):
        # As long as this node has at least one unvisited child, choose a legal move
        children = self.digraph.successors(node)
        legal_moves = node.legal_moves()
        print('Legal moves: {}'.format(legal_moves))

        # Select the next unvisited child with uniform probability
        unvisited_children = []
        corresponding_actions = []
        for move in legal_moves:
            child = node.transition_function(*move)
            if child not in children:
                unvisited_children.append(child)
                corresponding_actions.append(move)
        # Todo: why is it possible for there to be no unvisited children?
        if len(unvisited_children) > 0:
            idx = np.random.randint(len(unvisited_children))
            child, move = unvisited_children[idx], corresponding_actions[idx]

            self.digraph.add_node(child, attr_dict={'w': 0, 'n': 0, 'expanded': False})
            self.digraph.add_edge(node, child, attr_dict={'action': move})

        # If all legal moves are now children, mark this node as expanded.
        if len(children) + 1 == len(legal_moves):
            self.digraph.node[node]['expanded'] = True

        return child

    def simulation(self, node):
        """
        Conducts a light playout from the specified node
        :return: The reward obtained once a terminal state is reached
        """
        random_policy = RandomPolicy()
        while not node.winner():
            move = random_policy.move(node)
            node = node.transition_function(*move)

        if node.winner() == self.player:
            return 1
        else:
            return 0

    def backpropagation(self, path, last_visited, reward):
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
                                                          current))

            # Will throw an IndexError when we arrive at the root of the path
            try:
                current = path.predecessors(current)[0]
            except IndexError:
                break

    def uct(self, state, parent_state):
        """
        Returns the expected value of a state, calculated as a weighted sum of
        its exploitation value and exploration value
        """
        n = self.digraph.node[state]['n']  # Number of plays from this node
        w = self.digraph.node[state]['w']  # Number of wins from this node
        t = self.digraph.node[parent_state]['n']  # Total number of plays from parent node
        c = self.uct_c
        epsilon = EPSILON

        exploitation_value = w / (n + epsilon)
        exploration_value = c * np.sqrt(np.log(t) / (n + epsilon))

        value = exploitation_value + exploration_value

        print('UCT value {:.3f} for state:\n{}'.format(value, state))

        return value
