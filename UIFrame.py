############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Frame.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# pyOBDA is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyOBDA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyOBDA; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
############################################################################

import wx
import sys

import AppSettings
from ListCtrl import ListCtrl
from SensorManager import SensorManager
from SensorProducer import SensorProducer, ThreadCommands
from ConfigDlg import ConfigDlg
from EventHandler import EventHandler
from EventDebug import EventDebug
from OBD2Device.Codes import Codes

#
# The pyOBDA Frame
#
class UIFrame(wx.Frame):
    def __init__(self, strTitle: str):
        # ====================
        # Setup Main Window
        # ====================
        wx.Frame.__init__(self, None, wx.ID_ANY, strTitle, size=(800, 600))

        # ====================
        # Setup Configuration
        # ====================
        self.configDialog = ConfigDlg(self)

        self.events = EventHandler(self.SensorShutdown, self.configDialog.UpdateStatus)

        self.SetBackgroundColour('BLACK')
        self.Initialize()
        self.SetInitialSize((800, 600))

    def Initialize(self):
        wx.PostEvent( self.events, EventDebug([3, "Inititalizing..."]) )
        self.sensorProducer = None # ...a thread
        self.iIgnitionIndex = 0
        self.iIgnitionType = -1

        # ====================
        # Build StatusBar
        # ====================

        self.BuildStatusBar()

        # ====================
        # Build Notebook
        # ====================

        # Main notebook...
        self.notebook = wx.Notebook(self, wx.ID_ANY, style=wx.NB_TOP)
        self.notebook.SetBackgroundColour('BLACK')
        self.notebook.SetForegroundColour('WHITE')

        # Build Notebook Pages...
        # --------------------
        self.BuildStatusPage()
        self.BuildTestsPage()
        self.BuildSensorPage()
        self.BuildDTCPage()
        self.BuildTracePage()

        self.notebook.SetSelection(0)

        # ====================
        # Build Menus
        # ====================

        # Setting up the File menu...
        self.filemenu = wx.Menu()
        self.filemenu.Append(AppSettings.ID_EXIT, "E&xit", " Terminate the program")

        # Setting up the Settings menu...
        self.settingmenu = wx.Menu()
        self.settingmenu.Append(AppSettings.ID_CONFIG, "Configure", "Configure pyOBD")
        self.settingmenu.Append(AppSettings.ID_RESET, "Connect", "Connect to device")
        self.settingmenu.Append(AppSettings.ID_DISCONNECT, "Disconnect", "Close device connection")

        # Setting up the DTC menu...
        self.listctrlDTCmenu = wx.Menu()
        self.listctrlDTCmenu.Append(AppSettings.ID_GETC, "Get DTCs", " Get DTC Codes")
        self.listctrlDTCmenu.Append(AppSettings.ID_CLEAR, "Clear DTC", " Clear DTC Codes")
        self.listctrlDTCmenu.Append(AppSettings.ID_LOOK, "Code Lookup", " Lookup DTC Codes")

        # Setting up the Help menu...
        self.helpmenu = wx.Menu()
        self.helpmenu.Append(AppSettings.ID_HELP_ABOUT, "About", " About this program")

        # Creating the menubar...
        self.menuBar = wx.MenuBar()
        # Adding the menus to the MenuBar...
        self.menuBar.Append(self.filemenu, "&File")
        self.menuBar.Append(self.settingmenu, "&OBD-II")
        self.menuBar.Append(self.listctrlDTCmenu, "&Codes")
        self.menuBar.Append(self.helpmenu, "&Help")

        # Add the MenuBar...
        self.SetMenuBar(self.menuBar)

        # ====================
        # Bind Menu Event Handlers
        # ====================

        # Bind the menu events...
        self.Bind(wx.EVT_MENU, self.OnExit,       id=AppSettings.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnClearDTC,   id=AppSettings.ID_CLEAR)
        self.Bind(wx.EVT_MENU, self.OnConfigure,  id=AppSettings.ID_CONFIG)
        self.Bind(wx.EVT_MENU, self.OnConnect,    id=AppSettings.ID_RESET)
        self.Bind(wx.EVT_MENU, self.OnDisconnect, id=AppSettings.ID_DISCONNECT)
        self.Bind(wx.EVT_MENU, self.OnGetDTC,     id=AppSettings.ID_GETC)
        self.Bind(wx.EVT_MENU, self.OnLookupCode, id=AppSettings.ID_LOOK)
        self.Bind(wx.EVT_MENU, self.OnHelpAbout,  id=AppSettings.ID_HELP_ABOUT)

        # ====================
        # Process and Display
        # ====================

        self.SensorControlOff()

        return True

    def SensorControlOn(self):
        wx.PostEvent( self.events, EventDebug([0, "Sensor Control On"]) )
        # Enable a few buttons...
        self.settingmenu.Enable(AppSettings.ID_CONFIG, False)
        self.settingmenu.Enable(AppSettings.ID_RESET, False)
        self.settingmenu.Enable(AppSettings.ID_DISCONNECT, True)
        self.listctrlDTCmenu.Enable(AppSettings.ID_GETC, True)
        self.listctrlDTCmenu.Enable(AppSettings.ID_CLEAR, True)
        self.buttonGetDTC.Enable(True)
        self.buttonClearDTC.Enable(True)

    def SensorControlOff(self):
        wx.PostEvent( self.events, EventDebug([0, "Sensor Control Off"]) )
        # Disable a few buttons...
        self.settingmenu.Enable(AppSettings.ID_CONFIG, True)
        self.settingmenu.Enable(AppSettings.ID_RESET, True)
        self.settingmenu.Enable(AppSettings.ID_DISCONNECT, False)
        self.listctrlDTCmenu.Enable(AppSettings.ID_GETC, False)
        self.listctrlDTCmenu.Enable(AppSettings.ID_CLEAR, False)
        self.buttonGetDTC.Enable(False)
        self.buttonClearDTC.Enable(False)
        #self.listctrlSensors.Unbind(wx.EVT_LIST_ITEM_ACTIVATED)

    def SensorShutdown(self) :
        # Signal current producer to finish...
        if self.sensorProducer != None:
            self.SensorControlOff()
            if self.sensorProducer.is_alive() :
                self.sensorProducer.setThreadControl(ThreadCommands.Disconnect) # ...signal disconnect on port
                self.sensorProducer.join() # ...wait for finish
            self.sensorProducer = None

    def BuildStatusBar(self):
        wx.PostEvent( self.events, EventDebug([2, "Build Status Bar"]) )
        self.idStatus = wx.NewIdRef(count=1)
        styleStatus = ( wx.LC_REPORT | wx.SUNKEN_BORDER )
        self.CreateStatusBar(11, wx.STB_DEFAULT_STYLE, wx.ID_ANY, name="OBDA StatusBar")
        #self.StatusBar.SetMinHeight(60)
        self.configDialog.SetStatusBar(self.StatusBar)

    def BuildStatusPage(self):
        wx.PostEvent( self.events, EventDebug([2, "Build Status Page"]) )
        self.panelStatus = wx.Panel(self.notebook, wx.ID_ANY)
        self.idStatus = wx.NewIdRef(count=1)
        styleStatus = ( wx.LC_REPORT | wx.SUNKEN_BORDER )
        self.listctrlStatus = ListCtrl(self.panelStatus, self.idStatus, style=styleStatus)
        self.events.SetStatus(self.listctrlStatus)
        self.listctrlStatus.SetBackgroundColour('BLACK')
        self.listctrlStatus.SetForegroundColour('WHITE')

        self.configDialog.SetStatusListCtrl(self.listctrlStatus)

        ####################################################################
        # This little bit of magic keeps the list the same size as the frame
        def OnPanelResize(evt):
            self.panelStatus.SetSize(evt.GetSize())
            self.listctrlStatus.SetSize(evt.GetSize())
            w, h = self.GetClientSize()
            self.listctrlStatus.SetSize(0, 0, w, h - 29)
        ####################################################################
        self.panelStatus.Bind(wx.EVT_SIZE, OnPanelResize)

        self.notebook.AddPage(self.panelStatus, "Status")

    def BuildTestsPage(self):
        self.panelTests = wx.Panel(self.notebook, wx.ID_ANY)
        self.idTests = wx.NewIdRef(count=1)
        styleTests = ( wx.LC_REPORT | wx.SUNKEN_BORDER )
        self.listctrlTests = ListCtrl(self.panelTests, self.idTests, style=styleTests)
        self.events.SetTests(self.listctrlTests)
        self.listctrlTests.SetBackgroundColour('BLACK')
        self.listctrlTests.SetForegroundColour('WHITE')

        self.listctrlTests.InsertColumn(0, "Description", format=wx.LIST_FORMAT_RIGHT, width=150)
        self.listctrlTests.InsertColumn(1, "Value")

        ####################################################################
        # This little bit of magic keeps the list the same size as the frame
        def OnPanelResize(evt):
            self.panelTests.SetSize(evt.GetSize())
            self.listctrlTests.SetSize(evt.GetSize())
            w, h = self.GetClientSize()
            self.listctrlTests.SetSize(0, 0, w, h - 29)
        ####################################################################
        self.panelTests.Bind(wx.EVT_SIZE, OnPanelResize)

        self.notebook.AddPage(self.panelTests, "Tests")

        # Fill known test entries...
        self.listctrlTests.Append(["System: =====", "=========="])
        for strTest in Codes.Test.SystemCode:
            self.listctrlTests.Append([strTest, "---"])
        self.listctrlTests.Append(["Basic: =====", "=========="])
        for strTest in Codes.Test.BaseCode:
            self.listctrlTests.Append([strTest, "---"])
        self.listctrlTests.Append(["Ignition: =====", "=========="])
        self.iIgnitionIndex = self.listctrlTests.GetItemCount()
        self.iIgnitionType = 0
        for strTest in Codes.Test.SparkCode: # ...default vs CompressionCode
            self.listctrlTests.Append([strTest, "---"])

    def setTestIgnition(self, iIgnitionType):
        if iIgnitionType != self.iIgnitionType:
            # Remove existing...
            iEnd = self.listctrlTests.GetItemCount()
            if iEnd > self.iIgnitionIndex:
                for iIndex in range(8, iEnd):
                    self.listctrlTests.DeleteItem(iIndex)
            # Set...
            self.iIgnitionType = iIgnitionType
            # Append new...
            if iIgnitionType == 0: # ...Spark
                for strTest in Codes.Test.SparkCode:
                    self.listctrlTests.Append([strTest, "---"])
            else: # ...Compression
                for strTest in Codes.Test.CompressionCode:
                    self.listctrlTests.Append([strTest, "---"])

    def BuildSensorPage(self):
        wx.PostEvent( self.events, EventDebug([2, "Build Sensor Page"]) )
        #HOFFSET_LIST = 0 # ...offset from the top of panel
        #posSensors = wx.Point(0, HOFFSET_LIST)
        #styleSensors = ( wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_SINGLE_SEL )
        styleSensors = ( wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL )

        self.idNotebookSensors = wx.NewIdRef(count=1)
        #self.notebookSensors = wx.Notebook(self.notebook, self.idNotebookSensors, style=wx.NB_TOP)
        self.notebookSensors = wx.Notebook(self.notebook, wx.ID_ANY, style=wx.NB_TOP)
        self.notebookSensors.SetBackgroundColour('BLACK')
        self.notebookSensors.SetForegroundColour('WHITE')

        ####################################################################
        # This little bit of magic keeps the list the same size as the frame
        def OnPanelResize(event):
            w, h = self.GetClientSize()
            for iSensorGroup in range(3) :
                self.panelSensors[iSensorGroup].SetSize(event.GetSize())
                self.listctrlSensors[iSensorGroup].SetSize(event.GetSize())
                #self.listctrlSensors[iSensorGroup].SetSize(0, HOFFSET_LIST, w, h - 58)
                self.listctrlSensors[iSensorGroup].SetSize(0, 0, w, h - 58)
        ####################################################################

        iSensorListLen = len(SensorManager.SENSORS)
        strlistSensors = [ str( chr(65 + iIndex) ) for iIndex in range(iSensorListLen) ]
        self.panelSensors = [None] * iSensorListLen
        self.idSensors = [None] * iSensorListLen
        self.listctrlSensors = [None] * iSensorListLen
        self.events.SetSensors(self.listctrlSensors)
        for iSensorGroup in range( iSensorListLen ) :
            self.panelSensors[iSensorGroup] = wx.Panel(self.notebookSensors, wx.ID_ANY)
            self.idSensors[iSensorGroup] = wx.NewIdRef(count=1)
            #self.listctrlSensors[iSensorGroup] = ListCtrl(self.panelSensors[iSensorGroup], self.idSensors[iSensorGroup], pos=posSensors, style=styleSensors)
            self.listctrlSensors[iSensorGroup] = ListCtrl(self.panelSensors[iSensorGroup], self.idSensors[iSensorGroup], style=styleSensors)
            self.listctrlSensors[iSensorGroup].SetBackgroundColour('BLACK')
            self.listctrlSensors[iSensorGroup].SetForegroundColour('WHITE')

            self.listctrlSensors[iSensorGroup].InsertColumn(0, "Supported", format=wx.LIST_FORMAT_CENTER, width=100)
            self.listctrlSensors[iSensorGroup].InsertColumn(1, "Sensor", format=wx.LIST_FORMAT_RIGHT, width=250)
            self.listctrlSensors[iSensorGroup].InsertColumn(2, "Value")
            for sensor in SensorManager.SENSORS[iSensorGroup] :
                self.listctrlSensors[iSensorGroup].Append([AppSettings.CHAR_QMARK, sensor.strTableDesc, ""])
            self.listctrlSensors[iSensorGroup].Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnToggleSensor, id=self.idSensors[iSensorGroup])

            self.panelSensors[iSensorGroup].Bind(wx.EVT_SIZE, OnPanelResize)

            self.notebookSensors.AddPage(self.panelSensors[iSensorGroup], "Sensors " + strlistSensors[iSensorGroup])

        self.notebookSensors.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookSensorPageChanged, id=self.idNotebookSensors)
        self.notebook.AddPage(self.notebookSensors, "Sensors")

    def BuildDTCPage(self):
        wx.PostEvent( self.events, EventDebug([2, "Build DTC Page"]) )
        HOFFSET_LIST = 30 # ...offset from the top of panel (space for buttons)
        self.panelDTC = wx.Panel(self.notebook, wx.ID_ANY)
        self.buttonGetDTC   = wx.Button(self.panelDTC, wx.ID_ANY, "Get DTC",   wx.Point(3, 0))
        self.buttonClearDTC = wx.Button(self.panelDTC, wx.ID_ANY, "Clear DTC", wx.Point(100, 0))

        # Bind functions to button click action...
        self.panelDTC.Bind(wx.EVT_BUTTON, self.OnGetDTC,   self.buttonGetDTC)
        self.panelDTC.Bind(wx.EVT_BUTTON, self.OnClearDTC, self.buttonClearDTC)

        self.idDTC = wx.NewIdRef(count=1)
        posDTC = wx.Point(0, HOFFSET_LIST)
        #styleDTC = ( wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_SINGLE_SEL )
        styleDTC = ( wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL )
        self.listctrlDTC = ListCtrl(self.panelDTC, self.idDTC, pos=posDTC, style=styleDTC)
        self.events.SetDTC(self.listctrlDTC)
        self.listctrlDTC.SetBackgroundColour('BLACK')
        self.listctrlDTC.SetForegroundColour('WHITE')

        self.listctrlDTC.InsertColumn(0, "Code", width=100)
        self.listctrlDTC.InsertColumn(1, "Status", width=100)
        self.listctrlDTC.InsertColumn(2, "Trouble Code")

        ####################################################################
        # This little bit of magic keeps the list the same size as the frame
        def OnPanelResize(evt):
            self.panelDTC.SetSize(evt.GetSize())
            self.listctrlDTC.SetSize(evt.GetSize())
            w, h = self.GetClientSize()
            self.listctrlDTC.SetSize(0, HOFFSET_LIST, w, h - 59)
        ####################################################################
        self.panelDTC.Bind(wx.EVT_SIZE, OnPanelResize)

        self.notebook.AddPage(self.panelDTC, "DTC")

    def BuildTracePage(self):
        self.panelTrace = wx.Panel(self.notebook, wx.ID_ANY)
        idTrace = wx.NewIdRef(count=1)
        styleTrace = ( wx.LC_REPORT | wx.SUNKEN_BORDER )

        self.listctrlTrace = ListCtrl(self.panelTrace, idTrace, style=styleTrace)
        self.events.SetTrace(self.listctrlTrace)
        self.listctrlTrace.SetBackgroundColour('BLACK')
        self.listctrlTrace.SetForegroundColour('WHITE')

        self.listctrlTrace.InsertColumn(0, "Level", format=wx.LIST_FORMAT_RIGHT, width=60)
        self.listctrlTrace.InsertColumn(1, "Message")

        ####################################################################
        # This little bit of magic keeps the list the same size as the frame
        def OnPanelResize(evt):
            self.panelTrace.SetSize(evt.GetSize())
            self.listctrlTrace.SetSize(evt.GetSize())
            w, h = self.GetClientSize()
            self.listctrlTrace.SetSize(0, 0, w, h - 29)
        ####################################################################
        self.panelTrace.Bind(wx.EVT_SIZE, OnPanelResize)

        self.notebook.AddPage(self.panelTrace, "Trace")

    def OnToggleSensor(self, event):
        iIndex = event.GetIndex()
        if self.sensorProducer != None and self.sensorProducer.supported[iIndex] : # ...is Changable?
            wx.PostEvent( self.events, EventDebug( [1, "Toggle Sensor: " + self.listctrlSensors.GetItemText(iIndex, 1)] ) )
            if self.sensorProducer.active[iIndex] : # ...is ON?
                self.sensorProducer.setIDOff(iIndex)
                self.listctrlSensors.SetItem(iIndex, 0, AppSettings.CHAR_BALLOTX) # CHAR_BALLOTX
            else : # ...is OFF?
                self.sensorProducer.setIDOn(iIndex)
                self.listctrlSensors.SetItem(iIndex, 0, AppSettings.CHAR_CHECK)

            #else:
            #    wx.PostEvent( self.EventHandler, EventDebug([1, "ERROR: Incorrect Sensor State"]) )

    def OnNotebookSensorPageChanged(self, event):
        self.sensorProducer.setSensorPage( event.GetSelection() )

    def OnHelpAbout(self, event):
        HelpAboutDlg = wx.MessageDialog(self, AppSettings.STR_HELP_TEXT, 'About', wx.OK | wx.ICON_INFORMATION)
        HelpAboutDlg.ShowModal()
        HelpAboutDlg.Destroy()

    def OnConnect(self, event):
        wx.PostEvent( self.events, EventDebug([2, "OnConnect..."]) )
        self.SensorShutdown()
        # Create sensor Producer...
        self.sensorProducer = SensorProducer(self.configDialog.connection, self.notebook, self.events, self.setTestIgnition)
        self.sensorProducer.start()
        self.SensorControlOn()

    def OnDisconnect(self, event): # ...disconnect from the ECU
        wx.PostEvent( self, EventDebug([2, "OnDisconnect..."]) )
        self.SensorShutdown()

    def OnGetDTC(self, event):
        wx.PostEvent( self.events, EventDebug([2, "OnGetDTC..."]) )
        self.notebook.SetSelection(3)
        if self.sensorProducer != None:
            self.sensorProducer.setThreadControl(ThreadCommands.DTC_Load)

    #def AddDTC(self, code) :
    #    wx.PostEvent( self.EventHandler, EventDebug([2, "AddDTC..."]) )
    #    self.listctrlDTC.InsertStringItem(0, "")
    #    self.listctrlDTC.SetItem(0, 0, code[0])
    #    self.listctrlDTC.SetItem(0, 1, code[1])

    def OnLookupCode(self, event=None):
        wx.PostEvent( self.events, EventDebug([2, "OnLookupCode..."]) )
        id = 0
        diag = wx.Frame(None, id, title="Diagnostic Trouble Codes")

        treectrlDTC = wx.TreeCtrl(diag, id, style=wx.TR_HAS_BUTTONS)

        idRoot = treectrlDTC.AddRoot("Code Reference")
        keysCode = sorted(Codes.Codes.keys())
        strGroup = "" # ...initial group ensures start
        idBranch = None
        for strCode in keysCode:
            if strCode[:3] != strGroup:
                # New Group string...
                strGroup = strCode[:3]
                # New Group ID: Group Text for Branch on Root...
                idBranch = treectrlDTC.AppendItem(idRoot, strCode[:3] + "XX")
            # New Leaf ID: Key Text for Leaf on Branch...
            idLeaf = treectrlDTC.AppendItem(idBranch, strCode)
            # Value Text for Leaf...
            treectrlDTC.AppendItem(idLeaf, Codes.Codes[strCode])

        diag.SetSize((600, 800))
        diag.Show(True)

    def OnClearDTC(self, event):
        wx.PostEvent( self.events, EventDebug([2, "OnClearDTC..."]) )
        id = 0
        diag = wx.Dialog(self, id, title="Clear DTC?")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(
            wx.StaticText(
                diag, -1,
                "Are you sure you wish to\n" +
                "clear all DTC codes and\n" +
                "the freeze frame data?"
            ), 0
        )
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(wx.Button(diag, wx.ID_OK, "Ok"), 0)

        sizer.Add(box, 0)
        diag.SetSizer(sizer)
        diag.SetAutoLayout(True)
        sizer.Fit(diag)
        result = diag.ShowModal()
        if result == wx.ID_OK:
            self.ClearDTC()

    def ClearDTC(self):
        wx.PostEvent( self.events, EventDebug([0, "ClearDTC..."]) )
        self.notebook.SetSelection(3)
        if self.sensorProducer != None:
            self.sensorProducer.setThreadControl(ThreadCommands.DTC_Clear)

    def OnConfigure(self, event=None):
        wx.PostEvent( self.events, EventDebug([2, "OnConfigure..."]) )
        self.configDialog.SetPorts()
        result = self.configDialog.ShowModal()
        self.configDialog.ProcessSettings(result)

    def OnExit(self, event=None):
        wx.PostEvent( self.events, EventDebug( [1, "OnExit..."] ) )
        self.SensorShutdown()
        sys.exit(0)
