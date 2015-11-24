"""
Game play policies can be defined here.
"""
import random


def random_policy(state):
    """Chooses moves randomly from the legal moves in a given state"""
    return random.choice(state.legal_moves())
