#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        BACnetCommTest.py
#
# Purpose:     This module is the testcase program for the ISO 16484-5 BACnet comm
#              library <BACnetComm.py>, it will start a server in sub-thread and
#              init client to test the data read, write and the auto ladder logic
#              execution functions.
#
# Author:      Yuancheng Liu
#
# Created:     2026/01/06
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import sys
import time
import threading
import BACnetComm

DEV_ID = 123456
DEV_NAME = "TestBACDevice"

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." % message if val == expectVal else "[x] %s error, expect:%s, get: %s." % (
        message, str(expectVal), str(val))
    print(rst)
    time.sleep(0.2)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class BACnetServerThread(threading.Thread):
    def __init__(self, port=47808):
        threading.Thread.__init__(self)
        self.server = BACnetComm.BACnetServer(DEV_ID, DEV_NAME)
        self.initParameters()

    #-----------------------------------------------------------------------------
    def initParameters(self):
        simpleAnalogVal = [
            {
                "objectName": "Temperature",
                "objectIdentifier": ("analogValue", 1),
                "presentValue": 22.5,
                "description": "Room Temperature",
                "units": "degreesCelsius"
            },
            {
                "objectName": "Humidity",
                "objectIdentifier": ("analogValue", 2),
                "presentValue": 45.0,
                "description": "Room Humidity",
                "units": "percent"
            },
            {
                "objectName": "Pressure",
                "objectIdentifier": ("analogValue", 3),
                "presentValue": 101.3,
                "description": "Atmospheric Pressure",
                "units": "kilopascals"
            }
        ]

        for parameter in simpleAnalogVal:
            #print(parameter)
            self.server.addAnalogObject(parameter["objectName"], 
                                parameter["objectIdentifier"][1], 
                                parameter["presentValue"], 
                                parameter["description"], 
                                parameter["units"])
    
    #-----------------------------------------------------------------------------
    def getObjValue(self, objName):
        return self.server.getObjValue(objName)
    
    def setObjValue(self, objName, value):
        return self.server.setObjValue(objName, value)

    def run(self):
        self.server.runServer()

    #-----------------------------------------------------------------------------
    def runLadderLogic(self):
        #print("Run the internal ladder logic")
        val1 = self.server.getObjValue("Temperature")
        val2 = self.server.getObjValue("Humidity")
        val3 = val1 + val2 
        self.server.setObjValue("Pressure", val3)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    print("[_] Test BACnet server start")
    serverThread = BACnetServerThread()
    serverThread.start()
    time.sleep(1)
    r0 = serverThread.getObjValue("Temperature")
    showTestResult(22.5, r0, "Read the object property 'Temperature' value")

    serverThread.setObjValue("Humidity", 42.5)
    r1 = serverThread.getObjValue("Humidity")
    showTestResult(42.5, r1, "Set the object property 'Humidity' value")

    serverThread.runLadderLogic()
    r2 = serverThread.getObjValue("Pressure")
    showTestResult(r0+r1, r2, "Test run simple ladder logic")

    print("[_] Test BACnet client start")
    serveraddr = "127.0.0.1:47808" 
    client = BACnetComm.BACnetClient(2, "TestClient", '127.0.0.1', 47808)
    time.sleep(1)
    r3 = client.readObjProperty(None, 1)
    showTestResult(22.5, r3, "Read the object property 'Temperature' value")
    
    client.writeObjProperty(serveraddr, 2, 50.1)
    r4 = client.readObjProperty(serveraddr, 2)
    showTestResult(50.1, round(r4, 1), "Write the object property 'Humidity' value")

    serverThread.runLadderLogic()
    r5 = client.readObjProperty(serveraddr, 3)
    showTestResult(72.6, round(r5, 1), "Test run simple ladder logic")
    client.cleanup()
    print("Client shut down successfully.")
    print("Server shutting down...")
    sys.exit(0)
    
if __name__ == "__main__":
    main()