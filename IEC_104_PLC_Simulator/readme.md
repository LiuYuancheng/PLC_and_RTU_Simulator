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

In this section we will introduce the detailed IEC 60870-5-104 protocol packet structure, the data storage address configuration of station and points, the measured point and changeable point. 



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



#### IEC 60870-5-104 Measured Point and Changeable Point

In the context of IEC 60870-5-104 (IEC 104) communication, two fundamental data categories are used to represent the system state and support control functions:"measured points" refer to data that represent the state of a device or process, while "changeable points" represent commands or requests that can be sent to the device to control its behavior. 

- **Measured Points (Telemetry Data)** : Measured points—also known as *monitoring points* or *telemetry objects*—represent real-time values acquired from field sensors or process instruments. These points are **read-only** from the SCADA system's perspective and are periodically or event-driven sent from field devices to the control center. Example of MP: M_ME_NA (Measured value, normalized), M_ME_NB (Measured value, scaled), M_SP_NA (Single point information), M_DP_NA (Double point information). Link: https://tatsoft.com/wp-content/uploads/2021/01/IEC8705104.pdf
- **Changeable Points (Telecontrol Commands)** : Changeable points, or *controllable points*, represent actuators or process elements that can be **remotely controlled** via SCADA commands. These include digital outputs (on/off) and analog setpoints. The commands are issued by the SCADA client and processed by the field device (PLC/RTU), which then changes its internal state or output.  example of CP: C_SC_NA (Single command), C_DC_NA (Double command), C_RC_NA (Regulating step command), C_SE_NA (Setpoint command). Link: https://tatsoft.com/wp-content/uploads/2021/10/IEC8705104S.pdf



------

### System Design Overview

After understanding the detailed structure of the IEC 60870-5-104 protocol in previous section, we now present the system design of the Python Virtual IEC104 PLC Simulator. The goal is to focus on simulating OT control stack — from physical-level devices to SCADA/HMI systems — in a modular, flexible Python environment suitable for academic research and industrial automation education.

The system architecture is divided into three main components as illustrated in the system workflow diagram:

![](doc/img/s_05.png)

The system contents 3 main components : 

- **Communication Module** : This component handles all external data exchange and real-time interfacing tasks includes IEC 60870-5-104 communication stack and UDP-based electrical signal interfaces. 
- **PLC/RTU Station Simulation Framework** : At the core of the system is the virtual PLC/RTU station includes station control modules,  memory management, measured points, changeable points and IEC104 Server. 
- **Ladder Logic / Structured Text Module** : This component interprets control logic using Ladder Logic Diagram (61131-3-LD) or Structured Text (IEC 61131-3-STX) as defined in IEC 61131-3 and the Input Map and Output Map modules. 



------

### Design of Communication Module

The Communication Module of the IEC 104 PLC Simulator is responsible for two essential data exchange pathways within the simulated OT system architecture: PLC/RTU to Physical World Electrical Signal Link (between Level 0 OT Physical Field I/O Devices and Level 1 OT Controller Devices) and PLC/RTU to SCADA-HMI Communication Link (Between Level 1 OT Controller Devices and Level 2 OT Control Center)

#### PLC/RTU to Physical World Electrical Signal Link

To simulate realistic interactions between field-level sensors/actuators and the PLC/RTU controller, this subsystem provides UDP-based electrical signal interfaces to simulate analog/digital signals from Level 0 physical I/O devices. These interfaces bridge virtual sensor readings (e.g., voltage, current, breaker status) and control commands (e.g., motor start/stop) to the PLC simulation with two UDP-based communication interfaces:

**UDP Electrical Signal Measurement Interface**

This interface simulates high-frequency analog/digital signal transmission from virtual sensors to the PLC/RTU input ports, mimicking physical hardwired connections. A dedicated simulator generates virtual signals such as voltage, current, RPM, and breaker states, which are transmitted using the following message format:

```
Measure_Signal_GET;<SensorID>;<timestamp>;{<SignalID>:<SignalType>:<SignalValue>}
```

- **Example:** If a virtual breaker position sensor sends an "OFF" state to the PLC input pin, the UDP message would appear as:

```
Measure_Signal_GET;PG_BK_S_0011;2024-12-06 10:38:29,134;{'POS0011':'VOLTAGE':'5V'}
```

**UDP Electrical Signal Control Interface**

