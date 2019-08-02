"""
Common routines functions
"""
from fabric.api import local
from fabric.colors import red
from fabric.contrib import django

# sets up DJANGO_SETTINGS_MODULE
django.settings_module('terraPorta.settings.test')


def _manage(command, settings='terraPorta.settings.test'):
    """
    Runs manage.py with given parameters

    Arguments:
    - `command`: command to execute
    - `settings`: settings to use (defaults to development)
    """
    print(command)
    local('python manage.py {} --settings={}'.format(command, settings))


def migrate(*apps):
    """
    Performs migrations for given application list

    Arguments:
    - `apps`: applications to migrate
    """
    # First sync db
    print(apps)

    if len(apps) > 0:
        for app in apps:
            try:
                _manage('migrate %s' % app)
            except Exception as e:
                print(red('Failed to migrate {} app! {}'.format(app, str(e))))
    else:
        _manage('migrate')


def makemigrations(*apps):
    """
    Performs migrations for given application list

    Arguments:
    - `apps`: applications to migrate
    """
    # First sync db
    print(apps)

    if len(apps) > 0:
        for app in apps:
            try:
                _manage('makemigrations %s' % app)
            except Exception as e:
                print(red('Failed to migrate {} app! Exception: {}'.format(app, str(e))))
    else:
        _manage('makemigrations')


def create_user():
    """
    Executes module tests
    """
    _manage('createsuperuser', settings='terraPorta.settings.test')


def test(*test):
    """
    Executes module tests
    """
    _manage('test {}'.format(' '.join(test)), settings='terraPorta.settings.test')
    local('python -m flake8 --max-line-length=180 --exclude .git,__pycache__,migrations,__init__.py,settings')


def run(*port):
    """
    Starts the development server
    """
    print(port)
    if port:
        port = port[0]
    else:
        port = 8000
    external_ip = '0.0.0.0:{}'.format(port)
    _manage('runserver %s' % external_ip)
