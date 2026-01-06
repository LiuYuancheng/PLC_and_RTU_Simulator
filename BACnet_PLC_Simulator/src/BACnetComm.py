#!/usr/bin/env python
"""
Simple BACnet Server Example
Hosts multiple analog value objects that can be read/written
"""
import sys
from bacpypes.core import run
from bacpypes.primitivedata import Real
from bacpypes.object import AnalogValueObject, register_object_type
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject

from bacpypes.core import run, stop
from bacpypes.pdu import Address
from bacpypes.app import BIPSimpleApplication
from bacpypes.primitivedata import Real
from bacpypes.apdu import ReadPropertyRequest, WritePropertyRequest
from bacpypes.constructeddata import Any
from bacpypes.iocb import IOCB
from threading import Thread, Event
import time


DEF_SERVER_IP = "0.0.0.0"
DEF_SERVER_PORT = 47808

DEF_CLIENT_IP = "0.0.0.0/24"  # Change to your client machine's IP
DEF_CLIENT_PORT = 47809

DEF_ANALOG_VALUE_TYPE = 'analogValue'
DEF_PROPERTY_IDENTIFIER = 'presentValue'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class BACnetServer(object):

    def __init__(self, deviceID, deviceName, ipaddr=DEF_SERVER_IP, port=DEF_SERVER_PORT):
        self.deviceID = int(deviceID)
        self.deviceName = str(deviceName)
        self.deviceIP = "%s:%s" % (str(ipaddr), str(port))
        self.deviceInfo = LocalDeviceObject(
            objectName=self.deviceName,
            objectIdentifier=self.deviceID,
            maxApduLengthAccepted=1024,
            segmentationSupported="segmentedBoth",
            vendorIdentifier=15,
        )
        self.application = BIPSimpleApplication(self.deviceInfo, self.deviceIP)
        print("BACnetServer: Start device server with ip %s" % self.deviceIP)
        self.analogObjDict = {} # init the analog object dict

    #-----------------------------------------------------------------------------
    def addAnalogObject(self, objName, objID, objValue, objDesc, objUnit):
        analogObj = AnalogValueObject(
            objectIdentifier=("analogValue", objID),
            objectName=objName,
            presentValue=objValue,
            description=objDesc,
            units=objUnit,
            outOfService=True
        )
        self.application.add_object(analogObj)
        self.analogObjDict[objName] = analogObj
        print("BACnetServer: Add analog object %s" % objName)

    #-----------------------------------------------------------------------------
    # define all the get() method here:
    def getServerInfo(self):
        return self.deviceID, self.deviceName, self.deviceIP
    
    def getObjNames(self):
        return self.analogObjDict.keys()
    
    def getObjDict(self):
        return self.addAnalogObject

    def getObjValue(self, objName):
        if objName in self.analogObjDict:
            return self.analogObjDict[objName].presentValue
        else:
            print("getObjValue() Error: the object name %s is not exist" %str(objName))
            return None
    
    #-----------------------------------------------------------------------------
    def setObjValue(self, objName, objValue):
        if objName in self.analogObjDict:
            self.analogObjDict[objName].presentValue = objValue
            return True
        else:
            print("setObjValue() Error: the object name %s is not exist" %str(objName))

    #-----------------------------------------------------------------------------
    def runServer(self):
        print("BACnetServer: Start server ...")
        run()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class BACnetClient(object):

    def __init__(self, deviceID, deviceName, serverIP, serverPort, 
                 ipaddr=DEF_CLIENT_IP, port=DEF_CLIENT_PORT):
        self.deviceID = int(deviceID)
        self.deviceName = str(deviceName)
        self.serverIP = "%s:%s" % (str(serverIP), str(serverPort))
        self.clientIP = "%s:%s" % (str(ipaddr), str(port))
        self.device = LocalDeviceObject(
            objectName=self.deviceName ,
            objectIdentifier=self.deviceID,
            maxApduLengthAccepted=1024,
            segmentationSupported="segmentedBoth",
            vendorIdentifier=15,
        )
        self.application = BIPSimpleApplication(self.device, self.clientIP)
        # Start the BACpypes core in a separate thread
        self.bacnetThread = Thread(target=run, daemon=True)
        self.bacnetThread.start()
        time.sleep(1)
        # Response storage
        self.responseValue = None
        self.responseEvent = Event()

    #-----------------------------------------------------------------------------
    def responseCallback(self, iocb):
        """Callback for handling responses"""
        if iocb.ioError:
            print("responseCallback() iocb Error: %s" %str(iocb.ioError))
            self.responseValue = None
        elif iocb.ioResponse:
            # Check for SimpleAckPDU (write response)
            if not hasattr(iocb.ioResponse, 'propertyValue'):
                self.responseValue = "success"
            else: # Read response
                try:
                    self.responseValue = iocb.ioResponse.propertyValue.cast_out(Real)
                except Exception as e:
                    print("responseCallback() Value extraction error: %s" %str(e))
                    self.responseValue = None
        else:
            print("responseCallback() Error: No response received")
            self.responseValue = None
        self.responseEvent.set()

    #-----------------------------------------------------------------------------
    def readObjProperty(self, serverAddress, objectInstance, 
                        objectType=DEF_ANALOG_VALUE_TYPE, 
                        propertyIdentifier = DEF_PROPERTY_IDENTIFIER):
        """Read a property from a BACnet object"""
        try:
            # Reset response
            self.responseValue = None
            self.responseEvent.clear()
            # Build the request
            request = ReadPropertyRequest(
                objectIdentifier=(objectType, objectInstance),
                propertyIdentifier=propertyIdentifier
            )
            if serverAddress is None: serverAddress = self.serverIP
            print("Send request to server %s ..." %str(serverAddress))
            request.pduDestination = Address(serverAddress)
            # Make an IOCB with callback
            iocb = IOCB(request)
            iocb.add_callback(self.responseCallback)
            # Submit the request to the server.
            self.application.request_io(iocb)
            # Wait for response (with timeout)
            if self.responseEvent.wait(timeout=10.0): return self.responseValue
            print("readObjProperty() Error: Timeout waiting for response")
            return None
        except Exception as e:
            print("readObjProperty() Read error: %s" %str(e))
            return None

    #-----------------------------------------------------------------------------
    def write_property(self, serverAddress, objectInstance, value, objectType=DEF_ANALOG_VALUE_TYPE, 
                       propertyIdentifier = DEF_PROPERTY_IDENTIFIER):
        #try:
            # Reset response
        self.responseValue = None
        self.responseEvent.clear()
        # Build the request
        request = WritePropertyRequest(
            objectIdentifier=(objectType, objectInstance),
            propertyIdentifier=propertyIdentifier,
            priority=16 
        )
        if serverAddress is not None: serverAddress = self.serverIP
        request.pduDestination = Address(serverAddress)

        # Convert the value to the appropriate type
        request.propertyValue = Any()
        request.propertyValue.cast_in(Real(value))

        # Make an IOCB with callback
        iocb = IOCB(request)
        iocb.add_callback(self.responseCallback)
        
        # Submit the request
        self.application.request_io(iocb)

        # Wait for response (with timeout)
        if self.responseEvent.wait(timeout=10.0):
            if self.responseValue == "success":
                print(f"   Successfully wrote {value} to {objectType}:{objectInstance}")
                return True
            else:
                return False
        else:
            print("   Timeout waiting for write confirmation")
            return False

        #except Exception as e:
        #    print("write_property() Write error: %s" %str(e))
        #    return None

    #-----------------------------------------------------------------------------
    def cleanup(self):
        """Cleanup resources"""
        stop()
        if self.bacnetThread.is_alive():self.bacnetThread.join(timeout=2)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    server = BACnetServer(123456, "TestDevice")
    analog_values = [
            {
                "objectName": "Temperature",
                "objectIdentifier": ("analogValue", 1),
                "presentValue": 22.5,
                "description": "Room Temperature",
                "units": "degreesCelsius"
            },
            {
                "objectName": "Humidity",
                "objectIdentifier": ("analogValue", 2),
                "presentValue": 45.0,
                "description": "Room Humidity",
                "units": "percent"
            },
            {
                "objectName": "Pressure",
                "objectIdentifier": ("analogValue", 3),
                "presentValue": 101.3,
                "description": "Atmospheric Pressure",
                "units": "kilopascals"
            },
            {
                "objectName": "SetPoint",
                "objectIdentifier": ("analogValue", 4),
                "presentValue": 24.0,
                "description": "Temperature Setpoint",
                "units": "degreesCelsius"
            }
        ]

    for parameter in analog_values:
        print(parameter)
        server.addAnalogObject(parameter["objectName"], 
                               parameter["objectIdentifier"][1], 
                               parameter["presentValue"], 
                               parameter["description"], 
                               parameter["units"])

    val = server.getObjValue('Temperature')
    print("get the obj value: %s" % str(val))
    server.setObjValue('Temperature', 25.0)
    server.runServer()



if __name__ == "__main__":
    main()
