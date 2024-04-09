#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        rtuSimulator.py
#
# Purpose:     A simple RTU simulation lib module to connect and control the real-world 
#              emulator via UDP (to simulate the electrical signals changes) and handle
#              SCADA system S7Comm request.
# 
# Author:      Yuancheng Liu
#
# Version:     v0.1.3
# Created:     2024/04/02
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

"""
Program Design:

A RTU simulator interface module with 3 components: 

- RealWorldConnector: A UDP/TCP client to fetch and parse the data from the real world
    simulation app and update the real world components. (simulate fetch electrical 
    signal from sensor and change the switch state)

- s7CommService: A sub-threading service class to run the S7Comm server parallel with 
    the main program thread. 
    
- rtuSimuInterface: A interface class with the basic function for the user to inherit 
    it to build their RTU module.

"""

import os
import time
import json
import threading
from datetime import datetime
from collections import OrderedDict

import Log # the module need to work with the lib Log module
import udpCom
import snap7Comm
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE

RECON_INT = 30      # reconnection time interval default set 30 sec
DEF_RW_PORT = 3001  # default realworld UDP connection port
DEF_S7_PORT = 102   # default S7comm port.


# Define all the module local untility functions here:
#-----------------------------------------------------------------------------
def parseIncomeMsg(msg):
    """ parse the income realworld emulator's message to tuple with 3 element: 
        request key, type and jsonString
        Args: msg (str): example: 'GET;dataType;{"user":"<username>"}'
    """
    req = msg.decode('UTF-8') if not isinstance(msg, str) else msg
    reqKey = reqType = reqJsonStr= None
    try:
        reqKey, reqType, reqJsonStr = req.split(';', 2)
    except Exception as err:
        Log.error('parseIncomeMsg(): The income message format is incorrect.')
        Log.exception(err)
        return (reqKey, reqType, reqJsonStr)
    return (reqKey.strip(), reqType.strip(), reqJsonStr)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class RealWorldConnector(object):
    """ A UDP connector(client) used to connect to the realword emulator app 
        to fetech the realworld electrical signal changes or sensor value.
    """

    def __init__(self, parent, address) -> None:
        self.parent = parent
        self.address = address
        self.realwordInfo = {'ip': address[0], 'port': address[1]}
        self.rwConnector = udpCom.udpClient((self.realwordInfo['ip'], self.realwordInfo['port']))
        self.recoonectCount = RECON_INT
        # Test login the real world emulator
        self.rtuID = self.parent.getID()
        self.realworldOnline = self._loginRealWord(plcID=self.rtuID)
        connMsg = 'Login the realworld successfully.' if self.realworldOnline else 'Cannot connect to the realworld emulator.'
        Log.info(connMsg)

#-----------------------------------------------------------------------------
    def _loginRealWord(self, plcID=None):
        """ Try to connect to the realworld emulator with the plc ID."""
        Log.info("Try to connnect to the realword [%s]..." % str(self.address))
        rqstKey, rqstType, rqstDict = 'GET', 'login', {'plcID': plcID}
        result = self._queryToRW(rqstKey, rqstType, rqstDict)
        if result:
            Log.info("Realworld emulator online, state: ready")
            return True
        return False

    def isRealWorldOnline(self):
        return self.realworldOnline

#-----------------------------------------------------------------------------
    def reConnectRW(self):
        """ Try to reconnect to the real world emulator."""
        if self.recoonectCount <= 0:
            Log.info('Try to reconnect to the realword.')
            self.realworldOnline = self._loginRealWord(plcID=self.rtuID)
            self.recoonectCount = RECON_INT
        self.recoonectCount -= 1

#-----------------------------------------------------------------------------
    def fetchRWInputData(self, rqstType='input', inputDict={}):
        """ Fetch the input data from the realworld emulator. 
            return: (key, rqstType, inputResultDict)
        """
        rqstKey = 'GET'
        if isinstance(inputDict, dict):
            return self._queryToRW(rqstKey, rqstType, inputDict)
        Log.warning("getRWInputData(): passed in input parm needs to be a dict() type.")
        return None

#-----------------------------------------------------------------------------
    def changeRWCoil(self, rqstType='signals', coilDict={}):
        """ Send the current rtu coils state to the realwrold emulator."""
        rqstKey = 'POST'
        if isinstance(coilDict, dict):
            return self._queryToRW(rqstKey, rqstType, coilDict)
        else:
            Log.warning("changeRWCoil(): passed in input parm needs to be a dict() type.get %s" %str(coilDict))
            return None

#-----------------------------------------------------------------------------
    def _queryToRW(self, rqstKey, rqstType, rqstDict, response=True):
        """ Query message send to realword emulator app.
            Args:
                rqstKey (str): request key (GET/POST/REP)
                rqstType (str): request type string.
                rqstDict (doct): request detail dictionary.
                response (bool): flag to identify whether get the response
            Returns:
                tuple: (key, type, result) or None if lose connection.
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
                    if t != rqstType: Log.warning('The reply type miss match: %s' %str((rqstType, t)))
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
    """ A sub-threading service class to run the S7Comm server parallel with the 
        the main program thread.
    """
    def __init__(self, parent, threadID, dllpath=None, hostIP='0.0.0.0', hostPort=DEF_S7_PORT) -> None:
        """ Init example: s7Service = s7CommService(self, 1, dllpath='snap7.dll')
            Args:
                parent (ref): parent obj reference
                threadID (int): sub thread ID
                dllpath (str, optional): snap7.dll path (only for Windows OS). Defaults to None.
                hostIP (str, optional): _description_. Defaults to '0.0.0.0'.
                hostPort (int, optional): _description_. Defaults to 102.
        """
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

#-----------------------------------------------------------------------------
    def getHostAddress(self):
        return (self.hostIp, self.hostPort)

    def getThreadID(self):
        return self.threadID 

    def getS7ServerRef(self):
        return self.server

#-----------------------------------------------------------------------------
    def run(self):
        """ Start the udp server's main message handling loop."""
        Log.info("S7comm service thread run() start.")
        self.server.startService(eventHandlerFun=self.ladderHandler)
        Log.info("S7comm service thread run() end.")
        self.threadName = None # set the thread name to None when finished.

