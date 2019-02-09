#!C:\Users\voval\PycharmProjects\calibration_web_2.7\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'clever-cam-calibration==1.0','console_scripts','calibrate_cam'
__requires__ = 'clever-cam-calibration==1.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('clever-cam-calibration==1.0', 'console_scripts', 'calibrate_cam')()
    )
