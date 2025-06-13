#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        ice104Comm.py
#
# Purpose:     This module will provide the IEC-60870-5-104 client and server 
#              communication API to test or simulate the data flow connection 
#              between PLC/RTU and SCADA system. The module is implemented based 
#              on python iec104-python lib module: 
#              - Reference: https://github.com/Fraunhofer-FIT-DIEN/iec104-python
#
# Author:      Yuancheng Liu
#
# Created:     2025/04/27
# Version:     v_0.0.4
# Copyright:   Copyright (c) 2025 Liu Yuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design:

    We want to create a simple IEC-60870-5-104 channel (client + server) library 
    module to simulate the data communication to PLC or RTU via IEC104. For the 
    server data storage 3 types of point data are provided:
    1. Server measured bool value (M_SP_NA): 
        - Single-point information, can be read from server and client, but can only 
        be changed from server via point.value = <val>. 
        - Expected value: True/False
    2. Server measured number value (M_ME_NC) : 
        - Short floating point number, can be read from server and client, but can only
        be changed from server via point.value = <val>
        - Expected value: float number, need to do round if do value compare.
    3. Server changeable value (C_RC_TA): 
        - Regulating step command , can be read from server and client, but can only 
        be changed from client via transmit call.
        - Expected value: iec104.Step.HIGHER/LOWER/INVALID_0/INVALID_1

    To change a measured bool value from client, add a function to link one M_SP_NA
    with one C_RC_TA, when the client side changed C_RC_TA, then modify the M_SP_NA. 

    reference: https://support.kaspersky.com/kics-for-networks/3.0/206199


    Three modules will be provided in this module: 
    - ladderLogic: An interface class hold the ladder logic calculation algorithm run in the 
        PLC side to set the measured src value based on PLC physical input and update the measured 
        dest value based on PLC output. ps: to change the measured src value, link the change value 
        to the measured value.

    - iec104Client: IEC-60870-5-104 client class run in the SCADA (HMI) side to read and set data 
        from the PLC/RTU side.

    - iec104Server: IEC-60870-5-104 server class run in the PLC/RTU side to read and set data.

