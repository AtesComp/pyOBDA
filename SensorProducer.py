############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# SensorProducer.py
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
import threading

import AppSettings
from Connection import Connection
from OBD2Port import OBD2Port
from EventDebug import EventDebug
from EventDTC import EventDTC
from EventResult import EventResult
from EventStatus import EventStatus
from EventTest import EventTest
from OBD2Device.Codes import Codes

# A Sensor Producer class to produce sensor managers...
class SensorProducer(threading.Thread):
    def __init__(self, controls): # controls is a Frame object
        super().__init__()
        self.controls = controls
        self.connection = Connection(controls.configDialog.connection)
        self.notebook = controls.notebook
        self.supported = [0] * 3
        self.active = [[]] * 3

    def run(self):
        self.StartProduction()
        self.StopProduction()

    def StartProduction(self):
        wx.PostEvent( self.controls, EventDebug( [2, "Starting Sensor Connection..."] ) )
        wx.PostEvent( self.controls, EventStatus( [0, 1, AppSettings.CHAR_QMARK] ) )
        self.InitCommunication()
        if self.connection.PORT.Connected == False:  # ...cannot connect, exit thread
            wx.PostEvent( self.controls, EventDebug( [1, "ERROR: Connection Failed!"] ) )
            # Signal app that communication failed...
            wx.PostEvent( self.controls, EventStatus( [0, 1, AppSettings.CHAR_CROSSX] ) )
            wx.PostEvent( self.controls, EventStatus( [-1, -1, "SIGNAL: Failed"] ) ) # ...signal connection failure to app
            return

        wx.PostEvent( self.controls, EventDebug( [3, "  Connected"] ) )
        wx.PostEvent( self.controls, EventStatus( [0, 1, AppSettings.CHAR_CHECK] ) )
        wx.PostEvent( self.controls, EventStatus( [2, 1, self.connection.PORT.ELMver] ) )
        wx.PostEvent( self.controls, EventStatus( [3, 1, self.connection.PORT.ELMvolts] ) )
        statePrev = -1
        stateCurr = -1
        while self.controls.ThreadControl != -1:  # ...connected, thread loop...
            statePrev = stateCurr # ...store last state
            stateCurr = self.notebook.GetSelection()

            if stateCurr == 0:  # ...Status Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.controls, EventDebug([2, "Status Page..."] ) )

            elif stateCurr == 1:  # ...Tests Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.controls, EventDebug([2, "Test Page..."] ) )
                results = self.connection.PORT.getStatusTests()
                for iIndex in range(0, len(results)):
                    wx.PostEvent( self.controls, EventTest( [ iIndex, 1, results[iIndex] ] ) )

            elif stateCurr == 2:  # ...Sensor Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.controls, EventDebug( [2, "Sensor Page..."] ) )
                iStartSensors = 3
                if self.controls.iCurrSensorsPage > 0 :
                    iStartSensors = 1

                for iIndex in range(iStartSensors, len(self.active[self.controls.iCurrSensorsPage])):
                    if self.active[self.controls.iCurrSensorsPage][iIndex]:
                        sensor = self.connection.PORT.getSensorInfo(self.controls.iCurrSensorsPage, iIndex)
                        response = [self.controls.iCurrSensorsPage, iIndex, 2, "%s (%s)" % (sensor[1], sensor[2])]
                        wx.PostEvent( self.controls, EventResult(response) )

            elif stateCurr == 3:  # ...DTC Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.controls, EventDebug( [2, "DTC Page..."] ) )

                if self.controls.ThreadControl == 1:  # ...Clear DTC...
                    response = self.connection.PORT.clear_dtc()
                    # Response is N/A for CLEAR_DTC

                    # Before resetting ThreadControl, check for a disconnect
                    if self.controls.ThreadControl == -1:
                        break
                    self.controls.ThreadControl = 2  # ...signal Get DTC command on port

                if self.controls.ThreadControl == 2:  # ...Get DTC...
                    wx.PostEvent( self.controls, EventDTC(0) )  # ...clear list
                    codesDTC = self.connection.PORT.getDTC()
                    if len(codesDTC) == 0:
                        response = ["", "", "No DTC Codes (all clear)"]
                        wx.PostEvent( self.controls, EventDTC(response) )
                    for iIndex in range(0, len(codesDTC)):
                        response = [ codesDTC[iIndex][1], codesDTC[iIndex][0], Codes.Codes[ codesDTC[iIndex][1] ] ]
                        wx.PostEvent( self.controls, EventDTC(response) )

                    # Before resetting ThreadControl, check for a disconnect
                    if self.controls.ThreadControl == -1:  # ...disconnect
                        break
                    self.controls.ThreadControl = 0  # ...signal do nothing on port

            elif stateCurr == 4:  # ...Trace Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.controls, EventDebug( [2, "Trace Page..."] ) )
                # View the trace log...

            else: # ...everything else
                if statePrev != stateCurr :
                    wx.PostEvent( self.controls, EventDebug( [2, "ERROR Page..."] ) )
                # We should never see this message

            if self.controls.ThreadControl == -1:  # ...end thread
                break

    def InitCommunication(self):
        self.connection.PORT = OBD2Port(self.controls, self.connection)
        if self.connection.PORT.Connected == False:  # ...cannot connect to vehicle
            return

        wx.PostEvent( self.controls, EventDebug( [1, "Communication initialized..."] ) )

        # Populate sensor pages with initial data...
        for iSensorGroup in range(3) :
            response = self.connection.PORT.getSensorInfo(iSensorGroup, 0)[1]
            if ( response.isNull() ) :
                # NOTE: Event message already from getSensorInfo()
                self.supported[iSensorGroup] = ""
            else:
                self.supported[iSensorGroup] = response.value  # ...Supported PIDs
            self.active[iSensorGroup] = []

            for iIndex, bSupport in enumerate(self.supported[iSensorGroup]) :
                self.active[iSensorGroup].append(bSupport)

                if bSupport :
                    wx.PostEvent( self.controls, EventResult([iSensorGroup, iIndex, 0, AppSettings.CHAR_CHECK] ) )
                else:
                    wx.PostEvent( self.controls, EventResult([iSensorGroup, iIndex, 0, AppSettings.CHAR_BALLOTX] ) )

        wx.PostEvent( self.controls, EventDebug( [3, "  Sensors marked for support..."] ) )

    def StopProduction(self):
        wx.PostEvent( self.controls, EventDebug( [2, "Stopping Sensor Connection..."] ) )
        # If stop is called on a defined connection port...
        if self.connection.PORT != None:
            self.connection.PORT.close()
            self.connection.PORT = None
        wx.PostEvent( self.controls, EventStatus([0, 1, AppSettings.CHAR_BALLOTX] ) )
        wx.PostEvent( self.controls, EventStatus([2, 1, "Unknown"] ) )
        wx.PostEvent( self.controls, EventStatus([3, 1, "---"] ) )

    def SetIDOff(self, iID):
        wx.PostEvent( self.controls, EventDebug( [2, "Setting Sensor ID OFF"] ) )
        if iID >= 0 and iID < len(self.active):
            self.active[iID] = False
        else:
            wx.PostEvent( self.controls, EventDebug( [2, "Invalid Sensor ID"] ) )

    def SetIDOn(self, iID):
        wx.PostEvent( self.controls, EventDebug( [2, "Setting Sensor ID ON"] ) )
        if iID >= 0 and iID < len(self.active):
            self.active[iID] = True
        else:
            wx.PostEvent( self.controls, EventDebug( [2, "Invalid Sensor ID"] ) )

    def SetAllIDsOff(self):
        for iID in range(0, len(self.active)):
            self.SetIDOff(iID)

    def SetAllIDsOn(self):
        for iID in range(0, len(self.active)):
            self.SetIDOff(iID)

# ...end Class SensorProducer
