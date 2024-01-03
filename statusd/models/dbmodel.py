from statusd._statusd import db
from sqlalchemy.sql import func


class Printer(db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)

    last_status = db.Column(db.Text, nullable=True)
    last_online = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_updated = db.Column(db.DateTime, nullable=True)

    display = db.Column(db.Boolean, nullable=False, default=True)

    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    location_short = db.relationship('Location', backref=db.backref('printers', lazy=True))

    def __repr__(self):
        return '<Printer %r>' % self.name


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    short_name = db.Column(db.String(15), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    printers = db.relationship('Printer', backref=db.backref('locations', lazy=True))

    def __repr__(self):
        return '<Locations %r>' % self.name


printer_locations = db.Table('printer_locations',
                             db.Column('printer_id', db.Integer, db.ForeignKey('printers.id')),
                             db.Column('location_id', db.Integer, db.ForeignKey('locations.id'))
                             )


class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(20), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<Settings %r>' % self.key
