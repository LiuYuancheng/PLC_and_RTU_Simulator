# Python Virtual PLC & RTU Simulator

**Program Design Purpose**: The objective of this program is create a python program which can simulate the fundamental function of two kinds of common industrial automation OT-devices, PLC (Programmable Logic Controller) and RTU (Remote Terminal Unit). The program can run on different OS to convert a VM/Machine to be a virtual PLC/RTU, which can handle the request from SCADA-HMI system via Modbus TCP or S7Comm, then simulate the real PLC/RTU device's electrical signal changes then use UDP to feed the changes to the real-world emulation program. The project contents two main project:

- **PLC Simulation System [ `Modbus` ]**: A PLC simulate system follow the operation logic of the  Schneider M221 PLC with the Modbus-TCP client, Modbus-TCP server, Ladder logic simulation, PLC register-memory-coil control,Real-world emulator components connection interface. 
- **RTU Simulation System [ `S7Comm` ]**: A PLC and RTU simulation system follow the operation logic of the Siemens Simatic S7-1200 PLC and SIMATIC RTU3000C with the S7comm client, S7comm server, PLC/RTU memory management, Ladder logic / RTU logic simulation, real-world emulator components connection interface.

The system overview is shown below : 

![](doc/img/overview.png)

```
# version:     v0.1.3
# Created:     2024/02/21
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### Introduction



We developed virtual PLC emulator program which can auto run simple ladder logic and provided below customized function for flexible usage: 

- Emulate Schneider M22X Modbus-TCP [port 502] Communication protocol 
- Emulate Siemens S71200 S7comm [port 102] Communication protocol 
- Customized software define ladder diagram execution priority 
- UDP interface for electrical signal (such as voltage) connection emulation to connect to the real world.
- Simulate the PLC ladder logic execution with customizable time clock cycle configuration for education purpose. 
- Simulate the multiple PLCs master-slave connection (DCM-DCM with RS422 multi-dop connection).
- Simulate the PLC access limitation (IP addresses allow read list / allow set list) config. 



------

### Background Knowledge 

##### Difference Between Modbus TCP and S7comm 

Modbus TCP and S7Comm are both communication protocols used in OT environment industrial automation, but they are associated with different manufacturers and have some differences in their features and implementations:

1. **Origin and Manufacturers:**
   - **Modbus TCP:** Modbus is an open-source protocol developed by Modicon (now Schneider Electric). Modbus TCP is an Ethernet-based implementation of the Modbus protocol.
   - **S7Comm:** S7Comm is a protocol developed by Siemens for communication with their programmable logic controllers (PLCs), primarily in the Simatic S7 series.
2. **Vendor Support:**
   - **Modbus TCP:** Being an open protocol, Modbus TCP is supported by a wide range of industrial automation equipment manufacturers.
   - **S7Comm:** S7Comm is proprietary to Siemens, so it's primarily used with Siemens PLCs and devices.
3. **Functionality and Features:**
   - **Modbus TCP:** Modbus TCP is relatively simple and lightweight, making it easy to implement and suitable for basic communication needs in industrial automation. It supports functions such as reading and writing data registers, reading input registers, and controlling discrete outputs.
   - **S7Comm:** S7Comm is more feature-rich and comprehensive, offering advanced functionality tailored specifically for Siemens PLCs. It supports a broader range of data types, diagnostic capabilities, and features like access to PLC hardware information.
4. **Performance and Efficiency:**
   - **Modbus TCP:** Modbus TCP tends to be simpler and lighter, which can result in lower overhead and faster communication in certain scenarios, especially for smaller-scale systems.
   - **S7Comm:** S7Comm may offer better performance and efficiency in larger and more complex industrial automation environments due to its optimized design for Siemens PLCs.
5. **Security:**
   - **Modbus TCP:** Modbus TCP lacks built-in security features, although it can be used over VPNs or in conjunction with additional security measures to secure communication.
   - **S7Comm:** Siemens has implemented various security features in S7Comm, such as encryption and authentication, to ensure secure communication between devices.

In summary, while both Modbus TCP and S7Comm serve similar purposes in industrial automation, they differ in terms of their origin, vendor support, functionality, performance, and security features. The choice between them often depends on factors such as the specific requirements of the automation system, the compatibility with existing equipment, and the preferences of the system integrator or end-user.









This is the main simulator UI:

![](DesignDoc/img/mainUI.png)

https://medium.com/@pt.artem/how-to-use-python-to-build-a-simple-client-server-based-on-the-s7-protocol-f4b96e563cc1

https://python-snap7.readthedocs.io/en/latest/_modules/snap7/server.html#Server
