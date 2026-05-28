#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        mqttRtuServerTest.py
#
# Purpose:     This module is a simple RTU simulation program use the MQTT lib 
#              module <mqttComm.py> to simulate a RTU/IIoT with one MQTT broker
#              and one execution logic to handle variable read and changeable value 
#              set from client side.
#
# Author:      Yuancheng Liu
#
# Created:     2026/05/27
# Version:     v_0.0.1
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

TOPDIR = 'MQTT_RTU_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import MQTT lib: ")
try:
    import mqttComm
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class TestBroker(mqttComm.MQTTBroker):
    """ Test broker class, it will start a broker in sub-thread and multiple clients 
        to test the data read and transmit. 
    """

    def __init__(self, brokerName='testBroker', brokerPort=1883):
        super().__init__()
        self.mqttClients = []

    def executeLogic(self):
        """ The fan control logic overwrite the executeLogic in mqttComm.MQTTBroker. """
        print("> execute the control logic")
        temp = float(self.getParmVal('temperature'))
        mode = self.getParmVal('mode')
        print("temp = %s mode=%s" %(str(temp), mode))
        if mode == 'auto':
            if temp > 50:
                self.setParmVal('fan', 'on')
                self.setParmVal('fanSpeed', '50')
            else:
                self.setParmVal('fan', 'off')
                self.setParmVal('fanSpeed', '0')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MQTTbrokerThread(threading.Thread):
    """ MQTT broker thread class. """
    def __init__(self):
        threading.Thread.__init__(self)
        self.mqttBroker = TestBroker()
        self.mqttBroker.addParm('temperature', '25.0')
        self.mqttBroker.addParm('mode', 'manual')
        self.mqttBroker.addParm('fan', 'off')
        self.mqttBroker.addParm('fanSpeed', '0')

    def run(self):
        print("Starting MQTT broker thread.")
        self.mqttBroker.run()

    def getMQTTBroker(self):
        return self.mqttBroker

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class rtuSimulator(object):
    """ RTU simulator class. """
    def __init__(self):
        self.mqttBrokerThread = MQTTbrokerThread()
        self.brokerObj = self.mqttBrokerThread.getMQTTBroker()
        self.srcValDict = {
            'temperature': 25.0,
            'autoMode': False
        }
        self.destValDict = {
            'fanPwr': False,
            'fanSpeed': 0
        }
        self.mqttBrokerThread.start()
        self.terminate = False 

    def fetchDataFromPhysicalWorld(self):
        print("Fetch data from physical world.")
        self.srcValDict['temperature'] = random.uniform(10, 90)

    def run(self):
        while not self.terminate:
            self.fetchDataFromPhysicalWorld()
            self.brokerObj.setParmVal('temperature', str(self.srcValDict['temperature']))
            self.brokerObj.executeLogic()
            time.sleep(0.1) # sleep 0.1 sec to wait the broker's 
            self.srcValDict['autoMode'] = self.brokerObj.getParmVal('mode') == 'auto'
            self.destValDict['fanPwr'] = self.brokerObj.getParmVal('fan') == 'on'
            self.destValDict['fanSpeed'] = int(self.brokerObj.getParmVal('fanSpeed'))
            print("Source Parameter: %s" % str(self.srcValDict))
            print("Destination Parameter: %s" % str(self.destValDict))
            time.sleep(1)
            
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    rtuObj = rtuSimulator()
    rtuObj.run()