#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcSimulator.py
#
# Purpose:     A simple plc simulation lib module to connect and control the real-world 
#              emulator via UDP (to simulate the eletrical signals change) and handle
#              SCADA system Modbus TCP request.
# 
# Author:      Yuancheng Liu
#
# Version:     v0.1
# Created:     2023/06/22
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

"""
Program Design:

Returns:
    _type_: _description_
"""

import time
import json
import threading
from datetime import datetime
from collections import OrderedDict

import Log
import udpCom
import modbusTcpCom

RECON_INT = 30 # reconnection time interval default set 30 sec

# Define all the module local untility functions here:
#-----------------------------------------------------------------------------
def parseIncomeMsg(msg):
    """ parse the income message to tuple with 3 element: request key, type and jsonString
        Args: msg (str): example: 'GET;dataType;{"user":"<username>"}'
    """
    req = msg.decode('UTF-8') if not isinstance(msg, str) else msg
    reqKey = reqType = reqJsonStr= None
    try:
        reqKey, reqType, reqJsonStr = req.split(';', 2)
    except Exception as err:
        Log.error('parseIncomeMsg(): The income message format is incorrect.')
        Log.exception(err)
    return (reqKey.strip(), reqType.strip(), reqJsonStr)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class RealWorldConnector(object):
    """ A UDP connector used to connect to the realword to fetech the realworld 
        PLC input data and 

        Args:
            object (_type_): _description_
    """
    def __init__(self, parent, address) -> None:
        self.parent = parent
        self.address = address
        self.realwordInfo= {
            'ip': address[0],
            'port': address[1]
        }
        self.rwConnector = udpCom.udpClient((self.realwordInfo['ip'], self.realwordInfo['port']))
        self.recoonectCount = RECON_INT
        # Test login the real world emulator
        self.plcID = self.parent.getPlcID()
        self.realworldOnline = self._loginRealWord(plcID= self.plcID)
        connMsg = 'Login the realworld successfully' if self.realworldOnline else 'Cannot connect to the realworld emulator'
        Log.info(connMsg)

    def isRealWorldOnline(self):
        return self.realworldOnline

#-----------------------------------------------------------------------------
    def _loginRealWord(self, plcID=None):
        """ Try to connect to the realworld emulator with the plc ID."""
        Log.info("Try to connnect to the realword [%s]..." %str(self.address))
        rqstKey = 'GET'
        rqstType = 'login'
        rqstDict = {'plcID': plcID}
        result = self._queryToRW(rqstKey, rqstType, rqstDict)
        if result:
            Log.info("Realworld emulator online, state: ready")
            return True
        return False

#-----------------------------------------------------------------------------
    def reConnectRW(self):
        """ Try to reconnect to the real world emulator."""
        if self.recoonectCount <= 0:
            Log.info('Try to reconnect to the realword.')
            self.realworldOnline = self._loginRealWord(plcID=self.plcID)
            self.recoonectCount = RECON_INT
        self.recoonectCount -= 1

#-----------------------------------------------------------------------------
    def fetchRWInputData(self, rqstType='input', inputDict={}):
        """ Fetch the input data from the realworld emulator. 
            return: 
                (key, rqstType, inputResultDict)
        """
        rqstKey = 'GET'
        if isinstance(inputDict, dict):
            return self._queryToRW(rqstKey, rqstType, inputDict)
        Log.warning("getRWInputData(): passed in input parm needs to be a dict() type.")
        return None

#-----------------------------------------------------------------------------
    def changeRWCoil(self, rqstType='signals', coilDict={}):
        """ Send the current plc coils state to the realwrold emulator."""
        rqstKey = 'POST'
        print(coilDict)
        if isinstance(coilDict, dict):
            return self._queryToRW(rqstKey, rqstType, coilDict)
        else:
            Log.warning("changeRWCoil(): passed in input parm needs to be a dict() type.get %s" %str(coilDict))
            return None

