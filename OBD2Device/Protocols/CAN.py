############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# CAN.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file
#   "obd/protocols/protocol_can.py"
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
# CLASS: Controller Area Network Protocol
#
class CANProtocol(Protocol):
    TX_ID_ENGINE = 0
    TX_ID_TRANSMISSION = 1

    FRAME_TYPE_SF = 0x00 # ...single frame
    FRAME_TYPE_FF = 0x10 # ...first frame of multi-frame message
    FRAME_TYPE_CF = 0x20 # ...consecutive frame(s) of multi-frame message

    def __init__(self, listRespLines : list[str], iBitesID : int):
        # Set the ID Bits FIRST since the base class Protocol __init__()
        #   uses the parsing system...
        self.iBitsID = iBitesID

        Protocol.__init__(self, listRespLines)

    def parseFrameData(self, frame: Frame):
        strRaw = frame.strRaw

        # ELM CAN headers are 11 bit and 29 bits
        #    Pad the headers to 32 bits
        # NOTE: 29 bits must use 4 bytes, 8 nibbles by default:
        #           ---x xxxx xxxx xxxx xxxx xxxx xxxx xxxx
        #       11 bits must use 1.5 bytes, 3 nibbles by default.
        #           -xxx xxxx xxxx

        # Increase 11 bit CAN headers to 4 bytes...
        #   Example:
        #              _ __ = 3 nibbles
        #              7 E8 06 41 00 BE 7F B8 13
        #   transform to:
        #       00 00 07 E8 06 41 00 BE 7F B8 13
        if self.iBitsID == 11:
            strRaw = "00000" + strRaw

        # Handle odd size frames...
        # NOTE: To unhexlify(), an even number of digits is required (2 per bytes)
        if len(strRaw) & 1:
            #logger.debug("Dropping frame for being odd")
            #return False
            strRaw = "0" + strRaw

        bsRaw = bytearray( unhexlify(strRaw) )

        #
        # Validate size...
        #
        # Ensure a PCI byte and at least one following data byte for FF frames
        # with headers, 11-bit length codes or 1 byte of data...
        #   Example:
        #       ---header-- PCI+data...
        #       00 00 07 E8 10 20 ...
        if len(bsRaw) < 6:
            logger.debug("Protocol: Frame too short! Dropping...")
            return False
        if len(bsRaw) > 12:
            logger.debug("Protocol: Frame too long! Dropping...")
            return False

        #
        # Read header information...
        #
        if self.iBitsID == 11:
            # Example:
            #  0  1  2  3  4  5 ...
            # 00 00 07 E8 06 41 00 BE 7F B8 13
            # [--Header-]
            frame.iPriority = bsRaw[2] & 0x0F  # ...0x07 Always
            frame.iAddrMode = bsRaw[3] & 0xF0  # ...0xD0 Functional, 0xE0 = Physical

            if frame.iAddrMode == 0xD0: # ...Functional Request
                # NOTE: A Frame to a Functional Receiver from the Scanner Transmitter should NEVER be received by the Scanner!
                #   Response frames should always be Physical!
                frame.iRxID = bsRaw[3] & 0x0F     # ...0x0F = Functional Receiver
                frame.iTxID = 0xF1                   # ...0xF1 = Scanner Transmitter (implied)
            elif frame.iAddrMode == 0xE0: # ...Physical Request or Response
                if bsRaw[3] & 0x08: # ...Response (low nibble high bit set)
                    frame.iRxID = 0xF1               # ...0xF1 = Scanner Receiver (implied)
                    frame.iTxID = bsRaw[3] & 0x07 # ...0x0X = ECU#1-8(0-7) Transmitter (low nibble lower 3 bits)
                else: # ...Request (low nibble high bit NOT set)
                    # NOTE: A Frame to a Functional Receiver from the Scanner Transmitter should NEVER be received by the Scanner!
                    frame.iRxID = bsRaw[3] & 0x07 # ...0x0X = ECU#1-8(0-7) Receiver (low nibble lower 3 bits)
                    frame.iTxID = 0xF1               # ...0xF1 = Scanner Transmitter (implied)
            else: # Error
                logger.debug("Protocol: Incorrect 11 bit Frame! Dropping...")
                return False


        else: # self.id_bits == 29:
            # Example:
            #  0  1  2  3  4  5 ...
            # 18 DA 00 F1 06 41 00 BE 7F B8 13
            # [--Header-]
            frame.iPriority = bsRaw[0] # ...0x18 Always
            frame.iAddrMode = bsRaw[1] # ...0xDB = Functional, 0xDA = Physical
            frame.iRxID = bsRaw[2]    # ...0xF1 = Scanner Receiver
                # NOTE: A Frame to a Functional or Physical Receiver...
                #       0x33 = Functional Receiver, 0xXX = ECU # 1-256 (0-255) Receiver
            frame.iTxID = bsRaw[3]    # ...0xXX = ECU # 1-256 (0-255) Transmitter
                # NOTE: ...from the Scanner Transmitter should NEVER be received by the Scanner!
                #       0xF1 = Scanner

        # Extract the frame data...
        #  0  1  2  3  4  5 ...
        # 00 00 07 E8 06 41 00 BE 7F B8 13
        #             [------Frame-------]
        frame.baData = bsRaw[4:]

        # Analyze the PCI byte (the high nibble of the first data byte)...
        #             v
        # 00 00 07 E8 06 41 00 BE 7F B8 13
        frame.iType = frame.baData[0] & 0xF0
        if frame.iType not in [self.FRAME_TYPE_SF,
                              self.FRAME_TYPE_FF,
                              self.FRAME_TYPE_CF]:
            logger.debug("Protocol: Frame has unknown PCI Frame Type. Dropping...")
            return False

        # If a Single Frame...
        if frame.iType == self.FRAME_TYPE_SF:
            # Single frames have 4 bit length codes (the low nibble of
            #   the first data byte)...
            #              v
            # 00 00 07 E8 06 41 00 BE 7F B8 13
            frame.iDataLen = frame.baData[0] & 0x0F

            # If the frame has no data, drop it...
            if frame.iDataLen == 0:
                return False

        # If a First Frame of a multiframe...
        elif frame.iType == self.FRAME_TYPE_FF:
            # First Frames have a 12 bit length codes (the next 3 nibbles
            #   after the first data nibble)...
            #              v vv
            # 00 00 07 E8 10 20 49 04 00 01 02 03
            frame.iDataLen = (frame.baData[0] & 0x0F) << 8
            frame.iDataLen += frame.baData[1]

            # If the frame has no data, drop it...
            if frame.iDataLen == 0:
                return False

        # If a Consecutive Frame of a multiframe...
        elif frame.iType == self.FRAME_TYPE_CF:
            # Consecutive frames have a 4 bit Order index (the low nibble
            #   of the first data byte)...
            #              v
            # 00 00 07 E8 21 04 05 06 07 08 09 0A
            frame.iOrder = frame.baData[0] & 0x0F

        return True

    def parseMessage(self, message : Message):
        frames = message.listFrames

        if len(frames) == 1:
            frame = frames[0]

            if frame.iType != self.FRAME_TYPE_SF:
                logger.debug("Protocol: Solitary Frame received NOT marked as a Single Frame. Dropping...")
                return False

            # Extract the data ignoring the PCI byte and any data after
            #   the length marker...
            #             [      Frame       ]
            # 00 00 07 E8 06 41 00 BE 7F B8 13 xx xx xx xx
            #                [     Data      ]
            message.baData = frame.baData[ 1:(1 + frame.iDataLen) ]

        else:
            # Sort multiframes (FF and CF) into separate lists...
            listFramesFirst : list[Frame] = []
            listFramesAfter : list[Frame] = []

            for frame in frames:
                if frame.iType == self.FRAME_TYPE_FF:
                    listFramesFirst.append(frame)
                elif frame.iType == self.FRAME_TYPE_CF:
                    listFramesAfter.append(frame)
                else:
                    logger.debug("Protocol: Frame in MultiFrame response not marked as FF or CF.")

            # If there is more than one First Frame...
            if len(listFramesFirst) > 1:
                logger.debug("Protocol: Multiple frames marked First. Dropping...")
                return False
            # If there are NO First Frames...
            elif len(listFramesFirst) == 0:
                logger.debug("Protocol: No Frame marked First. Dropping...")
                return False

            # If there are NO consecutive frames...
            if len(listFramesAfter) == 0:
                logger.debug("Protocol: No Frame marked Consecutive. Dropping...")
                return False

            # The Following calculation NEVER occurs as documented as there are NEVER any HIGH BITS:
            #   framePair[0].iOrder & ~0x0F == 0 ALWAYS!!!
            #   Also, ~0x0F == 0xFFFFFFF0
            # The code is reduced to the proper frame advancing Order index calculation after this
            # COMMENT as there are only EVER 16 indices (0 to F) that repeat.
            #
            ## Calculate proper frame order from the Order bits given...
            #for framePair in zip(listFramesAfter, listFramesAfter[1:]):
            #    # Frame order only specifies the low order bits.  Calculate the full Order index
            #    #   from the Frame index and the last Order index:
            #    #   1. Get the high order bits from the previous Frame's Order index and
            #    #       low order bits from the current Frame's Order index...
            #    iOrder = (framePair[0].iOrder & ~0x0F) + framePair[1].iOrder
            #    #   2. If Order is more than 7 frames away, an index wrap probably occurred:
            #    #       pair[0] = 0x0F, pair[1] = 0x01 should produce 0x11, not 0x01)
            #    if iOrder < framePair[0].iOrder - 7:
            #        iOrder += 0x10
            #
            #    framePair[1].iOrder = iOrder

            for iIndex in range( len(listFramesAfter) - 1 ):
                # If the NEXT frame Order is less than the PRIOR frame Order minus a Window value
                #   (8, half the available indices), then ASSUME the NEXT frame Order indicates a
                #   new index cycle and INCREMENT the NEXT frame order by 16 (pushing it up over
                #   PRIOR frame Order)...
                # NOTE: This will naturally push any following low Order NEXT frames (inside the
                #       window) up as well and leave in place any high Order NEXT frames (outside
                #       the window).
                # NOTE: Any repeating Order index that is not incremented will "replace" the prior
                #       "same Order index" frame. This will reduce the number of frames and could
                #       be problematic if a frame should have otherwise been incremented.
                frameNext = listFramesAfter[iIndex + 1]
                framePrior = listFramesAfter[iIndex]
                iWindow = 8 # NOTE: Narrow by increasing, Widen by decreasing
                if frameNext.iOrder < framePrior.iOrder - iWindow:
                    frameNext.iOrder += 0x10

            # Sort the frames by Order index...
            listFramesAfter = sorted( listFramesAfter, key = lambda frame: frame.iOrder )

            listIndices = [frame.iOrder for frame in listFramesAfter]
            # If the Order indices are not contiguous...
            if not self.isContiguousInts( listIndices, 1, len(listFramesAfter) ):
                # An error occurred...
                logger.debug("Protocol: The MultiFrame is NOT contiguous (missing or duplicate Frames). Dropping...")
                return False

            #
            # Accumulate ordered data from each frame...
            #
            # First Frame:
            #             [       Frame         ]
            #             [PCI]                    <-- Frame has a 2 byte PCI
            #              [L ] [     Data      ]  L = message length in bytes
            # 00 00 07 E8 10 13 49 04 01 35 36 30
            #
            # Consecutive Frame:
            #             [       Frame         ]
            #             []                       <-- Frames have a 1 byte PCI
            #              N [       Data       ]  N = Frame Order Number (rolls over to 0 after F)
            # 00 00 07 E8 21 32 38 39 34 39 41 43
            # 00 00 07 E8 22 00 00 00 00 00 00 31
            #
            # Accumulated Data:
            # [                          Data                        ]    Length == L
            # 49 04 01 35 36 30 32 38 39 34 39 41 43 00 00 00 00 00 00 31

            message.baData = listFramesFirst[0].baData[2:] # ...skip the First Frame PCI two bytes
            for frame in listFramesAfter:
                message.baData += frame.baData[1:]  # skip the Consecutive Frame PCI byte

            # Trim the data to the First Frame data length size...
            message.baData = message.baData[:listFramesFirst[0].iDataLen]

        # If a GET_DTC request...
        if message.baData[0] == 0x43:
            # Trim GET_DTC requests based on DTC Count...

            # NOTE: This is NOT in the decoder because the legacy protocols don't provide DTC Count bytes.
            #       Legacy protocols insert a 0x00 for consistency

            # [         Data        ]
            # [] []                    <-- Mode and DTC count
            # 43 03 11 11 22 22 33 33
            #       [DTC] [DTC] [DTC]

            iDTCCount = message.baData[1] * 2  # ...each DTC Code is 2 bytes
            message.baData = message.baData[:(iDTCCount + 2)]  # ...add Mode & DTC Count bytes

        return True


