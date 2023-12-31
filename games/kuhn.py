from common.constants import CHECK, BET, CALL, FOLD, A, CHANCE, RESULTS_MAP
import random
from games.game_state_base import GameStateBase

class KuhnRootChanceGameState(GameStateBase):

    def __init__(self, actions, report = False):
        super().__init__(parent = None, to_move = CHANCE, actions = actions)
        self.children = {
            cards: KuhnPlayerMoveGameState(
                self, A, [],  cards, [BET, CHECK], report
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

class KuhnPlayerMoveGameState(GameStateBase):

    def __init__(self, parent, to_move, actions_history, cards, actions, report = False):
        super().__init__(parent = parent, to_move = to_move, actions = actions)

        self.actions_history = actions_history
        self.cards = cards
        self.children = {
            a : KuhnPlayerMoveGameState(
                self,
                -to_move,
                self.actions_history + [a],
                cards,
                self.__get_actions_in_next_round(a),
                report
            ) for a in self.actions
        }

        public_card = self.cards[0] if self.to_move == A else self.cards[1]
        self._information_set = ".{0}.{1}".format(public_card, ".".join(self.actions_history))

        self.report = report

    def __get_actions_in_next_round(self, a):
        if len(self.actions_history) == 0 and a == BET:
            return [FOLD, CALL]
        elif len(self.actions_history) == 0 and a == CHECK:
            return [BET, CHECK]
        elif self.actions_history[-1] == CHECK and a == BET:
            return [CALL, FOLD]
        elif a == CALL or a == FOLD or (self.actions_history[-1] == CHECK and a == CHECK):
            return []

    def inf_set(self):
        return self._information_set

    def is_terminal(self):
        return self.actions == []

    def evaluation(self):
        if self.is_terminal() == False:
            raise RuntimeError("trying to evaluate non-terminal node")

        if self.actions_history[-1] == CHECK and self.actions_history[-2] == CHECK:
            result = RESULTS_MAP[self.cards] * 1

            if self.report:
                print(f"{self.actions_history}: {self.cards} and {result}")

            return result # only ante is won/lost

        if self.actions_history[-2] == BET and self.actions_history[-1] == CALL:
            result = RESULTS_MAP[self.cards] * 2

            if self.report:
                print(f"{self.actions_history}: {self.cards} and {result}")

            return result

        if self.actions_history[-2] == BET and self.actions_history[-1] == FOLD:
            result = self.to_move * 1

            if self.report:
                print(f"{self.actions_history}: {self.cards} and {result}")

            return result
