from .base import *

DEBUG = True

# Allow Django's test client host + any proxy host in development
ALLOWED_HOSTS += ['testserver', 'backend', '0.0.0.0']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

CORS_ALLOW_CREDENTIALS = True
