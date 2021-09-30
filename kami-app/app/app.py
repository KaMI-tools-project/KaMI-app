import os

from flask import Flask
from werkzeug.middleware.shared_data import SharedDataMiddleware
#from flask_sqlalchemy import SQLAlchemy

from .constants import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILESIZE, KAMI_VERSION

pwd = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(pwd, 'templates')
static = os.path.join(pwd, 'static')

app = Flask(__name__,  template_folder=templates, static_folder=static)
app.config['SECRET_KEY'] = '5F3EAXjUf?%,)h#R92y9aq5'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['MAX_FILESIZE'] = MAX_FILESIZE

app.config['KAMI_VERSION'] = KAMI_VERSION

from .routes import index
from .errorhandler import cant_find_page, server_unavailable

