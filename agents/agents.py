import numpy as np
from environments.base import HitStand
import pickle
import time


class Agent:

    __TABLE_TYPES = ('v', 'q')
    __INIT_TYPES = ('random', 'null')
    __TABLES_Dir = 'tables'
    __TABLES_file = 'BaseAgent_'

    def __init__(self, environment, table_type='v', table_init='random'):
        self.environment = environment
        if table_type not in self.__TABLE_TYPES:
            raise Exception('Invalid table type')

        if table_init not in self.__INIT_TYPES:
            raise Exception('Invalid table initializer')

        if table_type == 'v':
            if table_init == 'random':
                self.table = np.random.random(size=(self.environment.observation_space_high
                                                    - self.environment.observation_space_low + 1))
            else:
                self.table = np.zeros((self.environment.observation_space_high
                                       - self.environment.observation_space_low + 1))
        elif table_type == 'q':
            if table_init == 'random':
                self.table = np.random.random(size=(list(self.environment.observation_space_high
                                                    - self.environment.observation_space_low + 1) +
                                                    [self.environment.action_space_len]))
            else:
                self.table = np.zeros((list(self.environment.observation_space_high -
                                       self.environment.observation_space_low + 1) +
                                       [self.environment.action_space_len]))

    def load_table(self):
        pass

    def save_table(self, filename=None):
        if filename is None:
            pass


if __name__ == '__main__':

    env = HitStand()
    agent = Agent(env, table_type='q', table_init='null')
    matrix = np.random.random(size=(env.observation_space_high - env.observation_space_low + 1))
    print(agent.table[26,24])
