#-----------------------------------------------------------------------------
# Name:        uiGlobal.py
#
# Purpose:     This module is used as a local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2020/01/10
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import os

print("Current working directory is : %s" % os.getcwd())
dirpath = os.path.dirname(__file__)
print("Current source code location : %s" % dirpath)
APP_NAME = 'M221-PLC-Simulator'

#------<IMAGES PATH>-------------------------------------------------------------
IMG_FD = 'img'
ICO_PATH = os.path.join(dirpath, IMG_FD, "plcIcon.png")
BGIMG_PATH = os.path.join(dirpath, IMG_FD, "plcBg.jpg")

MBTcp_RQ = ('Transaction Identifier', 'Protocol Identifier', 'Message Length', 'Device address', 
            'Function code', 'Byte Count', 'Register value Hi (AO0)', 'Register value Lo (AO0)',
            'Register value Hi (AO1)', 'Register value Lo (AO1)', '	Register value Hi (AO2)', 
            'Register value Lo (AO2)')


#-------<GLOBAL VARIABLES (start with "g")>------------------------------------
# VARIABLES are the built in data type.
gTranspPct = 100     # Windows transparent percentage.
gUpdateRate = 1     # main frame update rate 1 sec.
gTcpMsg = ('0001', '0000', '0009', '11', '03', '06', '02', '2B', '00', '64', '00', '7F')


#-------<GLOBAL PARAMTERS>-----------------------------------------------------
iMainFrame = None   # MainFrame.
iImagePanel = None  # Image panel.
iCtrlPanel = None   # control panel
iMBmsgPanel = None 



