#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        opcuaComm.py
#
# Purpose:     This module will provide the IEC62541 OPC-UA TCP client and server 
#              communication API to test or simulate the data/cmd flow connection 
#              between PLC/RTU and other SCADA device in the OT system. The module 
#              is implemented based on python opcua-asyncio lib module: 
#              - Reference: https://github.com/FreeOpcUa/opcua-asyncio
#
# Author:      Yuancheng Liu
#
# Created:     2025/11/28
# Version:     v_0.0.4
# Copyright:   Copyright (c) 2025 Liu Yuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design:

    We want to create a simple IEC-62541 channel (client + server) library module 
    to simulate the data communication to PLC or RTU via opc-ua-tcp. For the server 
    data storage 4 types of point data are provided:
    
    1.  Unified Architecture bool 
    2.  Unified Architecture int16
    3.  Unified Architecture float
    4.  Unified Architecture string

    The structure of the data storage is as follows:
    Server Name
        |
        DataStorage-> Namespace
                        |__ Object
                                |__ Variable = value

    OPCUA-TCP: opc.tcp://localhost:4840/UADiscovery
    OPCUA-Websockets: opc.wss://localhost:443/UADiscovery
    OPCUA-HTTPS: https://localhost:443/UADiscovery
    https://github.com/FreeOpcUa/opcua-asyncio/blob/master/examples/client-minimal.py