"""

import time
import c104 # pip install c104
from collections import OrderedDict

# define the network constants
DEF_HOST_IP = '0.0.0.0'
DEF_60870_5_104_PORT = 2404
IPV4_PATTERN = r'^(\d{1,3}\.){3}\d{1,3}$' # regex pattern for ipv4 address verification.

# define the IEC104 data type
M_BOOL_TYPE = c104.Type.M_SP_NA_1   # measured bool type can only be changed by server.
M_FLOAT_TYPE = c104.Type.M_ME_NC_1  # measured float type can only be changed by server.
C_STEP_TYPE = c104.Type.C_RC_TA_1   # Changeable step type can only be changed by client.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class ladderLogic(object):
    """ The PLC/RTU ladder logic class, this class will be inherited by your ladder diagram,
        and you need to implement initLadderInfo() and runLadderLogic() function.
    """
    def __init__(self, parent, ladderName='TestLadderDiagram'):
        """ To create a simple ladder example, please refer to file <testCase/iec104PlcServerTest.py>
            Args:
                parent (iec104Server): parent need to be a iec104 server obj
                ladderName (str, optional): _description_. Defaults to 'TestLadderDiagram'.
        """
        self.parent = parent # the parent need to be a iec104 server obj
        self.ladderName = ladderName
        self.stationAddr= None
        self.srcPointAddrList = []
        self.srcPointTypeList = []
        self.destPointAddrList = []
        self.destPointTypeList = []
        self.initLadderInfo()

    def initLadderInfo(self):
        """ Init the ladder register, src and dest coils information, this function will 
            be called during the logic init. Please over write this function.
        """
        # This function need to be overwritten. 
        return None

    #-----------------------------------------------------------------------------
    # define all the get and set functions.
    def getLadderName(self):
        return self.ladderName

    def getStationAddr(self):
        return self.stationAddr
    
    def getSrcPointAddrList(self):
        return self.srcPointAddrList

    def getSrcPointTypeList(self):
        return self.srcPointTypeList

    def getDestPointAddrList(self):
        return self.destPointAddrList
    
    def getDestPointTypeList(self):
        return self.destPointTypeList
    
    #-----------------------------------------------------------------------------
    def runLadderLogic(self):
        """ Read the measured point value and changeable step value from the parent IEC104 server, 
            and update the measured point value. 
        """
        # This function need to be overwritten. 
        return None 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class iec104Client(object):
    """ IEC104 client class for the communication with the server."""

    def __init__(self, serverIp, port=DEF_60870_5_104_PORT):
        """ Example to init the client: iec104Comm.iec104Client('127.0.0.1', port=2404)
            Args:
                serverIp (str): server ip address.
                port (int, optional): iec104 port number. Defaults to DEF_60870_5_104_PORT(2404).
        """
        self.serverIP = serverIp
        self.serverPort = port
        self.client = c104.Client()
        self.connection = self.client.add_connection(ip=self.serverIP, port=self.serverPort, init=c104.Init.ALL)
        self.connection.on_unexpected_message(callable=self._unexpectedMsgHandler)
        self.stationAddrDict = OrderedDict()
        self.terminate = False
        print("iec104Client init finished.")

    #-----------------------------------------------------------------------------
    def _unexpectedMsgHandler(self, connection: c104.Connection, message: c104.IncomingMessage, cause: c104.Umc) -> None:
        """ Handle the unexpected message from the server."""
        if cause == c104.Umc.MISMATCHED_TYPE_ID :
            station = connection.get_station(message.common_address)
            if station:
                point = station.get_point(message.io_address)
                if point:
                    print("CL] <-in-- CONFLICT | SERVER CA {0} reports IOA {1} type as {2}, but is already registered as {3}".format(message.common_address, message.io_address, message.type, point.type))
                    return
        print("CL] <-in-- REJECTED | {1} from SERVER CA {0}".format(message.common_address, cause))

    #-----------------------------------------------------------------------------
    def addStation(self, stationAddr):
        """ Add a new local station to the client.
            Args:
                stationAddr (int): station memory address in range [1, 65534].
            Returns:
                _type_: None if the address existed, true if added successfully, false 
                    if the address is out of range.
        """
        stationAddr = int(stationAddr)
        if 1 <= stationAddr <= 65534:
            if stationAddr in self.stationAddrDict.keys():
                print('Station address %s already exist!' %str(stationAddr))
                return None
            else:
                self.stationAddrDict[stationAddr] = []
                self.connection.add_station(common_address=stationAddr)
                return True
        print('Station address %s is out of range!' %str(stationAddr))
        return False

    #-----------------------------------------------------------------------------
    def addPoint(self, stationAddr, pointAddr, pointType=C_STEP_TYPE):
        """ Add a new point to the exist station in the client local station.
            Args:
                stationAddr (int): the station comm address in the station in range 1-65534.
                pointAddr (int): the common address in the station in range between 0 and 16777215.
                pointType (_type_, optional): Defaults to c104.Type.C_STEP_TYPE(c104.Step.LOWER).
            Returns:
                bool: None if the point existed, true if added successfully, false if the pointAddr 
                address not exist is out of range.
        """
        if pointAddr < 0 or pointAddr > 16777215: return False 
        if stationAddr in self.stationAddrDict.keys():
            if pointAddr in self.stationAddrDict[stationAddr]:
                print('Point address %s already exist!' %str(pointAddr))
                return None
            else:
                self.stationAddrDict[stationAddr].append(pointAddr)
                station = self.connection.get_station(common_address=stationAddr)
                station.add_point(io_address=pointAddr, type=pointType)
                return True
        return False
    #-----------------------------------------------------------------------------
    # define all the get and set function.
    def getStationsAddr(self):
        """ Return the configured station address list."""
        return self.stationAddrDict.keys()

    def getStationsAddrDict(self):
        """ Return the configured station address dictionary."""
        return self.stationAddrDict

    def getStation(self, commonAddr):
        """ Return the c104 station obj based on input memory address, return None if 
            the address is not exist.
        """
        commonAddr = int(commonAddr)
        if commonAddr in self.stationAddrDict.keys():
            return self.connection.get_station(common_address=commonAddr)
        return None

    def getPoint(self, stationAddr, pointAddr):
        """ Return the c104 point obj based on input station and io address, return None
            if the station or io address is not in the station dict.
        """
        stationAddr = int(stationAddr)
        pointAddr = int(pointAddr)
        if stationAddr in self.stationAddrDict.keys():
            if pointAddr in self.stationAddrDict[stationAddr]:
                station = self.connection.get_station(common_address=stationAddr)
                return station.get_point(io_address=pointAddr)
        return None     

    def getServerPointValue(self, stationAddr, pointAddr):
        """ Send read request to the server to synchronize the point value, return 
            the point value if the point exist else None 
        """
        point = self.getPoint(stationAddr, pointAddr)
        if point:
            try:
                point.read()
                time.sleep(0.005) # wait 50ms for the server to response.
            except Exception as err:
                print(err)
            val = point.value
            return val
        return None

    def setServerPointStepValue(self, stationAddr, pointAddr, value):
        """ Change the local point's step value and synchronize to the server with 
            transmit request.
        """
        point = self.getPoint(stationAddr, pointAddr)
        if point:
            if point.type == C_STEP_TYPE:
                point.value = value
                return point.transmit(cause=c104.Cot.ACTIVATION)
            else:
                print('Point type %s is not transmittable!' %str(point.type))
                return False
        return False

    #-----------------------------------------------------------------------------
    def startConnection(self, retryTime=1):
        """ Start the client connection to the server."""
        self.client.start()
        while self.connection.state != c104.ConnectionState.OPEN:
            print("Error: IEC104 client can not connect to the server: %s" %str(self.serverIP))
            time.sleep(retryTime)
            print("Try to reconnect...")
        print("INFO: IEC104 client connected to the server")   

    def stopConnection(self):
        self.terminate = True
        self.client.stop()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class iec104Server(object):
    """ IEC104 server class for host the PLC or RTU data and provide to clients."""

    def __init__(self, ip=DEF_HOST_IP, port=DEF_60870_5_104_PORT):
        """ Init example : server = iec104Comm.iec104Server(ip="0.0.0.0", port=2404)
            Args:
                ip (str, optional): either localhost or 0.0.0.0. Defaults to DEF_HOST_IP.
                port (int, optional): iec104 port number. Defaults to DEF_60870_5_104_PORT.
        """
        self.hostIP = ip
        self.hostPort = port
        self.server = c104.Server(ip=self.hostIP, port=self.hostPort)
        self.stationAddrDict = OrderedDict()
        self.terminate = False
        print("iec104Server init finished.")

    #-----------------------------------------------------------------------------
    def addStation(self, stationAddr):
        """ Add a new station to the server.
            Args:
                stationAddr (int): the station comm address in range 1-65534.
            Returns:
                bool/None: None if the address existed, true if added successfully, false 
                    if the address is out of range.
        """
        stationAddr = int(stationAddr)
        if 1 <= stationAddr <= 65534:
            if stationAddr in self.stationAddrDict.keys():
                print('WARN: Station address %s already exist!' %str(stationAddr))
                return None
            else:
                self.stationAddrDict[stationAddr] = []
                self.server.add_station(common_address=stationAddr)
                return True
        print('ERR: Station address %s is out of range!' %str(stationAddr))
        return False

    #-----------------------------------------------------------------------------
    def addPoint(self, stationAddr, pointAddr, pointType=C_STEP_TYPE):
        """ Add a new point to the existed station in the server.
            Args:
                stationAddr (int): the station comm address in range 1-65534.
                pointAddr (int): the io address in the station in range between 0 and 16777215.
                pointType (_type_, optional): Defaults to C_STEP_TYPE(bool true).
            Returns:
                bool/None: None if the point existed, true if added successfully, false if the pointAddr 
                address not exist is out of range.
        """
        if stationAddr in self.stationAddrDict.keys():
            if pointAddr in self.stationAddrDict[stationAddr]:
                print('WARN: Point address %s already exist!' % str(pointAddr))
                return None
            else:
                self.stationAddrDict[stationAddr].append(pointAddr)
                station = self.server.get_station(common_address=stationAddr)
                station.add_point(io_address=pointAddr, type=pointType)
                return True
        print('ERR: Target station address %s not exist!' % str(stationAddr))
        return False

    #-----------------------------------------------------------------------------
    # define all the get and set function.
    def getServerObj(self):
        """ Return the c104 server object."""
        return self.server
    
    def getStationsAddr(self):
        """ Return the configured station address list."""
        return self.stationAddrDict.keys()

    def getStationsAddrDict(self):
        """ Return the configured station address list."""
        return self.stationAddrDict

    def getStation(self, commonAddr):
        """ Return the c104 station obj based on input memory address, return None if 
            the address is not exist.
        """
        commonAddr = int(commonAddr)
        if commonAddr in self.stationAddrDict.keys():
            return self.server.get_station(common_address=commonAddr)
        return None

    def getPoint(self, stationAddr, pointAddr):
        """ Return the c104 point obj based on input station and io address, return None
            if the station or io address is not in the station dict.
        """
        stationAddr = int(stationAddr)
        pointAddr = int(pointAddr)
        if stationAddr in self.stationAddrDict.keys():
            if pointAddr in self.stationAddrDict[stationAddr]:
                station = self.server.get_station(common_address=stationAddr)
                return station.get_point(io_address=pointAddr)
        return None
        
    def getPointVal(self, stationAddr, pointAddr):
        """ Return the point value based on input station and io address, return None if 
            the station or io address is not in the station address dict.
        """
        point = self.getPoint(stationAddr, pointAddr)
        return point.value if point else None 
            
    def setPointVal(self, stationAddr, pointAddr, value, showInfo=False):
        """ Set a measured point value based on input station and io address, return None if
            the station or io address is not in the station address dict.
        """
        point = self.getPoint(stationAddr, pointAddr)
        if point:
            if showInfo: print("INFO: set point value from %s to %s" %(str(point.value), str(value)))
            point.value = value # only the measured point can be set.
            return True
        return False
    
    #-----------------------------------------------------------------------------
    def startServer(self):
        print("Start the 60870-5-104 server...")
        self.server.start()
        while not self.terminate:
            if not self.server.has_active_connections:
                print("INFO: Waiting for IEC 104 client connection.")
                time.sleep(1)
        print("Server stop.")
        self.server.stop()

    def stopServer(self):
        self.terminate = True
        self.server.stop()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    server = iec104Server()
    server.addStation(1)
    server.addPoint(1, 1)
    server.addPoint(1, 2)
    server.addPoint(1, 3)
    server.addPoint(1, 4)
    server.addPoint(1, 5)
    server.addPoint(1, 6)
    server.startServer()

if __name__ == "__main__":
    # c104.set_debug_mode(c104.Debug.Server|c104.Debug.Point|c104.Debug.Callback)
    main()

