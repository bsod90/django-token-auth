import os

PROJECT_ROOT = os.path.dirname(__file__)

TOKEN_AUTH_PUBLIC_KEY = os.path.join(PROJECT_ROOT, 'data', 'public.pub')
TOKEN_AUTH_PRIVATE_KEY = os.path.join(PROJECT_ROOT, 'data', 'private.pem')


# Minimal django settings setup

SECRET_KEY = 'verysecret'

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'auth_token_db'
TEST_DATABASE_NAME = 'test_auth_toke_db'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'TEST_NAME': TEST_DATABASE_NAME,
    }
}
