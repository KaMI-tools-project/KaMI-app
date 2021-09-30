import glob
import os
import random

from flask import render_template, request, send_file, send_from_directory, url_for, redirect, flash
from werkzeug.utils import secure_filename

from .app import app
#from .aspyrelib import aspyre

from kami.Kami import Kami

# ROUTES ##############################################################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    """Generate the index page and handles comparing 2 strings with KaMI"""
    error = None

    if request.method == "POST":
        print(request.__dict__)
    return render_template('page/index.html', title="KaMI App | Upload", kami_version = app.config['KAMI_VERSION'], error=error)
