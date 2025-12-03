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

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
    async def runLadderLogic(self):
        print("Execute the ladder logic: compare 2 temperature value.")
        val1 = await self.parent.getVariableVal(VAR_ID1)
        val2 = await self.parent.getVariableVal(VAR_ID2)
        val3 = val1 >= val2
        await self.parent.updateVariable(VAR_ID3, val3)
        val4 = "Temp1=%sC, Temp2=%sC" %(str(val1), str(val2))
        await self.parent.updateVariable(VAR_ID4, val4)

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

class plcSimulator(object):
    """ PLC simulator class for test the ladder logic."""
    def __init__(self):
        self.opctuServerTh = opcuaServerThread(4840)
        self.ladderLogic = testLadder(self.opctuServerTh)
    
        self.srcVariableDict = {
            VAR_ID1: 10, 
        }





    def run(self):
        asyncio.run(self.ladder.runLadderLogic())