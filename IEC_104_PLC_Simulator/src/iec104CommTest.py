#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        ice104CommTest.py
#
# Purpose:     This module is the testcase program for the IEC-60870-5-104 comm 
#              library <iec104Comm.py>, it will start a server in sub-thread and 
#              init client to test the data read and transmit.
#
# Author:      Yuancheng Liu
#
# Created:     2025/05/07
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import c104
import iec104Comm
import threading

STATION_ADDR = 5
PT1_ADDR = 11
PT2_ADDR = 12
PT3_ADDR = 13

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class testLadder(iec104Comm.ladderLogic):

    def __init__(self, parent):
        iec104Comm.ladderLogic.__init__(self, parent)

    def runLadderLogic(self):
        print("Test server value read functions in test ladder class.")
        val1 = self.parent.getPointVal(STATION_ADDR, PT1_ADDR)
        showTestResult(c104.Step.LOWER, val1, "read point value1")
        val2 = self.parent.getPointVal(STATION_ADDR, PT2_ADDR)
        showTestResult(False, val2, "read point value2")
        val3 = self.parent.getPointVal(STATION_ADDR, PT3_ADDR)
        showTestResult(1.01, round(val3, 2), "read point value3")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class IEC104ServerThread(threading.Thread):
    """ IEC104 server thread class for host the PLC or RTU data and provide to clients."""
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.server = iec104Comm.iec104Server()
        # set the station 
        self.server.addStation(STATION_ADDR)
        # test add same station twice
        val = self.server.addStation(STATION_ADDR)
        showTestResult(None, val, "test add same station twice")

        # default step point
        self.server.addPoint(STATION_ADDR, PT1_ADDR)
        self.server.setPointVal(STATION_ADDR, PT1_ADDR, c104.Step.LOWER)
        # bool data point
        self.server.addPoint(STATION_ADDR, PT2_ADDR, pointType=iec104Comm.M_BOOL_TYPE)
        self.server.setPointVal(STATION_ADDR, PT2_ADDR, False)
        # float number data point
        self.server.addPoint(STATION_ADDR, PT3_ADDR, pointType=iec104Comm.M_FLOAT_TYPE)
        self.server.setPointVal(STATION_ADDR, PT3_ADDR, 1.01)

        val = self.server.addPoint(STATION_ADDR, PT3_ADDR, pointType=iec104Comm.C_STEP_TYPE)
        showTestResult(None, val, "test add same point twice")
        # Init the test ladder

    def getServer(self):
        return self.server

    #-----------------------------------------------------------------------------
    def updateValue(self):
        self.server.setPointVal(5, 11, c104.Step.HIGHER) # the changeable step will not be set
        self.server.setPointVal(5, 12, True)
        self.server.setPointVal(5, 13, 1.02)

    def run(self):
        self.server.startServer()

    def stop(self):
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    print("[_] Test server start")
    serverThread = IEC104ServerThread('0.0.0.0', 2404)
    serverThread.start()
    time.sleep(1)
    ladderLogic = testLadder(serverThread.getServer())
    ladderLogic.runLadderLogic()
    time.sleep(1)
    print("[_] Test client connection")
    client = iec104Comm.iec104Client('127.0.0.1')

    client.addStation(STATION_ADDR)
    client.addPoint(STATION_ADDR, PT1_ADDR)
    client.addPoint(STATION_ADDR, PT2_ADDR, pointType=c104.Type.M_SP_NA_1)
    client.addPoint(STATION_ADDR, PT3_ADDR, pointType=c104.Type.M_ME_NC_1)
    #test add out of range point
    val = client.addPoint(STATION_ADDR, -1)
    showTestResult(False, val, "test add out of range point")
    client.startConnection()
    print("[o] Test client connection pass.")
    time.sleep(1)

    print("Test read points")
    val1 = client.getServerPointValue(STATION_ADDR, PT1_ADDR)
    showTestResult(c104.Step.LOWER, val1, "client read point value1")

    val2 = client.getServerPointValue(STATION_ADDR, PT2_ADDR)
    showTestResult(False, val2, "client read point value2")

    val3 = client.getServerPointValue(STATION_ADDR, PT3_ADDR)
    showTestResult(1.01, round(val3, 2), "client read point value3")
    time.sleep(1)

    print("Test update points")
    serverThread.updateValue()

    val2 = client.getServerPointValue(STATION_ADDR, PT2_ADDR)
    showTestResult(True, val2, "client read point value2")

    val3 = client.getServerPointValue(STATION_ADDR, PT3_ADDR)
    showTestResult(1.02, round(val3, 2), "client read point value3")
    time.sleep(1)

    print("Test change point step value")
    client.setServerPointStepValue(STATION_ADDR, PT1_ADDR, c104.Step.HIGHER)
    server = serverThread.getServer()
    val0 = server.getPointVal(STATION_ADDR, PT1_ADDR)
    showTestResult(c104.Step.HIGHER, val0, "server read point value0")

    val1 = client.getServerPointValue(STATION_ADDR, PT1_ADDR)
    showTestResult(c104.Step.HIGHER, val1, "client read point value1")

    client.stopConnection()
    serverThread.stop()

if __name__ == '__main__':
    main()