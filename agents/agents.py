import numpy as np

import environments
from environments.base import HitStand
import pickle
from pathlib import Path
from os.path import getctime
from uuid import uuid4
from dill import dump, load


def folderpath_search(origin:Path, sought_folder:str)->Path:
    for element in origin.iterdir():
        if element.is_dir():
            if element.name == sought_folder:
                return Path(element)

    return folderpath_search(origin.parent, sought_folder)


def list_saved_agents() -> list:
    folder = folderpath_search(Path.cwd(), 'stored_agents')
    return list(map(str,folder.iterdir()))


def get_agent(filename:str, dilling=True):
    with open(filename, 'rb') as f:
        if dilling:
            agent = load(f)
        else:
            agent = pickle.load(f)

    return agent


class Agent:

    __TABLE_TYPES = ('v', 'q')
    __INIT_TYPES = ('random', 'null')
    __TABLES_Dir = folderpath_search(Path.cwd(), 'tables')
    __AGENTS_Dir = folderpath_search(Path.cwd(), 'stored_agents')

    def __init__(self, environment, table_type='v', table_init='random'):
        self.id = uuid4().hex
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

        self.table_type= table_type
        self.hyperparams = {'discount_rate': 1,
                            'learning_rate': None}
        self.save_at_episodes = []
        self.current_table_path = ''
        self.num_executed_episodes = 0
        self.current_episode_steps = {}

    def load_table(self, episode=None, overwrite=False, filename=None):
        if filename is None:
            if episode:
                criteria = 'T_' + self.id + '_' + str(episode)
            else:
                criteria = 'T_' + self.id + '_*'

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

    def save_table(self, filename=None):
        episode = self.num_executed_episodes
        if filename is None:
            path = self.__TABLES_Dir.joinpath('T_' + self.id + '_' + str(episode))

        else:
            path = self.__TABLES_Dir.joinpath(filename)

        with open(path, 'wb') as f:
            pickle.dump(self.table, f)

        self.save_at_episodes.append(episode)

    def table_look_up(self, observation):
        observation = np.array(observation)
        table_indexes = observation - np.array(self.environment.observation_space_low)
        return list(table_indexes)

    def incremental_average(self, current_average, new_value, num_observations):
        if self.hyperparams['learning_rate']:
            return current_average + self.hyperparams['learning_rate'] * (new_value - current_average)
        else:
            return current_average + (1/num_observations) * (new_value - current_average)

    def set_hyperparams(self, **args):
        for k in args:
            if k not in self.hyperparams.keys():
                raise Exception('Param {0} not implemented. Current available are: {1}'.format(k, self.hyperparams.keys()))

            self.hyperparams[k] = args[k]

    def evaluate_state(self, *args):
        raise NotImplementedError

    def follow_policy(self, *args):
        raise NotImplementedError

    def list_saved_tables(self):
        return list(map(str, sorted(self.__TABLES_Dir.glob('T_' + self.id + '_*'),key=getctime)))

    def save(self, episode, dilling=True):
        path = self.__AGENTS_Dir.joinpath('A_' + self.__class__.__name__ + '_' + str(self.id) + '_' + str(episode))
        with open(path, 'wb') as f:
            if dilling:
                dump(self, f)
            else:
                pickle.dump(self, f)

    def get_parent_class_str(self):
        return self.__class__.__bases__[0].__name__


class MonteCarloPredictor(Agent):

    __TABLES_file = 'MonteCarloPredictor_'

    def __init__(self, environment, table_type='v'):
        super().__init__(environment,  table_type=table_type, table_init='null')

    def evaluate_state(self, observation, reward, terminal, action):
        table_look_up = self.table_look_up(observation)
        if self.table_type == 'q':
            table_look_up = table_look_up + [action]

        self.current_episode_steps[len(self.current_episode_steps)] = {'observation': tuple(table_look_up),
                                                                       'reward':reward
                                                                       }
        if terminal:
            self.update_table()
            self.current_episode_steps = {}
            self.num_executed_episodes +=1

    def update_table(self):
        accum_discounted_reward = 0
        for time_step in range(len(self.current_episode_steps)-1, -1, -1):
            reward = self.current_episode_steps[time_step]['reward'] + self.hyperparams['discount_rate'] * accum_discounted_reward
            self.time_steps_counter[self.current_episode_steps[time_step]['observation']] += 1
            self.table[self.current_episode_steps[time_step]['observation']] = self.incremental_average(
                                                                                   self.table[self.current_episode_steps[time_step]['observation']],
                                                                                   reward,
                                                                                   self.time_steps_counter[self.current_episode_steps[time_step]['observation']])

            accum_discounted_reward = reward


class MontecarloController(MonteCarloPredictor):

    __TABLES_file = 'MonteCarloController_'

    def __init__(self, environment):
        super().__init__(environment, table_type='q')
        self.hyperparams['epsilon_start'] = 1
        self.hyperparams['epsilon_min'] = 0.05
        self.hyperparams['epsilon_decay'] = 0.995


