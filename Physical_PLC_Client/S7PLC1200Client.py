#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:           S7PLC1200.py
#
# Purpose:       This module is used to connect to the siemens s7-1200 PLC. This
#                moduel was improved based on the project:
#                http://simplyautomationized.blogspot.com/2014/12/raspberry-pi-getting-data-from-s7-1200.html
#
# Author:      Yuancheng Liu
#
# Created:     2019/08/02
# Copyright:   NUS Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------
import time
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import snap7
from snap7.util import *

# Set the output type
OUT_BOOL = 1
OUT_INT = 2
OUT_REAL = 3
OUT_WORD = 4
OUT_DWORD = 5

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class S7PLC1200(object):
    def __init__(self, ip, debug=False):
        self.ip = ip
        self.debug = debug
        self.connected = False
        self.memAreaDict = {'m': 0x83, 'q': 0x82, 'i': 0x81} # memory access dict.
        self.plc = None
        if self._pingPLC(self.ip):
            self.plc = snap7.client.Client()
            try:
                self.plc.connect(ip, 0, 1)  # connect to the PLC
                self.connected = True
            except snap7.snap7exceptions.Snap7Exception as error:
                print('S7PLC1200 ERROR: %s' %error)

#-----------------------------------------------------------------------------
    def _pingPLC(self, host):
        """ Returns True if host (str) responds to a ping request. Remember that a host 
            may not respond to a ping (ICMP) request even if the host name is valid.
        """
        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower()=='windows' else '-c'
        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', host]
        return subprocess.call(command) == 0

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
            length, out, start, bit = 1, OUT_BOOL, int(
                mem.split('.')[0][2:]), int(mem.split('.')[1])
        elif(mem[1].lower() == 'b'):  # byte
            length, out, start = 1, OUT_INT, int(mem[2:])
        elif(mem[1].lower() == 'w'):  # word
            length, out, start = 2, OUT_INT, int(mem[2:])
        elif(mem[1].lower() == 'd'):  # double
            length, out, start = 4, OUT_DWORD, int(mem.split('.')[0][2:])
        elif('freal' in mem.lower()):  # double word (real numbers)
            length, out, start = 4, OUT_REAL, int(mem.lower().replace('freal', ''))
        # Read data from the PLC
        mbyte = self.plc.read_area(area, 0, start, length)
        if(self.debug):
            print("S7PLC1200 getMem() get data set[mem[0], start, length, bit, mbyte]:" % str(
                mem[0].lower(), start, length, bit, str(mbyte)))
        # Call the utility functions from <snap7.util>
        if(returnByte):
            return mbyte
        elif(out == OUT_BOOL):
            return get_bool(mbyte, 0, bit)
        elif(out == OUT_INT):
            return get_int(mbyte, start)
        elif(out == OUT_REAL):
            return get_real(mbyte, 0)
        elif(out == OUT_DWORD):
            return get_dword(mbyte, 0)
        elif(out == OUT_WORD):
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
