from common.constants import CHECK_INITIATE, CHECK_RESPONSE, BET, CALL, FOLD, A, CHANCE, MAX_TURNS, INITIAL_ACTIONS, results_map
from math import comb
import random
import numpy as np

class CompetitionAbstractPoker():

    def __init__(self, player1, player2, max_turns, ante = 1, report = False):
        self.player1 = player1
        self.player2 = player2

        self.players = [player1, player2]

        self.max_turns = max_turns
        self.ante = ante

        # Constants
        self.num_players = 2
        self.max_hand_strength = comb(52,2)
        self.results = [0 for i in range(self.num_players)]

        self.report = report

    def compete(self, rounds):
        result = 0
        for i in range(rounds):
            result += self.single_round(order = 1)
            # if i%2 == 0:
            #     result += self.single_round(order = 1)
            # else:
            #     result += self.single_round(order = -1)

        return result/rounds

    def single_round(self, order):
        # Initialize and deal cards
        player_granularity = {p:p.root.max_hand_strength
                              for p in self.players}
        player_depth = {p:p.root.max_turns
                              for p in self.players}
        hand_strength = {p:np.random.choice(np.arange(self.max_hand_strength)) + 1
                         for p in self.players}
        converted_hand_strength = {p:int(np.ceil(hand_strength[p]/self.max_hand_strength * player_granularity[p]))
                                   for p in self.players}
        hands_str = ".".join([str(int(hand_strength[p])) for p in self.players])
        action_log = []
        new_turn = True

        if order == 1:
            ix_active_player = 0
        elif order == -1:
            ix_active_player = 1
        else:
            raise(NotImplementedError("Order is only implemented for 2P games."))

        # loop players playing their strategies until a player has empty action set
        # put large number and break out
        while True:
            # Get active action distribution
            active_player = self.players[ix_active_player]
            active_converted_hand_strength = converted_hand_strength[active_player]
            active_player_depth = player_depth[active_player]

            # Create relevant action log
            if new_turn:
                action_log.append([])
                new_turn = False

            # If more than max turns, stop the loop
            if len(action_log) > self.max_turns:
                break

            if action_log != []:
                relevant_action_log = np.concatenate(action_log[-active_player_depth:])
            else:
                relevant_action_log = action_log

            # Get active action distribution
            active_info_set = f'.{active_converted_hand_strength}.{".".join(relevant_action_log)}'
            active_action_distribution = active_player.nash_equilibrium[active_info_set]

            if active_action_distribution == {}:
                if self.report:
                    print("Round over")
                break
            
            # Based on action distribution, choose an action
            possible_actions = list(active_action_distribution.keys())
            action_probs = [active_action_distribution[a] for a in possible_actions]
            action = np.random.choice(possible_actions, p = action_probs)

            

            


            action_log[-1].append(action)

            # Update turn count
            just_played_ix = ix_active_player
            if action == FOLD:
                break
            if action in [CHECK_RESPONSE, CALL]:
                # new turn
                ix_active_player = 0
                new_turn = True
            else:
                ix_active_player = (ix_active_player + 1)%2

            # Report
            if self.report:
                s0 = "-------------------------------------------------------------------"
                s1 = (f"Player {just_played_ix} with card {hand_strength[active_player]}"
                      f" and self-estimated strength {active_converted_hand_strength}/{player_granularity[active_player]}.")
                s2 = (f"Action distribution was {active_action_distribution}. "
                      f"Player chose {action}.")
                s3 = (f"Information set is {active_info_set}")
                s4 = (f"Current turn log is {action_log[-1]}. "
                       f"Current action log is {action_log}.")
                print(s0, s1, s3, s2, s4,sep = "\n")
                       

        # pass the round log into the evaluate_round function to return payoffs for each player
        action_log = np.concatenate(action_log)
        result = self.evaluate_round(action_log, hands_str, just_played_ix)
        # check that the payoffs are the negative of each other (sum to zero)

        return result

    def evaluate_round(self, action_log, hands, last_player_to_move):
        # bet pool is number of calls plus ante of 1
        bet_pool = self.ante

        for i in range(len(action_log)):
            if action_log[i] == CALL:
                if action_log[i-1] == BET:
                    bet_pool += 1
                elif action_log[i-1] == RAISE:
                    bet_pool += 2
                else:
                    raise(NotImplementedError("Call but not in response to bet or raise."))

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

        else:
            result = results_map(hands) * bet_pool

            if self.report:
                print(f"{action_log}: {hands} and {result}")

        return result