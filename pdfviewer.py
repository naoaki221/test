#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

DATA_DIRS = ["./DATA", "./DATA2"]
MAIN_WIN_GEOMETRY = (50, 50, 320, 600)
SUB_WIN_GEOMETRY = (400, 50, 600, 600)
NOTIFY_WIN_GEOMETRY = (50, 50, 320, 240)
CHECK_INT = 3
DPI_LARGE = 100
DPI_SMALL = 10

PAGE_FONT_SIZE = 32
CACHE_DIR = "./CACHE"

import os
import sys
import time
from datetime import datetime
import re
import threading
from collections import deque

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

working_dir = os.getcwd() 
os.environ["PATH"] = os.path.join(working_dir, r".\pypop3\dist;") + os.environ["PATH"]
sys.path.append(r".\pypop3\dist")

import pypop3

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import join
from sqlalchemy import and_, or_





Base = declarative_base()
class Doc(Base):
    __tablename__ = "doc"
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    already_read = Column(Boolean)

class Page(Base):
    __tablename__ = "page"
    id = Column(Integer, primary_key = True)
    num = Column(Integer)
    rot = Column(Integer)
    doc_id = Column(Integer, ForeignKey("doc.id"))
    doc = relationship("Doc", back_populates = "pages")

Doc.pages = relationship("Page", order_by = Page.id, back_populates = "doc")

class Memo(Base):
    __tablename__ = "memo"
    id = Column(Integer, primary_key = True)
    x = Column(Integer)
    y = Column(Integer)
    text = Column(String)
    page_id = Column(Integer, ForeignKey("page.id"))
    page = relationship("Page", back_populates = "memos")

Page.memos = relationship("Memo", order_by = Memo.id, back_populates = "page")

db_exists = os.path.exists("pdf.db")
#engine = create_engine('sqlite:///pdf.db', echo = True)
engine = create_engine('sqlite:///pdf.db', echo = False)
if not db_exists:
    Base.metadata.create_all(engine)
    
Session = sessionmaker(bind = engine)
session = Session()

try:
    os.mkdir(CACHE_DIR)
except:
    pass



class Notify(QWidget):
    def __init__(self, data_dirs):# {{{
        super().__init__()
        self.data_dirs = data_dirs
        self.setWindowTitle("Notify")    
        self.setGeometry(*NOTIFY_WIN_GEOMETRY)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        ly1 = QVBoxLayout()
        self.edit = QTextEdit()
        ly1.addWidget(self.edit)
        self.setLayout(ly1)

        self.list_of_pdf_files = self.getFileList()

        self.timer = QTimer(self)
        self.timer.setInterval(1000 * CHECK_INT)
        self.timer.timeout.connect(self.checkNewFiles)

    def getFileList(self):
        list_of_pdf_files = []
        for data_dir in self.data_dirs:
            for fp in [os.path.join(data_dir, _fp).replace("/", "\\\\") for _fp in os.listdir(data_dir)]:
                if fp.lower().endswith("pdf"):
                    list_of_pdf_files += [fp]
        return list_of_pdf_files

    @pyqtSlot()
    def checkNewFiles(self):
        diff = set(self.getFileList()).difference(set(self.list_of_pdf_files))
        if diff:
            self.list_of_pdf_files += list(diff)
            self.edit.setText("\n".join(list(diff)))
            self.show()
# }}}

class Sub(QWidget):
    def __init__(self):# {{{
        super().__init__()
        self.setGeometry(*SUB_WIN_GEOMETRY)
        self.title = "View"

        self.filename = None
        self.rawData = None
        self.page = 0
        self.last_page = 0
        self.pixmap = None

        self.press_pos = None
# }}}
    def setFile(self, filename):# {{{
        with open(filename, "rb") as fh:
            self.rawData = fh.read()[:]
        self.filename = filename
        self.last_page = pypop3.get_num_of_pages(self.rawData)
        self.render(0)
# }}}
    def render(self, page):# {{{
        if 0 <= page and page < self.last_page:
            w, h, bpr, d = pypop3.render(self.rawData, page, DPI_LARGE)
            image = QImage(d, w, h, bpr, QImage.Format_RGB32).copy()
            p = session.query(Page).select_from(join(Doc, Page))\
                    .filter(and_(Doc.name == self.filename, Page.num == self.page + 1)).first()
            if p: 
                rot = QTransform()
                rot = rot.rotate(p.rot)
                self.pixmap = QPixmap.fromImage(image.transformed(rot))
            else:
                self.pixmap = QPixmap.fromImage(image)
            self.page = page
            self.setWindowTitle(self.title.format(self.page + 1, self.last_page))    
            self.update()
# }}}
    def paintEvent(self, event):# {{{
        QWidget.paintEvent(self, event)
        if self.pixmap:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))

            font = painter.font()
            font.setWeight(QFont.DemiBold)
            font.setPixelSize(PAGE_FONT_SIZE)
            painter.setFont(font)
            painter.setPen(Qt.red)
            painter.drawText(self.size().width() - PAGE_FONT_SIZE * 3, self.size().height() - PAGE_FONT_SIZE, \
                    "{}/{}".format(self.page + 1, self.last_page))
            painter.end()
# }}}
    def wheelEvent(self, event):# {{{
        delta = event.angleDelta().y()
        if delta > 0 and self.page > 0:
            self.page -= 1
        elif delta < 0 and self.page < self.last_page - 1:
            self.page += 1
        self.render(self.page)
# }}}
    def mousePressEvent(self, event):# {{{
        self.press_pos = event.pos()
