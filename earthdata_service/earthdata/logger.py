"""
Contains logging configs
"""
import os
import logging.config

# Main system directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Logging setup
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format':
            '{'
                '"date": "%(asctime)s",'
                '"level": "%(levelname)s", '
                '"function": "%(funcName)s",'
                '"filename": "%(filename)s",'
                '"line_no": "%(lineno)d"'
                '"message": "%(message)s"'
            '}',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'oberver': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'models': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'sched': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'parser': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'notifications': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'rabbit.consumer': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'rabbit.publisher': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'rabbit.rpcclient': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        }
    }
}

logging.config.dictConfig(LOGGING)
