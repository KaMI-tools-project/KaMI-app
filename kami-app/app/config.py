# -*- coding: utf-8 -*-

import os
import pkg_resources

from flask import Flask


def pkg_version(name_pkg: str) -> str:
    return pkg_resources.get_distribution(name_pkg).version


BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(BASE, 'templates')
STATIC = os.path.join(BASE, 'static')

app = Flask(__name__,  template_folder=TEMPLATES, static_folder=STATIC)

app.config['SECRET_KEY'] = '5F3EAXjUf?%,)h#R92y9aq5'
app.config['JSON_SORT_KEYS'] = False

app.config["KAMI_OPT_VERB"] = False
app.config["KAMI_OPT_TRUNC"] = True
app.config["KAMI_OPT_PERC"] = True
app.config["KAMI_OPT_ROUND"] = '0.001'
app.config['KAMI_VERSION'] = pkg_version("kamilib-light")

from .views import index, cant_find_page, server_unavailable

