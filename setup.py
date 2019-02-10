from setuptools import setup
from os.path import join, dirname

setup(
    name='ccc_server',
    version='1.0',
    packages=["ccc_server, ccc_script"],
    entry_points={
        'console_scripts': ['runserver = ccc_server.app', "calibrate_cam = ccc_script.calibration:__calibrate_command",
                            "calibrate_cam = ccc_script.calibration:__calibrate_ex_command"]})
