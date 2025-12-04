# Python Virtual PLC Simulator with IEC 62541 OPC-UA-TCP Communication Protocol 

**Project Design Purpose** : In this follow-up project, I extend the previous Python-based virtual PLC/RTU simulator program (which interfaced to SCADA systems via [Modbus-TCP and S7Comm]( https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc ), or [IEC 60870-5-104](https://www.linkedin.com/pulse/python-virtual-plc-simulator-iec-60870-5-104-protocol-yuancheng-liu-bov7c)  by adding the support for IEC 62541 Open Platform Communications Unified Architecture TCP (OPC-UA-TCP) protocol -- an industrial machine-to-machine OT communication protocol for automation, SCADA systems, robotics, and IIoT devices. This virtual PLC simulation program re-implement part of the PLC/RTU  OT variable storage and data exchange flow based on the requirement of IEC 62541 standard. The new simulator include 3 main section:

- **OPC-UA-TCP Comm Module** : a OPC-UA communication module (with PLC-side server and SCADA/HMI-side client interfaces) enabling standardized OPC-UA data exchange. 
- **PLC/RTU Simulator Framework** : an Framework maintains virtual PLC/RTU device contact input and coil output to physical world simulator, the UA data name space, node, object and variables, the simulated ladder logic algorithm. 
- **Simulated ladder logic Module** : a python module embed in the simulator framework and simulated the ladder logic execution to implement the control and response function of the PLC.



```python
# Author:      Yuancheng Liu
# Created:     2025/11/28
# Version:     v_0.0.3
# Copyright:   Copyright (c) 2025 Liu Yuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### Introduction

OPC Unified Architecture (OPC UA) is a cross-platform, open-source, IEC62541 standard for data exchange from sensors to cloud applications developed by the [OPC Foundation](https://en.wikipedia.org/wiki/OPC_Foundation). 