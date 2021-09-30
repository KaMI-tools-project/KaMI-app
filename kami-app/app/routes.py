import glob
import os
import random

from flask import render_template, request, send_file, send_from_directory, url_for, redirect, flash
from werkzeug.utils import secure_filename

from .app import app
#from .aspyrelib import aspyre


# CONTROL FUNCTIONS ###################################################################################################


# ROUTES ##############################################################################################################
# docs:
# see https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
# and above all: https://www.youtube.com/watch?v=6WruncSoCdI
@app.route('/', methods=['GET'])#, 'POST'])
def index():
    """Generate the index page and handle loading and transforming a zip file before serving it to the client"""
    error = None
    """if request.method == "POST":
        if request.files:
            # controlling uploaded file
            # under max size
            if not allowed_filesize(request.cookies.get('filesize')):
                print("File exceeded maximum size")
                flash("File exceeded maximum size", "error")
                error = "File exceeded maximum size"
                return redirect(request.url)

            zipfile = request.files["zipfile"]

            # named file
            if zipfile.filename == "":
                print("File must have a name")
                flash("File must have a name", "error")
                error = "File must have a name"
                return redirect(request.url)

            # allowed file extension
            if not allowed_file(zipfile.filename):
                print("That file extension is not allowed")
                flash("That file extension is not allowed", "error")
                error = "That file extension is not allowed"
                return redirect(request.url)
            else:
                # last cleaning with werkzeug
                filename = secure_filename(zipfile.filename)
                # saving uploaded file in a newly generated folder
                upload_id = generate_upload_id()
                dest = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
                os.mkdir(dest)
                zipfile.save(os.path.join(dest, filename))

                # TODO @aspyre: verify the content of the file and unzip it if it's safe
                if not allowed_zip_content(os.path.join(dest, filename)):
                    print("That zip file is too dangerous")
                    flash("That zip file is too dangerous", "error")
                    error = "That zip file is too dangerous"
                    return redirect(request.url)

                unpack_dest = os.path.join(dest, 'unpack')
                os.mkdir(unpack_dest)
                flag, msg = safely_unzip(dest, filename, unpack_dest)
                if flag == 'error':
                    print(msg)
                    flash(msg, "error")
                    error = msg
                    return redirect(request.url)

                # orig_destination should be the folder containing "mets.xml"
                mets_location = os.path.join(unpack_dest, os.path.join('**', 'mets.xml'))
                if not len(mets_location) > 0:
                    # this shouldn't happen, but just in case...
                    print("Could not find mets.xml, something must've gone wrong during unzipping step")
                    flash("An unexpected error occurred. Make sure the zip file was produced by Transkribus.", "error")
                    error = "An unexpected error occurred. Make sure the zip file was produced by Transkribus."
                    return redirect(request.url)

                # apply Aspyre processing and save to repack directory
                mets_location = os.path.dirname(glob.glob(mets_location, recursive=True)[0])
                repack_dest = os.path.join(dest, 'repack')
                os.mkdir(repack_dest)
                aspyre_report = {"msg":"coucou", "failed":False} 
                #aspyre.main(orig_source=mets_location, orig_destination=repack_dest, talktome=False)
                print(aspyre_report)

                if aspyre_report["failed"] is True:
                    print("Something went wrong retrieving the files, Aspyre failed.")
                    print(aspyre_report["msg"])
                    flash(aspyre_report['msg'], "error")
                    error = aspyre_report['msg']
                    return redirect(request.url)


                # create the zip file containing the modified documents
                export_zip = zip_dir(upload_id, repack_dest, dest)
                # send it back to client
                return send_file(export_zip, as_attachment=True)
    """
    # if GET...
    return render_template('page/index.html', title="KaMI App | Upload", kami_version = app.config['KAMI_VERSION'], error=error)