class QLearning(Agent):

    __TABLES_file = 'QLearning_'

    def __init__(self, environment):
        super().__init__(environment,  table_type='q', table_init='null')
        self.hyperparams['epsilon_start'] = 1
        self.hyperparams['epsilon_min'] = 0.05
        self.hyperparams['epsilon_decay'] = 0.995

    def evaluate_state(self, observation, reward, terminal, action, next_state):
        table_look_up = self.table_look_up(observation)
        next_table_look_up = self.table_look_up(next_state)
        table_look_up = tuple(table_look_up + [action])
        next_table_look_up = tuple(next_table_look_up + [np.argmax(self.table[tuple(next_table_look_up)][:])])

        self.time_steps_counter[table_look_up] += 1

        learning_rate = self.hyperparams['learning_rate'] if self.hyperparams['learning_rate'] else\
            (1 / self.time_steps_counter[tuple(table_look_up)])

        self.table[table_look_up] += learning_rate *\
                                     (reward + self.hyperparams['discount_rate'] * self.table[next_table_look_up] - self.table[table_look_up])


class Sarsa(Agent):

    __TABLES_file = 'Sarsa_'

    def __init__(self, environment):
        super().__init__(environment,  table_type='q', table_init='null')
        self.hyperparams['epsilon_start'] = 1
        self.hyperparams['epsilon_min'] = 0.05
        self.hyperparams['epsilon_decay'] = 0.995

    def evaluate_state(self, observation, reward, terminal, action, next_state, next_action=None):
        table_look_up = self.table_look_up(observation)
        next_table_look_up = self.table_look_up(next_state)
        table_look_up = tuple(table_look_up + [action])
        if terminal:
            next_table_look_up = tuple(next_table_look_up + [0])
        else:
            if next_action:
                next_table_look_up = tuple(next_table_look_up + [next_action])
            else:
                return None

        self.time_steps_counter[table_look_up] += 1

        learning_rate = self.hyperparams['learning_rate'] if self.hyperparams['learning_rate'] else\
            (1 / self.time_steps_counter[tuple(table_look_up)])

        self.table[table_look_up] += learning_rate *\
                                     (reward + self.hyperparams['discount_rate'] * self.table[next_table_look_up] - self.table[table_look_up])


class TDLambdaPredictor(Agent):

    __TABLES_file = 'TDLambdaPredictor_'

    def __init__(self, environment, table_type='v'):
        super().__init__(environment,  table_type=table_type, table_init='null')
        self.hyperparams['_lambda'] = 1
        self.hyperparams['traces'] = 'accumulating'
        self.eligibility_table = np.zeros_like(self.time_steps_counter)

    def evaluate_state(self, observation, reward, terminal, action, next_state):
        table_look_up = self.table_look_up(observation)
        next_table_look_up = self.table_look_up(next_state)
        if self.table_type == 'q':
            table_look_up = table_look_up + [action]
            next_table_look_up = next_table_look_up + [self.follow_policy(next_state)]
        # WATKINS

        table_look_up = tuple(table_look_up)
        next_table_look_up = tuple(next_table_look_up)
        self.time_steps_counter[table_look_up] += 1

        if self.hyperparams['traces'] == 'dutch':
            learning_rate = self.hyperparams['learning_rate'] if self.hyperparams['learning_rate'] else\
                (1 / self.time_steps_counter[tuple(table_look_up)])
            self.eligibility_table[table_look_up] = (1 - learning_rate) * self.eligibility_table[table_look_up] + 1
        elif self.hyperparams['traces'] == 'replacing':
            self.eligibility_table[table_look_up] = 1
        else:
            self.eligibility_table[table_look_up] +=1

        eligible = np.argwhere(self.eligibility_table > 0)
        s_t = self.table[next_table_look_up]
        s_t_1 = self.table[table_look_up]
        for element in eligible:
            learning_rate = self.hyperparams['learning_rate'] if self.hyperparams['learning_rate'] else\
                (1/self.time_steps_counter[tuple(element)])

            self.table[tuple(element)] += learning_rate * (reward + self.hyperparams['discount_rate'] * s_t - s_t_1) * \
                                                           self.eligibility_table[tuple(element)]
            self.eligibility_table[tuple(element)] *= self.hyperparams['_lambda'] * self.hyperparams['discount_rate']

        if terminal:
            self.eligibility_table = np.zeros_like(self.time_steps_counter)


