from flask import render_template, url_for

from .app import app

@app.errorhandler(404)
def cant_find_page(error):
    """Redirect to 404.html"""
    return render_template("error/404.html", title="KaMI App | Error 404", kami_version = app.config['KAMI_VERSION']), 404

@app.errorhandler(500)
def server_unavailable(error):
    """Redirect to 500.html"""
    return render_template("error/500.html", title="KaMI App | Error 500", kami_version = app.config['KAMI_VERSION'])