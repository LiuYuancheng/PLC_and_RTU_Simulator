#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        uiPanel.py
#
# Purpose:     This module is used to create different function panels.
# Author:      Yuancheng Liu
#
# Created:     2020/01/10
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import wx
import wx.grid
from datetime import datetime
import plcSimuGobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelImge(wx.Panel):
    """ Panel to display image. """

    def __init__(self, parent, panelSize=(450, 600)):
        wx.Panel.__init__(self, parent, size=panelSize)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.panelSize = panelSize
        self.bmp = wx.Bitmap(gv.BGIMG_PATH, wx.BITMAP_TYPE_ANY)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.SetDoubleBuffered(True)

#--PanelImge--------------------------------------------------------------------
    def onPaint(self, evt):
        """ Draw the map on the panel."""
        dc = wx.PaintDC(self)
        w, h = self.panelSize
        
        dc.SetBrush(wx.Brush("White", wx.SOLID))
        dc.DrawRectangle(0, 0, 400, 600)
        dc.DrawBitmap(self._scaleBitmap(self.bmp, 400, 400), 0, 0)
        dc.SetPen(wx.Pen('RED'))
        dc.DrawText('This is a sample image', w//2, h//2)
        for i in range(len(gv.OUTCL)):
            x = 205 + 16*i
            y1 = 320
            y2 = 470 - 20*i
            dc.DrawLine(x, y1, x, y2)

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


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMDbus(wx.Panel):
    """ Modbus TCP message simulator panel."""
    def __init__(self, parent, panelSize=(350, 400)):
        wx.Panel.__init__(self, parent,  size=panelSize)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.gpsPos = None
        self.SetSizer(self._buidUISizer())

#--PanelCtrl-------------------------------------------------------------------
    def _buidUISizer(self):
        """ build the control panel sizer. """
        flagsR = wx.LEFT
        ctSizer = wx.BoxSizer(wx.VERTICAL)
        ctSizer.Add(wx.StaticText(self, label="ModBus TCP Message Simulator".ljust(15)),
                  flag=flagsR, border=2)        
        ctSizer.AddSpacer(5)

        ctSizer.Add(wx.StaticText(self, label="Message send to PLC".ljust(15)),
            flag=flagsR, border=2)     

        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.grid = wx.grid.Grid(self)
        self.grid.SetColLabelSize(30)
        self.grid.SetRowLabelSize(30)
        self.grid.CreateGrid(13, 3)

        self.grid.SetColSize(0, 140)
        self.grid.SetColLabelValue(0, "Message Tab")

        self.grid.SetColSize(1, 40)
        self.grid.SetColLabelValue(1, "Len")

        self.grid.SetColSize(2, 60)
        self.grid.SetColLabelValue(2, "Value")

        
        for idx in range(len(gv.MBTcp_RQ)):
            self.grid.SetCellValue(idx, 0, gv.MBTcp_RQ[idx])
            byteLen = 2 if idx < 3 else 1
            self.grid.SetCellValue(idx, 1, str(byteLen))
            self.grid.SetCellValue(idx, 2, str(gv.gTcpMsg[idx]))
        
        hbox0.Add(self.grid, flag=flagsR, border=2)
        hbox0.AddSpacer(2)
        hbox0.Add(wx.Button(self, label='Load>>', size=(60, 25)), flag=wx.CENTER, border=2)

        ctSizer.Add(hbox0, flag=flagsR, border=2)

        ctSizer.AddSpacer(3)

        ctSizer.Add(wx.StaticText(self, label="PLC answer".ljust(15)),
            flag=flagsR, border=2)
        ctSizer.AddSpacer(3)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.detailTC = wx.TextCtrl(self, size=(270, 400), style=wx.TE_MULTILINE)
        hbox1.Add(self.detailTC, flag=flagsR, border=2)
        hbox1.AddSpacer(2)
        hbox1.Add(wx.Button(self, label='Fetch<<', size=(60, 25)), flag=wx.CENTER, border=2)
        ctSizer.Add(hbox1, flag=flagsR, border=2)

        # Row idx 0: show the search key and map zoom in level.
        #hbox0 = wx.BoxSizer(wx.HORIZONTAL)

        #ctSizer.Add(hbox0, flag=flagsR, border=2)
        return ctSizer


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelCtrl(wx.Panel):
    """ Function control panel."""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.gpsPos = None
        self.SetSizer(self._buidUISizer())

#--PanelCtrl-------------------------------------------------------------------
    def _buidUISizer(self):
        """ build the control panel sizer. """
        flagsR = wx.CENTER
        ctSizer = wx.BoxSizer(wx.VERTICAL)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        ctSizer.AddSpacer(5)
        # Row idx 0: show the search key and map zoom in level.
        hbox0.Add(wx.StaticText(self, label="Control panel".ljust(15)),
                  flag=flagsR, border=2)
        ctSizer.Add(hbox0, flag=flagsR, border=2)
        return ctSizer

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    """ Main function used for local test debug panel. """

    print('Test Case start: type in the panel you want to check:')
    print('0 - PanelImge')
    print('1 - PanelCtrl')
    #pyin = str(input()).rstrip('\n')
    #testPanelIdx = int(pyin)
    testPanelIdx = 1    # change this parameter for you to test.
    print("[%s]" %str(testPanelIdx))
    app = wx.App()
    mainFrame = wx.Frame(gv.iMainFrame, -1, 'Debug Panel',
                         pos=(300, 300), size=(640, 480), style=wx.DEFAULT_FRAME_STYLE)
    if testPanelIdx == 0:
        testPanel = PanelImge(mainFrame)
    elif testPanelIdx == 1:
        testPanel = PanelCtrl(mainFrame)
    mainFrame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()



