#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        opcuaComm.py
#
# Purpose:     This module will provide the IEC62541 OPC-UA client and server 
#              communication API to test or simulate the data flow connection 
#              between PLC/RTU and SCADA system. The module is implemented based 
#              on python opcua-asyncio lib module: 
#              - Reference: https://github.com/FreeOpcUa/opcua-asyncio
#
# Author:      Yuancheng Liu
#
# Created:     2025/10/13
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2025 Liu Yuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time 
import asyncio
from asyncua import Server, ua
from asyncua import Client
from asyncua.common.methods import uamethod

# OPCUA-TCP: opc.tcp://localhost:4840/UADiscovery
# OPCUA-Websockets: opc.wss://localhost:443/UADiscovery
# OPCUA-HTTPS: https://localhost:443/UADiscovery
# https://github.com/FreeOpcUa/opcua-asyncio/blob/master/examples/client-minimal.py

OPCUA_DEF_PORT = 4840

UA_TYPE_BOOL = ua.VariantType.Boolean
UA_TYPE_INT16 = ua.VariantType.Int16
UA_TYPE_FLOAT = ua.VariantType.Float
UA_TYPE_STRING = ua.VariantType.String

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class ladderLogic(object):
    """ The PLC/RTU ladder logic class, this class will be inherited by your ladder diagram,
        and you need to implement initLadderInfo() and runLadderLogic() function.
    """
    def __init__(self, parent, ladderName='TestLadderDiagram'):
        """ To create a simple ladder example, please refer to file <testCase/iec104PlcServerTest.py>
            Args:
                parent (iec104Server): parent need to be a iec104 server obj
                ladderName (str, optional): _description_. Defaults to 'TestLadderDiagram'.
        """
        self.parent = parent # the parent need to be a iec104 server obj
        self.ladderName = ladderName
        self.srcVarIDList = []
        self.srcVarTypeList = []
        self.destVarIDList = []
        self.destVarTypeList = []
        self.initLadderInfo()

    def initLadderInfo(self):
        """ Init the ladder register, src and dest coils information, this function will 
            be called during the logic init. Please over write this function.
        """
        # This function need to be overwritten. 
        return None

    #-----------------------------------------------------------------------------
    # define all the get and set functions.
    def getLadderName(self):
        return self.ladderName
    
    def getSrcVarIDList(self):
        return self.srcPointAddrList

    def getSrcVarTypeList(self):
        return self.srcPointTypeList

    def getDestVarIDList(self):
        return self.destPointAddrList
    
    def getDestVarTypeList(self):
        return self.destPointTypeList
    
    #-----------------------------------------------------------------------------
    async def runLadderLogic(self):
        """ Read the measured point value and changeable step value from the parent IEC104 server, 
            and update the measured point value. 
        """
        # This function need to be overwritten. 
        return None 
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class opcuaServer(object):
    """ OPCUA server class, it will create a opc-ua server instance and 
        register the opcua node tree.
        https://github.com/FreeOpcUa/opcua-asyncio/blob/master/examples/server-minimal.py
    """
    def __init__(self, serverName, nameSpace, port=OPCUA_DEF_PORT):
        self.serverName = str(serverName)
        self.serverPort = int(port)
        self.nameSpaceDict = {str(nameSpace):0}
        self.objectDict = {}
        self.variableDict = {}
        self.server = Server()
        self.endPointURL = "opc.tcp://0.0.0.0:%s/%s/server/" %(str(self.serverPort), self.serverName)
        #self._initServer()
        self.terminated = False
        
    async def initServer(self):
        """ Init the opcua server instance and register the opcua node tree.
        """
        await self.server.init()
        self.server.set_endpoint(self.endPointURL)
        nameSpaceStr = list(self.nameSpaceDict.keys())[0]
        idx = await self.server.register_namespace(nameSpaceStr)
        self.nameSpaceDict[nameSpaceStr] = idx

    async def addNameSpace(self, nameSpace):
        """ Add a new namespace to the opcua server instance."""
        nameSpaceStr = str(nameSpace)
        if nameSpaceStr in self.nameSpaceDict.keys():
            print("Warning: addNameSpace() Namespace %s already exists!" %nameSpace)
            return False
        idx = await self.server.register_namespace(nameSpaceStr)
        self.nameSpaceDict[nameSpaceStr] = idx
        return True

    async def addObject(self, nameSpace, objName):
        """ Add a new object to the opcua server instance."""
        nameSpaceStr = str(nameSpace)
        objNameStr = str(objName)
        if nameSpaceStr not in self.nameSpaceDict.keys():
            print("Warning: addObject() Target Namespace %s not exists!" %nameSpace)
            return False
        idx = self.nameSpaceDict[nameSpaceStr]
        if objNameStr in self.objectDict.keys():
            print("Warning: addObject() Object %s already exists!" %objName)
            return False
        objects_node = self.server.get_objects_node()
        newObj  = await objects_node.add_object(idx, objNameStr)
        self.objectDict[objNameStr] = newObj
        return True

    async def addVariable(self, idx, objName, varName, intValue):
        """ Add a new variable to the opcua server instance."""
        objNameStr = str(objName)
        varNameStr = str(varName)
        if objNameStr not in self.objectDict.keys():
            print("Warning: addVariable() Target Object %s not exists!" %objName)
            return False
        if varNameStr in self.variableDict.keys():
            print("Warning: addVariable() Variable %s already exists!" %varName)
            return False
        newVar = await self.objectDict[objNameStr].add_variable(idx, varNameStr, intValue)
        await newVar.set_writable()
        self.variableDict[varNameStr] = newVar
        return True

    def getEndPtUrl(self):
        return self.endPointURL
    
    def getNameSpaceIdx(self, nameSpace):
        if nameSpace in self.nameSpaceDict.keys():
            return self.nameSpaceDict[nameSpace]
        return None

    async def getVariableVal(self, varName):
        varName = str(varName)
        if varName in self.variableDict.keys():
            return await self.variableDict[varName].get_value()
        print("Error: varName %s not found!" %varName)
        return None

    async def updateVariable(self, varName, newValue):
        """ Update the variable value in the opcua server instance.
        """
        varNameStr = str(varName)
        if varNameStr not in self.variableDict.keys():
            return None
        await self.variableDict[varNameStr].write_value(newValue)
        return True

    async def runServer(self, interval=0.2):
        """ Run the opcua server instance.
        """
        async with self.server:
            while not self.terminated:
                await asyncio.sleep(interval)
                #print("...")

    def stopServer(self):
        """ Stop the opcua server instance.
        """
        self.terminated = True


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class opcuaClient(object):
    """ OPCUA client class, it will connect to a opc-ua server instance and 
        register the opcua node tree.
        https://github.com/FreeOpcUa/opcua-asyncio/blob/master/examples/server-minimal.py
    """
    def __init__(self, serverUrl):
        self.serverUrl = str(serverUrl)
        self.client = Client(self.serverUrl)
        
    async def connect(self):
        await self.client.connect()
        print("Client connected!")

    async def disconnect(self):
        await self.client.disconnect()
        print("Client disconnected!")

    async def getVariableVal(self, namespace, objName, varName):
        """ Get the variable value from the opcua server instance.
        """
        root = self.client.get_root_node()
        var = await root.get_child(["0:Objects", "2:%s" % objName, "2:%s" % varName])
        value =  await var.read_value()
        return value

    async def setVariableVal(self, namespace, objName, varName, value):
        """ Set the variable value to the opcua server instance.
        """
        root = self.client.get_root_node()
        var = await root.get_child(["0:Objects", "2:%s" % objName, "2:%s" % varName])
        #value =  await var.read_value()
        await var.write_value(value)

