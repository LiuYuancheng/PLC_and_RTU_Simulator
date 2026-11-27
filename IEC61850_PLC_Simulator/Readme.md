# Python Virtual PLC/IED Simulator With IEC 61850 MMS Communication Support for OT Cyber Twin Development

**Project Design Purpose** : In this project, I extended my previous [Python-based Virtual PLC/RTU/MU/IED Simulator Library](https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc) by introducing support for the IEC 61850 MMS (Manufacturing Message Specification) communication protocol. The original simulator library provides communication interfaces for industrial control systems using protocols includes `Modbus-TCP`, `Siemens-S7Comm`, `MQTT`, `IEC60870-5-104`, `BACnet`, `OPCUA-TCP` and `IEEE 1815-2021 DNP3.0`. After integrating IEC 61850 MMS communication capabilities, the simulator can expose simulated IED data attributes and exchange measurement, status and control-related information with external SCADA systems, HMI applications and other OT components, then it can be used for developing virtual representations of real-world industrial devices, such as WAGO PLCs (e.g., PFC100 and PFC200 series), within a software-based OT Cyber Twin environment.

The implementation consists of two main components:

- **IEC 61850 MMS Comm Library** : The library provides the minimal, dependency-free fundamental communication functions required for establishing IEC 61850 MMS client-server associations using Python's standard libraries (`socket` + `struct`). The lib is full compatible for Windows, Linux and macOS and does not require a C/C++ compiler, external IEC 61850 SDK or specialized development toolchain.
- **PLC/IED Simulator Framework** : The framework provides simulation layer for modelling operational behaviours of industrial OT field devices via VM/Docker. The framework allows multiple virtual OT devices to be instantiated and integrated into a larger OT Cyber Twin environment by processing  IEC 61850 MMS data exchange requests, interface with physical-world simulation modules, and executing the user-defined control logic. 

```python
# Author:      Yuancheng Liu
# Created:     2026/11/24
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2026 Liu Yuancheng
# License:     MIT License
```

**Table of Contents** 



------

### 1. Project Introduction