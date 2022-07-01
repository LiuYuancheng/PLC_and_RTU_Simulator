#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        uiRun.py
#
# Purpose:     This module is used as a sample to create the main wx frame.
#
# Author:      Yuancheng Liu
#
# Created:     2022/07/01
# Copyright:   YC @ National Cybersecurity R&D Laboratories
# License:     YC
#-----------------------------------------------------------------------------

import wx
import wx.grid
from datetime import datetime
import plcSimuGobal as gv

class LadderPanel(wx.Panel): 

    def __init__(self, parent, panelSize=(650, 650)):
        wx.Panel.__init__(self, parent, size=panelSize)
        self.SetSizer(self._buidUISizer())

    def _buidUISizer(self):
        """ build the control panel sizer. """
        flagsR = wx.LEFT
        ctSizer = wx.BoxSizer(wx.VERTICAL)

        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.Button(self, label=' ', size=(30, 30)), flag=wx.CENTER, border=0)
        
        self.c1bt = wx.Button(self, label='Contact-1', size=(100, 30))
        hbox0.Add(self.c1bt, flag=flagsR, border=0)

        self.c2bt = wx.Button(self, label='Contact-2', size=(100, 30))
        hbox0.Add(self.c2bt, flag=flagsR, border=0)

        self.c3bt = wx.Button(self, label='Contact-3', size=(100, 30))
        hbox0.Add(self.c3bt, flag=flagsR, border=0)

        self.c4bt = wx.Button(self, label='Contact-4', size=(100, 30))
        hbox0.Add(self.c4bt, flag=flagsR, border=0)

        self.c5bt = wx.Button(self, label='Contact-5', size=(100, 30))
        hbox0.Add(self.c5bt, flag=flagsR, border=0)

        self.c6bt = wx.Button(self, label='Coil', size=(100, 30))
        hbox0.Add(self.c6bt, flag=flagsR, border=0)
        
        ctSizer.Add(hbox0, flag=flagsR, border=0)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.v1bt = wx.Button(self, label='I1', size=(30, 100))
        vbox.Add(self.v1bt, flag=flagsR, border=0)

        self.v2bt = wx.Button(self, label='I2', size=(30, 100))
        vbox.Add(self.v2bt, flag=flagsR, border=0)

        self.v3bt = wx.Button(self, label='I3', size=(30, 100))
        vbox.Add(self.v3bt, flag=flagsR, border=0)

        self.v4bt = wx.Button(self, label='I4', size=(30, 100))
        vbox.Add(self.v4bt, flag=flagsR, border=0)

        self.v5bt = wx.Button(self, label='I5', size=(30, 100))
        vbox.Add(self.v5bt, flag=flagsR, border=0)

        self.v6bt = wx.Button(self, label='I6', size=(30, 100))
        vbox.Add(self.v6bt, flag=flagsR, border=0)

        hbox1.Add(vbox, flag=flagsR, border=0)

        ladderEditor = LadderEditor(self)

        hbox1.Add(ladderEditor, flag=flagsR, border=0)

        ctSizer.Add(hbox1, flag=flagsR, border=0)

        return ctSizer

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class LadderEditor(wx.Panel):
    """ Panel to display image. """

    def __init__(self, parent, panelSize=(600, 600)):
        wx.Panel.__init__(self, parent, size=panelSize)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.panelSize = panelSize
        self.bmp = wx.Bitmap(gv.BGIMG_PATH, wx.BITMAP_TYPE_ANY)
        self.editPos = [-1, -1]
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.SetDoubleBuffered(True)

    def OnLeftDown(self, event):
        scrnPt = event.GetPosition()
        self.editPos = scrnPt[0]//100*100, scrnPt[1]//100*100
        self.updateDisplay()

#--PanelImge--------------------------------------------------------------------
    def onPaint(self, evt):
        """ Draw the map on the panel."""
        dc = wx.PaintDC(self)
        w, h = self.panelSize
        dc.SetBrush(wx.Brush("White", wx.SOLID))
        dc.DrawRectangle(0, 0, w, h)
        dc.SetPen(wx.Pen('black', 1, wx.LONG_DASH))

        for i in range(5):
            dc.DrawLine(100*(i+1), 0, 100*(i+1), 600)
            dc.DrawLine(0, 100*(i+1), 600, 100*(i+1))

        if self.editPos[0] >=0 and self.editPos[1] >=0:
            dc.SetPen(wx.Pen('Red', 3, wx.LONG_DASH))
            dc.DrawRectangle(self.editPos[0], self.editPos[1], 100, 100)


#--PanelImge--------------------------------------------------------------------
    def _scaleBitmap(self, bitmap, width, height):
        """ Resize a input bitmap.(bitmap-> image -> resize image -> bitmap)"""
        #image = wx.ImageFromBitmap(bitmap) # used below 2.7
        image = bitmap.ConvertToImage()
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        #result = wx.BitmapFromImage(image) # used below 2.7
        result = wx.Bitmap(image, depth=wx.BITMAP_SCREEN_DEPTH)
        return result

#--PanelImge--------------------------------------------------------------------
    def _scaleBitmap2(self, bitmap, width, height):
        """ Resize a input bitmap.(bitmap-> image -> resize image -> bitmap)"""
        image = wx.ImageFromBitmap(bitmap) # used below 2.7
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image) # used below 2.7
        return result

#--PanelImge--------------------------------------------------------------------
    def updateBitmap(self, bitMap):
        """ Update the panel bitmap image."""
        if not bitMap: return
        self.bmp = bitMap

#--PanelMap--------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function
            will set the self update flag.
        """
        self.Refresh(False)
        self.Update()
