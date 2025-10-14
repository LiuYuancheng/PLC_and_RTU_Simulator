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
from asyncua.common.methods import uamethod

# OPCUA-TCP: opc.tcp://localhost:4840/UADiscovery
# OPCUA-Websockets: opc.wss://localhost:443/UADiscovery
# OPCUA-HTTPS: https://localhost:443/UADiscovery
# https://github.com/FreeOpcUa/opcua-asyncio/blob/master/examples/client-minimal.py

OPCUA_DEF_PORT = 4840

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class opcuaServer(object):
    """ OPCUA server class, it will create a opcua server instance and 
        register the opcua node tree.
        https://github.com/FreeOpcUa/opcua-asyncio/blob/master/examples/server-minimal.py
    """
    def __init__(self, serverName, nameSpace, port=OPCUA_DEF_PORT):
        self.serverName = str(serverName)
        self.serverPort = int(port)
        self.nameSpaceDict = {str(nameSpace):0}
        self.server = Server()
        self.endPointURL = "opc.tcp://0.0.0.0:%s/%s/server/" %(str(self.serverPort), self.serverName)
        self._initServer()
        
    async def _initServer(self):
        """ Init the opcua server instance and register the opcua node tree.
        """
        await self.server.init()
        self.server.set_endpoint(self.endPointURL)
        nameSpaceStr = str(self.nameSpaceDict.keys()[0])
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



import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod


@uamethod
def func(parent, value):
    return value * 2


async def main():
    _logger = logging.getLogger(__name__)
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("")

    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    myobj = await server.nodes.objects.add_object(idx, "MyObject")
    myvar = await myobj.add_variable(idx, "MyVariable", 6.7)
    # Set MyVariable to be writable by clients
    await myvar.set_writable()
    await server.nodes.objects.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("ServerMethod", idx),
        func,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )
    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(1)
            new_val = await myvar.get_value() + 0.1
            _logger.info("Set value of %s to %.1f", myvar, new_val)
            await myvar.write_value(new_val)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)

