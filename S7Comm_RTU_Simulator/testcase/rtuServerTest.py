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
import snap7Comm
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE

#-----------------------------------------------------------------------------
libpath = os.path.join(gLibDir, 'snap7.dll')
print("dll path: %s" %str(libpath))

print("Init the server and memory address")
server = snap7Comm.s7commServer(snapLibPath=libpath)
server.initNewMemoryAddr(1, [0, 2, 4], [BOOL_TYPE, INT_TYPE, REAL_TYPE])
server.initNewMemoryAddr(2, [0, 4], [REAL_TYPE, REAL_TYPE])

print("Test set values.")
server.setMemoryVal(1, 0, True)
server.setMemoryVal(1, 2, 10)
server.setMemoryVal(1, 4, 3.141592)

server.setMemoryVal(2, 0, 1.23)
server.setMemoryVal(2, 4, 4.56)

print("Test get values.")
print(server.getMemoryVal(1, 0))
print(server.getMemoryVal(1, 2))
print(server.getMemoryVal(1, 4))

# The auto data handling function.
def handlerS7request(parmList):
    global server
    addr, dataIdx, datalen = parmList
    print("Received data write request: ")
    print("Address: %s " %str(addr))
    print("dataIdx: %s " %str(dataIdx))
    print("datalen: %s" %str(datalen))
    if server:
        print("dataVal: %s" %str(server.getMemoryVal(addr, dataIdx)))
        if addr == 2 and dataIdx == 4:
            server.setMemoryVal(addr, 0, server.getMemoryVal(addr, dataIdx))

print("Server start")
server.startService(eventHandlerFun=handlerS7request)



