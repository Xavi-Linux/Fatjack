from types import MethodDescriptorType
from flask import Flask, render_template, request, session
from agents.agents import MonteCarloPredictor, get_agent, list_saved_agents, find_results
from json import load, dumps
import numpy as np
import environments
from copy import deepcopy
import pickle
import pathlib
import re

class Evaluator(MonteCarloPredictor):
    #greedy policy:
    def follow_policy(self, observation, *args):
        table_look_up = tuple(self.table_look_up(observation))
        action = np.argmax(self.table[table_look_up][:])
        
        return action

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = b"7l\xe37\xaf,\x9b\t\x9c\x9f\x18\xe2'xM\xd9"

TOP =  ['A_FixEpsilon_1694735483da4ee5aa0b4e0c020a5225',
 'A_QDecayRate_41eb1831b3fd43d5aab3e5b38422208a',
 'A_QVisitsDecay_a448d79b4b5b45258103e111d1c1f490',
 'A_DecayRate_a81ffac6ceef4e7abbedab434b11dca6',
 'A_QVisitsDecay_6cfb7d8b6df64593a88c8de054bebedd',
 'A_QVisitsDecay_c688b215e42e40daa54c2249040a9a39',
 'A_QVisitsDecay_a08b71ff7c0749618027631507a49bbf',
 'A_QDecayRate_b798d2c5acd64e658f52d0be9169d01e',
 'A_FixEpsilon_31bad91b04084908852b5c283cb2cf08',
 'A_FixEpsilon_1b720ec52e6640e298a3b41eeb9043f4']

def exceptions(value):
    exceps = ['A_FixEpsilon_fd1f72645ff54bda8d657bc204415c66',
    'A_UCB_c53ebd1c23634775a8d0e3a79ccaeac5',
    'A_UCB_253fabab6dc54090adb37a71a16e2b5a',
    'A_FixEpsilon_1e2748d2c9dc4b25940dca10393f47f2',
    'A_VisitsDecay_3c6267913c894118a9e60bc796652cc7',
    'A_UCB_d9546ca2809d43e4b8b5be4a5d5c33ac',
    'A_UCB_341235ec2ac7476981f9be3281506c7a',
    'A_DecayRate_2923aed748004df4819f142b64433e8e',
    'A_AlwaysGreedy_3cab8bb2ecd94981bd57c46af642e9f8']
    if value in exceps:
        return False
    else:
        return True

OTHERS = list(filter(exceptions,[ a for a in list_saved_agents(filter='unique')]))
AGENTS = [ a for a in TOP]
env = environments.make('hitstand')

def get_features(route):
    def translate_null(value, lr=False):
        if value:
            return value

        else:
            if lr:
                return '1/visits'

            else:
                return 'N/A'
    
    def rename(feats_dict):
        regex_ucb = re.compile('UCB')
        if regex_ucb.search(feats_dict['strategy']):
            feats_dict['ep_min'] = 'N/A'
            feats_dict['ep_decay'] = 'N/A'
            feats_dict['strategy'] = 'Upper bound confidence'
        else:
            feats_dict['ucb'] ='N/A'

            regex_fixep = re.compile('FixEpsilon')
            if regex_fixep.search(feats_dict['strategy']):
               feats_dict['strategy'] = 'E-Greedy'
               feats_dict['ep_decay'] = 'N/A'

            regex_decay = re.compile('DecayRate')
            if regex_decay.search(feats_dict['strategy']):
                feats_dict['strategy'] = 'E-Greedy with decay rate'
            
            regex_visits = re.compile('VisitsDecay')
            if regex_visits.search(feats_dict['strategy']):
               feats_dict['strategy'] = 'E-Greedy 1/visits decay'
               feats_dict['ep_decay'] = 'N/A'
            
            regex_visits = re.compile('GreedyOff')
            if regex_visits.search(feats_dict['strategy']):
               feats_dict['strategy'] = 'E-Greedy'
               feats_dict['ep_decay'] = 'N/A'
            
            regex_visits = re.compile('Random')
            if regex_visits.search(feats_dict['strategy']):
               feats_dict['strategy'] = 'Random play'
               feats_dict['ep_decay'] = 'N/A'
               feats_dict['ep_min'] = 'N/A'
            
        if feats_dict['algorithm'] ==  'MontecarloController':
            feats_dict['algorithm'] = 'Every visit Montecarlo'

        return feats_dict

    agent = get_agent(route, criterion='most_trained')
    features = {'algorithm': agent.get_parent_class_str(),
                'strategy': agent.__class__.__name__,
                'lr': translate_null(agent.hyperparams.get('learning_rate'), True),
                'dr': translate_null(agent.hyperparams.get('discount_rate')),
                'lambda': translate_null(agent.hyperparams.get('_lambda')),
                'traces': translate_null(agent.hyperparams.get('traces')),
                'ep_min': translate_null(agent.hyperparams.get('epsilon_min')),
                'ep_decay': translate_null(agent.hyperparams.get('epsilon_decay')),
                'ucb': translate_null(agent.hyperparams.get('ucb_c')),
                }
    
    return rename(features)

