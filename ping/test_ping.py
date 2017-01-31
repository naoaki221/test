#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import os
import sys
import time
from datetime import datetime
import re

#working_dir = os.getcwd() 
#os.environ["PATH"] = os.path.join(working_dir, r".\build\lib.win32-3.4;") + os.environ["PATH"]
sys.path.append(r".\build\lib.win32-3.4")
import ping

res = ping.ping("8.8.8.8")
print(res)
