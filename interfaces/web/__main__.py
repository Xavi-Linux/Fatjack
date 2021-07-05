from flask import Flask, render_template, request
from agents.agents import MonteCarloPredictor, get_agent, list_saved_agents
from json import load, dumps
import numpy as np
import environments

class Evaluator(MonteCarloPredictor):
    #greedy policy:
    def follow_policy(self, observation, *args):
        table_look_up = tuple(self.table_look_up(observation))
        action = np.argmax(self.table[table_look_up][:])
        
        return action

app = Flask(__name__, static_folder='static', template_folder='templates')

AGENTS = list_saved_agents()[-5]
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
        summary = dict(zip(keys, list(outcome)+['-']))
        steps[i] = summary
        while not outcome[2]:
            action = agent.follow_policy(outcome[0])
            outcome = env.step(action)      
            summary = dict(zip(keys, list(outcome)+[int(action)]))
            i+=1
            steps[i] = summary
        yield steps

@app.route('/', methods=['GET'])
def main():
    return render_template('main.html')


@app.route('/start', methods=['POST'])
def start():
    info = dict(request.form)
    if info:
        print(request.form['agent'])
        evaluator = clone_table(AGENTS)
        hand = run_experiment(env, evaluator)
        print(next(hand))
        print(next(hand))
        print(next(hand))
        return dumps(dict(next(hand)))

    return '200'

if __name__ == '__main__':
  
    app.run('0.0.0.0', 5000)
