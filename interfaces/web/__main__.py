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
    info = request.json
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


if __name__ == '__main__':

    app.run('0.0.0.0', 5000)
