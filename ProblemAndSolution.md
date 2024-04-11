# **Problem and Solution**

**In this document we will share the valuable problems and the solution we meet during the project development as a reference menu for the new programmer who may take over this project for further development. Later we will sort the problem based on the problem <type>.**

[TOC]

**Format:** 

**Problem**: ( Situation description )

**OS Platform** :

**Error Message**:

**Type**: Setup exception

**Solution**:

**Related Reference**:

------

###### Problem[1]: RTU server execution error

**OS Platform** : Windows / Linus 

**Error Message**:

```
Test import lib: 
- pass
Import snap7 dll path: c:\Works\TechArticles\Python_PLC_Simulator\S7Comm_RTU_Simulator\src\snap7.dll
- pass
Init the server and memory address
s7commServer > Load the Snap7 Win-OS lib-dll file : c:\Works\TechArticles\Python_PLC_Simulator\S7Comm_RTU_Simulator\src\snap7.dll
s7commServerInit > Host IP: 0.0.0.0, Port: 102
Test set and values:
 - test set bool value : pass
 - test set int value   : pass
 - test set real value  : pass
Server start
Start the S7comm event handling loop.
Error: startService() Error to start s7snap server: exception: access violation writing 0x005EEF4C
```

**Type**: Setup exception

**Solution**:

This error is because using the 32bit python, install the 64bit version python will fix the problem.

**Related Reference**: https://github.com/gijzelaerr/python-snap7/issues/23