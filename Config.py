############################################################################
#
# Config.py
#
# Copyright 2023 Keven L. Ates (atescomp@gmail.com)
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
# along with pyOBDA; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
############################################################################

import wx

import os  # ...for os.environ
import sys
import configparser  # ...safe application configuration
from os import path, mkdir

import Connection
import EventDebug
import OBD2Port
import Utility

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self, parent, wx.ID_ANY, title="Configure",
            size=(400, 200), style=wx.DIALOG_ADAPTATION_STANDARD_SIZER )

        self.SetBackgroundColour('BLACK')
        self.SetForegroundColour('WHITE')
        self.initialize()

    def initialize(self):
        global DEBUG_LEVEL

        # Set up to read settings from file...
        self.config = configparser.RawConfigParser()
        self.configSettings = Connection(None)

        #print( platform.system() )
        #print( platform.mac_ver()[] )

        self.stateTitle = [
            "Link: ",
            "Proto: ",
            "Cable: ",
            "Volts: ", # Cable Volts
            "Port: ",
            "Baud: ",
            "Fast: ",
            "Check: ", # Check Voltage
            "Timeout: ",
            "Times: ",
            "Debug: " ]

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
            self.configSettings.resetConnection()
        else :
            if not self.config.has_section("OBD") :
                self.config.add_section("OBD")
            if not self.config.has_section("DEBUG") :
                self.config.add_section("DEBUG")
            self.configSettings.PORTNAME = self.config.get("OBD", "PORT", fallback="/dev/ttyUSB0")
            strBaud = self.config.get("OBD", "BAUD", fallback="")
            if (strBaud == "Auto") :
                self.configSettings.BAUD = 0
            else :
                self.configSettings.BAUD = self.config.getint("OBD", "BAUD", fallback=115200)
            self.configSettings.PROTOCOL = self.config.get("OBD", "PROTOCOL", fallback="6")
            self.configSettings.FAST = self.config.getboolean("OBD", "FAST", fallback=True)
            self.configSettings.CHECKVOLTS = self.config.getboolean("OBD", "CHECKVOLTS", fallback=True)
            self.configSettings.TIMEOUT = self.config.getint("OBD", "TIMEOUT", fallback=10)
            self.configSettings.RECONNECTS = self.config.getint("OBD", "RECONNECTS", fallback=3)
            DEBUG_LEVEL = self.config.getint("DEBUG", "LEVEL", fallback=1)


        # Common Positions and Sizes...
        sizeStaticText = ( 95, 40)
        sizeChoiceText = (305, 40)
        sizeCheckText  = (300, 40)
        posTextCtrl    = (100, -10)
        sizeTextCtrl   = ( 50, 40)
        sizeButton     = ( 80, 30)

        # Serial Ports Input RadioBox...
        self.checkPorts()
        panelPorts = wx.Panel(self)
        staticPorts = wx.StaticText(
            panelPorts, wx.ID_ANY, 'Serial Port:', size = sizeStaticText, style = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.choicePorts = wx.Choice(panelPorts, wx.ID_ANY, posTextCtrl, sizeChoiceText, self.ports)
        # Set the default serial port choice...
        iIndex = 0
        if (self.configSettings.PORTNAME != None) and (self.configSettings.PORTNAME in self.ports):
            iIndex = self.ports.index(self.configSettings.PORTNAME)
        self.choicePorts.SetSelection(iIndex)

        # Serial Baud Input Panel & Control...
        # 9600, 19200, 38400, 57600, 115200
        self.bauds = \
            [   "Auto Select",
                "9600",
                "19200",
                "38400",
                "57600",
                "115200",
            ]
        panelBauds = wx.Panel(self)
        staticBauds = wx.StaticText(
            panelBauds, wx.ID_ANY, 'Baud Rate:', size=sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.choiceBauds = wx.Choice(panelBauds, wx.ID_ANY, posTextCtrl, sizeChoiceText, self.bauds)
        # Set the default connection protocol choice...
        iIndex = 0
        strBaud = str(self.configSettings.BAUD)
        if (self.configSettings.BAUD != None) and (strBaud in self.bauds) :
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
        panelProtocols = wx.Panel(self)
        staticProtocols = wx.StaticText(
            panelProtocols, wx.ID_ANY, 'Protocol:', size=sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.choiceProtocols = wx.Choice(panelProtocols, wx.ID_ANY, posTextCtrl, sizeChoiceText, protocols)
        # Set the default connection protocol choice...
        iIndex = 0
        if (self.configSettings.PROTOCOL != None) and (self.configSettings.PROTOCOL in self.protocolShort) :
            iIndex = self.protocolShort.index(self.configSettings.PROTOCOL)
        self.choiceProtocols.SetSelection(iIndex)

        self.checkFast = \
            wx.CheckBox(
                self, wx.ID_ANY, "Fast Connect?", size=sizeCheckText, style=wx.CHK_2STATE)
        if (self.configSettings.FAST == True) :
            self.checkFast.SetValue(self.configSettings.FAST)

        self.checkVolts = \
            wx.CheckBox(
                self, wx.ID_ANY, "Check Voltage?", size=sizeCheckText, style=wx.CHK_2STATE)
        if (self.configSettings.CHECKVOLTS == True) :
            self.checkVolts.SetValue(self.configSettings.CHECKVOLTS)

        # Timeout Input Panel & Control...
        panelTimeout = wx.Panel(self)
        staticTimeout = wx.StaticText(
            panelTimeout, wx.ID_ANY, 'Timeout:', size=sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.ctrlTimeout = wx.TextCtrl(
            panelTimeout, wx.ID_ANY, str(self.configSettings.TIMEOUT), posTextCtrl, sizeTextCtrl)

        # Reconnects Input Panel & Control...
        panelReconnect = wx.Panel(self)
        staticReconnect = wx.StaticText(
            panelReconnect, wx.ID_ANY, 'Reconnects:', size=sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.ctrlReconnect = wx.TextCtrl(
            panelReconnect, wx.ID_ANY, str(self.configSettings.RECONNECTS), posTextCtrl, sizeTextCtrl)

        # Debug Level Input Panel & Control...
        panelDebugLevel = wx.Panel(self)
        staticDebugLevel = wx.StaticText(
            panelDebugLevel, wx.ID_ANY, 'Debug:', size=sizeStaticText, style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.ctrlDebugLevel = wx.TextCtrl(
            panelDebugLevel, wx.ID_ANY, str(DEBUG_LEVEL), posTextCtrl, sizeTextCtrl)

        boxButtons = wx.BoxSizer(wx.HORIZONTAL)
        boxButtons.Add(wx.Button(self, wx.ID_OK,     size=sizeButton))
        boxButtons.Add(wx.Button(self, wx.ID_CANCEL, size=sizeButton))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panelPorts,      1, wx.LEFT)
        sizer.Add(panelBauds,      1, wx.LEFT)
        sizer.Add(panelProtocols,  1, wx.LEFT)
        sizer.Add(self.checkFast,  1, wx.LEFT)
        sizer.Add(self.checkVolts, 1, wx.LEFT)
        sizer.Add(panelTimeout,    0, wx.LEFT)
        sizer.Add(panelReconnect,  0, wx.LEFT)
        sizer.Add(panelDebugLevel, 0, wx.LEFT)
        sizer.Add(boxButtons,      1, wx.CENTER)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def checkPorts(self):
        self.ports = OBD2Port.getPorts()
        self.bGoodPorts = True
        if (len(self.ports) <= 0) :
            self.bGoodPorts = False
            self.ports = ["No Available Devices on Ports!"]

    def processSettings(self, controls, result):
        if (result == wx.ID_OK):
            # Create sections...
            if not self.config.has_section("OBD") :
                self.config.add_section("OBD")
            if not self.config.has_section("DEBUG") :
                self.config.add_section("DEBUG")

            # Set and save CONNECTION STATE...
            iIndex = 0
            if self.bGoodPorts:
                controls.listctrlStatus.SetItem(iIndex, 1, "CONNECTION STATE by SensorProducer")
                controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + Utility.CHAR_QMARK, iIndex)

            # Set and save PROTOCOL...
            iIndex += 1
            self.configSettings.PROTOCOL = self.protocolShort[self.choiceProtocols.GetSelection()]
            self.config.set("OBD", "PROTOCOL", self.configSettings.PROTOCOL)
            controls.listctrlStatus.SetItem(iIndex, 1, self.configSettings.PROTOCOL)
            controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + self.configSettings.PROTOCOL, iIndex)

            # Set and save CABLE VERSION...
            iIndex += 1
            if self.bGoodPorts:
                controls.listctrlStatus.SetItem(iIndex, 1, "CABLE VERSION by SensorProducer")
                controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + "CABLE VERSION by SensorProducer", iIndex)

            # Set and save CABLE VOLTAGE...
            iIndex += 1
            if self.bGoodPorts:
                controls.listctrlStatus.SetItem(iIndex, 1, "CABLE VOLTAGE by SensorProducer")
                controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + "CABLE VOLTAGE by SensorProducer", iIndex)

            # Set and save PORTNAME...
            iIndex += 1
            if self.bGoodPorts:
                self.configSettings.PORTNAME = self.ports[self.choicePorts.GetSelection()]
            else:
                self.configSettings.PORTNAME = Connection.strPortNameDefault
            self.config.set("OBD", "PORT", self.configSettings.PORTNAME)
            controls.listctrlStatus.SetItem(iIndex, 1, self.configSettings.PORTNAME)
            controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + self.configSettings.PORTNAME, iIndex)

            # Set and save BAUD...
            iIndex += 1
            if self.choiceBauds.GetSelection() == 0 :
                self.configSettings.BAUD = "Auto"
            else :
                self.configSettings.BAUD = int(self.bauds[self.choiceBauds.GetSelection()])
            self.config.set("OBD", "BAUD", self.configSettings.BAUD)
            strBaud = str(self.configSettings.BAUD)
            controls.listctrlStatus.SetItem(iIndex, 1, strBaud)
            controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + strBaud, iIndex)

            # Set and save FAST...
            iIndex += 1
            self.configSettings.FAST = self.checkFast.GetValue()
            self.config.set("OBD", "FAST", self.configSettings.FAST)
            strFast = str(self.configSettings.FAST)
            controls.listctrlStatus.SetItem(iIndex, 1, strFast)
            controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + (Utility.CHAR_CHECK if self.configSettings.FAST else Utility.CHAR_BALLOTX), iIndex)

            # Set and save CHECKVOLTS...
            iIndex += 1
            self.configSettings.CHECKVOLTS = self.checkVolts.GetValue()
            self.config.set("OBD", "CHECKVOLTS", self.configSettings.CHECKVOLTS)
            strCheckVolts = str(self.configSettings.CHECKVOLTS)
            controls.listctrlStatus.SetItem(iIndex, 1, strCheckVolts)
            controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + (Utility.CHAR_CHECK if self.configSettings.CHECKVOLTS else Utility.CHAR_BALLOTX), iIndex)

            # Set and save TIMEOUT...
            iIndex += 1
            self.configSettings.TIMEOUT = int(self.ctrlTimeout.GetValue())
            self.config.set("OBD", "TIMEOUT", self.configSettings.TIMEOUT)
            strTimeOut = str(self.configSettings.TIMEOUT)
            controls.listctrlStatus.SetItem(iIndex, 1, strTimeOut)
            controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + strTimeOut, iIndex)

            # Set and save RECONNECTS...
            iIndex += 1
            self.configSettings.RECONNECTS = int(self.ctrlReconnect.GetValue())
            self.config.set("OBD", "RECONNECTS", self.configSettings.RECONNECTS)
            strReconnects = str(self.configSettings.RECONNECTS)
            controls.listctrlStatus.SetItem(iIndex, 1, strReconnects)
            controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + strReconnects, iIndex)

            # Set and save DEBUGLEVEL...
            iIndex += 1
            DEBUG_LEVEL = int(self.ctrlDebugLevel.GetValue())
            self.config.set("DEBUG", "LEVEL", DEBUG_LEVEL)
            strDebugLevel = str(DEBUG_LEVEL)
            controls.listctrlStatus.SetItem(iIndex, 1, strDebugLevel)
            controls.StatusBar.SetStatusText(self.stateTitle[iIndex] + strDebugLevel, iIndex)

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

    def setStatusBar(self, theStatusBar, ):
        theStatusBar.SetStatusWidths([50, 58, -1, 58, -1, 96, 50, 62, 90, 68, 94])
        theStatusBar.SetStatusText(self.stateTitle[ 0] + Utility.CHAR_BALLOTX, 0)
        theStatusBar.SetStatusText(self.stateTitle[ 1] + self.configSettings.PROTOCOL, 1)
        theStatusBar.SetStatusText(self.stateTitle[ 2] + "Unknown", 2)
        theStatusBar.SetStatusText(self.stateTitle[ 3] + "---", 3)
        theStatusBar.SetStatusText(self.stateTitle[ 4] + self.configSettings.PORTNAME, 4)
        theStatusBar.SetStatusText(self.stateTitle[ 5] + str(self.configSettings.BAUD), 5)
        theStatusBar.SetStatusText(self.stateTitle[ 6] + (Utility.CHAR_CHECK if self.configSettings.FAST else Utility.CHAR_BALLOTX), 6)
        theStatusBar.SetStatusText(self.stateTitle[ 7] + (Utility.CHAR_CHECK if self.configSettings.CHECKVOLTS else Utility.CHAR_BALLOTX), 7)
        theStatusBar.SetStatusText(self.stateTitle[ 8] + str(self.configSettings.TIMEOUT), 8)
        theStatusBar.SetStatusText(self.stateTitle[ 9] + str(self.configSettings.RECONNECTS), 9)
        theStatusBar.SetStatusText(self.stateTitle[10] + str(DEBUG_LEVEL), 10)

    def setStatusListCtrl(self, theStatusListCtrl):
        theStatusListCtrl.InsertColumn(0, "Description", format=wx.LIST_FORMAT_RIGHT, width=150)
        theStatusListCtrl.InsertColumn(1, "Value")
        theStatusListCtrl.Append(["Link:",          Utility.CHAR_BALLOTX])           #  0
        theStatusListCtrl.Append(["Protocol:",      self.configSettings.PROTOCOL])   #  1
        theStatusListCtrl.Append(["Cable Version:", "Unknown"])                      #  2
        theStatusListCtrl.Append(["Cable Volts:",   "---"])                          #  3
        theStatusListCtrl.Append(["Serial Port:",   self.configSettings.PORTNAME])   #  4
        theStatusListCtrl.Append(["Baud:",          self.configSettings.BAUD])       #  5
        theStatusListCtrl.Append(["Fast Connect:",  self.configSettings.FAST])       #  6
        theStatusListCtrl.Append(["Check Voltage:", self.configSettings.CHECKVOLTS]) #  7
        theStatusListCtrl.Append(["Timeout:",       self.configSettings.TIMEOUT])    #  8
        theStatusListCtrl.Append(["Reconnects:",    self.configSettings.RECONNECTS]) #  9
        theStatusListCtrl.Append(["Debug:",         DEBUG_LEVEL])                    # 10

    def updateStatus(self, controls, iItem, iColumn, strValue):
        controls.listctrlStatus.SetItem(iItem, iColumn, strValue)
        controls.StatusBar.SetStatusText(self.stateTitle[iItem] + strValue, iItem)

