from common.constants import CHECK_INITIATE, CHECK_RESPONSE, BET, CALL, FOLD, A, CHANCE, MAX_TURNS, INITIAL_ACTIONS, results_map
from math import comb
import random
import numpy as np

class CompetitionAbstractPoker():

    def __init__(self, player1, player2, report = False):
        self.player1 = player1
        self.player2 = player2

        self.players = [player1, player2]

        # Constants
        self.num_players = 2
        self.max_hand_strength = comb(52,2)
        self.results = [0 for i in range(self.num_players)]

        self.report = report

    def compete(self, rounds):
        result = 0
        for i in range(rounds):
            if i%2 == 0:
                result += self.single_round(order = 1)
            else:
                result += self.single_round(order = -1)

        return result

    def single_round(self, order):
        # Initialize and deal cards
        player_granularity = {p:p.root.max_hand_strength 
                              for p in self.players}
        hand_strength = {p:np.random.choice(np.arange(self.max_hand_strength)) + 1 
                         for p in self.players}
        converted_hand_strength = {p:int(np.ceil(hand_strength[p]/self.max_hand_strength * player_granularity[p])) 
                                   for p in self.players}
        hands_str = ".".join([str(int(hand_strength[p])) for p in self.players])
        action_log = []

        if order == 1:
            ix_active_player = 0
        elif order == -1:
            ix_active_player = 1
        else:
            raise(NotImplementedError("Order is only implemented for 2P games."))        

        # loop players playing their strategies until a player has empty action set
        # put large number and break out
        for i in range(100):
            # Get active action distribution
            active_player = self.players[ix_active_player]
            active_converted_hand_strength = converted_hand_strength[active_player]
            active_info_set = f'.{active_converted_hand_strength}.{".".join(action_log)}'
            active_action_distribution = active_player.nash_equilibrium[active_info_set]

            if active_action_distribution == {}:
                if self.report:
                    print("Round over")
                break
            
            # Based on action distribution, choose an action
            possible_actions = list(active_action_distribution.keys())
            action_probs = [active_action_distribution[a] for a in possible_actions]
            action = np.random.choice(possible_actions, p = action_probs)

            just_played_ix = ix_active_player
            if action in [CHECK_RESPONSE, CALL, FOLD]:
                ix_active_player = 0
            else:
                ix_active_player = (ix_active_player + 1)%2

            # Add action to the action log
            action_log.append(action)

            # Report
            if self.report:
                print((f"Player {just_played_ix} with card {hand_strength[active_player]} "
                       f"and self-estimated strength {active_converted_hand_strength} "
                       f"chose {action}. "
                       f"Current action log is {action_log}"))

        # pass the round log into the evaluate_round function to return payoffs for each player
        result = self.evaluate_round(action_log, hands_str, just_played_ix)
        # check that the payoffs are the negative of each other (sum to zero)

        return result

    def evaluate_round(self, action_log, hands, last_player_to_move):
        # bet pool is number of calls plus ante of 1
        bet_pool = sum([1 for i in action_log if i == CALL]) + 1
        last_to_move = None

        if last_player_to_move == 0:
            result_multiplier = 1
        elif last_player_to_move == 1:
            result_multiplier = -1
        else:
            raise(NotImplementedError("Evaluation only implemented for two players"))

        if action_log[-1] == FOLD:
            result = -result_multiplier * bet_pool

            if self.report:
                print(f"{action_log}: {hands} and {result}")

            return result
        else:
            result = results_map(hands) * bet_pool

            if self.report:
                print(f"{action_log}: {hands} and {result}")

            return result