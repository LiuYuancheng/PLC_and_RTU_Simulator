# Python Virtual RTU/IIoT Simulator with IEC-20922 MQTT Communication Protocol

**Project Design Purpose** :  In this follow-up project, we extend the previous Python-based virtual PLC/RTU simulator project (which interfaced to SCADA systems via Modbus-TCP and S7Comm, related link:  https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc)  by adding the support for IEC-20922 Message Queuing Telemetry Transport (MQTT) protocol.  The new feature design consists of two major components:

- **MQTT Comm Module** : Implements the Message Queuing Telemetry Transport communication layer with the MQTT broker and client interface, enabling fully standardized IEC-20922  data exchange.
- **RTU/IIoT Simulator Framework** : A program to simulate the behaviors of RTU/IIoT manages virtual device message inputs and outputs, handles interactions with the physical-world simulator and execute the control logic. 

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

The Message Queuing Telemetry Transport (MQTT) is a lightweight, publish-subscribe network protocol designed for constrained devices and low-bandwidth, high-latency networks. It is the de facto messaging standard for the Internet of Things (IoT), enabling efficient machine-to-machine (M2M) communication across industries like automotive, manufacturing, and smart cities. The usage of MQTT with IIoT/RTU and the architecture is shown below:

![](doc/img/s_02.png)

We want to create a simulator module with the broker and client lib functions so when I build the cyber twin simulation system, I can use plug the MQTT Simulator modules in the other device simulation module to build the whole SCADA system which same as the one use the industry. 