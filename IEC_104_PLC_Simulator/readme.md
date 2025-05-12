# Python Virtual PLC Simulator with IEC-60870-5-104 Communication Protocol 

**Project Design Purpose**: 

In this follow-up project, we extend the previous Python-based virtual PLC/RTU simulator program (which interfaced to SCADA systems via Modbus-TCP and S7Comm, related link: https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc ) by adding the IEC 60870-5-104 (IEC104) protocol. This project aims to extend the PLC simulator's capabilities with IEC104 PLC/RTU feature and integrating support for the IEC-60870-5-104 (IEC104) communication protocol -- a widely-used telecontrol standard for power system automation. 

The new simulator is organized into three modular components:

- **IEC104 Communication Module** : an IEC104 communication module (with PLC-side server and SCADA/HMI-side client interfaces) enabling standardized IEC104 data exchange. 
- **PLC/RTU Simulation Framework** : an Framework maintains virtual PLC/RTU device memory, IEC104 station (save linked IED data) , IEC104 points (save contacts and coils data), customized operation ladder logic/Structured Text algorithm, IEC104 server linking to next level OT SCADA components and a UDP physical signal connector linking to the lower level physical components sensor simulator.
- **Ladder Logic/Structured Text Module** : which uses a Python plugin interface to simulate PLC/RTU logic behavior by processing virtual contact/memory inputs and updating coil states accordingly which same as the Ladder Logic Diagram (IEC 61131-3-LD) or Structured Text Program(IEC 61131-3-STX)  

```python
# Author:      Yuancheng Liu
# Created:     2025/05/10
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### Introduction

IEC 60870-5-104 (commonly referred to as IEC 104) is a widely adopted communication protocol used in SCADA (Supervisory Control and Data Acquisition) systems for real-time/remote data exchange in critical infrastructure sectors such as power grids, water treatment, and industrial automation. Supported by major PLC and RTU manufacturers including Siemens, ABB, Mitsubishi Electric, and Altus Sistemas de Automação, IEC 104 plays a vital role in enabling remote monitoring and control across geographically distributed systems.

This project aims to develop a cross-platform Python-based virtual PLC and RTU simulator that complies with the IEC 60870-5-104 standard. The purpose is to offer an educational and prototyping tool that allows users—particularly academic researchers and automation developers—to emulate and test control systems across different layers of an operational technology (OT) environment. As illustrated in the system architecture diagram (below), the simulator supports the creation and interaction of components spanning from Level 0 (physical field devices and sensors) up to Level 2/3 (control center and operations management zones).

![](doc/img/s_03.png)

This article presents the implementation of the virtual PLC simulator with IEC 104 communication capability. It begins with a brief overview of the IEC 104 protocol, followed by a detailed explanation of the simulator's modular design—covering the communication module, IEC data storage, electrical signal simulation links, and the ladder logic/structured text algorithm engine. Finally, practical examples will demonstrate how users can apply the simulator to model real-world OT systems in a fully virtual environment.



------

### Background knowledge 

#### IEC 60870-5-104 Protocol Detail

IEC 60870-5-104 (IEC 104) is a network-based extension of IEC 60870-5-101 and is designed for communication between control stations (e.g., SCADA, DCS) and substations or field equipment over TCP/IP networks. IEC 104 uses the same Application Protocol Data Unit (APDU) format as IEC 101 but encapsulated within TCP/IP packets. An IEC 104 APDU consists of the Start Byte, Length, and Application Protocol Control Information (APCI), followed optionally by Application Service Data Unit (ASDU). The packet detail is shown blow: 

![](doc/img/s_04.png)

The ASDU contains the actual data being transmitted, such as monitoring values or control commands. Here's a more detailed breakdown:

**APCI (Application Protocol Control Information)** section determines the frame type:

- **Start byte (0x68):** Indicates the beginning of a packet.

- **Length byte:** Specifies the length of the data within the packet. 
- **Four-byte control field:** Provides control information, including options for data transmission and acknowledgements. 

**ASDU (Application Service Data Unit)** holds the actual control or monitoring data and has the following structure:

- **Type Identification (TI)** : 1 byte to indicates the type of information (e.g., `0x01` for single-point)
- **Variable Structure Qualifier (VSQ)** : 1 byte to indicate the number of elements and addressing mode. 
- **Cause of Transmission (COT)** : 2 bytes to indicate the reason for sending (e.g., spontaneous, request, activation)
- **Common Address (CA)** : 2 bytes identifies the source device station memory address. 
- **Information Object Address  (IOA)** : 3 bytes indicate the source device station's point object memory address. 
- **Information elements (Data)** : Depends on the type (e.g., 1 byte for a boolean status, 3 bytes for float)
- **Time tag of information element** :  Time information this information is optional. 

> Reference: https://infonomics-society.org/wp-content/uploads/Passive-Security-Monitoring-for-IEC-60870-5-104-based-SCADA-Systems.pdf



#### IEC 60870-5-104 Packet Example

When we capture a simple ASDU payload for a single digital point might look like this (hex):

```
68 0E 00 00 00 00 01 01 06 00 01 00 00 00 01
```

We can mapping it to the protocol detail to parse the information: 

- `68` → Start byte
- `0E` → Length
- `00 00 00 00` → I-Frame APCI (send/recv = 0)
- `01` → Type ID: Single-Point Information (M_SP_NA)
- `01` → VSQ: 1 element
- `06 00` → Cause of Transmission: spontaneous
- `01 00` → ASDU station address 256. 
- `00 00 00` → Information Object Address 0.
- `01` → Data: status = ON (IEC type M_SP_NA)

After analysis the packet, we it it is a repose data from PLC to the HMI to report one point's bool state.



#### IEC 60870-5-104 Station and Point

In IEC 104, a station represents a physical device or a group of devices that are managed and controlled by a central system. A point, within the station, represents a specific piece of data or a command that can be exchanged between the station and the central system.

The ASDU Address and the Information Object Address (IOA) define the station and its internal points: 

- **ASDU Address** is a 2-byte field that uniquely identifies a **remote station** (e.g., a PLC, RTU, or IED) within the SCADA network. This station represents a logical unit that gathers or controls field data, and it acts as the source or destination of telecontrol messages. The range of a station address is [1, 65534].
- **IOA Address** is The **Information Object Address** is a 3-byte field used to uniquely identify **individual data points** (e.g., sensors, switches, analog inputs) within the context of a given ASDU (station). The range of a point address in the station is n [0, 16777215]



------

