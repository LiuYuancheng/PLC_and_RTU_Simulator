#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        snap7Comm.py
#
# Purpose:     This module will provide the modbus-TCP client and server communication
#              API for testing or simulating the data flow connection between PLC and SCADA 
#              system. The module is implemented based on python pyModbus lib module: 
#              - Reference: https://github.com/sourceperl/pyModbusTCP
#
# Author:      Yuancheng Liu
#
# Created:     2023/06/11
# Version:     v_0.1.3
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design:
"""

import threading
import ctypes
import snap7
from snap7.common import load_library
import time

BOOL_TYPE = 0 # bool type 2 bytes data 
INT_TYPE = 1 # integer type 2 bytes data 
REAL_TYPE = 2 # float type 4 bytes number. 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class s7CommClient(object):

    def __init__(self, rtuIp, rtuPort=102, snapLibPath=None) -> None:
        self._rtuIp = rtuIp
        self._rtuPort = rtuPort
        self._libPath = snapLibPath
        if self._libPath is None:
            self.client = snap7.client.Client()
        else:
            self.client = snap7.client.Client(lib_location=self._libPath)
        
        self.client.connect(self._rtuIp, 0, 0, self._rtuPort)
        self.connected = self.client.get_connected()

    #-----------------------------------------------------------------------------
    def readAddressVal(self, addressIdx, dataIdx, dataType=None):
        data = self.client.db_read(addressIdx, 0, 8)
        if dataType == BOOL_TYPE:
            return snap7.util.get_bool(data, dataIdx, 0)
        elif dataType == INT_TYPE:
            return snap7.util.get_int(data, dataIdx)
        elif dataType == REAL_TYPE:
            return snap7.util.get_real(data, dataIdx)
        else:
            return data

    #-----------------------------------------------------------------------------
    def setAddressVal(self, addressIdx, dataIdx, data, dataType=None):
        command = bytearray(4) if dataType == REAL_TYPE else bytearray(2)
        if dataType == BOOL_TYPE:
            snap7.util.set_bool(command, 0, 0, bool(data))
        elif dataType == INT_TYPE:
            snap7.util.set_int(command, 0, int(data))
        else:
            snap7.util.set_real(command, 0, float(data))
        return self.client.db_write(addressIdx, dataIdx, command)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class s7commServer(object):
    """ The server need to run under 64bit version python. Otherwise there will
        be error: OSError: exception: access violation reading 0x00000001
        Args:
            object (_type_): _description_
    """

    def __init__(self, hostIp='0.0.0.0', hostPort=102, snapLibPath=None, dataHandler=None) -> None:
        self._hostIp = hostIp
        self._hostPort = hostPort
        self._server = None
        self._dbDict = {}
        # data base example
        # self._dbDict = {
        #     '1': {
        #         'dbData':(ctypes.c_ubyte*8)(),
        #         'dataIdx':[],
        #         'dataType':[],
        #     }    
        # }
        self.runingFlg = False
        self._server = snap7.server.Server()
        if snapLibPath:
            print("Set path")
            load_library(snapLibPath)
        self.clockInterval = 0.05
        self.terminate = False

    #-----------------------------------------------------------------------------
    def _initNewMemoryAddr(self, memoryIdx, dataIdxList, dataTypeList):
        """ Init a new memeory 8 bytes address."""
        if isinstance(memoryIdx, int) and memoryIdx >= 0:
            if str(memoryIdx) in self._dbDict.keys():
                print("Error: _initNewMemoryAddr()> memory address %s already exist" %str(memoryIdx))
                return None 
            else:
                self._dbDict[str(memoryIdx)] = {
                    'dbData':(ctypes.c_ubyte*8)(),
                    'dataIdx':dataIdxList,
                    'dataType':dataTypeList
                }
        else:
            print("Error: _initNewMemoryAddr()> input memory index need to be a >=0 int type")
            return None

    #-----------------------------------------------------------------------------
    def _initMemoryDB(self):
        pass 

    def _handlerS7request(self, address, dataIdx, writeLen):
        print("Three Paramters: %s" %str((address, dataIdx, writeLen)))

    #-----------------------------------------------------------------------------
    def initRegisterArea(self):
        """ register the address index and the data to the snap7 area DB."""
        for addressIdxStr in self._dbDict.keys():
            addressIdx = int(addressIdxStr)
            self._server.register_area(snap7.types.srvAreaDB, addressIdx, self._dbDict[addressIdxStr]['dbData'])

    def isRunning(self):
        return self.runingFlg

    def startService(self):
        #try:
        self.initRegisterArea()
        self._server.start(self._hostPort)
        self.runingFlg = True
        # except Exception as err:
        #     print("Error: startService() Error to start s7snap server: %s" %str(err))
        #     self.runingFlg = False 
        #     return None

        while not self.terminate:
            event = self._server.pick_event()
            if event:
                print("event: %s" %str(event))
                if event.EvtCode == 262144 and event.EvtRetCode == 0: # write command executed
                    if event.EvtParam1 == 132: # DB write
                        address = event.EvtParam2
                        dataIdx = event.EvtParam3
                        writeLen = event.EvtParam4
                        self._handlerS7request(address, dataIdx, writeLen)
            else:
                time.sleep(self.clockInterval)

    #-----------------------------------------------------------------------------
    def setMemoryVal(self, memoryIdx, dataIdx, dataVal):
        if str(memoryIdx) in self._dbDict.keys():
            if dataIdx in self._dbDict[str(memoryIdx)]['dataIdx']:
                typeIdx = self._dbDict[str(memoryIdx)]['dataIdx'].index(dataIdx)
                dataType = self._dbDict[str(memoryIdx)]['dataType'][int(typeIdx)]
                if dataType == BOOL_TYPE:
                    snap7.util.set_bool(self._dbDict[str(memoryIdx)]['dbData'], int(dataIdx), 0, bool(dataVal))
                elif dataType == INT_TYPE:
                    snap7.util.set_int(self._dbDict[str(memoryIdx)]['dbData'], int(dataIdx), int(dataVal))
                elif dataType == REAL_TYPE:
                    snap7.util.set_real(self._dbDict[str(memoryIdx)]['dbData'], int(dataIdx), float(dataVal))
                else:
                    print("Error: setMemoryVal()> invalid data type: %s" %str(dataType))
                    return False 
                return True
            else:
                print("Error: setMemoryVal()> invalid data index: %s" %str(dataIdx))
                return False
        print("Error: setMemoryVal()> invalid memory index: %s" %str(memoryIdx))
        return None 

    #-----------------------------------------------------------------------------
    def setClockInterval(self, interval):
        self.clockInterval = interval

    #-----------------------------------------------------------------------------
    def stopServer(self):
        self.terminate = True
        self._server.destroy()
    