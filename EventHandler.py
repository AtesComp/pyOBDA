############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# EventHandler.py
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
from typing import Callable

import AppSettings
from ListCtrl import ListCtrl
from EventDebug import EventDebug
from EventDTC import EventDTC
from EventSensor import EventSensor
from EventConnection import EventConnection
from EventTest import EventTest

class EventHandler(wx.EvtHandler):
    """
    The pyOBDA Event Handler Class.
    """

    def __init__(self, funcShutdownConnection: Callable, funcUpdateConnection: Callable):
        wx.EvtHandler.__init__(self)
        self.shutdownConnection = funcShutdownConnection
        self.updateConnection = funcUpdateConnection

        self.listctrlConnection = None
        self.listctrlTests = None
        self.listctrlSensors = None
        self.listctrlDTC = None
        self.listctrlDebug = None

        # ====================
        # Connect Process Event Handlers
        # ====================

        self.Connect(-1, -1, EventConnection.ID, self.onConnection)
        self.Connect(-1, -1, EventTest.ID,   self.onTests)
        self.Connect(-1, -1, EventSensor.ID, self.onSensor)
        self.Connect(-1, -1, EventDTC.ID,    self.onDTC)
        self.Connect(-1, -1, EventDebug.ID,  self.onDebug)


    def setConnection(self, listctrlConnection: ListCtrl):
        self.listctrlConnection = listctrlConnection

    def setTests(self, listctrlTests: ListCtrl):
        self.listctrlTests = listctrlTests

    def setSensors(self, listctrlSensors: ListCtrl):
        self.listctrlSensors = listctrlSensors

    def setDTC(self, listctrlDTC: ListCtrl):
        self.listctrlDTC = listctrlDTC

    def setDebug(self, listctrlDebug: ListCtrl):
        self.listctrlDebug = listctrlDebug


    def onConnection(self, event) :
        wx.PostEvent( self, EventDebug( [2, "OnConnection..." + event.data[2]] ) )
        if event.data[0] == -1:  # ...signal for connection failed...
            self.shutdownConnection()
        else :
            self.updateConnection(event.data)

    def onTests(self, event) :
        wx.PostEvent( self, EventDebug([2, "OnTests..."]) )
        self.listctrlTests.SetItem(event.data[0], event.data[1], event.data[2])

    def onSensor(self, event) :
        wx.PostEvent( self, EventDebug([2, "OnSensor..."]) )
        self.listctrlSensors[ event.data[0] ].SetItem(event.data[1], event.data[2], event.data[3])

    def onDTC(self, event) :
        wx.PostEvent( self, EventDebug([2, "OnDTC..."]) )
        if event.data == 0:  # ...signal that DTC was cleared
            self.listctrlDTC.DeleteAllItems()
        else:
            self.listctrlDTC.Append(event.data)

    def onDebug(self, event) :
        if AppSettings.DEBUG_LEVEL >= event.data[0]:
            self.listctrlDebug.Append([str(event.data[0]), event.data[1]])
