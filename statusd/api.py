from flask import Blueprint, jsonify, request, escape
from models import db, Location, Printer, Setting
from flask_login import current_user
from requests import get
from app import env

api = Blueprint('api', __name__, static_folder='static', template_folder='templates')


def error_resp(message):
    return {
        'status': 'error',
        'message': message
    }


def success_resp(message):
    return {
        'status': 'success',
        'message': message
    }


@api.route('/')
def api_index():
    return {
        'status': 'success',
        'message': 'API is running',
        'version': env.version,
        'github': env.github,
        'discord': env.discord,
        'default_loc': env.default_loc,
        'support_contact': env.support_contact,
    }


@api.route('/printers', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def printers_api():
    login = current_user.is_authenticated or request.headers.get('X-Apikey') == env.api_key
    if request.method in ['PUT', 'PATCH', 'DELETE'] and not login:
        return error_resp('Unauthorized')

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

    req_args = []
    if request.method in ['PUT']:
        req_args = [name, brand, type, ip, location]
    if request.method in ['PATCH']:
        req_args = [printer_id, name, brand, type, ip, location]
    if request.method in ['DELETE']:
        req_args = [printer_id]

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
        return success_resp(f'{name} added')

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

        return success_resp(f'{name} updated')

    # Delete a printer from DB
    elif request.method == 'DELETE':
        if not (printer := Printer.query.filter_by(id=int(printer_id)).first()):
            return error_resp('Invalid printer_id')

        db.session.delete(printer)
        db.session.commit()

        return success_resp(f'{printer.name} deleted')


@api.route('/locations', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def locations_api():
    login = current_user.is_authenticated or request.headers.get('X-Apikey') == env.api_key
    if request.method in ['PUT', 'PATCH', 'DELETE'] and not login:
        return error_resp('Unauthorized')

    filters = {'visible': True} if not login else {}

    location_id = request.args.get('location_id', request.form.get('location_id'))
    name = str(escape(request.form.get('name', '')))
    short_name = str(escape(request.form.get('short', '')))
    description = str(escape(request.form.get('description', '')))
    visible = request.form.get('visible') == 'true'

    req_args = []
    if request.method in ['PUT']:
        req_args = [name, short_name]
    if request.method in ['PATCH']:
        req_args = [location_id, name, short_name]
    if request.method in ['DELETE']:
        req_args = [location_id]

    if not all(req_args):
        return error_resp(
            f'Missing required fields: {",".join([k for k, v in globals().items() if id(v) in map(id, req_args)])}')

    # Get all locations, or a specific location
    if request.method == 'GET':
        if location_id:
            locations = Location.query.filter_by(id=location_id, **filters).first()
            return jsonify(locations.info())
        elif short_name:
            locations = Location.query.filter_by(short_name=short_name, **filters).first()
            return jsonify(locations.info())
        else:
            locations = Location.query.filter_by(**filters)
            return jsonify(list(map(lambda x: x.info(), locations)))

    # Add a location to DB
    elif request.method == 'PUT':
        if Location.query.filter_by(short_name=short_name).first():
            return error_resp('Location already exists')

        location = Location(name=name, short_name=short_name, description=description, visible=visible)
        db.session.add(location)
        db.session.commit()
        return success_resp(f'{name} added')

    # Update a location in DB
    elif request.method == 'PATCH':
        if not (location := Location.query.filter_by(id=int(location_id)).first()):
            return error_resp('Invalid location_id')

        if existing_loc := Location.query.filter_by(short_name=short_name).first():
            if existing_loc.short_name != location.short_name:
                return error_resp('Location already exists')

        location.name = name
        location.short_name = short_name
        location.description = description
        location.visible = visible

        db.session.add(location)
        db.session.commit()

        return success_resp(f'{name} updated')

    # Delete a location from DB
    elif request.method == 'DELETE':
        if not (location := Location.query.filter_by(id=int(location_id)).first()):
            return error_resp('Invalid location_id')

        if location.short_name == 'dev':
            return error_resp('Cannot delete this location')

        dev_loc = Location.query.filter_by(short_name='dev').first()

        for printer in location.printers:
            printer.location = dev_loc

        db.session.add_all(location.printers)
        db.session.delete(location)
        db.session.commit()

        return success_resp(f'{location.name} deleted')


@api.route('/settings', methods=['GET', 'PATCH'])
def settings_api():
    if not (current_user.is_authenticated or request.headers.get('X-Apikey') == env.api_key()):
        return error_resp('Unauthorized')

    key = str(escape(request.form.get('key', '')))
    value = str(escape(request.form.get('value', '')))

    if request.method == 'GET':
        if key == '':
            return jsonify(list(map(lambda x: x.info(), Setting.query.all())))
        else:
            if not (setting := Setting.query.filter_by(key=key).first()):
                return error_resp('Invalid key')
            return jsonify(setting.info())

    elif request.method == 'PATCH':
        if not (setting := Setting.query.filter_by(key=key).first()):
            return error_resp('Invalid key')
        setting.value = value
        db.session.add(setting)
        db.session.commit()
        return success_resp(f'{key} updated')
