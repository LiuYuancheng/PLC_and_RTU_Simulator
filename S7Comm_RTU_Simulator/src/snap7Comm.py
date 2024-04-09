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
# Version:     v_0.1.3
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design:

    We want to create a Siemens S7comm communication channel (client + server) lib
    to read the data from a real PLC/RTU or simulate the PLC/RTU S7comm data handling 
    process (handle S7commm request from other program).

    Three components will be provided in this module:
    
    - ladder logic interface: An interface class hold the ladder logic calculation algorithm.
        The ladder logic obj class will inherit this interface class by overwritten the init() 
        and runLadderLogic() function by adding the memory info and the detail control.
        for example speed value save on memory Idx=0, dataIdx=0 and check whether the val more 
        than the threshold then write the result to memory Idx=0 dataIdx=2:
        1. Overwrite the initLadderInfo() to set the src and dest address info.
        2. Overwrite the runLadderLogic() to do the value check and memory udpate.
        3. Use or pass the ladder logic object in a handlerS7request() function.

    - S7CommClient: S7Comm client module to read src memory val or write target val 
        from/to the target PLC/RTU. 
        
    - S7CommServer: S7Comm  server module will be used by RTU/PLC module to handle the S7Comm
        data read/set request.
"""
import time
import ctypes
import snap7
from snap7.common import load_library

BOOL_TYPE = 0   # bool type 2 bytes data.
INT_TYPE = 1    # integer type 2 bytes number. 
REAL_TYPE = 2   # float type 4 bytes number. 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def parseS7bytes(databytes, dataIdx, dataType):
    """ Function to parse the s7snap read bytes data to get the relate value
        Args:
            databytes (bytes): bytes data
            dataIdx (int): data index in the 8 bytes.
            dataType (_type_): data type
        Returns:
            _type_: return the value or None if not specify the data type.
    """
    if dataType == BOOL_TYPE:
        return snap7.util.get_bool(databytes, int(dataIdx), 0)
    elif dataType == INT_TYPE:
        return snap7.util.get_int(databytes, int(dataIdx))
    elif dataType == REAL_TYPE:
        return snap7.util.get_real(databytes, int(dataIdx))
    else:
        return 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class rtuLadderLogic(object):
    """ The rtu data ladder logic object used by RTU server, details refer to 
        the < Program Design > part.
    """
    def __init__(self, parent, ladderName=None) -> None:
        """ Init example: testladderlogic = testLogic(None)
            Args:
                parent (s7commServer): the parent s7commServer object.
                ladderName (str, optional): logic name string. Defaults to None.
        """
        self.parent = parent
        self.ladderName = ladderName
        self.srcAddrValInfo = {'addressIdx': None, 'dataIdx': None}
        self.destAddrValInfo = {'addressIdx': None, 'dataIdx': None}
        self.initLadderInfo()

    def initLadderInfo(self):
        """ Init thesrc and dest address information, this function will 
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
    def runLadderLogic(self, inputData=None):
        """ Pass in the inputData, then run the ladder logic to calculate the 
            dest address data.
        """
        return []

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class s7CommClient(object):
    """ The S7Comm client used to import in the OT lvl2/3 application such as 
        HMI or remote display console to communicate with the PLC/RTU which use 
        the S7comm protocol.
    """

    def __init__(self, rtuIp, rtuPort=102, snapLibPath=None) -> None:
        """ init example: client = snap7Comm.s7CommClient('192.168.0.101', rtuPort=102, snapLibPath='snap7.dll')
            Args:
                rtuIp (str): target RTU/PLC ip address.
                rtuPort (int, optional): S7Comm port. Defaults to 102.
                snapLibPath (str, optional): For windows OS, need input the dll file, 
                    pass in the dll path in the client. Defaults to None.
        """
        self._rtuIp = rtuIp
        self._rtuPort = rtuPort
        self._libPath = snapLibPath
        self.client = snap7.client.Client() if snapLibPath is None else snap7.client.Client(lib_location=snapLibPath)
        self.connected = False
        try:
            self.client.connect(self._rtuIp, 0, 0, self._rtuPort)
            self.connected = self.client.get_connected()
        except Exception as err:
            print("s7CommClient init Error: %s" % err)
            return None

    #-----------------------------------------------------------------------------
    def checkConn(self):
        return self.connected

    #-----------------------------------------------------------------------------
    def readAddressVal(self, addressIdx, dataIdxList=None, dataTypeList=None):
        """ Read the data value/bytes from the RTU memory address.
            Args:
                addressIdx (int): memory address index.
                dataIdxList (list(int)): data index list
                dataTypeList (list(XX_TYPE), optional): data type list. Defaults to None.

            Returns:
                list(data): return the byte orignal data if the input dataIdxList is None 
                    else a list of the data. 
        """
        data = None 
        try:
            data = self.client.db_read(addressIdx, 0, 8)
            self.connected = True
        except Exception as err:
            print("Error: readAddressVal()> read RTU data error: %s" %str(err))
            self.connected = False
            return None
        # return the byte orignal data if the input dataIdxList is None 
        if dataIdxList is None or dataTypeList is None:
            return data
        dataList = [parseS7bytes(data, dataIdx, dataType)
         for dataIdx, dataType in zip(dataIdxList, dataTypeList)]
        return dataList

    #-----------------------------------------------------------------------------
    def setAddressVal(self, addressIdx, dataIdx, data, dataType=REAL_TYPE):
        """ Set the data Idx value in the address
            Args:
                addressIdx (int): memory address index.
                dataIdx (int):  data index.
                data (_type_): data value
                dataType (_type_, optional): data type. Defaults to REAL_TYPE.
            Returns:
                _type_: return snap7.db_write() result if set successfully else None.
        """
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
        Remark: The server need to run under 64bit version python3. Otherwise 
        there will be an OSError: exception: access violation reading 0x00000001
    """

    def __init__(self, hostIp='0.0.0.0', hostPort=102, snapLibPath=None) -> None:
        """ Init example: server = snap7Comm.s7commServer(snapLibPath='snap7.dll')
            Args:
                hostIp (str, optional): service host. Defaults to '0.0.0.0'.
                hostPort (int, optional): service port. Defaults to 102.
                snapLibPath (_type_, optional): libflie 'snap7.dll' path for Win-OS if 
                    the system path is not set. Defaults to None use system path.
        """ 
        self._hostIp = hostIp
        self._hostPort = hostPort
        self._server = None
        self._dbDict = {}  # data base dictionary
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
        self.clockInterval = 0.05 # the interval of the event handling clock 
        self.terminate = False
        print("s7commServerInit > Host IP: %s, Port: %d" %(self._hostIp, self._hostPort))

    #-----------------------------------------------------------------------------
    def initNewMemoryAddr(self, memoryIdx, dataIdxList, dataTypeList):
        """ Init a new memory 8 bytes address with the data info. All the init must 
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
                print("Warning: initNewMemoryAddr()> memory address %s already exist" %str(memoryIdx))
                return False 
            else:
                self._dbDict[str(memoryIdx)] = {
                    'dbData': (ctypes.c_ubyte*8)(),
                    'dataIdx': dataIdxList,
                    'dataType': dataTypeList
                }
                return True
        else:
            print("Error: initNewMemoryAddr()> input memory index need to be a >=0 int type")
            return False

    #-----------------------------------------------------------------------------
    def initRegisterArea(self):
        """ Register the new added address index and the data base to the snap7 area DB."""
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
        """ Get the value saved in the memory address under byte index.
            Args:
                memoryIdx (int/str): memory address index.
                dataIdx (int): data index in the memory.
            return: Value saved in the memory, None if the memory is not set.
        """
        if str(memoryIdx) in self._dbDict.keys():
            byteData = self._dbDict[str(memoryIdx)]['dbData']
            typeIdx = self._dbDict[str(memoryIdx)]['dataIdx'].index(dataIdx)
            dataType = self._dbDict[str(memoryIdx)]['dataType'][int(typeIdx)]
            return parseS7bytes(byteData, dataIdx, dataType)
        return None 

    #-----------------------------------------------------------------------------
    def startService(self, eventHandlerFun=None, printEvt=True):
        """ Start the S7comm service
            Args:
                eventHandlerFun ( function reference, optional): reference of the 
                    function used to handle the event. Defaults to None.
                printEvt (bool, optional): flag to identify whether print the event. Defaults to True.
        """
        print("Start the S7comm event handling loop.")
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
                        eventHandlerFun((address, dataIdx, writeLen))
            time.sleep(self.clockInterval)

    #-----------------------------------------------------------------------------
    def setClockInterval(self, interval):
        self.clockInterval = interval

    #-----------------------------------------------------------------------------
    def setMemoryVal(self, memoryIdx, dataIdx, dataVal):
        """ Set the memory index byte index value.
            Args:
                memoryIdx (int): memory index.
                dataIdx (int): byte index.
                dataVal (_type_): data value
        """
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
    def stopServer(self):
        self.runingFlg = False
        self.terminate = True
        self._server.stop()
        self._server.destroy()
    
