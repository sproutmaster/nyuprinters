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
from datetime import timedelta
from dotenv import load_dotenv

from models import db, User

load_dotenv()


class Env:
    def __init__(self):
        self.version = environ.get("VERSION", default="0.1")
        self.support_contact = environ.get("SUPPORT_CONTACT", default="67924667+sproutmaster@users.noreply.github.com")
        self.discord = environ.get("DISCORD", default='')
        self.repo = environ.get("REPO", default='sproutmaster/nyuprinters')
        self.github = f'https://github.com/{self.repo}'
        self.postgres_url = environ.get("POSTGRES_URL", default="postgresql://admin:admin@localhost:5432/nyup")
        self.default_loc = environ.get("DEFAULT_LOC", default="dev")
        self.secret_key = environ.get("SECRET_KEY", default="dingdongbingbongbangdangpfchans")
        self.sourced_url = environ.get("SOURCED_URL", default="http://localhost:8000")
        self.api_key = environ.get("API_KEY", default='iloveapis')


env = Env()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = env.postgres_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    app.config['SECRET_KEY'] = env.secret_key
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "underground.underground_home"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    Migrate(app, db)
    return app
