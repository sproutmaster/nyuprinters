from flask import Blueprint, jsonify, request, escape
from models import db, Location, Printer, Setting, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user
from requests import get
from app import env
from json import loads as json_parse

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
        if not ip or ip == '127.0.0.1' or ip == '0.0.0.0':  # Prevent access to loopback IPs (there is a flaw here but will fix later)
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


@api.route('/settings', methods=['GET', 'POST', 'PATCH'])
def settings_api():
    if not (current_user.is_authenticated or request.headers.get('X-Apikey') == env.api_key()):
        return error_resp('Unauthorized')

    key = str(escape(request.form.get('key', request.args.get('key', ''))))
    value = str(escape(request.form.get('value', '')))
    key_values = request.form.get('settings', '')

    # Get all settings, or a specific setting
    if request.method == 'GET':
        if not key:
            return jsonify(list(map(lambda x: x.info(), Setting.query.all())))
        else:
            if not (setting := Setting.query.filter_by(key=key)):
                return error_resp('Invalid key')
            return jsonify(setting.first().info())

    # Update a setting
    elif request.method == 'PATCH':
        if key_values:  # Update multiple settings
            key_values = json_parse(key_values)
            for k, v in key_values.items():
                if not (setting := Setting.query.filter_by(key=k).first()):
                    return error_resp('Invalid key')
                setting.value = str(escape(v)) if v else setting.default_value
                db.session.add(setting)
            db.session.commit()
            return success_resp('Settings updated')

        elif not (setting := Setting.query.filter_by(key=key).first()):  # Update single setting
            return error_resp('Invalid key')

        setting.value = value if value else setting.default_value
        db.session.add(setting)
        db.session.commit()
        return success_resp(f'{key} updated')

    # Reset settings to default
    elif request.method == 'POST':
        reset = request.form.get('reset', False)
        if reset:
            for setting in Setting.query.all():
                setting.value = setting.default_value
                db.session.add(setting)
            db.session.commit()
            return success_resp('Settings reset to default')
        else:
            return error_resp('Invalid request')


@api.route('/users', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def users_api():
    if not request.headers.get('X-Apikey') == env.api_key:
        if not current_user.is_authenticated:
            return error_resp('Unauthenticated')

        if not current_user.type == 'superuser':
            return error_resp('Unauthorized')

    userid = request.args.get('user_id', request.form.get('user_id'))
    netid = str(escape(request.form.get('netid', ''))).strip()
    name = str(escape(request.form.get('name', ''))).strip()
    password = request.form.get('password', '')  # will implement password reset later
    user_type = str(escape(request.form.get('type', 'user'))).strip()
    user = User.query.filter_by(id=userid).first()

    if request.method in ['PUT', 'PATCH']:
        if not all([netid, name, user_type]):
            return error_resp('Missing required fields')
    if request.method in ['DELETE']:
        if not userid:
            return error_resp('Missing required fields')

    # For getting user info
    if request.method == 'GET':
        if userid:
            if user:
                return jsonify(user.info())
            else:
                return error_resp('User not found')
        users = User.query.all()
        return jsonify(list(map(lambda x: x.info(), users)))

    # For adding user
    elif request.method == 'PUT':
        user = User.query.filter_by(netid=netid).first()
        if user:
            return jsonify(error_resp('User already exists'))
        user = User(
            netid=netid,
            name=name,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            type=user_type,
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'{name.split()[0]} added'})

    # For updating user
    elif request.method == 'PATCH':
        if not user:
            return jsonify(error_resp('User not found'))
        user.netid = netid
        user.name = name
        if password:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
        user.type = user_type
        db.session.add(user)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'{name.split()[0]} updated'})

    # For deleting user
    elif request.method == 'DELETE':
        if not user:
            return jsonify(error_resp('User not found'))
        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'{user.name.split()[0]} deleted'})


@api.route('/contrib')  # Get contributors list from github
def contrib():
    try:
        resp = get(f'https://api.github.com/repos/{env.repo}/contributors',
                   headers={'Authorization': f'Bearer {env.github_token}'})
        return jsonify(resp.json())
    except Exception:
        return error_resp('Failed to get contributors')
