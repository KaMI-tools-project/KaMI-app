import os
import kami

#UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
#ALLOWED_EXTENSIONS = set(['txt'])
#MAX_FILESIZE = 500000000 #  Allowing 500 MB max

KAMI_OPT_VERB = False
KAMI_OPT_TRUNC = True
KAMI_OPT_PERC = True
KAMI_OPT_ROUND = '0.001'

KAMI_VERSION = kami.__version__
