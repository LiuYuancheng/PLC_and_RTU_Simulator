#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        rtuClientTest.py
#
# Purpose:     This module is a test case program of lib module <snap7Comm.py> 
#              to start a S7comm client connecting to the <rtuServerTest.py> to 
#              test set and read the data from S7comm (rtu/plc) server.
#
# Author:      Yuancheng Liu
#
# Created:     2024/03/41
# Version:     v_0.1.4
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import os
import sys
import time

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'S7Comm_RTU_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
# found it - truncate right after TOPDIR
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath
# Config the lib folder
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

#-----------------------------------------------------------------------------
print("Test import lib: ")
try:
    import snap7Comm
    from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

#-----------------------------------------------------------------------------
# Import dll file for windows platform.
libpath = os.path.join(gLibDir, 'snap7.dll')
print("Import snap7 dll path: %s" % str(libpath))
if os.path.exists(libpath):
    print("- pass")
else:
    print("Error: not file the dll file.")
    exit()

#-----------------------------------------------------------------------------
# Test cases:

client = snap7Comm.s7CommClient('127.0.0.1', rtuPort=102, snapLibPath=libpath)

print("\nTestcase01: set bool val in memory addrIdx=1, dataIdx=0, val=True")
client.setAddressVal(1, 0, True, dataType=BOOL_TYPE)
time.sleep(0.2)
val = client.readAddressVal(1, dataIdxList=(0,), dataTypeList=(BOOL_TYPE,))[0]
rst = 'pass' if val else 'fail'
print("Result: %s" % str(rst))
time.sleep(1)

print("\nTestcase02: set int val in memory addrIdx=1, dataIdx=2, val=5")
client.setAddressVal(1, 2, 5, dataType=INT_TYPE)
time.sleep(0.2)
val = client.readAddressVal(1, dataIdxList=(2,), dataTypeList=(INT_TYPE,))[0]
rst = 'pass' if val == 5 else 'fail'
print("Result: %s" % str(rst))
time.sleep(1)

print("\nTestcase03: set real val in memory addrIdx=1, dataIdx=4, val=3.14150")
client.setAddressVal(1, 4, 3.14150, dataType=REAL_TYPE)
time.sleep(0.2)
val = client.readAddressVal(1, dataIdxList=(4,), dataTypeList=(REAL_TYPE,))[0]
print(val)
time.sleep(1)

print("\nTestcase04: test ladder logic execution: after set addrIdx=2, dataIdx4, the dataIdx will set to same value.")
client.setAddressVal(2, 4, 5.0, dataType=REAL_TYPE)
time.sleep(0.2)
client.setAddressVal(2, 0, 3.0, dataType=REAL_TYPE)
time.sleep(0.2)
val = client.readAddressVal(2, dataIdxList=(0, 4), dataTypeList=(REAL_TYPE, REAL_TYPE))
print("Init addrIdx2, dataidx0, val=%s" %str(val[0]))
print("Init addrIdx2, dataidx4, val=%s" %str(val[1]))
time.sleep(0.2)
client.setAddressVal(2, 4, 3.14150, dataType=REAL_TYPE)
time.sleep(0.2)
val = client.readAddressVal(2, dataIdxList=(0, 4), dataTypeList=(REAL_TYPE, REAL_TYPE))

rst1, rst2 = round(val[0], 5), round(val[1], 5)
print("After run ladder logic addrIdx2, dataidx0, val=%s" %str(rst1))
print("After run ladder logic addrIdx2, dataidx4, val=%s" %str(rst2))
rst = 'pass' if rst1 == rst2 else 'fail'
print("Result: %s" % str(rst))
time.sleep(1)

client.close()
