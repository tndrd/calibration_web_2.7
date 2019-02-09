from setuptools import setup
from os.path import join, dirname

setup(
    name='ccc_server',
    version='1.0',
    entry_points={'console_scripts': ['runserver = app']})
