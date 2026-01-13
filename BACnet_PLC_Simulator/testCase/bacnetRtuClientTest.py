#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        bacnetRtuClientTest.py
#
# Purpose:     This module is a simple RTU connector program use the BACnet comm 
#              module <BACnetComm.py> to simulate a SCADA device with one BACnet  
#              client to connect to the <bacnetRTUServerTest.py> to random setup the 
#              source variables value then verify the result.
# 
# Author:      Yuancheng Liu
#
# Created:     2026/01/07
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os
import sys
import time
import random

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
DEV_NAME = "TestBACnetClientDevice"

SERVER_ADDR = "127.0.0.1:47808" 

PARM_ID1 = 1
PARM_ID2 = 2
PARM_ID3 = 3
PARM_ID4 = 4
PARM_ID5 = 5

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class RTUConnector(object):
    """ RTU ladder logic class, this class will be inherited by your ladder diagram,
        and you need to implement initLadderInfo() and runLadderLogic() function.
    """
    def __init__(self, parent, ladderName='TestLadderDiagram'):
        self.parent = parent
        self.client = BACnetComm.BACnetClient(DEV_ID, DEV_NAME, '127.0.0.1', 47808)

    def run(self):
        print("[_] Test read data from server start")
        flag1 = int(self.client.readObjProperty(SERVER_ADDR, PARM_ID1))
        showTestResult(0, flag1, "Read the 'InputManualFlag' value.")
        flag2 = int(self.client.readObjProperty(SERVER_ADDR, PARM_ID2))
        showTestResult(0, flag2, "Read the 'OutputManualFlag' value.")
        val1 = self.client.readObjProperty(SERVER_ADDR, PARM_ID3)
        print("val1=%s" %str(val1))
        time.sleep(0.1)
        val2 = self.client.readObjProperty(SERVER_ADDR, PARM_ID4)
        print("val2=%s" %str(val2))
        time.sleep(0.1)
        val3 = self.client.readObjProperty(SERVER_ADDR, PARM_ID5)
        print("val3=%s" %str(val3))
        time.sleep(0.1)
        showTestResult(round(val3, 1), round(val1 + val2, 1), "Read the RTU input and output value.")
        time.sleep(0.5)
        print("[_] Test write data to server input start")
        self.client.writeObjProperty(SERVER_ADDR, PARM_ID1, 1.0)
        time.sleep(0.1)
        flag1 = int(self.client.readObjProperty(SERVER_ADDR, PARM_ID1))
        showTestResult(1, flag1, "Write the 'InputManualFlag' value.")
        val1 = round(random.uniform(20.0, 50.0),1)
        val2 = round(random.uniform(20.0, 50.0),1)
        self.client.writeObjProperty(SERVER_ADDR, PARM_ID3, val1)
        self.client.writeObjProperty(SERVER_ADDR, PARM_ID4, val2)
        time.sleep(2.1) # sleep more that 2 sec to wait the ladder execution finish.
        val3 = self.client.readObjProperty(SERVER_ADDR, PARM_ID3)
        showTestResult(val1, round(val3, 1), "Write the RTU input 1 value.")
        val4 = self.client.readObjProperty(SERVER_ADDR, PARM_ID4)
        showTestResult(val2, round(val4, 1), "Write the RTU input 2 value.")
        val5 = self.client.readObjProperty(SERVER_ADDR, PARM_ID5)
        showTestResult(round(val5, 1), round(val1 + val2, 1), "Write the RTU input and output value.")
        time.sleep(0.5)
        print("[_] Test write data to server output start")
        self.client.writeObjProperty(SERVER_ADDR, PARM_ID2, 1.0)
        time.sleep(0.1)
        flag2 = int(self.client.readObjProperty(SERVER_ADDR, PARM_ID2))
        showTestResult(1, flag2, "Write the 'OutputManualFlag' value.")
        val3 = round(random.uniform(20.0, 50.0),1)
        self.client.writeObjProperty(SERVER_ADDR, PARM_ID5, val3)
        time.sleep(0.5)
        val4 = self.client.readObjProperty(SERVER_ADDR, PARM_ID5)
        showTestResult(val3, round(val4, 1), "Write the RTU output value.")
        # reset the overwrite flag and clean the connection
        self.client.writeObjProperty(SERVER_ADDR, PARM_ID1, 0)
        self.client.writeObjProperty(SERVER_ADDR, PARM_ID2, 0)
        self.client.cleanup()
        print("Client shut down successfully.")

def main():
    connector = RTUConnector(None)
    connector.run()

if __name__ == "__main__":
    main()