# }}}
    def mouseReleaseEvent(self, event):# {{{
        release_pos = event.pos()
        if self.press_pos:
            delta_x = self.press_pos.x() - release_pos.x()
            delta_y = self.press_pos.y() - release_pos.y()
            if abs(delta_x) > 32 or abs(delta_y) > 32:
                if abs(delta_x) > abs(delta_y):
                    rot = 90 if delta_x > 0 else 270
                else:
                    rot = 180 if delta_y > 0 else 0

        page = session.query(Page).select_from(join(Doc, Page))\
                .filter(and_(Doc.name == self.filename, Page.num == self.page + 1)).first()
        if page: 
            page.rot = rot
            session.commit()
        self.render(self.page)
# }}}

class Main(QMainWindow):
    def __init__(self):# {{{
        super().__init__()

        self.list_of_files = []

        cw = QWidget(self)

        ly1 = QVBoxLayout()

        self.listview = QListView()
        self.listview.setIconSize(QSize(96, 96));
        self.listview.setGridSize(QSize(128, 128));
        self.listview.setUniformItemSizes(True)
        self.listview.setViewMode(QListView.IconMode);
        self.listview.setResizeMode(QListView.Adjust)
        self.listview.verticalScrollBar().valueChanged.connect(self.valueChanged)
        self.listview.clicked.connect(self.itemClicked)
        self.model = QStandardItemModel()
        self.listview.setModel(self.model)
        ly1.addWidget(self.listview)

        self.pdf_icon = QIcon("./sample.png")

        self.reloadAct = QAction("&Refresh", self, shortcut = "Ctrl+R",
                triggered = self.reload)
        self.actionMenu = QMenu("&Action", self)
        self.actionMenu.addAction(self.reloadAct)
        self.menuBar().addMenu(self.actionMenu)
        
        self.setDirs(DATA_DIRS)
        cw.setLayout(ly1)
        self.setCentralWidget(cw)
        self.setGeometry(*MAIN_WIN_GEOMETRY)
        self.setWindowTitle('Main')    
        self.show()

        self.sub = Sub()

        self.notify = Notify(DATA_DIRS)
        self.notify.timer.start()
# }}}
    def reload(self):# {{{
        self.setDirs(DATA_DIRS)
        self.replaceIcon()
# }}}
    def getListOfPdfFilesWithTime(self, data_dir):# {{{
        list_of_pdf_files_with_time = []
        for fp in [os.path.join(data_dir, _fp).replace("/", "\\\\") for _fp in os.listdir(data_dir)]:
            if fp.lower().endswith("pdf"):
                mtime_str = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(os.path.getmtime(fp)))
                list_of_pdf_files_with_time += [(fp, mtime_str)]
        return sorted(list_of_pdf_files_with_time, key = lambda x: x[1], reverse = True)
# }}}
    def setDirs(self, dirs):# {{{
        self.model.removeRows(0, self.model.rowCount())

        list_of_files_with_time = []
        for d in dirs:
            list_of_files_with_time += self.getListOfPdfFilesWithTime(d)
        for fn, mt in sorted(list_of_files_with_time, key = lambda x: x[1], reverse = True):
            item = QStandardItem(self.pdf_icon, "{}".format(mt))
            item.filename = fn
            item.mtime = mt
            item.thumb = False

            with open(fn, "rb") as fh:
                rawdata = fh.read()[:]
            n = pypop3.get_num_of_pages(rawdata)
            doc = session.query(Doc).filter_by(name = fn).first()
            item.setForeground(Qt.red)
            if doc:
                if doc.already_read:
                    item.setForeground(Qt.black)
            else:
                doc = Doc(name = fn, already_read = False)
                doc.pages = [Page(num = i, rot = 0) for i in range(1, n + 1)]
                session.add(doc)

            self.model.appendRow(item)
        session.commit()
# }}}
    def replaceIcon(self):# {{{
        rect = self.listview.viewport().rect()
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.thumb == False:
                itemRect = self.listview.visualRect(self.model.index(i, 0))
                if rect.contains(itemRect.x(), itemRect.y()):
                    cached_file = os.path.join(CACHE_DIR, \
                            "".join(map(lambda x : "{:02x}".format(x), item.filename.encode("cp932"))) + ".png")
                    #print(cached_file)
                    if os.path.exists(cached_file):
                        image = QImage()
                        image.load(cached_file)
                    else:
                        with open(item.filename, "rb") as fh:
                            w, h, bpr, d = pypop3.render(fh.read(), 0, DPI_SMALL)

                        image = QImage(d, w, h, bpr, QImage.Format_RGB32).copy()
                        image.save(cached_file)
                    
                    p = session.query(Page).select_from(join(Doc, Page))\
                            .filter(and_(Doc.name == item.filename, Page.num == 1)).first()

                    if p: 
                        rot = QTransform()
                        rot = rot.rotate(p.rot)
                        pixmap = QPixmap.fromImage(image.transformed(rot))
                    else:
                        pixmap = QPixmap.fromImage(image)
                    item.setIcon(QIcon(pixmap))
                    item.thumb = True
# }}}
    def itemClicked(self, modelIndex):# {{{
        item = self.model.item(modelIndex.row())
        item.setForeground(Qt.black)
        doc = session.query(Doc).filter_by(name = item.filename).first()
        if doc:
            doc.already_read = True
            session.commit()
        self.sub.setFile(item.filename)
        self.sub.show()
# }}}
    def resizeEvent(self, event):# {{{
        self.replaceIcon()
# }}}
    def valueChanged(self, value):# {{{
        self.replaceIcon()
# }}}
    def closeEvent(self, event):# {{{
        self.notify.timer.stop()
        self.notify.close()
        self.sub.close()
        self.close()
# }}}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())

