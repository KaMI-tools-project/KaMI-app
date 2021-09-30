import glob
import os
import random
#from typing_extensions import Required

from flask import render_template, request, send_file, send_from_directory, url_for, redirect, flash
from werkzeug.utils import secure_filename

from .app import app

from kami.Kami import Kami


class kamiForm():
    def validate(self, form):
        if "prediction" in form and "reference" in form:
            return True

    def __init__(self, form):
        if self.validate(form):
            self.options = []
            self.prediction = form["prediction"]
            self.reference = form["reference"]
            for field in request.form:
                if field == "optdigit":
                    self.options.append("D")
                elif field == "optcase":
                    self.options.append("L")
                elif field == "optponct":
                    self.options.append("P")
                elif field == "optdiac":
                    self.options.append("X")
            self.options = "".join(self.options)


# ROUTES ##############################################################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    """Generate the index page and handles comparing 2 strings with KaMI"""
    error = None
    score_board = None

    if request.method == "POST":
        kami_form = kamiForm(request.form)
        if kami_form:
            print("starting evaluation")
            kevaluator = Kami(
                [kami_form.reference, kami_form.prediction], 
                verbosity=app.config["KAMI_OPT_VERB"], 
                truncate=app.config["KAMI_OPT_TRUNC"],
                percent=app.config["KAMI_OPT_PERC"],
                round_digits=app.config["KAMI_OPT_ROUND"],
                apply_transforms=kami_form.options)
            score_board = kevaluator.scores.board
        else:
            print("cannot perform evaluation")
            error = "Invalid Form"
    return render_template('page/index.html', title="KaMI App | Upload", kami_version = app.config['KAMI_VERSION'], error=error)#, score_board=score_board)

