#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        opcuaPlcServerTest.py
#
# Purpose:     This module is a simple PLC simulation program use the OPC-UA lib 
#              module <opcuaComm.py> to simulate a PLC with one OPC-UA-TCP server 
#              and one ladder logic to handle variable read and changeable value 
#              set from client side.
#
# Author:      Yuancheng Liu
#
# Created:     2025/12/03
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os
import sys
import time
import random
import asyncio
import threading

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
class testLadder(opcuaComm.ladderLogic):

    def __init__(self, parent):
        opcuaComm.ladderLogic.__init__(self, parent)

    def initLadderInfo(self):
        # init all the ladder source variables
        self.srcVarIDList.append(VAR_ID1)
        self.srcVarTypeList.append(UA_TYPE_INT16)
        self.srcVarIDList.append(VAR_ID2)
        self.srcVarTypeList.append(UA_TYPE_FLOAT)
        # init all the ladder destination variables
        self.destVarIDList.append(VAR_ID3)
        self.destVarTypeList.append(UA_TYPE_BOOL)
        self.destVarIDList.append(VAR_ID4)
        self.destVarTypeList.append(UA_TYPE_STRING)

    async def runLadderLogic(self):
        print("Execute the ladder logic: compare 2 temperature value.")
        val1 = await self.parent.getVariableVal(VAR_ID1)
        val2 = await self.parent.getVariableVal(VAR_ID2)
        val3 = val1 >= val2
        await self.parent.updateVariable(VAR_ID3, val3)
        val4 = "Temp1=%sC, Temp2=%sC" %(str(val1), str(val2))
        await self.parent.updateVariable(VAR_ID4, val4)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class opcuaServerThread(threading.Thread):
    """ OPC-UA server thread class for host the PLC or RTU data and provide to clients."""

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.server = opcuaComm.opcuaServer(SERVER_NAME, NAME_SPACE)

    #-----------------------------------------------------------------------------
    async def initDataStorage(self):
        await self.server.initServer()
        r0 = await self.server.addObject(NAME_SPACE, OBJ_NAME)
        showTestResult(True, r0, "Add new object")
        showTestResult(False, await self.server.addObject(NAME_SPACE, OBJ_NAME),
                       "Add an exists object")
        # Add the value

        idx = self.server.getNameSpaceIdx(NAME_SPACE)
        # Added the overwrite mode variables
        m1 = await self.server.addVariable(idx, OBJ_NAME, SRC_OW_MD, False)
        m2 = await self.server.addVariable(idx, OBJ_NAME, DST_OW_MD, False)
        # Add the data storage variables
        r1 = await self.server.addVariable(idx, OBJ_NAME, VAR_ID1, 1)
        showTestResult(True, r1, "Add new int variable")
        r2 = await self.server.addVariable(idx, OBJ_NAME, VAR_ID2, 1.1)
        showTestResult(True, r2, "Add new float variable")
        r3 = await self.server.addVariable(idx, OBJ_NAME, VAR_ID3, True)
        showTestResult(True, r3, "Add new bool variable")
        r4 = await self.server.addVariable(idx, OBJ_NAME, VAR_ID4, 'testStr')
        showTestResult(True, r4, "Add new string variable")
        return True

    def getServer(self):
        return self.server

    def run(self):
        data = asyncio.run(self.server.getVariableVal(VAR_ID1))
        print(VAR_ID1 + " = " + str(data))
        asyncio.run(self.server.runServer())
        print("OPC-UA server thread exit.")

    def stop(self):
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class plcSimulator(object):
    """ PLC simulator class for test the ladder logic."""
    def __init__(self):
        self.opcuaServerTh = opcuaServerThread(4840)
        self.ladderLogic = None 
        self.srcVariableDict = {
            VAR_ID1: 10, 
            VAR_ID2: 20.0
        }
        self.destVariableDict = {
            VAR_ID3: False,
            VAR_ID4: 'Information_String'
        }
        self.terminate = False 

    def runLadderLogic(self):
        print("Run the physcial ladder logic")
        compareRst = self.srcVariableDict[VAR_ID1] >= self.srcVariableDict[VAR_ID2]
        self.destVariableDict[VAR_ID3] = compareRst
        self.destVariableDict[VAR_ID4] = "Temp1=%sC, Temp2=%sC" %(str(self.srcVariableDict[VAR_ID1]), str(self.srcVariableDict[VAR_ID2]))

    def fetchDataFromPhysicalWorld(self):
        print("Fetch data from physical world.")
        self.srcVariableDict[VAR_ID1] = random.randint(0, 100)
        self.srcVariableDict[VAR_ID2] = random.uniform(0, 100)

    async def run(self):
        await self.opcuaServerTh.initDataStorage()
        self.ladderLogic = testLadder(self.opcuaServerTh.getServer())
        self.opcuaServerTh.start()
        time.sleep(1)
        while not self.terminate:
            # simulate fetch real world simulator's components data
            self.fetchDataFromPhysicalWorld()
            srcOwMd = await self.opcuaServerTh.getServer().getVariableVal(SRC_OW_MD)
            if srcOwMd:
                val1 = await self.opcuaServerTh.getServer().getVariableVal(VAR_ID1)
                val2 = await self.opcuaServerTh.getServer().getVariableVal(VAR_ID2)
                if val1 != self.srcVariableDict[VAR_ID1] or val2 != self.srcVariableDict[VAR_ID2]:
                    print("Source variable value updated.")
                    self.srcVariableDict[VAR_ID1] = val1
                    self.srcVariableDict[VAR_ID2] = val2
            else:
                await self.opcuaServerTh.getServer().updateVariable(VAR_ID1, self.srcVariableDict[VAR_ID1])
                await self.opcuaServerTh.getServer().updateVariable(VAR_ID2, self.srcVariableDict[VAR_ID2])
            
            time.sleep(0.1)
            self.runLadderLogic()
            time.sleep(0.1)    
            
            destOwMd = await self.opcuaServerTh.getServer().getVariableVal(DST_OW_MD)
            if destOwMd:
                val3 = await self.opcuaServerTh.getServer().getVariableVal(VAR_ID3)
                val4 = await self.opcuaServerTh.getServer().getVariableVal(VAR_ID4)
                if val3 != self.destVariableDict[VAR_ID3] or val4 != self.destVariableDict[VAR_ID4]:
                    print("Destination variable value updated.")
                    self.destVariableDict[VAR_ID3] = val3
                    self.destVariableDict[VAR_ID4] = val4
            else:
                await self.opcuaServerTh.getServer().updateVariable(VAR_ID3, self.destVariableDict[VAR_ID3])
                await self.opcuaServerTh.getServer().updateVariable(VAR_ID4, self.destVariableDict[VAR_ID4])
            # simulate set real world simulator's components data
            print("Current internal coil data status:")
            print(str(self.destVariableDict))
            time.sleep(0.5)
        print("PLC simulator thread exit.")

    def stop(self):
        self.terminate = True
        self.opcuaServerTh.stop()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    plcObj = plcSimulator()
    asyncio.run(plcObj.run())