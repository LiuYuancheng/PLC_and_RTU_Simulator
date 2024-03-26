import os
import snap7Comm


print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(__file__) if os.path.dirname(__file__) else os.getcwd()
print("Current source code location : %s" % dirpath)
APP_NAME = ('OpenAI', 'threats2Mitre')

libpath = os.path.join(DIR_PATH, 'snap7.dll')
print("dll path: %s" %str(libpath))
server = snap7Comm.s7commServer(snapLibPath=libpath)
server.startService()

