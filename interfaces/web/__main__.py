from flask import Flask, render_template, request, session
from agents.agents import MonteCarloPredictor, get_agent, list_saved_agents
from json import load, dumps
import numpy as np
import environments
from copy import deepcopy

class Evaluator(MonteCarloPredictor):
    #greedy policy:
    def follow_policy(self, observation, *args):
        table_look_up = tuple(self.table_look_up(observation))
        action = np.argmax(self.table[table_look_up][:])
        
        return action

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = b"7l\xe37\xaf,\x9b\t\x9c\x9f\x18\xe2'xM\xd9"

AGENTS = {1: list_saved_agents()[10],
          2: list_saved_agents()[11]
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

def get_generator(key, times=10):
    evaluator = clone_table(AGENTS[int(key)])
    generator = run_experiment(env, evaluator)
    pool = [next(generator) for _ in range(0, times)]
    return pool

@app.route('/', methods=['GET'])
def main():
    return render_template('main.html')


@app.route('/start', methods=['POST'])
def start():
    info = dict(request.form)
    if info:
        value = request.form['agent']
        session['value'] = value
        
        return dumps(get_generator(value))

    return '200'

@app.route('/play', methods=['GET'])
def play():
    value = int(session['value'])
    return dumps(get_generator(value))


if __name__ == '__main__':
  
    app.run('0.0.0.0', 5000)
