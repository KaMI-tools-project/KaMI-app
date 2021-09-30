import csv
from datetime import datetime
import glob
import os
import random

from flask import render_template, request, send_file, send_from_directory, url_for, redirect, flash
from kami.Kami import Kami
import pandas as pd
from werkzeug.utils import secure_filename

from .app import app



"""
#TODO: implémenter un bouton d'export CSV
# tiré du colab de KaMI
def make_csv():
    name_csv = f"evaluation_report_kami_{metadatas['DATETIME']}_{metadatas['MODEL']}.csv"
    with open(name_csv, 'w')  as csv_file:
        writer = csv.writer(csv_file, 
                            delimiter=',',
                            quotechar='|', 
                            quoting=csv.QUOTE_MINIMAL)
    for key, value in metadatas.items():
        row = []
        row.append(key)
        row.append(value)
        writer.writerow(row)
        df_metrics.to_csv(name_csv, mode='a', header=True)
        files.download(name_csv)
"""

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


def make_dataframe(score_board, reference):
    metadata_keys = ['levensthein_distance_char', 'levensthein_distance_words', 'hamming_distance',  'wer',  'cer',  'wacc',  'mer',  'cil',  'cip',  'hits',  'substitutions',  'deletions',  'insertions']
    now = datetime.now()
    metadatas = {}
    metrics = {}
    metadatas["DATETIME"] = now.strftime("%d_%m_%Y_%H:%M:%S")
    metadatas["IMAGE"] = None  #TODO changer quand implémenté
    metadatas["REFERENCE"] = reference
    metadatas["MODEL"] = None #TODO changer quand implémenté

    for key, value in score_board.items():
        if type(value) != dict and key not in metadata_keys:
            metadatas[key] = value
        else:
            metrics[key] = value
    try:
        df_metrics = pd.DataFrame.from_dict(metrics)
    except:
        df_metrics = pd.DataFrame.from_dict(metrics, orient='index')
    
    tables=[df_metrics.to_html(classes="data")]
    titles=[df_metrics.columns.values]
    return tables, titles

    

# ROUTES ##############################################################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    """Generate the index page and handles comparing 2 strings with KaMI"""
    error = None
    tables = None
    titles = None

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
            tables, titles = make_dataframe(kevaluator.scores.board, kami_form.reference)
        else:
            print("cannot perform evaluation")
            error = "Invalid Form"
    return render_template('page/index.html', title="KaMI App | Upload", kami_version = app.config['KAMI_VERSION'], error=error, tables=tables, titles=titles)

