#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        dnp3CommTest.py
#
# Purpose:     This module is the test case program for the (IEEE 1815) DNP3.0  
#              library <dnp3Comm.py>, it will start a server in sub-thread and 
#              init 2 clients to test the data read and write function.
#
# Author:      Yuancheng Liu
#
# Created:     2026/07/28
# Version:     v_0.0.3
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import random 
import threading 

import dnp3Comm

TYPE_NAMES = {
    dnp3Comm.GRP_BINARY_INPUT: "BinaryInput        (G1V2)",
    dnp3Comm.GRP_ANALOG_INPUT: "AnalogInput        (G30V1)",
    dnp3Comm.GRP_BINARY_OUTPUT_STATUS: "BinaryOutputStatus (G10V2)",
    dnp3Comm.GRP_ANALOG_OUTPUT_STATUS: "AnalogOutputStatus (G40V1)",
}

def print_readout(data: dict):
    for gv in dnp3Comm.READABLE_TYPES:
        label = TYPE_NAMES[gv]
        values = data.get(gv, {})
        if not values:
            print(f"  {label}: (no data returned)")
            continue
        rendered = ", ".join(f"[{i}]={v}" for i, v in sorted(values.items()))
        print(f"  {label}: {rendered}")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." % message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
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

    def runLadderLogic(self):
        # random set the input value
        v1 = random.choice([True, False])
        self.server.setBinaryInput(0, v1)
        v2 = random.choice([True, False])
        self.server.setBinaryInput(1, v2)
        v3 = float(random.randint(0, 100))
        self.server.setAnalogInput(0, v3)

        v4 = self.server.getBinaryOutput(0)
        v5 = self.server.getBinaryOutput(1)
        if v4 and v5:
            self.server.setAnalogOutput(0, 100-v3)
        else:
            self.server.setAnalogOutput(0, 100+v3)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    print("[_] Test server start")
    serverThread = DNP3ServerThread()
    serverThread.start()
    serverObj = serverThread.getDNP3ServerObj()
    print("[_] Test multiple client connection and read data.")
    time.sleep(1)
    client1 = dnp3Comm.DNP3Client("127.0.0.1")
    client1.connect()
    time.sleep(1)
    client2 = dnp3Comm.DNP3Client("127.0.0.1")
    client2.connect()
    serverThread.runLadderLogic()
    data = client1.readAll()
    print(data)
    print("[_] Test client write data to binary output.")
    client2.writeBinaryOutput(0, True)
    client2.writeBinaryOutput(1, True)
    serverThread.runLadderLogic()
    v3 = serverObj.getAnalogInput(0)
    data = client1.readAll()
    result = data.get(dnp3Comm.GRP_ANALOG_INPUT).get(0)
    showTestResult(v3, result, "AnalogInput check")

    print("[_] Test client write data to Analog output.")
    val = 35
    client1.writeAnalogOutput(0, val)
    time.sleep(0.2)
    data = client1.readAll()
    result = data.get(dnp3Comm.GRP_ANALOG_OUTPUT_STATUS).get(0)
    showTestResult(val, result, "AnalogOutput check")
    
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()  





