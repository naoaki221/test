#
# -*- coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

# needs libiconv-2.dll in gow

from distutils.core import setup, Extension

setup(name='pypop', version='1.0',  \
      ext_modules=[Extension('pypop', ['pypop.cpp'], 
          include_dirs = [r"..\poppler-0.50\include\poppler\cpp"],
          library_dirs=[r'..\poppler-0.50\lib'],
          libraries=['poppler.dll', 'poppler-cpp.dll'],
          depends=['libiconv-2.dll'],
          )])

