#
# coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

# needs libiconv-2.dll in gow

import os
import sys
import shutil

from distutils.core import setup, Command, Extension

setup(
    name = "ping", 
    version = "1.0",
    ext_modules = [Extension("ping", ["ping.cpp"], 
        libraries  =["wsock32", "ws2_32", "iphlpapi"],
        )]
)

