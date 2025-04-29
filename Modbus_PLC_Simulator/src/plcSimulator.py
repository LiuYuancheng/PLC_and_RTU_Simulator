#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcSimulator.py
#
# Purpose:     A simple PLC simulation lib module to connect and control the real-world 
#              emulator via UDP (to simulate the electrical signals change) and handle
#              SCADA system ModBus TCP request.
# 
# Author:      Yuancheng Liu
#
# Version:     v0.1.4
# Created:     2023/06/22
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design:
    A RTU simulator interface module with 3 components: 

    - RealWorldConnector: A UDP/TCP client to fetch and parse the data from the Real-world
        simulation app and update the Real-world components. (simulate fetch electrical 
        signal from sensor and change the switch state)

    - modBusService: A sub-threading service class to run the ModBus-TCP server parallel with 
        the main program thread to handler the ModBus request.

    - plcSimuInterface: A interface class with the basic function for the user to inherit 
        it to build their PLC module.
"""

import time
import json
import threading
from datetime import datetime
from collections import OrderedDict

import Log  # the module need to work with the lib Log module
import udpCom
import modbusTcpCom

RECON_INT = 15 # reconnection time interval default set 30 sec
DEF_RW_PORT = 3001  # default Real-world UDP connection port
DEF_MB_PORT = 502   # default ModBus port.

# Define all the module local utility functions here:
#-----------------------------------------------------------------------------
def parseIncomeMsg(msg):
    """ parse the income Real-world emulator's message to tuple with 3 element: 
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
    """ A UDP connector(client) used to connect to the real word emulator app 
        to fetch the Real-world electrical signal changes or sensor value.
    """

    def __init__(self, parent, address) -> None:
        self.parent = parent
        self.address = address
        self.realworldInfo= { 'ip': address[0], 'port': address[1]}
        self.rwConnector = udpCom.udpClient((self.realworldInfo['ip'], self.realworldInfo['port']))
        self.reconnectCount = RECON_INT
        # Test login the Real-world emulator
        self.plcID = self.parent.getPlcID()
        self.realworldOnline = self._loginRealWord(plcID= self.plcID)
        connMsg = 'Login the Real-world simulator successfully' if self.realworldOnline else 'Cannot connect to the Real-world emulator'
        Log.info(connMsg)

#-----------------------------------------------------------------------------
    def _loginRealWord(self, plcID=None):
        """ Try to connect to the Real-world emulator with the plc ID."""
        Log.info("Try to connect to the real word [%s]..." % str(self.address))
        rqstKey, rqstType, rqstDict = 'GET', 'login', {'plcID': plcID}
        result = self._queryToRW(rqstKey, rqstType, rqstDict)
        if result:
            Log.info("Real-world emulator online, state: ready")
            return True
        if result is None: 
            Log.warning("Real-world emulator did not response login request.")
            return False
        elif result and len(result) == 3:
            k, t, val = result
            if k == 'REP' and t == 'login':
                try:
                    if 'state' in val.keys() and val['state'] == 'ready':
                        print("Reconnection finished.")
                        Log.info("Real-world emulator online, state: ready")
                        return True 
                    else:
                        Log.warning("Real-world emulator response not ready")
                        return False
                except:
                    Log.warning("Real-world emulator response not valid: %s" %str(val))
                    return False
            else:
                Log.warning("Real-world emulator response parameter missing: %s" %str(result))
                return False
        else:
            Log.warning("Real-world emulator response format not valid: %s , ignore the message." %str(result))
            return False

    def isRealWorldOnline(self):
        return self.realworldOnline

#-----------------------------------------------------------------------------
    def reConnectRW(self):
        """ Try to reconnect to the Real-world emulator."""
        if self.reconnectCount <= 0:
            Log.info('Try to reconnect to the Real-world simulator.')
            self.realworldOnline = self._loginRealWord(plcID=self.plcID)
            self.reconnectCount = RECON_INT
            return
        print("Reconnect to the Real-world emulator in %s sec" %str(self.reconnectCount))
        self.reconnectCount -= 1

#-----------------------------------------------------------------------------
    def fetchRWInputData(self, rqstType='input', inputDict={}):
        """ Fetch the input data from the Real-world emulator. 
            return: (key, rqstType, inputResultDict)
        """
        rqstKey = 'GET'
        if isinstance(inputDict, dict):
            return self._queryToRW(rqstKey, rqstType, inputDict)
        Log.warning("getRWInputData(): passed in input parm needs to be a dict() type.")
        return None

#-----------------------------------------------------------------------------
    def changeRWCoil(self, rqstType='signals', coilDict={}):
        """ Send the current plc coils state to the Real-world emulator."""
        rqstKey = 'POST'
        print(coilDict)
        if isinstance(coilDict, dict):
            return self._queryToRW(rqstKey, rqstType, coilDict)
        else:
            Log.warning("changeRWCoil(): passed in input parm needs to be a dict() type.get %s" %str(coilDict))
            return None

