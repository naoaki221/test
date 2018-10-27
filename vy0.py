#
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# vim: set foldmethod=marker:

import sys
import os
import signal
import fcntl
import re
import time
import copy
import termios
import struct



def init_term():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    newattr[6][termios.VMIN] = 1
    newattr[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    return oldterm

def revert_term(oldterm):
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

def get_key():
    c1 = sys.stdin.read(1)
    fd = sys.stdin.fileno()
    # some delay may be necessary here
    termattr = termios.tcgetattr(fd)
    termattr[6][termios.VMIN] = 0
    termios.tcsetattr(fd, termios.TCSANOW, termattr)
    c2 = sys.stdin.read(3)
    termattr[6][termios.VMIN] = 1
    termios.tcsetattr(fd, termios.TCSANOW, termattr)
    return c1, c2

def window_size():
    results = fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0))
    h, w, hp, wp = struct.unpack('HHHH', results)
    return w, h

def clear():
    print("\033[2J", end = "")

def movec(x, y):
    print("\033[{0};{1}H".format(y + 1, x + 1), end = "")

def puts(x, y, s):
    print("\033[{0};{1}H".format(y + 1, x + 1), end = "")
    print(s, end = "")

def open_file(filename):
    f = open(filename, "r")
    buf = [l.rstrip() for l in f.readlines()]
    f.close()
    return buf

def save_file(filename, buf):
    f = open(filename, "w")
    f.write("\n".join(buf))
    f.close()

def paint_edit(win_x, win_y, win_width, win_height, buf, gy, cx, cy, sel_mode, sel_x, sel_y):
    buf_slice = buf[gy:gy + win_height]

    num_width = 4
    num_format = "{0:>%d} " % (num_width - 1)

    clear()
    r = gy 
    y = 0
    filled = []
    while r - gy < len(buf_slice) and y < win_height:
        movec(0, win_y + y)
        line = buf[r]
        start_num()
        print(num_format.format(r + 1), end = "")

        if sel_mode == "line" and \
            ((sel_y <= r and r <= gy + cy) or (gy + cy <= r and r <= sel_y)):
            start_sel()
        else:
            start_text()
                
        line2 = line
        print(line2[:win_width - num_width], end = "")
        filled += [len(line2[:win_width - num_width])]
        while len(line2) > win_width - num_width:
            line2 = line2[win_width - num_width:]
            y += 1
            movec(num_width, y)
            print(line2[:win_width - num_width], end = "")
            filled += [len(line2[:win_width - num_width])]

        r += 1
        y += 1

    movec(num_width + cx, win_y + cy)

    return filled

def paint_cmd(win_x, win_y, win_width, win_height, cmd_buf, cmdx):
    movec(0, win_y)
    print(cmd_buf[:win_width], end = "")
    movec(cmdx, win_y)

def start_num():
    print("\033[0m", end = "")
    print("\033[31m", end = "")
    #print("\033[48m", end = "")

def start_text():
    print("\033[0m", end = "")
    print("\033[37m", end = "")
    #print("\033[48m", end = "")

def start_sel():
    print("\033[0m", end = "")
    print("\033[7m", end = "")

def start_underline():
    print("\033[0m", end = "")
    print("\033[4m", end = "")



def get_filelist(lcd):
    #filer_buf = [".."] + [f for f in os.listdir(lcd)]
    filer_buf = [".."]
    filer_attr = [["d", "../"]]

    for fn in os.listdir(lcd):
        file_type = ""
        if os.path.isdir(fn):
            file_type = "d"
        if file_type == "d":
            fn = fn + "/"
        file_path = fn

        filer_buf += [fn]
        filer_attr += [[file_type, file_path],]

    return filer_buf, filer_attr

oldterm = init_term()
def signal_handler(signal, frame):
    global oldterm
    revert_term(oldterm)
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)




win_width, win_height = window_size()
edit_width = win_width
edit_height = win_height - 1
num_width = 3

