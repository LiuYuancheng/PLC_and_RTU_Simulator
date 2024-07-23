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

#### Problem[1]: RTU server execution error

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



------

#### Problem[2]: Program execution attribute missing error for latest version of python-snap7(2.0)

**OS Platform** : Windows / Linus 

**Error Message**:

```
s7commServerInit > Host IP: 0.0.0.0, Port: 102
Start the S7comm event handling loop.
Exception in thread Thread-1:
Traceback (most recent call last):
  File "/usr/lib/python3.10/threading.py", line 1016, in _bootstrap_inner
    self.run()
  File "/home/ncl/cidex2024/src/lib/rtuSimulator.py", line 207, in run
    self.server.startService(eventHandlerFun=self.ladderHandler)
  File "/home/ncl/cidex2024/src/lib/snap7Comm.py", line 311, in startService
    self.initRegisterArea()
  File "/home/ncl/cidex2024/src/lib/snap7Comm.py", line 273, in initRegisterArea
    self._server.register_area(snap7.types.srvAreaDB,
AttributeError: module 'snap7' has no attribute 'types'. Did you mean: 'type'?
```

**Type**: Setup exception

**Solution**:

For Windows platform, install the version 1.1 or 1.3 :

```
pip install setuptools
pip install python-snap7==1.1
```

or 

```
pip install python-snap7==1.3
```

For Linux install, follow the  version 1.3 directly. 

Ubuntu need to follow this link to install the lib first: https://python-snap7.readthedocs.io/en/latest/installation.html

```shell
$ sudo add-apt-repository ppa:gijzelaar/snap7
$ sudo apt-get update
$ sudo apt-get install libsnap7-1 libsnap7-dev
```

Then install version 1.3 with pip: 

```
pip install python-snap7==1.3
```



------

#### Problem[3]:  OSError: [WinError 193] %1 is not a valid Win32 application

**OS Platform** : Windows 

**Error message**: 

```
OSError: [WinError 193] %1 is not a valid Win32 application
```

Snap7 download link: https://sourceforge.net/projects/snap7/

Python version 3.12 64bit.

**Solution**:

This may because the snap7 dll file(205K 32/64 bit multi-platform Ethernet S7 PLC communication suite) may not work correct in some 64 bit system, you can down load the pure 64 bit system dll from this link and that will solve the problem.

https://github.com/LiuYuancheng/PLC_and_RTU_Simulator/tree/main/S7Comm_RTU_Simulator/WinOS_dll/64bit

For 32bit dll, you can download from this link:

https://github.com/LiuYuancheng/PLC_and_RTU_Simulator/tree/main/S7Comm_RTU_Simulator/WinOS_dll



------



> last edit by LiuYuancheng ([liu_yuan_cheng@hotmail.com](mailto:liu_yuan_cheng@hotmail.com)) by 23/07/2024 if you have any problem, please send me a message.