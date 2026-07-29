#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        dnp3RtuClientTest.py
#
# Purpose:     This module is a simple RTU simulation program use the DNP3 lib 
#              module <dnp3Comm.py> to simulate a PLC/RTU with one DNP3.0 client
#              to read and write data from the connected DNP3.0 server side
#
# Author:      Yuancheng Liu
#
# Created:     2026/07/27
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

TOPDIR = 'DNP3_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import DNP3 Communication lib: ")
try:
    import dnp3Comm
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

SEV_IP = '127.0.0.1'
SEV_PORT = dnp3Comm.DNP3_PORT

def main():
    print("DNP3 RTU Client Test Start ...")
    dnp3Client = dnp3Comm.DNP3Client(SEV_IP, port=SEV_PORT)
    dnp3Client.connect()

    if dnp3Client.getConnectionState():
        print("DNP3 RTU Client connected to server.")
    else:
        print("DNP3 RTU Client connect to server failed.")
        exit()
    print("[_] Start to overwrite the RTU output data")
    ob1 = random.choice([True, False])
    ob2 = random.choice([True, False])
    oa1 = random.randint(0, 100)
    print("Output Binary 0: %s" % str(ob1))
    print("Output Binary 1: %s" % str(ob2))
    print("Output Analog 0: %s" % str(oa1))
    dnp3Client.writeBinaryOutput(0, ob1)
    dnp3Client.writeBinaryOutput(1, ob2)
    dnp3Client.writeAnalogOutput(0, oa1)
    time.sleep(2) # wait 1 sec to make sure the RTU data updated.

    print("[_] Start to read the RTU input data")
    data = dnp3Client.readAll()
    print(data)
    ib1 = data.get(dnp3Comm.GRP_BINARY_INPUT).get(0)
    showTestResult(not ob1, ib1, "Read binary input 0")
    ib2 = data.get(dnp3Comm.GRP_BINARY_INPUT).get(1)
    showTestResult(not ob2, ib2, "Read binary input 1")
    ia1 = data.get(dnp3Comm.GRP_ANALOG_INPUT).get(0)
    rst = 100-oa1 if ib1 and ib2 else 100+oa1
    showTestResult(ia1, rst, "Read analog input 0")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()  