#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:         S71200PlcClient.py
#
# Purpose:      This module is used to connect to the Siemens S7-1200 PLC to read 
#               data from memory to get the input state of a PLC contact or write 
#               data to a memory address then change the output state of a PLC coil.
#
# Author:      Yuancheng Liu
#
# Created:     2024/06/26
# Version:     v0.1.3
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
"""
    Design purpose:
    To connect to an S7-1200 PLC, we can use the Siemens WinCC SDK to communicate 
    with the physical PLC. This python lib module aims to create a Python module that 
    can be integrated into your application to read and write data from the PLC.
    
    S7-1200 support mapping memory area directly to read and write data on PLC contact, 
    memory and coils. We use the snap7 library to communicate with the PLC via Siemens
    S7Comm protocol. The PLC ladder logic can be configure directly as: 
        | ix.x/mx.x | --> | Your Ladder Logic | --> | qx.x/mx.x |

    Protocol type: S7Comm
        
    Returns:
        1. This lib follow the design in this article: 
            http://simplyautomationized.blogspot.com/2014/12/raspberry-pi-getting-data-from-s7-1200.html
        2. Python snap7 lib: https://pypi.org/project/python-snap7/
"""

import time
import threading
import snap7
import snap7.util
from pythonping import ping

# PLC port
PLC_PORT = 102
# default memory start Index on S7-1200
MEM_AREA_IDX = {
    'i': 0x81,
    'q': 0x82, 
    'm': 0x83 
}

# Set the output type tag
BOOL_TYPE   = 1
INT_TYPE    = 2
REAL_TYPE   = 3
WORD_TYPE   = 4
DWORD_TYPE  = 5

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class S71200Reader(threading.Thread):
    """ A thread based PLC reader to read the PLC state regularly based on the 
        user configured memory list and read interval.
    """
    def __init__(self, parent, threadID, plcClient, memoryList=None, readIntv=3):
        """ Init Example: 
            plcReader = S71200Reader(None, 1, S71200Client('127.0.0.1', debug=True), 
                                    memoryList=['qx0.1', 'qx0.2'])
            Args:
                parent (ref): parent obj ref.
                threadID (int): Thread ID. 
                plcClient (ref): a <S71200Client> obj ref.
                memoryList (list(str), optional): memory tag list. Defaults to None.
                readIntv (int, optional): read time interval (sec). Defaults to 3.
        """
        super().__init__(parent)
        self.parent = parent
        self.threadID = threadID
        self.S71200PlcClient = plcClient
        self.readIntv = readIntv
        self.memoryList = memoryList
        self.memData = {'time': time.time(), 'data': []}
        self.terminate = False

    #-----------------------------------------------------------------------------
    def run(self):
        print("M71200Reader: Start to read data from PLC [%s]" %str(self.S71200PlcClient.getPLCInfo()))
        while not self.terminate:
            if self.S71200PlcClient and self.S71200PlcClient.getConnectionState():
                dataList = []
                self.memData['time'] = time.time()
                for mem in self.memoryList:
                    data = self.S71200PlcClient.readMem(mem)
                    dataList.append(data)
                self.memData['data'] = dataList
            else:
                self.S71200PlcClient.reconnect()
            time.sleep(self.readIntv)

    #-----------------------------------------------------------------------------
    def getLastData(self):
        return self.memData

    def stop(self):
        self.terminate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class S71200Client(object):
    """ Client to connect to the M221 PLC to read the memory data"""
    def __init__(self, plcIp, plcPort=PLC_PORT, pingPlc=True, debug=False):
        """ Init Example: client = S71200Client('127.0.0.1', debug=True)
            Args:
                plcIp (str): PLC IP address.
                plcPort (int, optional): PLC port. Defaults to PLC_PORT.
                pingPlc (bool, optional): flg to identify whether ping PLC before
                    establish connection. Defaults to True.
                debug (bool, optional): debug print flag. Defaults to False.
            Returns:
                Ref: return None if connection failed.
        """
        self.ip = plcIp
        self.port = plcPort
        self.debug = debug
        self.connected = False
        # Check whether the PLC is reachable
        if pingPlc and not self._pingPLC(self.ip): 
            print("Warning: The PLC [%s] is not reachable. Please check the connection." % self.ip)
            return None
        self.plcAgent = snap7.client.Client()        
        try:
            self.plcAgent.connect(self.ip, 0, 1, self.port)
            if self.debug: print("S71200Client: Connected to the PLC [%s]" % self.ip)
            self.connected = True 
        except Exception as err:
            print("Error: S71200Client init Error: %s" % err)
            return None

