# Python Visual Building Controller (RTU) with ISO 16484-5 BACnet Communication Protocol

**Project Design Purpose** : In this project, I extend the [Python-Based virtual Remote Terminal Unit Simulator System](https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc) (which interfaced to SCADA system via Modbus-TCP, Siemens-S7Comm, IEC 60870-5-104 and IEC 62541 OPC-UA-TCP)  by adding the support for **ISO 16484-5 BACne**t protocol. The BACnet (Building Automation and Control Networks) is an open communication protocol defined in ANSI/ASHRAE 135 and ISO 16484-5. It is widely used in building automation to integrate systems such as HVAC, lighting, energy management, security, and access control. By providing a common communication language, BACnet enables devices from different manufacturers to interoperate seamlessly.

The enhanced virtual RTU simulator developed in this project focuses on modeling the core behaviors of BACnet devices and controllers, including data acquisition, value exchange, processing, and automated control according to the ISO 16484-5 specification which can help build the OT components in cyber range. This project delivers three key capabilities:

- **BACnet Communication Module** – A Python BACnet communication layer (server and client) supporting interaction among Sensors, Controllers, RTUs, BACnet Gateways, and SCADA/HMI systems, enabling analog and discrete BACnet data exchange.
- **RTU Simulator Framework** – A virtual building-system controller framework that simulates physical components such as HVAC, lighting, and security systems, supporting monitoring and automatic control based on predefined logic rules.
- **Data Processing and Control Module** – A plug-in Python module for BACnet data storage, processing, and control-signal generation, integrated with the RTU simulator framework to execute control strategies.

```python
# Author:      Yuancheng Liu
# Created:     2026/01/08
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 Liu Yuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### 1. Introduction

The python ISO 16484-5 BACnet Simulator is designed to used to build the virtual components in the building management (such as the HVAC, lighting, and security system) of a OT digital/Cyber twin. It serves as both a learning and testing platform for BACnet-based building automation applications. The RTU simulator is **NOT** 1:1 emulate the real BACnet devices function, this simulator focuses on the core operational behaviors of BACnet remote controller : the variable storage model, data exchange patterns, and control logic execution cycle. It provides an educational and prototyping environment for below purpose:

- Academic researchers studying industrial automation
- Students learning OT protocols and BAC device behavior
- Developers building or testing BACnet-enabled systems
- OT cybersecurity professionals analyzing communication flows

In this system I use the python BACnet lib [BACpypes](https://bacpypes.readthedocs.io/en/latest/gettingstarted/gettingstarted001.html) to implement the communication part. The RTU simulator allows users to construct a cyber twin that architectures that mirror the basic 3 level components in real OT environments. As illustrated in the diagram below, it supports interactions across multiple OT layers, from Level 0 (physical field devices and sensors)  to Level 2 (control center/Processing Lan). Users can prototype virtual field controllers, RTUs, I/O servers, or SCADA clients, all communicating through the BACnet protocol. 

![](doc/img/s_03.png)











https://youtu.be/xxZrl2InHuM?si=bPPfYq2hx5O53adJ