import os
import time
import snap7Comm
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(__file__) if os.path.dirname(__file__) else os.getcwd()
print("Current source code location : %s" % dirpath)
APP_NAME = ('OpenAI', 'threats2Mitre')

libpath = os.path.join(DIR_PATH, 'snap7.dll')

client = snap7Comm.s7CommClient('127.0.0.1', rtuPort=102, snapLibPath=libpath)

client.setAddressVal(1, 0, True, dataType=BOOL_TYPE)
time.sleep(1)
print(client.readAddressVal(1, 0, dataType=BOOL_TYPE))
time.sleep(1)
print(client.readAddressVal(1, 2, dataType=INT_TYPE))
time.sleep(1)
print(client.readAddressVal(1, 4, dataType=REAL_TYPE))
time.sleep(1)

print(client.readAddressVal(2, 0, dataType=REAL_TYPE))
time.sleep(1)

print(client.readAddressVal(2, 4, dataType=REAL_TYPE))
time.sleep(1)