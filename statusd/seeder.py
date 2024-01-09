import os
import sys
import json
import random
from sqlalchemy.sql import func

from models import db, Location, Printer, Setting
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

printers = []
locations = []
settings = []

for raw_resp in location_sample_data:
    loc = Location(name=raw_resp['name'],
                   short_name=raw_resp['short_name'],
                   description=raw_resp['description'])
    locations.append(loc)

with app.app_context():
    db.session.add_all(locations)
    db.session.commit()

with app.app_context():
    locations = Location.query.all()

for raw_resp in printer_sample_data:
    resp = raw_resp['response']
    message = resp['message']
    meta = resp['meta']
    printer = Printer(name=meta['name'],
                      model=message['model'] if message.get('model') else None,
                      serial=meta['serial'] if meta.get('serial') else None,
                      ip_address=meta['ip'],
                      current_state=json.dumps(resp),
                      last_state=json.dumps(resp),
                      last_online=func.now(),
                      location=random.choice(locations)
                      )


    printers.append(printer)

with app.app_context():
    db.session.add_all(printers)
    db.session.commit()

for pref in settings_sample_data:
    setting = Setting(key=pref['key'],
                      value=pref['value'],
                      default_value=pref['default_value'],
                      type=pref['type'],
                      description=pref['description']
                      )
    settings.append(setting)

with app.app_context():
    db.session.add_all(settings)
    db.session.commit()
