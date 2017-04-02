#
# -*- coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

import os
import sys
import StringIO
from PyQt4 import QtCore, QtGui

cpos = [
    [13,142],
    [161,142],
    [309,142],
    [13,213],
    [161,213],
    [309,213],
    [13,283],
    [161,283],
    [309,283],
    [13,389],
    [161,389],
    [309,389],
    [13,459],
    [161,459],
    [309,459],
]

class CheckBox2(QtGui.QAbstractButton):
    def __init__(self, parent):
        super(CheckBox2, self).__init__(parent)
        self.setCheckable(True)
        self.resize(30, 30)
        

    def paintEvent(self, evt):
        painter = QtGui.QPainter(self)
        if self.isChecked():
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 3))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.green, 3))
        painter.drawRect(5, 5, 25, 25)
        

class ImageViewer(QtGui.QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()

        self.res = {}
        self.scaleFactor = 0.0

        self.imageLabel = QtGui.QLabel()

        self.pane = QtGui.QWidget()
        self.pane.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.li = QtGui.QListWidget()
        self.li.setFixedWidth(200)

        lh = QtGui.QHBoxLayout()
        lh.addWidget(self.li)
        lh.addWidget(self.imageLabel)
        self.pane.setLayout(lh)
        self.setCentralWidget(self.pane)

        self.createActions()
        self.createMenus()

        self.li.itemDoubleClicked.connect(self.selectDoc)
        #self.setWindowTitle("Image Viewer - " + self.program_name)

        self.resize(800, 720)

        #lbl1 = CheckBox2(self.imageLabel)
        #lbl1.move(15, 10)
        self.cc = []
        for p in cpos:
            lbl = CheckBox2(self.imageLabel)
            lbl.move(p[0], p[1])
            lbl.hide()
            self.cc += [lbl]

    def selectDoc(self):
        print(self.li.currentItem().text())
        n = self.li.currentItem().text()
        image = QtGui.QImage(".\\results\\" + n + ".png")
        w = image.size().width()
        h = image.size().height()
        self.scaleFactor = 700.0 / h
        print(w, h)
        image_scaled = image.scaled(w * self.scaleFactor, h * self.scaleFactor, QtCore.Qt.KeepAspectRatio)
        print(w * self.scaleFactor, h * self.scaleFactor)
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image_scaled))

        for i, p in enumerate(cpos):
            x = p[0] * self.scaleFactor
            y = p[1] * self.scaleFactor
            self.cc[i].move(x, y)
            self.cc[i].show()

        #self.imageLabel.scaleFactor = 1.0
        #self.imageLabel.scaleFactor *= factor
        #self.imageLabel.resize(0.1 * self.imageLabel.pixmap().size())

        #self.saveAct.setEnabled(True)
        #self.fitToWindowAct.setEnabled(True)
        #self.updateActions()
        #if not self.fitToWindowAct.isChecked():
        #    self.imageLabel.adjustSize()

    def open(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())

        self.res = {}
        if fileName:
            self.li.clear()
            f = open(fileName, "r")
            f.readline()
            for _l in f.readlines():
                l = _l.rstrip().split(",")
                self.res[l[0]] = l[1:]
            f.close()
            print(self.res)
            for i, k in enumerate(sorted(self.res.keys())):
                ni = QtGui.QListWidgetItem()
                ni.setText(k)
                self.li.insertItem(i, ni)

    def fitToWindow(self):
        #fitToWindow = self.fitToWindowAct.isChecked()
        #self.scrollArea.setWidgetResizable(fitToWindow)
        #if not fitToWindow:
        #    self.normalSize()

        self.updateActions()

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.fitToWindowAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.imageLabel.scaleFactor *= factor
        self.imageLabel.resize(self.imageLabel.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.imageLabel.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.imageLabel.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())

