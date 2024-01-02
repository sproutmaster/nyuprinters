from statusd._statusd import db


class Printer(db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)

    last_status = db.Column(db.Text, nullable=True)
    last_online = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)

    display = db.Column(db.Boolean, nullable=False, default=True)

    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)

    def __repr__(self):
        return '<Printer %r>' % self.name


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    printers = db.Column(db.Text)

    def get_printer_ids(self) -> list[int]:
        return list(map(int, filter(None, self.printers.split(','))))

    def add_printer_id(self, printer_id) -> bool:
        printer_ids = self.get_printers()
        if printer_id in printer_ids:
            return False
        if len(printer_ids) == 0:
            self.printers = str(printer_id)
        else:
            self.printers += f',{printer_id}'
        return True

    def reorder_printer_ids(self, printer_ids) -> None:
        self.printers = ','.join(map(str, printer_ids))

    def remove_printer_id(self, printer_id) -> bool:
        printer_ids = self.get_printers()
        if printer_id in printer_ids:
            printer_ids.remove(printer_id)
            self.reorder_printers(printer_ids)
            return True
        return False

    def __repr__(self):
        return '<Locations %r>' % self.name


class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(20), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<Settings %r>' % self.key
