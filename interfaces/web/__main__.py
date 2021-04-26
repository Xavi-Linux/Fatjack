from flask import Flask, render_template


def create_app():
    app = Flask(__name__,static_folder='static', template_folder='templates')

    @app.route('/')
    def first():
        return render_template('main.html')

    return app


if __name__ == '__main__':

    app = create_app()
    app.run('0.0.0.0', 5000)

