from games.blackjacks import Blackjack
import numpy as np


class ResetEnvironmentError(BaseException):

    def __init__(self, text):
        super().__init__(text)


class BaseEnvironment:

    def __init__(self):
        pass

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
    __NUM_DECKS = 8
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

        self.rewards_space = np.array([-1, 0, 1, 1.5])
        self.rewards_space_description = {-1: 'The House beats {0}'.format(self.__NAME),
                                           0: 'Draw/not terminal',
                                           1: '{0} beats the House'.format(self.__NAME),
                                          1.5: 'Blackjack for {0}'.format(self.__NAME)
                                          }

        self.__game_instance = None
        self.verbose = False
        self.current_state = None

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
                      self.__game_instance.croupier_hand.best_value
        done = len(self.__game_instance.retrieve_hands_alive()) == 0
        info = self.__game_instance.players[0].current_hand.card_names, self.__game_instance.croupier_hand.card_names
        if not done:
            reward = 0
        else:
            if self.__game_instance.croupier_hand.best_value > 9:
                self.__game_instance.get_croupier_hand()

            observation = self.__game_instance.alive_players[0].current_hand.best_value, \
                          self.__game_instance.croupier_hand.best_value
            self.__game_instance.resolve_round(self.__game_instance.players[0])
            reward = self.__game_instance.players[0].gains

        return observation, reward, done, info

    def step(self, action:int):
        if self.__game_instance:
            self.__game_instance.send_action(self.__game_instance.alive_players[0],self.action_space_description[action])

            observation = self.__game_instance.players[0].current_hand.best_value,\
                          self.__game_instance.croupier_hand.best_value
            done = len(self.__game_instance.retrieve_hands_alive())==0
            info = self.__game_instance.players[
                       0].current_hand.card_names, self.__game_instance.croupier_hand.card_names
            if not done:
                reward = 0
            else:
                if not self.__game_instance.alive_players[0].current_hand.is_busted:
                    self.__game_instance.get_croupier_hand()

                observation = self.__game_instance.alive_players[0].current_hand.best_value,\
                              self.__game_instance.croupier_hand.best_value
                self.__game_instance.resolve_round(self.__game_instance.players[0])
                reward = self.__game_instance.players[0].gains

            return observation, reward, done, info

        raise ResetEnvironmentError('Reset environment before sending any action!')

    def render(self):
        self.verbose = True

    def conditional_decorator(self):
        pass


if __name__ == '__main__':

    env = HitStand()
    for i in range(10_0000):
        state, r, terminal, state_info = env.reset()
        print('EPISODE {}:'.format(i+1), '\n')
        print('initial state: {0}, {1}, {2}, {3}'.format(state, r, terminal, state_info), '\n')
        j=0
        while not terminal:
            action = 0 if np.random.uniform() < .5 else 1
            print(action)
            state, r, terminal, state_info = env.step(action)
            print('--> step {4}: {0}, {1}, {2}, {3}'.format(state, r, terminal, state_info, j+1), '\n')
        print('-------------','\n')



