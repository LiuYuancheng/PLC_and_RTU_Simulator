#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        dnp3RtuServerTest.py
#
# Purpose:     This module is a simple RTU simulation program use the DNP3 lib 
#              module <dnp3Comm.py> to simulate a PLC/RTU with one DNP3.0 server
#              and one execution logic to handle variable read and changeable value 
#              set from client side.
#
# Author:      Yuancheng Liu
#
# Created:     2026/07/27
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os
import sys
import time
import random
import threading

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'DNP3_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import DNP3 Communication lib: ")
try:
    import dnp3Comm
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DNP3ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = dnp3Comm.DNP3Server(maxConn=3)
        # Add the parameters:
        self.server.addBinaryInput(0, False)
        self.server.addBinaryInput(1, True)
        self.server.addAnalogInput(0, 0)
        self.server.addBinaryOutput(0, False)
        self.server.addBinaryOutput(1, True)
        self.server.addAnalogOutput(0, 0)

    def run(self):
        self.server.run()

    def getDNP3ServerObj(self):
        return self.server

#-----------------------------------------------------------------------------
def rtuMainThread():
    print("[_] Init the DNP3 server")
    serverThread = DNP3ServerThread()
    serverThread.start()
    time.sleep(1)
    serverObj = serverThread.getDNP3ServerObj()
    # Run the RTU logic
    print("[_] Start the RTU ladder logic loop")
    while True:
        o1 = serverObj.getBinaryOutput(0)
        serverObj.setBinaryInput(0, not o1)
        o2 = serverObj.getBinaryOutput(1)
        serverObj.setBinaryInput(1, not o2)
        o3 = serverObj.getAnalogOutput(0)
        print("o1:%s, o2:%s, o3:%s" %(str(o1), str(o2), str(o3)))
        i1 = serverObj.getBinaryInput(0)
        i2 = serverObj.getBinaryInput(1)
        if i1 and i2:
            serverObj.setAnalogInput(0, 100-o3)
        else:
            serverObj.setAnalogInput(0, 100+o3)
        time.sleep(0.3)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    rtuMainThread()  
