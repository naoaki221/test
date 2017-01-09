#
# -*- coding: cp932 -*-
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

from __future__ import print_function

import os
import sys
import re
import subprocess

os.environ["PATH"] = r".\pypop_dist;" + os.environ["PATH"]
sys.path.append(r".\pypop_dist")
sys.path.append(r"C:\Users\naoaki\app\opencv\build\python\2.7\x86")

import pypop
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PyQt4 import QtCore, QtGui

#DPI = 100
with open("DPI.txt", "r") as fh:
    DPI = eval(fh.read())

def match_marker(image, img_marker):
    res = cv2.matchTemplate(image, img_marker, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc
    tw, th = img_marker.shape[::-1]
    bottom_right = (top_left[0] + tw, top_left[1] + th)
    
    return top_left, bottom_right

def group_ypos(list_of_pos):
    def pos_compare_v(a, b):
        if (a[1] > b[1]):
            return 1
        elif (a[1] < b[1]):
            return -1
        else:
            return 0

    list_of_pos_sorted = sorted(list_of_pos, pos_compare_v)
    diff = []
    for i in range(len(list_of_pos_sorted) - 1):
        a = list_of_pos_sorted[i]
        b = list_of_pos_sorted[i + 1]
        diff += [b[1] - a[1]]
    avg = sum(diff) / len(diff)
    list_of_pos_group = [[list_of_pos_sorted[0]]]
    for a in list_of_pos_sorted[1:]:
        if a[1] - list_of_pos_group[-1][0][1] < avg:
            list_of_pos_group[-1].append(a)
        else:
            list_of_pos_group.append([a])
    return list_of_pos_group

def group_xpos(list_of_pos):
    def pos_compare_v(a, b):
        if (a[0] > b[0]):
            return 1
        elif (a[0] < b[0]):
            return -1
        else:
            return 0

    list_of_pos_sorted = sorted(list_of_pos, pos_compare_v)
    diff = []
    for i in range(len(list_of_pos_sorted) - 1):
        a = list_of_pos_sorted[i]
        b = list_of_pos_sorted[i + 1]
        diff += [b[0] - a[0]]
    avg = sum(diff) / len(diff)
    list_of_pos_group = [[list_of_pos_sorted[0]]]
    for a in list_of_pos_sorted[1:]:
        if a[0] - list_of_pos_group[-1][0][0] < avg:
            list_of_pos_group[-1].append(a)
        else:
            list_of_pos_group.append([a])
    return list_of_pos_group
    
def match_cbox(image, img_cbox):
    cw, ch = img_cbox.shape[::-1]
    res = cv2.matchTemplate(image, img_cbox, cv2.TM_CCOEFF_NORMED)
    threshold = 0.85
    #threshold = 0.92
    loc = np.where(res >= threshold)
    list_of_pos = []
    for pt in zip(*loc[::-1]):
        list_of_pos +=  [(pt[0], pt[1], pt[0] + cw, pt[1] + ch)]
    #return list_of_pos
    list_of_ygroup_pos = group_ypos(list_of_pos)
    list_of_filtered_pos = []
    for ygroup in list_of_ygroup_pos:
        list_of_xgroup_pos = group_xpos(ygroup)
        for xgroup in list_of_xgroup_pos:
            list_of_filtered_pos += [xgroup[0]]
    return list_of_filtered_pos

def match_sheet(img_tgt, img_marker, img_cbox):
    top_left, bottom_right = match_marker(img_tgt, img_marker)
    cv2.rectangle(img_res, top_left, bottom_right, (0, 255, 0), 1)
    print(">Marker position: ", end = "")
    print(top_left, bottom_right)

    list_of_pos = match_cbox(img_tgt, img_cbox)
    print(">Number of found checkboxes: ", end = "")
    print(len(list_of_pos))

    def pos_compare_v(a, b):
        if (a[1] > b[1]):
            return 1
        elif (a[1] < b[1]):
            return -1
        else:
            return 0

    list_of_pos_sorted = sorted(list_of_pos, pos_compare_v)
    diff = []
    for i in range(len(list_of_pos_sorted) - 1):
        a = list_of_pos_sorted[i]
        b = list_of_pos_sorted[i + 1]
        diff += [b[1] - a[1]]
    avg = sum(diff) / len(diff)
    list_of_pos_group = [[list_of_pos_sorted[0]]]
    for a in list_of_pos_sorted[1:]:
        if a[1] - list_of_pos_group[-1][0][1] < avg:
            list_of_pos_group[-1].append(a)
        else:
            list_of_pos_group.append([a])

    def pos_compare_h(a, b):
        if (a[0] > b[0]):
            return 1
        elif (a[0] < b[0]):
            return -1
        else:
            return 0

    serial_num = 0
    list_of_cbox_pos = []
    for pos_group in list_of_pos_group:
        pos_group_sorted = sorted(pos_group, pos_compare_h)
        for i, pt in enumerate(pos_group_sorted):
            #cv2.putText(img_res, str(serial_num), (pt[0], pt[1]), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
            #cv2.rectangle(img_res, (pt[0], pt[1]), (pt[2], pt[3]), (255, 0, 0), 1)
            list_of_cbox_pos += [pt]
            serial_num += 1

    return ((top_left[0], top_left[1], bottom_right[0], bottom_right[1]), list_of_cbox_pos)

def load_matrix_from_pdf_stream(stream, page):
    w, h, bpr, d = pypop.render(stream, page, DPI)
    qi = QtGui.QImage(d, w, h, bpr, QtGui.QImage.Format_RGB32).copy()

    ptr = qi.bits()
    ptr.setsize(qi.byteCount())
    img_tgt = np.array(ptr).reshape(qi.height(), qi.width(), 4)
    img_tgt_gray = cv2.cvtColor(img_tgt.copy(), cv2.COLOR_BGR2GRAY)
    return img_tgt_gray

def convert_to_relative_pos(marker_pos, list_of_cbox_pos):
    list_of_cbox_rel_pos = []
    for i, pt in enumerate(list_of_cbox_pos):
        #list_of_cbox_rel_pos += [(pt[0] - marker_pos[0], pt[1] - marker_pos[1], pt[2] - marker_pos[2], pt[3] - marker_pos[3])]
        list_of_cbox_rel_pos += [(pt[0] - marker_pos[0], pt[1] - marker_pos[1], pt[2] - marker_pos[0], pt[3] - marker_pos[1])]
    return list_of_cbox_rel_pos



img_marker = cv2.imread("marker.png", cv2.IMREAD_GRAYSCALE)
#plt.subplot(221),plt.imshow(img_marker, cmap = 'gray')

img_cbox = cv2.imread("checkbox.png", cv2.IMREAD_GRAYSCALE)
#plt.subplot(222),plt.imshow(img_cbox, cmap = 'gray')
cbox_h, cbox_w = img_cbox.shape[:2]
cbox_size = (cbox_h + cbox_w) // 2 // 2
print("Size of checkbox:", end = "")
print(cbox_size)

print("Blank pdf:")
with open(".\data\check.pdf", "rb") as fh:
    b = fh.read()
img_tgt_gray = load_matrix_from_pdf_stream(b, 0)
img_res = cv2.cvtColor(img_tgt_gray, cv2.COLOR_GRAY2RGB)

base_marker_pos, base_list_of_cboxes = match_sheet(img_tgt_gray, img_marker, img_cbox)
list_of_base_cbox = convert_to_relative_pos(base_marker_pos, base_list_of_cboxes)
#print(base_marker_pos, base_list_of_cboxes)


pdf_path = r".\data"
list_of_pdf = []
for root, dirs, files in os.walk(pdf_path):
    for f in files:
        if re.match(".*[.]pdf$", f):
            list_of_pdf += [os.path.join(root, f)]

print(list_of_pdf)



for file_path in list_of_pdf:
    print("Start: " + file_path)
    with open(file_path, "rb") as fh:
        b = fh.read()
    num_of_pages = pypop.get_num_of_pages(b)

    print("Number of pages: " + str(num_of_pages))

    with open(file_path, "rb") as fh:
        b = fh.read()
    for page in range(num_of_pages):
    #for page in range(1):
        print(">Page: " + str(page))

        img_tgt_gray = load_matrix_from_pdf_stream(b, page)
        img_res = cv2.cvtColor(img_tgt_gray, cv2.COLOR_GRAY2RGB)

        marker_pos, list_of_cbox = match_sheet(img_tgt_gray, img_marker, img_cbox)
        list_of_empty_cbox = convert_to_relative_pos(marker_pos, list_of_cbox)
        print(marker_pos)
        print(list_of_empty_cbox )
        #for i, pt in enumerate(list_of_empty_cbox):
        #    cv2.putText(img_res, str(i), (pt[0], pt[1]), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
        #    cv2.rectangle(img_res, (pt[0], pt[1]), (pt[2], pt[3]), (255, 0, 0), 1)

        result = []
        for i, pt1 in enumerate(list_of_base_cbox):
            found = -1
            for j, pt2 in enumerate(list_of_empty_cbox):
                dd = (pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2
                if dd < cbox_size ** 2:
                    found = j
                    break
            #pt = pt1
            #color = (0, 255, 0)
            print(i, end = ": ")
            print(found)
            if found >= 0:
                pt_rel = list_of_empty_cbox[found]
                pt = (pt_rel[0] + marker_pos[0], \
                      pt_rel[1] + marker_pos[1], \
                      pt_rel[2] + marker_pos[0], \
                      pt_rel[3] + marker_pos[1])
                color = (0, 255, 0)
                result += ["x"]
            else:
                pt_rel = pt1
                pt = (pt_rel[0] + marker_pos[0], \
                      pt_rel[1] + marker_pos[1], \
                      pt_rel[2] + marker_pos[0], \
                      pt_rel[3] + marker_pos[1])
                color = (0, 0, 255)
                result += ["v"]
            cv2.putText(img_res, str(i), (pt[0], pt[1]), cv2.FONT_HERSHEY_PLAIN, 2, color)
            cv2.rectangle(img_res, (pt[0], pt[1]), (pt[2], pt[3]), color, 1)

        print(result)
        cv2.imwrite(".\\tmp\\" + str(page) + ".png", img_res)
        #plt.imshow(img_res)

    

    print("End: " + file_path)
    #plt.imshow(img_res, cmap = 'gray')
    #plt.subplot(223),plt.imshow(img_tgt, cmap = 'gray')
    #plt.suptitle("hello")

#plt.show()

