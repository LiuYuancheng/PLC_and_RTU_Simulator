# Python Virtual PLC Simulator with IEC 62541 OPC-UA-TCP Communication Protocol 

**Project Design Purpose** : In this follow-up project, I extend my previous Python-based virtual PLC/RTU simulator program (which interfaced to SCADA systems via [Modbus-TCP and S7Comm]( https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc ), or [IEC 60870-5-104](https://www.linkedin.com/pulse/python-virtual-plc-simulator-iec-60870-5-104-protocol-yuancheng-liu-bov7c)  by adding the support for IEC 62541 OPC-UA-TCP industrial OT communication protocol. OPC-UA is a modern, secure, and interoperable machine-to-machine OT protocol widely used in automation, SCADA systems, robotics, and IIoT environments.

This enhanced virtual PLC simulator re-implements key aspects of PLC/RTU data modeling, variable storage, and value exchange flows according to the requirements of the IEC 62541 standard. The updated design consists of three major components:

- **OPC-UA-TCP Comm Module** – Implements an OPC-UA communication layer with both PLC-side server capabilities and SCADA/HMI-side client interfaces, enabling fully standardized OPC-UA data exchange.
- **PLC/RTU Simulator Framework** – Manages virtual device inputs and outputs, maintains the OPC-UA data structure space (nodes, objects, and variables), and handles interactions with the physical-world simulator and internal logic engine.
- **Simulated Ladder Logic Module** – A Python-based circuit logic execution engine that emulates PLC ladder logic behavior to realize the control and response functions of the real PLC.

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

Open Platform Communications Unified Architecture (OPC UA) is a cross-platform, open-source, IEC62541 standard for data exchange from sensors to cloud applications developed by the [OPC Foundation](https://en.wikipedia.org/wiki/OPC_Foundation).  It's a data exchange protocol that facilitates interoperability between different vendors' devices and systems, from PLCs and PCs to cloud servers and embedded microcontrollers. OPC UA ensures secure data exchange through features like encryption, authentication, and a standardized information model that represents devices and their data.

In this project we follow the idea in the article "[Connecting PLCs to Various Software Packages with OPC UA](https://opcconnect.opcfoundation.org/2022/03/connecting-plcs-to-various-software-packages-with-opc-ua/)" (as shown in the below diagram from the article) from [opcconnect](https://opcconnect.opcfoundation.org/) aims to develop a cross-platform Python-based virtual PLC and RTU simulator that complies with the IEC62541OPC-UA-TCP standard. 

![](doc/img/s_03.png)

The simulator is **NOT** 1:1 emulate the real PLC's function but distill the main logic of the PLC to simulate the behaviors and data exchange for a PLC under working condition. The purpose is to offer an educational and prototyping tool that allows users—particularly academic researchers and automation developers—to emulate and test control systems across different layers of an operational technology (OT) environment. As illustrated in the system architecture diagram (below), the simulator supports the creation and interaction of components spanning from Level 0 (physical field devices and sensors) up to Level 3 (control center and operations management zones).

![](doc/img/s_04.png)

The communication follow the host-connector module : User will embed the OPC-UA-TCP server module in the components running in lower level to host the information, then integrate the OTC-UA-TCP client in the next higher OT level to connect fetch the data or change the state.



------

