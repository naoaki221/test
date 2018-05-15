#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import os
import sys
import time
from datetime import datetime
import re

import subprocess
import asyncio
import queue

import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate



T = 10 * 1

hosts = [
    ("vyos", "192.168.56.105"),
    ("vyos1", "192.168.56.106"),
    ("vyos2", "192.168.56.107"),
    ("vyos3", "192.168.56.108"),
    ("vyos4", "192.168.56.105"),
    ("vyos5", "192.168.56.110"),
]

status = {}
for name, ip in hosts:
    status[name] = 0

async def do_ping(name, ip, q):

    p = await asyncio.create_subprocess_shell( \
        "ping -q -c 1 -W 1 {} | egrep -q \"^1 packets transmitted, 1 received,\"".format(ip))

    s = await p.wait()
    if status[name] != s:
        if s == 0:
            q.put("{} up".format(name))
        else:
            q.put("{} down".format(name))
        status[name] = s



loop = asyncio.get_event_loop()

while True:

    q = queue.Queue()
    tasks = asyncio.wait([do_ping(*h, q) for h in hosts])
    loop.run_until_complete(tasks)

    buf = []
    while not q.empty():
        buf += [q.get()]

    if len(buf) > 0:
        print(buf)
        jp = "iso-2022-jp"
        msg = MIMEText("\n".join(buf).encode(jp), "plain", jp)
        msg["Date"] = formatdate(localtime = True)
        print(msg.as_string())

    t1 = T - time.time() % T
    time.sleep(t1)
    
#loop.close()

