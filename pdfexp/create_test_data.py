#
# coding: utf-8
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim:set foldmethod=marker:
#

import os
import codecs

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import cm

from reportlab.pdfbase.ttfonts import TTFont



pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))

for i in range(5, 10):
    pdfFile = canvas.Canvas("./data/test_data_{}.pdf".format(i))
    
    
    pdfFile.setAuthor("Unknown")
    pdfFile.setTitle("Untitled")
    pdfFile.setSubject("2017")
        
    for j in range(3):
        pdfFile.saveState()
        pdfFile.setPageSize((21*cm, 29.7*cm))
        
        pdfFile.setFont("Vera", 32)
        pdfFile.drawString(2*cm, 26*cm, "test data {}-{}".format(i, j))
        
        pdfFile.restoreState()
        pdfFile.showPage()
    
    pdfFile.save()


