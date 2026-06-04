# Python Virtual RTU/IIoT Simulator with IEC-20922 MQTT Communication Protocol

**Project Design Purpose** : In this project, we extend the previous Python-based virtual PLC/RTU simulator library (which interfaced to SCADA systems via Modbus-TCP and S7Comm, related link:  https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc)  by adding the support function for IEC-20922 Message Queuing Telemetry Transport (MQTT) protocol.  The new feature design consists of two major components:

- **MQTT Communication Module** : The MQTT Communication Module implements the IEC 20922-compliant MQTT protocol stack, providing connectivity between virtual devices and MQTT brokers to support the message publishing and subscription, topic management, telemetry data exchange, and command/control communication. 
- **RTU/IIoT Simulator Framework** : The RTU/IIoT Simulator Framework models the operational behavior of industrial field devices, remote terminal units (RTUs), and IIoT sensors. It manages virtual device inputs and outputs, processes MQTT messages, interfaces with physical-world simulation modules, and executes user-defined control logic.

```python
# Author:      Yuancheng Liu
# Created:     2026/06/01
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 Liu Yuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### 1. Project Introduction

The **Message Queuing Telemetry Transport (MQTT)** protocol, standardized as **IEC 20922**, is a lightweight publish-subscribe messaging protocol designed for resource-constrained devices and low-bandwidth networks. Due to its simplicity, scalability, and low communication overhead, MQTT has become one of the most widely adopted communication standards in the Industrial Internet of Things (IIoT) domain and machine-to-machine (M2M) communication across industries such as manufacturing, energy, transportation, and smart infrastructure. 

In a typical IIoT deployment, field devices publish operational data to a centralized MQTT broker, while supervisory systems, Human-Machine Interfaces (HMIs), mobile applications, and monitoring platforms subscribe to the required data streams. This decoupled communication model simplifies system integration and provides a flexible architecture for large-scale industrial monitoring and control systems The usage case example of MQTT with IIoT/RTU and the architecture is shown below:

![](doc/img/s_02.png)

To support the development of industrial cyber twins and OT cybersecurity research platforms, I developed a Python-based Virtual RTU/IIoT Simulator with MQTT Communication Support. The project provides reusable MQTT Broker and MQTT Client modules that can be integrated into different cyber-twin components. 

#### 1.1 System Overview

The simulator is **NOT** 1:1 emulate the real RTU/IIoT/MU hardware function, it focuses on reproducing the **core operational behaviors** commonly found in MQTT-enabled industrial devices, including:

- Device variable and tag storage management
- MQTT publish and subscribe communication mechanisms
- Telemetry and control data exchange workflows
- Device control logic execution cycles
- Interactions between field devices, controllers, and supervisory systems

This lightweight design provides an effective educational, prototyping, and research environment for:

- Academic researchers studying industrial automation and IIoT architectures
- Students learning OT communication protocols and MQTT device behaviors
- Developers building, testing, or validating MQTT-enabled applications
- OT cybersecurity professionals analyzing industrial communication flows and attack scenarios

#### 1.2 System ISA-95 Architecture 

The simulator enables users to construct cyber twins' components that mirror the hierarchical architecture commonly found in modern industrial environments. As shown in the figure below, the framework follows a simplified four-level OT architecture based on the ISA-95 model as shown in the below diagram : 

![](doc/img/s_03.png)

- At **Level 0 (Physical Process Field I/O Devices)**, simulated IIoT devices, sensors, and metering units generate operational data representing measurements collected from physical processes. At **Level 1 (Controller LAN)**, virtual RTUs process the incoming data and operate as MQTT clients, publishing telemetry and status information to the MQTT Broker.
- The **MQTT Broker Server**, located at **Level 2 (Control Center Processing LAN)**, acts as the central communication hub. It receives published messages from field devices, manages topic subscriptions, stores device data, and executes server-side processing logic when required. Control HMIs and operator consoles within the same network segment can also subscribe to or publish MQTT messages through the broker.
- At **Level 3 (Operations Management Zone)**, supervisory applications such as monitoring workstations, engineering desktops, mobile devices, and touchscreen operator panels run MQTT client services to subscribe to device data, visualize process information, and issue control commands. 

This architecture closely resembles real-world IIoT and SCADA deployments while remaining lightweight, extensible, and suitable for simulation, training, and cybersecurity experimentation.



------

### 2. MQTT Protocol Background Knowledge

Message Queuing Telemetry Transport (MQTT) is a lightweight messaging protocol standardized as **IEC 20922**. It follows a **publish-subscribe communication model**, where devices do not communicate directly with one another. Instead, all messages are exchanged through a central **MQTT Broker**.

In an MQTT system, devices acting as **publishers** send data to specific topics hosted by the broker, while **subscribers** receive messages from topics they are interested in. This architecture reduces communication complexity, improves scalability, and enables efficient operation over low-bandwidth or unreliable networks.

#### 2.1 MQTT Protocol Packet Structure

MQTT communication is performed through a series of protocol packets exchanged between clients and the broker. Regardless of packet type, every MQTT packet consists of three logical sections:

1. Fixed Header (Mandatory)
2. Variable Header (Optional)
3. Payload (Optional)

The general MQTT packet structure is illustrated below:

![](doc/img/s_04.png)

For the detail packet analysis, please refer to below document : 

- http://www.steves-internet-guide.com/mqtt-protocol-messages-overview/
- https://www.hivemq.com/blog/mqtt-packets-comprehensive-guide/

#### 2.2 MQTT Protocol Key Features

**Lightweight Header:** Protocol packets are tiny (often just a few bytes), which preserves bandwidth, memory, and battery life. 

**Quality of Service (QoS):** Developers can choose the level of delivery assurance:

- *QoS 0 (At most once):* Fast delivery but messages may be lost.
- *QoS 1 (At least once):* Delivery guaranteed, but duplicates can occur.
- *QoS 2 (Exactly once):* Message delivered exactly once, with no loss or duplication. 

**Last Will and Testament (LWT):** Allows a device to pre-register a message with the broker that gets automatically broadcasted if the device unexpectedly goes offline



------

### 3. Design of The MQTT Virtual IIoT and RTU

In this section I will introduce the detail design of the module and use the simulated factory air vacuum system and IoT drone data receiver how these MQTT communication modules are integrated in the different components of the cyber twin system. 

#### 3.1 Communication Module Design

For the MQTT Broker communication module, the packet type covered is shown below : 

![](doc/img/s_05.png)

```python
# MQTT packet type constants (currently what we need, may add more in the future)
CONNECT     = 0x10
CONNACK     = 0x20
PUBLISH_Q0  = 0x30  # QoS level 0 (At most once) currently we use the QoS level0 DUP = 0, Retain = 0
PUBLISH_Q1  = 0x32  # QoS level 1 (At least once)
PUBLISH_Q2  = 0x34  # QoS level 2 (Exactly once)
PUBACK      = 0x40
SUBSCRIBE   = 0x82
SUBACK      = 0x90
PINGREQ     = 0xC0
PINGRESP    = 0xD0
DISCONNECT  = 0xE0
```

For each of the broker module, when a new broker is connected, it will start a client handler running in the sub-thread to handle the data publish and subscribe request. For the publish request, the parameters value get request topic I use `parameters/get/<topicName>` , the value set request topic I use `parameters/set/<topicName>`. For the subscribe request the parameter topic I use `parameters/value/<topicName>`. 

In the broker, if we need to execute some logic to process some data there is one interface function `executeLogic` is provided: 

```python
def executeLogic(self):
    """ Interface function in the main loop for the MQTT broker to execute the control logic."""
	pass
```

So you need to create a broker class inherit this MQTTBroker class and overwrite this interface function to add the logic you want. Then the function will be executed every time when a new value is published set to a parameter. In your main function thread you can also call this function periodically to regularly process the current stored data. 

For the MQTT client module, I use the PAHO-MQTT lib: https://pypi.org/project/paho-mqtt/ to build the functions of the client with the `getParmVal()` to get the parameter's value from broker, `setParmVal()` to set the parameter value to a broker and `watch()/watchall()` to continues subscribe parameters from broker. 



