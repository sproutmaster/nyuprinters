from sys import path
from flask import Flask
from urllib.parse import urlparse
from redis import Redis
from flask_mongoengine import MongoEngine

path.append("../")
app = Flask(__name__)

import project_settings

redis_uri_parsed = urlparse(project_settings.redis_uri)
redis_client = Redis(host=redis_uri_parsed.hostname, port=redis_uri_parsed.port)
