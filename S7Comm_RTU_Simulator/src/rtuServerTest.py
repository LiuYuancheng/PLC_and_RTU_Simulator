import os
import snap7Comm
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(__file__) if os.path.dirname(__file__) else os.getcwd()
print("Current source code location : %s" % dirpath)
APP_NAME = ('OpenAI', 'threats2Mitre')

libpath = os.path.join(DIR_PATH, 'snap7.dll')
print("dll path: %s" %str(libpath))
server = snap7Comm.s7commServer(snapLibPath=libpath)

server.initNewMemoryAddr(1, [0,2,4], [BOOL_TYPE, INT_TYPE, REAL_TYPE] )

server.initNewMemoryAddr(2, [0, 4], [REAL_TYPE, REAL_TYPE] )

server.setMemoryVal(1, 0, True)
server.setMemoryVal(1, 2, 10)
server.setMemoryVal(1, 4, 3.141592)

server.setMemoryVal(2, 0, 1.23)
server.setMemoryVal(2, 4, 4.56)

server.startService()



