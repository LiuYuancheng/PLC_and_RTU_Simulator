#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        iec104PlcClientTest.py
#
# Purpose:     This module is a test case program of the lib module <iec104Comm.py>
#              to simulate a HMI read or set data from the test simulated PLC module 
#              <iec104PlcServerTest.py>
# 
# Author:      Yuancheng Liu
#
# Created:     2025/05/10
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os
import sys
import time
import random 
import c104


print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'IEC_104_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import lib: ")
try:
    import iec104Comm
    from iec104Comm import M_BOOL_TYPE, M_FLOAT_TYPE, C_STEP_TYPE
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# same station and point configuration as the server side.
STATION_ADDR = 47
PT1_ADDR = 11
PT2_ADDR = 12
PT3_ADDR = 13
PT4_ADDR = 14
PT5_ADDR = 15

client = iec104Comm.iec104Client('127.0.0.1')
client.addStation(STATION_ADDR)
client.addPoint(STATION_ADDR, PT1_ADDR, pointType=M_BOOL_TYPE)
client.addPoint(STATION_ADDR, PT2_ADDR, pointType=M_BOOL_TYPE)
client.addPoint(STATION_ADDR, PT3_ADDR, pointType=C_STEP_TYPE)
client.addPoint(STATION_ADDR, PT4_ADDR, pointType=C_STEP_TYPE)
client.addPoint(STATION_ADDR, PT5_ADDR, pointType=M_FLOAT_TYPE)
client.startConnection()

for i in range(10):
    print("Start client I/O test round %s" %str(i))
    random_bool1 = random.choice([True, False])
    random_bool2 = random.choice([True, False])
    print("Set value pt3 and pt3:")
    print(random_bool1)
    print(random_bool2)
    val3 = c104.Step.HIGHER if random_bool1 else c104.Step.LOWER
    val4 = c104.Step.HIGHER if random_bool2 else c104.Step.LOWER
    client.setServerPointStepValue(STATION_ADDR, PT3_ADDR, val3)
    time.sleep(0.1)
    client.setServerPointStepValue(STATION_ADDR, PT4_ADDR, val4)
    time.sleep(0.1)
    time.sleep(2)
    val1 = client.getServerPointValue(STATION_ADDR, PT1_ADDR)
    showTestResult(random_bool1, val1, "read point 1")
    val2 = client.getServerPointValue(STATION_ADDR, PT2_ADDR)
    showTestResult(random_bool2, val2, "read point 2")
    val5 = client.getServerPointValue(STATION_ADDR, PT5_ADDR)
    val5 = round(val5, 2)
    expectVal = 1.01 if val1 and val2 else 1.02
    showTestResult(expectVal, val5, "read point 5")
    time.sleep(3)
    client.setServerPointStepValue(STATION_ADDR, PT3_ADDR, c104.Step.INVALID_0)
    client.setServerPointStepValue(STATION_ADDR, PT4_ADDR, c104.Step.INVALID_0)
    time.sleep(1)

client.stopConnection()