#-----------------------------------------------------------------------------
    def _pingPLC(self, host):
        """ Returns True if host (str) responds to a ping request. Remember that a host 
            may not respond to a ping (ICMP) request even if the host name is valid.
        """
        data = ping(host, timeout=2, verbose=False)
        if data.rtt_avg_ms >= 1000:
            # PLC more than 1000ms response, time out.
            print("S71200Client: PLC [%s] is not responding." % host)
            return False
        return True

    #-----------------------------------------------------------------------------
    def _memByte2Value(self, mbyte, valType, startMIdx, bitIndex):
        """ Convert the memory byte to the value of the specified type.
            Args:
                mbyte (bytes): data bytes. 
                valType (int): convert value's data type.
                startMIdx (int): start index of the memory byte.
                bitIndex (_type_): start index of the memory bit.
            Returns:
                _type_: _description_
        """
        data = None
        if valType == BOOL_TYPE:
            data = snap7.util.get_bool(mbyte, 0, bitIndex)
        elif valType == INT_TYPE:
            data = snap7.util.get_int(mbyte, startMIdx)
        elif valType == REAL_TYPE:
            data = snap7.util.get_real(mbyte, 0)
        elif valType == WORD_TYPE:
            data = snap7.util.get_word(mbyte, startMIdx)
        elif valType == DWORD_TYPE:
            data = snap7.util.get_dword(mbyte, 0)
        else:
            print("Error: _getMemValue()> input type invalid: %s" % str(valType))
        return data

#-----------------------------------------------------------------------------
# Define all the get() methods for the S71200 PLC.
    def getPLCInfo(self):
        return {'ip': self.ip, 'port': self.port, 'connected': self.connected}

    def getConnectionState(self):
        """ Returns the connection state of the PLC."""
        return self.connected

#-----------------------------------------------------------------------------
    def readMem(self, memAddrTag, returnByte=False):
        """ Fetch the current PLC state from related memory address: IX0.N-input contact, 
            QX0.N-output coil, MX0.N-memory address tag

            Args:
                memAddrTag (_type_): S71200 memory tag such as "qx0.6"
                returnByte (bool, optional): flag to identify whether return the raw memory 
                    bytes data or converted data. Defaults to False.
            Returns:
                _type_: raw memory bytes data if returnByte flag set to True or converted data
        """
        if not self.connected: return None
        memType = str(memAddrTag[0]).lower()
        if not memType in MEM_AREA_IDX.keys():
            print("Error: readMem()> input memory tag invalid: %s" %str(memAddrTag))
        valLength = 1   # value byte length
        valType = None  # value type
        bitIndex = 0    # start index of the memory byte.
        startMIdx = 0   # start index of the memory bit.
        if(memAddrTag[1].lower() == 'x'):
            # Config the bool type data tag 
            valLength = 1
            valType = BOOL_TYPE
            startMIdx = int(memAddrTag.split('.')[0][2:])
            bitIndex = int(memAddrTag.split('.')[1])
        elif(memAddrTag[1].lower() == 'b'):
            # Config the byte or integer type data tag
            valLength = 1
            valType = INT_TYPE
            startMIdx = int(memAddrTag[2:])
        elif(memAddrTag[1].lower() == 'w'):
            # Config the word type data tag
            valLength = 2
            valType = WORD_TYPE
            startMIdx = int(memAddrTag[2:])
        elif(memAddrTag[1].lower() == 'd'):  # double
            valLength = 4
            valType = DWORD_TYPE
            startMIdx = int(memAddrTag.split('.')[0][2:])
        elif('freal' in memAddrTag.lower()): # float real number
            valLength = 4
            valType = REAL_TYPE
            startMIdx = int(memAddrTag.lower().replace('freal', ''))
        else:
            print("Error: readMem()> input memory tag invalid: %s" %str(memAddrTag))
            return None
        # Init the memory start area.
        memoryArea = MEM_AREA_IDX[memType]
        try: 
            mbyte = self.plcAgent.read_area(memoryArea, 0, startMIdx, valLength)
            if self.debug:
                print("S7PLC1200 readMem() get data set[mem[0], start, length, bit, mbyte]:" % str(
                    memAddrTag[0].lower(), startMIdx, valLength, bitIndex, str(mbyte)))
            self.connected = True 
            return mbyte if returnByte else self._memByte2Value(mbyte, valType, startMIdx, bitIndex)
        except Exception as e:
            print("Error: readMem()> data read error: %s" %str(e))
            self.connected = False
            return None