class SarsaLambda(Sarsa):

    __TABLES_file = 'SarsaLambda_'

    def __init__(self, environment):
        super().__init__(environment)
        self.hyperparams['_lambda'] = 1
        self.hyperparams['traces'] = 'accumulating'
        self.eligibility_table = np.zeros_like(self.time_steps_counter)

    def evaluate_state(self, observation, reward, terminal, action, next_state, next_action=None):
        table_look_up = self.table_look_up(observation)
        next_table_look_up = self.table_look_up(next_state)
        table_look_up = tuple(table_look_up + [action])

        if terminal:
            next_table_look_up = tuple(next_table_look_up + [0])
        else:
            if next_action:
                next_table_look_up = tuple(next_table_look_up + [next_action])
            else:
                return None

        self.time_steps_counter[table_look_up] += 1

        if self.hyperparams['traces']=='dutch':
            learning_rate = self.hyperparams['learning_rate'] if self.hyperparams['learning_rate'] else\
                (1 / self.time_steps_counter[tuple(table_look_up)])
            self.eligibility_table[table_look_up] = (1 - learning_rate) * self.eligibility_table[table_look_up] + 1
        elif self.hyperparams['traces']=='replacing':
            self.eligibility_table[table_look_up] = 1
        else:
            self.eligibility_table[table_look_up] += 1

        eligible = np.argwhere(self.eligibility_table > 0)
        s_t = self.table[next_table_look_up]
        s_t_1 = self.table[table_look_up]
        for element in eligible:
            learning_rate = self.hyperparams['learning_rate'] if self.hyperparams['learning_rate'] else\
                (1 / self.time_steps_counter[tuple(element)])

            self.table[tuple(element)] += learning_rate * (reward + self.hyperparams['discount_rate'] * s_t - s_t_1) *\
                                          self.eligibility_table[tuple(element)]

            self.eligibility_table[tuple(element)] *= self.hyperparams['_lambda'] * self.hyperparams['discount_rate']

        if terminal:
            self.eligibility_table = np.zeros_like(self.time_steps_counter)


class WatkinsLambda(SarsaLambda):

    __TABLES_file = 'WatkinsLambda_'

    def __init__(self, environment):
        super().__init__(environment)
        self.hyperparams['_lambda'] = 1
        self.hyperparams['traces'] = 'accumulating'
        self.eligibility_table = np.zeros_like(self.time_steps_counter)

    def evaluate_state(self, observation, reward, terminal, action, next_state, next_action=None):
        table_look_up = self.table_look_up(observation)
        next_table_look_up = self.table_look_up(next_state)
        table_look_up = tuple(table_look_up + [action])
        best_action = np.argmax(self.table[tuple(next_table_look_up)][:])
        if terminal:
            next_table_look_up = tuple(next_table_look_up + [0])
        else:
            if next_action:
                next_table_look_up = tuple(next_table_look_up + [best_action])
            else:
                return None

        self.time_steps_counter[table_look_up] += 1

        if self.hyperparams['traces']=='dutch':
            learning_rate = self.hyperparams['learning_rate'] if self.hyperparams['learning_rate'] else\
                (1 / self.time_steps_counter[tuple(table_look_up)])
            self.eligibility_table[table_look_up] = (1 - learning_rate) * self.eligibility_table[table_look_up] + 1
        elif self.hyperparams['traces']=='replacing':
            self.eligibility_table[table_look_up] = 1
        else:
            self.eligibility_table[table_look_up] += 1

        eligible = np.argwhere(self.eligibility_table > 0)
        s_t = self.table[next_table_look_up]
        s_t_1 = self.table[table_look_up]
        for element in eligible:
            learning_rate = self.hyperparams['learning_rate'] if self.hyperparams['learning_rate'] else\
                (1 / self.time_steps_counter[tuple(element)])

            self.table[tuple(element)] += learning_rate * (reward + self.hyperparams['discount_rate'] * s_t - s_t_1) *\
                                          self.eligibility_table[tuple(element)]

            if best_action == next_action:
                self.eligibility_table[tuple(element)] *= self.hyperparams['_lambda'] * self.hyperparams['discount_rate']

            else:
                self.eligibility_table[tuple(element)] = 0

        if terminal:
            self.eligibility_table = np.zeros_like(self.time_steps_counter)


class OffPolicyMontecarlo(MontecarloController):

    def __init__(self, env):
        super().__init__(env)
        self.cumulative_weights = np.zeros_like(self.time_steps_counter)

    def update_table(self):
        accum_discounted_reward = 0
        weight = 1
        for time_step in range(len(self.current_episode_steps)-1, -1, -1):
            reward = self.current_episode_steps[time_step]['reward'] + self.hyperparams['discount_rate'] * accum_discounted_reward
            self.cumulative_weights[self.current_episode_steps[time_step]['observation']] += weight
            self.time_steps_counter[self.current_episode_steps[time_step]['observation']] += 1
            self.table[self.current_episode_steps[time_step]['observation']] = self.incremental_average(
                                                                                   self.table[self.current_episode_steps[time_step]['observation']],
                                                                                   reward,
                                                                                   (self.cumulative_weights[self.current_episode_steps[time_step]['observation']]/weight))
            target_policy = np.argmax(self.table[self.current_episode_steps[time_step]['observation'][:-1]])
            if self.current_episode_steps[time_step]['observation'][-1] != target_policy:
                break

            weight += 1/(1/self.environment.action_space_len)

            accum_discounted_reward = reward


