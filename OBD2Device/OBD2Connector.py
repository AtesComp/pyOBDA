############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# OBD2Connector.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file "obd/odb.py"
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


import logging
import errno
import glob
import sys
import serial

from .ELM327 import ELM327
from .CommandList import CommandList
from .Command import Command
from .ConnectionStatus import ConnectionStatus
from .Response import Response
from .Protocols.ECU import ECU


logger = logging.getLogger(__name__)


#
# Class: OBD II Connector
#
class OBD2Connector(object):
    """
    Class representing an OBD-II connection with it's assorted commands and sensors.

    This class uses a synchronous value reporting process.
    """

    @classmethod
    def __isPortAvailable(cls, strPort : str):
        # Is a port available?
        try:
            serialPort = serial.Serial(strPort)
            serialPort.close()  # ...explicit close
            # Available...
            return True
        except serial.SerialException:
            pass
        except OSError as e:
            # If NOT a No Entry (File or Directory) error...
            if e.errno != errno.ENOENT:
                # ...throw that error...
                raise e
        # Otherwise, not available...
        return False

    @classmethod
    def scanSerialPorts(cls):
        """
        Scan for available serial ports.
        """

        # Get all possible ports...
        listPortsPossible : list[str]  = []
        if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            listPortsPossible += glob.glob("/dev/rfcomm[0-9]*")
            listPortsPossible += glob.glob("/dev/ttyUSB[0-9]*")
        elif sys.platform.startswith('win'):
            listPortsPossible += ["\\.\COM%d" % i for i in range(256)]
        elif sys.platform.startswith('darwin'):
            listPortsExclude = [
                '/dev/tty.Bluetooth-Incoming-Port',
                '/dev/tty.Bluetooth-Modem'
            ]
            listPortsPossible += [port for port in glob.glob('/dev/tty.*') if port not in listPortsExclude]
        #listPortsPossible += glob.glob('/dev/pts/[0-9]*') # for OBDSim?

        listPortsAvailable : list[str] = []
        for strPort in listPortsPossible:
            if cls.__isPortAvailable(strPort):
                listPortsAvailable.append(strPort)

        return listPortsAvailable


    def __init__(self, strPort:str = "", iBaudRate:int = 0, strProtocol:str = "", bFast:bool = True,
                 fTimeout:float = 0.1, bCheckVoltage:bool = True, bStartLowPower:bool = False):
        self.interface:(ELM327|None) = None
        self.CMDS = CommandList()
        self.listCommandsSupported:list = set(self.CMDS.getBaseCmds())
        self.bFast:bool = bFast  # ...switch to allow optimizations
        self.fTimeout:float = fTimeout
        self.__baLastCommand:bytearray = b""  # ...store previous command to run with a CR
        self.__baLastHeader:bytearray = ECU.HEADER.ENGINE  # ...to compare with previously used header
        self.__dictFrameCounts:dict = {}  # ...count the number of return frames for each command

        # Validate parameters...
        if strPort == "" or strPort.startswith("Auto"):
            strPort = None

        logger.info("=== OBD-II Connector ===")
        # Connect and load sensors...
        self.__connect(strPort, iBaudRate, strProtocol, bCheckVoltage, bStartLowPower)
        # Load the vehicles's supported commands...
        self.__loadCmds()
        logger.info("========================")

    def __connect(self, strPort, iBaudRate, strProtocol, bCheckVoltage,
                  bStartLowPower):
        """
        Attempt to connect to an ELM327 device.
        """

        if strPort is None :
            logger.info("Scanning for serial ports...")
            astrPortNames = self.scanSerialPorts()
            logger.info("Available ports: " + str(astrPortNames))

            if not astrPortNames:
                logger.warning("No OBD-II adapters found!")
                return

            for strPort in astrPortNames :
                if not strPort :
                    continue
                logger.info("Attempting to use port: " + strPort)
                self.interface = ELM327(strPort, iBaudRate, strProtocol,
                                        self.fTimeout, bCheckVoltage,
                                        bStartLowPower)

                if self.interface.getStatus() >= ConnectionStatus.ELM :
                    break  # ...success! stop searching for serial port
        else:
            logger.info("Attempting to use configured port:" + strPort)
            self.interface = ELM327(strPort, iBaudRate, strProtocol,
                                    self.fTimeout, bCheckVoltage,
                                    bStartLowPower)

        # If the connection failed, close it...
        if self.interface.getStatus() == ConnectionStatus.NONE :
            # The ELM327 class will report its own errors
            self.close()

    def __loadCmds(self):
        """
        Queries for available PIDs, sets their support status, and compiles a list of command objects.
        """

        if self.status() != ConnectionStatus.VEHICLE :
            logger.warning("No Connection: Cannot load commands!")
            return

        logger.info("Querying for supported commands...")
        cmdsPID = self.CMDS.getPIDCmds()
        for cmdPID in cmdsPID :
            # NOTE: PID listing commands should sequentially become supported.
            #       Mode 1 PID 0 is assumed to always be supported.
            if not self.isCmdUsable(cmdPID) :
                continue

            # NOTE: When querying, only use the blocking OBD2Connector.query().
            #       This prevents problems when the query is redefined in a subclass (like OBD2ConnectorAsync)
            response = OBD2Connector.query(self, cmdPID)

            if ( response.isNull() ) :
                logger.warn("No valid data for PID listing command: %s" % cmdPID)
                continue

            # Loop through PIDs bit-array...
            for iIndex, bBit in enumerate(response.value) :
                if bBit :
                    iMode = cmdPID.mode
                    iPID = cmdPID.pid + iIndex + 1

                    if self.CMDS.hasPID(iMode, iPID) :
                        self.listCommandsSupported.add(self.CMDS[iMode][iPID])

                    # If Mode 1 command, set support for same Mode 2 command...
                    if iMode == 1 and self.CMDS.hasPID(2, iPID) :
                        self.listCommandsSupported.add(self.CMDS[2][iPID])

        logger.info("Finished querying with %d commands supported." % len(self.listCommandsSupported))

    def __setHeader(self, header):
        """
        Set the default header for commands.
        """

        # If this header is also the last header...
        if header == self.__baLastHeader:
            return # ...nothing to do

        # Set the new header...
        listMsg = self.interface.send_and_parse(b'AT SH ' + header + b' ')

        # If there is no result...
        if not listMsg:
            # ...log and return empty response...
            logger.info("Set Header ('AT SH %s') did not return data", header)
            return Response()

        # If the response is NOT OK...
        if "".join( [msg.raw() for msg in listMsg] ) != "OK":
            # ...log and return empty response...
            logger.info("Set Header ('AT SH %s') did not return 'OK'", header)
            return Response()

        # Set the new header as the last header...
        self.__baLastHeader = header

    def close(self):
        """
        Closes the connection and clears supported commands.
        """

        self.listCommandsSupported = set()

        if self.interface is not None :
            logger.info("Closing connection")
            self.__setHeader(ECU.HEADER.ENGINE)
            self.interface.close()
            self.interface = None

    def status(self):
        """
        Return the OBD connection status.
        """

        if self.interface is None :
            return ConnectionStatus.NONE
        else :
            return self.interface.getStatus()

    def setLowPower(self):
        """
        Enter Low Power mode.
        """

        if self.interface is None :
            return ConnectionStatus.NONE
        else :
            return self.interface.setToLowPower()

    def setNormalPower(self):
        """
        Exit Low Power mode.
        """

        if self.interface is None :
            return ConnectionStatus.NONE
        else :
            return self.interface.setToNormalPower()

    # TODO: Review for usefulness
    def getECUs(self) -> list:
        """
        Get a list of ECUs in the vehicle.
        """

        if self.interface is None:
            return []
        else:
            return list( self.interface.getECUsValues() )

    def getProtocolName(self):
        """
        Return the name of the protocol being used by the ELM327.
        """

        if self.interface is None :
            return ""
        else :
            return self.interface.getProtocolName()

    def getProtocolID(self):
        """
        Return the ID of the protocol being used by the ELM327.
        """

        if self.interface is None :
            return ""
        else :
            return self.interface.getProtocolID()

    def getPortName(self):
        """
        Return the name of the currently connected port.
        """

        if self.interface is not None :
            return self.interface.getPortName()
        else :
            return ""

    def isConnected(self):
        """
        Is a vehicle connected?

        NOTE: This function returns False when the connector's status indicates ConnectionStatus.VEHICLE (i.e., "Vehicle Connected")
        """

        return self.status() == ConnectionStatus.VEHICLE

    def printCmds(self):
        """
        Utility function for connection working in interactive mode. Prints all commands supported by the vehicle.
        """

        for cmd in self.listCommandsSupported :
            print(str(cmd))

    def isCmdSupported(self, cmd):
        """
        Is a command supported by the vehicle?
        """

        return cmd in self.listCommandsSupported

    def isCmdUsable(self, cmd, bWarn=True):
        """
        Is a command usable without using force?
        """

        # Test if the command is supported...
        if not self.isCmdSupported(cmd) :
            if bWarn :
                logger.warning("Command [%s] is NOT supported!" % str(cmd))
            return False

        # Mode 6 is only implemented for the CAN protocols...
        if cmd.mode == 6 and self.interface.getProtocolID() not in ["6", "7", "8", "9"] :
            if bWarn :
                logger.warning("Mode 6 commands are ONLY supported over CAN protocols!")
            return False

        return True

    def query(self, cmd:Command, bForce=False):
        """
        Send command to the vehicle with protection against unsupported commands.
        """

        respNull = Response()
        if self.status() == ConnectionStatus.NONE :
            logger.warning("Unconnected: No connection available!")
            return respNull

        # If the user is NOT forcing the command and the command is not usable...
        if not bForce and not self.isCmdUsable(cmd, False) :
            return respNull # ...nothing to do

        self.__setHeader(cmd.bsHeader)

        logger.info("Sending command: %s" % str(cmd))
        bytesCmd = self.__buildCmdString(cmd)
        messages = self.interface.send_and_parse(bytesCmd)

        # If the command is new, note it...
        # NOTE: Check that the current command WAS NOT sent as an empty string
        #       (CR is added by the ELM327 class)
        if bytesCmd :
            self.__baLastCommand = bytesCmd

        # If the command has an unknown frame count, log it so we can specify it next time...
        if cmd not in self.__dictFrameCounts :
            self.__dictFrameCounts[cmd] = sum([len(msg.listFrames) for msg in messages])

        if not messages :
            logger.warn("No valid OBD Messages returned!")
            return respNull

        return cmd(messages)  # ...compute a response object

    def __buildCmdString(self, cmd:Command):
        """
        Assemble the appropriate command string.
        """

        bytesCmd = cmd.bsCmdID

        # If we know the number of frames that this command returns,
        # only wait for exactly that number. This avoids some harsh
        # timeouts from the ELM, thus speeding up queries.
        if self.bFast and cmd.bFast and (cmd in self.__dictFrameCounts) :
            bytesCmd += str(self.__dictFrameCounts[cmd]).encode()

        # If we sent the command last time, just send a CR...
        # NOTE: The CR is added by the ELM327 class
        if self.bFast and (bytesCmd == self.__baLastCommand) :
            bytesCmd = b""

        return bytesCmd
