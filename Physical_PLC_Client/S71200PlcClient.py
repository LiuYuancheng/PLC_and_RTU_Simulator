#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:         S71200PlcClient.py
#
# Purpose:      This module is used to connect to the Siemens s7-1200 PLC to read 
#               data from memory to get the input state of a PLC contact or write 
#               data to a memory address then change the output state of a PLC coil.
#               http://simplyautomationized.blogspot.com/2014/12/raspberry-pi-getting-data-from-s7-1200.html
#
# Author:      Yuancheng Liu
#
# Created:     2024/06/26
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import snap7
import snap7.util
from pythonping import ping

# PLC port
PLC_PORT = 102
# default memeory start Index on S7-1200
MEM_AREA_IDX = {
    'i': 0x81,
    'q': 0x82, 
    'm': 0x83 
}

# Set the output type
BOOL_TYPE = 1
INT_TYPE = 2
REAL_TYPE = 3
WORD_TYPE = 4
DWORD_TYPE = 5

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class S71200Client(object):
    def __init__(self, plcIp, plcPort=PLC_PORT, pingPlc=True, debug=False):
        self.ip = plcIp
        self.port = plcPort
        self.debug = debug
        self.connected = False
        # Check whether the PLC is reachable
        if pingPlc and not self._pingPLC(self.ip): 
            print("The PLC [%s] is not reachable. Please check the connection." % self.ip)
            return None
        self.plcAgent = snap7.client.Client()        
        try:
            self.plcAgent.connect(self.plcIp, 0, 1, self.port)
            self.connected = self.plcAgent.get_connected()
        except Exception as err:
            print("S71200: S71200Client init Error: %s" % err)
            return None

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

    def _getMemValue(self, mbyte, valType, startMIdx, bitIndex):
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
            print("Error: _getMemValue()> input type invlided: %s" %str(valType))
        return data


    def getPLCInfo(self):
        return {'ip': self.ip, 'port': self.port, 'connected': self.connected}

    def getConnectionState(self):
        """ Returns the connection state of the PLC."""
        return self.connected

#-----------------------------------------------------------------------------
    def readMem(self, memAddrTag, returnByte=False):
        """ Fetch the current PLC state from related memeory address: IX0.N-input contact, 
            QX0.N-output coil, MX0.N-memory address tag

            Args:
                memAddrTag (_type_): _description_
                returnByte (bool, optional): _description_. Defaults to False.

            Returns:
                _type_: _description_
        """
        if not self.connected: return None
        memType = str(memAddrTag[0]).lower()
        if not memType in MEM_AREA_IDX.keys():
            print("Error: readMem()> input memory tag invlided: %s" %str(memAddrTag))
        valLength = 1
        valType = None 
        bitIndex = 0
        startMIdx = 0
        if(memAddrTag[1].lower() == 'x'):
            # Config the bool type data tag 
            valLength = 1
            valType = BOOL_TYPE
            startMIdx = int(memAddrTag.split('.')[0][2:])
            bitIndex = int(memAddrTag.split('.')[1])
        elif(memAddrTag[1].lower() == 'b'):
            # Config the bype or integer type data tag
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
        elif('freal' in memAddrTag.lower()):
            valLength = 4
            valType = REAL_TYPE
            startMIdx = int(memAddrTag.lower().replace('freal', ''))
        else:
            print("Error: readMem()> input memory tag invlided: %s" %str(memAddrTag))
            return None
        
        memoryArea = MEM_AREA_IDX[memType]
        try: 
            mbyte = self.plcAgent.read_area(memoryArea, 0, startMIdx, valLength)
            if self.debug:
                print("S7PLC1200 getMem() get data set[mem[0], start, length, bit, mbyte]:" % str(
                    memAddrTag[0].lower(), startMIdx, valLength, bitIndex, str(mbyte)))
            self.connected = True 
            return mbyte if returnByte else self._getMemValue(mbyte, valType, bitIndex)
        except Exception as e:
            print("Error: readMem()> %s" %str(e))
            self.connected = False
            return None

