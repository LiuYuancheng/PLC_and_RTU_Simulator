#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        opcuaPlcClientTest.py
#
# Purpose:     This module is a simple PLC connector program use the OPC-UA lib 
#              module <opcuaComm.py> to simulate a SCADA device with one OPC-UA-TCP  
#              client to connect to the <opcuaPlcServerTest.py> to random setup the 
#              source variables value then verify the result.
# 
# Author:      Yuancheng Liu
#
# Created:     2025/12/04
# Version:     v_0.0.3
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os
import sys
import time
import random
import asyncio
import threading
from queue import Queue

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'OPCUA_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import opcuaComm lib: ")
try:
    import opcuaComm
    from opcuaComm import UA_TYPE_BOOL, UA_TYPE_INT16, UA_TYPE_FLOAT, UA_TYPE_STRING
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

SERVER_NAME = 'TestPlc01'
NAME_SPACE = 'newNameSpace01'
OBJ_NAME = 'newObject01'
VAR_ID1 = 'Temperature_var1'
VAR_ID2 = 'Temperature_var2'
VAR_ID3 = 'compare_bool_var'
VAR_ID4 = 'combine_message'
SRC_OW_MD = 'Src_overwrite_mode'
DST_OW_MD = 'Dst_overwrite_mode'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class opcuaClientThread(threading.Thread):
    """ OPC-UA client thread class to init a client and fetch the data from the
        PLC simulator.
    """

    def __init__(self, port):
        threading.Thread.__init__(self)
        serverUrl = "opc.tcp://localhost:4840/%s/server/" % SERVER_NAME
        self.client = opcuaComm.opcuaClient(serverUrl)
        self.srcVariableDict = {
            VAR_ID1: None, 
            VAR_ID2: None
        }
        self.destVariableDict = {
            VAR_ID3: None,
            VAR_ID4: None 
        }
        self.cmdQueue = Queue(maxsize=3)
        self.terminate = False

    #----------------------------------------------------------------------------- 
    def run(self):
        asyncio.run(self.plcDataProcessLoop())

    #-----------------------------------------------------------------------------
    async def plcDataProcessLoop(self):
        print("Start opcua client thread...")
        await self.client.connect()
        while not self.terminate:
            print("Fetch data from PLC")
            val1 = await self.client.getVariableVal(NAME_SPACE, OBJ_NAME, VAR_ID1)
            val2 = await self.client.getVariableVal(NAME_SPACE, OBJ_NAME, VAR_ID2)
            self.srcVariableDict = {
                VAR_ID1: val1, 
                VAR_ID2: val2
            }
            val3 = await self.client.getVariableVal(NAME_SPACE, OBJ_NAME, VAR_ID3)
            val4 = await self.client.getVariableVal(NAME_SPACE, OBJ_NAME, VAR_ID4)
            self.destVariableDict = {
                VAR_ID3: val3,
                VAR_ID4: val4
            }
            print("Send control command to PLC")
            while not self.cmdQueue.empty():
                (varibleName, value) = self.cmdQueue.get()
                await self.client.setVariableVal(NAME_SPACE, OBJ_NAME, varibleName, value)
            time.sleep(0.5)
    
    #-----------------------------------------------------------------------------
    def getSourceVariableDict(self):
        return self.srcVariableDict

    def getDestVariableDict(self):
        return self.destVariableDict

    #-----------------------------------------------------------------------------
    def setPlcVariable(self, varibleName, value):
        if not self.cmdQueue.full():
            self.cmdQueue.put((varibleName, value))
        else:
            print("PLC connector queue is full, please wait for the previous command to be executed.")

    async def stop(self):
        self.terminate = True
        await self.client.disconnect()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PlcConnector(object):
    """ PLC ladder logic class, this class will be inherited by your ladder diagram,
        and you need to implement initLadderInfo() and runLadderLogic() function.
    """
    def __init__(self, parent, ladderName='TestLadderDiagram'):
        self.parent = parent
        self.opcUAClientTh = opcuaClientThread(4840)
        self.opcUAClientTh.start()
        self.terminate = False

    async def run(self):
        # Set auto modo first
        time.sleep(2)
        print("Set PLC auto mode")
        #await self.opcUAClientTh.setPlcVariable(SRC_OW_MD, False)
        #await self.opcUAClientTh.setPlcVariable(DST_OW_MD, False)
        
        print("[_] verify PLC auto ladder logic execution.")
        srcDataDict = self.opcUAClientTh.getSourceVariableDict()
        expectVal3 = srcDataDict[VAR_ID1] > srcDataDict[VAR_ID2]
        expectVal4 = "Temp1=%sC, Temp2=%sC" %(str(srcDataDict[VAR_ID1]), str(srcDataDict[VAR_ID2]))
        destDataDict = self.opcUAClientTh.getDestVariableDict()
        showTestResult(expectVal3, destDataDict[VAR_ID3], "Compare bool value")
        showTestResult(expectVal4, destDataDict[VAR_ID4], "Combine message")
        time.sleep(1)

        print("[_] verify PLC src manual mode data overwrite ladder logic execution.")
        expectVal1 = 20
        expectVal2 = 10.5
        expectVal3 = True
        expectVal4 = "Temp1=20C, Temp2=10.5C"
        print("Change the mode to manual mode")
        self.opcUAClientTh.setPlcVariable(SRC_OW_MD, True)
        print("Change the value to 20 and 10.5")
        self.opcUAClientTh.setPlcVariable(VAR_ID1, expectVal1)
        self.opcUAClientTh.setPlcVariable(VAR_ID2, expectVal2)
        time.sleep(2)
        srcDataDict = self.opcUAClientTh.getSourceVariableDict()
        showTestResult(expectVal1, srcDataDict[VAR_ID1], "temp value1")
        showTestResult(expectVal2, srcDataDict[VAR_ID2], "temp value2")
        destDataDict = self.opcUAClientTh.getDestVariableDict()
        showTestResult(expectVal3, destDataDict[VAR_ID3], "Compare bool value")
        showTestResult(expectVal4, destDataDict[VAR_ID4], "Combine message")
        
        print("[_] verify PLC dest manual mode data overwrite ladder logic execution.")
        self.opcUAClientTh.setPlcVariable(DST_OW_MD, True)
        random_bool1 = random.choice([True, False])
        expectVal4 = "Overwrite message from manual mode"
        self.opcUAClientTh.setPlcVariable(VAR_ID3, random_bool1)
        self.opcUAClientTh.setPlcVariable(VAR_ID4, expectVal4)
        time.sleep(2)
        destDataDict = self.opcUAClientTh.getDestVariableDict()
        showTestResult(random_bool1, destDataDict[VAR_ID3], "Compare bool value")
        showTestResult(expectVal4, destDataDict[VAR_ID4], "Combine message")

        await self.opcUAClientTh.stop()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    plcObj = PlcConnector(None)
    time.sleep(2)
    asyncio.run(plcObj.run())