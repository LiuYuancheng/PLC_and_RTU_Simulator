#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        rtuServerTest.py
#
# Purpose:     This module is a test case program of lib module <snap7Comm.py>
#              to start a S7comm server to simulate a PLC or RTU to handle the 
#              memory read/set request.
#
# Author:      Yuancheng Liu
#
# Created:     2024/03/41
# Version:     v_0.1.3
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
"""
    Remark: this program need to run under 64-bit python, use workon to active the 
            virtual env: workon vEnv3.8 then run the program.

"""

import os, sys

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'S7Comm_RTU_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

#-----------------------------------------------------------------------------
print("Test import lib: ")
try:
    import snap7Comm
    from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

#-----------------------------------------------------------------------------
libpath = os.path.join(gLibDir, 'snap7.dll')
print("Import snap7 dll path: %s" % str(libpath))
if os.path.exists(libpath):
    print("- pass")
else:
    print("Error: not file the dll file.")
    exit()

print("Init the server and memory address")
server = snap7Comm.s7commServer(snapLibPath=libpath)
server.initNewMemoryAddr(1, [0, 2, 4], [BOOL_TYPE, INT_TYPE, REAL_TYPE])
server.initNewMemoryAddr(2, [0, 4], [REAL_TYPE, REAL_TYPE])

print("Test set and values:")
server.setMemoryVal(1, 0, True)
server.setMemoryVal(1, 2, 10)
server.setMemoryVal(1, 4, 3.1415920)

server.setMemoryVal(2, 0, 1.23)
server.setMemoryVal(2, 4, 4.56)

rst = 'pass' if server.getMemoryVal(1, 0) else 'failed'
print(" - test set bool value : %s" %str(rst))

rst = 'pass' if server.getMemoryVal(1, 2) == 10 else 'failed'
print(" - test set int value   : %s" %str(rst))

rst = 'pass' if round(server.getMemoryVal(1, 4), 6)== 3.141592 else 'failed'
print(" - test set real value  : %s" %str(rst))

class testLadderLogic(snap7Comm.rtuLadderLogic):

    def __init__(self, parent, nameStr):
        super().__init__(parent, ladderName=nameStr)

    def initLadderInfo(self):
        self.srcAddrValInfo = {'addressIdx': 2, 'dataIdx': 4}
        self.destAddrValInfo = {'addressIdx': 2, 'dataIdx': 0}

    def runLadderLogic(self, inputData=None):
        print(" - runLadderLogic")
        addr, dataIdx, datalen = inputData
        print("Received data write request: ")
        print("Address: %s " %str(addr))
        print("dataIdx: %s " %str(dataIdx))
        print("datalen: %s" %str(datalen))
        if addr == self.srcAddrValInfo['addressIdx'] and dataIdx == self.srcAddrValInfo['dataIdx']:
            val = self.parent.getMemoryVal(self.srcAddrValInfo['addressIdx'], 
                                        self.srcAddrValInfo['dataIdx'])
            print("dataVal: %s" %str(print))
            self.parent.setMemoryVal(self.destAddrValInfo['addressIdx'],
                                    self.destAddrValInfo['dataIdx'], val)


testRtuLL = testLadderLogic(server, 'testRtuLL')

# The auto data handling function.
def handlerS7request(parmList):
    """ ladder logic simulation function: when the user set the address Idx=2
        and dataIdx = 4 value, the ladder logic will change the address Idx=2
        dataIdx = 0 's value to the same value.
    """
    global testRtuLL
    if server:
        testRtuLL.runLadderLogic(inputData=parmList)


def handlerS7request_old(parmList):
    """ ladder logic simulation function: when the user set the address Idx=2
        and dataIdx = 4 value, the ladder logic will change the address Idx=2
        dataIdx = 0 's value to the same value.
    """
    global server
    addr, dataIdx, datalen = parmList
    print("Received data write request: ")
    print("Address: %s " %str(addr))
    print("dataIdx: %s " %str(dataIdx))
    print("datalen: %s" %str(datalen))
    if server:
        print("dataVal: %s" %str(server.getMemoryVal(addr, dataIdx)))
        if addr == 2 and dataIdx == 4:
            server.setMemoryVal(addr, 0, server.getMemoryVal(addr, dataIdx))


print("Server start")
server.startService(eventHandlerFun=handlerS7request)



