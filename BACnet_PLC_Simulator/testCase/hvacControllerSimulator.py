#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        HvacControllerSimulator.py
#
# Purpose:     This module is a simple building center Heating Ventilation and 
#              Air Conditioning(HVAC) wall thermostat controller simulator with 
#              the UI and use BACnet to connect to the HVAC machine simulator 
#              module <HvacMachineSimulator.py>
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
import threading

import wx
import knob # use knob to build the temperature control panel https://github.com/kdschlosser/wxVolumeKnob

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

#-----------------------------------------------------------------------------
DEV_ID = 123456
DEV_NAME = "HVAC_Thermostat_Controller"
HVAC_IP = '127.0.0.1'

PARM_ID1 = 1
PARM_ID2 = 2
PARM_ID3 = 3
PARM_ID4 = 4
PARM_ID5 = 5
PARM_ID6 = 6

PARM_ID11 = 11
PARM_ID12 = 12
PARM_ID13 = 13

FRAME_SIZE = (600, 450)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class BACnetClientThread(threading.Thread):
    def __init__(self, port=47808):
        threading.Thread.__init__(self)
        self.client = BACnetComm.BACnetClient(DEV_ID, DEV_NAME, HVAC_IP, 47808)
        self.terminate = False 
        self.powerState = 0 
        self.tempVal = 24.0
        self.humidityVal = 50
        self.compressVal = 1
        self.heaterVal = 1
        self.fanVal = 5

    def run(self):
        print("start the data fetching loop")
        while not self.terminate:
            self.powerState = self.client.readObjProperty(HVAC_IP, PARM_ID13)
            time.sleep(0.1)
            self.tempVal = self.client.readObjProperty(HVAC_IP, PARM_ID3)
            time.sleep(0.1)
            self.humidityVal = self.client.readObjProperty(HVAC_IP, PARM_ID4)
            time.sleep(0.1)
            self.compressVal = self.client.readObjProperty(HVAC_IP, PARM_ID5)
            time.sleep(0.1)
            self.heaterVal = self.client.readObjProperty(HVAC_IP, PARM_ID6)
            time.sleep(0.1)
            self.fanVal = self.client.readObjProperty(HVAC_IP, PARM_ID12)
            time.sleep(2)
            print(str(self.getData()))

    def getData(self):
        return (self.powerState, self.tempVal, self.humidityVal, self.compressVal, self.heaterVal, self.fanVal)

    def setValue(self, parmId, value):
        self.client.writeObjProperty(HVAC_IP, parmId, value)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class UIFrame(wx.Frame):
    """ Main UI frame window."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=FRAME_SIZE)
        #self.SetIcon(wx.Icon(gv.ICO_PATH))
        # No boarder frame:
        # wx.Frame.__init__(self, parent, id, title, style=wx.MINIMIZE_BOX | wx.STAY_ON_TOP)
        # self.SetBackgroundColour(wx.Colour(30, 40, 62))
        
        self.powerState = 0 
        self.tempVal = 24.0
        self.humidityVal = 50
        self.compressVal = 1
        self.heaterVal = 1
        self.fanVal = 5

        self.targetTemp = self.tempVal
        
        self.SetBackgroundColour(wx.Colour('BLACK'))
        self.SetSizer(self._buidltUISizer())

        self.hvacConnector = BACnetClientThread()
        self.hvacConnector.start()

        self.updateLock = False 
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(500)

    #-----------------------------------------------------------------------------
    def _buidltUISizer(self):
        """ Build the main UI sizer."""
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        # Add the time label
        font0 = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        font1 = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        font2 = wx.Font(24, wx.DECORATIVE, wx.NORMAL, wx.BOLD)

        mainSizer.AddSpacer(5)
        self.timeLabel = wx.StaticText(self, label=time.strftime("%b %d %Y %H:%M:%S", time.localtime(time.time())))
        self.timeLabel.SetFont(font1)
        self.timeLabel.SetForegroundColour(wx.Colour(193, 229, 245))
        mainSizer.Add(self.timeLabel, flag=wx.CENTRE, border=2)
        mainSizer.AddSpacer(5)
        mainSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(600, -1), style=wx.LI_HORIZONTAL), flag=wx.LEFT, border=2)
        mainSizer.AddSpacer(5)
        # Added the data display sizer
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(5)

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.AddSpacer(5)
        lb0 = wx.StaticText(self, label="HVAC State : ")
        lb0.SetFont(font0)
        lb0.SetForegroundColour(wx.Colour(193, 229, 245))
        vbox1.Add(lb0, flag=wx.LEFT, border=2)
        vbox1.AddSpacer(5)
        self.stateLabel = wx.StaticText(self, label="Power Off")
        self.stateLabel.SetFont(font1)
        self.stateLabel.SetForegroundColour(wx.Colour('GREY'))
        vbox1.Add(self.stateLabel, flag=wx.CENTER, border=2)
        vbox1.AddSpacer(10)

        lb1 = wx.StaticText(self, label="Temperature : ")
        lb1.SetFont(font0)
        lb1.SetForegroundColour(wx.Colour(193, 229, 245))
        vbox1.Add(lb1, flag=wx.LEFT, border=2)
        vbox1.AddSpacer(5)
        self.tempLabel = wx.StaticText(self, label="24.0 °C")
        self.tempLabel.SetFont(font2)
        self.tempLabel.SetForegroundColour(wx.Colour(193, 229, 245))
        vbox1.Add(self.tempLabel, flag=wx.CENTER, border=2)
        vbox1.AddSpacer(10)
        
        lb2 = wx.StaticText(self, label="Humidity : ")
        lb2.SetFont(font0)
        lb2.SetForegroundColour(wx.Colour(193, 229, 245))
        vbox1.Add(lb2, flag=wx.LEFT, border=2)
        vbox1.AddSpacer(5)
        self.humiLabel = wx.StaticText(self, label="50.0 %")
        self.humiLabel.SetFont(font1)
        self.humiLabel.SetForegroundColour(wx.Colour(193, 229, 245))
        vbox1.Add(self.humiLabel, flag=wx.CENTER, border=2)
        vbox1.AddSpacer(5)

        self.compressLb = wx.StaticText(self, label="Compressor State : Working")
        self.compressLb.SetFont(font0)
        self.compressLb.SetForegroundColour(wx.Colour(193, 229, 245))
        vbox1.Add(self.compressLb, flag=wx.LEFT, border=2)
        vbox1.AddSpacer(10)

        self.heaterLb = wx.StaticText(self, label="Heater State : Working")
        self.heaterLb.SetFont(font0)
        self.heaterLb.SetForegroundColour(wx.Colour(193, 229, 245))
        vbox1.Add(self.heaterLb, flag=wx.LEFT, border=2)
        vbox1.AddSpacer(10)

        lb3 = wx.StaticText(self, label="Fan Speed :")
        lb3.SetFont(font0)
        lb3.SetForegroundColour(wx.Colour(193, 229, 245))
        vbox1.Add(lb3, flag=wx.LEFT, border=2)
        vbox1.AddSpacer(5)
        self.gauge = wx.Gauge(self, range = 8, size = (250, 25), style =  wx.GA_HORIZONTAL)
        self.gauge.SetValue(int(self.fanVal))
        vbox1.Add(self.gauge, flag=wx.CENTER, border=2)
        hbox.Add(vbox1, flag=wx.LEFT, border=2)

        hbox.AddSpacer(5)
        hbox.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 300), style=wx.LI_VERTICAL), flag=wx.LEFT, border=2)
        hbox.AddSpacer(5)
        
        self.ctrl = knob.KnobCtrl(self, value=24, minValue=16, maxValue=36, increment=.5, size=(300, 300))
        self.ctrl.ShowToolTip = False
        self.ctrl.ShowPointer = True
        self.ctrl.ShowValue = True
        self.ctrl.GaugeText = '°C\n\n'
        self.ctrl.GaugeImage = wx.Image(dirpath+'/img/thermometer.png')
        self.ctrl.GaugeImagePos = 0
        self.ctrl.ShowScale = True
        self.ctrl.SetThumbSize(5)
        self.ctrl.SetTickFrequency(0.5)
        self.ctrl.SetTickColours(['#ffffff', '#ADD8E6FF', '#03C03CFF', '#FF6347FF'])
        self.ctrl.SetTickColourRanges([25, 50, 75, 100])
        self.ctrl.SetBackgroundColour(wx.Colour(80, 80, 80))
        #self.ctrl.SetPrimaryColour((33, 36, 112, 255))
        self.ctrl.SetSecondaryColour('#1e90ff')
        self.ctrl.SetDefaultTickColour('#ffffff') # White
        self.ctrl.SetHotSpots()
        self.ctrl.SetAlwaysTickColours(True)

        self.ctrl.InsideScale = False
        self.ctrl.Bind(wx.EVT_SCROLL, self.on_event)
        self.ctrl.Bind(wx.EVT_LEFT_UP, self.on_focus_event)

        hbox.Add(self.ctrl, flag=wx.LEFT, border=2)
        mainSizer.Add(hbox, flag=wx.LEFT, border=2)
        mainSizer.AddSpacer(5)
        mainSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(600, -1), style=wx.LI_HORIZONTAL), flag=wx.LEFT, border=2)
        mainSizer.AddSpacer(5)

        gSizer = wx.GridSizer(1, 5, 2, 2)
        pwrBt = wx.Button(self, label ='POWER', size =(110, 25))
        pwrBt.Bind(wx.EVT_BUTTON, self.onPowerChange)
        gSizer.Add(pwrBt, flag=wx.CENTER, border=2)

        coolBt = wx.Button(self, label ='COOLING', size =(110, 25))
        coolBt.Bind(wx.EVT_BUTTON, self.onCoolingChange)
        gSizer.Add(coolBt, flag=wx.CENTER, border=2)

        heatBt = wx.Button(self, label ='HEATING', size =(110, 25))
        heatBt.Bind(wx.EVT_BUTTON, self.onHeatingChange)
        gSizer.Add(heatBt, flag=wx.CENTER, border=2)

        fanDownBt = wx.Button(self, label ='FAN [-]', size =(110, 25))
        fanDownBt.Bind(wx.EVT_BUTTON, self.onFanSpeedDown)
        gSizer.Add(fanDownBt, flag=wx.CENTER, border=2)

        fanUpBt = wx.Button(self, label ='FAN [+]', size =(110, 25))
        fanUpBt.Bind(wx.EVT_BUTTON, self.onFanSpeedUp)
        gSizer.Add(fanUpBt, flag=wx.CENTER, border=2)

        mainSizer.Add(gSizer, flag=wx.CENTER, border=2)
        return mainSizer

    #-----------------------------------------------------------------------------
    def onPowerChange(self, event):
        if self.powerState == 0:
            print("onPowerChange: Power On")
            self.hvacConnector.setValue(PARM_ID13, 1)
        else:
            print("onPowerChange: Power Off")
            self.hvacConnector.setValue(PARM_ID13, 0)

    #-----------------------------------------------------------------------------
    def onCoolingChange(self, event):
        if self.powerState != 1:
            print("onCoolingChange: compressor on")
            self.hvacConnector.setValue(PARM_ID13, 1)

    def onHeatingChange(self,event):
        if self.powerState != 2:
            print("onHeatingChange: heater on")
            self.hvacConnector.setValue(PARM_ID13, 2)

    def onFanSpeedDown(self, event):
        val = max(1, int((self.fanVal - 1)))
        self.hvacConnector.setValue(PARM_ID12, val)

    def onFanSpeedUp(self, event):
        val = min(8, int((self.fanVal + 1)))
        self.hvacConnector.setValue(PARM_ID12, val)

    def on_event(self, event):
        print (event, "Position:", event.Position)
        self.targetTemp = round(event.Position, 1)

    # Prevent keyboard event taking focus from ctrl
    def on_focus_event(self, event):
        self.ctrl.SetFocus()
        print(event, "-- send control request", event.Position)
        event.Skip()
        self.hvacConnector.setValue(PARM_ID11, self.targetTemp)

    #-----------------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        now = time.time()
        if (not self.updateLock) and now - self.lastPeriodicTime >= 0.5:
            print("periodic(): main frame update at %s" % str(now))
            dataList = self.hvacConnector.getData()
                    
            self.powerState = dataList[0]
            self.tempVal = dataList[1]
            self.humidityVal = dataList[2]
            self.compressVal = dataList[3]
            self.heaterVal = dataList[4]
            self.fanVal = dataList[5]

            self.timeLabel.SetLabel(time.strftime("%b %d %Y %H:%M:%S", time.localtime(time.time())))
            if self.powerState == 0:
                self.stateLabel.SetLabel('Power OFF')
                self.stateLabel.SetForegroundColour(wx.Colour('GREY'))
            elif self.powerState == 1:
                self.stateLabel.SetLabel('Cooling')
                self.stateLabel.SetForegroundColour(wx.Colour('GREEN'))
            else:
                self.stateLabel.SetLabel('Heating')
                self.stateLabel.SetForegroundColour(wx.Colour('YELLOW'))
            
            self.tempLabel.SetLabel(" %s °C" %str(round(self.tempVal, 1)))

            self.humiLabel.SetLabel(" %s %%" %str(round(self.humidityVal, 1)))
            stateStr = [' OFF ', 'IDLE', 'WORKING']
            
            self.compressLb.SetLabel("Compressor State : %s" %str(stateStr[int(self.compressVal)]))
            self.heaterLb.SetLabel("Heater State : %s" %str(stateStr[int(self.heaterVal)]))

            self.gauge.SetValue(int(self.fanVal))
            self.lastPeriodicTime = now

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
