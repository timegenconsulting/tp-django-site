
from .common import *  # noqa


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'terraporta_db',
        'USER': 'terraporta',
        'PASSWORD': 'terraPorta',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TEST': {
            'NAME': 'api_test'
        }
    }
}
