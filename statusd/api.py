from flask import Blueprint, jsonify, request, escape
from models import Location, Printer

api = Blueprint('api', __name__, static_folder='static', template_folder='templates')


@api.route('/')
def home():
    return "Not Implemented", 501


@api.route('/locations')
def get_locations():
    locations = Location.query.all()
    resp = list(map(lambda x: x.info, locations))
    return jsonify(resp)


@api.route('/printers')
def send_printers_by_loc():
    short_name = escape(request.args.get('short_name'))
    if short_name is None or short_name == '':
        return {'error': 'no location specified. Send GET param short_name=<location>'}
    location = Location.query.filter_by(short_name=short_name).first()
    if location is None:
        return {'error': 'location not found'}
    printers = Printer.query.filter_by(location=location)
    resp = list(map(lambda x: x.info, printers))
    return jsonify(resp)
