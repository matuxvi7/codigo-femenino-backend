1from flask import Flask

from src.routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(api)
    return app


if __name__ == "__main__":
    create_app().run(debug=True)