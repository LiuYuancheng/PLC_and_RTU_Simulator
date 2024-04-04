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

import time
import os
import json
import threading
from datetime import datetime
from collections import OrderedDict

import Log

import udpCom
import snap7Comm
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE

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
        self.plcID = self.parent.getID()
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
class s7CommService(threading.Thread):

    def __init__(self, parent, threadID, dllpath=None, hostIP='0.0.0.0', hostPort=102) -> None:
        threading.Thread.__init__(self)
        self.parent = parent
        self.threadID = threadID
        self.hostIp = hostIP
        self.hostPort = hostPort
        self.server = None 
        if dllpath and os.path.exists(dllpath):
            self.server = snap7Comm.s7commServer(hostIp=self.hostIp, hostPort=self.hostPort, snapLibPath=dllpath)
        else:
            self.server = snap7Comm.s7commServer(hostIp=self.hostIp, hostPort=self.hostPort)
        self.ladderHandler = None 

    def getHostAddress(self):
        return (self.hostIp, self.hostPort)

    def getThreadID(self):
        return self.threadID 

    def getS7ServerRef(self):
        return self.server

    def run(self):
        """ Start the udp server's main message handling loop."""
        Log.info("S7comm service thread run() start.")
        self.server.startService(eventHandlerFun=self.ladderHandler)
        Log.info("S7comm service thread run() end.")
        self.threadName = None # set the thread name to None when finished.

    def setLadderHandler(self, ladderHandler):
        self.ladderHandler = ladderHandler

    def stop(self):
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class rtuSimuInterface(object):
    """ A PlC simulator to provide below functions: 
        - Create a modbus service running in subthread to handle the SCADA system's 
            modbus requirment.
        - Connect to the real world emulator to fetch the sensor state and calculate 
            the output coils state based on the ladder logic. 
        - Send the signal setup request to the real world emulator to change the signal.
    """
    def __init__(self, parent, rtuID, addressInfoDict, dllPath=None, updateInt=0.5):
        self.parent = parent
        self.rtuID = rtuID
        self.regsStateRW = OrderedDict()
        self.updateInt = updateInt
        # Init the UDP connector to connect to the realworld and test the connection.
        self.regSRWfetchKey = None 
        self.realworldAddr = addressInfoDict['realworld'] if 'realworld' in addressInfoDict.keys() else ('127.0.0.1', 3001)
        self.rwConnector = RealWorldConnector(self, self.realworldAddr)
        self._initRealWorldConnectionParm()
        # Init the modbus TCP service
        self.s7commAddr = addressInfoDict['hostaddress'] if 'hostaddress' in addressInfoDict.keys() else ('localhost', 502)
        self.s7Service = s7CommService(self, 1, dllpath=dllPath,
                                       hostIP=self.s7commAddr[0], 
                                       hostPort=self.s7commAddr[1])
        self._initMemoryAddrs()
        self._initMemoryDefaultVals()
        self._initLadderHandler()

        self.s7Service.start()
        self.terminate = False
        Log.info('Finished init the RTU: %s' %str(self.rtuID))

    def _initRealWorldConnectionParm(self):
        self.regSRWfetchKey = None
        pass

    def _initMemoryAddrs(self):
        """ overwrite this function to add the memory init address setting here
            example:
        """
        s7commServer = self.s7Service.getS7ServerRef()
        s7commServer.initNewMemoryAddr(1, [0, 2, 4], [BOOL_TYPE, INT_TYPE, REAL_TYPE])

    def _initMemoryDefaultVals(self):
        """ overwrite this function to add the memory init address value setting here
            example:
        """
        s7commServer = self.s7Service.getS7ServerRef()
        s7commServer.setMemoryVal(1, 0, True)
        s7commServer.setMemoryVal(1, 2, 10)
        s7commServer.setMemoryVal(1, 4, 3.1415920)

    def _initLadderHandler(self):
        def handlerS7request(parmList):
            print(parmList)
        self.s7Service.setLadderHandler(handlerS7request)

    def _updateMemory(self, result):
        """ overwrite this function to update the memory state based on the realworld feed back
        """
        pass

#-----------------------------------------------------------------------------
    def getID(self):
        return self.rtuID

#-----------------------------------------------------------------------------
    def getRWInputInfo(self):
        """ Get sensors state from the real-world simulator. """
        rqstDict = {}
        for key in self.regsStateRW.keys():
            rqstDict[key] = None
        reuslt = self.rwConnector.fetchRWInputData(rqstType=self.regSRWfetchKey, inputDict=rqstDict)
        return reuslt
            
#-----------------------------------------------------------------------------
    def periodic(self, now):
        sensorInfo = self.getRWInputInfo()
        if sensorInfo is None: return
        (_, _, result) = sensorInfo
        time.sleep(0.2)
        self._updateMemory(result)
        time.sleep(self.updateInt)
        
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
        self.s7Service.stop()

#-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True


