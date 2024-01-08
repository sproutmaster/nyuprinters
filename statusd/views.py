from flask import Blueprint, render_template, send_from_directory, escape
from app import env

index = Blueprint('index', __name__, static_folder='static', template_folder='templates')


@index.route('/')
def home():
    return render_template('index.html',
                           github=env.github,
                           discord=env.discord,
                           default_loc=env.default_loc,
                           )


@index.route('/<string:loc>')
def send_info_by_loc(loc):
    loc = escape(loc)
    return render_template('app.html',
                           loc=loc,
                           github=env.github,
                           discord=env.discord,
                           )


@index.route('/icons/<path:path>')
def send_report(path):
    return send_from_directory('static/icons', path)
