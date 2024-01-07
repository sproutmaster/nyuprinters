from flask_sqlalchemy import SQLAlchemy
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

    def __repr__(self):
        return f'<Location {self.id}, {self.name}>'


def eastern_time(dt):
    return dt.astimezone(timezone('US/Eastern')).strftime('%H:%M:%S, %a %d %b %Y') if dt else ''


class Printer(db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    model = db.Column(db.String(30))
    serial = db.Column(db.String(30))
    ip_address = db.Column(db.String(15), nullable=False)
    current_state = db.Column(db.Text)
    last_state = db.Column(db.Text)
    last_online = db.Column(db.DateTime())
    last_updated = db.Column(db.DateTime(), server_default=func.now(), onupdate=func.now())
    display = db.Column(db.Boolean, default=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='CASCADE', onupdate='CASCADE'))

    @property
    def info(self):
        cur_state = json_loads(self.current_state) if self.current_state else ''
        print(self.last_updated.astimezone(timezone('US/Eastern')))
        meta = {
            'id': self.id,
            'name': self.name,
            'location': self.location.short_name,
            'last_online': eastern_time(self.last_online),
            'last_updated': eastern_time(self.last_updated),
        }

        return {
            'meta': meta,
            'data': cur_state,
        }

    def __repr__(self):
        return f'<Printer {self.id}, {self.name}, {self.ip_address} at Location<{self.location_id}>>'


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(25), nullable=False, unique=True)
    value = db.Column(db.Text)
    default_value = db.Column(db.Text)
    type = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Setting {self.key}: {self.value}>'
