from flask import Blueprint, render_template, send_from_directory, jsonify
from models import Location, Printer

print_status = Blueprint('print_status', __name__, static_folder='static', template_folder='templates')


@print_status.route('/<string:loc>')
def send_info_by_loc(loc):
    location = Location.query.filter_by(short_name=loc).first()
    if location is None:
        return "Not found"
    printers = Printer.query.filter_by(location_id=location.id).all()
    resp = list(map(lambda x: x.info, printers))
    return jsonify(resp)


@print_status.route('/icons/<path:path>')
def send_report(path):
    return send_from_directory('static/print_status/icons', path)
