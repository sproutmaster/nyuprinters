from flask import Blueprint, render_template, escape, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import env
from models import db, Location, User, Setting
from utils import simple_sanitize, error_resp, success_resp
from sqlalchemy import inspect
from json import load as json_parse

index = Blueprint('index', __name__, static_folder='static', template_folder='templates')
underground = Blueprint('underground', __name__, static_folder='static', template_folder='templates')


@index.route('/')
def home():
    return render_template('index.html',
                           github=env.github,
                           discord=env.discord,
                           loc=env.default_loc
                           )


@index.route('/init')
def init():
    inspector = inspect(db.engine)
    if "settings" not in inspector.get_table_names():
        db.create_all()
        with open('seed/settings.json', 'r') as file:
            init_settings = json_parse(file)

        settings = [Setting(**resp) for resp in init_settings]
        init_location = Location(name='Dev', short_name='dev', visible=False)
        init_user = User(
            name='Admin',
            netid='admin',
            password=generate_password_hash('admin', "pbkdf2:sha256"),
            type='superuser',
            location=init_location
        )

        db.session.add_all(settings)
        db.session.add(init_location)
        db.session.add(init_user)
        db.session.commit()

        return success_resp('Database initialized')

    return success_resp('OK')


@index.route('/<string:loc>')
def send_info_by_loc(loc):
    filters = {'visible': True} if not current_user.is_authenticated else {}
    loc = simple_sanitize(loc.lower())

    if loc := Location.query.filter_by(short_name=loc).first():
        return render_template('app.html',
                               login=current_user.is_authenticated,
                               locs=Location.query.filter_by(**filters).all(),
                               loc=loc.short_name,
                               github=env.github,
                               )

    return redirect(url_for('index.home'))


@underground.route('/')
def underground_home():
    login = current_user.is_authenticated
    locations = Location.query.all() if login else []
    return render_template('underground.html',
                           locs=locations,
                           login=login,
                           name=current_user.name.split()[0] if login else None,
                           superuser=current_user.type == 'superuser' if login else False,
                           footer=False,
                           github=env.github,
                           discord=env.discord,
                           )


@underground.route('/auth', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def underground_auth():
    # For getting user info
    if request.method == 'GET':
        if current_user.is_authenticated:
            return jsonify({'netid': current_user.netid, 'name': current_user.name, 'type': current_user.type})
        return jsonify({'netid': None, 'name': None, 'type': None})

    # For logging in
    elif request.method == 'POST':
        netid = request.form.get('netid')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(netid=netid).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
        return redirect(url_for('underground.underground_home'))

    # For changing password
    elif request.method == 'PATCH':
        if current_user.is_authenticated:
            old_password = request.form.get('old_password')
            password = request.form.get('new_password')
            if check_password_hash(current_user.password, old_password):
                user = User.query.filter_by(netid=current_user.netid).first()
                user.password = generate_password_hash(password, method='pbkdf2:sha256')
                db.session.add(user)
                db.session.commit()
                return success_resp('Password updated')
            return error_resp('Current password is incorrect')
        return error_resp('Unauthenticated')

    # For logging out
    elif request.method == 'DELETE':
        logout_user()
        return success_resp('Logged out')


@underground.route('/auth/logout')
def underground_logout():
    logout_user()
    return redirect(url_for('underground.underground_home'))
