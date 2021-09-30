import os

from flask import Flask
from werkzeug.middleware.shared_data import SharedDataMiddleware
#from flask_sqlalchemy import SQLAlchemy

from .constants import KAMI_VERSION, KAMI_OPT_VERB, KAMI_OPT_TRUNC, KAMI_OPT_PERC, KAMI_OPT_ROUND

pwd = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(pwd, 'templates')
static = os.path.join(pwd, 'static')

app = Flask(__name__,  template_folder=templates, static_folder=static)
app.config['SECRET_KEY'] = '5F3EAXjUf?%,)h#R92y9aq5'

app.config["KAMI_OPT_VERB"] = KAMI_OPT_VERB
app.config["KAMI_OPT_TRUNC"] = KAMI_OPT_TRUNC
app.config["KAMI_OPT_PERC"] = KAMI_OPT_PERC
app.config["KAMI_OPT_ROUND"] = KAMI_OPT_ROUND
app.config['KAMI_VERSION'] = KAMI_VERSION

from .routes import index
from .errorhandler import cant_find_page, server_unavailable

