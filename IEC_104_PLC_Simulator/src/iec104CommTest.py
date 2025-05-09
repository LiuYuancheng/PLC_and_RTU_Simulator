#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        ice104CommTest.py
#
# Purpose:     This module is the case case program for the 
#
# Author:      Yuancheng Liu
#
# Created:     2025/04/27
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import c104
import iec104Comm
import threading

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class IEC104ServerThread(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.server = iec104Comm.iec104Server()
        # set the station 
        testStationAddr = 5 
        self.server.addStation(testStationAddr)
        # default 
        ptAddr1 = 11
        self.server.addPoint(testStationAddr, ptAddr1)
        self.server.setPointVal(testStationAddr, ptAddr1, c104.Step.LOWER)

        ptAddr2 = 12
        self.server.addPoint(testStationAddr, ptAddr2, pointType=iec104Comm.M_BOOL_TYPE)
        self.server.setPointVal(testStationAddr, ptAddr2, False)

        ptAddr3 = 13
        self.server.addPoint(testStationAddr, ptAddr3, pointType=iec104Comm.M_FLOAT_TYPE)
        self.server.setPointVal(testStationAddr, ptAddr3, 1.01)

    #-----------------------------------------------------------------------------
    def updateValue(self):
        self.server.setPointVal(5, 11, c104.Step.HIGHER)
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
    time.sleep(1)
    print("[ ] Test client connection")
    client = iec104Comm.iec104Client('127.0.0.1')

    testStationAddr = 5 
    client.addStation(testStationAddr)
    ptAddr1 = 11
    client.addPoint(testStationAddr, ptAddr1)
    ptAddr2 = 12
    client.addPoint(testStationAddr, ptAddr2, pointType=c104.Type.M_SP_NA_1)
    ptAddr3 = 13
    client.addPoint(testStationAddr, ptAddr3, pointType=c104.Type.M_ME_NC_1)
    client.startConnection()
    print("[_] Test client connection pass.")
    time.sleep(1)

    print("Test read points")
    val1 = client.setServerPointValue(testStationAddr, ptAddr1)
    rst = "[_] read point value1 pass." if val1 == c104.Step.LOWER else "[x] read point value1 error: %s." %str(val1)
    print(rst)

    val2 = client.setServerPointValue(testStationAddr, ptAddr2)
    rst = "[_] read point value2 pass." if val2 == False else "[x] read point value2 error: %s." %str(val2)
    print(rst)

    val3 = client.setServerPointValue(testStationAddr, ptAddr3)
    val3 = round(val3, 2)
    rst = "[_] read point value4 pass." if val3 == 1.01 else "[x] read point value4 error: %s." %str(val3)
    print(rst)
    time.sleep(1)

    print("Test update points")
    serverThread.updateValue()

    val2 = client.setServerPointValue(testStationAddr, ptAddr2)
    rst = "[_] read point value2 pass." if val2 == True else "[x] read point value2 error: %s." %str(val2)
    print(rst)

    val3 = client.setServerPointValue(testStationAddr, ptAddr3)
    val3 = round(val3, 2)
    rst = "[_] read point value4 pass." if val3 == 1.02 else "[x] read point value4 error: %s." %str(val3)
    print(rst)
    time.sleep(1)

    print("Test change point step value")
    client.setServerPointStepValue(testStationAddr, ptAddr1, c104.Step.HIGHER)

    val1 = client.setServerPointValue(testStationAddr, ptAddr1)
    rst = "[_] read point value1 pass." if val1 == c104.Step.HIGHER else "[x] read point value1 error: %s." %str(val1)
    print(rst)


    serverThread.stop()


if __name__ == '__main__':
    main()