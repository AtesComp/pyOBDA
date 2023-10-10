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
from EventResult import EventResult
from EventStatus import EventStatus
from EventTest import EventTest

#
# The pyOBDA Event Handler
#
class EventHandler(wx.EvtHandler):
    def __init__(self, funcSensorShutdown: Callable, funcUpdateStatus: Callable):
        wx.EvtHandler.__init__(self)
        self.SensorShutdown = funcSensorShutdown
        self.UpdateStatus = funcUpdateStatus

        self.listctrlTests = None
        self.listctrlSensors = None
        self.listctrlDTC = None
        self.listctrlStatus = None
        self.listctrlTrace = None

        # ====================
        # Connect Process Event Handlers
        # ====================

        self.Connect(-1, -1, EventTest.ID,   self.OnTests)
        self.Connect(-1, -1, EventResult.ID, self.OnResult)
        self.Connect(-1, -1, EventDTC.ID,    self.OnDTC)
        self.Connect(-1, -1, EventStatus.ID, self.OnStatus)
        self.Connect(-1, -1, EventDebug.ID,  self.OnDebug)


    def SetTests(self, listctrlTests: ListCtrl):
        self.listctrlTests = listctrlTests

    def SetSensors(self, listctrlSensors: ListCtrl):
        self.listctrlSensors = listctrlSensors

    def SetDTC(self, listctrlDTC: ListCtrl):
        self.listctrlDTC = listctrlDTC

    def SetStatus(self, listctrlStatus: ListCtrl):
        self.listctrlStatus = listctrlStatus

    def SetTrace(self, listctrlTrace: ListCtrl):
        self.listctrlTrace = listctrlTrace


    def OnTests(self, event) :
        wx.PostEvent( self, EventDebug([2, "OnTests..."]) )
        self.listctrlTests.SetItem(event.data[0], event.data[1], event.data[2])

    def OnResult(self, event) :
        wx.PostEvent( self, EventDebug([2, "OnResult..."]) )
        self.listctrlSensors[ event.data[0] ].SetItem(event.data[1], event.data[2], event.data[3])

    def OnDTC(self, event) :
        wx.PostEvent( self, EventDebug([2, "OnDTC..."]) )
        if event.data == 0:  # ...signal that DTC was cleared
            self.listctrlDTC.DeleteAllItems()
        else:
            self.listctrlDTC.Append(event.data)

    def OnStatus(self, event) :
        wx.PostEvent( self, EventDebug( [2, "OnStatus..." + event.data[2]] ) )
        if event.data[0] == -1:  # ...signal for connection failed...
            self.SensorShutdown()
        else :
            self.UpdateStatus(event.data)

    def OnDebug(self, event) :
        if AppSettings.DEBUG_LEVEL >= event.data[0]:
            self.listctrlTrace.Append([str(event.data[0]), event.data[1]])
