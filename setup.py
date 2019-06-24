from setuptools import setup
from os.path import join, dirname

setup(
    name='clever_cam_calibration',
    version='1.0',
    py_modules=['clever_cam_calibration'],
    entry_points={
        'console_scripts': ["calibrate_cam = clever_cam_calibration:__calibrate_command",
                            "calibrate_from_dir = clever_cam_calibration:__calibrate_ex_command"]})