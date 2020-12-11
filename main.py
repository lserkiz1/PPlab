from flask import Flask
from flask_bcrypt import Bcrypt
from sqlalchemy.orm.exc import NoResultFound

from blueprint import api_blueprint
from ercheck import not_found, server_error

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'

app.register_blueprint(api_blueprint, url_prefix="/api/v1")

app.register_error_handler(NoResultFound, not_found)
app.register_error_handler(Exception, server_error)

bcrypt = Bcrypt(app)