#
# -*- coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

import sys
import time
from datetime import datetime
import threading
import feedparser

from PyQt5 import QtWidgets, QtGui, QtCore

class Updater(QtCore.QThread):

    def __init__(self, parent = None):
        super(Updater, self).__init__(parent)
        self.stopped = False
        self.mutex = QtCore.QMutex()

    def setup(self, model):
        self.model = model 
        self.stopped = False

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def restart(self):
        with QMutexLocker(self.mutex):
            self.stopped = False

    def run(self):

        rssurl = "http://headlines.yahoo.co.jp/rss/asahik-dom.xml"
        #rssurl = "http://news.yahoo.co.jp/biz/rss/category/economy.xml"
        while 1:
            fdp = feedparser.parse(rssurl)
            self.model.clear()
            for entry in fdp['entries']:
                loc = datetime.fromtimestamp(time.mktime(entry.published_parsed) + 60 * 60 * 9)
                t = tuple(loc.timetuple())
                item = QtGui.QStandardItem("{0}/{1:02} {2:02}:{3:02} {4}".format(t[1], t[2], t[3], t[4], entry.title))
                self.model.appendRow(item)

            time.sleep(5)

        self.stop()
        self.finished.emit()

class mymainwindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        #self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(0.5)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.initUI()

    def initUI(self):
        self.resize(300, 300)
        self.move(900, 10)
        self.setWindowTitle("News")
        
        self.list = QtWidgets.QListView()
        self.model = QtGui.QStandardItemModel(self.list)
        self.list.setModel(self.model)
        self.setCentralWidget(self.list)

        self.up = Updater()
        self.up.setup(self.model)
        self.up.start()




app = QtWidgets.QApplication(sys.argv)
#app.setWindowIcon(QtGui.QIcon('bomb.png'))
mywindow = mymainwindow()
mywindow.show()
app.exec_()

