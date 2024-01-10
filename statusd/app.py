#########################################################################################
# nyuprinters
#
# Copyright (c) 2023-2024, Joe Prakash
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#########################################################################################

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from os import environ

from models import db, User


class Env:
    def __init__(self):
        self.discord = environ.get("DISCORD", default='#')
        self.github = environ.get("GITHUB", default='#')
        self.postgres_uri = environ.get("POSTGRES_URI", default="postgresql://admin:admin@localhost:5432/nyup")
        self.default_loc = environ.get("DEFAULT_LOC", default="bobst")
        self.secret_key = environ.get("SECRET_KEY", default="not-a-secret")


env = Env()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = env.postgres_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    app.config['SECRET_KEY'] = env.secret_key

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "underground.underground_home"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    Migrate(app, db)
    return app
