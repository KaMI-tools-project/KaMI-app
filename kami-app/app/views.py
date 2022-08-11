# -*- coding: utf-8 -*-

from unicodedata import normalize

from flask import render_template, request, jsonify, flash, redirect, url_for, abort
from kami_light.Kami import Kami

from .config import app
from .utils import serialize_scores, show_diff_color_html


@app.route('/')
@app.route('/compute_results', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        #try:
        response = dict(request.json)
        kevaluator = Kami([
            response['reference'],
            response['prediction']],
            verbosity=app.config["KAMI_OPT_VERB"],
            truncate=app.config["KAMI_OPT_TRUNC"],
            percent=app.config["KAMI_OPT_PERC"],
            round_digits=app.config["KAMI_OPT_ROUND"],
            apply_transforms=response['preprocessingOpts']
        )
        # get preprocess sentences from kami evaluator
        # uncomment to display this sentence
        # in versus text
        """
        reference = kevaluator.reference_preprocess \
            if kevaluator.reference_preprocess != "" \
            else response['reference']
        prediction = kevaluator.prediction_preprocess \
            if kevaluator.prediction_preprocess != "" \
            else response['prediction']
        """
        # test if versustext feature activate by user
        versus_text = {"comparaison": []}
        if bool(response['vtOpt']):
            versus_text = show_diff_color_html(
                normalize("NFKD", str(response['reference'])),
                normalize("NFKD", str(response['prediction']))
            )
        # add this to jsonify if something wrong
        # with show_diff_color_html() : **{"reference": reference, "prediction": prediction},
        return jsonify({**serialize_scores(kevaluator.scores.board),
                        **versus_text
                        }), 200
        #except MemoryError as e:
        #    print(e)
        #    return jsonify({}), 400
    return render_template('page/index.html',
                           title="KaMI App",
                           kami_version=app.config['KAMI_VERSION']), 200


@app.errorhandler(404)
def cant_find_page(error):
    """Redirect to 404.html"""
    return render_template("error/404.html", title="KaMI App | Error 404", kami_version=app.config['KAMI_VERSION']), 404

@app.errorhandler(500)
def server_unavailable(error):
    """Redirect to 500.html"""
    return render_template("error/500.html", title="KaMI App | Error 500", kami_version=app.config['KAMI_VERSION']), 500
