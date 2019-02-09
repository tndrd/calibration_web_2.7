from setuptools import setup
from os.path import join, dirname

setup(
    name='ccc_server',
    version='1.0',
    packages=["ccc_server"],
    entry_points={'console_scripts': ['runserver = ccc_server.app']})
