#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        snap7Comm.py
#
# Purpose:     This module will provide a packaged Siemens S7Comm client and server 
#              communication API for testing or simulating the data connection 
#              flow between PLC/RTU and SCADA system. The module is implemented 
#              based on python-snapy lib module: 
#              - Reference: https://github.com/gijzelaerr/python-snap7
#
# Author:      Yuancheng Liu
#
# Created:     2024/03/21
# Version:     v_0.1.2
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design:

    We want to create a Siemens S7comm communication channel (client + server) lib
    to read the data from a real PLC/RTU or simulate the PLC/RTU S7comm data handling 
    process (handle S7commm request from other program).

    Four modules will be provided in this module: 

"""
import time
import ctypes
import snap7
from snap7.common import load_library

BOOL_TYPE = 0   # bool type 2 bytes data 
INT_TYPE = 1    # integer type 2 bytes data 
REAL_TYPE = 2   # float type 4 bytes number. 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class ladderLogic(object):
    """ The ladder logic object used by data handler, details refer to the < Program 
        Design > part.
    """

    def __init__(self, parent, ladderName=None) -> None:
        """ Init example: testladderlogic = testLogic(None)"""
        self.parent = parent
        self.ladderName= ladderName
        self.srcAddrValInfo = {'addressIdx': None, 'dataIdx': None}
        self.destAddrValInfo = {'addressIdx': None, 'dataIdx': None}
        self.initLadderInfo()

    def initLadderInfo(self):
        """ Init the ladder register, src and dest coils information, this function will 
            be called during the logic init. Please over write this function.
        """
        pass

#-----------------------------------------------------------------------------
# Define all the get() functions here:

    def getLadderName(self):
        return self.ladderName

    def getSrcAddrValInfo(self):
        return self.srcAddrValInfo

    def getDestAddrValInfo(self):
        return self.destAddrValInfo

#-----------------------------------------------------------------------------
    def runLadderLogic(self, regsList, coilList=None):
        """ Pass in the registers state list, source coils state list and 
            calculate output destination coils state, this function will be called by 
            plcDataHandler.updateState() function.
            - Please over write this function.
        """
        return []

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
    def checkConn(self):
        return self.connected

    #-----------------------------------------------------------------------------
    def readAddressVal(self, addressIdx, dataIdx, dataType=None):
        data = None 
        try:
            data = self.client.db_read(addressIdx, 0, 8)
            self.connected = True
        except Exception as err:
            print("Error: readAddressVal()> read RTU data error: %s" %str(err))
            self.connected = False
            return None 
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
        try: 
            rst = self.client.db_write(addressIdx, dataIdx, command)
            self.connected = True
            return rst
        except Exception as err:
            print("Error: setAddressVal()> set RTU data error: %s" %str(err))
            self.connected = False
            return None 

    #-----------------------------------------------------------------------------
    def close(self):
        self.connected = False 
        self.client.disconnect()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class s7commServer(object):
    """ multi thread s7comm server, used by PLC/RTU to handle the data read/set 
        request.
        Remark: The server need to run under 64bit version python. Otherwise 
        there will be an OSError: exception: access violation reading 0x00000001
    """

    def __init__(self, hostIp='0.0.0.0', hostPort=102, snapLibPath=None) -> None:
        """ Init the s7 server

            Args:
                hostIp (str, optional): service host. Defaults to '0.0.0.0'.
                hostPort (int, optional): service port. Defaults to 102.
                snapLibPath (_type_, optional): libflie 'snap7.dll' path for Win-OS if 
                    the system path is not set. Defaults to None use system path.
        """ 
        self._hostIp = hostIp
        self._hostPort = hostPort
        self._server = None
        self._dbDict = {}
        # Example of data base with one address save one bool, one int and one float number:
        # self._dbDict = {
        #     '1': {    # address index as the key.
        #         'dbData':(ctypes.c_ubyte*8)(), # 8 byte data 
        #         'dataIdx':[0, 2, 4], # paramter start index of bytes. 
        #         'dataType':[BOOL_TYPE, INT_TYPE, REAL_TYPE], # paramter type
        #     }    
        # }
        self.runingFlg = False
        self._server = snap7.server.Server()
        if snapLibPath:
            print("s7commServer > Load the Snap7 Win-OS lib-dll file : %s" %str(snapLibPath))
            load_library(snapLibPath)
        self.clockInterval = 0.05
        self.terminate = False
        print("s7commServerInit > Host IP: %s, Port: %d" %(self._hostIp, self._hostPort))

    #-----------------------------------------------------------------------------
    def initNewMemoryAddr(self, memoryIdx, dataIdxList, dataTypeList):
        """ Init a new memeory 8 bytes address with the data info. All the init must 
            be called before the server start. 
            Args:
                memoryIdx (int): the memory index 
                dataIdxList (list[int]): list of data index
                dataTypeList (list[XXX_TYPE]): list of data type matches to the data index

            Returns:
                Bool: True if added success, else False.
        """
        if isinstance(memoryIdx, int) and memoryIdx >= 0:
            if str(memoryIdx) in self._dbDict.keys():
                print("Error: initNewMemoryAddr()> memory address %s already exist" %str(memoryIdx))
                return None 
            else:
                self._dbDict[str(memoryIdx)] = {
                    'dbData':(ctypes.c_ubyte*8)(),
                    'dataIdx':dataIdxList,
                    'dataType':dataTypeList
                }
                return True
        else:
            print("Error: initNewMemoryAddr()> input memory index need to be a >=0 int type")
            return None

    #-----------------------------------------------------------------------------
    def initRegisterArea(self):
        """ Register the address index and the data base to the snap7 area DB."""
        for addressIdxStr in self._dbDict.keys():
            addressIdx = int(addressIdxStr)
            self._server.register_area(snap7.types.srvAreaDB, 
                                       addressIdx, 
                                       self._dbDict[addressIdxStr]['dbData'])

    #-----------------------------------------------------------------------------
    def isRunning(self):
        return self.runingFlg

    def getDBDict(self):
        return self._dbDict

    def getEvent(self):
        return self._server.pick_event()

    def getMemoryVal(self, memoryIdx, dataIdx):
        """ Get the value saved in the memory address.
            Args:
                memoryIdx (int): memory address index.
                dataIdx (int): data index in the memory.
            return: value saved in the memory.
        """
        if str(memoryIdx) in self._dbDict.keys():
            typeIdx = self._dbDict[str(memoryIdx)]['dataIdx'].index(dataIdx)
            dataType = self._dbDict[str(memoryIdx)]['dataType'][int(typeIdx)]
            if dataType == BOOL_TYPE:
                return snap7.util.get_bool(self._dbDict[str(memoryIdx)]['dbData'], int(dataIdx), 0)
            elif dataType == INT_TYPE:
                return snap7.util.get_int(self._dbDict[str(memoryIdx)]['dbData'], int(dataIdx))
            elif dataType == REAL_TYPE:
                return snap7.util.get_real(self._dbDict[str(memoryIdx)]['dbData'], int(dataIdx))
        return None 

    #-----------------------------------------------------------------------------
    def startService(self, eventHandlerFun=None, printEvt=True):
        try:
            self.initRegisterArea()
            self._server.start(self._hostPort)
            self.runingFlg = True
        except Exception as err:
             print("Error: startService() Error to start s7snap server: %s" %str(err))
             self.runingFlg = False 
             return None
        # Added the loop to print the event and handle the DB change request.
        while not self.terminate:
            event = self._server.pick_event()
            if event:
                if printEvt: print(" - Event: %s" % str(event))
                if eventHandlerFun and event.EvtCode == 262144 and event.EvtRetCode == 0:  # write command executed
                    if event.EvtParam1 == 132:  # DB write
                        address, dataIdx, writeLen = event.EvtParam2, event.EvtParam3, event.EvtParam4
                        parmList = (address, dataIdx, writeLen)
                        eventHandlerFun(parmList)
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
        self.runingFlg = False
        self.terminate = True
        self._server.stop()
        self._server.destroy()
    
