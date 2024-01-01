from flask import render_template, redirect, url_for, session
from _statusd import app
from _statusd import project_settings
from admin.routes_ import admin
from print_status.routes import print_status

from api.user import *
from api.printer import *

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(print_status, url_prefix='/print-status')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
