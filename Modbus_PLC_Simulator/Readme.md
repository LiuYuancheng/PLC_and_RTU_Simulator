# Modbus PLC Simulator [Usage Manual]

```powershell
# Library Usage Manual
```

**Project Design Purpose**: The main objective of this project is to develop a Python library capable of simulating the OT PLCs (Programmable Logic Controllers)  device which use the Modbus-TCP protocol. 

This component emulates the functionality of a PLC, the design follows the core operation logic of Schneider M221 PLC . It includes Modbus TCP client and server functionalities, ladder logic simulation, PLC register-memory-coil control, and interfaces for connecting with real-world physical or virtual OT devices. The program module workflow diagram is shown below:

![](../doc/img/plcWorkflow.png)

```
# Version:     v0.1.3
# Created:     2023/06/22
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
```

**Table of Contents** 

[TOC]

------

### Introduction 

PLCs are programmable devices designed primarily for controlling machinery and processes in industrial environments. They are used to automate sequences of operations, monitor inputs from sensors, and control outputs to actuators based on programmed logic. This library provides the software simulation solution for user to build their customized PLC by using a virtual machine, physical server or Raspberry PI, then integrated the emulation App as a bridge to link the OT level-0 components (physical field device) and level-2/3 components (HMI or remote field control console). This lib provides two main modules:

