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
        """ Add a new namespace to the opcua server instance.
        """
        nameSpaceStr = str(nameSpace)
        if nameSpaceStr in self.nameSpaceDict.keys():
            return None
        idx = await self.server.register_namespace(nameSpaceStr)
        self.nameSpaceDict[nameSpaceStr] = idx

    def getEndPtUrl(self):
        return self.endPointURL
    
    def getNameSpaceIdx(self, nameSpace):
        if nameSpace in self.nameSpaceDict.keys():
            return self.nameSpaceDict[nameSpace]
        return None

    async def addObject(self, nameSpace, objName):
        """ Add a new object to the opcua server instance.
        """
        nameSpaceStr = str(nameSpace)
        objNameStr = str(objName)
        if nameSpaceStr not in self.nameSpaceDict.keys():
            return None
        idx = self.nameSpaceDict[nameSpaceStr]
        objects_node = self.server.get_objects_node()


        newObj  = await objects_node.add_object(idx, objNameStr)
        self.objectDict[objNameStr] = newObj
        return True

    async def addVariable(self, idx, objName, varName, intValue):
        """ Add a new variable to the opcua server instance.
        """
        objNameStr = str(objName)
        varNameStr = str(varName)
        if objNameStr not in self.objectDict.keys():
            return None
        newVar = await self.objectDict[objNameStr].add_variable(idx, varNameStr, intValue)
        await newVar.set_writable()
        return newVar

    async def updateVariable(self, varName, newValue):
        """ Update the variable value in the opcua server instance.
        """
        varNameStr = str(varName)
        if varNameStr not in self.variableDict.keys():
            return None
        await self.variableDict[varNameStr].write_value(newValue)
        return True

    async def runServer(self):
        """ Run the opcua server instance.
        """
        async with self.server:
            while not self.terminated:
                await asyncio.sleep(0.2)
                print("...")

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
        
    def connect(self):
        self.client.connect()

    def getVariableVal(self, namespace, objName, varName):
        """ Get the variable value from the opcua server instance.
        """
        nsidx = '0' #await self.client.get_namespace_index(namespace)
        var =  self.client.nodes.root.get_child("0:Objects/%s:%s/%s:%s" % (nsidx, objName, nsidx, varName))
        value =  var.read_value()
        return value

    def setVariableVal(self, namespace, objName, varName, value):
        """ Set the variable value to the opcua server instance.
        """
        nsidx =  self.client.get_namespace_index(namespace)
        var =  self.client.nodes.root.get_child("0:Objects/%s:%s/%s:%s" % (nsidx, objName, nsidx, varName))
        var.write_value(value)

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

