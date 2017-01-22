#
# coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import os
import sys

working_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = os.path.join(working_dir, r".\dist;") + os.environ["PATH"]

sys.path.append(r".\dist")

import pypop3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

print("pypop3 version: {}".format(pypop3.version()))
f = open("./test/travelguard_brochure.pdf", "rb")
b = f.read()[:]
f.close()
print("File sieze: {}".format(len(b)))

n = pypop3.get_num_of_pages(b)
print("The number of pages: {}".format(n))

w, h, bpr, d = pypop3.render(b, 0, 50)
print("The geometry(Width, Height, Bits per line) is: ({}, {}, {})".format(w, h, bpr))

image = QImage(d, w, h, bpr, QImage.Format_RGB32).copy()

class Main(QMainWindow):

    def __init__(self):
        super().__init__()

        label = QLabel("", self)
        label.setPixmap(QPixmap.fromImage(image))
        self.setCentralWidget(label)
        self.setGeometry(50, 50, 640, 480)
        self.setWindowTitle('pypop3 test')    
        self.show()

    def mousePressEvent(self, event):
        self.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())