"""

import asyncio
from asyncua import Client
from asyncua import Server, ua

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

    #-----------------------------------------------------------------------------
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
        """ Asynchronous ladder logic algo execution function. This function need to be 
            overwritten.
        """ 
        return None 
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class opcuaServer(object):
    """ OPC-UA-TCP server class, it will create a opc-ua server instance and register 
        the opcua nodes tree.
    """
    def __init__(self, serverName, nameSpace, port=OPCUA_DEF_PORT):
        """ Init example: server = opcuaComm.opcuaServer(SERVER_NAME, NAME_SPACE)
            Args:
                serverName (str): serverName
                nameSpace (str): name space name 
                port (int, optional): port number . Defaults to OPCUA_DEF_PORT 4804.
        """
        self.serverName = str(serverName)
        self.serverPort = int(port)
        # Name space dict, key: name space name, value: name space index
        self.nameSpaceDict = {str(nameSpace):0}
        # Node Object dict, key: object name, value: object node obj
        self.objectDict = {}
        # Variable dict, key: variable name, value: variable obj
        self.variableDict = {}
        self.endPointURL = "opc.tcp://0.0.0.0:%s/%s/server/" %(str(self.serverPort), self.serverName)
        self.server = Server()
        self.terminated = False

    #-----------------------------------------------------------------------------   
    async def initServer(self):
        """ Init the opcua server instance and register the name space."""
        await self.server.init()
        self.server.set_endpoint(self.endPointURL)
        nameSpaceStr = list(self.nameSpaceDict.keys())[0]
        idx = await self.server.register_namespace(nameSpaceStr)
        self.nameSpaceDict[nameSpaceStr] = idx
        print("OPC-UA Server %s initialized, name space %s, index %s" %(self.serverName, nameSpaceStr, str(idx)))

    #-----------------------------------------------------------------------------
    async def addNameSpace(self, nameSpace):
        """ Add a new namespace to the opcua server instance."""
        nameSpaceStr = str(nameSpace)
        if nameSpaceStr in self.nameSpaceDict.keys():
            print("Warning: addNameSpace() Namespace=%s already exists! Return False." %nameSpace)
            return False
        idx = await self.server.register_namespace(nameSpaceStr)
        self.nameSpaceDict[nameSpaceStr] = idx
        return True

    #-----------------------------------------------------------------------------
    async def addObject(self, nameSpace, objName):
        """ Add a new object under a specific name space to the opcua server instance."""
        nameSpaceStr = str(nameSpace)
        objNameStr = str(objName)
        if nameSpaceStr not in self.nameSpaceDict.keys():
            print("Warning: addObject() Target Namespace=%s not exists! Return False." %nameSpace)
            return False
        idx = self.nameSpaceDict[nameSpaceStr]
        if objNameStr in self.objectDict.keys():
            print("Warning: addObject() Target Object=%s already exists! Return False." %objName)
            return False
        objects_node = self.server.get_objects_node()
        newObj  = await objects_node.add_object(idx, objNameStr)
        self.objectDict[objNameStr] = newObj
        return True

    #-----------------------------------------------------------------------------
    async def addVariable(self, idx, objName, varName, intValue):
        """ Add a new variable under a specific object to the opcua server instance."""
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

    #-----------------------------------------------------------------------------
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

    #-----------------------------------------------------------------------------
    async def updateVariable(self, varName, newValue):
        """ Update the specific variable value in the opcua server instance based on 
            the variable ID/Name.
        """
        varNameStr = str(varName)
        if varNameStr not in self.variableDict.keys():
            return None
        await self.variableDict[varNameStr].write_value(newValue)
        return True

    #-----------------------------------------------------------------------------
    async def runServer(self, interval=0.1):
        """ Run the opcua server instance with a loop to handling the client requests.
            the loop will sleep a very shot interval to limit the request process speed.
        """
        async with self.server:
            while not self.terminated:
                await asyncio.sleep(interval)

    def stopServer(self):
        """ Stop the opcua server instance."""
        self.terminated = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class opcuaClient(object):
    """ OPCUA-TCP client class, it will connect to a opc-ua server to read and write
        the variables data.
    """
    def __init__(self, serverUrl, timeout=None, watchdog_interval=None):
        """ Init example: opcuaComm.opcuaClient("opc.tcp://localhost:4840/PLC_09/server/", 
                                    timeout=5, watchdog_interval=10)
            Args:
                serverUrl (str): OPC-UP Target server url.
                timeout (int, optional): Each request sent to the server expects an answer within this
                    time. The timeout is specified in seconds.Defaults to None (4 sec in asyncua.Client).
                watchdog_interval (int, optional): The time between checking if the server is still alive. 
                The timeout is specified in seconds. Defaults to None (1 sec in asyncua.Client).
        """
        self.serverUrl = str(serverUrl)
        self.client = None 
        if timeout is not None and watchdog_interval is not None:
            self.client = Client(self.serverUrl, timeout=int(timeout), watchdog_intervall=int(watchdog_interval))
        else:
            self.client = Client(self.serverUrl)

    #----------------------------------------------------------------------------- 
    async def connect(self):
        await self.client.connect()
        print("Client connected! Server OPCUA-TCP URL: %s" %self.serverUrl)

    async def disconnect(self):
        await self.client.disconnect()
        print("Client disconnected!")

    def getServerUrl(self):
        return self.serverUrl

    #----------------------------------------------------------------------------- 
    async def getVariableVal(self, namespace, objName, varName):
        """ Get the variable value from the opcua server instance."""
        root = self.client.get_root_node()
        var = await root.get_child(["0:Objects", "2:%s" % str(objName), "2:%s" % str(varName)])
        value =  await var.read_value()
        return value

    #----------------------------------------------------------------------------- 
    async def setVariableVal(self, namespace, objName, varName, value):
        """ Set the variable value to the opcua server instance."""
        root = self.client.get_root_node()
        var = await root.get_child(["0:Objects", "2:%s" % str(objName), "2:%s" % str(varName)])
        await var.write_value(value)

#----------------------------------------------------------------------------- 
#----------------------------------------------------------------------------- 
async def main():
    server = opcuaServer('testServer', 'newNameSpace01')
    await server.initServer()
    await server.addObject('newNameSpace01', 'newObject01')
    await server.addVariable(server.getNameSpaceIdx('newNameSpace01'), 'newObject01', 'newVariable01', 0.11)
    await server.runServer()

if __name__ == "__main__":
    asyncio.run(main())