#-----------------------------------------------------------------------------
    def _queryToRW(self, rqstKey, rqstType, rqstDict, response=True):
        """ Query message to realword emulator
            Args:
                rqstKey (str): request key (GET/POST/REP)
                rqstType (str): request type string.
                rqstDict (doct): request detail dictionary.
                dataOnly (bool, optional): flag to indentify whether only return the 
                    data. Defaults to True. return (responseKey, responseType, responseJson) if set
                    to False.
        Returns:
            _type_: refer to <dataOnly> flag's explaination.
        """
        k = t = result = None
        if rqstKey and rqstType and rqstDict:
            rqst = ';'.join((rqstKey, rqstType, json.dumps(rqstDict)))
            if self.rwConnector:
                resp = self.rwConnector.sendMsg(rqst, resp=response)
                if resp:
                    #gv.gDebugPrint('===> resp:%s' %str(resp), logType=gv.LOG_INFO)
                    k, t, data = parseIncomeMsg(resp)
                    if k != 'REP': Log.warning('The msg reply key %s is invalid' % k)
                    if t != rqstType: Log.warning('The reply type doesnt match.%s' %str((rqstType, t)))
                    try:
                        result = json.loads(data)
                        self.lastUpdateT = datetime.now()
                    except Exception as err:
                        Log.exception('Exception: %s' %str(err))
                        return None
                else:
                    Log.warning("Lost connection to the server.")
                    self.realworldOnline = False
                    return None
        else:
            Log.error("queryBE: input missing: %s" %str(rqstKey, rqstType, rqstDict))
        return (k, t, result)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class modBusService(threading.Thread):
    """ mod bus service hold one datahandler, on databank and one Modbus server 
        to handler the SCADA system's modbus request.
    """
    def __init__(self, parent, threadID, ladderHandler, hostIP='localhost', hostPort=502):
        threading.Thread.__init__(self)
        self.parent = parent
        self.threadID = threadID
        self.hostIp = hostIP
        self.hostPort = hostPort
        self.ladderHandler = ladderHandler
        # Init the modbus TCP server.
        self.server = modbusTcpCom.modbusTcpServer(hostIp=self.hostIp, 
                                                   hostPort=self.hostPort, 
                                                   dataHandler=self.ladderHandler)
        # load the server info into the 
        serverInfo = self.server.getServerInfo()
        self.ladderHandler.initServerInfo(serverInfo)
        self.daemon = True

    def getHostAddress(self):
        return (self.hostIp, self.hostPort)

    def getThreadID(self):
        return self.threadID 

    def run(self):
        """ Start the udp server's main message handling loop."""
        Log.info("ModbusTCP service thread run() start.")
        self.server.startServer()
        Log.info("ModbusTCP service thread run() end.")
        self.threadName = None # set the thread name to None when finished.

    def stop(self):
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class plcSimuInterface(object):
    """ A PlC simulator to provide below functions: 
        - Create a modbus service running in subthread to handle the SCADA system's 
            modbus requirment.
        - Connect to the real world emulator to fetch the sensor state and calculate 
            the output coils state based on the ladder logic. 
        - Send the signal setup request to the real world emulator to change the signal.
    """
    def __init__(self, parent, plcID, addressInfoDict, ladderObj, updateInt=0.5):
        self.parent = parent
        self.id = plcID
        self.updateInt = updateInt
        self.realworldAddr = addressInfoDict['realworld'] if 'realworld' in addressInfoDict.keys() else ('127.0.0.1', 3001)
        self.allowReadAddr = addressInfoDict['allowread'] if 'allowread' in addressInfoDict.keys() else None
        self.allowWriteAddr = addressInfoDict['allowwrite'] if 'allowwrite' in addressInfoDict.keys() else None
        self.autoUpdate = True
        # input sensors state from real world emulator:
        self.regsAddrs = (0, 1) 
        self.regs2RWmap = None
        self.regsStateRW = None
        self.initInputState()
        # out put coils state to real world emulator:
        self.coilsAddrs = (0, 1)
        self.coils2RWMap = None
        self.coilStateRW = None
        self.initCoilState()
        # Init the ladder handler.
        self.dataMgr = modbusTcpCom.plcDataHandler(allowRipList=self.allowReadAddr, 
                                                   allowWipList=self.allowWriteAddr)
        self.dataMgr.addLadderLogic(ladderObj.getLadderName(), ladderObj)
        self.dataMgr.setAutoUpdate(self.autoUpdate)

        # Init the UDP connector to connect to the realworld and test the connection. 
        self.rwConnector = RealWorldConnector(self, self.realworldAddr)
        # Init the modbus TCP service
        self.modBusAddr = addressInfoDict['hostaddress'] if 'hostaddress' in addressInfoDict.keys() else ('localhost', 502)
        self.mbService = modBusService(self, 1, self.dataMgr, hostIP=self.modBusAddr[0], hostPort=self.modBusAddr[1])
        self.mbService.start()
        self.terminate = False
        Log.info('Finished init the PLC: %s' %str(self.id))

    def initInputState(self):
        self.regsAddrs = (0, 1)
        self.regSRWfetchKey = 'sensors'
        self.regs2RWmap = OrderedDict()
        self.regsStateRW = OrderedDict()

    def initCoilState(self):
        self.coilsAddrs = (0, 1)
        self.coilsRWSetKey = 'signals'
        self.coils2RWMap = OrderedDict()
        self.coilStateRW = OrderedDict()

