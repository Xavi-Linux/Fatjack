import numpy as np
from environments.base import HitStand
import pickle
from pathlib import Path
from os.path import getctime
from uuid import uuid4


def folderpath_search(origin:Path, sought_folder:str)->Path:
    for element in origin.iterdir():
        if element.is_dir():
            if element.name == sought_folder:
                return Path(element)

    return folderpath_search(origin.parent, sought_folder)


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

    def save(self, episode):
        path = self.__AGENTS_Dir.joinpath('A_' + self.__class__.__name__ + '_' + str(self.id) + '_' + str(episode))
        with open(path, 'wb') as f:
            pickle.dump(self, f)


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

    def __init__(self, environment, table_type='q'):
        super().__init__(environment, table_type=table_type)
        self.hyperparams['epsilon_start'] = 1
        self.hyperparams['epsilon_min'] = 0.05
        self.hyperparams['epsilon_decay'] = 0.995


class TDLambdaPredictor(Agent):

    __TABLES_file = 'TDLambdaPredictor_'

    def __init__(self, environment, table_type='v'):
        super().__init__(environment,  table_type=table_type, table_init='null')
        self.hyperparams['_lambda'] = 1
        self.hyperparams['traces'] = 'accumulating'
        self.eligibility_table = np.zeros_like(self.time_steps_counter)

    def evaluate_state(self, observation, reward, terminal, action, next_state, next_action=None):
        table_look_up = self.table_look_up(observation)
        next_table_look_up = self.table_look_up(next_state)
        if self.table_type == 'q':
            table_look_up = table_look_up + [action]
            next_table_look_up = next_table_look_up + [action]

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


class SarsaLambda(TDLambdaPredictor):

    __TABLES_file = 'SarsaLambda_'

    def __init__(self, environment, table_type='q'):
        super().__init__(environment,  table_type=table_type)
        self.hyperparams['epsilon_start'] = 1
        self.hyperparams['epsilon_min'] = 0.05
        self.hyperparams['epsilon_decay'] = 0.995

    def evaluate_state(self, observation, reward, terminal, action, next_state, next_action=None):
        pass


if __name__ == '__main__':

    class FixAgent(TDLambdaPredictor):

        def follow_policy(self, observation, *args):
            if observation[0] > 19:
                return 0
            else:
                return 1


    def run_experiment(env, agent, episodes, show, save=None, collect_rewards=None, train=True):
        rewards = []
        average_rewards = []
        for episode in range(episodes):
            if (episode + 1) % show==0:
                print('Episode {0}:'.format(episode + 1))
                env.render()

            state, reward, terminal, _ = env.reset()
            while not terminal:
                action = agent.follow_policy(state)
                next_state, reward, terminal, _ = env.step(action)
                if train:
                    agent.evaluate_state(state, reward, terminal, action, next_state)

                state = next_state

            rewards.append(reward)

            if save:
                if (episode + 1) % save==0:
                    agent.save_table()

            if collect_rewards:
                if (episode + 1) % collect_rewards==0:
                    average_reward = sum(rewards[-collect_rewards:]) / collect_rewards
                    average_rewards.append(average_reward)

        return average_rewards


    env = HitStand()
    td_agent = FixAgent(env)
    td_agent.set_hyperparams(_lambda=0.5)
    EPISODES = 10_000
    SHOW_EVERY = 10_000
    SAVE_EVERY = None
    COLLECT_EVERY = 1_000
    results = run_experiment(env, td_agent, EPISODES, SHOW_EVERY, SAVE_EVERY, COLLECT_EVERY)
