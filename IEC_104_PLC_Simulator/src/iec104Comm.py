#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        ice104Comm.py
#
# Purpose:     This module will provide the IEC-60870-5-104 client and server 
#              communication API for testing or simulating the data flow connection 
#              between PLC/RTU and SCADA system. The module is implemented based 
#              on python iec104-python lib module: 
#              - Reference: https://github.com/Fraunhofer-FIT-DIEN/iec104-python
#
# Author:      Yuancheng Liu
#
# Created:     2025/04/27
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import time
import c104
from collections import OrderedDict

DEF_60870_5_104_PORT = 2404
DEF_HOST_IP = '0.0.0.0'

IPV4_PATTERN = r'^(\d{1,3}\.){3}\d{1,3}$'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class iec104Client(object):

    def __init__(self, serverIp, port=DEF_60870_5_104_PORT):
        self.serverIP = serverIp
        self.serverPort = port
        self.client = c104.Client()
        self.connection = self.client.add_connection(ip="127.0.0.1", port=2404, init=c104.Init.ALL)
        self.connection.on_unexpected_message(callable=self.con_on_unexpected_message)
        self.stationAddrDict = OrderedDict()
        self.terminate = False

    def startClient(self):
        self.client.start()
        while self.connection.state != c104.ConnectionState.OPEN:
            print("Error: IEC104 client can not connect to the server: %s" %str(self.serverIP))
            time.sleep(1)
            print("Try to reconnect...")
        print("Client Start")   

    def con_on_unexpected_message(self, connection: c104.Connection, message: c104.IncomingMessage, cause: c104.Umc) -> None:
        if cause == c104.Umc.MISMATCHED_TYPE_ID :
            station = connection.get_station(message.common_address)
            if station:
                point = station.get_point(message.io_address)
                if point:
                    print("CL] <-in-- CONFLICT | SERVER CA {0} reports IOA {1} type as {2}, but is already registered as {3}".format(message.common_address, message.io_address, message.type, point.type))
                    return
        print("CL] <-in-- REJECTED | {1} from SERVER CA {0}".format(message.common_address, cause))

    def addStation(self, stationAddr):
        """ Add a new station to the server."""
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

    def getStationsAddr(self):
        """ Return the configured station address list."""
        return self.stationDict.keys()

    def getStation(self, commonAddr):
        """ Return the station object by address."""
        commonAddr = int(commonAddr)
        if commonAddr in self.stationAddrDict.keys():
            return self.connection.get_station(common_address=commonAddr)
        return None

    def addPoint(self, stationAddr, ioAddr, pointType=c104.Type.M_SP_NA_1):
        """ Add a new point to the existed station in the server.
            Args:
                stationAddr (int): the station comm address in the station in range 1-65534.
                commonAddr (int): the common address in the station in range between 0 and 16777215.
                pointType (_type_, optional): Defaults to c104.Type.M_SP_NA_1(bool true).
            Returns:
                _type_: _description_
        """
        if stationAddr in self.stationAddrDict.keys():
            if ioAddr in self.stationAddrDict[stationAddr]:
                print('Point address %s already exist!' %str(ioAddr))
                return None
            else:
                self.stationAddrDict[stationAddr].append(ioAddr)
                station = self.connection.get_station(common_address=stationAddr)
                station.add_point(io_address=ioAddr, type=pointType)
                return True

    def getPoint(self, stationAddr, commonAddr):
        """ Return the point object by address."""
        stationAddr = int(stationAddr)
        commonAddr = int(commonAddr)
        if stationAddr in self.stationAddrDict.keys():
            if commonAddr in self.stationAddrDict[stationAddr]:
                station = self.connection.get_station(common_address=stationAddr)
                return station.get_point(io_address=commonAddr)
        return None     
        
    def readServerPointValue(self, stationAddr, commonAddr):
        point = self.getPoint(stationAddr, commonAddr)
        if point:
            point.read()
            return point.value
        return None
    
    def setServerPointVal(self, stationAddr, commonAddr, value):
        point = self.getPoint(stationAddr, commonAddr)
        if point:
            point.value = value
            return point.transmit(cause=c104.Cot.ACTIVATION)
        return False

    def stopConnection(self):
        self.terminate = True
        self.client.stop()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class iec104Server(object):

    def __init__(self, ip=DEF_HOST_IP, port=DEF_60870_5_104_PORT):
        self.hostIP = ip
        self.hostPort = port
        self.server = c104.Server(ip=self.hostIP, port=self.hostPort)
        self.stationAddrDict = OrderedDict()
        self.terminate = False
        pass

    def getStationsAddr(self):
        """ Return the configured station address list."""
        return self.stationDict.keys()

    def addStation(self, stationAddr):
        """ Add a new station to the server."""
        stationAddr = int(stationAddr)
        if 1 <= stationAddr <= 65534:
            if stationAddr in self.stationAddrDict.keys():
                print('Station address %s already exist!' %str(stationAddr))
                return None
            else:
                self.stationAddrDict[stationAddr] = []
                self.server.add_station(common_address=stationAddr)
                return True
        print('Station address %s is out of range!' %str(stationAddr))
        return False

    def getStation(self, commonAddr):
        """ Return the station object by address."""
        commonAddr = int(commonAddr)
        if commonAddr in self.stationAddrDict.keys():
            return self.server.get_station(common_address=commonAddr)
        return None
    
    def addPoint(self, stationAddr, ioAddr, pointType=c104.Type.M_SP_NA_1):
        """ Add a new point to the existed station in the server.
            Args:
                stationAddr (int): the station comm address in the station in range 1-65534.
                commonAddr (int): the common address in the station in range between 0 and 16777215.
                pointType (_type_, optional): Defaults to c104.Type.M_SP_NA_1(bool true).
            Returns:
                _type_: _description_
        """
        if stationAddr in self.stationAddrDict.keys():
            if ioAddr in self.stationAddrDict[stationAddr]:
                print('Point address %s already exist!' %str(ioAddr))
                return None
            else:
                self.stationAddrDict[stationAddr].append(ioAddr)
                station = self.server.get_station(common_address=stationAddr)
                station.add_point(io_address=ioAddr, type=pointType)
                return True
            
    def getPoint(self, stationAddr, commonAddr):
        """ Return the point object by address."""
        stationAddr = int(stationAddr)
        commonAddr = int(commonAddr)
        if stationAddr in self.stationAddrDict.keys():
            if commonAddr in self.stationAddrDict[stationAddr]:
                station = self.server.get_station(common_address=stationAddr)
                return station.get_point(io_address=commonAddr)
        return None     
        
    def getPointVal(self, stationAddr, commonAddr):
        point = self.getPoint(stationAddr, commonAddr)
        if point:
            return point.value
        return None
    
    def setPointVal(self, stationAddr, commonAddr, value):
        point = self.getPoint(stationAddr, commonAddr)
        if point:
            print(point.value)
            point.value = value
            return True
        return False
    
    def startServer(self):
        print("Start the 60870-5-104 server...")
        self.server.start()
        while not self.terminate:
            if not self.server.has_active_connections:
                print("Waiting for connection")
                time.sleep(1)
        print("Server stop")
        self.server.stop()

    def stopServer(self):
        self.terminate = True
        self.server.stop()


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

