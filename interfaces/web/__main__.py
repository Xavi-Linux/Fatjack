from flask import Flask, render_template, request
from games.blackjacks import Blackjack
from json import load, dump


def create_app():
    app = Flask(__name__,static_folder='static', template_folder='templates')
    game = None

    @app.route('/', methods=['GET'])
    def main():
        return render_template('main.html')

    @app.route('/start', methods=['GET', 'POST'])
    def start():
        return 'hello'

    return app


if __name__ == '__main__':

    app = create_app()
    app.run('0.0.0.0', 5000)

