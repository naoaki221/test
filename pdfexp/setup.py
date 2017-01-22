#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import os
import sys
from distutils.core import *
import py2exe

import platform
from glob import glob
from distutils.core import *
import py2exe

option = {
    "bundle_files": 3,
    "compressed": 1, 
    "includes" : ["sip", "PyQt5.QtCore"],
}

setup(
    options = {"py2exe": option},
    #console = ["pdfexp.py"],
    windows = [{
        "script" : "pdfexp.py", 
        "icon_resources": [(0, "pdfexp.ico")],
        }],
    zipfile = 'pdfexp.zip', 
    data_files = [
        #('', glob(r'C:\Windows\SYSTEM32\msvcp100.dll')),
        #('', glob(r'C:\Windows\SYSTEM32\msvcr100.dll')),
        ("platforms", [os.path.join(os.path.dirname(sys.executable).replace("\\", "/"), "Lib/site-packages/PyQt5/plugins/platforms/qwindows.dll")])
        ],
)

