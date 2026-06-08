#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        mqttRtuServerTest.py
#
# Purpose:     This module is a simple RTU simulation program use the MQTT lib 
#              module <mqttComm.py> to simulate a RTU/IIoT with one MQTT client
#              to connect to the server to simulate the RTU data publish and 
#              subscribe.
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
class RtuConnector(object):

    def __init__(self, clientId, host, port=1883):
        self.mHost = host
        self.mPort = port
        self.mClientId = clientId
        self.client = mqttComm.MQTTClient(clientId, host, port=1883)
        self.client.connect()

    #-----------------------------------------------------------------------------
    def startTest(self):
        index = 0
        print("Start the client test")
        #self.client.watch_all()
        #exit()

        index += 1
        print("\nTest-%d Subscribe data from the server." % index)
        temp = self.client.getParmVal('temperature')
        mode = self.client.getParmVal('mode')
        fan = self.client.getParmVal('fan')
        fanS = self.client.getParmVal('fanSpeed')
        print("Temperature : %s" % temp)
        showTestResult('manual', mode, 'Fan status')
        showTestResult('off', fan, 'Fan status')
        showTestResult('0', fanS, 'Fan speed')
        time.sleep(1)

        index += 1
        print("\nTest-%d Publish data to the server." % index)
        self.client.setParmVal('mode', 'auto')
        temp = float(self.client.getParmVal('temperature'))
        mode = self.client.getParmVal('mode')
        showTestResult('auto', mode, 'Fan status')
        time.sleep(1)
        fan = self.client.getParmVal('fan')
        fanS = self.client.getParmVal('fanSpeed')
        if temp > 50:
            showTestResult('on', fan, 'Fan status')
            showTestResult('50', fanS, 'Fan speed')
        else:
            showTestResult('off', fan, 'Fan status')
            showTestResult('0', fanS, 'Fan speed')

        #Reset the value 
        self.client.setParmVal('mode', 'manual')
        time.sleep(2)
        self.client.setParmVal('fan', 'off')
        self.client.setParmVal('fanSpeed', '0')
        self.client.disconnect()

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 1883
    clientId = 'rtuClient'
    rtu = RtuConnector(clientId, host, port)
    rtu.startTest()