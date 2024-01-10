from views import index, underground
from api import api

from app import create_app

app = create_app()

app.register_blueprint(index, url_prefix='/')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(underground, url_prefix='/underground')


if __name__ == '__main__':
    app.run(debug=True)
