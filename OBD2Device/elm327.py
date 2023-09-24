########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2016 Brendan Whitfield (brendan-w.com)                     #
#                                                                      #
########################################################################
#                                                                      #
# elm327.py                                                            #
#                                                                      #
# This file is part of python-OBD (a derivative of pyOBD)              #
#                                                                      #
# python-OBD is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# python-OBD is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with python-OBD.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                      #
########################################################################

import re
import serial
import time
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
    #   Selected baud (bps), 8 bit, 0 parity, None handshake
    #       9600, 8, 0, None
    #      38400, 8, 0, None
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
        "6",  # ISO_15765_4_11bit_500k
        "8",  # ISO_15765_4_11bit_250k
        "1",  # SAE_J1850_PWM
        "7",  # ISO_15765_4_29bit_500k
        "9",  # ISO_15765_4_29bit_250k
        "2",  # SAE_J1850_VPW
        "3",  # ISO_9141_2
        "4",  # ISO_14230_4_5baud
        "5",  # ISO_14230_4_fast
        "A",  # SAE_J1939
    ]

    # Bits Per Second (bps)
    #
    # NOTE: This is called "Baud Rate" in documentation, but baud refers to a generic symbol rate or
    #       modulation rate in symbols per second or pulses per second. More accurately, digital
    #       communication is specifically bits per second (bps) for components such as ELM.
    #
    # Startup bps are 38400 and 9600 unless reprogrammed via the "PP 0C" command. Additionally, the
    # communication channel must be set to 8 bits, 0 parity, None handshake.
    # Other bps 19200, 38400, 57600, 115200, 230400, 500000 are listed in the ELM327 datasheet on page 59.
    #
    # For comm rate information, see the ELM327 datasheet pages 3, 7, 10, 17, 33, 59, 63-64
    #
    # TODO: When pyserial supports non-standard baud rates on platforms other than Linux, add 500K.
    #
    # Try connecting using the two default baud rates first, then fastest to slowest since settings using a
    # slower baud rate infers a slower connection time to detect it.
    _TRY_BPS_ORDER = [
        38400, # ...Default High bps
         9600, # ...Default Low bps
       230400, 115200, 57600, 19200 # ...Other bps
    ]

    def __init__(self, portname, baudrate, protocol, timeout,
                 check_voltage=True, start_low_power=False):
        """Initializes port by resetting device and gettings supported PIDs. """

        logger.info("Initializing ELM327: PORT=%s BAUD=%s PROTOCOL=%s" %
                    (
                        portname,
                        "auto" if baudrate is None else baudrate,
                        "auto" if protocol is None else protocol,
                    ))

        self.__status = ConnectionStatus.NONE
        self.__port = None
        self.__protocol = UnknownProtocol([])
        self.__low_power = False
        self.timeout = timeout

        # ------------- open port -------------
        try:
            self.__port = serial.serial_for_url(portname,
                                                parity=serial.PARITY_NONE,
                                                stopbits=1,
                                                bytesize=8,
                                                timeout=10)  # seconds
        except serial.SerialException as e:
            self.__error(e)
            return
        except OSError as e:
            self.__error(e)
            return

        # If the IC is in the low power state, wake it up...
        if start_low_power:
            self.__port.write(b" ")
            self.__port.flush()
            time.sleep(1)

        #
        # Find the ELM's bps (baud rate)
        #
        if not self.set_baudrate(baudrate):
            self.__error("Failed to set baud rate")
            return

        #
        # Command: ATZ (Reset)
        #
        try:
            self.__send(b"AT Z", delay=1)  # ...wait 1 second for ELM to initialize
            # Ignore return data as it can be junk bits
        except serial.SerialException as e:
            self.__error(e)
            return

        #
        # Command: ATE0 (Echo OFF)
        #
        r = self.__send(b"AT E0")
        if not self.__isok(r, expectEcho=True):
            self.__error("AT E0 (Echo OFF) did not return 'OK'")
            return

        #
        # Command: ATH1 (Headers ON)
        #
        r = self.__send(b"AT H1")
        if not self.__isok(r):
            self.__error("AT H1 (Headers ON) did not return 'OK'")
            return

        #
        # Command: ATL0 (Linefeeds OFF)
        #
        r = self.__send(b"AT L0")
        if not self.__isok(r):
            self.__error("AT L0 (Linefeeds OFF) did not return 'OK'")
            return

        # Communication with the ELM at this point is successful...
        self.__status = ConnectionStatus.ELM

        #
        # Command: AT RV (ELM Volts)
        #
        if check_voltage:
            r = self.__send(b"AT RV")
            if not r or len(r) != 1 or r[0] == '':
                self.__error("AT RV (ELM Volts) did not respond")
                return
            try:
                if float(r[0].lower().replace('v', '')) < 6:
                    logger.error("OBD2 socket disconnected")
                    return
            except ValueError as e:
                self.__error("AT RV (ELM Volts) incorrect response")
                return
            # by now, we've successfuly connected to the OBD socket
            self.__status = ConnectionStatus.OBD

        #
        # Attempt communicate with the vehicle and load the correct protocol parser...
        #
        if self.set_protocol(protocol):
            self.__status = ConnectionStatus.VEHICLE
            logger.info("Adapter connected: Vehicle connected, Ignition ON, PORT=%s BAUD=%s PROTOCOL=%s" %
                        (   portname,
                            self.__port.baudrate,
                            self.__protocol.ELM_ID, ))
        else:
            if self.__status == ConnectionStatus.OBD:
                logger.error("Adapter connected: Vehicle connected, Ignition OFF")
            else:
                logger.error("Adapter connected: Vehicle connection FAILED")

    def set_protocol(self, protocol_):
        if protocol_ is not None:
            # an explicit protocol was specified
            if protocol_ not in self._SUPPORTED_PROTOCOLS:
                spKeys = list(self._SUPPORTED_PROTOCOLS)
                logger.error(
                    "{:} is not a valid protocol. ".format(protocol_) +
                    "Please use '%s' through '%s'" % ( spKeys[0], spKeys[-1])
                )
                return False
            return self.manual_protocol(protocol_)
        else:
            # Auto detect the protocol...
            return self.auto_protocol()

    def manual_protocol(self, protocol_):
        r = self.__send(b"AT TP" + protocol_.encode())
        r0100 = self.__send(b"0100")

        if not self.__has_message(r0100, "UNABLE TO CONNECT"):
            # Successfully found the protocol...
            self.__protocol = self._SUPPORTED_PROTOCOLS[protocol_](r0100)
            return True

        return False

    def auto_protocol(self):
        # Attempts communication with the vehicle
        #
        # If no protocol is specified, then protocols at tried with "AT TP".
        # On success, load the appropriate protocol parser and return True

        #
        # Command: ELM "Auto Protocol" mode
        #
        r = self.__send(b"AT SP0", delay=1)

        #
        # Command: 0100 (first command, SEARCH protocols)
        #
        r0100 = self.__send(b"0100", delay=1)
        if self.__has_message(r0100, "UNABLE TO CONNECT"):
            logger.error("Protocol Query (0100) FAILED: Unable to connect")
            return False

        #
        # Command: AT DPN (List Protocol Number) -------------------
        #
        r = self.__send(b"AT DPN")
        if len(r) != 1:
            logger.error("Failed to retrieve current protocol")
            return False

        p = r[0]  # ...get the first (and only) line returned
        # Suppress any "automatic" prefix...
        p = p[1:] if (len(p) > 1 and p.startswith("A")) else p

        # Is the protocol known?
        if p in self._SUPPORTED_PROTOCOLS:
            # ...set the corresponding protocol handler...
            self.__protocol = self._SUPPORTED_PROTOCOLS[p](r0100)
            return True
        # Otherwise, an unknown protocol...
        else:
            # This may occur as not all adapter / vehicle combinations work in "Auto Protocol" mode.
            # Some respond to the "AT DPN" command with "0"
            logger.debug("ELM responded with an unknown protocol. Trying known protocols...")

            for p in self._TRY_PROTOCOL_ORDER:
                r = self.__send(b"AT TP" + p.encode())
                r0100 = self.__send(b"0100")
                if not self.__has_message(r0100, "UNABLE TO CONNECT"):
                    # Successfully found the protocol...
                    self.__protocol = self._SUPPORTED_PROTOCOLS[p](r0100)
                    return True

        # Otherwise, no protocol found...
        logger.error("ELM Protocol not found")
        return False

    def set_baudrate(self, baud):
        if baud is None:
            # If using pseudo terminal, skip auto baud process...
            if self.port_name().startswith("/dev/pts"):
                logger.debug("Pseudo terminal detected, skipping baud rate setup")
                return True
            else:
                return self.auto_baudrate()
        else:
            self.__port.baudrate = baud
            return True

    def auto_baudrate(self):
        # Detect the baud rate for a connected ELM32x interface
        #
        # On success, return True

        # Save the "normal" value before changing...
        timeout = self.__port.timeout
        self.__port.timeout = self.timeout  # ...ELM comms, so should be fast

        for baud in self._TRY_BPS_ORDER:
            self.__port.baudrate = baud
            self.__port.flushInput()
            self.__port.flushOutput()

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

            response = self.__send(b"AT WS")
            logger.debug("Response on baud %d: %s" % (baud, repr(response)))

            # If response is the prompt character...
            if response.endswith(b">"):
                logger.debug("Selected baud %d" % baud)
                self.__port.timeout = timeout  # reinstate our original timeout
                return True

        logger.debug("Auto Baud selection FAILED")
        self.__port.timeout = timeout  # reinstate our original timeout
        return False

    def __isok(self, lines, expectEcho=False):
        if not lines:
            return False
        if expectEcho:
            # don't test for the echo itself
            # allow the adapter to already have echo disabled
            return self.__has_message(lines, 'OK')
        else:
            return len(lines) == 1 and lines[0] == 'OK'

    def __has_message(self, lines, text):
        for line in lines:
            if text in line:
                return True
        return False

    def __error(self, msg):
        # Handle fatal failures, print logger.info info and closes serial
        self.close()
        logger.error(str(msg))

    def port_name(self):
        if self.__port is not None:
            return self.__port.portstr
        else:
            return ""

    def status(self):
        return self.__status

    def ecus(self):
        return self.__protocol.ecu_map.values()

    def protocol_name(self):
        return self.__protocol.ELM_NAME

    def protocol_id(self):
        return self.__protocol.ELM_ID

    def low_power(self):
        # Enter Low Power mode
        #
        # This command causes the ELM327 to shut off all but essential services.
        #
        # The ELM327 can be woken by a message to the RS232 bus as well as a few other ways.
        # See the Power Control section in the ELM327 datasheet for details on other ways to
        # wake the chip.
        #
        # Return the status from the ELM327: 'OK' means low power mode is activated.

        if self.__status == ConnectionStatus.NONE:
            logger.info("Unconnected: Cannot enter Low Power mode")
            return None

        r = self.__send(b"AT LP", delay=1, end_marker=self.ELM_LP_ACTIVE)

        if 'OK' in r:
            logger.debug("Successfully entered Low Power mode")
            self.__low_power = True
        else:
            logger.debug("Low Power mode FAILED")

        return r

    def normal_power(self):
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

        if self.__status == ConnectionStatus.NONE:
            logger.info("Unconnected: Cannot exit low power")
            return None

        lines = self.__port.write(b" ")
        self.__port.flush()

        # Assume we woke up
        logger.debug("Successfully exited low power mode")
        self.__low_power = False

        return lines

    def close(self):
        # Resets the device and sets all attributes to unconnected states.

        self.__status = ConnectionStatus.NONE
        self.__protocol = None

        if self.__port is not None:
            logger.info("Closing port...")
            self.__write(b"AT Z")
            self.__port.close()
            self.__port = None

    def send_and_parse(self, cmd):
        # The send() function is used to service all Commands
        #
        # Sends the given command string and parses the response lines with
        # the protocol object.
        #
        # An empty command string will re-trigger the previous command
        #
        # Return a list of Message objects

        if self.__status == ConnectionStatus.NONE:
            logger.info("cannot send_and_parse() when unconnected")
            return None

        # Check if we are in Low Power mode...
        if self.__low_power == True:
            self.normal_power()

        lines = self.__send(cmd)
        messages = self.__protocol(lines)
        return messages

    def __send(self, cmd, delay=None, end_marker=ELM_PROMPT):
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

        r = self.__read(end_marker=end_marker)
        while delayed < 1.0 and len(r) <= 0:
            d = 0.1
            logger.debug("No response...wait: %f seconds" % d)
            time.sleep(d)
            delayed += d
            r = self.__read(end_marker=end_marker)
        return r

    def __write(self, cmd):
        # A "low-level" function to write a string to the port

        if self.__port:
            cmd += b"\r"  # terminate with carriage return in accordance with ELM327 and STN11XX specifications
            logger.debug("write: " + repr(cmd))
            try:
                self.__port.flushInput()  # dump everything in the input buffer
                self.__port.write(cmd)  # turn the string into bytes and write
                self.__port.flush()  # wait for the output buffer to finish transmitting
            except Exception:
                self.__status = ConnectionStatus.NONE
                self.__port.close()
                self.__port = None
                logger.critical("Device disconnected while writing")
                return
        else:
            logger.info("Unconnected: Cannot perform __write()")

    def __read(self, end_marker=ELM_PROMPT):
        # A "low-level" read function
        #
        # Accumulate characters until the end marker (by default, the prompt) is seen.
        #
        # Return a list of [/r/n] delimited strings

        if not self.__port:
            logger.info("cannot perform __read() when unconnected")
            return []

        buffer = bytearray()

        while True:
            # Retrieve as much data as possible...
            try:
                data = self.__port.read(self.__port.in_waiting or 1)
            except Exception:
                self.__status = ConnectionStatus.NONE
                self.__port.close()
                self.__port = None
                logger.critical("Device disconnected while reading")
                return []

            # If nothing was received...
            if not data:
                logger.warning("Failed to read port")
                break

            buffer.extend(data)

            # End on the specified end-marker sequence...
            if end_marker in buffer:
                break

        # Log--remove the "bytearray(   ...   )" part
        logger.debug("read: " + repr(buffer)[10:-1])

        # Clean out any null characters...
        buffer = re.sub(b"\x00", b"", buffer)

        # Remove the prompt character
        if buffer.endswith(self.ELM_PROMPT):
            buffer = buffer[:-1]

        # Convert bytes into a standard string...
        string = buffer.decode("utf-8", "ignore")

        # Splits string into lines while removing empty lines and trailing spaces...
        lines = [s.strip() for s in re.split("[\r\n]", string) if bool(s)]

        return lines
