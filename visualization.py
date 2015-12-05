"""
Visualizes game trees to a selected depth with node value estimate annotations.

Requires the NetworkX graph package and GraphViz, which are included in Anaconda
"""
import networkx as nx
from gamestate import GameState


def visualize_mcts_tree(mcts, depth, filename):
    """
    Creates a small subgraph for visualization with a
    number of levels equal to 2 + depth labelled with the
    MCTS values from mcts and saves it as filename.png
    """
    root = GameState()
    subgraph = nx.DiGraph()

    # Don't include the empty board (the root) in the graphs
    for first_move in mcts.digraph.successors(root):
        add_edges(mcts.digraph, subgraph, first_move, depth)

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
    dot_graph.write_png('{}.png'.format(filename))


def add_edges(graph, subgraph, parent, depth):
    for child in graph.successors(parent):
        if depth:
            add_edges(graph, subgraph, child, depth - 1)

        subgraph.add_node(parent)
        subgraph.add_node(child)
        for node in [parent, child]:
            subgraph.node[node]['n'] = graph.node[node]['n']
            subgraph.node[node]['w'] = graph.node[node]['w']
        subgraph.add_edge(parent, child)
