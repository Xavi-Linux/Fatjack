from flask import Flask, render_template, request
from games.blackjacks import Blackjack
from json import load, dumps

app = Flask(__name__, static_folder='static', template_folder='templates')
game = Blackjack()


@app.route('/', methods=['GET'])
def main():
    return render_template('main.html')


@app.route('/start', methods=['POST'])
def start():
    info = dict(request.form)
    if info:
        info['initial_cash'] = float(info['initial_cash'])
        info['allow_debt'] = True if ['allow_debt'] == 'Y' else False
        if not game.game_on:
            game.setup_players([info])
            game.start()

        return '400'

    return '200'


@app.route('/bet', methods=['POST'])
def bet():
    bet = float(request.form['value'])
    game.alive_players[0].place_bet(bet)
    game.start_round()
    return dumps({game.alive_players[0].name: game.alive_players[0].current_hand.card_names,
                  'Dealer': game.croupier_hand.card_names})


@app.route('/action', methods=['POST'])
def action():
    action = request.form['action']
    game.send_action(game.alive_players[0], action)
    croupier_hand = game.croupier_hand.card_names
    status = 'on'
    name= game.alive_players[0].name
    current_hand = game.alive_players[0].current_hand.card_names
    if action.lower() == 'stand':
        if not all(map(lambda p:p.current_hand.is_busted, game.alive_players)):
            croupier_hand = game.get_croupier_hand().card_names
        for player in game.alive_players:
            status = game.resolve_round(player).upper()

    return dumps({name: current_hand,
                  'Dealer': croupier_hand,
                  'Status': status})


if __name__ == '__main__':

    app.run('0.0.0.0', 5000)
