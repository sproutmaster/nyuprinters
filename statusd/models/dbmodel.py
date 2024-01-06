try:
    from statusd._statusd import db
except ModuleNotFoundError:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://admin:admin@localhost:5432/nyup"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    db = SQLAlchemy(app)

from sqlalchemy.sql import func


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    short_name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text)
    printers = db.relationship('Printer', backref=db.backref('location'))

    def __repr__(self):
        return f'<Location {self.id}, {self.name}>'


class Printer(db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    model = db.Column(db.String(30))
    serial = db.Column(db.String(30))
    ip_address = db.Column(db.String(15), nullable=False)
    current_state = db.Column(db.Text)
    last_state = db.Column(db.Text)
    last_online = db.Column(db.DateTime(timezone=True))
    last_updated = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    display = db.Column(db.Boolean, default=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='CASCADE', onupdate='CASCADE'))

    def __repr__(self):
        return f'<Printer {self.id}, {self.name}, {self.ip} at Location<{self.location_id}>>'


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
