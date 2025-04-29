#-----------------------------------------------------------------------------
# Name:        plcClientTest.py
#
# Purpose:     This module is a test case program of lib module <modbusTcpCom.py>
#              to start a ModBus-TCP client connecting to the <plcServerTest.py> to 
#              test set and read the data from PLC server.
#
# Author:      Yuancheng Liu
#
# Created:     2023/06/11
# Version:     v_0.1.4
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License      
#-----------------------------------------------------------------------------

import os
import sys
import time

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'Modbus_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
# found it - truncate right after TOPDIR
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath
# Config the lib folder
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir):
    sys.path.insert(0, gLibDir)

#-----------------------------------------------------------------------------
print("Test import lib: ")
try:
    import modbusTcpCom
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

#-----------------------------------------------------------------------------
hostIp = '127.0.0.1'
hostPort = 502

client = modbusTcpCom.modbusTcpClient(hostIp)

print('\nTestcase 01: test ModBus server connection.')

while not client.checkConn():
    print('try connect to the PLC')
    print(client.getCoilsBits(0, 4))
    time.sleep(0.5)
print('- pass')

print('\nTestcase 02: read the coils: ')
result = client.getCoilsBits(0, 4)
if result == [True, True, False, False]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

print('\nTestCase 03: read the holding registers')
result = client.getHoldingRegs(0, 4)
if result == [0, 0, 1, 1]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

print('\nTestcase 04: Set the holding registers')
client.setHoldingRegs(1, 1)
time.sleep(0.5)
result = client.getHoldingRegs(0, 4)
if result == [0, 1, 1, 1]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

print('\nTestcase 05: check auto update coils function')
result = client.getCoilsBits(0, 4)
if result == [True, False, False, False]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

print('\nTestcase 06: Set the coils')
client.setCoilsBit(1, 1)
time.sleep(0.5)
result = client.getCoilsBits(0, 4)
if result == [True, True, False, False]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

client.close()
