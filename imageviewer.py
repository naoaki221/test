#
# -*- coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

import os
import sys
import StringIO
from PyQt4 import QtCore, QtGui

import pypop

#DPI = 100
with open("DPI.txt", "r") as fh:
    DPI = eval(fh.read())

class QLabelEx(QtGui.QLabel):

    def __init__(self, parent = None):
    
        #super().__init__()
        super(QLabelEx, self).__init__()

        QtGui.QLabel.__init__(self, parent)
        self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self.origin = QtCore.QPoint()
        self.drawn = False

        self.scaleFactor = 1.0
    
    def mousePressEvent(self, event):
    
        if event.button() == QtCore.Qt.LeftButton:
       
            p = QtCore.QPoint(event.pos())
            self.origin = QtCore.QPoint(p.x() / self.scaleFactor, p.y() / self.scaleFactor)

            self.drawn = False
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
            self.rubberBand.show()
    
    def mouseMoveEvent(self, event):
    
        if not self.origin.isNull():
            self.rubberBand.setGeometry(\
                    QtCore.QRect(QtCore.QPoint(self.origin.x() * self.scaleFactor, self.origin.y() * self.scaleFactor), \
                    QtCore.QPoint(event.pos())).normalized())
    
    def mouseReleaseEvent(self, event):
    
        if event.button() == QtCore.Qt.LeftButton:
            self.rubberBand.hide()
            p = QtCore.QPoint(event.pos())
            self.end = QtCore.QPoint(p.x() / self.scaleFactor, p.y() / self.scaleFactor)

            self.drawn = True
            self.update()

    def paintEvent(self, event):

        #super(QtGui.QLabel, self).paintEvent(event)
        QtGui.QLabel.paintEvent(self, event)

        if self.drawn == True:
            qp = QtGui.QPainter(self)
            qp.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashDotLine, QtCore.Qt.RoundCap));
            qp.drawRect(QtCore.QRect(QtCore.QPoint(self.origin.x() * self.scaleFactor, self.origin.y() * self.scaleFactor), \
                    QtCore.QPoint(self.end.x() * self.scaleFactor - 1, self.end.y() * self.scaleFactor - 1)));
    

class ImageViewer(QtGui.QMainWindow):
    def __init__(self, program_name):
        super(ImageViewer, self).__init__()

        self.printer = QtGui.QPrinter()
        #self.scaleFactor = 0.0

        self.program_name = program_name
        #self.imageLabel = QtGui.QLabel()
        self.imageLabel = QLabelEx()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Image Viewer - " + self.program_name)

        self.resize(500, 400)

    def open(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())

        if fileName:
            f = open(fileName, "rb")
            b = f.read()
            f.close()
            w, h, bpr, d = pypop.render(b, 0, DPI)
            image = QtGui.QImage(d, w, h, bpr, QtGui.QImage.Format_RGB32).copy()

            if image.isNull():
                QtGui.QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            self.imageLabel.scaleFactor = 1.0

            self.saveAct.setEnabled(True)
            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def save(self):
        byte_array = QtCore.QByteArray()
        buffer = QtCore.QBuffer(byte_array)
        buffer.open(QtCore.QIODevice.WriteOnly)
        self.imageLabel.pixmap().copy( \
            self.imageLabel.origin.x(), \
            self.imageLabel.origin.y(), \
            self.imageLabel.end.x() - self.imageLabel.origin.x() - 1, \
            self.imageLabel.end.y() - self.imageLabel.origin.y() - 1 \
        ).save(buffer, "PNG")
        string_io = StringIO.StringIO(byte_array)
        string_io.seek(0)

        with open(".\\" + self.program_name +".png", "wb") as out_file:
            out_file.write(string_io.read())
        pass

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.imageLabel.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QtGui.QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.saveAct = QtGui.QAction("&Save", self, shortcut="Ctrl+S",
                enabled=False, triggered=self.save)

        self.printAct = QtGui.QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                shortcut="Ctrl+E", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

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

    program_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
    print(program_name)

    app = QtGui.QApplication(sys.argv)
    imageViewer = ImageViewer(program_name)
    imageViewer.show()
    sys.exit(app.exec_())

