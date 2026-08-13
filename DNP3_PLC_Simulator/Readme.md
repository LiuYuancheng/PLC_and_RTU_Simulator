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

DNP3 communication uses a layered packet structure designed to provide reliable communication between a DNP3 Master and DNP3 Outstation. A DNP3 frame consists of a Data Link Layer header, followed by a Transport Layer header and an Application Layer message. CRC values are also used to detect transmission errors. The Port for DNP3 communication use 20000. 

The main DNP3 packet structure is shown below:

![](doc/img/s_05.png)

Image Reference: https://www.semanticscholar.org/paper/DNP3-network-scanning-and-reconnaissance-for-Rodofile-Radke/5d628548e00319009dad6afb08f80c7ed58cf29c/figure/0

- The **Data Link Layer** identifies the beginning and length of the DNP3 frame and contains the source and destination addresses. 
- The **Transport Layer** is responsible for fragmenting and reassembling larger application messages. 
- The **Application Layer** contains the actual DNP3 operation, such as `READ`, `WRITE`, control operations, or responses containing process data.

**2.1.1 DNP3 Function Code**

In the application layer data, the "FN Code" will identify the function of this packet. As show in the below, the function code `0x81` identify it is a response for the data reading request from the DNP outstation: 

![](doc/img/s_06.png)



The DNP3 protocol uses 27 basic function codes to allow communication between master stations and remote units, in the DNP3 lib I created, I only implement below 7 function for data exchange and simplify control: 

| Name                      | FN Code | Hex Value | Direction / Purpose                                          |
| ------------------------- | ------- | --------- | ------------------------------------------------------------ |
| FUNC_CONFIRM              | 0       | `0x00`    | Application-layer confirmation connection                    |
| FUNC_READ                 | 1       | `0x01`    | Master requests data from Outstation                         |
| FUNC_WRITE                | 2       | `0x02`    | Master writes configuration/data to Outstation               |
| FUNC_DIRECT_OPERATE       | 5       | `0x05`    | Execute a control directly                                   |
| FUNC_DIRECT_OPERATE_NR    | 6       | `0x06`    | Direct control without application confirmation              |
| FUNC_RESPONSE             | 129     | `0x81`    | Standard Response from outstation to the master request      |
| FUNC_UNSOLICITED_RESPONSE | 130     | `0x82`    | Unsolicited Response (initiated autonomously by the outstation rather than replying to a direct request |

Reference : https://www.dpstele.com/blog/how-to-understand-dnp3-protocol.php

#### 2.2 Project DNP3 Master and Outstation Implementation 

DNP3 plays an important role in SCADA (Supervisory Control and Data Acquisition) architectures. In a typical deployment, a DNP3 Master—usually implemented as part of a SCADA server or control center—communicates with multiple **DNP3 Outstations,** such as RTUs, PLCs, or IEDs. The Master can acquire real-time measurements, receive events and alarms, synchronize device time, and issue control commands to field equipment.

The project will provide the multiple DNP clients to plug in the master to fetch data from different DNP Outstation devices which contents one DNP server. The data exchange and components diagram is shown below: 

![](doc/img/s_03.png)

**2.2.1 DNP3 Master Implementation **

The Master is typically the SCADA server or control center. Its responsibilities include:

- Polling outstations for measurements (voltage, current, temperature, etc.)
- Reading binary and analog inputs
- Sending control commands (open/close breakers, start/stop equipment)
- Synchronizing the outstation's clock
- Configuring or querying device parameters
- Receiving alarms and event reports

A single master often communicates with **many outstations** simultaneously.

**2.2.2 DNP3 Outstation Implementation**

The **Outstation** is the field device, such as an RTU, PLC, or IED. Its responsibilities include:

- Monitoring connected sensors and actuators
- Maintaining a database of process values
- Recording time-stamped events
- Responding to master requests
- Executing control commands received from the master
- Optionally sending **unsolicited messages** when significant events occur

An outstation generally serves one or more authorized masters, depending on the system design.



------

### 3. Design of Virtual DNP3 RTU 

This section introduces the detailed design of the DNP3 communication modules and demonstrates how they can be integrated into cyber twin environments. 

#### 3.1 DNP3 Communication Module Design

  The function implemented in this module will be enough of the Data Link, Transport and Application layers to:

   \- Open a TCP session on the standard DNP3.0 port (20000)

   \- Provide API: READ (function 0x01) Binary Inputs (Group1Var2), Analog Inputs

​    (Group30Var1), Binary Output status (Group10Var2) and Analog Output

​    status (Group40Var1)

   \- DIRECT_OPERATE (function 0x05) a Binary Output (Group12Var1 / CROB) or

​    an Analog Output (Group41Var1) to let a master WRITE a value into the

​    outstation's point database

   \- build syntactically correct DNP3 frames (valid sync bytes, length,

​    control byte, addresses and CRC-16/DNP checksums) so the traffic is

​    recognised natively by Wireshark's "dnp3.0" dissector on port 20000.

  

Remark: This is NOT a full/compliant DNP3 stack (no unsolicited responses, no multi-fragment transport reassembly, no confirm/retry handling, no serial support). It is intended for lab / training / detection-content use, not for production ICS deployments. The data types supported are limited to bool and int.

**3.1.1 Design of DNP3 Server**

DNP3.0 server class for host the PLC or RTU data and provide to clients. This obj needs to run in a sub-thread in the PLC/RTU's main thread. The server will keep the DNP3 data structure(point) as shown in the below diagram: 

![](doc/img/s_07.png)

Listens on TCP/20000 (the IANA-registered DNP3 port) and serves a small point database:

 Binary Input    (Group 1  Var 2)  read-only, bool type

 Analog Input    (Group 30 Var 1)   read-only, integer type 

 Binary Output   (Group 10 Var 2) i  read/write ("parameters"), bool type

 Analog Output   (Group 40 Var 1)read/write ("parameters"), integer type 

```
# Object group/variation pairs used by this implementation
GRP_BINARY_INPUT = (1, 2)           # Binary Input w/ flags        (1 byte/obj)
GRP_BINARY_OUTPUT_STATUS = (10, 2)  # Binary Output status w/flags (1 byte/obj)
GRP_CROB = (12, 1)                  # Control Relay Output Block  (11 bytes/obj)
GRP_ANALOG_INPUT = (30, 1)          # 32-bit Analog Input w/flag   (5 bytes/obj)
GRP_ANALOG_OUTPUT_STATUS = (40, 1)  # 32-bit Analog Output status  (5 bytes/obj)
GRP_ANALOG_OUTPUT_CMD = (41, 1)     # 32-bit Analog Output cmd     (5 bytes/obj)
```

A DNP3 master (client) can:

 \* READ (function 0x01) any/all of the four object types above

 \* DIRECT_OPERATE (function 0x05) a CROB (Group 12 Var 1) to flip a Binary

  Output, or an Analog Output command (Group 41 Var 1) to set an Analog

  Output -- i.e. WRITE a parameter's value.

**3.1.2 Design of DNP3 Client**

