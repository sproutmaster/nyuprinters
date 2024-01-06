#######################################################
# nyuprinters.com
#
# Copyright (c) 2022-2024, Joe Prakash
# Released under the MIT License
#######################################################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import environ


class Env:
    def __init__(self):
        self.discord = environ.get("DISCORD", default='#')
        self.github = environ.get("GITHUB", default='#')
        self.postgres_uri = environ.get("POSTGRES_URI", default="postgresql://admin:admin@localhost:5432/nyup")


env = Env()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = env.postgres_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)
