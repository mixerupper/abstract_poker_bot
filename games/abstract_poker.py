from common.constants import *
import random
from games.game_state_base import GameStateBase

class AbstractPokerRootChanceGameState(GameStateBase):

    def __init__(self, max_hand_strength, max_turns = 2, report = False):
        self.max_hand_strength = max_hand_strength
        self.max_turns = max_turns
        actions = card_dealing(max_hand_strength)

        super().__init__(parent = None, to_move = CHANCE, actions = actions)

        self.children = {
            cards: AbstractPokerPlayerMoveGameState(
                parent = self, 
                to_move = 1, 
                actions_history = [], 
                cards = cards, 
                actions = INITIAL_ACTIONS, 
                turn = 1,
                max_turns = self.max_turns,
                report = report
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

    def __init__(self, parent, to_move, actions_history, cards, actions, turn, max_turns, report = False):
        super().__init__(parent = parent, to_move = to_move, actions = actions)

        self.actions_history = actions_history
        self.cards = cards
        self.turn = turn
        self.max_turns = max_turns
        

        next_actions_and_turns = {a:self.__get_actions_and_turn_in_next_round(a) for a in self.actions}

        self.children = {
            a : AbstractPokerPlayerMoveGameState(
                parent = self,
                to_move = next_actions_and_turns[a]['next_to_move'],
                actions_history = self.actions_history + [a],
                cards = cards,
                actions = next_actions_and_turns[a]['next_actions'],
                turn = next_actions_and_turns[a]['next_turn'],
                max_turns = self.max_turns,
                report = report
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

    def __get_actions_and_turn_in_next_round(self, a):
        final_turn = (self.turn == self.max_turns)
        next_turn = self.turn
        next_to_move = self.to_move * -1
        assert (self.turn <= self.max_turns)&(self.turn >= 0)

        if a == FOLD:
            next_actions =  []
        elif a == BET:
            next_actions =  [CALL, FOLD]
        elif a == CHECK_INITIATE:
            next_actions = [BET, CHECK_RESPONSE]
        elif a == CALL:
            if final_turn:
                next_actions =  []
            else:
                next_turn += 1
                # check that self.turn won't change not pass by references
                next_actions =  INITIAL_ACTIONS

                # reset next to move back to player 1
                next_to_move = 1
        elif a == CHECK_RESPONSE:
            if final_turn:
                next_actions =  []
            else:
                next_turn += 1
                # check that self.turn won't change not pass by references
                next_actions =  INITIAL_ACTIONS

                # reset next to move back to player 1
                next_to_move = 1
        else:
            raise(Exception("Missing action type"))

        result_df = {'next_actions':next_actions, 
                'next_turn':next_turn, 
                'next_to_move':next_to_move}

        return result_df


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