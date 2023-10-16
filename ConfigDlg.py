############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Config.py
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

import os  # ...for os.environ
import sys
import configparser  # ...safe application configuration
from os import path, mkdir

import AppSettings
import OBD2Device
from ListCtrl import ListCtrl
from Connection import Connection
from EventDebug import EventDebug
from OBD2Port import OBD2Port


class ConfigDlg(wx.Dialog):
    def __init__(self, parent: wx.Frame):
        wx.Dialog.__init__(
            self, parent, wx.ID_ANY, title="Configure",
            size=(400, 200), style=wx.DIALOG_ADAPTATION_STANDARD_SIZER )

        self.elementCount = 0 # ...count in initialize()

        # Common Positions and Sizes...
        self.sizeStaticText = ( 95, 40)
        self.sizeChoiceText = (305, 40)
        self.sizeCheckText  = (300, 40)
        self.posTextCtrl    = (100, -10)
        self.sizeTextCtrl   = ( 50, 40)
        self.sizeButton     = ( 80, 30)

        # Common UI elements...
        self.panelPorts      = None
        self.choicePorts     = None
        self.panelBauds      = None
        self.panelProtocols  = None
        self.checkFast       = None
        self.checkVolts      = None
        self.panelTimeout    = None
        self.panelReconnect  = None
        self.panelDelay      = None
        self.panelDebugLevel = None
        self.boxButtons      = None

        self.theStatusListCtrl: ListCtrl = None
        self.theStatusBar = None

        self.SetBackgroundColour('BLACK')
        self.SetForegroundColour('WHITE')
        self.initialize()

    def initialize(self):
        # Set up to read settings from file...
        self.config = configparser.RawConfigParser()
        self.connection = Connection(None)

        #print( platform.system() )
        #print( platform.mac_ver()[] )

        self.stateTitle = \
            [   "Link: ",
                "Proto: ",
                "Cable: ",
                "Volts: ", # Cable Volts
                "Port: ",
                "Baud: ",
                "Fast: ",
                "Check: ", # Check Voltage
                "Timeout: ",
                "Reconnect: ",
                "Delay:",
                "Debug: ",
            ]
        self.elementCount = len( self.stateTitle )

        self.bIsLinux = False
        if sys.platform.startswith('win'):  # ...Windows
            self.fileConfig = "pyobda.ini"
        else:  # ...Linux-y, including Mac
            self.bIsLinux = True
            self.pathConfig = os.environ['HOME'] + '/.config'
            self.pathOBDA = self.pathConfig + '/pyobda'
            self.fileConfig = self.pathOBDA + '/config'
        bConfigExists = os.path.exists(self.fileConfig)
        if not bConfigExists :
            wx.PostEvent(self, EventDebug([1, "No configuration file exists: " + self.fileConfig]))
        if not bConfigExists or self.config.read(self.fileConfig) == [] :
            self.connection.resetConnection()
        else :
            if not self.config.has_section("OBD") :
                self.config.add_section("OBD")
            if not self.config.has_section("DEBUG") :
                self.config.add_section("DEBUG")
            self.connection.PORTNAME = self.config.get("OBD", "PORT", fallback="/dev/ttyUSB0")
            strBaud = self.config.get("OBD", "BAUD", fallback="")
            if (strBaud == "Auto") :
                self.connection.BAUD = 0
            else :
                self.connection.BAUD = self.config.getint("OBD", "BAUD", fallback=115200)
            self.connection.PROTOCOL = self.config.get("OBD", "PROTOCOL", fallback="6")
            self.connection.FAST = self.config.getboolean("OBD", "FAST", fallback=True)
            self.connection.CHECKVOLTS = self.config.getboolean("OBD", "CHECKVOLTS", fallback=True)
            self.connection.TIMEOUT = self.config.getfloat("OBD", "TIMEOUT", fallback=10.0)
            self.connection.RECONNECTS = self.config.getint("OBD", "RECONNECTS", fallback=3)
            self.connection.DELAY = self.config.getfloat("OBD", "DELAY", fallback=1.0)
            AppSettings.DEBUG_LEVEL = self.config.getint("DEBUG", "LEVEL", fallback=5)
            OBD2Device.setLogging()

        # Serial Ports Input RadioBox...
        self.panelPorts = wx.Panel(self)
        staticPorts = \
            wx.StaticText(
                self.panelPorts, wx.ID_ANY, 'Serial Port:',
                size=self.sizeStaticText, style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL
            )
        self.setPorts()

        # Serial Baud Input Panel & Control...
        # 9600, 19200, 38400, 57600, 115200
        self.bauds = \
            [   "Auto Select",
                "9600",
                "19200",
                "38400",
                "57600",
                "115200",
                "230400",
            ]
        self.panelBauds = wx.Panel(self)
        staticBauds = wx.StaticText(
            self.panelBauds, wx.ID_ANY, 'Baud Rate:', size=self.sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.choiceBauds = wx.Choice(self.panelBauds, wx.ID_ANY, self.posTextCtrl, self.sizeChoiceText, self.bauds)
        # Set the default connection protocol choice...
        iIndex = 0 # ...default to "Auto Select"
        strBaud = str(self.connection.BAUD)
        if (self.connection.BAUD != None) and (strBaud in self.bauds) :
            iIndex = self.bauds.index(strBaud)
        self.choiceBauds.SetSelection(iIndex)

        # Connection Protocol Input Panel & Control...
        # ID Name
        # 1  SAE J1850 PWM
        # 2  SAE J1850 VPW
        # 3  AUTO, ISO 9141-2
        # 4  ISO 14230-4 (KWP 5BAUD)
        # 5  ISO 14230-4 (KWP FAST)
        # 6  ISO 15765-4 (CAN 11/500)
        # 7  ISO 15765-4 (CAN 29/500)
        # 8  ISO 15765-4 (CAN 11/250)
        # 9  ISO 15765-4 (CAN 29/250)
        # A  SAE J1939 (CAN 29/250)
        protocols = \
            [   "Auto Select",
                "1: SAE J1850 PWM",
                "2: SAE J1850 VPW",
                "3: AUTO, ISO 9141-2",
                "4: ISO 14230-4 (KWP 5BAUD)",
                "5: ISO 14230-4 (KWP FAST)",
                "6: ISO 15765-4 (CAN 11/500)",
                "7: ISO 15765-4 (CAN 29/500)",
                "8: ISO 15765-4 (CAN 11/250)",
                "9: ISO 15765-4 (CAN 29/250)",
                "A: SAE J1939 (CAN 29/250)"
            ]
        self.protocolShort = ["Auto", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A"]
        self.panelProtocols = wx.Panel(self)
        staticProtocols = wx.StaticText(
            self.panelProtocols, wx.ID_ANY, 'Protocol:', size=self.sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.choiceProtocols = wx.Choice(self.panelProtocols, wx.ID_ANY, self.posTextCtrl, self.sizeChoiceText, protocols)
        # Set the default connection protocol choice...
        iIndex = 0
        if (self.connection.PROTOCOL != None) and (self.connection.PROTOCOL in self.protocolShort) :
            iIndex = self.protocolShort.index(self.connection.PROTOCOL)
        self.choiceProtocols.SetSelection(iIndex)

        self.checkFast = \
            wx.CheckBox(
                self, wx.ID_ANY, "Fast Connect?", size=self.sizeCheckText, style=wx.CHK_2STATE)
        if (self.connection.FAST == True) :
            self.checkFast.SetValue(self.connection.FAST)

        self.checkVolts = \
            wx.CheckBox(
                self, wx.ID_ANY, "Check Voltage?", size=self.sizeCheckText, style=wx.CHK_2STATE)
        if (self.connection.CHECKVOLTS == True) :
            self.checkVolts.SetValue(self.connection.CHECKVOLTS)

        # Timeout Input Panel & Control...
        self.panelTimeout = wx.Panel(self)
        staticTimeout = wx.StaticText(
            self.panelTimeout, wx.ID_ANY, 'Timeout:', size=self.sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.ctrlTimeout = wx.TextCtrl(
            self.panelTimeout, wx.ID_ANY, str(self.connection.TIMEOUT), self.posTextCtrl, self.sizeTextCtrl)

        # Reconnects Input Panel & Control...
        self.panelReconnect = wx.Panel(self)
        staticReconnect = wx.StaticText(
            self.panelReconnect, wx.ID_ANY, 'Reconnects:', size=self.sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.ctrlReconnect = wx.TextCtrl(
            self.panelReconnect, wx.ID_ANY, str(self.connection.RECONNECTS), self.posTextCtrl, self.sizeTextCtrl)

        # Delay Input Panel & Control...
        self.panelDelay = wx.Panel(self)
        staticDelay = wx.StaticText(
            self.panelDelay, wx.ID_ANY, 'Delay:', size=self.sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.ctrlDelay = wx.TextCtrl(
            self.panelDelay, wx.ID_ANY, str(self.connection.DELAY), self.posTextCtrl, self.sizeTextCtrl)

        # Debug Level Input Panel & Control...
        self.panelDebugLevel = wx.Panel(self)
        staticDebugLevel = wx.StaticText(
            self.panelDebugLevel, wx.ID_ANY, 'Debug:', size=self.sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.ctrlDebugLevel = wx.TextCtrl(
            self.panelDebugLevel, wx.ID_ANY, str(AppSettings.DEBUG_LEVEL), self.posTextCtrl, self.sizeTextCtrl)

        self.boxButtons = wx.BoxSizer(wx.HORIZONTAL)
        self.boxButtons.Add(wx.Button(self, wx.ID_OK,     size=self.sizeButton))
        self.boxButtons.Add(wx.Button(self, wx.ID_CANCEL, size=self.sizeButton))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panelPorts,      1, wx.LEFT)
        sizer.Add(self.panelBauds,      1, wx.LEFT)
        sizer.Add(self.panelProtocols,  1, wx.LEFT)
        sizer.Add(self.checkFast,       1, wx.LEFT)
        sizer.Add(self.checkVolts,      1, wx.LEFT)
        sizer.Add(self.panelTimeout,    0, wx.LEFT)
        sizer.Add(self.panelReconnect,  0, wx.LEFT)
        sizer.Add(self.panelDelay,      0, wx.LEFT)
        sizer.Add(self.panelDebugLevel, 0, wx.LEFT)
        sizer.Add(self.boxButtons,      1, wx.CENTER)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def setPorts(self):
        self.checkPorts()
        if self.choicePorts == None:
            self.choicePorts = \
                wx.Choice(self.panelPorts, wx.ID_ANY, self.posTextCtrl, self.sizeChoiceText, self.ports)
        else:
            self.choicePorts.Clear()
            self.choicePorts.AppendItems(self.ports)
        # Set the default serial port choice...
        iIndex = 0
        if (self.connection.PORTNAME != None) and (self.connection.PORTNAME in self.ports):
            iIndex = self.ports.index(self.connection.PORTNAME)
        self.choicePorts.SetSelection(iIndex)

    def checkPorts(self):
        self.ports = OBD2Port.getPorts()
        self.bGoodPorts = True
        if (len(self.ports) <= 0) :
            self.bGoodPorts = False
            self.ports = ["No Available Devices on Ports!"]

    def processSettings(self, result):
        if (result == wx.ID_OK):
            # Create sections...Frame
            if not self.config.has_section("OBD") :
                self.config.add_section("OBD")
            if not self.config.has_section("DEBUG") :
                self.config.add_section("DEBUG")

            # Set and save CONNECTION STATE...
            iIndex = 0
            if self.bGoodPorts:
                self.theStatusListCtrl.SetItem(iIndex, 1, "CONNECTION STATE by SensorProducer")
                self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + AppSettings.CHAR_QMARK, iIndex)

            # Set and save PROTOCOL...
            iIndex += 1
            self.connection.PROTOCOL = self.protocolShort[self.choiceProtocols.GetSelection()]
            self.config.set("OBD", "PROTOCOL", self.connection.PROTOCOL)
            self.theStatusListCtrl.SetItem(iIndex, 1, self.connection.PROTOCOL)
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + self.connection.PROTOCOL, iIndex)

            # Set and save CABLE VERSION...
            iIndex += 1
            if self.bGoodPorts:
                self.theStatusListCtrl.SetItem(iIndex, 1, "CABLE VERSION by SensorProducer")
                self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + "CABLE VERSION by SensorProducer", iIndex)

            # Set and save CABLE VOLTAGE...
            iIndex += 1
            if self.bGoodPorts:
                self.theStatusListCtrl.SetItem(iIndex, 1, "CABLE VOLTAGE by SensorProducer")
                self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + "CABLE VOLTAGE by SensorProducer", iIndex)

            # Set and save PORTNAME...
            iIndex += 1
            if self.bGoodPorts:
                self.connection.PORTNAME = self.ports[self.choicePorts.GetSelection()]
            else:
                self.connection.PORTNAME = Connection.strPortNameDefault
            self.config.set("OBD", "PORT", self.connection.PORTNAME)
            self.theStatusListCtrl.SetItem(iIndex, 1, self.connection.PORTNAME)
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + self.connection.PORTNAME, iIndex)

            # Set and save BAUD...
            iIndex += 1
            iSelection = self.choiceBauds.GetSelection()
            if iSelection == 0 : # ...Auto Select
                self.connection.BAUD = 0
            else :
                self.connection.BAUD = int(self.bauds[iSelection])
            self.config.set("OBD", "BAUD", self.connection.BAUD)
            strBaud = str(self.connection.BAUD) if iSelection > 0 else "Auto"
            self.theStatusListCtrl.SetItem(iIndex, 1, strBaud )
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + strBaud, iIndex)

            # Set and save FAST...
            iIndex += 1
            self.connection.FAST = self.checkFast.GetValue()
            self.config.set("OBD", "FAST", self.connection.FAST)
            strFast = str(self.connection.FAST)
            self.theStatusListCtrl.SetItem(iIndex, 1, strFast)
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + (AppSettings.CHAR_CHECK if self.connection.FAST else AppSettings.CHAR_BALLOTX), iIndex)

            # Set and save CHECKVOLTS...
            iIndex += 1
            self.connection.CHECKVOLTS = self.checkVolts.GetValue()
            self.config.set("OBD", "CHECKVOLTS", self.connection.CHECKVOLTS)
            strCheckVolts = str(self.connection.CHECKVOLTS)
            self.theStatusListCtrl.SetItem(iIndex, 1, strCheckVolts)
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + (AppSettings.CHAR_CHECK if self.connection.CHECKVOLTS else AppSettings.CHAR_BALLOTX), iIndex)

            # Set and save TIMEOUT...
            iIndex += 1
            self.connection.TIMEOUT = float(self.ctrlTimeout.GetValue())
            self.config.set("OBD", "TIMEOUT", self.connection.TIMEOUT)
            strTimeOut = str(self.connection.TIMEOUT)
            self.theStatusListCtrl.SetItem(iIndex, 1, strTimeOut)
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + strTimeOut, iIndex)

            # Set and save RECONNECTS...
            iIndex += 1
            self.connection.RECONNECTS = int(self.ctrlReconnect.GetValue())
            self.config.set("OBD", "RECONNECTS", self.connection.RECONNECTS)
            strReconnects = str(self.connection.RECONNECTS)
            self.theStatusListCtrl.SetItem(iIndex, 1, strReconnects)
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + strReconnects, iIndex)

            # Set and save DELAY...
            iIndex += 1
            self.connection.DELAY = float(self.ctrlDelay.GetValue())
            self.config.set("OBD", "DELAY", self.connection.DELAY)
            strDelay = str(self.connection.DELAY)
            self.theStatusListCtrl.SetItem(iIndex, 1, strDelay)
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + strDelay, iIndex)

            # Set and save DEBUGLEVEL...
            iIndex += 1
            AppSettings.DEBUG_LEVEL = int(self.ctrlDebugLevel.GetValue() )
            OBD2Device.setLogging()
            self.config.set("DEBUG", "LEVEL", AppSettings.DEBUG_LEVEL)
            strDebugLevel = str(AppSettings.DEBUG_LEVEL)
            self.theStatusListCtrl.SetItem(iIndex, 1, strDebugLevel)
            self.theStatusBar.SetStatusText(self.stateTitle[iIndex] + strDebugLevel, iIndex)

            # Write configuration to the config file...
            #   Check for config file and, if it doesn't exist, create path
            #   to file if needed and create file.
            if self.bIsLinux : # ...needs path to config file
                bConfigExists = path.exists(self.fileConfig)
                if not bConfigExists :
                    if not path.exists(self.pathConfig) :
                        mkdir(self.pathConfig)
                    if not path.exists(self.pathOBDA) :
                        mkdir(self.pathOBDA)
            self.config.write( open(self.fileConfig, 'w+') )

    def setStatusBar(self, theStatusBar):
        self.theStatusBar = theStatusBar
        self.theStatusBar.SetStatusWidths([50, 58, -1, 58, -1, 96, 50, 62, 90, 68, 90, 94])
        self.theStatusBar.SetStatusText(self.stateTitle[ 0] + AppSettings.CHAR_BALLOTX, 0)
        self.theStatusBar.SetStatusText(self.stateTitle[ 1] + self.connection.PROTOCOL, 1)
        self.theStatusBar.SetStatusText(self.stateTitle[ 2] + "Unknown", 2)
        self.theStatusBar.SetStatusText(self.stateTitle[ 3] + "---", 3)
        self.theStatusBar.SetStatusText(self.stateTitle[ 4] + self.connection.PORTNAME, 4)
        self.theStatusBar.SetStatusText(self.stateTitle[ 5] + str(self.connection.BAUD), 5)
        self.theStatusBar.SetStatusText(self.stateTitle[ 6] + (AppSettings.CHAR_CHECK if self.connection.FAST else AppSettings.CHAR_BALLOTX), 6)
        self.theStatusBar.SetStatusText(self.stateTitle[ 7] + (AppSettings.CHAR_CHECK if self.connection.CHECKVOLTS else AppSettings.CHAR_BALLOTX), 7)
        self.theStatusBar.SetStatusText(self.stateTitle[ 8] + str(self.connection.TIMEOUT), 8)
        self.theStatusBar.SetStatusText(self.stateTitle[ 9] + str(self.connection.RECONNECTS), 9)
        self.theStatusBar.SetStatusText(self.stateTitle[10] + str(self.connection.DELAY), 10)
        self.theStatusBar.SetStatusText(self.stateTitle[11] + str(AppSettings.DEBUG_LEVEL), 11)

    def setConnectionListCtrl(self, theStatusListCtrl):
        self.theStatusListCtrl = theStatusListCtrl
        self.theStatusListCtrl.InsertColumn(0, "Description", format=wx.LIST_FORMAT_RIGHT, width=150)
        self.theStatusListCtrl.InsertColumn(1, "Value")
        self.theStatusListCtrl.Append(["Link:",          AppSettings.CHAR_BALLOTX])   #  0
        self.theStatusListCtrl.Append(["Protocol:",      self.connection.PROTOCOL])   #  1
        self.theStatusListCtrl.Append(["Cable Version:", "Unknown"])                  #  2
        self.theStatusListCtrl.Append(["Cable Volts:",   "---"])                      #  3
        self.theStatusListCtrl.Append(["Serial Port:",   self.connection.PORTNAME])   #  4
        strBaud = str(self.connection.BAUD) if self.connection.BAUD > 0 else "Auto"
        self.theStatusListCtrl.Append(["Baud:",          strBaud])                    #  5
        self.theStatusListCtrl.Append(["Fast Connect:",  self.connection.FAST])       #  6
        self.theStatusListCtrl.Append(["Check Voltage:", self.connection.CHECKVOLTS]) #  7
        self.theStatusListCtrl.Append(["Timeout:",       self.connection.TIMEOUT])    #  8
        self.theStatusListCtrl.Append(["Reconnects:",    self.connection.RECONNECTS]) #  9
        self.theStatusListCtrl.Append(["Delay:",         self.connection.DELAY])      # 10
        self.theStatusListCtrl.Append(["Debug:",         AppSettings.DEBUG_LEVEL])    # 11

    def updateConnection(self, data):
        self.theStatusListCtrl.SetItem(data[0], data[1], data[2])
        self.theStatusBar.SetStatusText(self.stateTitle[data[0]] + data[2], data[0])

