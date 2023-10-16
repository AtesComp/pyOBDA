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
from wx.lib.dialogs import ScrolledMessageDialog
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

        self.events = EventHandler(self.shutdownConnection, self.configDialog.updateConnection)

        self.SetBackgroundColour('BLACK')
        self.initialize()
        self.SetInitialSize((800, 600))

    def initialize(self):
        wx.PostEvent( self.events, EventDebug([3, "Inititalizing..."]) )
        self.sensorProducer = None # ...a thread
        self.iIgnitionIndex = 0
        self.iIgnitionType = -1

        # ====================
        # Build StatusBar
        # ====================

        self.buildStatusBar()

        # ====================
        # Build Notebook
        # ====================

        # Main notebook...
        self.notebook = wx.Notebook(self, wx.ID_ANY, style=wx.NB_TOP)
        self.notebook.SetBackgroundColour('BLACK')
        self.notebook.SetForegroundColour('WHITE')

        # Build Notebook Pages...
        # --------------------
        self.buildConnectionPage()
        self.buildTestsPage()
        self.buildSensorPage()
        self.buildDTCPage()
        self.buildTracePage()

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
        self.Bind(wx.EVT_MENU, self.onExit,       id=AppSettings.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onClearDTC,   id=AppSettings.ID_CLEAR)
        self.Bind(wx.EVT_MENU, self.onConfigure,  id=AppSettings.ID_CONFIG)
        self.Bind(wx.EVT_MENU, self.onConnect,    id=AppSettings.ID_RESET)
        self.Bind(wx.EVT_MENU, self.onDisconnect, id=AppSettings.ID_DISCONNECT)
        self.Bind(wx.EVT_MENU, self.onGetDTC,     id=AppSettings.ID_GETC)
        self.Bind(wx.EVT_MENU, self.onLookupCode, id=AppSettings.ID_LOOK)
        self.Bind(wx.EVT_MENU, self.onHelpAbout,  id=AppSettings.ID_HELP_ABOUT)

        # ====================
        # Process and Display
        # ====================

        self.setSensorControlOff()

        return True

    def setSensorControlOn(self):
        wx.PostEvent( self.events, EventDebug([0, "Sensor Control On"]) )
        # Enable a few buttons...
        self.settingmenu.Enable(AppSettings.ID_CONFIG, False)
        self.settingmenu.Enable(AppSettings.ID_RESET, False)
        self.settingmenu.Enable(AppSettings.ID_DISCONNECT, True)
        self.listctrlDTCmenu.Enable(AppSettings.ID_GETC, True)
        self.listctrlDTCmenu.Enable(AppSettings.ID_CLEAR, True)
        self.buttonGetDTC.Enable(True)
        self.buttonClearDTC.Enable(True)

    def setSensorControlOff(self):
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

    def shutdownConnection(self) :
        # Signal current producer to finish...
        if self.sensorProducer != None:
            self.setSensorControlOff()
            if self.sensorProducer.is_alive() :
                self.sensorProducer.setThreadControl(ThreadCommands.Disconnect) # ...signal disconnect on port
                self.sensorProducer.join() # ...wait for finish
            self.sensorProducer = None

    def buildStatusBar(self):
        wx.PostEvent( self.events, EventDebug([2, "Build Status Bar"]) )
        self.idStatusBar = wx.NewIdRef(count=1)
        #styleStatus = ( wx.LC_REPORT | wx.SUNKEN_BORDER )
        #                                                    styleStatus
        self.CreateStatusBar(self.configDialog.elementCount, wx.STB_DEFAULT_STYLE, self.idStatusBar, name="OBDA StatusBar")
        #self.StatusBar.SetMinHeight(60)
        self.configDialog.setStatusBar(self.StatusBar)

    def buildConnectionPage(self):
        wx.PostEvent( self.events, EventDebug([2, "Build Connection Page"]) )
        self.panelConnection = wx.Panel(self.notebook, wx.ID_ANY)
        self.idConnection = wx.NewIdRef(count=1)
        styleConnection = ( wx.LC_REPORT | wx.SUNKEN_BORDER )
        self.listctrlConnection = ListCtrl(self.panelConnection, self.idConnection, style=styleConnection)
        self.events.setConnection(self.listctrlConnection)
        self.listctrlConnection.SetBackgroundColour('BLACK')
        self.listctrlConnection.SetForegroundColour('WHITE')

        self.configDialog.setConnectionListCtrl(self.listctrlConnection)

        ####################################################################
        # This little bit of magic keeps the list the same size as the frame
        def OnPanelResize(evt):
            self.panelConnection.SetSize(evt.GetSize())
            self.listctrlConnection.SetSize(evt.GetSize())
            w, h = self.GetClientSize()
            self.listctrlConnection.SetSize(0, 0, w, h - 29)
        ####################################################################
        self.panelConnection.Bind(wx.EVT_SIZE, OnPanelResize)

        self.notebook.AddPage(self.panelConnection, "Connection")

    def buildTestsPage(self):
        self.panelTests = wx.Panel(self.notebook, wx.ID_ANY)
        self.idTests = wx.NewIdRef(count=1)
        styleTests = ( wx.LC_REPORT | wx.SUNKEN_BORDER )
        self.listctrlTests = ListCtrl(self.panelTests, self.idTests, style=styleTests)
        self.events.setTests(self.listctrlTests)
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

    def buildSensorPage(self):
        wx.PostEvent( self.events, EventDebug([2, "Build Sensor Page"]) )
        #HOFFSET_LIST = 0 # ...offset from the top of panel
        #posSensors = wx.Point(0, HOFFSET_LIST)
        #styleSensors = ( wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_SINGLE_SEL )
        styleSensors = ( wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL )

        self.idNotebookSensors = wx.NewIdRef(count=1)
        # NOTE: Bind self.idNotebookSensors later after sensor groups.
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
        self.events.setSensors(self.listctrlSensors)
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
            self.listctrlSensors[iSensorGroup].Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onToggleSensor, id=self.idSensors[iSensorGroup])

            self.panelSensors[iSensorGroup].Bind(wx.EVT_SIZE, OnPanelResize)

            self.notebookSensors.AddPage(self.panelSensors[iSensorGroup], "Sensors " + strlistSensors[iSensorGroup])

        self.notebookSensors.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onNotebookSensorPageChanged, id=self.idNotebookSensors)
        self.notebook.AddPage(self.notebookSensors, "Sensors")

    def buildDTCPage(self):
        wx.PostEvent( self.events, EventDebug([2, "Build DTC Page"]) )
        HOFFSET_LIST = 30 # ...offset from the top of panel (space for buttons)
        self.panelDTC = wx.Panel(self.notebook, wx.ID_ANY)
        self.buttonGetDTC   = wx.Button(self.panelDTC, wx.ID_ANY, "Get DTC",   wx.Point(3, 0))
        self.buttonClearDTC = wx.Button(self.panelDTC, wx.ID_ANY, "Clear DTC", wx.Point(100, 0))

        # Bind functions to button click action...
        self.panelDTC.Bind(wx.EVT_BUTTON, self.onGetDTC,   self.buttonGetDTC)
        self.panelDTC.Bind(wx.EVT_BUTTON, self.onClearDTC, self.buttonClearDTC)

        self.idDTC = wx.NewIdRef(count=1)
        posDTC = wx.Point(0, HOFFSET_LIST)
        #styleDTC = ( wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_SINGLE_SEL )
        styleDTC = ( wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL )
        self.listctrlDTC = ListCtrl(self.panelDTC, self.idDTC, pos=posDTC, style=styleDTC)
        self.events.setDTC(self.listctrlDTC)
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

    def buildTracePage(self):
        self.panelTrace = wx.Panel(self.notebook, wx.ID_ANY)
        self.idTrace = wx.NewIdRef(count=1)
        styleTrace = ( wx.LC_REPORT | wx.SUNKEN_BORDER )

        self.listctrlTrace = ListCtrl(self.panelTrace, self.idTrace, style=styleTrace)
        self.events.setDebug(self.listctrlTrace)
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

    def onToggleSensor(self, event):
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

    def onNotebookSensorPageChanged(self, event):
        self.sensorProducer.setSensorPage( event.GetSelection() )

    def onHelpAbout(self, event):
        HelpAboutDlg = ScrolledMessageDialog(
            parent=self, msg=AppSettings.STR_HELP_TEXT, caption='About', size=(700, 500),
            style=wx.OK | wx.ICON_INFORMATION
        )
        font = wx.Font(10, family=wx.FONTFAMILY_MODERN, style=wx.NORMAL, weight=wx.NORMAL, faceName="Monospace")
        HelpAboutDlg.text.SetFont(font)
        HelpAboutDlg.text.SetInsertionPoint(0)
        HelpAboutDlg.ShowModal()
        HelpAboutDlg.Destroy()

    def onConnect(self, event):
        wx.PostEvent( self.events, EventDebug([2, "OnConnect..."]) )
        self.shutdownConnection()
        # Create sensor Producer...
        self.sensorProducer = SensorProducer(self.configDialog.connection, self.notebook, self.events, self.setTestIgnition)
        self.sensorProducer.start()
        self.setSensorControlOn()

    def onDisconnect(self, event): # ...disconnect from the ECU
        wx.PostEvent( self, EventDebug([2, "OnDisconnect..."]) )
        self.shutdownConnection()

    def onGetDTC(self, event):
        wx.PostEvent( self.events, EventDebug([2, "OnGetDTC..."]) )
        self.notebook.SetSelection(3)
        if self.sensorProducer != None:
            self.sensorProducer.setThreadControl(ThreadCommands.DTC_Load)

    #def AddDTC(self, code) :
    #    wx.PostEvent( self.EventHandler, EventDebug([2, "AddDTC..."]) )
    #    self.listctrlDTC.InsertStringItem(0, "")
    #    self.listctrlDTC.SetItem(0, 0, code[0])
    #    self.listctrlDTC.SetItem(0, 1, code[1])

    def onLookupCode(self, event=None):
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

    def onClearDTC(self, event):
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
            self.clearDTC()

    def clearDTC(self):
        wx.PostEvent( self.events, EventDebug([0, "ClearDTC..."]) )
        self.notebook.SetSelection(3)
        if self.sensorProducer != None:
            self.sensorProducer.setThreadControl(ThreadCommands.DTC_Clear)

    def onConfigure(self, event=None):
        wx.PostEvent( self.events, EventDebug([2, "OnConfigure..."]) )
        self.configDialog.setPorts()
        result = self.configDialog.ShowModal()
        self.configDialog.processSettings(result)

    def onExit(self, event=None):
        wx.PostEvent( self.events, EventDebug( [1, "OnExit..."] ) )
        self.shutdownConnection()
        sys.exit(0)
