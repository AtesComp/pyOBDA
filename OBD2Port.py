############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# OBD2Port.py
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
import OBD2Device

#import string # ...for logSensor()
import time

from EventDebug import EventDebug
from SensorManager import SensorManager
from Sensor import Sensor
from OBD2Device.CommandList import CommandList
from OBD2Device.Response import Response
from OBD2Device.Status import Status

class OBD2Port :
    # OBDPort abstracts all communication with OBD-II devices...

    @classmethod
    def getPorts(cls) :
        return OBD2Device.scanSerialPorts()

    def __init__(self, app, connection): # app is a Frame object, connection is a Connection object
        self.ELMver = "none"
        self.ELMvolts = "none"
        # Connected state for OBD connection is false (disconnected) & true (connected)
        self.Connected = False

        self.app = app
        wx.PostEvent( self.app, EventDebug( [1, "Opening interface (serial port)"] ) )

        self.cmds = CommandList()

        self.port = \
            OBD2Device.OBD2Connector(
                strPort        = connection.PORTNAME,
                iBaudRate      = connection.BAUD,
                strProtocol    = connection.PROTOCOL,
                bFast          = connection.FAST,
                fTimeout       = connection.TIMEOUT,
                bCheckVoltage  = connection.CHECKVOLTS,
                bStartLowPower = False,
            )
        time.sleep(1) # ...wait for it...

        if (self.port != None):
            wx.PostEvent(self.app, EventDebug([1, "Interface: " + self.port.getPortName()]))
            wx.PostEvent(self.app, EventDebug([1, " Protocol: [" + self.port.getProtocolID() + "] " + self.port.getProtocolName()]))
            wx.PostEvent(self.app, EventDebug([1, "   Status: " + self.port.status()]))

        if (self.port == None) or (not self.port.isConnected()) :
            wx.PostEvent(self.app, EventDebug([1, "ERROR: Cannot connect to interface"]))
            return

        self.Connected = True
        wx.PostEvent(self.app, EventDebug([1, "Successfully opened interface"]))
        wx.PostEvent(self.app, EventDebug([1, "Connecting to ECU..." ]))

        response = self.port.query(self.cmds.ELM_VERSION)
        if ( not response.isNull() ) :
            self.ELMver = str(response.value)
        wx.PostEvent(self.app, EventDebug([2, "ELM_VERSION response:" + self.ELMver]))

        response = self.port.query(self.cmds.ELM_VOLTAGE)
        if ( not response.isNull() ) :
            self.ELMvolts = str(response.value)
        wx.PostEvent(self.app, EventDebug([2, "ELM_VOLTS response:" + self.ELMvolts]))

        count = 1
        while True:  # ...loop until connection or exhausted attempts...
            wx.PostEvent( self.app, EventDebug( [2, "Connection attempt:" + str(count) ] ) )
            response = self.port.query(self.cmds.PIDS_A)

            if ( response.isNull() ) :
                wx.PostEvent( self.app, EventDebug( [2, "Connection attempt failed!" ] ) )
                time.sleep(5)
                if (count >= connection.RECONNECTS):
                    self.close()
                    wx.PostEvent( self.app, EventDebug( [2, "Connection attempts exhausted!" ] ) )
                    break
                count += 1
                continue

            self.PIDS_A = str(response.value)
            wx.PostEvent(
                self.app,
                EventDebug( [ 2, "PIDS_A response:" + self.PIDS_A ] )
            )
            break

    def close(self):
        # Resets device and closes all associated file handles...

        if (self.port and self.port != None) and self.Connected == True:
            response = self.port.query(self.cmds.ELM_VERSION) # atz
            self.port.close()

        self.port = None
        self.Connected = False

    def __processCommand(self, command):
        # Internal use only: not a public interface...
        response = Response()
        if self.port :
            wx.PostEvent(self.app, EventDebug([3, "Command: " + str(command)]))
            response = self.port.query(command)
            if ( response.isNull() ) :
                wx.PostEvent(self.app, EventDebug([3, "WARNING: No data!"]))
            else :
                wx.PostEvent(self.app, EventDebug([3, "Results: " + str(response.value)]))
        else :
            wx.PostEvent(self.app, EventDebug([3, "ERROR: No port!"]))
        return response


    # Return tabular sensor response from a sensor index of the current sensor page...
    def getSensorInfo(self, iSensorIndex):
        # Returns 3-tuple of given sensors. 3-tuple consists of
        # ( Sensor Table Descriptor (string), Sensor Response (Response), Sensor Unit (string) )...
        sensor : Sensor = SensorManager.SENSORS[self.app.iCurrSensorsPage][iSensorIndex]
        response = self.__processCommand(sensor.cmd)
        return (sensor.strTableDesc, response, sensor.strUnit)

    # Return tabular sensor response from a sensor group and index...
    def getSensorInfo(self, iSensorGroup, iSensorIndex):
        # Returns 3-tuple of given sensors. 3-tuple consists of
        # ( Sensor Table Descriptor (string), Sensor Response (Response), Sensor Unit (string) )...
        sensor : Sensor = SensorManager.SENSORS[iSensorGroup][iSensorIndex]
        response = self.__processCommand(sensor.cmd)
        return (sensor.strTableDesc, response, sensor.strUnit)


    def getStatusTests(self) -> list[str]:
        statusRes = self.getSensorInfo(0, 1)[1]  # ...Status Since Clear DTC
        if ( statusRes.isNull() ) :
            # NOTE: Event message already from getSensorInfo()
            return []

        # Process Status Items...
        status : Status = statusRes.value
        self.app.setTestIgnition(status.iIgnitionType)
        return status.listText()


    def getDTC(self):
        # Returns a list of all pending DTC codes. Each element consists of
        # a 2-tuple: ( DTC Code (string), Code Description (string) )...
        listDTCCodes = []

        statusRes = self.getSensorInfo(0, 1)[1]  # ...Status Info Response
        if ( statusRes.isNull() ) :
            # NOTE: Event message already from getSensorInfo()
            return listDTCCodes

        status : Status = statusRes.value
        wx.PostEvent(self.app, EventDebug([1, ":::Status:::"]))
        wx.PostEvent(self.app, EventDebug([1, "     MIL: " + str(status.bMIL)]))
        wx.PostEvent(self.app, EventDebug([1, "   DTC #: " + str(status.iDTC)]))
        wx.PostEvent(self.app, EventDebug([1, "Ignition: " + status.getIgnitionText()]))

        # Get all DTC...
        response = self.__processCommand(self.cmds.GET_DTC)
        if ( response.isNull() ) :
            wx.PostEvent(self.app, EventDebug([1, "GET_DTC not supported!"]))
        else :
            iDTCCount = len(response.value)
            if iDTCCount != status.iDTC :
                wx.PostEvent(self.app, EventDebug([2, "WARNING: Status DTC count does not match actual DTC count!"]))
            if (iDTCCount > 0) :
                for DTCCode in response.value :
                    listDTCCodes.append(["Active", DTCCode[0]])

        # Get current DTC...
        response = self.__processCommand(self.cmds.GET_CURRENT_DTC)
        if ( response.isNull() ) :
             wx.PostEvent(self.app, EventDebug([1, "GET_CURRENT_DTC not supported!"]))
        else :
            if (len(response.value) > 0) :
                for DTCCode in response.value :
                    listDTCCodes.append(["Passive", DTCCode[0]])

        return listDTCCodes

    def clearDTC(self):
        # Clears all DTCs and freeze frame data...
        response = self.__processCommand(self.cmds.CLEAR_DTC)
        # NOTE: Error message already from __processCommand()
        return response

    #def logSensor(self, indexSensor, strFilename):
    #    file = open(strFilename, "w")
    #    start_time = time.time()
    #    if file :
    #        data = self.getSensorInfo(indexSensor)
    #        file.write("%s     \t%s(%s)\n" %
    #                   ("Time", string.strip(data[0]), data[2]))
    #        while True:
    #            now = time.time()
    #            data = self.getSensorInfo(indexSensor)
    #            line = "%.6f,\t%s\n" % (now - start_time, str(data[1]))
    #            file.write(line)
    #            file.flush()
