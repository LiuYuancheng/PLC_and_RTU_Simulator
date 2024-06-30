# Python Physical PLC Communication Clients

**Project Design Purpose**: The main objective of this project is to develop a Python library capable of communicate with two different widely used PLC : Schneider M221 PLC and Siemens S7-1200 to read and write the PLC memory data. We have developed two distinct clients, each tailored to the specific protocols of these PLCs. Additionally, we will provide a multithreading wrapper class, enabling integration of the clients into your program's main thread or running them in parallel to regularly fetch the PLC state. The system overview is shown below:

![](img/title.png)

```
# Created:     2024/06/29
# Version:     v0.1.3
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
```

**Table of Contents** 

[TOC]

------

### Introduction

This project provides two different Python PLC communication clients to connect with two types of physical PLCs: the Schneider Modicon M221 and the Siemens SIMATIC S7-1200. The clients use the Modbus-TCP and S7Comm protocols, respectively. These clients offer APIs to read and write byte data from memory addresses in the PLC ladder logic, fetch the state of PLC input contacts, and change the state of PLC output coils. The project includes two libraries:

- **M221PlcCLient Module** : This module communicates with the Schneider Modicon M221 via Modbus-TCP. It provides API functions to read and write byte data from memory `%MXX` address tags and includes a multithreading client wrapper for easy integration.
-  **S71200PlcClient Module** : This module communicates with the Siemens SIMATIC S7-1200 via S7Comm. It offers API functions to read and write data (bool, int, word, float) from contacts `%I_.x`, memory `%M_.x`, and coils `%Q_.x`. It also includes a multithreading client wrapper for seamless integration.



------

### Program Design

For the program design, please refer to this document: https://github.com/LiuYuancheng/IT_OT_IoT_Cyber_Security_Workshop/blob/main/OT_System_Attack_Case_Study/PLC_Doc/Python_PLC_Communication.md