cx = 0
cy = 0
gy = 0
copy_buf = []
edit_mode = "normal"
edit_mode_next = edit_mode
norm_seq = ""
lcd = "."
files = []
c1 = chr(0x1b)
c2 = []
delayed_proc = 0
refresh_listdir = 0
edit_buf = [["scratch.txt", [""]],]
filer_buf = []
filer_attr = []
cmd_buf = ""
cmdx = 0
edit_cpos = [0, 0]
filer_cpos = [0, 0]
buf_cpos = [0, 0]
sel_mode = None
sel_x = 0
sel_y = 0
search_text = ""
jump = 0
jx = 0
jy = 0

#edit_buf = open_file("_old/edit2.py")
#edit_buf = open_file("show_ascii.py")
#edit_buf = [""]
filled = []
try:
    while 1:
        if edit_mode == "normal" or edit_mode == "insert":
            buf = edit_buf[0][1]
        elif edit_mode == "filer":
            buf = filer_buf
        elif edit_mode == "buffer":
            buf = [b[0] for b in edit_buf]

        if jump == 1:
            cx = jx
            if jy < gy:
                if jy < edit_height:
                    cy = jy
                    gy = 0
                else:
                    cy = edit_height // 2
                    gy = jy - cy
            elif jy < gy + edit_height:
                cy = jy - gy
            else:
                cy = edit_height // 2
                gy = jy - cy
            jump = 0


        filled = paint_edit(0, 0, edit_width, edit_height, buf, gy, cx, cy, sel_mode, sel_x, sel_y)
        if edit_mode == "command":
            paint_cmd(0, win_height - 1, edit_width, edit_height, cmd_buf, cmdx)
        sys.stdout.flush()

        if delayed_proc == 0:
            c1, c2 = get_key()
            #print(c1, c2)

        if edit_mode == "normal":
            if ord(c1) == 0x1b: # escape
                norm_seq = ""
                sel_mode = None
            elif c1 == "l" and cx < filled[cy] - 1:
                cx += 1
            elif c1 == "h" and cx > 0:
                cx -= 1
            elif c1 == "j":
                if gy + cy < len(buf) - 1:
                    if cy == edit_height - 1:
                        if delayed_proc == 0:
                            gy += 1
                            delayed_proc = 1
                            continue
                        else:
                            if cx > filled[cy]:
                                cx = filled[cy]
                    else:
                        cy += 1
                        if cx > filled[cy]:
                            cx = filled[cy]
            elif c1 == "k":
                if cy == 0 and gy > 0:
                    if delayed_proc == 0:
                        gy -= 1
                        delayed_proc = 1
                        continue
                    else:
                        if cx > filled[cy]:
                            cx = filled[cy]
                elif cy > 0:
                    cy -= 1
                    if cx > filled[cy]:
                        cx = filled[cy]
            elif ord(c1) == 0x6: # Ctrl-f
                if delayed_proc == 0:
                    jx = cx
                    if gy + cy + (edit_height // 2) < len(buf):
                        jy = gy + cy + (edit_height // 2) 
                    else:
                        jy = gy + cy
                    jump = 1
                    delayed_proc = 1
                    continue
                else:
                    if cx > filled[cy]:
                        cx = filled[cy]
            elif ord(c1) == 0x2: # Ctrl-b
                if delayed_proc == 0:
                    jx = cx
                    if gy + cy - (edit_height // 2) >= 0:
                        jy = gy + cy - (edit_height // 2) 
                    else:
                        jy = gy + cy
                    jump = 1
                    delayed_proc = 1
                    continue
                else:
                    if cx > filled[cy]:
                        cx = filled[cy]
            elif c1 == "$":
                cx = filled[cy]
            elif c1 == "i":
                edit_mode_next = "insert"
            elif c1 == "a":
                edit_mode_next = "insert"
                if cx < filled[cy] - 1:
                    cx += 1
            elif c1 == "O":
                edit_mode_next = "insert"
                buf.insert(gy + cy, "")
                cx = 0
            elif c1 == "o":
                edit_mode_next = "insert"
                buf.insert(gy + cy, "")
                cx = 0
                if cy < edit_height:
                    cy += 1
            elif c1 == "x":
                old_line = buf[gy + cy - 1]
                buf[gy + cy - 1] = old_line[:cx] + old_line[cx + 1:]
            elif c1 == "J":
                if gy + cy < len(buf) - 1:
                    buf[gy + cy] += " " + buf[gy + cy + 1] 
                    buf.pop(gy + cy + 1) 
            elif c1 == "P":
                for i, v in enumerate(copy_buf):
                    buf.insert(gy + cy - 1 + i, v) 
            elif c1 == "p":
                pass
            #elif c1 == "v":
            #    #sel_mode = "char"
            #    pass
            elif c1 == "V":
                sel_mode = "line"
                sel_x, sel_y = cx, gy + cy
            elif ord(c1) == 22: # ctrl-v
                #sel_mode = "box"
                pass
            elif c1 == "y" and sel_mode == "line":
                if sel_y < gy + cy:
                    copy_buf = copy.deepcopy(buf[sel_y:gy + cy + 1])
                else:
                    copy_buf = copy.deepcopy(buf[gy + cy:sel_y + 1])
                sel_mode = None
            elif c1 == ";":
                edit_mode_next = "command"
                cmd_buf = ""
                cmdx = 0
            elif c1 == "/":
                edit_mode_next = "command"
                cmd_buf = ":/"
                cmdx = 2
            elif c1 == "n":
                for i in range(len(buf)):
                    ii = (gy + cy + i) % len(buf)
                    found = []
                    p = buf[ii].find(search_text)
                    while p >= 0 and p + len(search_text) < len(buf[ii]):
                        if i != 0 or p > cx:
                            found += [p]
                        p = buf[ii].find(search_text, p + 1)
                    if len(found) > 0:
                        jx = found[0]
                        jy = ii
                        jump = 1
                        break
            elif c1 == "N":
                for i in range(len(buf)):
                    ii = (gy + cy - i) % len(buf)
                    found = []
                    p = buf[ii].find(search_text)
                    while p >= 0 and p + len(search_text) < len(buf[ii]):
                        if i != 0 or p < cx:
                            found += [p]
                        p = buf[ii].find(search_text, p + 1)
                    if len(found) > 0:
                        jx = found[-1]
                        jy = ii
                        jump = 1
                        break
            elif c1 == "G":
                jx = cx
                jy = len(buf) - 1
                jump = 1

            else:
                norm_seq += c1

                if norm_seq == " fv":
                    edit_mode_next = "filer"
                    norm_seq = ""
                    refresh_listdir = 1
                elif norm_seq == " fb":
                    edit_mode_next = "buffer"
                    norm_seq = ""
                elif norm_seq == "yy":
                    copy_buf = [copy.deepcopy(buf[gy + cy])]
                    norm_seq = ""
                elif norm_seq == "dd":
                    buf.pop(gy + cy - 1) 
                    norm_seq = ""
                elif norm_seq == "gg":
                    cx = 0
                    cy = 0
                    gy = 0
                    norm_seq = ""

        elif edit_mode == "insert":

            if ord(c1) == 0x1b:
                edit_mode_next = "normal"
            elif ord(c1) == 0xa: # enter
                old_line = buf[gy + cy]
                buf[gy + cy] = old_line[:cx]
                buf.insert(gy + cy + 1, old_line[cx:])
                cx = 0
                cy += 1
            elif ord(c1) == 0x7f: # backspace
                if cx > 0:
                    old_line = buf[gy + cy]
                    buf[gy + cy] = old_line[:cx - 1] + old_line[cx:]
                    cx -= 1
            else:
                old_line = buf[gy + cy]
                buf[gy + cy] = old_line[:cx] + c1 + old_line[cx:]
                if cx < edit_width - 1:
                    cx += 1

        elif edit_mode == "filer":

            if c1 == "q":
                edit_mode_next = "normal"
            elif c1 == "l" and cx < filled[cy] - 1:
                if filer_attr[gy + cy][0] == "d": # file_type
                    lcd += "/" + filer_attr[gy + cy][1] # new path
                    refresh_listdir = 1
                else:
                    cx += 1
            elif c1 == "h":
                if cx > 0:
                    cx -= 1
                lcd += "/../"
                refresh_listdir = 1
            elif c1 == "j":
                if gy + cy < len(buf) - 1:
                    if cy == edit_height - 1:
                        if delayed_proc == 0:
                            gy += 1
                            delayed_proc = 1
                            continue
                        else:
                            if cx > filled[cy]:
                                cx = filled[cy]
                    else:
                        cy += 1
                        if cx > filled[cy]:
                            cx = filled[cy]
            elif c1 == "k":
                if cy == 0 and gy > 0:
                    if delayed_proc == 0:
                        gy -= 1
                        delayed_proc = 1
                        continue
                    else:
                        if cx > filled[cy]:
                            cx = filled[cy]
                elif cy > 0:
                    cy -= 1
                    if cx > filled[cy]:
                        cx = filled[cy]
            elif c1 == "e":
                new_file = open_file(buf[gy + cy])
                edit_buf.insert(0, [buf[gy + cy], new_file])
                edit_mode_next = "normal"

        elif edit_mode == "command":

            if ord(c1) == 0x1b: # escape
                edit_mode_next = "normal"
            elif ord(c1) == 0xa: # enter
                if cmd_buf.startswith(":/"):
                    search_text = cmd_buf[2:]
                edit_mode_next = "normal"
            elif ord(c1) == 0x7f: # backspace
                if cmdx > 0:
                    cmd_buf = cmd_buf[:cmdx - 1] + cmd_buf[cmdx:]
                    cmdx -= 1
            else:
                cmd_buf = cmd_buf[:cmdx] + c1 + cmd_buf[cmdx:]
                if cmdx < edit_width - 1:
                    cmdx += 1

        elif edit_mode == "buffer":

            if c1 == "q":
                edit_mode_next = "normal"
            elif c1 == "l" and cx < filled[cy] - 1:
                cx += 1
            elif c1 == "h" and cx > 0:
                cx -= 1
            elif c1 == "j":
                if gy + cy < len(buf) - 1:
                    if cy == edit_height - 1:
                        if delayed_proc == 0:
                            gy += 1
                            delayed_proc = 1
                            continue
                        else:
                            if cx > filled[cy]:
                                cx = filled[cy]
                    else:
                        cy += 1
                        if cx > filled[cy]:
                            cx = filled[cy]
            elif c1 == "k":
                if cy == 0 and gy > 0:
                    if delayed_proc == 0:
                        gy -= 1
                        delayed_proc = 1
                        continue
                    else:
                        if cx > filled[cy]:
                            cx = filled[cy]
                elif cy > 0:
                    cy -= 1
                    if cx > filled[cy]:
                        cx = filled[cy]
            elif ord(c1) == 0xa: # enter
                temp_buf = edit_buf.pop(gy + cy)
                edit_buf.insert(0, temp_buf)
                edit_mode_next = "normal"

        if refresh_listdir == 1:
            filer_buf, filer_attr = get_filelist(lcd)
            refresh_listdir = 0

        if edit_mode != edit_mode_next:
            # backup
            if edit_mode == "normal" or edit_mode == "insert":
                edit_cpos = [cx, cy]
            elif edit_mode == "filer":
                filer_cpos = [cx, cy]
            elif edit_mode == "buffer":
                buf_cpos = [cx, cy]
            # restore
            if edit_mode_next == "normal" or edit_mode_next == "insert":
                cx, cy = edit_cpos
            elif edit_mode_next == "filer":
                cx, cy = filer_cpos
            elif edit_mode_next == "buffer":
                cx, cy = buf_cpos

        edit_mode = edit_mode_next
        delayed_proc = 0;

finally:
    revert_term(oldterm)
    print(c1, c2)



