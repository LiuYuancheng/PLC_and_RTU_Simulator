# Python Virtual RTU Simulator With IEEE IEEE 1815-2021 DNP3.0 Communication Protocol

**Project Design Purpose** : In this project, I did extend my previous Python-based virtual PLC/RTU simulator library (which interfaced to SCADA systems via Modbus-TCP and S7Comm, related link:  https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc)  by adding the support function for IEEE 1379-2000 Distributed Network Protocol 3 (DNP3) protocol. The new feature design consists of two major components :

- **DNP3.0 Communication Lib** : The DNP3.0 Communication Module implements a minimal and dependency-free DNP3 protocol stack, providing the data exchange between the DNP3 master and outstation. Compare with other DNP3 lib, the module is implement by basic Python standard socket + struct library without special tool-set such as C++ compiler. 
- **RTU Simulator Framework** : The RTU Simulator Framework models the operational behavior of industrial field devices such as RTU/PLC. It manages the cyber twin's virtual device inputs and outputs, processes DNP3.0 messages, interfaces with physical-world simulation modules, and executes user-defined control logic.

```python
# Author:      Yuancheng Liu
# Created:     2026/07/29
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 Liu Yuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### 1. Project Introduction

**Distributed Network Protocol 3** (**DNP3**) is a set of ICS communications protocols used between components in process automation systems. Its main use is in utilities such as electric and water companies. Usage in other industries is not common. It was developed for communications between various types of data acquisition and control equipment. It plays a crucial role in SCADA systems, where it is used by SCADA Master Stations (a.k.a. Control Centers), remote terminal units (RTUs), and intelligent electronic devices (IEDs). It is primarily used for communications between a master station and RTUs or IEDs.

DNP3 Wiki Reference: https://en.wikipedia.org/wiki/DNP3

There are several different type of good DNP3 lib such as the FreyrSCADA-NDP3 Lib https://github.com/FreyrSCADA/DNP3 which provide the full function of DNP3 communication, but most of them needs the Windows Software Development Kit - C C++ C# .NET Programming or the Linux Software Development Kit - C, C++ - (ARM, Coldfire, Power PC), Ubuntu Linux(X86, X86-64), Fedora, CentOS, Red Hat. Which need customized configuration of the node before using the lib, so I want to create a simpler  minimal and dependency-free implementation lib of the DNP3 communication lib under  Transport and Application layers to simulate the Data Link  between **DNP3 Master** and **DNP3 Outstation** which can be used in the cyber twins system I will develop in the further, it will try to reduce the  only use the Python standard library (socket + struct). 

For more information about DNP, please refer to https://www.dnp.org/About/Overview-of-DNP3-Protocol

#### 1.1 Project DNP3 Master and DNP3 Outstation

The DNP3 data exchange can go through serial link such as RS232/RS485, Ethernet and Wireless, this comm lib only provide the data exchange in the Ethernet and Wireless. 

The project will provide the multiple DNP clients to plug in the master to fetch data from different DNP Outstation devices which contents one DNP server. The data exchange and components diagram is shown below: 

![](doc/img/s_03.png)

**1.1.1 DNP3 Master **

The Master is typically the SCADA server or control center. Its responsibilities include:

- Polling outstations for measurements (voltage, current, temperature, etc.)
- Reading binary and analog inputs
- Sending control commands (open/close breakers, start/stop equipment)
- Synchronizing the outstation's clock
- Configuring or querying device parameters
- Receiving alarms and event reports

A single master often communicates with **many outstations** simultaneously.

**1.1.2 DNP3 Outstation**

The **Outstation** is the field device, such as an RTU, PLC, or IED. Its responsibilities include:

- Monitoring connected sensors and actuators
- Maintaining a database of process values
- Recording time-stamped events
- Responding to master requests
- Executing control commands received from the master
- Optionally sending **unsolicited messages** when significant events occur

An outstation generally serves one or more authorized masters, depending on the system design.



------

