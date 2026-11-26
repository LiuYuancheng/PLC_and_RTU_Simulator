#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        iec61850PlcServerTest.py
#
# Purpose:     This module is a simple PLC simulation program use the IEC-61850-MMS
#              module <iec61850MmsComm.py> to simulate a PLC/RTU with one IEC-61850 
#              server and one execution logic to handle variable read and changeable 
#              value set from client side.
#
# Author:      Yuancheng Liu
#
# Created:     2026/11/26
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

TOPDIR = 'IEC61850_PLC_Simulator'
LIBDIR = 'src'

# domain -> { item : (mms_type, initial_value, writable) }
DEFAULT_MODEL = {
    'IED1LD0': {
        'LLN0$DC$NamPlt$vendor':          ('string', 'WAGO_PFC200', False),
        'LLN0$DC$NamPlt$swRev':           ('string', '1.0.0', False),
        'LLN0$ST$Beh$stVal':              ('integer', 1, False),
        'MMXU1$MX$Hz$mag$f':              ('float', 50.0, True),
        'MMXU1$MX$TotW$mag$f':            ('float', 1250.5, True),
        'MMXU1$MX$PhV$phsA$cVal$mag$f':   ('float', 230.1, True),
        'GGIO1$ST$Ind1$stVal':            ('boolean', False, True),
        'GGIO1$ST$Ind2$stVal':            ('boolean', True, True),
        'GGIO1$MX$AnIn1$mag$f':           ('float', 49.98, True),
        'GGIO1$SP$IntSP1$setVal':         ('integer', 100, True),
        'GGIO1$SP$AnSP1$setMag$f':        ('float', 10.0, True),
        'GGIO1$DC$Desc$d':                ('string', 'Generic I/O', True),
        'XCBR1$CO$Pos$ctlVal':            ('boolean', False, True),
    }
}

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import DNP3 Communication lib: ")
try:
    import iec61850MmsComm as mmsComm
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class Iec61850MmsServerThread(threading.Thread):
    def __init__(self, ip='0.0.0.0', port=102):
        threading.Thread.__init__(self)
        self.server = mmsComm.Iec61850MmsServer(host=str(ip), port=int(port))
        self.modelName = 'IED1LD0'
        self.server.addModel(self.modelName, venderName='WAGO_PFC200')
        # Add all the parameters
        for item, (mmsType, initVal, writable) in DEFAULT_MODEL[self.modelName].items():
            self.server.addLogicNode(self.modelName, item, mmsType, initVal, writable)

    def run(self):
        self.server.startService()

    def getLnVal(self, itemName):
        return self.server.getParamterVal(self.modelName, itemName)

    def setLnVal(self, itemName, val):
        self.server.setParamterVal(self.modelName, itemName, val)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def plcMainThread():
    print("[_] Init the IEC61850MMS server")
    serverThread = Iec61850MmsServerThread()
    serverThread.start()
    time.sleep(1)
    print("[_] IEC61850MMS server is running ...")
    print("[_] Start the PLC ladder logic loop")
    while True:
        time.sleep(0.2)
        # Simulate PLC read IED sensor value from real physical device
        num1 = round(random.uniform(0, 100), 1)
        num2 = round(random.uniform(0, 100), 1)
        # Set the PLC measurement parameters
        serverThread.setLnVal('MMXU1$MX$Hz$mag$f', num1)
        serverThread.setLnVal('MMXU1$MX$TotW$mag$f', num2)
        serverThread.setLnVal('MMXU1$MX$PhV$phsA$cVal$mag$f', num1+num2)
        rst = (num1 + num2) <= 100
        serverThread.setLnVal('XCBR1$CO$Pos$ctlVal', rst)
        # get the client set GGIO parameters
        ggio1 = serverThread.getLnVal('GGIO1$MX$AnIn1$mag$f')
        ggio2 = serverThread.getLnVal('GGIO1$SP$IntSP1$setVal')
        serverThread.setLnVal('GGIO1$SP$AnSP1$setMag$f', ggio1[1]+ggio2[1])

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    plcMainThread()