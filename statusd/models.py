from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
from pytz import timezone
from json import loads as json_loads

db = SQLAlchemy()


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    short_name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text)
    printers = db.relationship('Printer', backref=db.backref('location'))
    visible = db.Column(db.Boolean, default=False)

    def info(self):
        return {
            'id': self.id,
            'name': self.name,
            'short': self.short_name,
            'description': self.description,
            'printer_count': len(self.printers),
            'visible': self.visible,
        }

    def __repr__(self):
        return f'<Location {self.id}, {self.name}>'


def eastern_time(dt):
    return dt.astimezone(timezone('US/Eastern')).strftime('%H:%M:%S, %a %d %b %Y') if dt else ''


class Printer(db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    brand = db.Column(db.String(30))
    model = db.Column(db.String(30))
    type = db.Column(db.String(10))
    serial = db.Column(db.String(30))
    ip_address = db.Column(db.String(15), nullable=False)
    current_state = db.Column(db.Text)
    last_state = db.Column(db.Text)
    last_online = db.Column(db.DateTime(timezone=True))
    last_updated = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='CASCADE', onupdate='CASCADE'))
    comment = db.Column(db.Text)
    visible = db.Column(db.Boolean, default=True)

    @property
    def status(self):
        state = json_loads(self.current_state) if self.current_state else None
        if state:
            return 'Online' if state['status'] == 'success' else state.get('message')
        return 'Provisioning'

    def info(self, admin=False):
        cur_state = json_loads(self.current_state) if self.current_state else {}

        meta = {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'type': self.type,
            'last_online': eastern_time(self.last_online),
            'last_updated': eastern_time(self.last_updated),
            'location': self.location.short_name,
            'comment': self.comment,
            'visible': self.visible,
        }

        if admin:
            meta['ip'] = self.ip_address
            meta['serial'] = self.serial

        return {
            'meta': meta,
            'response': cur_state,
        }

    def __repr__(self):
        return f'<Printer {self.id}, {self.name}, {self.ip_address} at Location<{self.location_id}>>'


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(40), nullable=False, unique=True)
    value = db.Column(db.Text)
    default_value = db.Column(db.Text)
    type = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text)

    def info(self):
        return {
            'key': self.key,
            'value': self.value,
            'default_value': self.default_value,
            'type': self.type,
            'description': self.description,
        }

    def __repr__(self):
        return f'<Setting {self.key}: {self.value}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    netid = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(128))
    type = db.Column(db.String(10), nullable=False, default='user')
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='SET NULL', onupdate='CASCADE'))
    location = db.relationship('Location', backref=db.backref('users', lazy=True))
