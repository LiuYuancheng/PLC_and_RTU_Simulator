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

Open Platform Communications Unified Architecture (**OPC UA**) is a cross-platform, open-source standard IEC 62541 industrial communication protocol designed for secure and interoperable data exchange across all layers of an OT ecosystem—from sensors and PLCs on the plant floor to enterprise-level servers and cloud applications. Developed by the [OPC Foundation](https://en.wikipedia.org/wiki/OPC_Foundation), OPC UA enables seamless communication between heterogeneous devices and software platforms by providing:

- A standardized, vendor-neutral information model

- Robust security (encryption, signing, authentication)

- Scalable communication mechanisms suitable for embedded controllers, SCADA systems, and IIoT platforms

In this project I follow the idea in the article "[Connecting PLCs to Various Software Packages with OPC UA](https://opcconnect.opcfoundation.org/2022/03/connecting-plcs-to-various-software-packages-with-opc-ua/)" (as shown in the below diagram from the article) from [opcconnect](https://opcconnect.opcfoundation.org/) aims to develop a cross-platform Python-based virtual PLC and RTU simulator that complies with the IEC62541OPC-UA-TCP standard.

![](doc/img/s_03.png)

The simulator is **NOT** 1:1 emulate the real PLC's hardware function this simulator focuses on the core operational behaviors of a PLC—its variable storage model, data exchange patterns, and control logic execution cycle. It provides an educational and prototyping environment for below purpose:

- Academic researchers studying industrial automation
- Students learning OT protocols and PLC behavior
- Developers building or testing OPC-UA-enabled systems
- OT cybersecurity professionals analyzing communication flows

The simulator allows users to construct and test control architectures that mirror real OT environments. As illustrated in the diagram below, it supports interactions across **multiple OT layers**, from Level 0 (physical field devices and sensors)  to Level 3 (control center and operations management zones). Users can prototype virtual field controllers, RTUs, I/O servers, or SCADA clients, all communicating through the OPC-UA-TCP protocol. The project use the library  [opcua-asyncio](https://github.com/FreeOpcUa/opcua-asyncio?tab=LGPL-3.0-1-ov-file) to implement the data communication.

![](doc/img/s_04.png)

The OPC-UA nodes' communication follows a host–connector model:

- Lower-level OT components (PLCs, RTUs, field controllers) host their data through an embedded OPC-UA-TCP server module.
- Higher-level components (HMI, SCADA, historian, database server) integrate an OPC-UA-TCP client module to browse, read, write, or subscribe to the data exposed by lower-level devices.

This layered approach allows users to easily construct realistic OT communication topologies and observe OPC-UA information flow across different operational zones.



------

### OPC UA Protocol Background Knowledge

In this section I will summarize the basic background knowledge introduction of the OPC UA protocol under network level which I used to develop the OPC-UA-TCP Comm Module in the virtual PLC simulator project. Unlike older OT protocols (Modbus, DNP3, S7Comm), OPC UA provides:

- A service-oriented architecture (SOA)
- A rich information modeling framework
- End-to-end security (signing, encryption, authentication)
- Multiple transport layers including OPC-UA TCP, HTTPS, WebSockets, and PubSub

For the transport Layers, OPC UA supports several transport bindings as shown in the below table:

| Transport  | Encoding    | Usage                         |
| ---------- | ----------- | ----------------------------- |
| opc.tcp:// | Binary      | Fastest and most common in OT |
| https://   | XML/JSON    | Enterprise integration        |
| WebSocket  | JSON/Binary | Browser and cloud systems     |
| UDP PubSub | UADP        | Real-time IIoT broadcast      |

For the PLC simulation module, I use the basic OPC UA Binary over TCP as it provides the Low overhead, High performance and Deterministic serialization capability. 



#### OPC-UA TCP Protocol Packet Structure

The OPC-UA TCP message structure includes three main section (TCP message header, OPC UA SecureChannel header and Binary encoded OPC UA body ) as shown in the document :  https://reference.opcfoundation.org/v104/Core/docs/Part6/6.7.2/

![](doc/img/s_05.png)

Each OPC-UA TCP message begins with a 12-byte fixed header:

| Offset | Size | Field                | Description                    |
| ------ | ---- | -------------------- | ------------------------------ |
| 0      | 3    | **Message Type**     | HEL, OPN, MSG, CLO, ERR        |
| 3      | 1    | **Chunk Type**       | F, C, A (Final/Continue/Abort) |
| 4      | 4    | **Message Size**     | Total packet length            |
| 8      | 4    | **SecureChannel ID** | 0 until channel established    |

For the 3 characters message type: 

- `HEL` – Hello (initial Client → Server handshake),
- `ACK` – Acknowledge (Server → Client Acknowledge)
- `OPN` – OpenSecureChannel
- `MSG` – Application service message (Standard service message such as Read, Write, Browse…)
- `CLO` – CloseSecureChannel
- `ERR` – Error response

For the message communication flow, this article [OPC UA Deep Dive (Part 3): Exploring the OPC UA Protocol](https://claroty.com/team82/research/opc-ua-deep-dive-part-3-exploring-the-opc-ua-protocol#The-Bits-and-Bytes-of-OPC-UA-Protocol-Structure) give a very detailed introduction and the picture below from the article gives a very clear summary:

![](doc/img/s_06.png)

Below is a simplified packet view from Wireshark with the `Binary encoding frames`, `SecureChannel metadata` and `Read/Write service bodies` section : 

![](doc/img/s_07.png)

```
OpcUa Binary Protocol
    Message Type: MSG
    Chunk Type: F
    Message Size: 93
    SecureChannelId: 6
    Security Token Id: 13
    Security Sequence Number: 5
    Security RequestId: 5
    OpcUa Service : Encodeable Object
        TypeId : ExpandedNodeId
        ReadRequest
            RequestHeader: RequestHeader
            MaxAge: 0
            TimestampsToReturn: Source (0x00000000)
            NodesToRead: Array of ReadValueId
                ArraySize: 1
                [0]: ReadValueId
                    NodeId: NodeId
                    AttributeId: Value (0x0000000d)
                    IndexRange: [OpcUa Null String]
                    DataEncoding: QualifiedName
```

#### OPC-UA Data Storage Structure

OPC UA organizes its storage data in an address space, the core elements include the Server Name, Namespaces, Objects, and Variables. In this project , we create a dictional tree structure to save the data as shown below to save the data:

```
    Server Name
        |
        DataStorage-> Namespace
                        |__ Object
                                |__ Variable = value
```

**Server Name** 

- Every OPC-UA server exposes an identity that clients can read, usually under the *Server* object. It includes: Server name / Application name, Endpoint URLs + Unique Application URI and Supported security policies. 
- Clients use this information to understand what system they are connecting to.

**Namespace**

- Namespaces prevent naming conflicts and organize the address space. 
- Each namespace is identified by an index such as: `0` for OPC UA standard namespace, `1` or `2`: Custom server-specific namespace

**Objects** 

- Object Nodes represent things in the system such as Devices, Machines, Subsystems, Functional groups. 
- Objects may contain Variables (data values), Methods (callable functions) and Other Objects (hierarchy).

**Variables** 

- Variable Nodes store the actual data values exposed by the server.
- Each variable includes : Current value, Data type, Access level, Timestamps and Monitored items for subscriptions. 



------

### Design of The Virtual PLC

In this section, I will use the workflow of how the Automatic Dependent Surveillance–Broadcast (ADS-B) system's ground station control PLC is implemented in the  [Mini OT Aviation CAT-II Airport Runway Lights Management Simulation Cyber Range ](https://www.linkedin.com/pulse/aviation-runway-lights-management-simulation-system-yuancheng-liu-5rzhc)  as an example to show the detailed design of the OPCUA Virtual PLC/RTU Simulator Framework. 

This example illustrates how a software-defined PLC can fully emulate industrial controller behavior, process I/O, and integrate with both Level-0 simulated field devices and Level-2 SCADA/HMI applications. The overall system architecture is divided into three major layers, as shown in the system workflow diagram:

![](doc/img/s_08.png)

The center portion of the diagram—Level 1 OT Controller Device—represents the Virtual PLC. This virtual controller contains Four primary components:

#### Communication Module

The Communication Module acts as the virtual PLC’s external interface to the surrounding OT ecosystem. It connects upward to Level-2/3 SCADA/HMI systems and downward to Level-0 physical world simulators.( As illustrated in the orange section of the architecture)

**OPC-UA TCP Communication Stack**

- Provides an embedded OPC-UA Server for exposing PLC I/O variables to higher-level systems.

- Uses an OPC-UA Client interface when the HMI or data archive module needs to fetch data from external devices or data services.

**UDP-Based ACARS Simulation Channel**

- The Incoming UDP ACARS message channel transfer physical world simulator's ACARS data into the virtual PLC's input hash table to simulate the PLC read real real time ADS-B information from different airport sensors/radar/antenna. 
- The Outgoing ACARS packets are send the processed ACARS message saved in PLC's output hash table and delivered back to the simulated ADS-B ground station broadcast antenna for the airplane to use.

The UDP-Based  Aircraft Communications Addressing and Reporting System (ACARS) challenge can also be replaced by other customized python interface module to simulate the electrical signal or connect to real GPIO of physical device.

#### PLC Functional Module

Represented in the light green section of the diagram, the OPC-UA PLC Function Framework is the core runtime component inside the Level-1 controller VM, the PLC functional module emulates the core behavior of the programmable logic execution:

- All incoming sensor values, contact states, and ACARS messages are stored in an internal PLC Input Variable Hash Table.
- The hash table is passed into the Ladder Logic Execution Engine, where user-defined control logic is evaluated.
- After logic execution, the computed results are written into the PLC Output Hash Table.
- These output values are then forwarded to the physical world simulator through UDP and The SCADA/HMI through OPC-UA.

#### UA Data Structure Module

Represented in the dark green section of the diagram to expose the PLC I/O data to external systems, the framework builds a complete Unified Architecture  address space. This includes:

- **UA_NameSpace** (for organizing custom PLC data)
- **UA_Object nodes** (representing logical PLC components)
- **UA_Variable nodes** (binding to each input/output hash table entry)

The UA structure is continuously synchronized with the PLC’s real-time state:

- Whenever a PLC input or output variable changes, the OPC-UA variable node is updated immediately.
- This ensures external OPC-UA Clients (SCADA, ADS-B monitoring HMI, Level-3 data center modules) always access up-to-date information.
- Two UA over write (manual) mode variable flags allow the UA store data overwrite the PLC variables to implement the HMI manual control.

#### Simulated PLC Ladder Logic Module

This module completes the closed-loop behavior of the virtual PLC, enabling realistic control of the simulated airport runway light system, ADS-B integration, timing logic, and safety interlocks. The key feature includes: 

- Parses and executes user-defined ladder logic instructions.

- Runs automatically at a configurable execution frequency (simulating a PLC’s scan rate).

- Reads values from the **input hash table**, processes rungs and logical operations, and updates the **output hash table**.

- Supports typical UA PLC data types (bool, int16, float, string) as reflected in the OPC-UA variable tree.









One additional function of the OPC-UA's ladder logic is the value over write control mode flag, each PLC variable will map to one UA variable and controlled by a overwrite (manual) mode flag, when the input manual mode UA_variable flag set to false, the related input 