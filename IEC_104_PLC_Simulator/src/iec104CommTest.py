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

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class IEC104ServerThread(threading.Thread):
    """ IEC104 server thread class for host the PLC or RTU data and provide to clients."""
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.server = iec104Comm.iec104Server()
        # set the station 
        self.server.addStation(STATION_ADDR)
        # default step point
        self.server.addPoint(STATION_ADDR, PT1_ADDR)
        self.server.setPointVal(STATION_ADDR, PT1_ADDR, c104.Step.LOWER)
        # bool data point
        self.server.addPoint(STATION_ADDR, PT2_ADDR, pointType=iec104Comm.M_BOOL_TYPE)
        self.server.setPointVal(STATION_ADDR, PT2_ADDR, False)
        # float number data point
        self.server.addPoint(STATION_ADDR, PT3_ADDR, pointType=iec104Comm.M_FLOAT_TYPE)
        self.server.setPointVal(STATION_ADDR, PT3_ADDR, 1.01)

    def testServerPtValRead(self):
        print("Test server value read functions.")
        print("Station dictionary: %s" %str(self.server.getStationsAddrDict()))
        val1 = self.server.getPointVal(STATION_ADDR, PT1_ADDR)
        rst = "[_] read point value1 pass." if val1 == c104.Step.LOWER else "[x] read point value1 error: %s." %str(val1)
        print(rst)
        val2 = self.server.getPointVal(STATION_ADDR, PT2_ADDR)
        rst = "[_] read point value2 pass." if val2 == False else "[x] read point value2 error: %s." %str(val1)
        print(rst)
        val3 = self.server.getPointVal(STATION_ADDR, PT3_ADDR)
        val3 = round(val3, 2)
        rst = "[_] read point value3 pass." if val3 == 1.01 else "[x] read point value3 error: %s." %str(val3)
        print(rst)

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
    print("[ ] Test server start")
    serverThread = IEC104ServerThread('0.0.0.0', 2404)
    serverThread.start()
    serverThread.testServerPtValRead()
    time.sleep(1)
    print("[ ] Test client connection")
    client = iec104Comm.iec104Client('127.0.0.1')

    client.addStation(STATION_ADDR)
    client.addPoint(STATION_ADDR, PT1_ADDR)
    client.addPoint(STATION_ADDR, PT2_ADDR, pointType=c104.Type.M_SP_NA_1)
    client.addPoint(STATION_ADDR, PT3_ADDR, pointType=c104.Type.M_ME_NC_1)
    client.startConnection()
    print("[_] Test client connection pass.")
    time.sleep(1)

    print("Test read points")
    val1 = client.getServerPointValue(STATION_ADDR, PT1_ADDR)
    rst = "[_] read point value1 pass." if val1 == c104.Step.LOWER else "[x] read point value1 error: %s." %str(val1)
    print(rst)

    val2 = client.getServerPointValue(STATION_ADDR, PT2_ADDR)
    rst = "[_] read point value2 pass." if val2 == False else "[x] read point value2 error: %s." %str(val2)
    print(rst)

    val3 = client.getServerPointValue(STATION_ADDR, PT3_ADDR)
    val3 = round(val3, 2)
    rst = "[_] read point value4 pass." if val3 == 1.01 else "[x] read point value4 error: %s." %str(val3)
    print(rst)
    time.sleep(1)

    print("Test update points")
    serverThread.updateValue()

    val2 = client.getServerPointValue(STATION_ADDR, PT2_ADDR)
    rst = "[_] read point value2 pass." if val2 == True else "[x] read point value2 error: %s." %str(val2)
    print(rst)

    val3 = client.getServerPointValue(STATION_ADDR, PT3_ADDR)
    val3 = round(val3, 2)
    rst = "[_] read point value3 pass." if val3 == 1.02 else "[x] read point value3 error: %s." %str(val3)
    print(rst)
    time.sleep(1)

    print("Test change point step value")
    client.setServerPointStepValue(STATION_ADDR, PT1_ADDR, c104.Step.HIGHER)
    server = serverThread.getServer()
    val0 = server.getPointVal(STATION_ADDR, PT1_ADDR)
    rst = "[_] server read server point value0 pass." if val0 == c104.Step.HIGHER else "[x] server read server point value1 error: %s." %str(val0)
    print(rst)

    val1 = client.getServerPointValue(STATION_ADDR, PT1_ADDR)
    rst = "[_] client read server point value1 pass." if val1 == c104.Step.HIGHER else "[x] client read server point value1 error: %s." %str(val1)
    print(rst)

    serverThread.stop()


if __name__ == '__main__':
    main()