# ==================================================
#
# CAN Protocol SubClasses
#
# ==================================================


class ISO_15765_4_11bit_500k(CANProtocol):
    ELM_NAME = "ISO 15765-4 (CAN 11/500)"
    ELM_ID = "6"

    def __init__(self, listRespLines):
        CANProtocol.__init__(self, listRespLines, iBitesID=11)


class ISO_15765_4_29bit_500k(CANProtocol):
    ELM_NAME = "ISO 15765-4 (CAN 29/500)"
    ELM_ID = "7"

    def __init__(self, listRespLines):
        CANProtocol.__init__(self, listRespLines, iBitesID=29)


class ISO_15765_4_11bit_250k(CANProtocol):
    ELM_NAME = "ISO 15765-4 (CAN 11/250)"
    ELM_ID = "8"

    def __init__(self, listRespLines):
        CANProtocol.__init__(self, listRespLines, iBitesID=11)


class ISO_15765_4_29bit_250k(CANProtocol):
    ELM_NAME = "ISO 15765-4 (CAN 29/250)"
    ELM_ID = "9"

    def __init__(self, listRespLines):
        CANProtocol.__init__(self, listRespLines, iBitesID=29)


class SAE_J1939(CANProtocol):
    ELM_NAME = "SAE J1939 (CAN 29/250)"
    ELM_ID = "A"

    def __init__(self, listRespLines):
        CANProtocol.__init__(self, listRespLines, iBitesID=29)
