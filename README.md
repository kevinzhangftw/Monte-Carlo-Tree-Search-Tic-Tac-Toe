# Monte-Carlo Tree Search implementation for Tic Tac Toe

## Core files
- **gamestate.py** Defines a Tic Tac Toe game state object with an associated transition function, a legal moves function, a move function, and a terminal state detector. Includes unit tests to verify proper functionality.
- **gameplay.py** Function to play a game given a policy for each player and keep track of the game as a NetworkX game tree.
- **policies.py** Game play policies can be defined here.

## Example files
**example_figures.py** Generates sample figures visualizing game trees.

First, it generates one [game graph](game_graph.png).

Then, it plays multiple games, and [composes their graphs](multiple_game_graph.png):

![](multiple_game_graph.png)

## Requirements
Requires NetworkX and GraphViz, which are included in the free [Anaconda](https://www.continuum.io/downloads) Python distribution or can be installed separately.
