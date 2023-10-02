############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Legacy.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file
#   "obd/protocols/protocol_legacy.py"
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
from binascii import unhexlify

from .Protocol import Protocol
from .Frame import Frame
from .Message import Message

logger = logging.getLogger(__name__)


#
# Class LegacyProtocol
#
# This class is a subclass of the Protocol class.
# This class is a base class for other legacy protocol implementations.
# NOTE: See the subclasses at the end of this file.
#
# Protocol objects are factories for Frame and Message objects.
# They are largely stateless, with the exception of an ECU tagging
# system that is initialized by passing the response to an "0100"
#  command.
#
# Protocols are called ( __call__ ) with a list of response strings
# and return a list of Messages.

class LegacyProtocol(Protocol):
    TX_ID_ENGINE = 0x10

    def __init__(self, listRespLines : list[str]):
        Protocol.__init__(self, listRespLines)

    def parseFrameData(self, frame : Frame):
        strRaw = frame.strRaw

        # If Frame has odd size...
        if len(strRaw) & 1:
            logger.debug("Protocol: Frame has odd length. Dropping...")
            return False

        baRaw = bytearray( unhexlify(strRaw) )

        # If Frame is too short...
        if len(baRaw) < 6:
            logger.debug("Protocol: Frame is too short. Dropping...")
            return False

        # If Frame is too long...
        if len(baRaw) > 11:
            logger.debug("Protocol: Frame is too long. Dropping...")
            return False

        # Ex.
        # [Header] [     Frame     ]
        # 48 6B 10 41 00 BE 7F B8 13 ck
        # ck = checksum byte

        # Exclude header and trailing checksum (handled by ELM adapter)
        frame.baData = baRaw[3:-1]

        # read header information
        frame.iPriority = baRaw[0]
        frame.iRxID = baRaw[1]
        frame.iTxID = baRaw[2]

        return True

    def parseMessage(self, message : Message):
        frames = message.listFrames

        # The frame count will always be >= 1 (see the caller, protocol.py)
        iMode = frames[0].baData[0]

        # Are the frame responses for the same Mode (SID)?
        if len(frames) > 1:
            if not all( [ iMode == frame.data[0] for frame in frames[1:] ] ):
                logger.debug("Protocol: Frames from multiple commands. Dropping...")
                return False

        # Legacy protocols have individual re-assembly procedures for each Mode

        # NOTE: THERE ARE HACKS HERE to align output to be compatible with CAN
        #       since CAN is the standard. As this is legacy, fix inconsistencies
        #       for the legacy protocol here.

        # If a GET_DTC request...
        if iMode == 0x43:
            # GET_DTC requests return frames with no PID or Order bytes
            # Accumulate all of the data, minus the Mode bytes, in each frame

            # Example:
            # Insert faux-byte to mimic the CAN style DTC requests
            #            |
            #          [ v     Frame      ]
            # 48 6B 10 43 03 00 03 02 03 03 ck
            # 48 6B 10 43 03 04 00 00 00 00 ck
            #             [  Data - Mode  ]

            message.baData = bytearray([iMode, 0x00])  # ...add Mode and CAN DTC Count bytes
            for frame in frames:
                message.baData += frame.baData[1:] # ...skip the Mode and append each frame's data

        else: # ...any other Mode
            if len(frames) == 1:
                # Set data excluding the Mode and PID bytes

                # Example:
                #          [     Frame     ]
                # 48 6B 10 41 00 BE 7F B8 13 ck
                #          [      Data     ]

                message.baData = frames[0].baData

            else: # len(frames) > 1:
                # Generic multiline requests have an Order byte

                # Example:
                #          [      Frame       ]
                # 48 6B 10 49 02 01 00 00 00 31 ck
                # 48 6B 10 49 02 02 44 34 47 50 ck
                # 48 6B 10 49 02 03 30 30 52 35 ck
                # etc...         ^^ [  Data   ]
                # transforms to:
                # [               Frame                   ]
                # 49 02 00 00 00 31 44 34 47 50 30 30 52 35
                #      ^[  Data   ] [  Data   ] [  Data   ]
                #      |
                #    Order byte removed

                # Sort the frames by the Order byte...
                frames = sorted( frames, key = lambda frame: frame.baData[2] )

                # Is the data contiguous?
                listIndices : list[int] = [ frame.data[2] for frame in frames ]
                if not self.isContiguousInts(listIndices, 1, len(frames)):
                    logger.debug("Protocol: MultiFrame has missing frames. Dropping...")
                    return False

                #
                # Accumulate ordered data from each frame...
                #
                frames[0].baData.pop(2)  # ...remove the Order byte from the First Frame
                message.baData = frames[0].baData # ...preserve the First Frame's Mode and PID bytes

                # Add the data from the remaining frames...
                for frame in frames[1:]:
                    message.baData += frame.baData[3:]  # ...skip the Mode PID and Order bytes

        return True


# ==================================================
#
# Legacy Protocol SubClasses
#
# ==================================================


class SAE_J1850_PWM(LegacyProtocol):
    ELM_NAME = "SAE J1850 PWM"
    ELM_ID = "1"


class SAE_J1850_VPW(LegacyProtocol):
    ELM_NAME = "SAE J1850 VPW"
    ELM_ID = "2"


class ISO_9141_2(LegacyProtocol):
    ELM_NAME = "ISO 9141-2"
    ELM_ID = "3"


class ISO_14230_4_5baud(LegacyProtocol):
    ELM_NAME = "ISO 14230-4 (KWP 5BAUD)"
    ELM_ID = "4"


class ISO_14230_4_fast(LegacyProtocol):
    ELM_NAME = "ISO 14230-4 (KWP FAST)"
    ELM_ID = "5"
