"""
Game play policies can be defined here. Policies should inherit from the
abstract class Policy.
"""
from abc import ABCMeta, abstractmethod
import random


class Policy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def move(self, state):
        pass


class RandomPolicy(Policy):
    def move(self, state):
        """Chooses moves randomly from the legal moves in a given state"""
        return random.choice(state.legal_moves())
