#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        opcuaCommTest.py
#
# Purpose:     This module is the testcase program for the IEC62541 OPC-UA comm 
#              library <opcuaCommTest.py>, it will start a server in sub-thread and 
#              init client to test the data read and transmit.
#
# Author:      Yuancheng Liu
#
# Created:     2025/05/07
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import asyncio
import threading
import time
import opcuaComm

VAR_ID1 = 'variable01'
VAR_ID2 = 'variable02'
VAR_ID3 = 'variable03'


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

    def setExpectVal(self, val1, val2, val3):
        self.expectVal1 = val1
        self.expectVal2 = val2
        self.expectVal3 = val3

    def runLadderLogic(self):
        print("Test server value read functions in test ladder class.")
        val1 = self.parent.getVariableVal(VAR_ID1)
        showTestResult(self.expectVal1 , val1, "read point value1")

        val2 = self.parent.getVariableVal(VAR_ID2)
        showTestResult(self.expectVal2, val2, "read point value2")

        val3 = self.parent.getVariableVal(VAR_ID3)
        showTestResult(self.expectVal3, val3, "read point value3")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class opcuaServerThread(threading.Thread):
    """ OPC-UA server thread class for host the PLC or RTU data and provide to clients."""
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        serverName = 'TestPlc01'
        self.nameSpace = 'newNameSpace01'
        self.server = opcuaComm.opcuaServer(serverName, self.nameSpace)

    async def initServer(self):
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
        showTestResult(True, r3, "Add new float variable")

        return True 
    

    def run(self):
        data = asyncio.run(self.server.getVariableVal(VAR_ID1))
        print(VAR_ID1 + " = " +str(data))
        asyncio.run(self.server.runServer())

if __name__ == "__main__":
    server = opcuaServerThread('127.0.0.1', 4840)
    val = None 
    val = asyncio.run(server.initServer())
    print(">>>")
    print(val)
    server.start()