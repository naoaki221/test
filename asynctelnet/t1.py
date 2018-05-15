#
# coding: cp932
# vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
# vim: set foldmethod=marker:

import os
import sys
import time
from datetime import datetime
import re

import telnetlib
import queue
import asyncio

q = queue.Queue()

async def async_read_until(tn, expect):
    buf = b""
    while True:
        buf += tn.read_eager()
        if expect in buf:
            return buf
        await asyncio.sleep(0)

async def work(myid):

    USER = b"user"
    PASSWORD = b"user"
    
    #print("start {}: {}".format(myid, time.time()))

    tn = telnetlib.Telnet("localhost")
       
    #print("connected {}: {}".format(myid, time.time()))
     
    await async_read_until(tn, b"login: ")
    tn.write(USER + b"\n")
      
    await async_read_until(tn, b"Password: ")
    tn.write(PASSWORD + b"\n")
      
    await async_read_until(tn, b"$ ")
    tn.write(b"sleep 3; echo $$\n")

    res = await async_read_until(tn, b"$ ")
    tn.write(b"exit\n")
    lines = res.decode("utf-8").replace("\r", "").split("\n")

    q.put(lines[1])
    #print(lines[1])
    #print("end   {}: {}".format(myid, time.time()))
    


loop = asyncio.get_event_loop()
#loop.run_until_complete(work(0))
tasks = asyncio.wait([work(i) for i in range(5)])
loop.run_until_complete(tasks)
loop.close()

#print(q)
while not q.empty():
    v = q.get()
    print(v)

