#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        ice104CommTest.py
#
# Purpose:     This module will provide the IEC-60870-5-104 client and server 
#              communication API for testing or simulating the data flow connection 
#              between PLC/RTU and SCADA system. The module is implemented based 
#              on python iec104-python lib module: 
#              - Reference: https://github.com/Fraunhofer-FIT-DIEN/iec104-python
#
# Author:      Yuancheng Liu
#
# Created:     2025/04/27
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time 
import iec104Comm
import threading

class IEC104ServerThread(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.server = iec104Comm.iec104Server()
        # set the station 
        testStationAddr = 5 
        self.server.addStation(testStationAddr)
        
        testReadPointAddr = 11
        self.server.addPoint(testStationAddr, testReadPointAddr)

        testWritePointAddr = 12
        self.server.addPoint(testStationAddr, testWritePointAddr)

        self.server.setPointVal(testStationAddr, testReadPointAddr, False)

        self.server.setPointVal(testStationAddr, testWritePointAddr, True)

    def run(self):
        self.server.startServer()

    def stop(self):
        self.server.stopServer()


def main():
    print("Test server start")
    serverThread = IEC104ServerThread('0.0.0.0', 2404)
    serverThread.start()
    time.sleep(1)
    print("Test client connection")
    client = iec104Comm.iec104Client('127.0.0.1')
    testStationAddr = 5 
    client.addStation(testStationAddr)
    testReadPointAddr = 11
    client.addPoint(testStationAddr, testReadPointAddr)
    testWritePointAddr = 12
    client.addPoint(testStationAddr, testWritePointAddr)
    client.startClient()

    print("test read points")
    val1 = client.readServerPointValue(testStationAddr, testReadPointAddr)
    if val1 == False:
        print("read point value1 pass.")
    else:
        print("[x] read point value1 error.")

    val2 = client.readServerPointValue(testStationAddr, testWritePointAddr)
    if val2 == True:
        print("read point value2 pass.")
    else:
        print("[x] read point value2 error.")

    serverThread.stop()


if __name__ == '__main__':
    main()