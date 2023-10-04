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
        # The Mode is contained in the 1st two command bytes...
        if len(self.bsCmdID) >= 2 and isHex( self.bsCmdID.decode() ):
            return int(self.bsCmdID[:2], 16)
        else:
            return None

    @property
    def pid(self):
        # The PID, if present, is contained in the 2nd two command bytes...
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
        # Hash command as key for a dict...
        return hash(self.bsHeader + self.bsCmdID)

    def __eq__(self, other):
        if isinstance(other, Command):
            return self.bsCmdID == other.bsCmdID and self.bsHeader == other.bsHeader
        else:
            return False
