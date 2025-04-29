#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        M221PlcCLient.py
#
# Purpose:     This module is used to connect to the Schneider M22x type PLC 
#              (physical device to read bits data from memory to get the input 
#              state of a PLC contact or write bit data in a memory address to
#              change the output state of a PLC coil. The related PLC setting 
#              link(function code):
#              1. https://www.schneider-electric.com/en/faqs/FA308725/
#              2. https://www.schneider-electric.com/en/faqs/FA295250/
#              3. https://www.schneider-electric.com/en/faqs/FA249614/
#               
# Author:      Yuancheng Liu
#
# Created:     2024/06/25
# Version:     v0.1.4
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" 
    Design purpose:
    To connect to an M221 PLC, we can use the Schneider SoMachine SDK to communicate 
    with the physical PLC. This python lib module aims to create a Python module that 
    can be integrated into your application to read and write data from the PLC.
        
    M221 supports normal ModBus TCP protocol communication, but if you don't use the 
    soMachine SDK, your program can not read the contact "I0.X" or write the coil "Q0.X" 
    directly.The solution is to link the contact "I0.X" or coil "Q0.X" to a PLC memory 
    address, then read or write the memory address to get the contact input or set the 
    coil output. The ladder logic can be draft as shown below:
        [ I0.x ] --> | M1.x | 
        | M1.x | --> | Your Ladder Logic | --> | M2.x |
        | M2.x | --> ( Q0.x )
    
    Protocol type: ModBus-TCP
    
    Reference: 
        - M221 User Manual: https://pneumatykanet.pl/pub/przekierowanie/Modicon-M221-Logic-Controller-Programming-Guide-EN.pdf
"""

import time
import socket
import threading

from platform import python_version
from pythonping import ping

# Check the python version, if < 3.6 use bytes.decode('hex') to decode the 
# PLC response data, else use bytes.hex() decode.
DECODE_MD = (float(python_version()[0:3]) < 3.6)

PLC_PORT = 502  # ModBus-TCP default TCP port.
BUFF_SZ = 1024  # TCP buffer size.

# M221 PLC memory address tag example list.
MEM_ADDR_TAG = {
    'M0':   '0000',
    'M1':   '0001',
    'M2':   '0002',
    'M3':   '0003',
    'M4':   '0004',
    'M5':   '0005',
    'M6':   '0006',
    'M10':  '000a',
    'M20':  '0014',
    'M30':  '001e',
    'M40':  '0028',
    'M50':  '0032',
    'M60':  '003c'
    }

# All the M221 Module bus constants we need: 
TID = '0000'            # Transaction Identifier (2bytes)
PROTOCOL_ID = '0000'    # Protocol Identifier (2bytes)
UID = '01'              # Unit Identifier (1byte)
BIT_COUNT = '0001'      # 
BYTE_COUNT = '01'       # 
W_LENGTH = '0008'       # write byte command unit length field  
R_LENGTH = '0006'       # read byte command unit length field
M_FC = '0f'             # memory access function code (write) multiple bit
M_RD = '01'             # memory state fetch internal multiple bits %M
VALUES = {'0': '00', '1': '01'} # state to hex number

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class M221Reader(threading.Thread):
    """ A thread based PLC reader to read the PLC state regularly based on the 
        user configured memory list and read interval.
    """
    def __init__(self, parent, threadID, plcClient, memoryList=None, readIntv=3):
        """ Init Example: 
            plcReader = M221Reader(None, 1, M221Client('192.168.10.72', debug=True), 
                                    memoryList=[('M20',4), ('M19',8)])
            Args:
                parent (ref): parent obj ref.
                threadID (int): Thread ID. 
                plcClient (ref): a <M221Client> obj ref.
                memoryList (list(str), optional): memory tag list. Defaults to None.
                readIntv (int, optional): read time interval (sec). Defaults to 3.
        """
        super().__init__(parent)
        self.parent = parent
        self.threadID = threadID
        self.M221PlcClient = plcClient
        self.readIntv = readIntv
        self.memoryList = memoryList
        self.memData = {'time': time.time(), 'data': []}
        self.terminate = False

    #-----------------------------------------------------------------------------
    def run(self):
        print("M221Reader: Start to read data from PLC [%s]" %str(self.M221PlcClient.getPLCInfo()))
        while not self.terminate:
            if self.M221PlcClient and self.M221PlcClient.getConnectionState():
                dataList = []
                self.memData['time'] = time.time()
                for mem, bitNum in self.memoryList:
                    data = self.M221PlcClient.readMem(mem, bitNum=bitNum)
                    dataList.append(data)
                self.memData['data'] = dataList
            else:
                self.M221PlcClient.reconnect()
            time.sleep(self.readIntv)
        print("M221Reader: Stop reading data from PLC [%s]" %str(self.M221PlcClient.getPLCInfo()))
        self.M221PlcClient.disconnect()
    
    #-----------------------------------------------------------------------------
    def getLastData(self):
        return self.memData

    def stop(self):
        self.terminate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class M221Client(object):
    """ Client to connect to the M221 PLC to read the memory data."""
    def __init__(self, plcIp, plcPort=PLC_PORT, pingPlc=True, debug=False):
        """ Init Example: client = M221Client('127.0.0.1', debug=True)
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
        self.connectLockFlg = False
        # Check whether the PLC is reachable
        if pingPlc and not self._pingPLC(self.ip): 
            print("Warning: The PLC [%s] is not reachable. Please check the connection." % self.ip)
            return None
        # Init the PLC connection parameters.
        self.plcAgent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.plcAgent.connect((self.ip, self.port))
            if self.debug: print("M221Client: Connected to the PLC [%s]" % self.ip)
            self.connected = True
        except Exception as error:
            print("M221Client: Can not access to the PLC [%s]" % str(self.plcAgent))
            print(error)

