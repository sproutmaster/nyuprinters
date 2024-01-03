from flask import render_template, send_from_directory

from flask import Blueprint, render_template

print_status = Blueprint('print_status', __name__, static_folder='static', template_folder='templates')


@print_status.route('/<string:loc>')
def location(loc):
    return loc


@print_status.route('/icons/<path:path>')
def send_report(path):
    return send_from_directory('static/print_status/icons', path)
