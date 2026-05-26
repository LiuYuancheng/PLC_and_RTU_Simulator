#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        mqTTCommTest.py
#
# Purpose:     This module is the testcase program for the IEC-20922 MQTT comm 
#              library <mqttComm.py>, it will start a broker in sub-thread and 
#              multiple clients to test the data read and transmit.
#
# Author:      Yuancheng Liu
#
# Created:     2026/05/25
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

"""

MQTT Broker 
                        ┌──────────────────────────┐
                        │  BrokerState             │
                        │  parameters{}            │
                        │  subscriptions{}         │
                        │                          ├──────────── Client B
   Client A ────────────┤  per-client thread each  ├──────────── Client N
                        └──────────────────────────┘

"""

import time
import threading
import mqttComm


def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class TestBroker(mqttComm.MQTTBroker):
    """ Test broker class, it will start a broker in sub-thread and multiple clients to test the data read and transmit. """

    def __init__(self, brokerName='testBroker', brokerPort=1883):
        super().__init__()
        self.mqttClients = []

    def executeLogic(self):
        """ The fan control logic. """
        print("> execute the control logic")
        temp = float(self.getParmVal('temperature'))
        mode = self.getParmVal('mode')
        if mode == 'auto':
            if temp > 50:
                self.setParmVal('fan', 'on')
                self.setParmVal('fanSpeed', '50')
            else:
                self.setParmVal('fan', 'off')
                self.setParmVal('fanSpeed', '0')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MQTTbrokerThread(threading.Thread):
    """ MQTT broker thread class. """
    def __init__(self):
        threading.Thread.__init__(self)
        self.mqttBroker = TestBroker()
        self.mqttBroker.addParam('temperature', '25.0')
        self.mqttBroker.addParam('mode', 'manual')
        self.mqttBroker.addParam('fan', 'off')
        self.mqttBroker.addParam('fanSpeed', '0')

    def run(self):
        print("Starting MQTT broker thread.")
        self.mqttBroker.run()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    """ Main function. """
    index = 0
    print("\nTest-%d Init the MQTT Broker Thread." % index)
    brokerThread = MQTTbrokerThread()
    brokerThread.start()
    time.sleep(1)

    index += 1
    print("\nTest-%d Init the MQTT client-A connection" % index)
    clientA = mqttComm.MQTTClient('clientA', '127.0.0.1', port=1883)
    clientA.connect()
    time.sleep(0.5)

    index += 1
    print("\nTest-%d Init the MQTT client-B connection" % index)
    clientB = mqttComm.MQTTClient('clientB', '127.0.0.1', port=1883)
    clientB.connect()
    time.sleep(0.5)

    index += 1
    print("\nTest-%d Change the temperature value" % index)
    clientA.setParmVal('temperature', '60.0')
    time.sleep(0.3)
    val1 = clientB.getParmVal('temperature')
    showTestResult('60.0', val1, "client read point value3")

    index += 1
    print("\nTest-%d Change the mode value" % index)
    clientA.setParmVal('mode', 'auto')
    time.sleep(0.3)
    val2 = clientB.getParmVal('mode')
    showTestResult('auto', val2, "client read point value3")
    val3 = clientB.getParmVal('fan')
    showTestResult('on', val3, "client read point value3")
    val4 = clientB.getParmVal('fanSpeed')
    showTestResult('50', val4, "client read point value3")


    clientA.disconnect()
    clientB.disconnect()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()