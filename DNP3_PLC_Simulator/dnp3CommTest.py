#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        dnp3CommTest.py
#
# Purpose:     This module is the testcase program for the (IEEE 1815) DNP3.0  
#              library <dnp3Comm.py>, it will start a server in sub-thread and 
#              init 2 clients to test the data read and transmit.
#
# Author:      Yuancheng Liu
#
# Created:     2026/07/28
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import threading 

import dnp3Comm

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." % message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DNP3ServerThread(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = dnp3Comm.DNP3Server(maxConn=3)
        # Add the parameters:
        self.server.addBinaryInput(0, False)
        self.server.addBinaryInput(1, True)
        self.server.addAnalogInput(0, 0.0)
        self.server.addBinaryOutput(0, False)
        self.server.addBinaryOutput(1, True)
        self.server.addAnalogOutput(0, 0.0)

    def run(self):
        self.server.start()

    def getDNP3ServerObj(self):
        return self.server

    def runLadderLogic(self):
        v1 = self.server.getBinaryInput(0)
        v2 = self.server.getBinaryInput(1)
        
        





