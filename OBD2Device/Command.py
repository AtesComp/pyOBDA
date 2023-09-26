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
# Command.py   OBDCommand                                              #
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

from .utils import *
from .protocols import ECU, ECU_HEADER
from .protocols.protocol import Message

from .Response import Response

import logging

logger = logging.getLogger(__name__)


class Command:
    def __init__(self,
                 name,
                 desc,
                 command,
                 _bytes,
                 decoder,
                 ecu=ECU.ALL,
                 fast=False,
                 header=ECU_HEADER.ENGINE):
        self.name    = name     # ...human readable name (also used as key in commands dict)
        self.desc    = desc     # ...human readable description
        self.command = command  # ...binary Command ID string
        self.bytes   = _bytes   # ...number of bytes expected in response messages
        self.decode  = decoder  # ...decoding function to use for response messages
        self.ecu     = ecu      # ...expected ECU ID that generates response messages
        self.fast    = fast     # ...boolean indicating whether an extra "return early" end-of-command value can be added
        self.header  = header   # ...ECU Header used in requests

    def clone(self):
        return Command(self.name,
                        self.desc,
                        self.command,
                        self.bytes,
                        self.decode,
                        self.ecu,
                        self.fast,
                        self.header)

    @property
    def mode(self):
        # The Mode is contained in the first 2 command bytes
        if len(self.command) >= 2 and isHex(self.command.decode()):
            return int(self.command[:2], 16)
        else:
            return None

    @property
    def pid(self):
        # The PID, if present, is contained in the second 2 command bytes
        if len(self.command) > 2 and isHex(self.command.decode()):
            return int(self.command[2:], 16)
        else:
            return None

    def __call__(self, messages:list[Message]) -> Response:
        # Filter applicable messages from the right ECU(s)...
        messages = [m for m in messages if (self.ecu & m.ecu) > 0]

        # Guarantee data size for the decoder...
        for m in messages:
            self.__constrain_message_data(m)

        # Create the response object with the raw data received and reference to original command
        response = Response(self, messages)
        if messages:
            response.value = self.decode(messages)
        else:
            logger.info(str(self) + " did not receive any acceptable messages")

        return response

    def __constrain_message_data(self, message):
        # Sizes the data field to the command's specified size...
        len_msg_data = len(message.data)
        if self.bytes > 0:
            if len_msg_data > self.bytes:
                # Trim the right side...
                message.data = message.data[:self.bytes]
                logger.debug(
                    "Message was longer than expected (%s>%s). " +
                    "Trimmed message: %s", len_msg_data, self.bytes,
                    repr(message.data))
            elif len_msg_data < self.bytes:
                # Pad the right with zeros...
                message.data += (b'\x00' * (self.bytes - len_msg_data))
                logger.debug(
                    "Message was shorter than expected (%s<%s). " +
                    "Padded message: %s", len_msg_data, self.bytes,
                    repr(message.data))

    def __str__(self):
        if self.header != ECU_HEADER.ENGINE:
            return "%s: %s" % (self.header + self.command, self.desc)
        return "%s: %s" % (self.command, self.desc)

    def __repr__(self):
        e = self.ecu
        if self.ecu == ECU.ALL:
            e = "ECU.ALL"
        if self.ecu == ECU.ENGINE:
            e = "ECU.ENGINE"
        if self.ecu == ECU.TRANSMISSION:
            e = "ECU.TRANSMISSION"
        if self.header == ECU_HEADER.ENGINE:
            return ("OBDCommand(%s, %s, %s, %s, raw_string, ecu=%s, fast=%s)"
                    ) % (repr(self.name), repr(self.desc), repr(self.command),
                         self.bytes, e, self.fast)
        return ("OBDCommand" +
                "(%s, %s, %s, %s, raw_string, ecu=%s, fast=%s, header=%s)"
                ) % (repr(self.name), repr(self.desc), repr(self.command),
                     self.bytes, e, self.fast, repr(self.header))

    def __hash__(self):
        # needed for using commands as keys in a dict (see async.py)
        return hash(self.header + self.command)

    def __eq__(self, other):
        if isinstance(other, Command):
            return self.command == other.command and self.header == other.header
        else:
            return False
