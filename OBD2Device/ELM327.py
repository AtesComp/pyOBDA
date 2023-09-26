############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# ELM327.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file "obd/elm327.py"
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


import re
import serial
import time
#import unicodedata
import logging
from .protocols import *

from .ConnectionStatus import ConnectionStatus

logger = logging.getLogger(__name__)


class ELM327:
    # Handles communication with the ELM327 adapter.
    #
    # See the ELM327 datasheet in the docs directory.
    #
    # Instantiate with a port (/dev/ttyUSB0, etc...) using:
    #   Selected baud (bps), 8 bit, No parity, 1 stop bit
    #       9600, 8, None, 1
    #      38400, 8, None, 1
    #
    # After instantiation with a port (/dev/ttyUSB0, etc...), the following functions become available:
    #   send_and_parse()
    #   close()
    #   status()
    #   port_name()
    #   protocol_name()
    #   ecus()

    # ELM Chevron (prompt)
    ELM_PROMPT = b'>'

    # ELM Low Power state 'OK' indicated
    ELM_LP_ACTIVE = b'OK'

    _SUPPORTED_PROTOCOLS = {
        # "0" : None = Automatic Mode
        #   NOTE: This isn't an actual protocol. If the ELM reports this, then we don't have enough information.
        #         See auto_protocol()
        "1": SAE_J1850_PWM,
        "2": SAE_J1850_VPW,
        "3": ISO_9141_2,
        "4": ISO_14230_4_5baud,
        "5": ISO_14230_4_fast,
        "6": ISO_15765_4_11bit_500k,
        "7": ISO_15765_4_29bit_500k,
        "8": ISO_15765_4_11bit_250k,
        "9": ISO_15765_4_29bit_250k,
        "A": SAE_J1939,
        # "B" : None, # user defined 1
        # "C" : None, # user defined 2
    }

    # Order of fallback protocols to try when command "ATSP0" doesn't produce the expected protocol...
    _TRY_PROTOCOL_ORDER = [
        "6",  # ISO_15765_4_11bit_500k  CAN
        "8",  # ISO_15765_4_11bit_250k  CAN
        "1",  # SAE_J1850_PWM           Legacy
        "7",  # ISO_15765_4_29bit_500k  CAN
        "9",  # ISO_15765_4_29bit_250k  CAN
        "2",  # SAE_J1850_VPW           Legacy
        "3",  # ISO_9141_2              Legacy
        "4",  # ISO_14230_4_5baud       Legacy
        "5",  # ISO_14230_4_fast        Legacy
        "A",  # SAE_J1939               CAN
    ]

    # Bits Per Second (bps)
    #
    # NOTE: This is called "Baud Rate" in documentation, but baud refers to a generic symbol rate or
    #       modulation rate in symbols per second or pulses per second. More accurately, digital
    #       communication is specifically bits per second (bps) for components such as ELM.
    #
    # Startup bps are 38400 and 9600 unless reprogrammed via the "PP 0C" command. Additionally, the
    # communication channel must be set to 8 bit, No parity, 1 stop bit.
    # Other bps 19200, 38400, 57600, 115200, 230400, 500000 are listed in the ELM327 datasheet on page 59.
    #
    # For comm rate information, see the ELM327 datasheet pages 3, 7, 10, 17, 33, 59, 63-64
    #
    # TODO: When pyserial supports non-standard baud rates on platforms other than Linux, add 500K.
    #
    # Try connecting using the two default baud rates first, then fastest to slowest since settings using a
    # slower baud rate infers a slower connection time to detect it.
    _TRY_BPS_ORDER = [
        38400, # ...default High bps
         9600, # ...default Low bps
       230400, 115200, 57600, 19200 # ...other bps
    ]

    # Bad CAN Maessages
    _BAD_CAN_MSGS = [
        "UNABLE TO CONNECT",
        "CAN ERROR",
    ]

    def __init__(self, strPortName:str, iBaudRate:int, strProtocol:str, fTimeout:float,
                 bCheckVoltage=True, bStartLowPower=False):
        # Initializes port by resetting device and gettings supported PIDs

        if strProtocol == "" or strProtocol == None:
            strProtocol = "Auto"
        logger.info(
            "Initializing ELM327: PORT=%s BAUD=%s PROTOCOL=%s" %
            (   strPortName,
                "Auto" if iBaudRate == 0 else str(iBaudRate),
                strProtocol,
            )
        )

        self.__strStatus = ConnectionStatus.NONE
        self.__objPort = None
        self.__objProtocol = UnknownProtocol([])
        self.__bLowPower = bStartLowPower
        self.__fTimeout = fTimeout

        #
        # Open Port
        #
        try:
            self.__objPort = \
                serial.serial_for_url(
                    strPortName,
                    bytesize = 8,
                    parity = serial.PARITY_NONE,
                    stopbits = 1,
                    timeout = fTimeout # in seconds
                )
        except serial.SerialException as err:
            self.__error(err)
            return
        except OSError as err:
            self.__error(err)
            return

        # If the IC is in the Low Power state, wake it up...
        if bStartLowPower:
            self.__objPort.write(b" ")
            self.__objPort.flush()
            time.sleep(1)
            self.__bLowPower = False

        #
        # Find the ELM's bps (baud rate)
        #
        if not self.setBaudRate(iBaudRate):
            self.__error("Set Baud Rate FAILED!")
            return

        #
        # Command: ATZ (Reset)
        #
        try:
            r = self.__send(b"AT Z", delay=1)  # ...wait 1 second for ELM to initialize
            if len(r) > 1:
                logger.debug("Response: " + r[1] )

            # Ignore return data as it can be junk bits
        except serial.SerialException as err:
            self.__error(err)
            return

        #
        # Command: AT E0 (Echo OFF)
        #
        r = self.__send(b"AT E0")
        if not self.__isOK(r, expectEcho=True):
            self.__error("AT E0 (Echo OFF) did not return 'OK'!")
            return
        logger.debug("Response: " + r[0] )

        #
        # Command: AT H1 (Headers ON)
        #
        r = self.__send(b"AT H1")
        if not self.__isOK(r):
            self.__error("AT H1 (Headers ON) did not return 'OK'!")
            return
        logger.debug("Response: " + r[0] )

        #
        # Command: AT L0 (Linefeeds OFF)
        #
        r = self.__send(b"AT L0")
        if not self.__isOK(r):
            self.__error("AT L0 (Linefeeds OFF) did not return 'OK'!")
            return
        logger.debug("Response: " + r[0] )

        #
        # Command: AT @1 (Device Description)
        #
        r = self.__send(b"AT @1")
        if len(r) == 0 or r[0] == '':
            self.__error("AT @1 (Device Description) did not respond!")
            return
        logger.debug("Response: " + r[0] )

        #
        # Command: AT @2 (Device Identified)
        #
        r = self.__send(b"AT @2")
        if len(r) == 0 or r[0] == '':
            self.__error("AT @1 (Device Identified) did not respond!")
            return
        logger.debug("Response: " + r[0] )

        # Communication with the ELM at this point is successful...
        self.__strStatus = ConnectionStatus.ELM

        #
        # Command: AT RV (ELM Volts)
        #
        if bCheckVoltage:
            r = self.__send(b"AT RV")
            if len(r) == 0 or r[0] == '':
                self.__error("AT RV (ELM Volts) did not respond!")
                return
            try:
                if float(r[0].lower().replace('v', '')) < 6.0:
                    self.__error("AT RV (ELM Volts) too low ( < 6.0 )!")
                    return
            except ValueError as err:
                self.__error("AT RV (ELM Volts) value error!")
                return
            # by now, we've successfuly connected to the OBD socket
            self.__strStatus = ConnectionStatus.OBD

        #
        # Attempt communicate with the vehicle and load the correct protocol parser...
        #
        if self.setProtocol(strProtocol):
            self.__strStatus = ConnectionStatus.VEHICLE
            logger.info(
                "Adapter connected: Vehicle connected, Ignition ON, PORT=%s BAUD=%s PROTOCOL=%s" %
                (   strPortName,
                    self.__objPort.baudrate,
                    self.__objProtocol.ELM_ID,
                )
            )
            return

        # Otherwise, protocol failed...
        if self.__strStatus == ConnectionStatus.OBD:
            logger.error("Adapter connected: Vehicle connected, Ignition OFF!")
        else:
            logger.error("Adapter connected: Vehicle connection FAILED!")

    def setProtocol(self, strProtocol:str):
        # If an explicit protocol was specified...
        if not (strProtocol == "Auto" or strProtocol == "" or strProtocol == None):
            if strProtocol not in self._SUPPORTED_PROTOCOLS:
                spKeys = list(self._SUPPORTED_PROTOCOLS)
                self.__error(
                    "Protocol {:} is not valid! ".format(strProtocol) +
                    "Please use '%s' through '%s'" % ( spKeys[0], spKeys[-1])
                )
                return False
            return self.setSelectedProtocol(strProtocol)
        else:
            # Auto detect the protocol...
            return self.findProtocol()

    def setSelectedProtocol(self, strProtocol:str):
        r = self.__send(b"AT TP" + strProtocol.encode())
        if not self.__isOK(r):
            self.__error("AT TP (Try Protocol) did not return 'OK'!")
            return False

        r0100 = self.__send(b"0100", delay=1)
        if self.__hasMessage(r0100, ELM327._BAD_CAN_MSGS):
            logger.error("1: Protocol Query (0100) FAILED: Unable to connect!")
            # Try again...
            r0100 = self.__send(b"0100", delay=1)
            if self.__hasMessage(r0100, ELM327._BAD_CAN_MSGS):
                logger.error("2: Protocol Query (0100) FAILED: Unable to connect!")
                self.__error("Set Selected Protocol FAILED! Use OBD-II->Configure to selected another or set to Auto Select.")
                return False

        # Successfully found the protocol...
        self.__objProtocol = self._SUPPORTED_PROTOCOLS[strProtocol](r0100)
        return True

    def findProtocol(self):
        # Attempts communication with the vehicle
        #
        # If no protocol is specified, then protocols are tried with "AT TP".
        # On success, load the appropriate protocol parser and return True

        #
        # Command: ELM "Auto Protocol" mode
        #
        r = self.__send(b"AT SP0", delay=1)
        if not self.__isOK(r):
            self.__error("AT SP0 (Set Protocol Auto) did not return 'OK'!")
            return False

        #
        # Command: 0100 (first command, SEARCH protocols)
        #
        r0100 = self.__send(b"0100", delay=1)
        if self.__hasMessage(r0100, ELM327._BAD_CAN_MSGS):
            logger.error("1: Protocol Query (0100) FAILED: Unable to connect!")
            # Try again...
            r0100 = self.__send(b"0100", delay=1)
            if self.__hasMessage(r0100, ELM327._BAD_CAN_MSGS):
                logger.error("2: Protocol Query (0100) FAILED: Unable to connect!")
                return False

        #
        # Command: AT DPN (List Protocol Number) -------------------
        #
        r = self.__send(b"AT DPN")
        if len(r) == 0:
            logger.error("AT DPN (Describe Protocol) did not retrieve protocol!")
            return False

        strProtoNo = r[0]  # ...get the first line returned
        # Suppress the "automatic" prefix...
        strProtoNo = strProtoNo[1:] if (len(strProtoNo) > 1 and strProtoNo[0] == "A") else strProtoNo

        # Is the protocol known?
        if strProtoNo in self._SUPPORTED_PROTOCOLS:
            # ...set the corresponding protocol handler...
            self.__objProtocol = self._SUPPORTED_PROTOCOLS[strProtoNo](r0100)
            return True
        # Otherwise, an unknown protocol...
        else:
            # This may occur as not all adapter / vehicle combinations work in "Auto Protocol" mode.
            # Some respond to the "AT DPN" command with "0"
            logger.debug("ELM responded with an unknown protocol. Trying known protocols...")

            for strProtoNo in self._TRY_PROTOCOL_ORDER:
                logger.debug("Trying: " + strProtoNo + "...")

                r = self.__send(b"AT TP" + strProtoNo.encode())
                r0100 = self.__send(b"0100", delay=1)
                if self.__hasMessage(r0100, ELM327._BAD_CAN_MSGS):
                    # Try again...
                    r0100 = self.__send(b"0100", delay=1)
                    if self.__hasMessage(r0100, ELM327._BAD_CAN_MSGS):
                        continue

                # Otherwise, successfully found the protocol...
                self.__objProtocol = self._SUPPORTED_PROTOCOLS[strProtoNo](r0100)
                logger.debug("Protocol " + strProtoNo + " succeeded.")
                return True

        # Otherwise, no protocol found...
        logger.error("ELM Protocol not found!")
        return False

    def setBaudRate(self, iBaud:int):
        if iBaud == 0 or iBaud == None:
            # If using pseudo terminal, skip auto baud process...
            if self.getPortName().startswith("/dev/pts"):
                logger.debug("Pseudo terminal detected, skipping baud rate setup")
                return True
            else:
                return self.findBaudRate()
        else:
            self.__objPort.baudrate = iBaud
            return True

    def findBaudRate(self):
        # Detect the baud rate for a connected ELM32x interface
        #
        # On success, return True

        # For Baud testing, set ELM comms to a relatively fast timeout...
        self.__objPort.timeout = 0.5

        for baud in self._TRY_BPS_ORDER:
            logger.debug("Testing baud %d" % baud)
            self.__objPort.baudrate = baud
            self.__objPort.flushInput()
            self.__objPort.flushOutput()

            # Send an "AT WS" command to get a prompt back from the scanner
            # (an empty command runs the risk of repeating a dangerous command)

            ## The first character might get eaten if the interface was busy,
            ## so write a second one (again so that the lone CR doesn't repeat
            ## the previous command)
            #
            ## All commands should be terminated with carriage return according
            ## to ELM327 and STN11XX specifications
            ##self.__port.write(b"\x7F\x7F\r")
            ##self.__port.flush()
            ##response = self.__port.read(1024)

            iTest = 2
            while iTest > 0:
                response = self.__send(b"AT WS")
                logger.debug( "Response on baud %d: %s" % ( baud, repr(response) ) )

                # If response is the prompt character...
                if response and len(response) > 0:
                    if response[-1].endswith(">"):
                        logger.debug("Selected baud %d" % baud)
                        self.__objPort.timeout = self.__fTimeout # ...reinstate user timeout
                        return True
                    # Otherwise, got something, so try again...
                    iTest -= 1
                    continue
                # Otherwise, no response...
                break
            # ...next baud...

        # Otherwise, no baud found...
        logger.warn("Auto Baud selection FAILED!")
        self.__objPort.timeout = self.__fTimeout # ...reinstate user timeout
        return False

    def __isOK(self, lines, expectEcho=False):
        if not lines:
            return False
        if expectEcho:
            # Allow the adapter to already have echo disabled by searching all lines...
            # NOTE: No need to test for the echo.
            return self.__hasMessage(lines, ["OK"])
        else: # ...no echo, just search the first line for OK...
            return len(lines) > 0 and lines[0] == "OK"

    def __hasMessage(self, lines, msgs:list[str]):
        for line in lines:
            for msg in msgs:
                if msg in line:
                    return True
        return False

    def __error(self, msg):
        # Handle fatal failures, print logger.error message, and closes serial...
        logger.error( str(msg) )
        self.close()

    def getPortName(self):
        if self.__objPort is not None:
            return self.__objPort.portstr
        else:
            return ""

    def getStatus(self):
        return self.__strStatus

    def getECUSValues(self):
        return self.__objProtocol.ecu_map.values()

    def getProtocolName(self):
        return self.__objProtocol.ELM_NAME

    def getProtocolID(self):
        return self.__objProtocol.ELM_ID

    def setToLowPower(self):
        # Enter Low Power mode
        #
        # This command causes the ELM327 to shut off all but essential services.
        #
        # The ELM327 can be woken by a message to the RS232 bus as well as a few other ways.
        # See the Power Control section in the ELM327 datasheet for details on other ways to
        # wake the chip.
        #
        # Return the status from the ELM327: 'OK' means low power mode is activated.

        if self.__strStatus == ConnectionStatus.NONE:
            logger.info("Unconnected: Cannot enter Low Power mode")
            return None

        r = self.__send(b"AT LP", delay=1, bytesEndMarker=self.ELM_LP_ACTIVE)

        if 'OK' in r:
            logger.debug("Successfully entered Low Power mode")
            self.__bLowPower = True
        else:
            logger.debug("Low Power mode FAILED")

        return r

    def setToNormalPower(self):
        # Exit Low Power mode
        #
        # Send a space to trigger the RS232 to wakeup.
        #
        # This will send a space even when not in Low Power mode to ensure Low
        # Power mode can be changed.
        #
        # See the Power Control section in the ELM327 datasheet for details on other
        # ways to wake the chip.
        #
        # Return the status from the ELM327.

        if self.__strStatus == ConnectionStatus.NONE:
            logger.info("Unconnected: Cannot exit low power")
            return None

        lines = self.__objPort.write(b" ")
        self.__objPort.flush()

        # Assume we woke up
        logger.debug("Successfully exited low power mode")
        self.__bLowPower = False

        return lines

    def close(self):
        # Resets the device and sets all attributes to unconnected states.

        self.__strStatus = ConnectionStatus.NONE
        self.__objProtocol = None

        if self.__objPort is not None:
            logger.info("Closing port...")
            self.__write(b"AT Z")
            self.__read()
            self.__objPort.close()
            self.__objPort = None

    def send_and_parse(self, cmd):
        # The send() function is used to service all Commands
        #
        # Sends the given command string and parses the response lines with
        # the protocol object.
        #
        # An empty command string will re-trigger the previous command
        #
        # Return a list of Message objects

        if self.__strStatus == ConnectionStatus.NONE:
            logger.info("Unconnected: Cannot send and parse!")
            return None

        # Check if we are in Low Power mode...
        if self.__bLowPower == True:
            self.setToNormalPower()

        lines = self.__send(cmd)
        # If the prompt ends the last line, remove it...
        if len(lines) > 0 and lines[-1].endswith( self.ELM_PROMPT.decode("ascii", "ignore") ):
            lines[-1] = lines[-1][:-1]
        # If the last line is now empty, remove it...
        if len(lines[-1]) == 0:
            lines = lines[:-1]

        messages = self.__objProtocol(lines)
        return messages

    def __send(self, cmd, delay = None, bytesEndMarker:bytes = ELM_PROMPT):
        # An unprotected send() function
        #
        # This will __write() the given string, no questions asked.
        #
        # Return result of __read() (a list of line strings) after an optional
        # delay until the end marker (by default, the prompt) is seen.

        self.__write(cmd)

        delayed = 0.0
        if delay is not None:
            logger.debug("Wait: %d seconds" % delay)
            time.sleep(delay)
            delayed += delay

        r = self.__read(bytesEndMarker=bytesEndMarker)
        while delayed < 1.0 and len(r) <= 0:
            d = 0.1
            logger.debug("No response...wait: %f seconds" % d)
            time.sleep(d)
            delayed += 1.0 # d
            r = self.__read(bytesEndMarker=bytesEndMarker)
        return r

    def __write(self, cmd):
        # A "low-level" function to write a string to the port

        if self.__objPort:
            cmd += b"\r"  # terminate with carriage return in accordance with ELM327 and STN11XX specifications
            logger.debug("write: " + repr(cmd))
            try:
                self.__objPort.flushInput()  # dump everything in the input buffer
                self.__objPort.write(cmd)  # turn the string into bytes and write
                self.__objPort.flush()  # wait for the output buffer to finish transmitting
            except Exception:
                self.__strStatus = ConnectionStatus.NONE
                self.__objPort.close()
                self.__objPort = None
                logger.critical("Device disconnected while writing")
                return
        else:
            logger.info("Unconnected: Cannot write!")

    def __read(self, bytesEndMarker:bytes = ELM_PROMPT):
        # A "low-level" read function
        #
        # Accumulate characters until the end marker (by default, the prompt) is seen.
        #
        # Return a list of [/r/n] delimited strings

        if not self.__objPort:
            logger.info("Unconnected: Cannot read!")
            return []

        baBuffer = bytearray()

        #
        # Read all the ELM's response data...
        #
        # NOTE: Normally, ELM will respond with a prompt ('>') character.
        #
        #       When an incomplete string is sent and no carriage return appears, ELM will abort the command.
        #       In this case, an internal timer will automatically abort the incomplete message after about 20
        #       seconds and the ELM327 will print a single question mark (‘?’) to show that the input was not
        #       understood (and was not acted upon). Messages that are not understood by the ELM327 (syntax
        #       errors) will always be signalled by a single question mark. These include incomplete messages,
        #       incorrect AT commands, or invalid hexadecimal digit strings, but are not an indication of
        #       whether or not the message was understood by the vehicle.
        while True:
            # Retrieve as much data as possible...
            try:
                data = self.__objPort.read(self.__objPort.in_waiting or 1)
            except Exception:
                self.__strStatus = ConnectionStatus.NONE
                self.__objPort.close()
                self.__objPort = None
                logger.critical("Port Read: Device disconnected while reading!")
                return []

            # If nothing was received...
            if not data:
                if len(baBuffer) == 0:
                    logger.warning("Port Read: FAILED!")
                else:
                    logger.warning("Port Read: Abnormal end!")
                break

            baBuffer.extend(data)
            logger.info( "Port Read: Found bytes: " + str( len(baBuffer) ) )

            # End on the specified End Marker sequence...
            if bytesEndMarker in baBuffer:
                break

        # Check buffer...
        if len(baBuffer) == 0:
            return []

        # Log...
        strLogC = ""
        strLogV = ""
        for iIndex in range( len(baBuffer) ):
            ch = baBuffer[iIndex]
            strLogC += ( chr(ch) if (ch > 31 and ch != 127) else '_' )
            strLogV += hex(ch)[2:].upper() + ' '
        logger.debug("Buffer Contents: " + strLogC)
        logger.debug("            Hex: " + strLogV)

        # Remove nulls...
        baBuffer = re.sub(b"\x00", b"", baBuffer)

        ## If the prompt ends the buffer, remove it...
        #if buffer.endswith(self.ELM_PROMPT):
        #    buffer = buffer[:-1]

        # Convert the bytearray into a string...
        strBuffer = baBuffer.decode("ascii", "ignore")

        # Split the string into lines--remove blank lines and trailing spaces...
        astrLines = [ strLine.strip() for strLine in re.split("[\r\n]", strBuffer) if bool(strLine) ]

        return astrLines
