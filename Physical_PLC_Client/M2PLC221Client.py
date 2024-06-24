#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:         M2PLC221.py
#
# Purpose:     This module is used to connect to the Schneider M2xx PLC. The
#              related PLC setting link(function code):
#              https://www.schneider-electric.com/en/faqs/FA308725/
#              https://www.schneider-electric.com/en/faqs/FA295250/
#              https://www.schneider-electric.com/en/faqs/FA249614/
#               
# Author:      Yuancheng Liu
#
# Created:     2019/09/02
# Copyright:   NUS Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------
import socket
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
from platform import python_version

# Check the python version, if < 3.6 use bytes.dencode('hex') to decode the 
# PLC response data, eles use bytes.hex() decode.
DECODE_MD = (float(python_version()[0:3]) < 3.6)

PLC_PORT = 502  # Mode bus TCP port.
BUFF_SZ = 1024  # TCP buffer size.
# M221 PLC memory address list.
MEM_ADDR = {'M0':   '0000',
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

TID = '0000'
PROTOCOL_ID = '0000'
UID = '01'
BIT_COUNT = '0001'
BYTE_COUNT = '01'
W_LENGTH = '0008'   # write byte lenght
R_LENGTH = '0006'   # read byte length
M_FC = '0f' # memory access function code(write).
M_RD = '01' # memory state fetch internal bits %M
VALUES = {'0': '00', '1': '01'}

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class M221(object):
    def __init__(self, ip, debug=False):
        self.ip = ip
        self.debug = debug
        self.connected = False
        self.plcAgent = None
        if self._pingPLC(self.ip):
            self.plcAgent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.plcAgent.connect((self.ip, 502))
                self.connected = True
            except OSError as error:
                print("M221: Can not access to the PLC [%s]" % str(self.plcAgent))
                print(error)

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
    def readMem(self):
        """ Fetch the current plc memory state."""
        modbusMsg = TID + PROTOCOL_ID + R_LENGTH + UID + M_RD+'0000003d'
        response = self._getRespStr(modbusMsg)
        return str(response)

#-----------------------------------------------------------------------------
    def writeMem(self, mTag, val):
        """ Set the plc memory address. mTag: (str)memory tag, val:(int) 0/1"""
        modbusMsg = TID + PROTOCOL_ID + W_LENGTH + UID + M_FC + \
            MEM_ADDR[mTag] + BIT_COUNT + BYTE_COUNT + VALUES[str(val)]
        response = self._getRespStr(modbusMsg)
        return str(response)

#-----------------------------------------------------------------------------
    def _getRespStr(self, modbusMsg):
        """ Convert the sendStr to hex byte and send to PLC. Wait for PLC's 
            response and convert the response hex bytes to string.
        """
        if not (self.connected and modbusMsg): return ''  # check whether the input is empty.
        if self.debug: print('M221 send: %s' % modbusMsg)
        bdata = bytes.fromhex(modbusMsg)
        self.plcAgent.send(bdata)
        respBytes = self.plcAgent.recv(BUFF_SZ)
        respStr = respBytes.dencode('hex') if DECODE_MD else respBytes.hex()
        return respStr

#-----------------------------------------------------------------------------
    def disconnect(self):
        """ Disconnect from PLC."""
        print("M221:    Disconnect from PLC.")
        self.connected = False
        if self.plcAgent: self.plcAgent.close()

#-----------------------------------------------------------------------------
def testCase(mode):
    """ Module testCase function."""
    if mode == 0:
        plc = M221('192.168.10.71', debug=True)
        plc.readMem()
        plc.writeMem('M10', 0)
        plc.disconnect()
    elif mode == 1:
        plc = M221('192.168.10.72', debug=True)
        plc.readMem()
        plc.writeMem('M10', 0)
        plc.disconnect()
    else:
        # Add more test case here and use <mode> flag to select.
        pass

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase(0)