#-----------------------------------------------------------------------------
    def getMem(self, mem, returnByte=False):
        """ Get the PLC state from related memeory address: IX0.N-input, QX0.N-output, 
            MX0.N-memory
        """
        if not self.connected: return None
        out = None  # output functino selection type
        start = 0  # start position idx
        bit = 0
        length = 1  # data length
        # get the area memory address
        memType = mem[0].lower()
        area = self.memAreaDict[memType]
        # Set the data lenght and start idx.
        if(mem[1].lower() == 'x'):  # bit
            length, out, start, bit = 1, BOOL_TYPE, int(
                mem.split('.')[0][2:]), int(mem.split('.')[1])
        elif(mem[1].lower() == 'b'):  # byte
            length, out, start = 1, INT_TYPE, int(mem[2:])
        elif(mem[1].lower() == 'w'):  # word
            length, out, start = 2, INT_TYPE, int(mem[2:])
        elif(mem[1].lower() == 'd'):  # double
            length, out, start = 4, DWORD_TYPE, int(mem.split('.')[0][2:])
        elif('freal' in mem.lower()):  # double word (real numbers)
            length, out, start = 4, REAL_TYPE, int(mem.lower().replace('freal', ''))
        # Read data from the PLC
        mbyte = self.plc.read_area(area, 0, start, length)
        if(self.debug):
            print("S7PLC1200 getMem() get data set[mem[0], start, length, bit, mbyte]:" % str(
                mem[0].lower(), start, length, bit, str(mbyte)))
        # Call the utility functions from <snap7.util>
        if(returnByte):
            return mbyte
        elif(out == BOOL_TYPE):
            return get_bool(mbyte, 0, bit)
        elif(out == INT_TYPE):
            return get_int(mbyte, start)
        elif(out == REAL_TYPE):
            return get_real(mbyte, 0)
        elif(out == DWORD_TYPE):
            return get_dword(mbyte, 0)
        elif(out == WORD_TYPE):
            return get_int(mbyte, start)

#-----------------------------------------------------------------------------
    def writeMem(self, mem, value):
        """ Set the PLC state from related memeory address: IX0.N-input, QX0.N-output, 
            MX0.N-memory.
        """
        if not self.connected: return None
        data = self.getMem(mem, True)
        start = bit = 0  # start position idx
        # get the area memory address
        memType = mem[0].lower()
        area = self.memAreaDict[memType]
        # Set the data lenght and start idx and call the utility functions from <snap7.util>
        if(mem[1].lower() == 'x'):  # bit
            start, bit = int(mem.split('.')[0][2:]), int(mem.split('.')[1])
            set_bool(data, 0, bit, int(value))
        elif(mem[1].lower() == 'b'):  # byte
            start = int(mem[2:])
            set_int(data, 0, value)
        elif(mem[1].lower() == 'd'):
            start = int(mem.split('.')[0][2:])
            set_dword(data, 0, value)
        elif('freal' in mem.lower()):  # double word (real numbers)
            start = int(mem.lower().replace('freal', ''))
            set_real(data, 0, value)
        # Call the write function and return the value.
        return self.plc.write_area(area, 0, start, data)

#-----------------------------------------------------------------------------
    def disconnect(self):
        """ Disconnect from PLC."""
        print("S7PLC1200:    Disconnect from PLC.")
        self.connected = False
        if self.plc: self.plc.disconnect()

#-----------------------------------------------------------------------------
def testCase():
    plc = S7PLC1200('192.168.10.73')  # ,debug=True)
    #turn on outputs cascading
    plc.writeMem('qx0.'+str(3), False)
    plc.writeMem('qx0.'+str(4), False)
    for x in range(0, 7):
        plc.writeMem('qx0.'+str(x), True)
        time.sleep(0.5)
    time.sleep(1)
    #turn off outputs
    for x in range(0, 7):
        plc.writeMem('qx0.'+str(x), False)
        time.sleep(0.5)
    plc.disconnect()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase()
