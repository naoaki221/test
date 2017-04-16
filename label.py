#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class QLabel2(QLabel):
    def __init__(self, parent = None):
        super(QLabel2, self).__init__(parent)
        self.pos_offset = None
        newfont = QFont("Times", 14, QFont.Bold) 
        self.setFont(newfont)
        self.selected = False

    def mousePressEvent(self, event):
        self.pos_offset = event.pos()
        self.selected = True

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            pos = self.mapToGlobal(event.pos())
            pos2 = self.parent().mapToGlobal(QPoint(0, 0))
            #self.move(pos.x() - pos2.x(), pos.y() - pos2.y())
            self.move(pos.x() - pos2.x() - self.pos_offset.x(), pos.y() - pos2.y() - self.pos_offset.y())

        
#class DropWidget(QWidget):
class DropWidget(QMainWindow):
    def __init__(self, parent = None):
        super(DropWidget, self).__init__(parent)
        self.setAcceptDrops(True)

        self.canvas = QWidget(self)
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.canvas)
        self.setCentralWidget(self.scrollArea)
        self.canvas.resize(1000, 1000)

        self.list_of_labels = []

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            #pos = self.mapToGlobal(event.pos())
            pos = event.pos()
            #w = QLabel2(self)
            w = QLabel2(self.canvas)
            self.list_of_labels += [w]
            w.setText("hello")
            w.move(pos.x(), pos.y())
            w.show()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore() 

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            #path = url.toLocalFile().toLocal8Bit().data()
            path = url.toLocalFile()
            if os.path.isfile(path):
                pos = event.pos()
                #w = QLabel2(self)
                w = QLabel2(self.canvas)
                self.list_of_labels += [w]
                #w.setText(path)
                image = QImage(path)
                pm = QPixmap.fromImage(image).scaled(image.width() / 4, image.height() / 4, Qt.KeepAspectRatio, Qt.FastTransformation)
                w.setPixmap(pm)
                w.move(pos.x(), pos.y())
                w.show()

def main():
    app = QApplication(sys.argv)
    w = DropWidget()
    w.resize(800, 600)
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()

