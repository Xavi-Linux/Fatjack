import numpy as np
from environments.base import HitStand
import pickle
from datetime import datetime
from pathlib import Path
from os.path import getctime


def folderpath_search(origin:Path, sought_folder:str)->Path:
    for element in origin.iterdir():
        if element.is_dir():
            if element.name == sought_folder:
                return Path(element)

    return folderpath_search(origin.parent, sought_folder)


class Agent:

    __TABLE_TYPES = ('v', 'q')
    __INIT_TYPES = ('random', 'null')
    __Tables = 'tables'
    __TABLES_Dir = folderpath_search(Path.cwd(), __Tables)

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
        self.save_at_episodes = []
        self.current_table_path = ''

    def load_table(self, episode=None, overwrite=False, most_recent=True, filename=None):
        if filename is None:
            if most_recent:
                criteria = self.__class__.__name__ + '_*'
            else:
                if episode:
                    criteria = self.__class__.__name__ + '_' + str(episode) + '_*'
                else:
                    raise Exception('Episode number must be specified when most_recent is False')
            try:
                path = sorted(self.__TABLES_Dir.glob(criteria), key=getctime, reverse=True)[0]

            except IndexError:
                raise Exception('No file found by following the desired criteria')

        else:
            path = self.__TABLES_Dir.joinpath(filename)

        with open(path, 'rb') as f:
            table = pickle.load(f)

        if overwrite:
            self.table = table
            self.current_table_path = path
        else:
            return table

    def save_table(self, episode, filename=None):
        if filename is None:
            path = self.__TABLES_Dir.joinpath(self.__class__.__name__ + '_' + str(episode) +'_'+
                                              str(datetime.now().strftime('%Y%m%d_%H%M')))
        else:
            path = self.__TABLES_Dir.joinpath(filename)

        with open(path, 'wb') as f:
            pickle.dump(self.table, f)

        self.save_at_episodes.append(episode)

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

    def list_saved_tables(self):
        return list(map(str, self.__TABLES_Dir.glob(self.__class__.__name__ + '_*')))


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
            for time_step in range(len(self.current_episode_steps)-2, -1, -1):
                reward = self.current_episode_steps[time_step + 1]['reward'] + self.hyperparams['discount_rate'] * accum_discounted_reward
                self.time_steps_counter[self.current_episode_steps[time_step]['observation']] += 1
                self.table[self.current_episode_steps[time_step]['observation']] = self.incremental_average(
                    self.table[self.current_episode_steps[time_step]['observation']],
                    reward,
                    self.time_steps_counter[self.current_episode_steps[time_step]['observation']])

                accum_discounted_reward = reward


if __name__ == '__main__':

    env = HitStand()
    agent = MonteCarloPredictor(env)
    tab = agent.load_table(most_recent=True, overwrite=False)
    print(agent.list_saved_tables())


