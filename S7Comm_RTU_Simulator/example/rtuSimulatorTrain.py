#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcSimulatorTrain.py
#
# Purpose:     A simple plc simulation module to connect and control the real-world 
#              emulator via UDP (to simulate the eletrical signals change) and handle
#              SCADA system Modbus TCP request.
#              - This module will simulate 2 PLCs connected under master-slave mode
#              to sense the train speed and control the trains power
#               
# Author:      Yuancheng Liu
#
# Created:     2023/05/29
# Version:     v0.1.2
# Copyright:   Copyright (c) 2023 Singapore National Cybersecurity R&D Lab LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" 
    Program design:
        We want to create a PLC simulator which can simulate a PLC set (Master[slot-0], 
        Slave[slot-1]) with thress 16-in 8-out PLCs. The PLC sets will take 10 input 
        speed sensor and provide 10 power output signal to implement the railway trains 
        control system.
"""

from collections import OrderedDict

import rtuSimGlobalTrain as gv
import snap7Comm
import rtuSimulator
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE
        
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class trainPowerRtu(rtuSimulator.rtuSimuInterface):
    """ A PlC simulator to provide below functions: 
        - Create a modbus service running in subthread to handle the SCADA system's 
            modbus requirment.
        - Connect to the real world emulator to fetch the sensor state and calculate 
            the output coils state based on the ladder logic. 
        - Send the signal setup request to the real world emulator to change the signal.
    """
    def __init__(self, parent, rtuID, addressInfoDict, dllPath=None, updateInt=0.6):
        super().__init__(parent, rtuID, addressInfoDict, dllPath=dllPath, updateInt=updateInt)

    def _initRealWorldConnectionParm(self):
        self.regSRWfetchKey = gv.gRealWorldKey


    def _initMemoryAddrs(self):
        """ overwrite this function to add the memory init address setting here
            example:
        """
        self.regsStateRW = OrderedDict()
        self.regsStateRW['weline'] = [1,2,3,4]
        self.regsStateRW['nsline'] = [5,6,7]
        self.regsStateRW['ccline'] = [8,9,10]
        s7commServer = self.s7Service.getS7ServerRef()
        # memory for weline trains
        s7commServer.initNewMemoryAddr(1, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(2, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(3, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(4, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        # memory for nsline trains
        s7commServer.initNewMemoryAddr(5, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(6, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(7, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        # memory for ccline trains
        s7commServer.initNewMemoryAddr(8, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(9, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(10, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])

    def _initMemoryDefaultVals(self):
        pass

    def _initLadderHandler(self):
        self.s7Service.setLadderHandler(None)

    def _updateMemory(self, result):
        """ overwrite this function to update the memory state based on the realworld feed back
        """
        #print(result)
        s7commServer = self.s7Service.getS7ServerRef()
        for key, value in self.regsStateRW.items():
            for idx, rstData in enumerate(result[key]):
                memoryIdx = value[idx]
                s7commServer.setMemoryVal(memoryIdx, 0, rstData[0])
                s7commServer.setMemoryVal(memoryIdx, 2, rstData[1])
                s7commServer.setMemoryVal(memoryIdx, 4, rstData[2])
                s7commServer.setMemoryVal(memoryIdx, 6, rstData[3])

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    gv.gDebugPrint("Start Init the TRU: %s" %str(gv.RTU_NAME), logType=gv.LOG_INFO)
    addressInfoDict = {
        'hostaddress': gv.gS7serverIP,
        'realworld':gv.gRealWorldIP, 
    }
    rtu = trainPowerRtu(None, gv.RTU_NAME, addressInfoDict, dllPath=gv.gS7snapDllPath, updateInt=gv.gInterval)
    rtu.run()

if __name__ == "__main__":
    main()