#-----------------------------------------------------------------------------
    def _pingPLC(self, host):
        """ Returns True if host (str) responds to a ping request. Remember that a host 
            may not respond to a ping (ICMP) request even if the host name is valid.
        """
        data = ping(host, timeout=2, verbose=False)
        if data.rtt_avg_ms >= 1000:
            # PLC more than 1000ms response, time out.
            print("M221Client: PLC [%s] is not responding." % host)
            return False
        return True

#-----------------------------------------------------------------------------
# Define all the get() methods for the M221 PLC.
    def _getPlCRespStr(self, modbusMsg):
        """ Convert the ModBus message string to hex byte and send to PLC, wait for 
            PLC's response and convert the response hex bytes to string.
        """
        if not (self.connected and modbusMsg): return ''  # check whether the input is empty.
        if self.debug: print('M221Client send: %s' % modbusMsg)
        bdata = bytes.fromhex(modbusMsg)
        try:
            self.plcAgent.send(bdata)
            respBytes = self.plcAgent.recv(BUFF_SZ)
            respStr = respBytes.decode('hex') if DECODE_MD else respBytes.hex()
            self.connected = True
            return respStr
        except Exception as error:
            self.connected = False
            print("Error > _getPlCRespStr(): Can not access to the PLC [%s]" % self.ip)
            return ''
    
    def getPLCInfo(self):
        return {'ip': self.ip, 'port': self.port, 'connected': self.connected}

    def getConnectionState(self):
        """ Returns the connection state of the PLC."""
        return self.connected

#-----------------------------------------------------------------------------
    def readMem(self, memAddrTag, bitNum=8):
        """ Fetch the current plc memory state with a bit length. 
            Args:
                memAddrTag (str): M221 memory tag such as "M60"
                bitNum (int, optional): number of bit to read from the memory address. Defaults to 8.
            Returns:
                _type_: hex byte string of the memory address state. example 0x0101
        """
        if str(memAddrTag).startswith('M'):
            memoryDecimal = int(memAddrTag[1:])
            memoryHex = hex(memoryDecimal)[2:]
            bitNumHex = hex(bitNum)[2:]
            modbusMsg = ''.join((TID, PROTOCOL_ID, R_LENGTH, UID, M_RD, memoryHex, bitNumHex))
            response = self._getPlCRespStr(modbusMsg)
            return response
        else:
            print("Error > readMem(): Invalid memory address [%s]" % memAddrTag)
            return None

#-----------------------------------------------------------------------------
    def writeMem(self, memAddrTag, val):
        """ Set one byte on/off data to the plc memory address."""
        if val not in ('0', '1'): val = '1' if val else '0'
        if str(memAddrTag).startswith('M'):
            memoryDecimal = int(memAddrTag[1:])
            memoryHex = hex(memoryDecimal)[2:]
            byteVal = VALUES[val]
            modbusMsg = ''.join((TID, PROTOCOL_ID, W_LENGTH, UID, M_FC, memoryHex, 
                                 BIT_COUNT, BYTE_COUNT, byteVal))
            response = self._getPlCRespStr(modbusMsg)
            return response
        else:
            print("Error > writeMem(): Invalid memory address [%s]" % memAddrTag)
            return None 

#-----------------------------------------------------------------------------
    def reconnect(self):
        """ Reconnect to the PLC and set the PLC connection flag."""
        if self.getConnectionState(): self.disconnect()
        try:
            self.plcAgent.connect((self.ip, self.port))
            if self.debug: print("M221Client: Connected to the PLC [%s]" % self.ip)
            self.connected = True
        except Exception as error:
            print("M221Client: Can not access to the PLC [%s]" % str(self.plcAgent))
            print(error)
            self.connected = False
        return self.connected

#-----------------------------------------------------------------------------
    def disconnect(self):
        """ Disconnect from PLC."""
        print("M221: Disconnect from PLC [%s]." %str(self.ip))
        self.connected = False
        if self.plcAgent: self.plcAgent.close()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def testCase(mode):
    """ Module testCase function."""
    if mode == 0:
        print("Test case 1: local connection test.")
        plc = M221Client('127.0.0.1', debug=True)
        plc.readMem('M10', bitNum=8)
        plc.writeMem('M10', 0)
        plc.disconnect()
    elif mode == 1:
        print("Test case 2: remote connection test.")
        plc = M221Client('192.168.10.72', debug=True)
        plc.readMem('M10', bitNum=8)
        plc.writeMem('M10', 0)
        plc.disconnect()
    elif mode == 2:
        print("Test case 3: remote connection test with reader thread.")
        plc = M221Client('192.168.10.72', debug=True)
        readMemList = [('M1', 8), ('M11', 8)]
        plcReader = M221Reader(None, 1, plc, memoryList=readMemList)
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
