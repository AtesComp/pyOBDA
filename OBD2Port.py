############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# OBD2Port.py
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
import OBD2Device

#import string # ...for logSensor()
import time

from SensorManager import SensorManager
from EventDebug import EventDebug
from OBD2Device.CommandList import CommandListObj

class OBD2Port :
    # OBDPort abstracts all communication with OBD-II devices...

    def getPorts() :
        return OBD2Device.scan_serial()

    def __init__(self, app, connection):
        self.ELMver = "none"
        self.ELMvolts = "none"
        # Connected state for OBD connection is false (disconnected) & true (connected)
        self.Connected = False

        self.app = app
        wx.PostEvent(self.app, EventDebug([1, "Opening interface (serial port)"]))

        self.port = \
            OBD2Device.OBD2Connector(
                portstr       = connection.PORTNAME,
                baudrate      = connection.BAUD,
                protocol      = connection.PROTOCOL,
                fast          = connection.FAST,
                timeout       = connection.TIMEOUT,
                check_voltage = connection.CHECKVOLTS
            )
        time.sleep(1) # ...wait for it...

        if (self.port != None):
            wx.PostEvent(self.app, EventDebug([1, "Interface: " + self.port.port_name()]))
            wx.PostEvent(self.app, EventDebug([1, " Protocol: [" + self.port.protocol_id() + "] " + self.port.protocol_name()]))
            wx.PostEvent(self.app, EventDebug([1, "   Status: " + self.port.status()]))

        if (self.port == None) or (not self.port.is_connected()) :
            wx.PostEvent(self.app, EventDebug([1, "ERROR: Cannot connect to interface"]))
            return

        self.Connected = True
        wx.PostEvent(self.app, EventDebug([1, "Successfully opened interface"]))
        wx.PostEvent(self.app, EventDebug([1, "Connecting to ECU..." ]))

        response = self.port.query(CommandListObj.ELM_VERSION)
        if ( not response.is_null() ) :
            self.ELMver = str(response.value)
        wx.PostEvent(self.app, EventDebug([2, "ELM_VERSION response:" + self.ELMver]))

        response = self.port.query(CommandListObj.ELM_VOLTAGE)
        if ( not response.is_null() ) :
            self.ELMvolts = str(response.value)
        wx.PostEvent(self.app, EventDebug([2, "ELM_VOLTS response:" + self.ELMvolts]))

        count = 1
        while True:  # ...loop until connection or exhausted attempts...
            wx.PostEvent( self.app, EventDebug( [2, "Connection attempt:" + str(count) ] ) )
            response = self.port.query(CommandListObj.PIDS_A)

            if ( response.is_null() ) : # ...if no response...
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
            response = self.port.query(CommandListObj.ELM_VERSION) # atz
            self.port.close()

        self.port = None
        self.Connected = False

    def __processCommand(self, command):
        # Internal use only: not a public interface...
        response = "NORESPONSE"
        if self.port:
            wx.PostEvent(self.app, EventDebug([3, "Command: " + str(command)]))
            response = self.port.query(command)
            if response != None :
                wx.PostEvent(self.app, EventDebug([3, "Results: " + str(response.value)]))
            else :
                response = "NODATA"
        else:
            wx.PostEvent(self.app, EventDebug([3, "ERROR: NO port!"]))
        return response

    # Return string of sensor name and value from sensor index...
    def getSensorInfo(self, iSensorIndex):
        # Returns 3-tuple of given sensors. 3-tuple consists of
        # ( Sensor Name (string), Sensor Value (string), Sensor Unit (string) )...
        sensor = SensorManager.SENSORS[self.app.iCurrSensorsPage][iSensorIndex]
        response = self.__processCommand(sensor.cmd)
        return (sensor.name, response, sensor.unit)

    # Return string of sensor name and value from sensor index...
    def getSensorInfo(self, iSensorGroup, iSensorIndex):
        # Returns 3-tuple of given sensors. 3-tuple consists of
        # ( Sensor Name (string), Sensor Value (string), Sensor Unit (string) )...
        sensor = SensorManager.SENSORS[iSensorGroup][iSensorIndex]
        response = self.__processCommand(sensor.cmd)
        return (sensor.name, response, sensor.unit)

    def __getSensorNames(self):
        # Internal use only: not a public interface...
        names = []
        for sensor in SensorManager.SENSORS[self.app.iCurrSensorsPage]:
            names.append(sensor.name)
        return names

    def getStatusTests(self):
        statusTrans = []  # ...translate values to text
        statusText = ["Unavailable", "Available: Incomplete", "Available: Complete"]

        statusRes = self.getSensorInfo(0, 1)[1]  # ...Status Since Clear DTC
        if (statusRes == "NORESPONSE" or statusRes == "NODATA") :
            return statusTrans

        #
        # Process Status Items...
        #

        # DTC Count...
        statusTrans.append( str( statusRes.value.DTC_count ) )

        # MIL...
        if statusRes.value.MIL :
            statusTrans.append("On")
        else :
            statusTrans.append("Off")

        # Ignition Type...
        statusTrans.append( statusRes.value.ignition_type )

        iStatus = 1 if statusRes.value.MISFIRE_MONITORING.available else 0
        iStatus += 1 if statusRes.value.MISFIRE_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.FUEL_SYSTEM_MONITORING.available else 0
        iStatus += 1 if statusRes.value.FUEL_SYSTEM_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.COMPONENT_MONITORING.available else 0
        iStatus += 1 if statusRes.value.COMPONENT_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.CATALYST_MONITORING.available else 0
        iStatus += 1 if statusRes.value.CATALYST_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.HEATED_CATALYST_MONITORING.available else 0
        iStatus += 1 if statusRes.value.HEATED_CATALYST_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.EVAPORATIVE_SYSTEM_MONITORING.available else 0
        iStatus += 1 if statusRes.value.EVAPORATIVE_SYSTEM_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.SECONDARY_AIR_SYSTEM_MONITORING.available else 0
        iStatus += 1 if statusRes.value.SECONDARY_AIR_SYSTEM_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.OXYGEN_SENSOR_MONITORING.available else 0
        iStatus += 1 if statusRes.value.OXYGEN_SENSOR_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.OXYGEN_SENSOR_HEATER_MONITORING.available else 0
        iStatus += 1 if statusRes.value.OXYGEN_SENSOR_HEATER_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.EGR_VVT_SYSTEM_MONITORING.available else 0
        iStatus += 1 if statusRes.value.EGR_VVT_SYSTEM_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.NMHC_CATALYST_MONITORING.available else 0
        iStatus += 1 if statusRes.value.NMHC_CATALYST_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.NOX_SCR_AFTERTREATMENT_MONITORING.available else 0
        iStatus += 1 if statusRes.value.NOX_SCR_AFTERTREATMENT_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.BOOST_PRESSURE_MONITORING.available else 0
        iStatus += 1 if statusRes.value.BOOST_PRESSURE_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.EXHAUST_GAS_SENSOR_MONITORING.available else 0
        iStatus += 1 if statusRes.value.EXHAUST_GAS_SENSOR_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        iStatus = 1 if statusRes.value.PM_FILTER_MONITORING.available else 0
        iStatus += 1 if statusRes.value.PM_FILTER_MONITORING.complete else 0
        statusTrans.append( statusText[ iStatus ] )

        return statusTrans

    def getDTC(self):
        # Returns a list of all pending DTC codes. Each element consists of
        # a 2-tuple: ( DTC Code (string), Code Description (string) )...
        statusRes = self.getSensorInfo(0, 1)[1]  # ...Status Info Response
        print(":::Status:::")
        print("     MIL: " + str(statusRes.value.MIL))
        print("   DTC #: " + str(statusRes.value.DTC_count))
        print("Ignition: " + str(statusRes.value.ignition_type))

        # Get all DTC...
        listDTCCodes = []
        response = self.__processCommand(CommandListObj.GET_DTC)
        if ( response.is_null() ) :
            wx.PostEvent(self.app, EventDebug([1, "GET_DTC not supported!"]))
        else :
            iDTCCount = len(response.value)
            if iDTCCount != statusRes.value.DTC_count :
                wx.PostEvent(self.app, EventDebug([2, "WARNING: Status DTC count does not match actual DTC count!"]))
            if (iDTCCount > 0) :
                for DTCCode in response.value :
                    listDTCCodes.append(["Active", DTCCode[0]])

        # Get current DTC...
        response = self.__processCommand(CommandListObj.GET_CURRENT_DTC)
        if ( response.is_null() ) :
             wx.PostEvent(self.app, EventDebug([1, "GET_CURRENT_DTC not supported!"]))
        else :
            if (len(response.value) > 0) :
                for DTCCode in response.value :
                    listDTCCodes.append(["Passive", DTCCode[0]])

        return listDTCCodes

    def clearDTC(self):
        # Clears all DTCs and freeze frame data...
        response = self.__processCommand(CommandListObj.CLEAR_DTC)
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