def clone_table(route):
    agent = get_agent(route, criterion='most_trained')
    evaluator = Evaluator(env)
    evaluator.table = agent.table.copy()
    return evaluator

def run_experiment(env, agent):
    keys = ('points', 'reward', 'terminal', 'cards', 'action')
    while True:
        i=0
        steps={}
        outcome = env.reset()
        outcome = list(outcome)
        outcome[3] = deepcopy(outcome[3])
        summary = dict(zip(keys, outcome + ['-']))
        
        steps[i] = summary
        while not outcome[2]:
            action = agent.follow_policy(outcome[0])
            outcome = env.step(action)
            outcome = list(outcome)
            outcome[3] = deepcopy(outcome[3]) 
            summary = dict(zip(keys, outcome + [int(action)]))
            i+=1
            steps[i] = summary

        yield steps

def get_generator(key, times=100):
    evaluator = clone_table(key)
    generator = run_experiment(env, evaluator)
    pool = [next(generator) for _ in range(0, times)]
    return pool

def get_results(key):
    agent = get_agent(key, criterion='most_trained')
    id_value = agent.id
    class_name = agent.__class__.__name__
    filepath = find_results(class_name, id_value, True)
    try:
        filepath = str(filepath[0])
        with open(filepath, 'rb') as f:
            instance = pickle.load(f)
        
        return instance
    except:
        return None

def get_table(key, full=True):
    agent = get_agent(key, criterion='most_trained')
    table = agent.table.copy()
    
    if full:
        policy_table = np.argmax(table[:18,:10,:], axis=3)
    else:
        policy_table = np.argmax(table[7:18,:10,:], axis=3)

    policy_table[:8,:,1] = 1

    return policy_table.tolist()


@app.route('/', methods=['GET'])
def main():
    return render_template('main.html', agents=AGENTS, others=OTHERS)


@app.route('/start', methods=['POST'])
def start():
    info = dict(request.form)
    if info:
        value = request.form['agent']
        session['value'] = value
        features = get_features(value)
        return dumps(features)

    return '200'


@app.route('/play', methods=['GET'])
def play():
    value = session['value']
    return dumps({'hands': get_generator(value)})


@app.route('/results', methods=['POST'])
def results():
    info = dict(request.form)
    if info:
        value = request.form['agent']
        session['value'] = value
        results = get_results(value)
        if results:
            return results
        else:
            return '500'


@app.route('/policy', methods=['POST'])
def policy():
    info = dict(request.form)
    if info: 
        value = request.form['agent']
        session['value'] = value
        return dumps(get_table(value))


if __name__ == '__main__':
  
    app.run('0.0.0.0', 5000)
