# Python Virtual RTU Simulator With IEEE IEEE 1815-2021 DNP3.0 Communication Protocol

**Project Design Purpose** : In this project, I did extend my previous Python-based virtual PLC/RTU/MU/IED simulator library (which interfaced to SCADA systems via Modbus-TCP and S7Comm, related link:  https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc)  by adding the support function for IEEE 1815-2021 Distributed Network Protocol 3 (DNP3) protocol. The new implementation consists of two main components :

- **DNP3.0 Communication Lib** : The DNP3.0 Communication Module implements a minimal and lib dependency-free DNP3 protocol stack, providing the data exchange between the DNP3 master and outstation. Compare with other DNP3 lib, this module is implement by basic Python standard socket + struct library without special tool-set such as C++ compiler. 
- **RTU Simulator Framework** : The RTU Simulator Framework models the operational behavior of industrial OT field devices such as RTU/PLC. It manages the cyber twin's virtual device inputs and outputs, processes DNP3.0 messages, interfaces with physical-world simulation modules, and executes user-defined control logic.

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

There are several different type of good Python DNP3.0 lib such as the `FreyrSCADA-NDP3` Lib https://github.com/FreyrSCADA/DNP3 which provide the full function of DNP3 communication, but most of them needs the  C/C++ or require platform-specific development environments, compilers, SDKs, or additional dependencies. This can make them less convenient when the primary objective is to quickly deploy a lightweight protocol simulator across different cyber-range nodes or virtual machines. 

Therefore, this project takes a different approach: implement a minimal DNP3 communication stack using only the Python standard library, primarily `socket` and `struct`. The goal is to provide the essential DNP3 communication mechanisms required to simulate "Data Link" between a DNP3 Master and DNP3 Outstation. The DNP3 data exchange can go through serial link such as RS232/RS485, Ethernet and Wireless, this comm lib only provide the data exchange in the Ethernet and Wireless. The use case of the DNP3 RTU devices configuration is shown below:

![](doc/img/s_02.png)

For more information about DNP3, please refer to https://www.dnp.org/About/Overview-of-DNP3-Protocol

#### 1.1 DNP3 Simulation System Overview

The simulator project is **NOT** designed for1:1 emulate the real RTU hardware function (not used for a digital twin system), it focuses on reproducing the core operational behaviors commonly found in the DNP3 industrial devices, including:

- Device internal data parameter/variable storage management
- DNP3.0 Telemetry and control data exchange workflows
- DNP3.0 RTU device automated control logic execution cycles
- Interactions between field devices, controllers, and supervisory systems

And the main purpose of the system application will be on the effective educational, prototyping, and research environment such as :

- Academic researchers studying industrial automation and OT system architectures
- Students learning OT communication protocols and DNP3 device behaviors
- Developers building, testing, or validating DNP3 applications, digital forensics (DNP3 traffic data capture and analysis)
- OT cybersecurity professionals analyzing industrial communication flows and attack scenarios

#### 1.2 DNP3 System ISA-95 Architecture 

The simulator enables users to construct cyber twins' components that mirror the hierarchical architecture commonly found in modern industrial environments. As shown in the figure below, the framework follows a simplified four-level OT architecture based on the ISA-95 model as shown in the below diagram : 

![](doc/img/s_04.png)

- At **Level 0 (Physical Process Field I/O Devices)**, simulated IED devices, sensors, and metering units generate operational data representing measurements collected from physical processes. The data will be transferred by using the UDP data to simulate the electrical analog signal to the level 1 devices (DNP3 outstation).

- At **Level 1 (Controller Processing LAN)**, the RTU simulator act as the main components of the DNP3 outstation, it collects the analog signal data from field devices, manages data storage and executes server-side processing logic when required. Then provide a DNP server interface for the level 2 components to fetch the data and control the device.
- At **Level 2 (Control Center/HQ Processing LAN)**, supervisory applications (NDP3 mater) such as monitoring workstations, engineering desktops, mobile devices, and touchscreen operator panels run DNP3 client services to fetch device data, visualize process information, and issue control commands. 



------

### 2. DNP3 Protocol Background Knowledge

If you are familiar about the DNP3 protocol, you can skip this section.

**Distributed Network Protocol 3** (**DNP3**) is a set of ICS communications protocols used between components in process automation systems. Its main use is in utilities such as electric and water companies. Usage in other industries is not common. It was developed for communications between various types of data acquisition and control equipment. It plays a crucial role in SCADA systems, where it is used by SCADA Master Stations (a.k.a. Control Centers), remote terminal units (RTUs), and intelligent electronic devices (IEDs). It is primarily used for communications between a master station and RTUs or IEDs. 

DNP3 Wiki Reference: https://en.wikipedia.org/wiki/DNP3

#### 2.1 NDP 3 Protocol Packet Structure











#### 2.2 Project DNP3 Master and Outstation Implementation 

DNP3 plays an important role in SCADA (Supervisory Control and Data Acquisition) architectures. In a typical deployment, a DNP3 Master—usually implemented as part of a SCADA server or control center—communicates with multiple **DNP3 Outstations,** such as RTUs, PLCs, or IEDs. The Master can acquire real-time measurements, receive events and alarms, synchronize device time, and issue control commands to field equipment.

The project will provide the multiple DNP clients to plug in the master to fetch data from different DNP Outstation devices which contents one DNP server. The data exchange and components diagram is shown below: 

![](doc/img/s_03.png)

**1.1.1 DNP3 Master Implementation **

The Master is typically the SCADA server or control center. Its responsibilities include:

- Polling outstations for measurements (voltage, current, temperature, etc.)
- Reading binary and analog inputs
- Sending control commands (open/close breakers, start/stop equipment)
- Synchronizing the outstation's clock
- Configuring or querying device parameters
- Receiving alarms and event reports

A single master often communicates with **many outstations** simultaneously.

**1.1.2 DNP3 Outstation Implementation**

The **Outstation** is the field device, such as an RTU, PLC, or IED. Its responsibilities include:

- Monitoring connected sensors and actuators
- Maintaining a database of process values
- Recording time-stamped events
- Responding to master requests
- Executing control commands received from the master
- Optionally sending **unsolicited messages** when significant events occur

An outstation generally serves one or more authorized masters, depending on the system design.



------

