import csv
from datetime import datetime
import glob
import os
import random
from numba import jit
from flask import render_template, request, send_file, send_from_directory, url_for, redirect, flash
from kami.Kami import Kami
import pandas as pd
import numpy as np
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

@jit(nopython=True, nogil=True)
def compute_distance(reference, prediction, distance):
    for char_pred in range(1, len(prediction) + 1):
        for char_ref in range(1, len(reference) + 1):
            delt = 1 if prediction[char_pred - 1] != reference[char_ref - 1] else 0
            distance[char_pred, char_ref] = min(distance[char_pred - 1, char_ref - 1] + delt,
                                                distance[char_pred - 1, char_ref] + 1,
                                                distance[char_pred, char_ref - 1] + 1)
    return distance

def show_diff_color_html(reference: str, prediction: str) -> list:
    """Display source and prediction in HTML format and color-code insertions (blue),
    deletions (red), and exact words (green). based on Levensthein algorithm.

    Example
    --------
    >>> show_diff_color_html("Chat", "Chien")
    ["<span style='color:#3CB371'>C</span>", "<span style='color:#3CB371'>h</span>",
    "<span style='color:#4169E1'>i</span>", "<span style='color:#4169E1'>e</span>",
    "<span style='color:#D2122E'>a</span>", "<span style='color:#4169E1'>n</span>",
    "<span style='color:#D2122E'>t</span>"]

    Args:
        reference (str): reference sequence
        prediction (str): prediction sequence

    Returns:
        list: list of HTML tag with color code
    """
    result = []

    # compute distance
    """
    distance = np.zeros((len(prediction) + 1, len(reference) + 1), dtype=int)
    distance[0, 1:] = range(1, len(reference) + 1)
    distance[1:, 0] = range(1, len(prediction) + 1)
    for char_pred in range(1, len(prediction) + 1):
        for char_ref in range(1, len(reference) + 1):
            delt = 1 if prediction[char_pred - 1] != reference[char_ref - 1] else 0
            distance[char_pred, char_ref] = min(distance[char_pred - 1, char_ref - 1] + delt,
                                                distance[char_pred - 1, char_ref] + 1,
                                                distance[char_pred, char_ref - 1] + 1)
    """
    distance = np.zeros((len(prediction) + 1, len(reference) + 1), dtype=int)
    distance[0, 1:] = range(1, len(reference) + 1)
    distance[1:, 0] = range(1, len(prediction) + 1)

    distance = compute_distance(reference, prediction, distance)

    # sequences alignment
    # iterate the matrix's values from back to forward
    char_pred = len(prediction)
    char_ref = len(reference)
    while char_pred > 0 and char_ref > 0:
        diagonal = distance[char_pred - 1, char_ref - 1]
        upper = distance[char_pred, char_ref - 1]
        left = distance[char_pred - 1, char_ref]

        # check back direction
        direction = "\\" if diagonal <= upper and \
                            diagonal <= left else "<-" \
            if left < diagonal and \
               left <= upper else "^"
        char_pred = char_pred - 1 if direction == "<-" or direction == "\\" else char_pred
        char_ref = char_ref - 1 if direction == "^" or direction == "\\" else char_ref

        # Colorize characters with HTML tags
        if (direction == "\\"):
            if distance[char_pred + 1, char_ref + 1] == diagonal:
                # exact match
                result.append(f"<span class='exact-match'>{prediction[char_pred]}</span>")
            elif distance[char_pred + 1, char_ref + 1] > diagonal:
                result.append(f"<span class='delSubts'>{reference[char_ref]}</span>")
                result.append(f"<span class='insertion'>{prediction[char_pred]}</span>")
            else:
                result.append(f"<span class='insertion'>{prediction[char_pred]}</span>")
                result.append(f"<span class='delSubts'>{reference[char_ref]}</span>")
        elif (direction == "<-"):
            result.append(f"<span class='insertion'>{prediction[char_pred]}</span>")
        elif (direction == "^"):
            result.append(f"<span class='delSubts'>{reference[char_ref]}</span>")

    # reverse the list of result
    return result[::-1]



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

    displayable_titles = {0: "Default",
                          "0": "Default",
                          "default":"Default",
                          "non_digits":"Ignoring digits",
                          "lowercase":"Ignoring case",
                          "remove_punctuation":"Ignoring punctuation",
                          "remove_diacritics":"Ignoring diacritics",
                          "all_transforms":"Combining all options"}
    displayable_index = {"cer":"Char. Error Rate (CER)", "wer":"Word Error Rate (WER)",
                        "levensthein_distance_char":"Levensthein Distance (Char.)", 
                        "levensthein_distance_words":"Levensthein Distance (Words)", 
                        "hamming_distance":"Hamming Distance", 
                        "wacc":"Word Accuracy (Wacc)", 
                        "mer":"Match Error Rate (MER)", 
                        "cil":"Char. Information Lost (CIL)", 
                        "cip":"Char. Information Preserved (CIP)", 
                        "hits":"Hits", 
                        "substitutions":"Substitutions", 
                        "deletions":"Deletions", 
                        "insertions":"Insertions"}

    df_metrics.rename(columns=displayable_titles, index=displayable_index, inplace=True)
    
    tables=[df_metrics.to_html(classes="data")]
    titles=[df_metrics.columns.values]
    return tables, titles


def correct_style(tables):
    tables = [table.replace("""<table border="1" class="dataframe data">""", """<table class="dataframe data table table-hover table-bordered">""") for table in tables]
    tables = [table.replace("""<tr style="text-align: right;">""", """<tr>""") for table in tables]
    return tables
    

# ROUTES ##############################################################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    """Generate the index page and handles comparing 2 strings with KaMI"""
    error = None
    tables = None
    titles = None
    reference = ""
    prediction = ""

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
            reference = kevaluator.reference_preprocess
            prediction = kevaluator.prediction_preprocess
            if reference == "":
                reference = kami_form.reference
            if prediction == "":
                prediction = kami_form.prediction
        else:
            print("cannot perform evaluation")
            error = "Invalid Form"

        tables = correct_style(tables)

    return render_template('page/index.html',
                           title="KaMI App",
                           kami_version= app.config['KAMI_VERSION'],
                           reference=reference,
                           prediction=prediction,
                           comparaison=show_diff_color_html(reference, prediction),
                           error=error,
                           tables=tables,
                           titles=titles)

