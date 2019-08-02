"""
Django settings for Terra Porta project.
"""
from .common import *  # noqa
import os


DEBUG = True
STATIC_ROOT = 'app/static/'
STATIC_URL = '/api/static/'

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(',')
SECRET_KEY = 'f+9&iu8d8fhsljo*#hxha9#kley-7d&pu*-*5$m*wb4iajhs+x'
SITE_URL = os.getenv('SITE_URL')

CORS_ORIGIN_WHITELIST = (os.getenv("ALLOWED_CORS"),)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_ADDR'),
        'PORT': os.getenv('POSTGRES_PORT')
    }
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            "PASSWORD": os.getenv('REDIS_PASSWORD'),
            'DB': os.getenv('REDIS_DB'),
        },
    },
}

CELERY_BROKER_URL = 'redis://{}/{}'.format(os.getenv('REDIS_URL'), os.getenv('REDIS_CELERY'))
CELERY_RESULT_BACKEND = 'redis://{}/{}'.format(os.getenv('REDIS_URL'), os.getenv('REDIS_CELERY'))

IOTA_USER = os.getenv('IOTA_USER')
IOTA_PASSWORD = os.getenv('IOTA_PASSWORD')
IOTA_VERIFY_URL = os.getenv('IOTA_VERIFY_URL')
IOTA_LOGIN = os.getenv("IOTA_LOGIN")

STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRYPE_SECRET_KEY = os.getenv("STRYPE_SECRET_KEY")
