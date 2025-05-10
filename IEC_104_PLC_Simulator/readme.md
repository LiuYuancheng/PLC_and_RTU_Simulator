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