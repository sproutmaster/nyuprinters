from flask import render_template
from views import print_status

from app import create_app

app = create_app()

app.register_blueprint(print_status, url_prefix='/')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
