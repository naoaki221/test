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

class MyFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.already_read = set()
        self.db = TinyDB("already_read_db.json")
        self.backup = "backup"
        if not os.path.exists(self.backup): 
            os.mkdir(self.backup)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        
        if not self.isDir(index):
            if role == Qt.BackgroundRole:
                last_modified = self.fileInfo(index).lastModified().toMSecsSinceEpoch() / 1000
                if (time.time() - last_modified) < 60 * 10:
                    return QColor(255, 204, 204)
                #elif (time.time() - last_modified) < 60 * 60:
                #    return QColor(255, 229, 204)
                #elif (time.time() - last_modified) < 60 * 60 * 3:
                #    return QColor(255, 255, 204)
                elif (time.time() - last_modified) < 60 * 60 * 24:
                    #return QColor(204, 255, 153)
                    return QColor(229, 255, 204)
                else:
                    return super().data(index, role)
            elif role == Qt.ForegroundRole:
                try:
                    File = Query()
                    file_path = self.filePath(index).replace("/", "\\")
                    last_modified = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(os.path.getmtime(self.filePath(index))))
                    results = self.db.search((File.name == file_path) & (File.last_modified == last_modified))
                    if len(results) > 0:
                        return QColor(Qt.black)
                    else:
                        return QColor(Qt.red)
                except:
                    return super().data(index, role)

        return super().data(index, role)

class Tree1(QTreeView):
    def __init__(self):
        QTreeView.__init__(self)
        self.setWindowTitle("Documents")
        self.setSortingEnabled(True)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

        model = MyFileSystemModel()
        model.setRootPath("")
        self.setModel(model)

        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 100)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.buildContextMenu)

        #rootpath = r"C:\Users\naoaki\Desktop\doc\Projects\test_qtreeview\data"
        #model.setRootPath("C:\\")
        #self.setRootIndex(self.model().index(rootpath))

    def buildContextMenu(self, pos):
        selected_files = list(set( \
            [self.model().filePath(index) for index in self.selectionModel().selectedIndexes()] \
        ))
        if len(selected_files) == 1 :
            selected_file = selected_files[0].replace("/", "\\")
            menu = QMenu(self)
            menu.addAction("Open")
            menu.addSeparator()
            menu.addAction("Copy Link")
            menu.addAction("Copy Link 2")
            menu.addSeparator()
            menu.addAction("Change Root")
            menu.addSeparator()
            menu.addAction("Delete")
            action = menu.exec_(self.mapToGlobal(QPoint(pos.x(), pos.y() + menu.size().height())))
            if action:
                if action.text() == "Open":
                    self.openItem(selected_file)
                elif action.text() == "Copy Link":
                    cb = QApplication.clipboard()
                    cb.clear(mode = cb.Clipboard )
                    cb.setText(selected_file, mode = cb.Clipboard)
                elif action.text() == "Copy Link 2":
                    cb = QApplication.clipboard()
                    cb.clear(mode = cb.Clipboard )
                    ctext = "<" + os.path.dirname(selected_file) + ">\n" \
                          + "File: " + os.path.basename(selected_file) + "\n"
                    cb.setText(ctext, mode = cb.Clipboard)
                elif action.text() == "Change Root":
                    pass
                elif action.text() == "Delete":
                    reply = QMessageBox.question(self, "Delete?", "Are you sure?", 
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        removed_time = time.strftime("%Y%m%d_%H%M%S_", time.localtime())
                        copyfile(selected_file, os.path.join(self.model().backup, removed_time + os.path.basename(selected_file)))
                        os.remove(selected_files[0])

    def openItem(self, file_path):
        File = Query()
        last_modified = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
        results = self.model().db.search((File.name == file_path) & (File.last_modified == last_modified))
        if len(results) == 0:
            self.model().db.remove(File.name == file_path)
            self.model().db.insert({'name': file_path, 'last_modified': last_modified})
        os.system("start \"\" \"{}\"".format(file_path))

#class Main(QWidget):
class Main(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Directory")    

        font = QFont()
        #font.setWeight(QFont.DemiBold)
        font.setPixelSize(16)

        self.edit = QLineEdit()
        self.tree1 = Tree1()

        self.edit.setFont(font)
        self.tree1.setFont(font)

        self.edit.returnPressed.connect(self.changeDir)

        cw = QWidget(self)

        ly1 = QVBoxLayout()
        ly1.addWidget(self.edit)
        ly1.addWidget(self.tree1)
        cw.setLayout(ly1)
        self.setCentralWidget(cw)

        self.readOnlyAct = QAction("&Read Only", self, checkable = True, triggered = self.toggleReadOnly)
        self.readOnlyAct.setChecked(True)
        self.menu = QMenu("&Menu", self)
        self.menu.addAction(self.readOnlyAct)
        self.menuBar().addMenu(self.menu)

        self.resize(800,400)

    def toggleReadOnly(self):
        if self.readOnlyAct.isChecked():
            self.tree1.model().setReadOnly(True)
        else:
            self.tree1.model().setReadOnly(False)
    
    def changeDir(self):
        self.tree1.model().setRootPath(self.edit.text())
        self.tree1.setRootIndex(self.tree1.model().index(self.edit.text()))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec_())

