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
        self.hyperparams = {'discount_rate': 1, 'learning_rate': 1}
        self.save_at_episodes = []
        self.current_table_path = ''
        self.num_executed_episodes = 0

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

    @staticmethod
    def incremental_average(current_average, new_value, num_observations):
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
        self.current_episode_steps = {}

    def evaluate_state(self, observation, reward, terminal, action=None):
        table_look_up = self.table_look_up(observation)
        if self.table_type == 'q' and action is not None:
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

    def run_experiment(env, agent, episodes, show, save=None, collect_rewards=None):
        rewards = []
        average_rewards = []
        for episode in range(episodes):
            if (episode + 1) % show==0:
                print('Episode {0}:'.format(episode + 1))
                env.render()

            state, reward, terminal, _ = env.reset()
            agent.evaluate_state(state, reward, terminal)
            if state[0] == 21:
                print('watch out')
            while not terminal:
                action = agent.follow_policy(state, reward, terminal)
                state, reward, terminal, _ = env.step(action)
                if state[0] == 21 and state[2] ==1:
                    print('hello')
                agent.evaluate_state(state, reward, terminal)

            rewards.append(reward)
            if save:
                if (episode + 1) % save==0:
                    agent.save_table(episode + 1)

            if collect_rewards:
                if (episode + 1) % collect_rewards==0:
                    average_reward = sum(rewards[-collect_rewards:]) / collect_rewards
                    average_rewards.append(average_reward)

        return average_rewards


    class RandomPolicyAgent(MonteCarloPredictor):

        def follow_policy(self, observation, *args):
            if observation[2] == 0:
                return np.random.randint(0, self.environment.action_space_len)
            else:
                return 1
    
    class FixAgent(MonteCarloPredictor):

        def follow_policy(self, observation, *args):
            if observation[0] > 19:
                return 0
            else:
                return 1

    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter

    def plot_v_func(table, title):
        X = np.linspace(1, 10, 10)
        Y = np.linspace(12, 21, 10)
        Xm, Ym = np.meshgrid(X, Y)

        fig = plt.figure(figsize=(20, 10))
        fig.suptitle(t=title, fontsize=16, x=0.5, y=1.05)

        common_style_dict = {'xlim':(X[0], X[-1]),
                             'xticks':X,
                             'xticklabels':['{:.0f}'.format(value) for value in list(X)[1:]] + ['A'],
                             'xlabel':'Dealer\'s Card',
                             'ylim':(Y[0], Y[-1]),
                             'yticks':Y,
                             'yticklabels':Y,
                             'ylabel':'Player\'s Total',
                             'zlim':(-1, 1.5),
                             'zticks':np.arange(-1, 1.8, 0.2),
                             'zticklabels':np.arange(-1, 1.8, 0.2),
                             }

        ax = fig.add_subplot(1, 2, 1, projection='3d', title='No usable Ace', **common_style_dict)
        #ax.plot_surface(Xm, Ym, table[8:18,:10,0], cmap=plt.get_cmap('bwr'), vmin=-1, vmax=1.5)
        ax.plot_wireframe(Xm, Ym, table[8:18, :10, 0], cmap=plt.get_cmap('bwr'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('% 1.0f'))
        ax.zaxis.set_major_formatter(FormatStrFormatter('% 1.1f'))
        ax.view_init(0, -45)

        ax = fig.add_subplot(1, 2, 2, projection='3d', title=' Usable Ace', **common_style_dict)
        #ax.plot_surface(Xm, Ym, table[8:18,:10,1], cmap=plt.get_cmap('bwr'), vmin=-1, vmax=1.5)
        ax.plot_wireframe(Xm, Ym, table[8:18, :10, 1], cmap=plt.get_cmap('bwr'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('% 1.0f'))
        ax.zaxis.set_major_formatter(FormatStrFormatter('% 1.1f'))
        ax.view_init(0, -45)
        return ax

    envi = HitStand()
    agent = FixAgent(envi)
    EPISODES = 1_000
    SHOW_EVERY = 100_000
    SAVE_EVERY = None
    COLLECT_EVERY = 40_000
    results = run_experiment(envi, agent, EPISODES, SHOW_EVERY, SAVE_EVERY, COLLECT_EVERY)
    ax = plot_v_func(agent.table, 'After')
    plt.show()
