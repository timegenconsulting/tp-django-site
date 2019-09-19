from setuptools import setup
from setuptools.command.test import test as TestCommand

import codecs
import os
import sys
import re


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    """
    Reads out software version from provided path(s).
    """
    version_file = read(*file_paths)
    lookup = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                       version_file, re.M)

    if lookup:
        return lookup.group(1)

    raise RuntimeError("Unable to find version string.")


class PyTest(TestCommand):
    """
    Allows python setup.py test to work properly.
    """
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    # def finalize_options(self):
    #     TestCommand.finalize_options(self)
    #     self.test_args = ['--strict', '--verbose', '--tb=long']
    #     # self.test_suite = True

    def run_tests(self):
        import shlex
        import pytest

        # error_code = pytest.main(self.test_args)
        args = ['--strict', '--verbose', '--tb=long']
        print(self.pytest_args)
        if self.pytest_args:
            print(shlex.split(self.pytest_args))
            args += shlex.split(self.pytest_args)
            print(args)
        error_code = pytest.main(args)
        sys.exit(error_code)


setup(
    # replace " service " with the correct service
    # package info

    #name="Service",  # project name
    version=find_version('fireservice', '__init__.py'),
    description="",
    long_description=read('README.md'),
    author='Nebojsa Mrkic',
    author_email='nebojsa@bridgewaterlabs.com',
    url='',

    # install dependencies
    
    #packages=['Service'],
    install_requires=[
        'pika==1.0.1',
        'pyyaml==3.13',
        'mongoengine==0.16.3'
    ],

    # development dependencies
    cmdclass={'test': PyTest},
    tests_require=['pytest'],
    extras_require={
        'testing': ['pytest']
    },
    # descriptions
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
