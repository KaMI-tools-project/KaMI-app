import glob
import os
import random

from flask import render_template, request, send_file, send_from_directory, url_for, redirect, flash
from werkzeug.utils import secure_filename

from .app import app
from .aspyrelib import aspyre


# CONTROL FUNCTIONS ###################################################################################################
def allowed_file(filename) -> bool:
    """Control that file extension is accepted

    :param filename str: name of the file
    :return bool: True if allowed, False otherwise
    """
    if not '.' in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.lower() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_filesize(filesize) -> bool:
    """Control that filesize doesn't exceed what is allowed

    :param filesize str: filesize
    :return bool: True if allowed, False otherwise
    """
    if int(filesize) <= app.config['MAX_FILESIZE']:
        return True
    else:
        return False


def generate_upload_id() -> str:
    """Generate a random and unique 7-digit id

    :return str: generated ID
    """
    existing_ids = os.listdir(app.config['UPLOAD_FOLDER'])
    generated_id = random.randint(100000, 999999)
    iter = 0
    while str(generated_id) in existing_ids and iter < 1000000:  # trying to avoid an infinite loop here
        generated_id = random.randint(100000, 999999)
        iter += 1
    if iter >= 1000000:
        print("We barely avoided an infinite loop during the id generation, you should check that out.")
    print(f"Generated ID: {generated_id}")
    return str(generated_id)


def allowed_zip_content(filename) -> bool:  # TODO: build this function
    """Control if the content of the zip file is secured

    :param filename: path to the zip file
    :return: True if allowed, False otherwise
    """
    from zipfile import ZipFile
    with ZipFile(filename, 'r') as fh:
        files = fh.namelist()
        #print(fh.infolist())
        #files = [f for f in files if not f.split(os.sep)[-1].startswith('.') and f.startswith('.')]
         #files = [f for f in files if not f.startswith('__MACOSX')]
        #TODO @alix: control content of 'files'
        #TODO @security: massive breach of security when it comes to unzipping the zip file
        #for file in files:
        #    print(file)
        #for file in files:
        #    print(file.infolist())
    return True


def safely_unzip(dest, filename, unpack_dest) -> tuple:
    """Unzip a zip file with as many precautions as possible

    :param dest: path to the directory where the uploaded zip file is located
    :param filename: name of the zip file
    :param unpack_dest: path to the directory where the zip file should be unzipped
    :return tuple: ('error', '<message>') if an error occurred, (None, None) otherwise
    """
    from zipfile import ZipFile

    zph = ZipFile(os.path.join(dest,filename), 'r')
    files = zph.infolist()
    ignored_files = []
    # no matter what, we are only interested in xml files
    ignored_files += [f for f in files if not f.filename.lower().endswith('.xml')]
    # ignoring hidden files and folder
    ignored_files += [f for f in files if f.filename.split(os.sep)[-1].startswith('.') or f.filename.startswith('.')]
    # ignoring OSX generated folders
    ignored_files += [f for f in files if f.filename.lower().startswith('__macosx')]
    files = [f for f in files if f not in ignored_files]
    # additional control
    # ignoring files containing .exe, .php or .asp - ex: 'my_suspicious_file.exe.xml' will be ignored
    # note that this might cause unexpected errors TODO: test
    ignored_files += [f for f in files if '.exe' in f.filename.lower() or '.php' in f.filename.lower() or \
                      '.asp' in filename.lower() or '.py' in f.filename.lower()]

    if not 'mets.xml' in [f.filename.split(os.sep)[-1] for f in files]:
        zph.close()
        return "error", "This is not a valid Transkribus Archive"

    for file in files:
        zph.extract(file, path=unpack_dest)
    zph.close()
    print(f"Ignored {len(ignored_files)} files")
    return None, None


def zip_dir(upload_id, repack_dest, dest) -> str:
    """Create a zip file out of a directory

    :param upload_id: unique id given to the upload
    :param repack_dest: path to the directory that should be zipped
    :param dest: path to the the directory where the zip file should be saved
    :return str: path to the created zip file
    """
    from zipfile import ZipFile

    print(f"creating this zip: {os.path.join(dest, f'export_{upload_id}.zip')}")
    zip_name = os.path.abspath(os.path.join(dest, f'export_{upload_id}.zip'))
    ziph = ZipFile(zip_name, 'w')
    for file in os.listdir(repack_dest):
        ziph.write(os.path.join(repack_dest, file), arcname=os.path.join("ALTO4eScriptorium", file))
    ziph.close()
    return zip_name


# ROUTES ##############################################################################################################
# docs:
# see https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
# and above all: https://www.youtube.com/watch?v=6WruncSoCdI
@app.route('/', methods=['GET', 'POST'])
def index():
    """Generate the index page and handle loading and transforming a zip file before serving it to the client"""
    error = None
    if request.method == "POST":
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
                aspyre_report = aspyre.main(orig_source=mets_location, orig_destination=repack_dest, talktome=False)
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
    # if GET...
    return render_template('page/index.html', title="KaMI App | Upload", kami_version = app.config['KAMI_VERSION'], error=error)
