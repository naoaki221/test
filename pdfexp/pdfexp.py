#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

# robocopy src dst /copy:DT /mon:1 /mot:10 /maxage:1 /r:1

# TODO
# * design of memo

import os
import sys
import time
#import math
import sqlite3

working_dir = os.getcwd() #os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = os.path.join(working_dir, r".\pypop3\dist;") + os.environ["PATH"]
sys.path.append(r".\pypop3\dist")

import pypop3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

db = sqlite3.connect("pdf.db") 
c = db.cursor()
c.execute("create table if not exists READ (name text)")
c.execute("create table if not exists MEMO (name text, page integer, x integer, y integer, memo text)")
c.execute("create table if not exists ROT (name text, page integer, angle integer)")
db.commit()

class InputForm(QWidget):
    def __init__(self):# {{{
        super().__init__()
        ly1 = QVBoxLayout()
        self.edit = QTextEdit()
        ly1.addWidget(self.edit)
        ly2 = QHBoxLayout()
        self.ok = QPushButton("OK")
        self.ok.setMinimumHeight(64)
        self.cancel = QPushButton("Cancel")
        self.cancel.setMinimumHeight(64)
        self.cancel.clicked.connect(self.onCancel)
        ly2.addWidget(self.ok)
        ly2.addWidget(self.cancel)
        ly1.addLayout(ly2)
        self.setLayout(ly1)

        self.memoPos = (0, 0)
# }}}
    def onCancel(self):# {{{
        self.edit.clear()
        self.close()
# }}}

class Sub(QWidget):
    def __init__(self):# {{{
        super().__init__()
        self.setGeometry(400, 50, 600, 600)
        self.title = "PDF ({}/{})"

        self.file_path = None
        self.rawData = None
        self.page = 0
        self.last_page = 0
        self.pixmap = None
        self.list_of_memos = []
        self.list_of_memos_del = []
        self.angles = {}

        self.press_pos = None

        self.inputForm = InputForm()
        self.inputForm.ok.clicked.connect(self.recordText)
        self.modifyForm = InputForm()
        self.modifyForm.ok.clicked.connect(self.modifyText)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.buildContextMenu)
# }}}
    def setFile(self, file_path):# {{{
        with open(file_path, "rb") as fh:
            self.rawData = fh.read()[:]
        self.file_path = file_path
        self.last_page = pypop3.get_num_of_pages(self.rawData)
        self.render(0)
# }}}
    def render(self, page):# {{{
        if 0 <= page and page < self.last_page:
            w, h, bpr, d = pypop3.render(self.rawData, page, 10)
            print(w, h)
            if (self.page in self.angles) and (self.angles[self.page] == 0 or self.angles[self.page] == 180):
                ratio_w = self.size().width() / w
                ratio_h = self.size().height() / h
                if ratio_w > ratio_h:
                    dpi = int(10 * ratio_h)
                else:
                    dpi = int(10 * ratio_w)
            else:
                ratio_w = self.size().height() / w
                ratio_h = self.size().width() / h
                if ratio_w > ratio_h:
                    dpi = int(10 * ratio_h)
                else:
                    dpi = int(10 * ratio_w)
            w, h, bpr, d = pypop3.render(self.rawData, page, dpi)
            #self.pixmap = QPixmap.fromImage(QImage(d, w, h, bpr, QImage.Format_RGB32).copy())

            image = QImage(d, w, h, bpr, QImage.Format_RGB32).copy()
            if self.page in self.angles:
                rot = QTransform()
                rot = rot.rotate(self.angles[self.page])
                self.pixmap = QPixmap.fromImage(image.transformed(rot))
            else:
                self.pixmap = QPixmap.fromImage(image)
            #self.resize(self.pixmap.size())
        self.page = page
        self.setWindowTitle(self.title.format(self.page + 1, self.last_page))    
        self.update()
# }}}
    def wheelEvent(self, event):# {{{
        #print(event.angleDelta().y())
        delta = event.angleDelta().y()
        if delta > 0 and self.page > 0:
            self.page -= 1
        elif delta < 0 and self.page < self.last_page - 1:
            self.page += 1
        self.render(self.page)
# }}}
    def mouseDoubleClickEvent(self, event):# {{{
        print("double click")
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            self.inputForm.memPos = (pos.x(), pos.y())
            self.inputForm.show()
# }}}
    def mousePressEvent(self, event):# {{{
        print("mouse pressed")
        self.press_pos = event.pos()
# }}}
    def mouseReleaseEvent(self, event):# {{{
        print("mouse released")
        release_pos = event.pos()
        if self.press_pos:
            delta_x = self.press_pos.x() - release_pos.x()
            delta_y = self.press_pos.y() - release_pos.y()
            if abs(delta_x) > abs(delta_y):
                if abs(delta_x) > 32:
                    if delta_x > 0:
                        self.angles[self.page] = 90
                    else:
                        self.angles[self.page] = 270
            else:
                if abs(delta_y) > 32:
                    if delta_y > 0:
                        self.angles[self.page] = 180
                    else:
                        self.angles[self.page] = 0
        print(self.angles)
        self.render(self.page)
