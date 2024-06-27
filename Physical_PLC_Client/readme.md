# Physical PLC Communication Clients

**Project Design Purpose**: The main objective of this project is to develop a Python library capable of communicate with two different widely used PLC : Schneider M221 PLC and Siemens S7-1200 to read and write the PLC memory data. We will develop 2 different clients to talk to the PLCs with different protocol and provide the multi-threading wrapper class so people can integrate the client in their program's main thread or making running parallel to fetch the PLC state regularly.  

```
# Created:     2024/06/25
# Version:     v0.1.3
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
```

**Table of Contents** 

[TOC]

------

### Introduction

The project will provide two different python PLC communication clients use to connect to two different kind of physical PLC (Schneider Modicon M221 or Siemens  SIMATIC S7-1200) via Modbus-TCP or S7Comm protocol. The client will provide the API to read and write the bytes data from memory address in the PLC ladder logic then fetch the state of the PLC input contact and change the PLC output coils state. Two libraries are included in:

- **M221PlcCLient Module** : Client module used to communicate Schneider Modicon M221 via Modbus-TCP, it provide the memory `% MXX` address tag byte data read and write API function and the multi-threading client wrapper for integration. 
-  **S71200PlcClient Module** : Client module used to communicate Siemens  SIMATIC S7-1200 via S7Comm, it provide the contact `% i_.x`, memory `% m_.x` and coil `% q_.x` data (bool, int, world, float) read and write API function and the multi-threading client wrapper for integration. 



------

### Program Design



How to use Python Program to Communicate with Schneider M221 PLC or Siemens S7-1200 PLC

