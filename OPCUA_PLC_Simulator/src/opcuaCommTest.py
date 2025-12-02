#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        opcuaCommTest.py
#
# Purpose:     This module is the testcase program for the IEC62541 OPC-UA comm 
#              library <opcuaComm.py>, it will start a server in sub-thread and 
#              init client to test the data read, write and the auto ladder logic 
#              execution functions.
#
# Author:      Yuancheng Liu
#
# Created:     2025/11/30
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import asyncio
import threading
import opcuaComm

SERVER_NAME = 'TestPlc01'
NAME_SPACE = 'newNameSpace01'
OBJ_NAME = 'TestObject01'

VAR_ID1 = 'variable01'
VAR_ID2 = 'variable02'
VAR_ID3 = 'variable03'
VAR_ID4 = 'variable04'

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class testLadder(opcuaComm.ladderLogic):

    def __init__(self, parent):
        opcuaComm.ladderLogic.__init__(self, parent)
        self.expectVal1 = None
        self.expectVal2 = None 
        self.expectVal3 = None
        self.expectVal4 = None 

    def setExpectVal(self, val1, val2, val3, val4):
        self.expectVal1 = val1
        self.expectVal2 = val2
        self.expectVal3 = val3
        self.expectVal4 = val4

    async def runLadderLogic(self):
        print("Test server value read functions in test ladder class.")
        val1 = await self.parent.getVariableVal(VAR_ID1)
        showTestResult(self.expectVal1 , val1, "verify new set int value")
        val2 = await self.parent.getVariableVal(VAR_ID2)
        showTestResult(self.expectVal2, val2, "verify new set float value")
        val3 = await self.parent.getVariableVal(VAR_ID3)
        showTestResult(self.expectVal3, val3, "verify new set bool value")
        val = str(val1 + val2) 
        await self.parent.updateVariable(VAR_ID4, val)
        await self.parent.getVariableVal(VAR_ID4)
        showTestResult(self.expectVal4, val, "verify ladder logic execution")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class opcuaServerThread(threading.Thread):
    """ OPC-UA server thread class for host the PLC or RTU data and provide to clients."""
    def __init__(self, port):
        threading.Thread.__init__(self)
        serverName = 'TestPlc01'
        self.nameSpace = 'newNameSpace01'
        self.server = opcuaComm.opcuaServer(serverName, self.nameSpace)

    #-----------------------------------------------------------------------------
    async def initDataStorage(self):
        await self.server.initServer()
        r0 = await self.server.addObject(self.nameSpace, 'newObject01')
        showTestResult(True, r0, "Add new object")
        showTestResult(False, await self.server.addObject(self.nameSpace, 'newObject01'), 
                       "Add an exists object")
        # Add the value
        idx = self.server.getNameSpaceIdx(self.nameSpace)
        r1 = await self.server.addVariable(idx, 'newObject01', VAR_ID1, 1)
        showTestResult(True, r1, "Add new int variable")
        r2 = await self.server.addVariable(idx, 'newObject01', VAR_ID2, 1.1)
        showTestResult(True, r2, "Add new float variable")
        r3 = await self.server.addVariable(idx, 'newObject01', VAR_ID3, True)
        showTestResult(True, r3, "Add new bool variable")
        r4 = await self.server.addVariable(idx, 'newObject01', VAR_ID4, 'testStr')
        showTestResult(True, r4, "Add new string variable")
        return True 
    
    def getServer(self):
        return self.server

    def run(self):
        data = asyncio.run(self.server.getVariableVal(VAR_ID1))
        print(VAR_ID1 + " = " +str(data))
        asyncio.run(self.server.runServer())
        print("OPC-UA server thread exit.")

    def stop(self):
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
async def main():
    print("[_] Test OPC-UA server start")
    serverThread = opcuaServerThread('127.0.0.1', 4840)
    await serverThread.initDataStorage()
    ladderLogic = testLadder(serverThread.getServer())
    serverThread.start()
    time.sleep(1)
    
    print("[_] Test client connection")
    serverName = 'TestPlc01'
    serverUrl = "opc.tcp://localhost:4840/%s/server/" %serverName
    client = opcuaComm.opcuaClient(serverUrl)
    await client.connect()
    r1 = await client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID1)
    showTestResult(1, r1, "client read int value1")
    r2 = await client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID2)
    showTestResult(1.1, r2, "client read float value1")
    r3 = await client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID3)
    showTestResult(True, r3, "client read float value1")
    r4 = await client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID4)
    showTestResult('testStr', r4, "client read float value1")

    print("[_] Test client write value")
    await client.setVariableVal('newNameSpace01','newObject01', VAR_ID1, 2)
    await client.setVariableVal('newNameSpace01','newObject01', VAR_ID2, 2.3)
    await client.setVariableVal('newNameSpace01','newObject01', VAR_ID3, False)
    r1 = await client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID1)
    showTestResult(2, r1, "client write int value1")
    r2 = await client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID2)
    showTestResult(2.3, r2, "client write int value1")
    r3 = await client.getVariableVal('newNameSpace01', 'newObject01', VAR_ID3)
    showTestResult(False, r3, "client write int value1")

    print("[_] Test ladder logic")
    ladderLogic.setExpectVal(2, 2.3, False, '4.3')
    await ladderLogic.runLadderLogic()

    await client.disconnect()
    serverThread.stop()

if __name__ == "__main__":
   asyncio.run(main())    
    
