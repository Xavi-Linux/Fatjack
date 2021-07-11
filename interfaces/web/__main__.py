from types import MethodDescriptorType
from flask import Flask, render_template, request, session
from agents.agents import MonteCarloPredictor, get_agent, list_saved_agents
from json import load, dumps
import numpy as np
import environments
from copy import deepcopy
import pickle

class Evaluator(MonteCarloPredictor):
    #greedy policy:
    def follow_policy(self, observation, *args):
        table_look_up = tuple(self.table_look_up(observation))
        action = np.argmax(self.table[table_look_up][:])
        
        return action

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = b"7l\xe37\xaf,\x9b\t\x9c\x9f\x18\xe2'xM\xd9"

AGENTS = {1: list_saved_agents()[25],
          2: list_saved_agents()[26]
          }

env = environments.make('hitstand')

def clone_table(route):
    agent = get_agent(route)
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
    evaluator = clone_table(AGENTS[int(key)])
    generator = run_experiment(env, evaluator)
    pool = [next(generator) for _ in range(0, times)]
    return pool

def get_results(key):
    path = AGENTS[int(key)]
    agent = get_agent(path)
    id_value = agent.id
    class_name = agent.__class__.__name__
    filepath = '/home/xavi/Documents/Blackjack/results/results_' + class_name + "_" + str(id_value) + '_CON'
    print(filepath)
    try:
        with open(filepath, 'rb') as f:
            instance = pickle.load(f)
        
        return instance
    except:
        return None

def get_table(key, full=True):
    path = AGENTS[int(key)]
    agent = get_agent(path)
    tables = agent.list_saved_tables()
    table = agent.load_table(filename=tables[-1], overwrite=False)
    if full:
        policy_table = np.argmax(table[:18,:10,:], axis=3)
    else:
        policy_table = np.argmax(table[7:18,:10,:], axis=3)

    return policy_table.tolist()

@app.route('/', methods=['GET'])
def main():
    return render_template('main.html')


@app.route('/start', methods=['POST'])
def start():
    info = dict(request.form)
    if info:
        value = request.form['agent']
        session['value'] = value
        
        return '400'

    return '200'

@app.route('/play', methods=['GET'])
def play():
    value = int(session['value'])
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
        value = session['value']
        return dumps(get_table(value))


if __name__ == '__main__':
  
    app.run('0.0.0.0', 5000)
