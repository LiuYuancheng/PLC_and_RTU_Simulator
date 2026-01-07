#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        BACCommTest.py
#
# Purpose:     This module is the testcase program for the ISO 16484-5 BACnet comm
#              library <BACnetComm.py>, it will start a server in sub-thread and
#              init client to test the data read, write and the auto ladder logic
#              execution functions.
#
# Author:      Yuancheng Liu
#
# Created:     2026/01/06
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import threading
import BACnetComm

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." % message if val == expectVal else "[x] %s error, expect:%s, get: %s." % (
        message, str(expectVal), str(val))
    print(rst)

DEV_ID = 123456
DEV_NAME = "TestBACDevice"

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
                "units": "degreesCelsius",
                "readonly": False
            },
            {
                "objectName": "Humidity",
                "objectIdentifier": ("analogValue", 2),
                "presentValue": 45.0,
                "description": "Room Humidity",
                "units": "percent",
                "readonly": False
            },
            {
                "objectName": "Pressure",
                "objectIdentifier": ("analogValue", 3),
                "presentValue": 101.3,
                "description": "Atmospheric Pressure",
                "units": "kilopascals",
                "readonly": True
            }
        ]

        for parameter in simpleAnalogVal:
            #print(parameter)
            self.server.addAnalogObject(parameter["objectName"], 
                                parameter["objectIdentifier"][1], 
                                parameter["presentValue"], 
                                parameter["description"], 
                                parameter["units"],
                                readOnly=parameter["readonly"])
        
    def getObjValue(self, objName):
        return self.server.getObjValue(objName)
    
    def setObjValue(self, objName, value):
        return self.server.setObjValue(objName, value)

    def run(self):
        self.server.runServer()

    def runLadderLogic(self):
        print("Run the internal ladder logic")
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
    showTestResult(42.5, r1, "Read the object property 'Humidity' value")

if __name__ == "__main__":
    main()