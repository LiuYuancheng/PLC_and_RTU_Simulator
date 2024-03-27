import os, sys

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'S7Comm_RTU_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir):
    sys.path.insert(0, gLibDir)

#-----------------------------------------------------------------------------
import time
import snap7Comm
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE

#-----------------------------------------------------------------------------
print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(__file__) if os.path.dirname(__file__) else os.getcwd()
print("Current source code location : %s" % dirpath)
APP_NAME = ('OpenAI', 'threats2Mitre')

libpath = os.path.join(gLibDir, 'snap7.dll')
print("dll path: %s" %str(libpath))

client = snap7Comm.s7CommClient('127.0.0.1', rtuPort=102, snapLibPath=libpath)

client.setAddressVal(1, 0, True, dataType=BOOL_TYPE)
time.sleep(1)
client.setAddressVal(1, 2, 5, dataType=INT_TYPE)
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

client.setAddressVal(2, 4, 5.0, dataType=REAL_TYPE)
time.sleep(1)

print(client.readAddressVal(2, 0, dataType=REAL_TYPE))
time.sleep(1)