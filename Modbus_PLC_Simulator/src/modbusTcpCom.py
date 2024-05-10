#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        modbusTcpCom.py
#
# Purpose:     This module will provide the modbus-TCP client and server communication
#              API for testing or simulating the data flow connection between PLC and SCADA 
#              system. The module is implemented based on python pyModbus lib module: 
#              - Reference: https://github.com/sourceperl/pyModbusTCP
#
# Author:      Yuancheng Liu
#
# Created:     2023/06/11
# Version:     v_0.1.3
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design:

    We want to create a normal Modbus TCP communication channel (client + server) lib
    to read the data from a real PLC or simulate the PLC Modbus data handling process (handle 
    modbusTCP request from other program which same as PLC).
    
    Four modules will be provided in this module: 

    - ladderLogic: An interface class hold the ladder logic calculation algorithm, it will take the 
        holding register's state, source coils state then generate the destination coils states.
        For example below ladder logic:
        --|reg-00|--|reg-01|----------------------(src-coil-00)------------(dest-coil-02)---
        1. Put the 'and' gate logic of reg-00, reg-01 and src-coil-00 in runLadderLogic() function. 
        2. Set source register info as {'address': 0, 'offset': 2} in initLadderInfo() function.
        3. Set source coil info as {'address': 0, 'offset': 1} in initLadderInfo() function.
        4. Set destination coil info as {'address': 2, 'offset': 1} in initLadderInfo() function.
        5. Add the ladder obj to plcDataHandler()
        6. When plcDataHandler holding registers changed, the list [reg-00, reg-01] and [coil-00],
            will auto passed in the runLadderLogic() function.
        7. runLadderLogic() will return the calculated coils list result, plcDataHandler will set 
            the destination coils with the result.

    - plcDataHandler: A pyModbusTcp.dataHandler module to keep one allow read white list and one 
        allow write white list to filter the client's coils or registers read and write request.
        As most of the PLC are using the input => register (memory) parameter config, they are 
        not allowed to change the input directly, we only provide the coil and holding register 
        write functions.
    
    - modbusTcpClient: Modbus-TCP client module to read/write holding register and coils data 
        from/to the target PLC. 

    - modbusTcpServer: Modbus-TCP server module will be used by PLC module to handle the modbus 
        data read/set request. If the input data handler is None, the server will create and keep 
        one empty databank inside.