#-----------------------------------------------------------------------------
    def setLadderHandler(self, ladderHandler):
        self.ladderHandler = ladderHandler

    def stop(self):
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class rtuSimuInterface(object):
    """ A RTU simulator to provide below functions: 
        - Create a S7Comm service running in subthread to handle the SCADA system's 
            request.
        - Connect to the real world emulator to fetch the sensor state and calculate 
            the output coils state based on the ladder logic. 
        - Send the signal setup request to the real world emulator to change the signal.
    """
    def __init__(self, parent, rtuID, addressInfoDict, dllPath=None, updateInt=0.5):
        """ init example:
            addressInfoDict = {
                'hostaddress': gv.gS7serverIP,
                'realworld':gv.gRealWorldIP, 
            }
            rtu = rtuSimuInterface(None, gv.RTU_NAME, addressInfoDict, 
                    dllPath=gv.gS7snapDllPath, updateInt=gv.gInterval)
        """
        self.parent = parent
        self.rtuID = rtuID
        self.regsStateRW = OrderedDict()
        self.updateInt = updateInt
        # Init the UDP connector to connect to the realworld and test the connection.
        self.regSRWfetchKey = None 
        self.realworldAddr = addressInfoDict['realworld'] if 'realworld' in addressInfoDict.keys() else ('127.0.0.1', DEF_RW_PORT)
        self.rwConnector = RealWorldConnector(self, self.realworldAddr)
        self._initRealWorldConnectionParm()
        # Init the S7Comm TCP service
        self.s7commAddr = addressInfoDict['hostaddress'] if 'hostaddress' in addressInfoDict.keys() else ('127.0.0.1', DEF_S7_PORT)
        self.s7Service = s7CommService(self, 1, dllpath=dllPath,
                                       hostIP=self.s7commAddr[0], 
                                       hostPort=self.s7commAddr[1])
        # Over write the below private function to add the customized function: 
        # Init the RTU memeory: 
        self._initMemoryAddrs()
        self._initMemoryDefaultVals()
        self._initLadderHandler()

        self.s7Service.start()
        self.terminate = False
        Log.info('Finished init the RTU: %s' %str(self.rtuID))

    #-----------------------------------------------------------------------------
    # The private function to be overwitten to add customized function.
    def _initRealWorldConnectionParm(self):
        """ Added the real world emulator data/parameters init code here.(Such as init
            the real world components state DB)
        """
        # Example: 
        # self.regSRWfetchKey = None
        pass

    def _initMemoryAddrs(self):
        """ Overwrite this function to add the RTU memory address init setting here."""
        # Example:
        #s7commServer = self.s7Service.getS7ServerRef()
        #s7commServer.initNewMemoryAddr(1, [0, 2, 4], [BOOL_TYPE, INT_TYPE, REAL_TYPE])
        pass 

    def _initMemoryDefaultVals(self):
        """ Overwrite this function to add the memory address init value here."""
        # Example:
        #s7commServer = self.s7Service.getS7ServerRef()
        #s7commServer.setMemoryVal(1, 0, True)
        #s7commServer.setMemoryVal(1, 2, 10)
        #s7commServer.setMemoryVal(1, 4, 3.1415920)
        pass 

    def _initLadderHandler(self):
        """ Overwrite this function to add the ladder logic here."""
        # Example:
        #def handlerS7request(parmList):
        #    print(parmList)
        #self.s7Service.setLadderHandler(handlerS7request)
        pass

    def _updateMemory(self, result):
        """ Overwrite this function to update the memory state based on the 
            realworld feed back
        """
        # Example: 
        # s7commServer = self.s7Service.getS7ServerRef()
        # for key, value in self.regsStateRW.items():
        #     for idx, rstData in enumerate(result[key]):
        #         memoryIdx = value[idx]
        #         s7commServer.setMemoryVal(memoryIdx, 0, rstData[0])
        #         s7commServer.setMemoryVal(memoryIdx, 2, rstData[1])
        #         s7commServer.setMemoryVal(memoryIdx, 4, rstData[2])
        #         s7commServer.setMemoryVal(memoryIdx, 6, rstData[3])
        pass

#-----------------------------------------------------------------------------
    def getID(self):
        return self.rtuID

    def getRWInputInfo(self):
        """ Get sensors state from the real-world simulator. """
        rqstDict = {}
        for key in self.regsStateRW.keys():
            rqstDict[key] = None
        reuslt = self.rwConnector.fetchRWInputData(rqstType=self.regSRWfetchKey, 
                                                   inputDict=rqstDict)
        return reuslt
            
#-----------------------------------------------------------------------------
    def periodic(self, now):
        """ Init all the RTU actions here and this function will be called periodicly 
            by the program main loop.
        """
        sensorInfo = self.getRWInputInfo()
        if sensorInfo is None: return
        (_, _, result) = sensorInfo
        time.sleep(0.1)
        self._updateMemory(result)
        
#-----------------------------------------------------------------------------
    def run(self):
        while not self.terminate:
            now = time.time()
            if self.rwConnector.isRealWorldOnline():
                self.periodic(now)
                time.sleep(0.6)
            else:
                print(" > try to reconnect to the real world emulation app: ")
                self.rwConnector.reConnectRW()
                time.sleep(2)
            time.sleep(self.updateInt)
        self.s7Service.stop()

#-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True

