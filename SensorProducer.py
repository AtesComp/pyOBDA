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
from typing import Callable

import AppSettings
from Connection import Connection
from OBD2Port import OBD2Port
from SensorManager import SensorManager
from EventHandler import EventHandler
from EventDebug import EventDebug
from EventDTC import EventDTC
from EventResult import EventResult
from EventStatus import EventStatus
from EventTest import EventTest
from OBD2Device.Codes import Codes

class ThreadCommands:
    Null       =  0 # ...Do Nothing
    DTC_Clear  =  1 # ...Clear DTCs
    DTC_Load   =  2 # ...Get DTCs
    Disconnect = -1 # ...Disconnect from vehicle's ECU

# A Sensor Producer class to produce sensor managers...
class SensorProducer(threading.Thread):
    def __init__(self, connection: Connection, notebook: wx.Notebook, events: EventHandler, funcSetTestIgnition: Callable):
        super().__init__()
        self.connection = Connection(connection) # ...copy
        self.PORT = None
        self.notebook = notebook
        self.events = events
        self.setTestIgnition = funcSetTestIgnition

        self.iSensorListLen = len(SensorManager.SENSORS)
        self.supported = [0] * self.iSensorListLen
        self.active = [[]] * self.iSensorListLen

        self.iThreadControl = ThreadCommands.Null
        self.iCurrSensorsPage = 0 # ...starting sensors page

    def run(self):
        self.startProduction()
        self.stopProduction()

    def setThreadControl(self, iThreadControl: int):
        self.iThreadControl = iThreadControl

    def setSensorPage(self, iCurrSensorPage: int):
        self.iCurrSensorsPage = iCurrSensorPage

    def getSensorPage(self) -> int:
        return self.iCurrSensorsPage

    def startProduction(self):
        wx.PostEvent( self.events, EventDebug( [2, "Starting Sensor Connection..."] ) )
        wx.PostEvent( self.events, EventStatus( [0, 1, AppSettings.CHAR_QMARK] ) )
        self.initCommunication()
        if self.PORT.bConnected == False:  # ...cannot connect, exit thread
            wx.PostEvent( self.events, EventDebug( [1, "ERROR: Connection Failed!"] ) )
            # Signal app that communication failed...
            wx.PostEvent( self.events, EventStatus( [0, 1, AppSettings.CHAR_CROSSX] ) )
            wx.PostEvent( self.events, EventStatus( [-1, -1, "SIGNAL: Failed"] ) ) # ...signal connection failure to app
            return

        wx.PostEvent( self.events, EventDebug( [3, "  Connected"] ) )
        wx.PostEvent( self.events, EventStatus( [0, 1, AppSettings.CHAR_CHECK] ) )
        wx.PostEvent( self.events, EventStatus( [2, 1, self.PORT.strELMver] ) )
        wx.PostEvent( self.events, EventStatus( [3, 1, self.PORT.strELMvolts] ) )
        statePrev = -1
        stateCurr = -1
        while self.iThreadControl != ThreadCommands.Disconnect:  # ...thread loop, not disconnecting...
            statePrev = stateCurr # ...store last state
            stateCurr = self.notebook.GetSelection()

            if stateCurr == 0:  # ...Status Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.events, EventDebug([2, "Status Page..."] ) )

            elif stateCurr == 1:  # ...Tests Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.events, EventDebug([2, "Test Page..."] ) )
                astrResults = self.PORT.getStatusTests()
                if astrResults:
                    for iIndex in range(0, len(astrResults)):
                        if (astrResults[iIndex] != None): # ...spacer
                            wx.PostEvent( self.events, EventTest( [ iIndex, 1, astrResults[iIndex] ] ) )

            elif stateCurr == 2:  # ...Sensor Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.events, EventDebug( [2, "Sensor Page..."] ) )
                iStartSensors = 3
                if self.iCurrSensorsPage > 0 :
                    iStartSensors = 1

                for iIndex in range(iStartSensors, len(self.active[self.iCurrSensorsPage])):
                    if self.active[self.iCurrSensorsPage][iIndex]:
                        tupSensorInfo = self.PORT.getSensorInfo(self.iCurrSensorsPage, iIndex)
                        listResponse = [self.iCurrSensorsPage, iIndex, 2, "%s (%s)" % (tupSensorInfo[1], tupSensorInfo[2])]
                        wx.PostEvent( self.events, EventResult(listResponse) )

            elif stateCurr == 3:  # ...DTC Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.events, EventDebug( [2, "DTC Page..."] ) )

                if self.iThreadControl == ThreadCommands.DTC_Clear:
                    listResponse = self.PORT.clearDTC()
                    # Response is N/A for CLEAR_DTC...no need to process

                    # Before resetting ThreadControl, check for a disconnect...
                    if self.iThreadControl == ThreadCommands.Disconnect:
                        break
                    self.iThreadControl = ThreadCommands.DTC_Load

                if self.iThreadControl == ThreadCommands.DTC_Load:
                    wx.PostEvent( self.events, EventDTC(0) )  # ...clear list
                    listCodesDTC = self.PORT.getDTC()
                    if len(listCodesDTC) == 0:
                        listResponse = ["", "", "No DTC Codes (all clear)"]
                        wx.PostEvent( self.events, EventDTC(listResponse) )
                    for iIndex in range(0, len(listCodesDTC)):
                        listResponse = [ listCodesDTC[iIndex][1], listCodesDTC[iIndex][0], Codes.Codes[ listCodesDTC[iIndex][1] ] ]
                        wx.PostEvent( self.events, EventDTC(listResponse) )

                    # Before resetting ThreadControl, check for a disconnect...
                    if self.iThreadControl == ThreadCommands.Disconnect:
                        break
                    self.iThreadControl = ThreadCommands.Null

            elif stateCurr == 4:  # ...Trace Page
                if statePrev != stateCurr :
                    wx.PostEvent( self.events, EventDebug( [2, "Trace Page..."] ) )
                # View the trace log...

            else: # ...everything else
                if statePrev != stateCurr :
                    wx.PostEvent( self.events, EventDebug( [2, "ERROR Page..."] ) )
                    # We should never see this message

            if self.iThreadControl == ThreadCommands.Disconnect:  # ...end thread
                break

    def initCommunication(self):
        self.PORT = OBD2Port(self.connection, self.events, self.getSensorPage, self.setTestIgnition)
        if self.PORT.bConnected == False:  # ...cannot connect to vehicle
            return

        wx.PostEvent( self.events, EventDebug( [1, "Communication initialized..."] ) )

        # Populate sensor pages with initial data...
        for iSensorGroup in range(self.iSensorListLen) :
            response = self.PORT.getSensorInfo(iSensorGroup, 0)[1]
            if ( response.isNull() ) :
                # NOTE: Event message already from getSensorInfo()
                self.supported[iSensorGroup] = ""
            else:
                self.supported[iSensorGroup] = response.value  # ...Supported PIDs
            self.active[iSensorGroup] = []

            for iIndex, bSupport in enumerate(self.supported[iSensorGroup]) :
                self.active[iSensorGroup].append(bSupport)

                if bSupport :
                    wx.PostEvent( self.events, EventResult([iSensorGroup, iIndex, 0, AppSettings.CHAR_CHECK] ) )
                else:
                    wx.PostEvent( self.events, EventResult([iSensorGroup, iIndex, 0, AppSettings.CHAR_BALLOTX] ) )

        wx.PostEvent( self.events, EventDebug( [3, "  Sensors marked for support..."] ) )

    def stopProduction(self):
        wx.PostEvent( self.events, EventDebug( [2, "Stopping Sensor Connection..."] ) )
        # If stop is called on a defined connection port...
        if self.PORT != None:
            self.PORT.close()
            self.PORT = None
        wx.PostEvent( self.events, EventStatus([0, 1, AppSettings.CHAR_BALLOTX] ) )
        wx.PostEvent( self.events, EventStatus([2, 1, "Unknown"] ) )
        wx.PostEvent( self.events, EventStatus([3, 1, "---"] ) )

    def setIDOff(self, iID):
        wx.PostEvent( self.events, EventDebug( [2, "Setting Sensor ID OFF"] ) )
        if iID >= 0 and iID < len(self.active):
            self.active[iID] = False
        else:
            wx.PostEvent( self.events, EventDebug( [2, "Invalid Sensor ID"] ) )

    def setIDOn(self, iID):
        wx.PostEvent( self.events, EventDebug( [2, "Setting Sensor ID ON"] ) )
        if iID >= 0 and iID < len(self.active):
            self.active[iID] = True
        else:
            wx.PostEvent( self.events, EventDebug( [2, "Invalid Sensor ID"] ) )

    def setAllIDsOff(self):
        for iID in range(0, len(self.active)):
            self.setIDOff(iID)

    def setAllIDsOn(self):
        for iID in range(0, len(self.active)):
            self.setIDOff(iID)

# ...end Class SensorProducer
