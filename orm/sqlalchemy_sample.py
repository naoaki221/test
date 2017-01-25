#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import os
import sys
import time
#import math
import sqlite3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship



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
if not db_exists:
    doc = Doc(name = "data1.pdf", already_read = False)
    doc.pages = [Page(num = i, rot = 0) for i in range(1, 6)] session.add(doc)
    session.commit()

#rows = session.query(Doc).filter_by(name = "data1.pdf").all()
#for r in rows:
#    print([page.num for page in r.pages])
#
#for d, p in session.query(Doc, Page).filter(Doc.name == "data1.pdf").filter(Page.num >= 1).all():
#    print(d.name, p.num, p.rot)
#    if p.num == 3:
#        p.rot = 90
#        p.memos = [Memo(x = 1, y = 1, text = "hello")]
#
#for d, p in session.query(Doc, Page).filter(Doc.name == "data1.pdf").filter(Page.num >= 1).all():
#    print(d.name, p.num, p.rot, p.memos)
#    for m in p.memos:
#        print(m.x, m.y, m.text)

