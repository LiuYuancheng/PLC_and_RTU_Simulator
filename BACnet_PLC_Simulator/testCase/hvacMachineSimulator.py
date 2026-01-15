#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        HvacMachineSimulator.py
#
# Purpose:     This module is a simple building center Heating Ventilation and 
#              Air Conditioning(HVAC) machine simulator program with the basic 
#              auto control function based on the controller's setting. It will 
#              host one BAC server which can  accept multiple clients(controller)'s 
#              control request.
#
# Author:      Yuancheng Liu
#
# Created:     2026/01/10
# Version:     v_0.0.3
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

#-----------------------------------------------------------------------------
DEV_ID = 123456
DEV_NAME = "HVAC_Signal_Receiver"

PARM_ID1 = 1
PARM_ID2 = 2
PARM_ID3 = 3
PARM_ID4 = 4
PARM_ID5 = 5
PARM_ID6 = 6

PARM_ID11 = 11
PARM_ID12 = 12
PARM_ID13 = 13

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
class hvacSimulator(object):
    def __init__(self):
        self.terminate = False
        self.server = BACnetServerThread()
        self.initModeFlag()
        self.initInternalParams()
        self.initControlParams()
        time.sleep(0.5)
        self.server.start()

    #-----------------------------------------------------------------------------
    def initModeFlag(self):
        """ Init the input and output overwrite flag: 0-auto_mode, 1-manual_mode."""
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
    def initInternalParams(self):
        """ Init the internal sensor and components control parameters."""
        simpleAnalogVal = [
            {
                "objectName": "Sensor_Temperature",
                "objectIdentifier": ("analogValue", PARM_ID3),
                "presentValue": 22.5,
                "description": "Room Temperature",
                "units": "degreesCelsius"
            },
            {
                "objectName": "Sensor_Humidity",
                "objectIdentifier": ("analogValue", PARM_ID4),
                "presentValue": 45.0,
                "description": "Room Humidity",
                "units": "percent"
            },
            {
                "objectName": "Compressor_Power",
                "objectIdentifier": ("analogValue", PARM_ID5),
                "presentValue": 1,  # 0 off, 1 idle, 2 working
                "description": "Atmospheric Pressure",
                "units": "kilopascals"
            },
            {
                "objectName": "Heater_Power",
                "objectIdentifier": ("analogValue", PARM_ID6),
                "presentValue": 0,  # 0 off, 1 idle, 2 working
                "description": "Atmospheric Pressure",
                "units": "kilopascals"
            }
        ]
        for parameter in simpleAnalogVal:
            self.server.addParameter(parameter)

    #-----------------------------------------------------------------------------
    def initControlParams(self):
        """ Init the thermostat controller's parameters."""
        simpleAnalogVal = [
            {
                "objectName": "Control_Temperature",
                "objectIdentifier": ("analogValue", PARM_ID11),
                "presentValue": 22.5,
                "description": "Room Temperature",
                "units": "degreesCelsius"
            },
            {
                "objectName": "Control_Fan_Speed",
                "objectIdentifier": ("analogValue", PARM_ID12),
                "presentValue": 1, # range 0 - 10
                "description": "Fan Speed",
                "units": "level"
            },
            {
                "objectName": "Hvac_Power",
                "objectIdentifier": ("analogValue", PARM_ID13),
                "presentValue": 1,  # 0 off, 1 Cooling, 2 Heating
                "description": "HVAC Power Control",
                "units": "bool"
            },
        ]
        for parameter in simpleAnalogVal:
            self.server.addParameter(parameter)

    #-----------------------------------------------------------------------------
    def periodic(self):
        print("Start the center HVAC main periodic loop.")
        while not self.terminate:
            # Hvac auto control logic
            print("\n*** Start One new HVAC Auto-Control Around...***")
            power = int(self.server.getObjValue("Hvac_Power"))
            print("Hvac_Power mode: %s" %str(('OFF', 'Cooling', 'Heating')[min(power, 2)]))
            time.sleep(0.5)
            ctrlTemp = round(self.server.getObjValue("Control_Temperature"), 1)
            print("Control_Temperature: %s °C" % str(ctrlTemp))
            time.sleep(0.5)
            sensorTemp = round(
                self.server.getObjValue("Sensor_Temperature"), 1)
            print("Sensor_Temperature: %s °C" % str(sensorTemp))
            fanSpeed = int(self.server.getObjValue("Control_Fan_Speed"))
            print("Control_Fan_Speed: lvl-%s" % str(fanSpeed))
            time.sleep(0.5)
            # set a random humanity value
            self.server.setObjValue("Sensor_Humidity", round(random.uniform(20.0, 60.0),1))
            time.sleep(0.5)
            if power == 0:
                print("HVAC is OFF, no auto control")
                # Keep both heater and compressor off
                self.server.setObjValue("Heater_Power", 0)
                self.server.setObjValue("Compressor_Power", 0)
            elif power == 1:
                print("Start cooling process.")
                print("[*] Make sure heater is off")
                self.server.setObjValue("Heater_Power", 0)
                if sensorTemp > ctrlTemp:
                    print("[*] Sensor_Temperature > Control_Temperature, set compressor [power on]")
                    self.server.setObjValue("Compressor_Power", 2)
                    # update the sensor value
                    newSensorTemp = sensorTemp - 0.1
                    self.server.setObjValue("Sensor_Temperature", newSensorTemp)
                else:
                    print("[*] Sensor_Temperature <= Control_Temperature, set compressor [idle]")
                    self.server.setObjValue("Compressor_Power", 1)
            elif power == 2:
                print("Start heating process.")
                print("[*] Make sure compressor is off")
                self.server.setObjValue("Compressor_Power", 0)
                if sensorTemp < ctrlTemp:
                    print("[*] Sensor_Temperature < Control_Temperature, set heater [power on]")
                    self.server.setObjValue("Heater_Power", 2)
                    # update the sensor value
                    newSensorTemp = sensorTemp + 0.1
                    self.server.setObjValue("Sensor_Temperature", newSensorTemp)
                else:
                    print("[*] Sensor_Temperature >= Control_Temperature, set heater [idle]")
                    self.server.setObjValue("Heater_Power", 1)
            time.sleep(2)

    def stop(self):
        self.terminate = True
        
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    havcObj = hvacSimulator()
    havcObj.periodic()
