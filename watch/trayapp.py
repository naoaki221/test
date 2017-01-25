#
# coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import sys
import time
import threading

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

stopped = False

class Job:
    def __init__(self):
        self.w = QWidget()
        self.w.setAttribute(Qt.WA_ShowWithoutActivating)
        self.w.setFocusPolicy(Qt.NoFocus); 
        self.w.resize(120, 120)
        self.w.move(10, 10)

    def exit(self):
        global stopped
        stopped = True
        QCoreApplication.exit()
    
    def run(self):
        global stopped
        print(time.ctime())
        self.w.show()
        time.sleep(3)
        #self.w.hide()
        if not stopped:
            threading.Timer(1, self.run).start()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    job = Job()

    trayIcon = QSystemTrayIcon(QIcon("icon.ico"))
    menu = QMenu("Menu")
    exitAction = menu.addAction("Exit")
    exitAction.triggered.connect(exit)
    trayIcon.setContextMenu(menu)
    trayIcon.show()
    job.run()
    sys.exit(app.exec_())

