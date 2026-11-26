#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        iec61850MmsCommTest.py
#
# Purpose:     This module is the testcase program for the IEC-61850-MMS comm 
#              library <iec61850MmsComm.py>, it will start a MMS server in one 
#              sub-thread and init one MMS client to test the data read and transmit.
#
# Author:      Yuancheng Liu
#
# Created:     2026/11/26
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time 
import threading
import iec61850MmsComm as mmsComm

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class Iec61850MmsServerThread(threading.Thread):

    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.server = mmsComm.Iec61850MmsServer()
        self.modelName = 'IED1LD0'
        self.server.addModel(self.modelName, venderName='WagosElt')
        # set measurement logic nodes
        self.server.addLogicNode(self.modelName, 'MMXU1$MX$Hz$mag$f', 'float', 50.0)
        self.server.addLogicNode(self.modelName, 'MMXU1$MX$TotW$mag$f', 'float', 1250.0, writable=True)
        # set the GGIO logic nodes
        self.server.addLogicNode(self.modelName, 'GGIO1$SP$IntSP1$setVal', 'integer', 100, writable=True)
        self.server.addLogicNode(self.modelName, 'GGIO1$DC$Desc$d', 'string', 'Generic I/O', writable=True)

    def run(self):
        self.server.startService()

    def getLnVal(self, itemName):
        return self.server.getParamterVal(self.modelName, itemName)

    def setLnVal(self, itemName, val):
        self.server.setParamterVal(self.modelName, itemName, val)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    print("[_] Test server start")
    server = Iec61850MmsServerThread('127.0.0.1', 102)
    server.start()
    time.sleep(1)
    val1 = server.getLnVal('MMXU1$MX$Hz$mag$f')
    showTestResult(('float', 50.0), val1, 'server get measurement : MMXU1$MX$Hz$mag$f')
    val2 = server.getLnVal('MMXU1$MX$TotW$mag$f')
    showTestResult(('float', 1250.0), val2, 'server get measurement : MMXU1$MX$TotW$mag$f')
    val3 = server.getLnVal('GGIO1$DC$Desc$d')
    showTestResult(('string','Generic I/O'), val3, 'server get GGIO : GGIO1$DC$Desc$d')
    val4 = server.getLnVal('GGIO1$SP$IntSP1$setVal')
    showTestResult(('integer', 100), val4, 'server get GGIO : GGIO1$SP$IntSP1$setVal')
    
    print("[_] Test client start")
    client = mmsComm.Iec61850MmsClient('127.0.0.1', 102)
    client.connect()
    domanName = client.get_domains()
    print(domanName)
    # get the vendor information
    val1 = client.read('IED1LD0', 'LLN0$DC$NamPlt$vendor')
    showTestResult(('string', 'WagosElt'), val1, 'client get Logical Node Zero : LLN0$DC$NamPlt$vendor')
    # get the model name
    val2 = client.read('IED1LD0', 'LLN0$DC$NamPlt$swRev')
    showTestResult(('string', '0.0.1'), val2, 'client get Logical Node Zero : LLN0$DC$NamPlt$swRev')
    val3 = client.read('IED1LD0', 'LLN0$ST$Beh$stVal')
    showTestResult(('integer', 1), val3, 'client get Logical Node Zero : LLN0$LN0$mod')

    print("[_] Test client data reading")
    val1 = client.read('IED1LD0', 'MMXU1$MX$Hz$mag$f')
    showTestResult(('float', 50.0), val1, 'client get measurement : MMXU1$MX$Hz$mag$f')
    val2 = client.read('IED1LD0', 'MMXU1$MX$TotW$mag$f')
    showTestResult(('float', 1250.0), val2, 'client get measurement : MMXU1$MX$TotW$mag$f')
    val3 = client.read('IED1LD0', 'GGIO1$DC$Desc$d')
    showTestResult(('string','Generic I/O'), val3, 'client get GGIO : GGIO1$DC$Desc$d')
    val4 = client.read('IED1LD0', 'GGIO1$SP$IntSP1$setVal')
    showTestResult(('integer', 100), val4, 'client get GGIO : GGIO1$SP$IntSP1$setVal')

    print("[_] Test server modify value")
    server.setLnVal('MMXU1$MX$TotW$mag$f', 200.0)
    time.sleep(0.5)
    val1 = server.getLnVal('MMXU1$MX$TotW$mag$f')
    showTestResult(('float', 200.0), val1, 'server get measurement : MMXU1$MX$TotW$mag$f')
    val2 = client.read('IED1LD0', 'MMXU1$MX$TotW$mag$f')
    showTestResult(('float', 200.0), val2, 'client get measurement : MMXU1$MX$TotW$mag$f')

    print("[_] Test client modify value")
    client.write('IED1LD0', 'GGIO1$SP$IntSP1$setVal', 'integer', 200)
    time.sleep(0.5)
    val1 = server.getLnVal('GGIO1$SP$IntSP1$setVal')
    showTestResult(('integer', 200), val1, 'server get GGIO : GGIO1$SP$IntSP1$setVal')
    val2 = client.read('IED1LD0', 'GGIO1$SP$IntSP1$setVal')
    showTestResult(('integer', 200), val2, 'client get GGIO : GGIO1$SP$IntSP1$setVal')
    
    print("[_] Test client modify un-writable value")
    try:
        client.write('IED1LD0', 'LLN0$DC$NamPlt$vendor', 'string', 'anyvender')
    except Exception as e:
        print(e)
    time.sleep(0.5)
    val1 = client.read('IED1LD0', 'LLN0$DC$NamPlt$vendor')
    showTestResult(('string', 'WagosElt'), val1, 'client get Logical Node Zero : LLN0$DC$NamPlt$vendor')

    time.sleep(1)
    client.close()
    server.server.stopService()
    print("[_] Test done.")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()