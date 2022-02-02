import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition
include(
    'components/app_definition.py',
)

# Database
include(
    'components/database.py',
)

# Password validation
include(
    'components/password_validation.py',
)

# Internationalization
include(
    'components/internationalization.py',
)

# Static files (CSS, JavaScript, Images)
include(
    'components/static_media_files.py',
)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]