#-----------------------------------------------------------------------------
    def getPlcID(self):
        return self.id

#-----------------------------------------------------------------------------
    def getRWInputInfo(self):
        """ Get sensors state from the real-world simulator. """
        rqstDict = {}
        for key in self.regsStateRW.keys():
            rqstDict[key] = None
        reuslt = self.rwConnector.fetchRWInputData(rqstType=self.regSRWfetchKey, inputDict=rqstDict)
        return reuslt
        
#-----------------------------------------------------------------------------
    def changeRWSignalCoil(self):
        """ Set the signal state to the real-world simulator. """
        result =  self.rwConnector.changeRWCoil(rqstType=self.coilsRWSetKey, 
                                                coilDict= self.coilStateRW)
        return result
    
#-----------------------------------------------------------------------------
    def periodic(self, now):
        sensorInfo = self.getRWInputInfo()
        if sensorInfo is None: return
        (_, _, result) = sensorInfo
        time.sleep(0.2)
        for key in result.keys():
            self.regsStateRW[key] = result[key]
        # Update PLC holding registers.
        self.updateHoldingRegs()
        time.sleep(0.2)
        coilUpdated = self.updateCoilOutput()
        # update the output coils state:
        if coilUpdated: self.changeRWSignalCoil()
        time.sleep(self.updateInt)
        
#-----------------------------------------------------------------------------
    def updateHoldingRegs(self):
        holdingRegs = []
        for val in self.regsStateRW.values():
            holdingRegs += val
        Log.info("updateModBusInfo(): update holding registers: %s" %str(holdingRegs))
        self.dataMgr.updateHoldingRegs(0, holdingRegs)

#-----------------------------------------------------------------------------
    def updateCoilOutput(self):
        address, offset = self.coilsAddrs
        result = self.dataMgr.getCoilState(address, offset)
        updatedFlg = False
        for key in self.coilStateRW.keys():
            idx, idxOffset = self.coils2RWMap[key]
            if self.coilStateRW[key] == result[idx:idxOffset]: continue
            self.coilStateRW[key] = result[idx:idxOffset]
            updatedFlg = True
        return updatedFlg
#-----------------------------------------------------------------------------
    def run(self):
        while not self.terminate:
            now = time.time()
            if self.rwConnector.isRealWorldOnline():
                self.periodic(now)
                time.sleep(0.6)
            else:
                self.rwConnector.reConnectRW()
                time.sleep(1)

#-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    pass
if __name__ == "__main__":
    main()