# }}}
    def recordText(self):# {{{
        print("record", self.inputForm.memPos, self.inputForm.edit.toPlainText())
        self.list_of_memos += [[None, self.page, self.inputForm.memPos[0], self.inputForm.memPos[1], self.inputForm.edit.toPlainText()]]
        print(self.list_of_memos)
        self.inputForm.hide()
        self.inputForm.edit.clear()
# }}}
    def modifyText(self):# {{{
        self.list_of_memos[self.modifyForm.index][4] = self.modifyForm.edit.toPlainText()
        self.modifyForm.hide()
        self.modifyForm.edit.clear()
# }}}
    def paintEvent(self, event):# {{{
        QWidget.paintEvent(self, event)
        if self.pixmap:
            painter = QPainter(self)
            font = painter.font()
            font.setWeight(QFont.DemiBold)
            #font.setFamily("Meiryo")
            font.setPixelSize(16)
            painter.setFont(font)
            #painter.setBrush(Qt.red)
            painter.drawPixmap(0, 0, self.pixmap)
            for rowid, page, x, y, text in self.list_of_memos:
                if page == self.page:
                    brect = painter.boundingRect(QRectF(x, y, self.size().width() - x, self.size().height() - y), Qt.AlignLeft, text)
                    #painter.drawText(x, brect.y() + brect.height(), text)
                    painter.setPen(Qt.black)
                    painter.fillRect(QRect(QPoint(brect.x() - 8, brect.y() - 8), QSize(brect.width() + 16, brect.height() + 16)), QColor(255, 255, 153))
                    painter.drawRect(QRect(QPoint(brect.x() - 8, brect.y() - 8), QSize(brect.width() + 16, brect.height() + 16)))
                    painter.setPen(Qt.red)
                    painter.drawText(QRect(QPoint(brect.x(), brect.y()), QSize(brect.width(), brect.height())), Qt.AlignLeft, text)
                    #painter.drawText(brect.x(), brect.y(), text)
            painter.end()
# }}}
    def buildContextMenu(self, pos):# {{{
        found = -1
        print("buildContextMenu", self)
        font = QFont()
        font.setWeight(QFont.DemiBold)
        font.setPixelSize(16)
        fmet = QFontMetrics(font)
        for i, memo in enumerate(self.list_of_memos):
            rowid, page, x, y, text = memo
            if self.page == page:
                brect = fmet.boundingRect(text)
                w = brect.width() - brect.x()
                h = brect.height() - brect.y()
                if x <= pos.x() and pos.x() <= x + w and y <= pos.y() and pos.y() <= y + h:
                    found = i
                    break

        if found >= 0:
            menu = QMenu(self)
            menu.addAction("Modify")
            menu.addAction("Delete")
            action = menu.exec_(self.mapToGlobal(pos))
            if action:
                if action.text() == "Modify":
                    print("modify", found)
                    self.modifyForm.index = found
                    self.modifyForm.edit.setText(self.list_of_memos[found][4])
                    self.modifyForm.show()
                elif action.text() == "Delete":
                    self.list_of_memos_del += [self.list_of_memos.pop(found)]
        else:
            menu = QMenu(self)
            menu.addAction("t:Group_1")
            menu.addAction("t:Group_2")
            menu.addAction("t:Group_3")
            action = menu.exec_(self.mapToGlobal(pos))
            if action:
                print(action)
                self.list_of_memos += [[None, self.page, 8, 20, action.text()]]

        self.update()
# }}}

class ListView2(QListView):
    def __init__(self):# {{{
        super().__init__()
        self.setIconSize(QSize(256, 256));
        self.setViewMode(QListView.IconMode);
        self.setResizeMode(QListView.Adjust)

        self.data_dir = None
        self.model = QStandardItemModel()
        self.setModel(self.model)

        self.list_of_files = []
# }}}
    def setDir(self, data_dir):# {{{
        self.list_of_files = []
        for file_path in [os.path.join(data_dir, _file_path) for _file_path in os.listdir(data_dir)]:
            if file_path.lower().endswith("pdf"):
                mtime_str = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
                self.list_of_files += [(file_path, mtime_str)]
