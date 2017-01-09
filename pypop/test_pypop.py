#
# -*- coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

import os
import sys

working_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = os.path.join(working_dir, r"..\poppler-0.50\bin;") + os.environ["PATH"]

sys.path.append(r".\build\lib.win32-2.7")

import pypop

print("version:", pypop.version())

f = open("./test/color.pdf", "rb")
b = f.read()
f.close()
print(len(b))
n = pypop.get_num_of_pages(b)
print(n)
w, h, bpr, d = pypop.render(b, 0, 10)
print(w, h, bpr)

