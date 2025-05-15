#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcSimulatorTrain.py
#
# Purpose:     A simple plc simulation module to connect and control the real-world 
#              emulator via UDP (to simulate the electric signals change) and handle
#              SCADA system Modbus TCP request.
#              - This module will simulate 2 PLCs connected under master-slave mode
#              to sense the train speed and control the trains power
#               
# Author:      Yuancheng Liu
#
# Created:     2023/05/29
# Version:     v0.1.2
# Copyright:   Copyright 2023 (c)LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" 
    Program design:
        We want to create a PLC simulator which can simulate a PLC set (Master[slot-0], 
        Slave[slot-1]) with three 16-in 8-out PLCs. The PLC sets will take 10 input 
        speed sensor and provide 10 power output signal to implement the railway trains 
        control system.
"""

from collections import OrderedDict

import plcSimGlobalTrain as gv
import modbusTcpCom
import plcSimulator

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class onlyCoilLadderLogic(modbusTcpCom.ladderLogic):
    """ Individual holder register and coil usage, no executable ladder logic 
        between them.
    """
    def __init__(self, parent, ladderName) -> None:
        super().__init__(parent, ladderName=ladderName)

    def initLadderInfo(self):
        self.holdingRegsInfo['address'] = 0
        self.holdingRegsInfo['offset'] = 10
        self.srcCoilsInfo['address'] = None
        self.srcCoilsInfo['offset'] = None
        self.destCoilsInfo['address'] = 0
        self.destCoilsInfo['offset'] = 11
        # For total 10 holding registers connected addresses
        # address: 0 - 3: weline trains speed.
        # address: 4 - 6: nsline trains speed.
        # address: 7 - 9: ccline trains speed.

#-----------------------------------------------------------------------------
    def runLadderLogic(self, regsList, coilList=None):
        print(regsList)
        return None
        
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class trainPowerPlcSet(plcSimulator.plcSimuInterface):
    """ A PlC simulator to provide below functions: 
        - Create a ModbusTCP service running in sub-thread to handle the SCADA system's 
            ModbusTCP requirement.
        - Connect to the real world emulator to fetch the sensor state and calculate 
            the output coils state based on the ladder logic. 
        - Send the signal setup request to the real world emulator to change the signal.
    """
    def __init__(self, parent, plcID, addressInfoDict, ladderObj, updateInt=0.6):
        super().__init__(parent, plcID, addressInfoDict, ladderObj,
                        updateInt=updateInt)

    def _initInputState(self):
        self.regsAddrs = (0, 10)
        self.regSRWfetchKey = gv.gRealWorldKey
        self.regs2RWmap = OrderedDict()
        self.regs2RWmap['weline'] = (0, 4)
        self.regs2RWmap['nsline'] = (4, 7)
        self.regs2RWmap['ccline'] = (7, 10)
        self.regsStateRW = OrderedDict()
        self.regsStateRW['weline'] = [0]*4
        self.regsStateRW['nsline'] = [0]*3
        self.regsStateRW['ccline'] = [0]*3

    def _initCoilState(self):
        self.coilsAddrs = (0, 11)
        self.coilsRWSetKey = gv.gRealWorldKey
        self.coils2RWMap = OrderedDict()
        self.coils2RWMap['weline'] = (0, 4)
        self.coils2RWMap['nsline'] = (4, 7)
        self.coils2RWMap['ccline'] = (7, 10)
        self.coils2RWMap['config'] = (10, 11)
        self.coilStateRW = OrderedDict()
        self.coilStateRW['weline']  = [False]*4
        self.coilStateRW['nsline']  = [False]*3 
        self.coilStateRW['ccline']  = [False]*3
        self.coilStateRW['config']  = [True]

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    gv.gDebugPrint("Start Init the PLC: %s" %str(gv.PLC_NAME), logType=gv.LOG_INFO)
    gv.iLadderLogic = onlyCoilLadderLogic(None, ladderName='only_coil_control')
    addressInfoDict = {
        'hostaddress': gv.gModBusIP,
        'realworld':gv.gRealWorldIP, 
        'allowread':gv.ALLOW_R_L,
        'allowwrite': gv.ALLOW_W_L
    }
    plc = trainPowerPlcSet(None, gv.PLC_NAME, addressInfoDict, gv.iLadderLogic)
    plc.run()

if __name__ == "__main__":
    main()
