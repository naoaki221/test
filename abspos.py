#
# -*- coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

import sys
from PyQt5 import QtGui, QtWidgets, QtCore

class CheckBox2(QtWidgets.QAbstractButton):
    def __init__(self, parent):
        super(CheckBox2, self).__init__(parent)
        self.setCheckable(True)
        self.resize(40, 40)
        

    def paintEvent(self, evt):
        painter = QtGui.QPainter(self)
        if self.isChecked():
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.green, 5))
        painter.drawRect(5, 5, 30, 30)

class Example(QtWidgets.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        lbl1 = CheckBox2(self)
        lbl1.move(15, 10)

        lbl2 = CheckBox2(self)
        lbl2.move(35, 40)

        lbl3 = CheckBox2(self)
        lbl3.move(55, 70)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Absolute')    
        self.show()
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

