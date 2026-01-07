#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        bacnetServerTest.py
#
# Purpose:     This module is a simple BACnet device simulation program use the 
#              module <BACnetComm.py> to simulate a PLC with one BACnet server 
#              and one ladder logic to handle variable read and changeable value 
#              set from client side.
#
# Author:      Yuancheng Liu
#
# Created:     2026/01/07
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os
import sys
import time
import threading

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'BACnet_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import BACnetComm lib: ")
try:
    import BACnetComm
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

DEV_ID = 123456
DEV_NAME = "TestBACDevice"

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class BACnetServerThread(threading.Thread):
    def __init__(self, port=47808):
        threading.Thread.__init__(self)
        self.server = BACnetComm.BACnetServer(DEV_ID, DEV_NAME)

    #-----------------------------------------------------------------------------
    def addParameter(self, parameter)
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
#-----------------------------------------------------------------------------
class plcSimulator(object):

    def __init__(self):
        self.server = BACnetServerThread()
        time.sleep(0.1)
        self.initParameters()
        self.terminate = False
        self.server.start()

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
            self.server.addParameter(parameter)

    #-----------------------------------------------------------------------------
    def runLadderLogic(self):
        #print("Run the internal ladder logic")
        val1 = self.server.getObjValue("Temperature")
        val2 = self.server.getObjValue("Humidity")
        val3 = val1 + val2 
        self.server.setObjValue("Pressure", val3)
    
    
    def periodic(self):
        print("Start the BACnet PLC main periodic loop.")
        while not self.terminate:
