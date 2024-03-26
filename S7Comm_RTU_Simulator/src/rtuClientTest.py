import os
import snap7Comm


print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(__file__) if os.path.dirname(__file__) else os.getcwd()
print("Current source code location : %s" % dirpath)
APP_NAME = ('OpenAI', 'threats2Mitre')

libpath = os.path.join(DIR_PATH, 'snap7.dll')

server = snap7Comm.s7CommClient('127.0.0.1', rtuPort=102, snapLibPath=libpath)
