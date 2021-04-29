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
    hand_players = game.retrieve_hands_alive()
    state = {game.alive_players[0].name: game.alive_players[0].current_hand.card_names,
             'Dealer': game.croupier_hand.card_names,
             'Player_value': game.alive_players[0].current_hand.best_value,
             'Dealer_value': game.croupier_hand.best_value,
             'Status': 'on',
             'Player_gains': game.alive_players[0].gains,
             'Player_cash': game.alive_players[0].cash,
             'Continuity': None
             }
    if len(hand_players) == 0:
        croupier_hand = game.get_croupier_hand()
        state['Dealer'] = croupier_hand.card_names
        state['Dealer_value'] = croupier_hand.best_value
        state['Status'] = game.resolve_round(game.alive_players[0]).upper()
        state['Player_gains'] = game.alive_players[0].gains
        state['Player_cash'] = game.alive_players[0].cash
        state['Continuity'] = game.assess_continuity()

    return dumps(state)


@app.route('/action', methods=['POST'])
def action():
    action = request.form['action']
    game.send_action(game.alive_players[0], action)

    hand_players = game.retrieve_hands_alive()
    state = {game.alive_players[0].name:game.alive_players[0].current_hand.card_names,
             'Dealer':game.croupier_hand.card_names,
             'Player_value':game.alive_players[0].current_hand.best_value,
             'Dealer_value':game.croupier_hand.best_value,
             'Status':'on',
             'Player_gains':game.alive_players[0].gains,
             'Player_cash':game.alive_players[0].cash,
             'Continuity':None
             }
    if len(hand_players)==0 or action.lower() == 'stand':
        croupier_hand = game.get_croupier_hand()
        state['Dealer'] = croupier_hand.card_names
        state['Dealer_value'] = croupier_hand.best_value
        state['Status'] = game.resolve_round(game.alive_players[0]).upper()
        state['Player_gains'] = game.alive_players[0].gains
        state['Player_cash'] = game.alive_players[0].cash
        state['Continuity'] = game.assess_continuity()
    """else:
        if action.lower() == 'stand':
            if not all(map(lambda p:p.current_hand.is_busted, game.alive_players)):
                croupier_hand = game.get_croupier_hand().card_names
            for player in game.alive_players:
                status = game.resolve_round(player).upper()
    """
    return dumps(state)


if __name__ == '__main__':

    app.run('0.0.0.0', 5000)
