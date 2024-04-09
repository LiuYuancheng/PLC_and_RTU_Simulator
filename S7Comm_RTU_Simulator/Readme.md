# S7Comm Remote Terminal Unit Simulator 

**Project Design Purpose**: The main objective of this project is develop a  Python library capable of simulating the OT RTUs (Remote Terminal Units) device which use the Siemens S7Comm protocol. 

This component can simulate both PLC and RTU operations, the design is based on the core operation logic of Siemens Simatic S7-1200 PLC and SIMATIC RTU3000C, respectively. It incorporates S7Comm client and server functionalities, manages PLC/RTU memory, performs ladder logic and RTU logic simulations, and provides interfaces for connecting with real-world emulators.

```
# version:     v0.1.3
# Created:     2024/02/21
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
```

[TOC]

------

### Introduction 

RTUs are specialized devices used primarily for remote monitoring and control of distributed assets in industrial applications, such as in oil and gas pipelines, water distribution systems, and electrical substations. They typically collect data from sensors and equipment in remote locations and transmit it to a central control system for monitoring and analysis. This library provide the software simulation solution to all user can build their customized RTU by using the VM, physical server or Raspberry PI, then integrated the emulation App as a bridge to link the OT level-0 and level-2/3 network.

The program module workflow diagram is shown below:

![](../doc/img/rtuWorkflow.png)

This lib provide two main modules with below components: rtuSimulator and snap7Comm

#### Module 1: rtuSimulator  

A simple RTU simulation lib module to connect and control the real-world emulator via UDP (to simulate the electrical signals changes) and handle SCADA system S7Comm request. The module contents three components: 

- `RealWorldConnector`: A UDP/TCP client to fetch and parse the data from the real world simulation app and update the real world components. (simulate fetch electrical signal from sensor and change the switch state)
- `s7CommService`: A sub-threading service class to run the S7Comm server parallel with the main program thread. 
- `rtuSimuInterface`: A interface class with the basic function for the user to inherit it to build their RTU module.

#### Module 2: snap7Comm

This module will provide a packaged Siemens S7Comm client and server communication API for testing or simulating the data connection flow between PLC/RTU and SCADA system. The module is implemented based on python-snap7 lib module: https://github.com/gijzelaerr/python-snap7. Three components will be provided in this module:

- `ladder logic interface`: An interface class hold the ladder logic calculation algorithm. The ladder logic obj class will inherit this interface class by overwritten the init() and runLadderLogic() function by adding the memory info and the detail control.
- `S7CommClient`: S7Comm client module to read src memory val or write target val from/to the target PLC/RTU. 
- `S7CommServer`: S7Comm  server module will be used by RTU/PLC module to handle the S7Comm data read/set request.



------

### Program Setup

Follow the below configuration steps before run the program.

##### Development Environment

- python 3.7.2rc2+ 64bit [Windows11]

##### Additional Lib/Software Need

- python-snap7: https://python-snap7.readthedocs.io/en/latest/, install: `pip install python-snap7`

##### Hardware Needed : None

##### Program Files List 

| Program File                 | Execution Env | Description                                                  |
| ---------------------------- | ------------- | ------------------------------------------------------------ |
| src/rtuSimulator.py          | python 3.7 +  | The main RTU simulator lib provides the simulator interface, Real world Emulation App connector and the S7Comm sub-threading service. |
| src/snap7.dll                | Windows-OS    | The Windows OS platform Snap7 lib dll file.                  |
| src/snap7Comm.py             | python 3.7 +  | The S7Comm protocol handling lib provides the S7Comm client, server and the RTU internal logic execution interface. |
| src/udpCom.py                | python 3.7 +  | UDP communication handling library module.                   |
| testCase/rtuClientTest.py    | python 3.7 +  | The test case of the `<snap7Comm.py>` lib module to test as a HMI to connect to a RTU simulator. |
| testCase/rtuServerTest.py    | python 3.7 +  | The test case of the `<snap7Comm.py>` lib module to test as a RTU to handle the HMI's connection request. |
| example/rtuSimulatorTrain.py | python 3.7 +  | An example of how to inherit the rtuSimulator interface to build a customized  RTU application. |



------

### Program Usage

##### Run the Test Case

Run rtuServerTest.py: 

```
python rtuServerTest.py
```

Run rtuClientTest.py:

```
python rtuClientTest.py
```

##### Build a Customized RTU

To build a Customized RTU please follow the example `rtuSimulatorTrain.py`

**Step 1**: Inherit the interface class : 

```
class trainPowerRtu(rtuSimulator.rtuSimuInterface):
```

**Step2**: Overwrite the private function `_initRealWorldConnectionParm` if need to set special parameters:

```
def _initRealWorldConnectionParm(self):
	self.regSRWfetchKey = gv.gRealWorldKey 
```

As shown in the above example, we need to set the RTU identify key to link to real world emulator. 

**Step3**: Init the RTU memory address you want to use to storge the data:

```
   def _initMemoryAddrs(self):
        s7commServer = self.s7Service.getS7ServerRef()
        s7commServer.initNewMemoryAddr(1, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(2, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(3, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(4, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(5, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(6, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(7, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(8, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(9, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
        s7commServer.initNewMemoryAddr(10, [0, 2, 4, 6], [BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
```

As shown above, we want to use 10 memory addresses to store 40 parameters of the train, call the function `getS7ServerRef()` to get the reference of the S7comm server then init the 64 bits memory address from 0x00000001 to 0X00000010. 

**Step4**: Init the memory's default value:

```
def _initMemoryDefaultVals(self):
	s7commServer = self.s7Service.getS7ServerRef()
	s7commServer.setMemoryVal(1, 4, 3)
```

As shown above, we want to set address `0x00000001`' s byte idx =4 to value 3 as dafault.

**Step5**: Overwrite the `_updateMemory()` function to process the memory changes

```
def _updateMemory(self, result):
s7commServer = self.s7Service.getS7ServerRef()
for key, value in self.regsStateRW.items():
    for idx, rstData in enumerate(result[key]):
        memoryIdx = value[idx]
        s7commServer.setMemoryVal(memoryIdx, 0, rstData[0])
        s7commServer.setMemoryVal(memoryIdx, 2, rstData[1])
        s7commServer.setMemoryVal(memoryIdx, 4, rstData[2])
        s7commServer.setMemoryVal(memoryIdx, 6, rstData[3])
```

As shown above, if you want to update some other memory address' value if there is  memory update happens, overwrite the `_updateMemory` function. If you need more complex execution, overwrite the function `_initLadderHandler()` and pass in the complex ladder logic in this function.



------

> last edit by LiuYuancheng (liu_yuan_cheng@hotmail.com) by 08/04/2024 if you have any problem, please send me a message. 