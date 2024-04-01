#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcServerTest.py
#
# Purpose:     testcase program used to test lib<modbusTcpCom.py> 
#
# Author:      Yuancheng Liu
#
# Created:     2023/06/11
# Version:     v_0.1
# Copyright:   
# License:     
#-----------------------------------------------------------------------------
import modbusTcpCom

class testLadderLogic(modbusTcpCom.ladderLogic):

    def __init__(self, parent) -> None:
        super().__init__(parent)

    def initLadderInfo(self):
        self.holdingRegsInfo['address'] = 0
        self.holdingRegsInfo['offset'] = 4
        self.srcCoilsInfo['address'] = 0
        self.srcCoilsInfo['offset'] = 4
        self.destCoilsInfo['address'] = 0
        self.destCoilsInfo['offset'] = 4

    def runLadderLogic(self, regsList, coilList=None):
        # coils will be set ast the reverse state of the input registers' state. 
        result = []
        for state in regsList:
            result.append(not state)
        return result

ALLOW_R_L = ['127.0.0.1', '192.168.0.10']
ALLOW_W_L = ['127.0.0.1']

hostIp = 'localhost'
hostPort = 502

testladderlogic = testLadderLogic(None)
dataMgr = modbusTcpCom.plcDataHandler(allowRipList=ALLOW_R_L, allowWipList=ALLOW_W_L)
server = modbusTcpCom.modbusTcpServer(hostIp=hostIp, hostPort=hostPort, dataHandler=dataMgr)
serverInfo = server.getServerInfo()
dataMgr.initServerInfo(serverInfo)
dataMgr.addLadderLogic('testLogic', testladderlogic)
dataMgr.setAutoUpdate(True)
# preset some case here: 
dataMgr.updateOutPutCoils(0, [0, 0, 0, 0])
dataMgr.updateHoldingRegs(0, [0, 0, 1, 1])
print('Start server ...')
server.startServer()