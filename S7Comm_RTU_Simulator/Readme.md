# S7Comm Remote Terminal Unit Simulator 

**Project Design Purpose**: The main objective of this project is develop a  Python library capable of simulating the OT RTUs (Remote Terminal Units) device which use the Siemens S7Comm protocol. 

This component can simulate both PLC and RTU operations, the design is based on the core operation logic of Siemens Simatic S7-1200 PLC and SIMATIC RTU3000C, respectively. It incorporates S7Comm client and server functionalities, manages PLC/RTU memory, performs ladder logic and RTU logic simulations, and provides interfaces for connecting with real-world emulators.

```
# version:     v0.1.3
# Created:     2024/02/21
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
```

[TOC]

------

### Introduction 

RTUs are specialized devices used primarily for remote monitoring and control of distributed assets in industrial applications, such as in oil and gas pipelines, water distribution systems, and electrical substations. They typically collect data from sensors and equipment in remote locations and transmit it to a central control system for monitoring and analysis. This library provide the software simulation solution to all user can build their customized RTU by using the VM, physical server or Raspberry PI, then integrated the emulation App as a bridge to link the OT level-0 and level-2/3 network.

The program module workflow diagram is shown below:

![](../doc/img/rtuWorkflow.png)

This lib provide two main modules with below components:

 

 

