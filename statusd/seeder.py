import os
import random
import sys
import json
from random import random, choice
from datetime import datetime, timedelta
from pytz import timezone
from werkzeug.security import generate_password_hash

from models import db, Location, Printer, Setting, User
from app import create_app

app = create_app()

with app.app_context():
    db.drop_all()
    if os.environ.get("WIPE_NYUP_DB"):
        sys.exit(0)
    db.create_all()

with open('seed/locations.json', 'r') as file:
    location_sample_data = json.load(file)

with open('seed/printers.json', 'r') as file:
    printer_sample_data = json.load(file)

with open('seed/settings.json', 'r') as file:
    settings_sample_data = json.load(file)

with open('seed/meta.json', 'r') as file:
    meta_sample_data = json.load(file)

printers = []
locations = []
settings = []

for resp in location_sample_data:
    loc = Location(
        name=resp['name'],
        short_name=resp['short_name'],
        description=resp['description'],
        visible=resp['visible'],
    )
    locations.append(loc)

with app.app_context():
    db.session.add_all(locations)
    db.session.commit()

with app.app_context():
    locations = Location.query.all()

get_datetime = lambda t: datetime.now(timezone('UTC')) - timedelta(hours=(0.2 + random()) * t)

for printer_resp, meta_resp in zip(printer_sample_data, meta_sample_data):
    p_resp = printer_resp['response']
    m_resp = meta_resp['meta']
    printer = Printer(
        name=m_resp['name'],
        brand=m_resp['brand'],
        model=m_resp.get('model'),
        type=m_resp.get('type'),
        serial=m_resp.get('serial'),
        ip_address=m_resp['ip'],
        current_state=json.dumps({**p_resp}),
        last_state=json.dumps({**m_resp.get('last_state', {})}),
        last_online=get_datetime(0) if p_resp['status'] == 'success' else get_datetime(24),
        location=choice(locations),
        comment=m_resp.get('comment'),
    )

    printers.append(printer)

with app.app_context():
    db.session.add_all(printers)
    db.session.commit()

for pref in settings_sample_data:
    setting = Setting(
        key=pref['key'],
        value=pref['value'],
        default_value=pref['default_value'],
        type=pref['type'],
        description=pref['description']
    )
    settings.append(setting)

with app.app_context():
    db.session.add_all(settings)
    db.session.commit()

user1 = User(
    netid='admin',
    name='Super User',
    password=generate_password_hash('admin', "pbkdf2:sha256"),
    type='superuser',
    location=locations[0],
    )
user2 = User(
    netid='user',
    name='Standard User',
    password=generate_password_hash('user', "pbkdf2:sha256"),
    type='user',
    location=choice(locations),
    )
with app.app_context():
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
