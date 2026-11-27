#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        iec61850PlcClientTest.py
#
# Purpose:     This module is a simple SCADA HMI, Terminal or Console simulation 
#              program use the IEC-61850-MMS module <iec61850MmsComm.py> to connect 
#              to the IEC61850-PLC server to read and write data.
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

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'IEC61850_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import IEC61850 MMS Communication lib: ")
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
def hmiMainThread():
    print("[_] Init the IEC61850MMS client")
    client = mmsComm.Iec61850MmsClient('127.0.0.1', 102)
    client.connect()
    domanName = client.get_domains()
    print(domanName)
    time.sleep(1)
    while True:
        time.sleep(1)
        print("[_] Test verify the PLC internal logic")
        val1 = client.read('IED1LD0', 'MMXU1$MX$Hz$mag$f')
        showTestResult('float', val1[0], 'client read measurement : MMXU1$MX$Hz$mag$f')
        val2 = client.read('IED1LD0', 'MMXU1$MX$TotW$mag$f')
        showTestResult('float', val2[0], 'client read measurement : MMXU1$MX$TotW$mag$f')
        val3 = client.read('IED1LD0', 'MMXU1$MX$PhV$phsA$cVal$mag$f')
        showTestResult('float', val3[0], 'client read measurement : MMXU1$MX$PhV$phsA$cVal$mag$f')
        showTestResult(round(val1[1]+val2[1], 1) , round(val3[1], 1), 'client read measurement : MMXU1$MX$PhV$phsA$cVal$mag$f')
        val4 = client.read('IED1LD0', 'XCBR1$CO$Pos$ctlVal')
        showTestResult(('boolean',val1[1]+val2[1]<=100) , val4, 'client read control : XCBR1$CO$Pos$ctlVal')
        print("[_] Test verify the PLC internal logic")
        num1 = round(random.uniform(0, 100), 1)
        client.write('IED1LD0', 'GGIO1$MX$AnIn1$mag$f', 'float', num1)
        num2 = random.randint(0, 100)
        client.write('IED1LD0', 'GGIO1$SP$IntSP1$setVal', 'int', num2)
        time.sleep(2)
        val5 = client.read('IED1LD0', 'GGIO1$SP$AnSP1$setMag$f')
        showTestResult(round(num1+num2, 1), round(val5[1], 1), 'client read control : XCBR1$CO$Pos$ctlVal')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    hmiMainThread()