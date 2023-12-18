from common.constants import CHECK, BET, CALL, FOLD, A, CHANCE, MAX_TURNS, INITIAL_ACTIONS, results_map
import random
from games.game_state_base import GameStateBase

class AbstractPokerRootChanceGameState(GameStateBase):

    def __init__(self, actions, report = False):
        super().__init__(parent = None, to_move = CHANCE, actions = actions)

        self.children = {
            cards: AbstractPokerPlayerMoveGameState(
                self, A, [],  cards, INITIAL_ACTIONS, report = report
            ) for cards in self.actions
        }
        self._chance_prob = 1. / len(self.children)

    def is_terminal(self):
        return False

    def inf_set(self):
        return "."

    def chance_prob(self):
        return self._chance_prob

    def sample_one(self):
        return random.choice(list(self.children.values()))

class AbstractPokerPlayerMoveGameState(GameStateBase):

    def __init__(self, parent, to_move, actions_history, cards, actions, report = False, turn = 1):
        super().__init__(parent = parent, to_move = to_move, actions = actions)

        self.actions_history = actions_history
        self.cards = cards
        self.turn = turn
        self.children = {
            a : AbstractPokerPlayerMoveGameState(
                parent = self,
                to_move = -to_move,
                actions_history = self.actions_history + [a],
                cards = cards,
                actions = self.__get_actions_in_next_round(a),
                report = report,
                turn = self.turn
            ) for a in self.actions
        }

        all_cards = self.cards.split('.')
        if self.to_move == A:
            public_card = all_cards[0]
        else:
            public_card = all_cards[1]

        _action_history = ".".join(self.actions_history)
            
        self._information_set = f".{public_card}.{_action_history}"

        self.report = report

    def __get_actions_in_next_round(self, a):
        first_action = (len(self.actions_history) == 0)
        final_turn = (self.turn == MAX_TURNS)

        if first_action:
            if a == CHECK:
                return [BET, CHECK]
            elif a == BET:
                return [CALL, FOLD]
            else:
                raise(Exception("Missing game state"))
        elif a == FOLD:
            return []
        elif a == BET:
            return [CALL, FOLD]
        elif self.actions_history[-1] != CHECK and a == CHECK:
            return [BET, CHECK]
        elif self.actions_history[-1] == CHECK and a == CHECK:
            if final_turn:
                return []
            elif self.turn < MAX_TURNS:
                self.turn += 1
                return INITIAL_ACTIONS
            else:
                raise(Exception("Missing game state"))
        elif self.actions_history[-1] == BET and a == CALL:
            if final_turn:
                return []
            elif self.turn < MAX_TURNS:
                self.turn += 1
                return INITIAL_ACTIONS
            else:
                raise(Exception("Missing game state"))
        else:
            raise(Exception("Missing game state"))


    def inf_set(self):
        return self._information_set

    def is_terminal(self):
        return self.actions == []

    def evaluation(self):
        if self.is_terminal() == False:
            raise RuntimeError("trying to evaluate non-terminal node")

        # Total pool is equal to number of times a bet was called plus one for the ante
        bet_pool = sum([1 for i in self.actions_history if i == CALL]) + 1

        if self.actions_history[-1] == FOLD:
            result = self.to_move * bet_pool

            if self.report:
                print(f"{self.actions_history}: {self.cards} and {result}")

            return result
        else:
            result = results_map(self.cards) * bet_pool

            if self.report:
                print(f"{self.actions_history}: {self.cards} and {result}")

            return result