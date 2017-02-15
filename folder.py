#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import os
import sys
import time
from datetime import datetime
import re
from shutil import copyfile

from tinydb import TinyDB, Query

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Tree1(QTreeView):
    def __init__(self):
        QTreeView.__init__(self)
        self.setWindowTitle("Documents")

        model = QFileSystemModel()
        model.setRootPath("")
        self.setModel(model)

        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 100)

class Main(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Directory")    

        font = QFont()
        #font.setWeight(QFont.DemiBold)
        font.setPixelSize(16)

        self.tree1 = Tree1()
        self.tree1.setFont(font)

        cw = QWidget(self)

        ly1 = QVBoxLayout()
        ly1.addWidget(self.tree1)
        cw.setLayout(ly1)
        self.setCentralWidget(cw)


self.resize(800,400)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Main()
    w.show()
    #self.tree1.model().setRootPath("")
    #self.tree1.setRootIndex(self.tree1.model().index(""))
    sys.exit(app.exec_())

