from flask import Blueprint, jsonify, request, escape
from models import db, Location, Printer
from flask_login import current_user
from requests import get
from app import env

api = Blueprint('api', __name__, static_folder='static', template_folder='templates')


def error_resp(message):
    return {
        'status': 'error',
        'message': message
    }


@api.route('/')
def home():
    return "Not Implemented", 501


@api.route('/locations')
def location_api():
    short_name = request.args.get('short_name')
    if short_name is None or short_name == '':
        locations = Location.query.all() if current_user.is_authenticated else Location.query.filter_by(visible=True)
    else:
        locations = Location.query.filter_by(short_name=short_name)
    resp = list(map(lambda x: x.info, locations))
    return jsonify(resp)


@api.route('/printers', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def printer_api():
    login = current_user.is_authenticated or request.headers.get('X-Apikey') == env.api_key
    filters = {'visible': True} if not login else {}

    printer_id = request.args.get('printer_id', request.form.get('printer_id'))
    name = str(escape(request.form.get('name', '')))
    brand = str(escape(request.form.get('brand', '')))
    model = str(escape(request.form.get('model', '')))
    type = 'color' if request.form.get('type') == 'true' else 'grayscale'
    serial = str(escape(request.form.get('serial', '')))
    ip = str(escape(request.form.get('ip', '')))
    location = request.form.get('location', '')
    comment = str(escape(request.form.get('comment', '')))
    visible = request.form.get('visible') == 'true'

    if request.method in ['PUT', 'PATCH', 'DELETE'] and not login:
        return error_resp('Unauthorized')

    req_args = []
    if request.method in ['PUT']:
        req_args = [name, brand, type, ip, location]
    if request.method in ['PATCH']:
        req_args = [printer_id, name, brand, type, ip, location]
    if request.method in ['DELETE']:
        req_args = [printer_id]

    print(request.method, req_args)

    if not all(req_args):
        return error_resp(
            f'Missing required fields: {",".join([k for k, v in globals().items() if id(v) in map(id, req_args)])}')

    # Get all printers, or printers at a location
    if request.method == 'GET':
        if location:  # For getting printers at a location
            if loc := Location.query.filter_by(short_name=location, **filters).first():
                return jsonify(list(map(lambda x: x.info(login), loc.printers)))
            else:
                return error_resp('Invalid Location, no printers, or no permission to view')
        elif printer_id:  # For getting a specific printer
            if printer := Printer.query.filter_by(id=int(printer_id), **filters).first():
                return jsonify(printer.info(login))
            else:
                return error_resp('Invalid id, or no permission to view')
        else:  # For getting all printers
            return jsonify(list(map(lambda x: x.info(login), Printer.query.filter_by(**filters))))

    # Relay message to and from sourced
    elif request.method == 'POST':
        if ip is None or ip == '' or ip == '127.0.0.1':
            return error_resp('Invalid IP Address')
        try:
            sourced_resp = get(f'{env.sourced_url}?ip={ip}')
        except Exception:
            return error_resp('Sourced is down')
        return sourced_resp.json()

    # Add a printer to DB
    elif request.method == 'PUT':
        if Printer.query.filter_by(ip_address=ip).first():
            return error_resp('Printer already exists')

        if not (loc := Location.query.filter_by(short_name=location).first()):
            return error_resp('Invalid location')

        printer = Printer(name=name, model=model, type=type, serial=serial, ip_address=ip, location=loc,
                          comment=comment, visible=visible)
        db.session.add(printer)
        db.session.commit()
        return {'status': 'success', 'message': f'Printer {name} added'}

    # Update a printer in DB
    elif request.method == 'PATCH':
        if not (printer := Printer.query.filter_by(id=int(printer_id)).first()):
            return error_resp('Invalid printer_id')

        if not (loc := Location.query.filter_by(short_name=location).first()):
            return error_resp('Invalid location')

        printer.name = name
        printer.model = model
        printer.type = type
        printer.serial = serial
        printer.ip_address = ip
        printer.location = loc
        printer.comment = comment
        printer.visible = visible

        db.session.add(printer)
        db.session.commit()

        return {'status': 'success', 'message': f'Printer {name} updated'}

    # Delete a printer from DB
    elif request.method == 'DELETE':
        if not (printer := Printer.query.filter_by(id=int(printer_id)).first()):
            return error_resp('Invalid printer_id')

        db.session.delete(printer)
        db.session.commit()

        return {'status': 'success', 'message': f'Printer {printer.name} deleted'}
