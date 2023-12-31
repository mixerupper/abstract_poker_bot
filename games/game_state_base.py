from common.constants import CHECK_INITIATE, CHECK_RESPONSE, BET, CALL, FOLD, A, CHANCE, results_map
import random


class GameStateBase:
    def __init__(self, parent, to_move, actions):
        self.parent = parent
        self.to_move = to_move
        self.actions = actions

    def play(self, action):
        return self.children[action]

    def is_chance(self):
        return self.to_move == CHANCE

    def inf_set(self):
        raise NotImplementedError("Please implement information_set method")