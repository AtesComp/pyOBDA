############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Command.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file "obd/OBDCommand.py"
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


from typing import Callable

from .Protocols.ECU import ECU
from .Protocols.Message import Message
from .Response import Response
from .utils import *

import logging

logger = logging.getLogger(__name__)


class Command:
    def __init__(self,
                 strName : str,
                 strDesc : str,
                 bsCmdID : bytes,
                 iBytes : int,
                 funcDecoder : Callable,
                 iECU : int = ECU.ALL,
                 bFast : bool = False,
                 bsHeader : bytes = ECU.HEADER.ENGINE
    ):
        self.strName     = strName     # ...human readable name (also used as key in commands dict)
        self.strDesc     = strDesc     # ...human readable description
        self.bsCmdID     = bsCmdID     # ...bytes Command ID string
        self.iBytes      = iBytes      # ...byte count expected in response messages
        self.funcDecoder = funcDecoder # ...decoding function to use for response messages
        self.iECU        = iECU        # ...expected ECU ID that generates response messages
        self.bFast       = bFast       # ...boolean indicating if an extra "return early" end-of-command value can be added
        self.bsHeader    = bsHeader    # ...bytes ECU Header used in requests

    def clone(self):
        return Command(self.strName,
                        self.strDesc,
                        self.bsCmdID,
                        self.iBytes,
                        self.funcDecoder,
                        self.iECU,
                        self.bFast,
                        self.bsHeader)

    @property
    def mode(self):
        """
        The mode method retrieves the mode contained in the 1st two command bytes.
        """

        if len(self.bsCmdID) >= 2 and isHex( self.bsCmdID.decode() ):
            return int(self.bsCmdID[:2], 16)
        else:
            return None

    @property
    def pid(self):
        """
        The pid method retrieves the PID, if present, contained in the 2nd two command bytes.
        """

        if len(self.bsCmdID) > 2 and isHex( self.bsCmdID.decode() ):
            return int(self.bsCmdID[2:], 16)
        else:
            return None

    def __call__(self, messages:list[Message]) -> Response:
        # Filter applicable messages from the right ECU(s)...
        messages = [ message for message in messages if (self.iECU & message.iECU) > 0 ]

        # Guarantee data size for the decoder...
        for message in messages:
            self.__constrainMessageData(message)

        # Create the response object with the raw data received and reference to original command
        response = Response(self, messages)
        if messages:
            response.value = self.funcDecoder(messages)
        else:
            logger.info(str(self) + " did not receive any acceptable messages")

        return response

    def __constrainMessageData(self, message:Message):
        # Sizes the data field to the command's specified size...
        iMsgDataLen = len(message.baData)
        if self.iBytes > 0:
            if iMsgDataLen > self.iBytes:
                # Trim the right side...
                message.baData = message.baData[:self.iBytes]
                logger.debug(
                    "Message was longer than expected (%s>%s). " +
                    "Trimmed message: %s", iMsgDataLen, self.iBytes,
                    repr(message.baData))
            elif iMsgDataLen < self.iBytes:
                # Pad the right with zeros...
                message.baData += (b'\x00' * (self.iBytes - iMsgDataLen))
                logger.debug(
                    "Message was shorter than expected (%s<%s). " +
                    "Padded message: %s", iMsgDataLen, self.iBytes,
                    repr(message.baData))

    def __str__(self):
        if self.bsHeader != ECU.HEADER.ENGINE:
            return "%s: %s" % (self.bsHeader + self.bsCmdID, self.strDesc)
        return "%s: %s" % (self.bsCmdID, self.strDesc)

    def __repr__(self):
        strECU = "ECU.UNKNOWN"
        if self.iECU == ECU.ALL:
            strECU = "ECU.ALL"
        elif self.iECU == ECU.ENGINE:
            strECU = "ECU.ENGINE"
        elif self.iECU == ECU.TRANSMISSION:
            strECU = "ECU.TRANSMISSION"

        if self.bsHeader == ECU.HEADER.ENGINE:
            return ("Command(%s, %s, %s, %d, raw_string, ecu=%s, fast=%s)"
                    ) % (repr(self.strName), repr(self.strDesc), repr(self.bsCmdID),
                         self.iBytes, strECU, self.bFast)
        return ("Command" +
                "(%s, %s, %s, %d, raw_string, ecu=%s, fast=%s, header=%s)"
                ) % (repr(self.strName), repr(self.strDesc), repr(self.bsCmdID),
                     self.iBytes, strECU, self.bFast, repr(self.bsHeader))

    def __hash__(self):
        """
        Hash the command as a key for a dict.
        """

        return hash(self.bsHeader + self.bsCmdID)

    def __eq__(self, other):
        if isinstance(other, Command):
            return self.bsCmdID == other.bsCmdID and self.bsHeader == other.bsHeader
        else:
            return False