async def main():
    server = opcuaServer('testServer', 'newNameSpace01')
    await server.initServer()
    await server.addObject('newNameSpace01', 'newObject01')
    await server.addVariable(server.getNameSpaceIdx('newNameSpace01'), 'newObject01', 'newVariable01', 0.11)
    await server.runServer()

if __name__ == "__main__":
    asyncio.run(main(), debug=True)


# import asyncio
# import logging

# from asyncua import Server, ua
# from asyncua.common.methods import uamethod


# @uamethod
# def func(parent, value):
#     return value * 2


# async def main():
#     _logger = logging.getLogger(__name__)
#     # setup our server
#     server = Server()
#     await server.init()
#     server.set_endpoint("")

#     # set up our own namespace, not really necessary but should as spec
#     uri = "http://examples.freeopcua.github.io"
#     idx = await server.register_namespace(uri)

#     # populating our address space
#     # server.nodes, contains links to very common nodes like objects and root
#     myobj = await server.nodes.objects.add_object(idx, "MyObject")
#     myvar = await myobj.add_variable(idx, "MyVariable", 6.7)
#     # Set MyVariable to be writable by clients
#     await myvar.set_writable()
#     await server.nodes.objects.add_method(
#         ua.NodeId("ServerMethod", idx),
#         ua.QualifiedName("ServerMethod", idx),
#         func,
#         [ua.VariantType.Int64],
#         [ua.VariantType.Int64],
#     )
#     _logger.info("Starting server!")
#     async with server:
#         while True:
#             await asyncio.sleep(1)
#             new_val = await myvar.get_value() + 0.1
#             _logger.info("Set value of %s to %.1f", myvar, new_val)
#             await myvar.write_value(new_val)


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG)
#     asyncio.run(main(), debug=True)