#-----------------------------------------------------------------------------
    def _queryToRW(self, rqstKey, rqstType, rqstDict, response=True):
        """ Query message send to Real-world emulator app.
            Args:
                rqstKey (str): request key (GET/POST/REP)
                rqstType (str): request type string.
                rqstDict (dict): request detail dictionary.
                dataOnly (bool, optional): flag to identify whether only return the 
                    data. Defaults to True. return (responseKey, responseType, responseJson) if set
                    to False.
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
                    if t != rqstType: Log.warning('The reply type do not match : %s' %str((rqstType, t)))
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

    def stop(self):
        self.rwConnector.disconnect()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class modBusService(threading.Thread):
    """ A sub-threading service ModBus service class hold one datahandler, one 
        data bank and one ModBus server to handler the SCADA system's ModBus request.
    """
    def __init__(self, parent, threadID, ladderHandler, hostIP='localhost', hostPort=DEF_MB_PORT):
        threading.Thread.__init__(self)
        self.parent = parent
        self.threadID = threadID
        self.hostIp = hostIP
        self.hostPort = hostPort
        self.ladderHandler = ladderHandler
        # Init the ModBus TCP server.
        self.server = modbusTcpCom.modbusTcpServer(hostIp=self.hostIp, 
                                                   hostPort=self.hostPort, 
                                                   dataHandler=self.ladderHandler)
        # load the server info into the 
        serverInfo = self.server.getServerInfo()
        self.ladderHandler.initServerInfo(serverInfo)
        self.daemon = True

#-----------------------------------------------------------------------------
    def getHostAddress(self):
        return (self.hostIp, self.hostPort)

    def getThreadID(self):
        return self.threadID 

#-----------------------------------------------------------------------------
    def run(self):
        """ Start the udp server's main message handling loop."""
        Log.info("ModBusTCP service thread run() start.")
        self.server.startServer()
        Log.info("ModBusTCP service thread run() end.")
        self.threadName = None # set the thread name to None when finished.

    def stop(self):
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class plcSimuInterface(object):
    """ A PlC simulator to provide below functions: 
        - Create a ModBus service running in sub-thread to handle the SCADA system's 
            ModBus requirement.
        - Connect to the Real-world emulator to fetch the sensor state and calculate 
            the output coils state based on the ladder logic. 
        - Send the signal setup request to the Real-world emulator to change the signal.
    """
    def __init__(self, parent, plcID, addressInfoDict, ladderObj, updateInt=0.5):
        self.parent = parent
        self.id = plcID
        self.updateInt = updateInt
        self.realworldAddr = addressInfoDict['realworld'] if 'realworld' in addressInfoDict.keys() else ('127.0.0.1', DEF_RW_PORT)
        self.allowReadAddr = addressInfoDict['allowread'] if 'allowread' in addressInfoDict.keys() else None
        self.allowWriteAddr = addressInfoDict['allowwrite'] if 'allowwrite' in addressInfoDict.keys() else None
        self.autoUpdate = True
        # input sensors state from Real-world emulator:
        self.regsAddrs = (0, 1) 
        self.regs2RWmap = None
        self.regsStateRW = None
        self._initInputState()
        # out put coils state to Real-world emulator:
        self.coilsAddrs = (0, 1)
        self.coils2RWMap = None
        self.coilStateRW = None
        self._initCoilState()
        # Init the ladder handler.
        self.dataMgr = modbusTcpCom.plcDataHandler(allowRipList=self.allowReadAddr, 
                                                   allowWipList=self.allowWriteAddr)
        self.dataMgr.addLadderLogic(ladderObj.getLadderName(), ladderObj)
        self.dataMgr.setAutoUpdate(self.autoUpdate)

        # Init the UDP connector to connect to the Real-world and test the connection. 
        self.rwConnector = RealWorldConnector(self, self.realworldAddr)
        # Init the modbus TCP service
        self.modBusAddr = addressInfoDict['hostaddress'] if 'hostaddress' in addressInfoDict.keys() else ('0.0.0.0', DEF_MB_PORT)
        self.mbService = modBusService(self, 1, self.dataMgr, hostIP=self.modBusAddr[0], hostPort=self.modBusAddr[1])
        self.mbService.start()
        self.terminate = False
        Log.info('Finished init the PLC: %s' %str(self.id))

    #-----------------------------------------------------------------------------
    # The private init functions below need to be overwitten to add customized function.

    def _initInputState(self):
        """ Overwrite this function to init all the input contact with holding 
            register setting. 
        """
        # example :
        # self.regsAddrs = (0, 1)
        # self.regSRWfetchKey = 'sensors'
        # self.regs2RWmap = OrderedDict()
        # self.regsStateRW = OrderedDict()
        pass 


    def _initCoilState(self):
        """  Overwrite this function  to init all the output coils setting. """
        # example : 
        # self.coilsAddrs = (0, 1)
        # self.coilsRWSetKey = 'signals'
        # self.coils2RWMap = OrderedDict()
        # self.coilStateRW = OrderedDict()
        pass 

#-----------------------------------------------------------------------------
    def getPlcID(self):
        return self.id

#-----------------------------------------------------------------------------
    def getRWInputInfo(self):
        """ Get sensors state from the real-world simulator. """
        rqstDict = {}
        for key in self.regsStateRW.keys():
            rqstDict[key] = None
        result = self.rwConnector.fetchRWInputData(rqstType=self.regSRWfetchKey, 
                                                   inputDict=rqstDict)
        return result
        
#-----------------------------------------------------------------------------
    def changeRWSignalCoil(self):
        """ Set the signal state to the real-world simulator app. """
        result =  self.rwConnector.changeRWCoil(rqstType=self.coilsRWSetKey, 
                                                coilDict= self.coilStateRW)
        return result
    
#-----------------------------------------------------------------------------
    def periodic(self, now):
        """ Init all the PLC actions here and this function will be called periodic
            by the program main loop.
        """
        sensorInfo = self.getRWInputInfo()
        if sensorInfo is None: return
        (_, _, result) = sensorInfo
        time.sleep(0.2)
        for key in result.keys():
            if key in self.regsStateRW.keys(): self.regsStateRW[key] = result[key]
        # Update PLC holding registers.
        self.updateHoldingRegs()
        time.sleep(0.2)
        coilUpdated = self.updateCoilOutput()
        # update the output coils state:
        if coilUpdated: self.changeRWSignalCoil()
        
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
        time.sleep(self.updateInt)

#-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True
        self.mbService.stop()
        self.rwConnector.stop()
