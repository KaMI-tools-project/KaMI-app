import os
import kami

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
ALLOWED_EXTENSIONS = set(['txt'])
MAX_FILESIZE = 500000000 #  Allowing 500 MB max

#TODO add KaMI version
KAMI_VERSION = kami.__version__
