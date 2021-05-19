from games.blackjacks import Blackjack
import numpy as np


class ResetEnvironmentError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class BaseEnvironment:

    def __init__(self):
        self.is_discrete = True

    def reset(self):
        pass

    def step(self, action):
        pass

    def render(self):
        pass

    def close(self):
        pass

    def seed(self):
        pass


class HitStand(BaseEnvironment):

    __NAME = 'Jack'
    __NUM_PLAYERS = 1
    __NUM_DECKS = 6
    __INITIAL_CASH = 10_000
    __ALLOW_INDEBTNESS = True
    __PLAYERS_BET = 1

    def __init__(self):
        super().__init__()

        self.action_space = np.array([0, 1])
        self.action_space_description = {0: 'stand',
                                         1: 'hit'
                                         }
        self.action_space_len = len(self.action_space)

        self.reward_space = np.array([-1, 0, 1, 1.5])
        self.reward_space_description = {-1: 'The House beats {0}'.format(self.__NAME),
                                           0: 'Draw/not terminal',
                                           1: '{0} beats the House'.format(self.__NAME),
                                          1.5: 'Blackjack for {0}'.format(self.__NAME)
                                          }
        self.rewards_space_len = len(self.reward_space)

        self.observation_space_len = 3
        self.observation_space_description = {0: "Player's total",
                                              1: "Dealer's card value",
                                              2: "Player has got usable ace"
                                              }
        self.observation_space_low = np.array([4, 2, 0])
        self.observation_space_high = np.array([30, 26, 1])

        self.__game_instance = None
        self.verbose = False
        self.current_state = []

    def __conditional_decorator(func):
        def wrapper(self,*args):
            values = func(self, *args)
            if self.verbose:
                if self.current_state[0]:
                    print('{}:'.format(self.__NAME))
                    print('\t-Cards: {0}'.format(self.current_state[3][0]))
                    print('\t-Value : {0}'.format(self.current_state[1][0]))
                    print('Dealer:')
                    print('\t-Cards: {0}'.format(self.current_state[3][1]))
                    print('\t-Value : {0}'.format(self.current_state[1][1]))

                else:
                    print('{0} decides to: {1}'.format(self.__NAME, self.current_state[5].upper()))
                    print('\t-Cards: {0}'.format(self.current_state[3][0]))
                    print('\t-Value : {0}'.format(self.current_state[1][0]))

                if self.current_state[2]:
                    print('Dealer:')
                    print('\t-Cards: {0}'.format(self.current_state[3][1]))
                    print('\t-Value : {0}'.format(self.current_state[1][1]))
                    print(self.current_state[4].upper())
                    self.verbose = False

            self.current_state = []
            return values
        return wrapper

    @__conditional_decorator
    def reset(self):
        self.__game_instance = Blackjack(self.__NUM_DECKS, self.__NUM_PLAYERS)
        self.__game_instance.setup_players([{'name': self.__NAME,
                                             'initial_cash': self.__INITIAL_CASH,
                                             'allow_debt': self.__ALLOW_INDEBTNESS
                                             }
                                            ])
        self.__game_instance.start()
        self.__game_instance.alive_players[0].place_bet(self.__PLAYERS_BET)
        self.__game_instance.start_round()

        observation = self.__game_instance.alive_players[0].current_hand.best_value,\
                      self.__game_instance.croupier_hand.best_value,\
                      int(self.__game_instance.alive_players[0].current_hand.is_soft)
        done = len(self.__game_instance.retrieve_hands_alive()) == 0
        info = self.__game_instance.players[0].current_hand.card_names, self.__game_instance.croupier_hand.card_names
        message = None
        if not done:
            reward = 0
        else:
            if self.__game_instance.croupier_hand.best_value > 9:
                self.__game_instance.get_croupier_hand()

            observation = self.__game_instance.alive_players[0].current_hand.best_value, \
            max(self.__game_instance.croupier_hand.card_values[0])\
                if isinstance(self.__game_instance.croupier_hand.card_values[0], list) else self.__game_instance.croupier_hand.card_values[0], \
            int(self.__game_instance.alive_players[0].current_hand.is_soft)

            message = self.__game_instance.resolve_round(self.__game_instance.players[0])
            reward = self.__game_instance.players[0].gains

        self.current_state.extend((True, observation, done, info, message))

        return observation, reward, done, info

    @__conditional_decorator
    def step(self, action:int):
        if self.__game_instance:
            self.__game_instance.send_action(self.__game_instance.alive_players[0],self.action_space_description[action])

            observation = self.__game_instance.players[0].current_hand.best_value,\
                          self.__game_instance.croupier_hand.best_value, \
                          int(self.__game_instance.players[0].current_hand.is_soft)
            done = len(self.__game_instance.retrieve_hands_alive())==0
            info = self.__game_instance.players[
                       0].current_hand.card_names, self.__game_instance.croupier_hand.card_names
            message = None
            if not done:
                reward = 0
            else:
                if not self.__game_instance.alive_players[0].current_hand.is_busted:
                    self.__game_instance.get_croupier_hand()

                observation = self.__game_instance.alive_players[0].current_hand.best_value,\
                              self.__game_instance.croupier_hand.best_value,\
                              int(self.__game_instance.alive_players[0].current_hand.is_soft)
                message = self.__game_instance.resolve_round(self.__game_instance.players[0])
                reward = self.__game_instance.players[0].gains

            self.current_state.extend((False, observation, done, info, message, self.action_space_description[action]))

            return observation, reward, done, info

        raise ResetEnvironmentError('Reset environment before sending any action!')

    def render(self):
        self.verbose = True

    def __str__(self):
        description = '1. 6 decks (with replacement after each episode)\n' \
                      '2. Dealer stands on soft 17\n' \
                      '3. No Double Down\n' \
                      '4. No split\n' \
                      '5. No insurance offered\n' \
                      '6. No surrender\n' \
                      '7. Natural Blackjack 3:2' \

        return description





