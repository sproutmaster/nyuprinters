from flask import Blueprint, render_template, escape, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import env
from models import db, Location, User
from api import error_resp

index = Blueprint('index', __name__, static_folder='static', template_folder='templates')
underground = Blueprint('underground', __name__, static_folder='static', template_folder='templates')


@index.route('/')
def home():
    return render_template('index.html',
                           github=env.github,
                           discord=env.discord,
                           loc=env.default_loc
                           )


@index.route('/<string:loc>')
def send_info_by_loc(loc):
    loc = escape(loc.lower())
    if loc := Location.query.filter_by(short_name=loc).first():
        return render_template('app.html',
                               loc=loc.short_name,
                               github=env.github,
                               discord=env.discord,
                               )
    else:
        return redirect(url_for('index.home'))


@underground.route('/')
def underground_home():
    login = current_user.is_authenticated
    locations = Location.query.all() if login else []
    return render_template('underground.html', locs=locations, login=login, footer=False)


@underground.route('/auth', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
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