This counterpart interface allows the PLC/RTU to send control commands to virtual actuators, simulating control signal output ports such as for motor switches, relays, or breaker triggers. The message format is:

```
Control_Signal_POST;<ItemID>;<timestamp>;{<SignalID>:<SignalType>:<SignalValue>}
```

- **Example** : To activate a virtual breaker motor for switching, the following command would be sent:

```
Control_Signal_POST;PG_BK_M_0011;2024-12-06 10:51:41,122;{'CTRL':'MOTO_IN':'Voltage_High'}
```

#### IEC 104 Server and Client Communication

To Implement the IEC 60870-5-104 communication stack, supporting both server (PLC/RTU side) and client (SCADA/HMI side) roles. The system uses the [**iec104-python** library](https://github.com/Fraunhofer-FIT-DIEN/iec104-python) developed by Fraunhofer-FIT, enabling multi-threaded IEC 60870-5-104 client-server communication. This integration ensures compatibility with standard SCADA protocols used in critical infrastructure.

**IEC 104 Server (PLC/RTU Side)**

The server module runs on the PLC/RTU simulation and supports two modes:

- **Fetch Mode**: Simulates real-time control operations. When a client sends a request (e.g., to read or write a data point), the server responds immediately, emulating interactive SCADA control.
- **Report Mode**: Simulates automatic periodic reporting from RTU to SCADA. The server broadcasts data updates to all connected clients at configurable intervals, reflecting real-world telemetry behavior.

**IEC 104 Client (SCADA-HMI Side)**

The IEC104 client module operates on the SCADA/HMI side and manages data acquisition and control commands:

- Reads measurement values (status, analog inputs) from the PLC/RTU.
- Writes control signals or setpoints back to the PLC/RTU.
- Interacts with real-time or historical data management modules in the SCADA system.



------

### Design PLC/RTU Simulation Framework

The **PLC/RTU Simulation Framework** is a multi-threaded virtual control engine that emulates the behavior of real industrial PLC or RTU devices within the IEC 60870-5-104 SCADA ecosystem. It serves as the core computational and communication layer between virtual field sensors (Level 0) and the SCADA control system (Level 2).

**Framework Initialization**: Upon startup, the PLC/RTU simulator performs the following initialization tasks:

- **Point & Station Configuration**: Reads system configuration to define the IEC 104 station address, and initialize a set of **measured** and **changeable** points, following standard point types (e.g., `M_SP_NA`, `M_ME_NC`, `C_RC_TA`).
- **Memory Management Module**: Initializes an internal mapping dictionary that associates UDP electrical signal identifiers with IEC 104 point types and values. This acts as a bridge between signal-level data and protocol-specific data formats.

To emulate the asynchronous behavior of actual PLCs/RTUs, the simulation framework launches multiple background threads:

**UDP Signal Handling Thread** will provide below functions:

- Manages multiple instances of **UDP Electrical Signal Measure Interfaces** and **UDP Electrical Signal Control Interfaces**, according to the number of connected virtual devices.
- Periodically fetches sensor signals (e.g., voltage, current, RPM) and control command states.
- Converts signal values to their IEC 104 equivalents and stores them in the associated memory-mapped points.

After the PLC get the simulated physical value, it will convert the raw signal value to IEC104 type and save the value to the related point for example a `0V` can be saved as M`_SP_NA_FALSE` and `5V` can be saved as `M_SP_NA_TRUE`. `Voltage_Signal_Low` can be saved as  `C_RC_NA_STEP_LOWER` and voltage high can be saved as `C_RC_NA_STEP_HIGHER`. 

**LD/ST Logic Execution Thread** 

This thread handles logic operations and mimics the PLC scan cycle behavior based on a configured operation clock cycle:

- **Input Mapping Stage**: The `LD/ST Input Map Module` fetches current values from measured (`M_*`) and changeable (`C_*`) points and maps them to logical operands (e.g., coils, contacts, memory registers) for Ladder Logic or Structured Text processing.
- **Logic Execution Stage**: Thee Ladder Logic / ST Calculation Module executes user-defined logic using the mapped inputs, updating internal states and determining output/control values.
- **Output Mapping Stage**: The `LD/ST Output Map Module` processes the logic result and updates corresponding **changeable points** (e.g., breaker control status, voltage steps), simulating coil/relay actions.

The work flow example will be show below:

![](doc/img/s_06.png)

**Supported IEC 104 Point Types (Current Version v0.0.2)**

In the currently version, we haven't implement all the measured and changeable value type, in the current version we only provide 3 type support which used to represent the state, value and step as shown below:

- **Server measured bool value (M_SP_NA**):  Single-point information, can be read from server and client, but can only be changed from server via `point.value = <val>`, Expected value: `True/False`
- **Server measured number value (M_ME_NC)** : Short floating point number, can be read from server and client, but can only be changed from server via `point.value = <val>`, Expected value: float number, need to do round if do value compare.
- **Server changeable value (C_RC_TA)** : Regulating step command , can be read from server and client, but can only be changed from client via transmit call. Expected value: `iec104.Step.HIGHER/LOWER/INVALID_0/INVALID_1`

**IEC 104 Server Integration**

To enable interaction with the upper-level SCADA (HMI/Console), the simulation framework launches a dedicated thread running an **IEC 60870-5-104 Server**, using the [Fraunhofer FIT IEC104-Python Library](https://github.com/Fraunhofer-FIT-DIEN/iec104-python). Two host modes are provides:

- **Real-Time Fetch Mode**: Responds to SCADA client queries for point states instantly.
- **Periodic Report Mode**: Broadcasts updates to all connected SCADA clients based on a defined report interval.



------

### Design of Ladder Logic/Structured Text Module

The **Ladder Logic / Structured Text (ST) Module** is a core programmable logic interface within the PLC/RTU simulation framework. It provides a customizable, Python-based interface for users to define control behavior using either ladder logic constructs or Structured Text-style operations.

The module is designed as a base **interface class** that users can inherit to implement their custom control logic. Two key methods must be overridden:

- `initLadderInfo()`: Defines the structure and mapping of source registers, source coils, and destination coils.
- `runLadderLogic()`: Implements the actual logic evaluation (e.g., Boolean gates, comparisons, timers) using inputs from holding registers and coils.

In **Ladder Logic Mode**, logic circuits are constructed using symbolic references to:

- **Holding Registers** (e.g., `reg-00`, `reg-01`)
- **Source Coils** (e.g., `src-coil-00`)
- **Destination Coils** (e.g., `dest-coil-02`)

Example Ladder Diagram:

```
 --|reg-00|--|reg-01|----------------------(src-coil-00)------------(dest-coil-02)---
```

To implement this logic:

- Define the logic operation (`AND` in this case) in `runLadderLogic()`.

- Initialize logic metadata in `initLadderInfo()`:

```python
self.holdingRegsInfo = {'address': 0, 'offset': 2}      # Registers reg-00 and reg-01
self.srcCoilsInfo    = {'address': 0, 'offset': 1}      # Coil src-coil-00
self.destCoilsInfo   = {'address': 2, 'offset': 1}      # Coil dest-coil-02
```

- Add the customized ladder object to `plcDataHandler`. When holding registers or coils change, the corresponding input values are automatically passed to `runLadderLogic()`.

- `runLadderLogic()` computes the output (e.g., destination coil state) and returns the result. `plcDataHandler` then updates the relevant memory/state accordingly. as shown below:

```python
def runLadderLogic(self, regVals, srcCoilsVals):
    output = regVals[0] and regVals[1] and srcCoilsVals[0]  # Example logic: AND gate
    return [output]
```

 **Structured Text (ST) Mode**

In **ST Mode**, users can directly link logic operations to **point addresses** (e.g., IEC104 mapped points) without referencing coil/register offsets. This is suitable for users preferring symbolic or protocol-specific memory addressing.

ST Address Setup Example:

```python
self.stationAddr = 1
self.srcPointAddrList  = [1001, 1002]                  # Source point addresses
self.srcPointTypeList  = ['M_SP_NA', 'M_ME_NC']        # Source types
self.destPointAddrList = [2001]                        # Destination point address
self.destPointTypeList = ['C_RC_TA']                   # Destination type
```

This allows logic to operate on memory-based point values retrieved directly from the simulation’s IEC 104 data map.

**Execution Flow Integration**

The Ladder Logic / ST module is tightly integrated with the `plcDataHandler`, which:

- Monitors changes to input registers and coils.
- Triggers execution of `runLadderLogic()` with current input values.
- Applies the returned results to the destination coils or points.

This mimics the **scan-execute-update cycle** used in real-world PLC logic engines.



------

> last edit by LiuYuancheng (liu_yuan_cheng@hotmail.com) by 12/05/2025 if you have any problem, please send me a message. 