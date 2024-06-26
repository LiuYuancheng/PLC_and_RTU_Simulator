#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        M221PlcCLient.py
#
# Purpose:     This module is used to connect to the Schneider M2xx type PLC to read 
#              data from memory to get the input state of a PLC contact or write 
#              data to a memory address then change the output state of a PLC coil.
#              related PLC setting link(function code):
#              https://www.schneider-electric.com/en/faqs/FA308725/
#              https://www.schneider-electric.com/en/faqs/FA295250/
#              https://www.schneider-electric.com/en/faqs/FA249614/
#               
# Author:      Yuancheng Liu
#
# Created:     2024/06/25
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" 
    Design purpose: 
    When we want to connect to a M221 PLC, we can use the Schneider SoMachine SDK to 
    communicate with the physical PLC. This prgram is aimed to create a python 
    module which can plug in your program to read and write data from the PLC.
    
    M221 support normal Modbus TCP protocol, but if you don't use the soMachine SDK, 
    your program can not read the contact "I0.X" or write the coil "Q0.X" directly.The 
    solution is to link the contact "I0.X" or coil "Q0.X" to a memory address, then 
    read or write the memory address to get or set the state of the contact or coil.
    As shown below:
        [I0.x] -- |M1x| 
        |M2x| -- (Q0.x)
        [I0.x] -- |Ladder Logic| -- (Q0.x)
    Protocol type: Modbus-TCP
    Reference: 
        - M221 User Manual: https://pneumatykanet.pl/pub/przekierowanie/Modicon-M221-Logic-Controller-Programming-Guide-EN.pdf
"""
import time
import socket
import threading

from platform import python_version
from pythonping import ping

# Check the python version, if < 3.6 use bytes.dencode('hex') to decode the 
# PLC response data, eles use bytes.hex() decode.
DECODE_MD = (float(python_version()[0:3]) < 3.6)

PLC_PORT = 502  # Mode bus TCP port.
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

# All the M221 Module bus constants
TID = '0000'            # Transaction Identifier (2bytes)
PROTOCOL_ID = '0000'    # Protocol Identifier (2bytes)
UID = '01'              # Unit Identifier (1byte)
BIT_COUNT = '0001'      # 
BYTE_COUNT = '01'       # 
W_LENGTH = '0008'       # write byte command unit lengh field  
R_LENGTH = '0006'       # read byte command unit length field
M_FC = '0f'             # memory access function code (write) mutiple bit
M_RD = '01'             # memory state fetch internal mupltiple bits %M
VALUES = {'0': '00', '1': '01'}

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class M221Reader(threading.Thread):
    def __init__(self, parent, threadID, plcClient, memoryList=None, readIntv=3):
        super().__init__(parent)
        self.parent = parent
        self.threadID = threadID
        self.M221PlcClient = plcClient
        self.readIntv = readIntv
        self.memoryList = memoryList
        self.memData = {'time': time.time(), 'data': []}
        self.terminate = False

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
    
    def getLastData(self):
        return self.memData

    def stop(self):
        self.terminate = True
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class M221Client(object):
    def __init__(self, plcIp, plcPort=PLC_PORT, pingPlc=True, debug=False):
        """ Init the PLC connection client: 
            Args:
                plcIp (_type_): _description_
                plcPort (_type_, optional): _description_. Defaults to PLC_PORT.
                pingPlc (bool, optional): _description_. Defaults to True.
                debug (bool, optional): _description_. Defaults to False.
            Returns:
                _type_: _description_
        """
        self.ip = plcIp
        self.port = plcPort
        self.debug = debug
        self.connected = False
        self.connectLockFlg = False
        # Check whether the PLC is reachable
        if pingPlc and not self._pingPLC(self.ip): 
            print("The PLC [%s] is not reachable. Please check the connection." % self.ip)
            return None
        
        # Init the PLC connection paramters.
        self.plcAgent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.plcAgent.connect((self.ip, self.port))
            if self.debug: print("M221: Connected to the PLC [%s]" % self.ip)
            self.connected = True
        except Exception as error:
            print("M221: Can not access to the PLC [%s]" % str(self.plcAgent))
            print(error)

#-----------------------------------------------------------------------------
    def _pingPLC(self, host):
        """ Returns True if host (str) responds to a ping request. Remember that a host 
            may not respond to a ping (ICMP) request even if the host name is valid.
        """
        data = ping(host, timeout=2, verbose=False)
        if data.rtt_avg_ms >= 1000:
            print("M221: PLC [%s] is not responding." % host)
            return False
        else:
            return True

#-----------------------------------------------------------------------------
    def _getPlCRespStr(self, modbusMsg):
        """ Convert the sendStr to hex byte and send to PLC. Wait for PLC's 
            response and convert the response hex bytes to string.
        """
        if not (self.connected and modbusMsg): return ''  # check whether the input is empty.
        if self.debug: print('M221 send: %s' % modbusMsg)
        bdata = bytes.fromhex(modbusMsg)
        try:
            self.plcAgent.send(bdata)
            respBytes = self.plcAgent.recv(BUFF_SZ)
            respStr = respBytes.dencode('hex') if DECODE_MD else respBytes.hex()
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
        """ Fetch the current plc memory state with a bit lengh 
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
            modbusMsg = ''.join((TID, PROTOCOL_ID, W_LENGTH, UID, M_FC, memoryHex, BIT_COUNT, BYTE_COUNT, byteVal))
            response = self._getPlCRespStr(modbusMsg)
            return response
        else:
            print("Error > writeMem(): Invalid memory address [%s]" % memAddrTag)
            return None 

#-----------------------------------------------------------------------------
    def reconnect(self):
        """ reconnect to the PLC and set the PLC connection flag."""
        if self.getConnectionState(): self.disconnect()
        try:
            self.plcAgent.connect((self.ip, self.port))
            if self.debug: print("M221: Connected to the PLC [%s]" % self.ip)
            self.connected = True
        except Exception as error:
            print("M221: Can not access to the PLC [%s]" % str(self.plcAgent))
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
        plc = M221Client('127.0.0.1', debug=True)
        plc.readMem('M10', bitNum=8)
        plc.writeMem('M10', 0)
        plc.disconnect()
    elif mode == 1:
        plc = M221Client('192.168.10.72', debug=True)
        plc.readMem('M10', bitNum=8)
        plc.writeMem('M10', 0)
        plc.disconnect()
    elif mode == 2:
        plc = M221Client('192.168.10.72', debug=True)
        readMemList = [('M1', 8), ('M11', 8)]
        plcReader = M221Reader(None, 1, plc, memoryList=readMemList)
        plcReader.start()
        time.sleep(3)
        print(plcReader.getLastData())
        time.sleep(1)
        plcReader.stop()
    else:
        # Add more test case here and use <mode> flag to select.
        pass

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testmode = int(input("Please enter the test mode [0-2]: "))
    testCase(testmode)
