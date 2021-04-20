import numpy as np
from environments.base import HitStand
import pickle
from datetime import datetime
from os.path import curdir, join, abspath


class Agent:

    __TABLE_TYPES = ('v', 'q')
    __INIT_TYPES = ('random', 'null')
    __TABLES_Dir = '../tables/'
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

            self.time_steps_counter = np.zeros((self.environment.observation_space_high
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

            self.time_steps_counter = np.zeros((list(self.environment.observation_space_high -
                                                self.environment.observation_space_low + 1) +
                                                [self.environment.action_space_len]))

        self.hyperparams = {'discount_rate': 1, 'learning_rate': 1}

    def load_table(self):
        pass

    def save_table(self, episode, filename=None):
        if filename is None:
            filename = self.__TABLES_Dir + self.__TABLES_file + str(episode) +'_'+\
                       str(datetime.now().strftime('%Y%m%d_%H%M'))

        path = abspath(filename)
        with open(path, 'wb') as f:
            pickle.dump(self.table, f)

    def table_look_up(self, observation):
        observation = np.array(observation)
        table_indexes = observation - np.array(self.environment.observation_space_low)
        return tuple(table_indexes)

    @staticmethod
    def incremental_average(current_average, new_value, num_observations):
        return current_average + (1/num_observations) * (new_value - current_average)

    def set_hyperparams(self, **args):
        for k in args:
            if k not in self.hyperparams.keys():
                raise Exception('Param {0} not implemented. Current available are: {1}'.format(k, self.hyperparams.keys()))

            self.hyperparams[k] = args[k]

    def evaluate_state(self, *args):
        raise NotImplemented

    def follow_policy(self, *args):
        raise NotImplemented


class MonteCarloPredictor(Agent):

    __TABLES_file = 'MonteCarloPredictor_'

    def __init__(self, environment):
        super().__init__(environment,  table_type='v', table_init='null')
        self.current_episode_steps = {}

    def evaluate_state(self, observation, reward, terminal):
        table_look_up = self.table_look_up(observation)
        self.current_episode_steps[len(self.current_episode_steps)] = {'observation':table_look_up,
                                                                       'reward':reward
                                                                       }
        if terminal:
            self.update_table()
            self.current_episode_steps = {}

    def update_table(self):
        accum_discounted_reward = 0
        if len(self.current_episode_steps) == 1:
            self.time_steps_counter[self.current_episode_steps[0]['observation']] += 1
            self.table[self.current_episode_steps[0]['observation']] = self.incremental_average(
                self.table[self.current_episode_steps[0]['observation']],
                self.current_episode_steps[0]['reward'],
                self.time_steps_counter[self.current_episode_steps[0]['observation']])
        else:
            for time_step in range(len(self.current_episode_steps)-1, 0, -1):
                pass

    def follow_policy(self):
        action = np.random.randint(0,self.environment.action_space_len)
        return action


if __name__ == '__main__':

    env = HitStand()
    agent = MonteCarloPredictor(env)
    obs, _, _, _ = env.reset()



