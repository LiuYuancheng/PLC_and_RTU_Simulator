# Python Virtual RTU Simulator With IEEE 1379-2000 DNP3.0 Communication Protocol

**Project Design Purpose** : In this project, I did extend my previous Python-based virtual PLC/RTU simulator library (which interfaced to SCADA systems via Modbus-TCP and S7Comm, related link:  https://www.linkedin.com/pulse/python-virtual-plc-rtu-simulator-yuancheng-liu-elkgc)  by adding the support function for IEEE 1379-2000 Distributed Network Protocol 3 (DNP3) protocol. The new feature design consists of two major components:

- **DNP3.0 Communication Lib** : The DNP3.0 Communication Module implements a minimal and dependency-free DNP3 protocol stack, providing the connectivity between the master and outstation 

