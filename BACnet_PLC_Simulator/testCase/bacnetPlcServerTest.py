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
import random
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
DEV_NAME = "TestBACnetServerDevice"

PARM_ID1 = 1
PARM_ID2 = 2
PARM_ID3 = 3
PARM_ID4 = 4
PARM_ID5 = 5

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class BACnetServerThread(threading.Thread):
    def __init__(self, port=47808):
        threading.Thread.__init__(self)
        self.server = BACnetComm.BACnetServer(DEV_ID, DEV_NAME)

    #-----------------------------------------------------------------------------
    def addParameter(self, parameter):
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
        # Init the input and output manual module flag 1 - True, 0 - False
        self.initModeFlag()
        # Init the parameters.
        self.srcVariableDict = {
            'Temperature': 22.5,
            'Humidity': 45.0,
        }
        self.destVariableDict = {
            'Pressure': 101.3,
        }
        self.initParameters()
        self.terminate = False
        time.sleep(1)
        self.server.start()

    #-----------------------------------------------------------------------------
    def initModeFlag(self):
        inputFlag = {
                "objectName": "InputManualFlag",
                "objectIdentifier": ("analogValue", PARM_ID1),
                "presentValue": 0,
                "description": "Input manual flag",
                "units": "bool"
        }
        self.server.addParameter(inputFlag)

        outputFlag = {
                "objectName": "OutputManualFlag",
                "objectIdentifier": ("analogValue", PARM_ID2),
                "presentValue": 0,
                "description": "Output manual flag",
                "units": "bool"
        }
        self.server.addParameter(outputFlag)

    #-----------------------------------------------------------------------------
    def initParameters(self):
        simpleAnalogVal = [
            {
                "objectName": "Temperature",
                "objectIdentifier": ("analogValue", PARM_ID3),
                "presentValue": 22.5,
                "description": "Room Temperature",
                "units": "degreesCelsius"
            },
            {
                "objectName": "Humidity",
                "objectIdentifier": ("analogValue", PARM_ID4),
                "presentValue": 45.0,
                "description": "Room Humidity",
                "units": "percent"
            },
            {
                "objectName": "Pressure",
                "objectIdentifier": ("analogValue", PARM_ID5),
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
        self.destVariableDict['Pressure'] = round(self.srcVariableDict['Temperature'] + self.srcVariableDict['Humidity'], 1)
        print("Generate output pressure vale %s" %str(self.destVariableDict['Pressure']))

    def fetchDataFromPhysicalWorld(self):
        print("Fetch data from physical world.")
        self.srcVariableDict['Temperature'] = round(random.uniform(20.0, 50.0),1)
        self.srcVariableDict['Humidity'] = round(random.uniform(20.0, 50.0),1)

    def periodic(self):
        print("Start the BACnet PLC main periodic loop.")
        self.fetchDataFromPhysicalWorld()
        while not self.terminate:
            self.fetchDataFromPhysicalWorld()
            srcOWMd = int(self.server.getObjValue("InputManualFlag"))
            if srcOWMd == 1:
                val1 = self.server.getObjValue("Temperature")
                val2 = self.server.getObjValue("Humidity")
                self.srcVariableDict['Temperature'] = val1
                self.srcVariableDict['Humidity'] = val2
            else:
                self.server.setObjValue('Temperature', self.srcVariableDict['Temperature'])
                r1 = self.server.getObjValue("Temperature")
                showTestResult( self.srcVariableDict['Temperature'], round(r1, 1), "Update Temperature")
                self.server.setObjValue('Humidity', self.srcVariableDict['Humidity'])
                r2 = self.server.getObjValue("Humidity")
                showTestResult( self.srcVariableDict['Humidity'], round(r2, 1), "Update Humidity")

            self.runLadderLogic()

            dstOWMd = int(self.server.getObjValue("OutputManualFlag"))
            if dstOWMd == 1:
                val = self.server.getObjValue("Pressure")
                self.destVariableDict['Pressure'] = val
            else:
                self.server.setObjValue('Pressure', self.destVariableDict['Pressure'])
                r3 = self.server.getObjValue("Pressure")
                showTestResult( self.destVariableDict['Pressure'], round(r3, 1), "Update Pressure")

            val1 = self.server.getObjValue("Temperature")
            val2 = self.server.getObjValue("Humidity")
            val3 = self.server.getObjValue("Pressure")
            print("Current parameter val are %s, %s, %s" %(str(val1), str(val2), str(val3)))
            time.sleep(2)

    def stop(self):
        self.terminate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    plcObj = plcSimulator()
    plcObj.periodic()
