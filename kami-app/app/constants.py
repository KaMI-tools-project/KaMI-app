import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
ALLOWED_EXTENSIONS = set(['zip'])
MAX_FILESIZE = 500000000 #  Allowing 500 MB max

KAMI_VERSION = "0.3"
