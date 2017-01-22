#
# coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

# needs libiconv-2.dll in gow

import os
import sys
import shutil

from distutils.core import setup, Command, Extension

class PreInstall(Command):
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        tgt_dir = "dist"
        if not os.path.exists(tgt_dir):
            os.mkdir(tgt_dir)
        src_dir = "lib"
        for fn in os.listdir(src_dir):
            shutil.copy2(os.path.join(src_dir, fn), tgt_dir)
        
        src_dir = "poppler-0.50/bin"
        for fn in os.listdir(src_dir):
            if fn.lower().endswith("dll"):
                shutil.copy2(os.path.join(src_dir, fn), tgt_dir)

        src_dir = "build/lib.win32-3.4"
        for fn in os.listdir(src_dir):
            shutil.copy2(os.path.join(src_dir, fn), tgt_dir)
    
class Clean2(Command):
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        shutil.rmtree("dist")

setup(
    name = 'pypop3', 
    version = '1.0',
    cmdclass = {
        'preinst': PreInstall,
        'clean2': Clean2,
    },
    ext_modules = [Extension('pypop3', ['pypop3.cpp'], 
        include_dirs = [r".\poppler-0.50\include\poppler\cpp"],
        library_dirs = [r'.\poppler-0.50\lib'],
        libraries  =['poppler.dll', 'poppler-cpp.dll'],
        depends=['.\depends\libiconv-2.dll'],
        )]
)