"""
import re
import time
from collections import OrderedDict

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer, DataHandler, DataBank
from pyModbusTCP.constants import EXP_ILLEGAL_FUNCTION

IPV4_PATTERN = r'^(\d{1,3}\.){3}\d{1,3}$'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class ladderLogic(object):
    """ The PLC ladder logic object used by data handler, details refer to the 
        < Program Design > part.
    """

    def __init__(self, parent, ladderName=None) -> None:
        """ Init example: testladderlogic = testLogic(None)"""
        self.parent = parent
        self.ladderName= ladderName
        self.holdingRegsInfo = {'address': None, 'offset': None}
        self.srcCoilsInfo = {'address': None, 'offset': None}
        self.destCoilsInfo = {'address': None, 'offset': None}
        self.initLadderInfo()

    def initLadderInfo(self):
        """ Init the ladder register, src and dest coils information, this function will 
            be called during the logic init. Please over write this function.
        """
        pass

#-----------------------------------------------------------------------------
# Define all the get() functions here:

    def getLadderName(self):
        return self.ladderName

    def getHoldingRegsInfo(self):
        return self.holdingRegsInfo

    def getSrcCoilsInfo(self):
        return self.srcCoilsInfo

    def getDestCoilsInfo(self):
        return self.destCoilsInfo

#-----------------------------------------------------------------------------
    def runLadderLogic(self, regsList, coilList=None):
        """ Pass in the registers state list, source coils state list and 
            calculate output destination coils state, this function will be called by 
            plcDataHandler.updateState() function.
            - Please over write this function.
        """
        return []

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class plcDataHandler(DataHandler):
    """ Module inherited from pyModbusTcp.dataHandlerto keep one allow read white list and one 
        allow write white list to filter the client's coils or registers read and write request.
        As most of the PLC are using the input => register (memory) parameter config, they are 
        not allowed to change the input directly, we only provide the coil and holding register 
        write functions.
    """
    def __init__(self, data_bank=None, allowRipList=None, allowWipList=None):
        """ Obj init example: plcDataHandler(allowRipList=['127.0.0.1', '192.168.10.112'], allowWipList=['192.168.10.113'])
        Args:
            data_bank (<pyModbusTcp.DataBank>, optional): . Defaults to None.
            allowRipList (list(str), optional): list of ip address string which are allowed to read 
                the data from PLC. Defaults to None allow any ip to read. 
            allowWipList (list(str), optional): list of ip address string which are allowed to write
                the data to PLC. Defaults to None allow any ip to write.
        """
        self.data_bank = DataBank() if data_bank is None else data_bank
        super().__init__(self.data_bank)
        self.serverInfo = None
        self.allowRipList = allowRipList
        self.allowWipList = allowWipList
        self.autoUpdate = False # auto update if the holding register state changed. 
        self.ladderDict = OrderedDict()

    def _checkAllowRead(self, ipaddress):
        """ Check whether the input IP addres is allowed to read the info."""
        if (self.allowRipList is None) or (ipaddress in self.allowRipList): return True
        return False 

    def _checkAllowWrite(self, ipaddress):
        """ Check whether the input IP addres is allowed to write the info."""
        if (self.allowWipList is None) or (ipaddress in self.allowWipList): return True
        return False
    
#-----------------------------------------------------------------------------
    def initServerInfo(self, serverInfo):
        """ Init the server Information.
            Args: serverInfo (<ModbusServer.ServerInfo>): after passed the datahandler to the 
            modbus server, call this function and pass in the ModbusServer.ServerInfo obj so in 
            PLC logic you can all the set/update function to change the value in databank.
        """
        self.serverInfo = serverInfo

    def addAllowReadIp(self, ipaddress):
        """ Add a IP address to the allow read list.
            Args:
                ipaddress (str): ip address string
        """
        if not isinstance(ipaddress, str): ipaddress = str(ipaddress)
        if ipaddress and re.match(IPV4_PATTERN, ipaddress):
            if not ipaddress in self.allowRipList:
                self.allowRipList.append(ipaddress)
            return True 
        return False

    def addAllowWriteIp(self, ipaddress):
        """ Add a IP address to the allow write list.
            Args:
                ipaddress (str): ip address string
        """
        if not isinstance(ipaddress, str): ipaddress = str(ipaddress)
        if ipaddress and re.match(IPV4_PATTERN, ipaddress):
            if not ipaddress in self.allowWipList:
                self.allowWipList.append(ipaddress)
            return True
        return False
        
    def addLadderLogic(self, ladderKey, logicObj):
        """ Add a <ladderLogic> obj in the ladder logic, all the ladder logic will be executed 
            in the add in sequence. So the logic execution piority will follow the add in 
            sequence, the next logic result will over write the previous one.
            Args:
                ladderKey (str): ladder logic name
                logicObj (ladderLogic): _description_
        """
        self.ladderDict[ladderKey] = logicObj

#-----------------------------------------------------------------------------
# Init all the iterator read() functions.(Internal callback by <modbusTcpServer>)
# All the input args will follow below below formate:
#   address (int): output coils address idx [Q0.x] 
#   count (int): address offset, return list length will be x + offsert.
#   srv_info (ModbusServer.ServerInfo>): passed in by server.

    def read_coils(self, address, addrOffset, srv_info):
        """ Read the output coils state"""
        try:
            if self._checkAllowRead(srv_info.client.address):
                return super().read_coils(address, addrOffset, srv_info)
        except Exception as err:
            print("read_coils() Error: %s" %str(err))
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_d_inputs(self, address, addrOffset, srv_info):
        """ Read the discrete input idx[I0.x]"""
        try:
            if self._checkAllowRead(srv_info.client.address):
                return super().read_d_inputs(address, addrOffset, srv_info)
        except Exception as err:
            print("read_d_inputs() Error: %s" %str(err))
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_h_regs(self, address, addrOffset, srv_info):
        """ Read the holding registers [idx]. """
        try:
            if self._checkAllowRead(srv_info.client.address):
                return super().read_h_regs(address, addrOffset, srv_info)
        except Exception as err:
            print("read_h_regs() Error: %s" %str(err))
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_i_regs(self, address, addrOffset, srv_info):
        """ Read the input registers"""
        try:
            if self._checkAllowRead(srv_info.client.address):
                return super().read_i_regs(address, addrOffset, srv_info)
        except Exception as err:
            print("read_i_regs() Error: %s" %str(err))
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

#-----------------------------------------------------------------------------
# Init all the iterator write() functions.(Internal callback by <modbusTcpServer>)
# All the input args will follow below below formate:
#   address (int): output coils address idx [Q0.x] 
#   count (int): address offset, return list length will be x + offsert.
#   srv_info (ModbusServer.ServerInfo>): passed in by server.


    def write_coils(self, address, bits_l, srv_info):
        """ Write the PLC out coils."""
        try:
            if self._checkAllowWrite(srv_info.client.address):
                return super().write_coils(address, bits_l, srv_info)
        except Exception as err:
            print("write_coils() Error: %s" %str(err))
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def write_h_regs(self, address, words_l, srv_info):
        """ write the holding registers."""
        try:
            if self._checkAllowWrite(srv_info.client.address):
                result = super().write_h_regs(address, words_l, srv_info)
                if self.autoUpdate: self.updateState()
                return result
        except Exception as err:
            print("write_h_regs() Error: %s" %str(err))
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

#-----------------------------------------------------------------------------
# define all the public functions wich can be called from other module.
    
    def getAllowReadIpaddresses(self):
        return self.allowRipList

    def getAllowWriteIpaddresses(self):
        return self.allowWipList

    def getHoldingRegState(self, address, offset):
        if self.data_bank and self.serverInfo:
            return self.data_bank.get_holding_registers(address, number=offset, srv_info=self.serverInfo)
        return None 

    def getCoilState(self, address, offset):
        if self.data_bank and self.serverInfo:
            return self.data_bank.get_coils(address, number=offset, srv_info=self.serverInfo)
        return None

    def setAutoUpdate(self, updateFlag):
        """ Set the auto update flag, if 'True', every time the holding registers
            state changed, the output coils will be updated automatically. 
        """
        self.autoUpdate = updateFlag

    def setAllowReadIpaddresses(self, ipList):
        if isinstance(ipList, list) or isinstance(ipList, tuple) or ipList is None:
            self.allowRipList = list(ipList)
            return True
        print("setAllowReadIpaddresses(): the input IP list is not valid.")
        return False

    def setAllowWriteIpaddresses(self, ipList):
        if isinstance(ipList, list) or isinstance(ipList, tuple) or ipList is None:
            self.allowWipList = list(ipList)
            return True
        print("setAllowWriteIpaddresses(): the input IP list is not valid.")
        return False

    def updateOutPutCoils(self, address, bitList):
        if self.serverInfo:
            return super().write_coils(address, bitList, self.serverInfo)
        print("updateOutPutCoils() Error: Parent modBus server not config, call initServerInfo() first.")
        return False

    def updateHoldingRegs(self, address, bitList):
        if self.serverInfo:
            result = super().write_h_regs(address, bitList, self.serverInfo)
            if self.autoUpdate: self.updateState()
            return result
        print("updateHoldingRegs() Error: Parent modBus server not config, call initServerInfo() first.")
        return False

    def updateState(self):
        """ Update the PLC state base on the input ladder logic one by one."""
        for key, item in self.ladderDict.items():
            print("updateState(): update ladder logic: %s" %str(key))
            # get the ladder logic related registers state.
            holdRegsInfo = item.getHoldingRegsInfo()
            if holdRegsInfo['address'] is None or holdRegsInfo['offset'] is None: continue
            regState = self.getHoldingRegState(holdRegsInfo['address'], holdRegsInfo['offset'])
            # get the ladder logic related coils state. 
            srcCoilState = None
            srcCoilInfo = item.getSrcCoilsInfo()
            if srcCoilInfo['address'] is None or srcCoilInfo['offset'] is None:
                pass
            else:
                srcCoilState = self.getCoilState(srcCoilInfo['address'], srcCoilInfo['offset'])
            # calculate the output coils state and update the coils.
            destCoilState = item.runLadderLogic(regState, coilList=srcCoilState)
            if destCoilState is None or len(destCoilState) == 0: continue
            destCoidInfo = item.getDestCoilsInfo()
            self.updateOutPutCoils(destCoidInfo['address'], destCoilState)
            
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class modbusTcpClient(object):
    """ Modbus-TCP client module to read/write data from/to PLC."""
    def __init__(self, tgtIp, tgtPort=502, defaultTO=30) -> None:
        """ Init example: client = modbusTcpCom.modbusTcpClient('127.0.0.1')
            Args:
                tgtIp (str): target PLC ip Address. 
                tgtPort (int, optional): modbus port. Defaults to 502.
                defaultTO (int, optional): default time out if modbus server doesn't 
                    response. Defaults to 30 sec.
        """
        self.tgtIp = tgtIp
        self.tgtPort = tgtPort
        self.client = ModbusClient(host=self.tgtIp, port=self.tgtPort, auto_open=True)
        self.client.timeout = defaultTO  # set time out.
        # Try to connect to the PLC in 1 sec. 
        for _ in range(5):
            print('Try to login to the PLC unit: %s.' %str((self.tgtIp, self.tgtPort)))
            if self.client.open(): break
            time.sleep(0.2)
        if self.client.is_open:
            print('Success connect to the target PLC: %s' % str((self.tgtIp, self.tgtPort)))
        else:
            print('Fail connect to the target PLC: %s' % str((self.tgtIp,self.tgtPort)))

#-----------------------------------------------------------------------------
    def checkConn(self):
        """ return the last connection state."""
        return self.client.is_open

#-----------------------------------------------------------------------------
# Define all the get() functions here:
# Return value type: 
#     - return [addressIdx: addressIdx + offset] if read success. 
#     - return None if error or server not allow client to read.


    def getCoilsBits(self, addressIdx, offset):
        """ Get the coils bit list [addressIdx: addressIdx + offset] of the PLC."""
        if self.client.is_open:
            data = self.client.read_coils(addressIdx, offset)
            if data: return list(data)
        return None
    
    def getHoldingRegs(self, addressIdx, offset):
        """ Get the holding register bit list [addressIdx: addressIdx + offset] of the PLC."""
        if self.client.is_open:
            data = self.client.read_holding_registers(addressIdx, offset)
            if data: return list(data)
        return None

#-----------------------------------------------------------------------------
# Define all the set() functions here:

    def setCoilsBit(self, addressIdx, bitVal):
        if self.client.is_open:
            data = self.client.write_single_coil(addressIdx, bitVal)
            return data
        return None

    def setHoldingRegs(self, addressIdx, bitVal):
        if self.client.is_open:
            data = self.client.write_single_register(addressIdx, bitVal)
            return data
        return None

    def close(self):
        self.client.close()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class modbusTcpServer(object):
    """ Modbus-TCP server, used by PLC module to handle the modbus data read/set 
        request.
    """
    def __init__(self, hostIp='0.0.0.0', hostPort=502, dataHandler=None) -> None:
        """Init example:
            dataMgr = modbusTcpCom.plcDataHandler(allowRipList=ALLOW_R_L, allowWipList=ALLOW_W_L)
            server = modbusTcpCom.modbusTcpServer(hostIp=hostIp, hostPort=hostPort, dataHandler=dataMgr)
        Args:
            hostIp (str, optional): '0.0.0.0' or 'localhost'. Defaults to '0.0.0.0'.
            hostPort (int, optional): modbus port. Defaults to 502.
            dataHandler (<plcDataHandler>, optional): The handler object to auto process 
                register and coils change. Defaults to None.
        """
        self.hostIp = hostIp
        self.hostPort = hostPort
        self.server = None
        if dataHandler is None:
            print("PLC logic data handler is not define, use a empty data bank")
            self.server = ModbusServer(host=hostIp, port=hostPort, data_bank=DataBank())
        else:
            self.server = ModbusServer(host=hostIp, port=hostPort, data_hdl=dataHandler)

#-----------------------------------------------------------------------------
    def isRunning(self):
        return self.server.is_run

#-----------------------------------------------------------------------------
# Define all the get() functions here:
    def getServerInfo(self):
        return self.server.ServerInfo

#-----------------------------------------------------------------------------
    def startServer(self):
        """ Run the server start loop."""
        print("Start to run the Modbus TCP server: (%s, %s)" %(self.hostIp, str(self.hostPort)))
        self.server.start()

    def stopServer(self):
        if self.isRunning():self.server.stop()