#-----------------------------------------------------------------------------
    def writeMem(self, memAddrTag, val):
        """ Write a value to the related memory address: IX0.N-input contact, 
            QX0.N-output coil, MX0.N-memory address tag
            Args:
                memAddrTag (_type_): S71200 memory tag such as "qx0.6"
                val (_type_): _description_
        """
        if not self.connected: return None
        # get the memory data byte
        data = self.readMem(memAddrTag, returnByte=True)
        memType = str(memAddrTag[0]).lower()
        if not memType in MEM_AREA_IDX.keys():
            print("Error: writeMem()> input memory tag invalid: %s" %str(memAddrTag))
        startMIdx = bitIndex = 0  # start position idx
        if(memAddrTag[1].lower() == 'x'):
            # Set bool value 
            startMIdx =  int(memAddrTag.split('.')[0][2:])
            bitIndex = int(memAddrTag.split('.')[1])
            snap7.util.set_bool(data, 0, bitIndex, int(val))
        elif(memAddrTag[1].lower() == 'b'):  # byte
            startMIdx = int(memAddrTag[2:])
            snap7.util.set_int(data, 0, val)
        elif(memAddrTag[1].lower() == 'd'):
            startMIdx = int(memAddrTag.split('.')[0][2:])
            snap7.util.set_dword(data, 0, val)
        elif('freal' in memAddrTag.lower()):
            startMIdx = int(memAddrTag.lower().replace('freal', ''))
            snap7.util.set_real(data, 0, val)
        else: 
            print("Error: writeMem()> input type invalid: %s" %str(memAddrTag))
            return None 
        try:
            memoryArea = MEM_AREA_IDX[memType]
            rst = self.plcAgent.write_area(memoryArea, 0, startMIdx, data)
            self.connected = True
            return rst 
        except Exception as err:
            print("PLC write error: %s " %str(err))
            return None

#-----------------------------------------------------------------------------
    def reconnect(self):
        """ Reconnect to the PLC and set the PLC connection flag."""
        if self.getConnectionState(): self.disconnect()
        try:
            self.plcAgent.connect(self.ip, 0, 1, self.port)
            self.connected = self.plcAgent.get_connected()
        except Exception as err:
            print("S71200Client init Error: %s" % err)
            return None

#-----------------------------------------------------------------------------
    def disconnect(self):
        """ Disconnect from PLC."""
        print("S71200Client: Disconnect from PLC [%s]." %str(self.ip))
        self.connected = False
        if self.plcAgent: self.plcAgent.disconnect()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def testCase(mode):
    if mode == 0:
        print("Test case 1: local connection read memory test.")
        plc = S71200Client('127.0.0.1', debug=True)
        for x in range(0, 7):
            data = plc.readMem('qx0.'+str(x))
            print(data)
            time.sleep(0.5)
        plc.disconnect()
    elif mode == 1:
        print("Test case 2: local connection write memory test.")
        plc = S71200Client('127.0.0.1', debug=True)
        for x in range(0, 7):
            data = plc.writeMem('qx0.'+str(x), 1)
            print(data)
            time.sleep(0.5)
        plc.disconnect()
    elif mode == 2:
        print("Test case 3: local connection test with reader thread.")
        plc = S71200Client('127.0.0.1', debug=True)
        readMemList = ['qx0.1', 'qx0.2', 'mx0.3', 'mx0.4', 'ix0.5', 'ix0.6']
        plcReader = S71200Reader(None, 1, plc, memoryList=readMemList)
        plcReader.start()
        time.sleep(3)
        print(plcReader.getLastData())
        time.sleep(3)
        print(plcReader.getLastData())
        plcReader.stop()
    else:
        # Add more test case here and use <mode> flag to select.
        pass

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testMode = int(input("Please enter the test mode [0-2]: "))
    testCase(testMode)
