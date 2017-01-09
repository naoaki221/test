#
# -*- coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

import os
import sys

os.environ["PATH"] = r".\pypop_dist;" + os.environ["PATH"]
sys.path.append(r".\pypop_dist")

from PyQt4 import QtCore, QtGui
import imageviewer

if __name__ == '__main__':

    import sys

    program_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
    print(program_name)

    app = QtGui.QApplication(sys.argv)
    imageViewer = imageviewer.ImageViewer(program_name)
    imageViewer.show()
    sys.exit(app.exec_())