# }}}
    def updateItems(self, search = None):# {{{
        self.model.removeRows(0, self.model.rowCount())

        c = db.cursor()
        c.execute("select name from READ")
        already_read = [r[0] for r in c.fetchall()]

        if search is not None:
            c.execute("select name from MEMO where memo like '%{}%'".format(search))
            #print("filtered", c.fetchall())
            list_of_searched = [r[0] for r in c.fetchall()]

        angles = {}
        c.execute("select name, angle from ROT where page = {}".format(0)) 
        for r in c.fetchall():
            angles[r[0]] = r[1]
        #print("angles of the first page loaded", angles)

        for file_path, mtime_str in sorted(self.list_of_files, key = lambda x: x[1], reverse = True):
            if search is not None:
                #print("filtered:", file_path, list_of_searched)
                if file_path not in list_of_searched:
                    continue
            with open(file_path, "rb") as fh:
                b = fh.read()[:]
                n = pypop3.get_num_of_pages(b)
                w, h, bpr, d = pypop3.render(b, 0, 15)

                image = QImage(d, w, h, bpr, QImage.Format_RGB32).copy()
                if file_path in angles:
                    rot = QTransform()
                    rot = rot.rotate(angles[file_path])
                    image = QImage(d, w, h, bpr, QImage.Format_RGB32).copy().transformed(rot)
                else:
                    image = QImage(d, w, h, bpr, QImage.Format_RGB32).copy()

                #image = QImage(d, w, h, bpr, QImage.Format_RGB32).copy()
                item = QStandardItem(QIcon(QPixmap.fromImage(image)), "{} [{}]".format(mtime_str, n))
                item.file_path = file_path
                #print(file_path, already_read)
                if file_path in already_read:
                    item.setForeground(Qt.black)
                else:
                    item.setForeground(Qt.red)
                mtime = time.mktime(time.strptime(mtime_str, "%Y/%m/%d %H:%M:%S"))
                if time.time() - mtime < 60 * 60: #60 * 60 * 24:
                    item.setBackground(QColor(255, 204, 204))
                elif time.time() - mtime < 60 * 60 * 24:
                    item.setBackground(QColor(255, 255, 153))
                elif time.time() - mtime < 60 * 60 * 24 * 3:
                    item.setBackground(QColor(102, 255, 102))
                elif time.time() - mtime < 60 * 60 * 24 * 7:
                    item.setBackground(QColor(153, 204, 255))
                self.model.appendRow(item)
# }}}

class Main(QMainWindow):
    def __init__(self):# {{{
        super().__init__()

        cw = QWidget(self)

        ly1 = QVBoxLayout()

        self.search = QLineEdit("")
        self.search.returnPressed.connect(self.filterItems)
        self.completer = QCompleter()
        self.search.setCompleter(self.completer)
        self.search_candidate = QStringListModel()
        self.completer.setModel(self.search_candidate)
        self.search_candidate.setStringList(["t:Group_1", "あいうえお", "かきくけこ"])

        self.listview = ListView2()
        #self.listview.setDir("pypop3/test")
        self.listview.setDir("data")
        self.listview.updateItems()
        self.listview.clicked.connect(self.itemClicked)
        ly1.addWidget(self.search)
        ly1.addWidget(self.listview)

        cw.setLayout(ly1)
        self.setCentralWidget(cw)
        self.setGeometry(50, 50, 320, 600)
        self.setWindowTitle('Main')    
        self.show()

        self.sub = Sub()
# }}}
    def filterItems(self):# {{{
        
        if len(self.search.text().strip()) > 0:
            self.listview.updateItems(self.search.text())
        else:
            self.listview.updateItems()
# }}}
    def itemClicked(self, modelIdx):# {{{
        c = db.cursor()
        if ((self.sub.list_of_memos is not None) and len(self.sub.list_of_memos) > 0) or \
                ((self.sub.list_of_memos_del is not None) and len(self.sub.list_of_memos_del) > 0):
            print("saved")
            for rowid, page, x, y, text in self.sub.list_of_memos:
                print(rowid, page, x, y, text)
                if rowid is not None:
                    c.execute("update MEMO set page = {}, x = {}, y = {}, memo = '{}' where rowid = {}".format(page, x, y, text, rowid))
                else:
                    c.execute("insert into MEMO values ('{}', {}, {}, {}, '{}')".format(self.sub.file_path, page, x, y, text))
            for rowid, page, x, y, text in self.sub.list_of_memos_del:
                c.execute("delete from MEMO where rowid = {}".format(rowid))
            db.commit()

        if len(self.sub.angles) > 0:
            c.execute("select page from ROT where name = '{}'".format(self.sub.file_path))
            old_angles = [r[0] for r in c.fetchall()]
            for page, angle in self.sub.angles.items():
                if page in old_angles:
                    c.execute("update ROT set angle = {} where name = '{}' and page = {}".format(angle, self.sub.file_path, page))
                else:
                    c.execute("insert into ROT values ('{}', {}, {})".format(self.sub.file_path, page, angle))

            db.commit()

        item = self.listview.model.item(modelIdx.row())
        item.setForeground(Qt.black)

        self.sub.list_of_memos = []
        self.sub.list_of_memos_del = []
        c.execute("select rowid, page, x, y, memo from MEMO where name = '{}'".format(item.file_path)) 
        for r in c.fetchall():
            #print(r)
            self.sub.list_of_memos += [list(r)]

        self.sub.angles = {}
        c.execute("select page, angle from ROT where name = '{}'".format(item.file_path)) 
        for r in c.fetchall():
            self.sub.angles[r[0]] = r[1]
        print("angles loaded", self.sub.angles)

        c.execute("select rowid from READ where name = '{}'".format(item.file_path))
        if c.fetchone() is None:
            c.execute("insert into READ values ('{}')".format(item.file_path))
            db.commit()

        self.sub.setFile(item.file_path)
        #self.sub.render(0)
        self.sub.show()
# }}}
    def closeEvent(self, event):# {{{
        self.sub.close()
        self.close()
# }}}

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())

