#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        HvacMachineSimulator.py
#
# Purpose:     This module is a simple Heating Ventilation and Air Conditioning(HVAC)
#              machine controller simulator with the UI to control the center
#              HVAC machine
#
# Author:      Yuancheng Liu
#
# Created:     2026/01/11
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os
import sys
import time
import random
import threading

import wx

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'BACnet_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

print("Test import BACnetComm lib: ")
try:
    import BACnetComm
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

def showTestResult(expectVal, val, message):
    rst = "[o] %s pass." %message if val == expectVal else "[x] %s error, expect:%s, get: %s." %(message, str(expectVal), str(val))
    print(rst)

DEV_ID = 123456
DEV_NAME = "HVAC_Thermostat_Controller"

FRAME_SIZE = (500, 400)

class UIFrame(wx.Frame):
    """ Main UI frame window."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=FRAME_SIZE)
        #self.SetIcon(wx.Icon(gv.ICO_PATH))
        # No boarder frame:
        # wx.Frame.__init__(self, parent, id, title, style=wx.MINIMIZE_BOX | wx.STAY_ON_TOP)
        # self.SetBackgroundColour(wx.Colour(30, 40, 62))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))

        self.updateLock = False 
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(500)

    def periodic(self, event):
        """ Call back every periodic time."""
        now = time.time()
        if (not self.updateLock) and now - self.lastPeriodicTime >= 0.5:
            print("periodic(): main frame update at %s" % str(now))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class mainApp(wx.App):
    def OnInit(self):
        iMainFrame = UIFrame(None, -1, DEV_NAME)
        iMainFrame.Show(True)
        return True

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app = mainApp(0)
    app.MainLoop()
