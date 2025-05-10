#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        iec104PlcServerTest.py
#
# Purpose:     This module is a test case program of the lib module <iec104Comm.py>
#              to simulate a PLC with one IEC104 server and one ladder logic to handle 
#              measured value read and changeable value set from client side.
#
# Author:      Yuancheng Liu
#
# Created:     2025/05/09
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os
import sys
import time
import random
import threading
import c104 # pip install c104

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'IEC_104_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import c104Comm lib: ")
try:
    import iec104Comm
    from iec104Comm import M_BOOL_TYPE, M_FLOAT_TYPE, C_STEP_TYPE
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

STATION_ADDR = 47
PT1_ADDR = 11 # measured bool val 1
PT2_ADDR = 12 # measured bool val 2
PT3_ADDR = 13 # changeable step val3
PT4_ADDR = 14 # changeable step val4
PT5_ADDR = 15 # measured float val 5

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class testLadderLogic(iec104Comm.ladderLogic):
    """ A test ladder logic :  
        PT3_ADDR -> PT1_ADDR
        PT4_ADDR -> PT2_ADDR
        PT1_ADDR & PT2_ADDR -> PT5_ADDR
    """
    def __init__(self, parent) -> None:
        super().__init__(parent)

    def initLadderInfo(self):
        self.stationAddr = STATION_ADDR 
        self.srcPointAddrList = [PT1_ADDR, PT2_ADDR, PT3_ADDR, PT4_ADDR]
        self.srcPointTypeList = [M_BOOL_TYPE, M_BOOL_TYPE, C_STEP_TYPE, C_STEP_TYPE]
        self.destPointAddrList = [PT5_ADDR]
        self.destPointTypeList = [M_FLOAT_TYPE]

    def runLadderLogic(self):
        print("Run ladder logic")
        val3 = self.parent.getPointVal(self.stationAddr, self.srcPointAddrList[2])
        if val3 == c104.Step.HIGHER:
            self.parent.setPointVal(self.stationAddr, self.srcPointAddrList[0],True)
        elif val3 == c104.Step.LOWER:
            self.parent.setPointVal(self.stationAddr, self.srcPointAddrList[0],False)

        val4 = self.parent.getPointVal(self.stationAddr, self.srcPointAddrList[3])
        if val4 == c104.Step.HIGHER:
            self.parent.setPointVal(self.stationAddr, self.srcPointAddrList[1],True)
        elif val4 == c104.Step.LOWER:
            self.parent.setPointVal(self.stationAddr, self.srcPointAddrList[1],False)

        val1 = self.parent.getPointVal(self.stationAddr, self.srcPointAddrList[0])
        val2 = self.parent.getPointVal(self.stationAddr, self.srcPointAddrList[1])

        if val1 and val2:
            self.parent.setPointVal(self.stationAddr, self.destPointAddrList[0], 1.01)
        else:
            self.parent.setPointVal(self.stationAddr, self.destPointAddrList[0], 1.02)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class IEC104ServerThread(threading.Thread):
    """ IEC104 server thread class for host the PLC or RTU data and provide to clients."""
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.server = iec104Comm.iec104Server()
        self.server.addStation(STATION_ADDR)
        self.server.addPoint(STATION_ADDR, PT1_ADDR, pointType=M_BOOL_TYPE)
        self.server.addPoint(STATION_ADDR, PT2_ADDR, pointType=M_BOOL_TYPE)
        self.server.addPoint(STATION_ADDR, PT3_ADDR, pointType=C_STEP_TYPE)
        self.server.addPoint(STATION_ADDR, PT4_ADDR, pointType=C_STEP_TYPE)
        self.server.addPoint(STATION_ADDR, PT5_ADDR, pointType=M_FLOAT_TYPE)
        self.server.setPointVal(STATION_ADDR, PT1_ADDR, False)
        self.server.setPointVal(STATION_ADDR, PT2_ADDR, True)
        self.server.setPointVal(STATION_ADDR, PT3_ADDR, c104.Step.INVALID_0)
        self.server.setPointVal(STATION_ADDR, PT4_ADDR, c104.Step.INVALID_0)
        self.server.setPointVal(STATION_ADDR, PT5_ADDR, 0.0)

    def getServer(self):
        return self.server
    
    def run(self):
        self.server.startServer()

    def stop(self):
        self.server.stopServer()

print("Test the IEC104 PLC function: \n")

print("Start the server thread.")
serverThread = IEC104ServerThread('0.0.0.0', 2404)
serverThread.start()
time.sleep(1)
server = serverThread.getServer()
# init the ladder logic 
ladderLogic = testLadderLogic(server)

while True:
    # simulate measurement data change
    random_bool = random.choice([True, False])
    print("Random measured value: %s" %str(random_bool))
    server.setPointVal(STATION_ADDR, PT1_ADDR, random_bool)
    server.setPointVal(STATION_ADDR, PT2_ADDR, random_bool)
    ladderLogic.runLadderLogic()
    val1 = server.getPointVal(STATION_ADDR, PT1_ADDR)
    val2 = server.getPointVal(STATION_ADDR, PT2_ADDR)
    rst = 1.01 if val1&val2 else 1.02
    val = server.getPointVal(STATION_ADDR, PT5_ADDR)
    if val == None:
        print("Error: Ladder execution: None")
        continue
    showTestResult(round(rst,2), round(val,2), "Ladder execution check" )
    time.sleep(1)

serverThread.stop()