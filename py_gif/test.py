#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import os
import sys
import time
from datetime import datetime
import re

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PIL import Image

im = Image.open("test.gif").convert("RGBA")
data = im.tobytes("raw", "RGBA") # the tostring() function is out of the loop
#while True:
imQt = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)

class Main(QMainWindow):

    def __init__(self):
        super().__init__()

        cw = QLabel(self)
        cw.setPixmap(QPixmap.fromImage(imQt))
        self.setCentralWidget(cw)
        self.setGeometry(50, 50, 300, 300)
        self.setWindowTitle('Main')    
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())

