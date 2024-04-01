#-----------------------------------------------------------------------------
# Name:        plcClientTest.py
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
import time
import modbusTcpCom

hostIp = '127.0.0.1'
hostPort = 502

client = modbusTcpCom.modbusTcpClient(hostIp)

print('TestCase 0: test connection')

while not client.checkConn():
    print('try connect to the PLC')
    print(client.getCoilsBits(0, 4))
    time.sleep(0.5)

print('TestCase 1: read the coils: ')
result = client.getCoilsBits(0, 4)
if result == [True, True, False, False]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

print('TestCase 2: read the holding registers')
result = client.getHoldingRegs(0, 4)
if result == [0, 0, 1, 1]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

print('TestCase 3: Set the holding registers')
client.setHoldingRegs(1, 1)
time.sleep(0.5)
result = client.getHoldingRegs(0, 4)
if result == [0, 1, 1, 1]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

print('TestCase 4: check auto update coils function')
result = client.getCoilsBits(0, 4)
if result == [True, False, False, False]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

print('TestCase 5: Set the coils')
client.setCoilsBit(1, 1)
time.sleep(0.5)
result = client.getCoilsBits(0, 4)
if result == [True, True, False, False]: 
    print(" - test pass")
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

client.close()