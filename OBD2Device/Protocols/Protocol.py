############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Protocol.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file
#   "obd/protocols/protocol.py"
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

from .Frame import Frame
from .ECU import ECU
from .Message import Message

from OBD2Device.Utility import Utility
from OBD2Device.BitArray import BitArray

logger = logging.getLogger(__name__)

#
# Class Protocol
#
# This class is a base class for other protocol implementations.
#
# Protocol objects are factories for Frame and Message objects.
# They are largely stateless, with the exception of an ECU tagging
# system that is initialized by passing the response to an "0100"
#  command.
#
# Protocols are called ( __call__ ) with a list of response strings
# and return a list of Messages.

class Protocol(object):
    #
    # OVERRIDES
    #
    # Override the following Class Variable in each protocol subclass.

    # ELM Values...
    ELM_NAME = ""  # ELM Name for this protocol (ie, "SAE J1939 (CAN 29/250)")
    ELM_ID   = ""  # ELM ID for this protocol (ie, "A")

    # TX_IDs of known ECUs...
    TX_ID_ENGINE : int       = None
    TX_ID_TRANSMISSION : int = None

    def __init__(self, listRespLines : list[str]):
        #
        # Construct a Protocol Object
        #

        # Use a list of raw strings from the vehicle to determine the ECU layout.

        # Create the default, empty ECU map...
        #   Example Map:
        #       { self.TX_ID_ENGINE : ECU.ENGINE }
        self.mapECU : dict[int, int] = {}

        if (self.TX_ID_ENGINE is not None):
            self.mapECU[self.TX_ID_ENGINE] = ECU.ENGINE

        if (self.TX_ID_TRANSMISSION is not None):
            self.mapECU[self.TX_ID_TRANSMISSION] = ECU.TRANSMISSION

        # Parse the "0100" response data into messages...
        # NOTE: At this point, the "ECU" property will be UNKNOWN
        messages = self.__call__(listRespLines)

        # Read the messages and assemble the map...
        # NOTE: Subsequent runs will be tagged correctly
        self.constructECUMap(messages)

        # Log the ECU map...
        for iTxID, ecu in self.mapECU.items():
            listNames = [k for k, v in ECU.__dict__.items() if v == ecu]
            listNames = ", ".join(listNames)
            logger.debug("Protocol: Map ECU %d --> %s" % (iTxID, listNames))

    def __call__(self, listRespLines : list[str]) -> list[Message]:
        # Main function
        #
        # Accept a list of raw strings from the vehicle, split into lines

        #
        # Preprocess
        #
        # NOTE: Non-OBD reponses shouldn't go through the big parsers since they are
        #       typically messages such as: "NO DATA", "CAN ERROR", "UNABLE TO CONNECT", etc.,
        #       so sort them into two lists.
        linesOBD : list[str] = []
        linesNonOBD : list[str] = []

        for strLine in listRespLines:
            strLineCondensed = strLine.replace(' ', '')
            if Utility.isHex(strLineCondensed):
                linesOBD.append(strLineCondensed)
            else:
                linesNonOBD.append(strLine)  # ...original, un-scrubbed line

        #
        # Handle Valid OBD Lines
        #

        # Parse each frame (each line)...
        frames : list[Frame] = []
        for strLine in linesOBD:

            frame = Frame(strLine)

            # Subclass function to parse the lines into Frames...
            # NOTE: Drop frames that couldn't be parsed.
            if self.parseFrameData(frame):
                frames.append(frame)

        # Group frames by transmitting ECU...
        framesByECU : dict[ int, list[Frame] ] = {}
        for frame in frames:
            if frame.iTxID not in framesByECU:
                framesByECU[frame.iTxID] = [frame]
            else:
                framesByECU[frame.iTxID].append(frame)

        # Parse frames into whole messages...
        messages : list[Message] = []
        for iECU in sorted(framesByECU.keys()):

            # Create new message object with a copy of the raw data and frames
            #   addressed for this ecu...
            message = Message( framesByECU[iECU] )

            # Subclass function to assemble frames into Messages...
            if self.parseMessage(message):
                # Mark the appropriate ECU ID...
                message.iECU = self.mapECU.get(iECU, ECU.UNKNOWN)
                messages.append(message)

        #
        # Handle Invalid Lines (probably from the ELM)
        #

        for strLine in linesNonOBD:
            # Give each line its own message object...
            # NOTE: Messages are ECU.UNKNOWN by default.
            messages.append( Message( [ Frame(strLine) ] ) )

        return messages

    def constructECUMap(self, messages : list[Message]):
        # Given a list of messages from different ECUs (in response to the 0100 PID listing command),
        #   associate each TxID to an ECU ID constant
        #
        # This is mostly concerned with finding the engine.

        # Filter out messages that don't contain any data...
        # NOTE: This will prevent ELM responses from being mapped to ECUs
        messages = [ message for message in messages if message.isParsed() ]

        #
        # Populate the map...
        #
        # If no response...
        if len(messages) == 0:
            pass
        # If one response, mark it as the engine regardless...
        elif len(messages) == 1:
            self.mapECU[messages[0].TxID] = ECU.ENGINE
        # Otherwise...
        else:
            # The engine is important!
            # If not found, use a fallback...
            found_engine = False

            # If any TxIDs are exact matches to the expected values, record them...
            for message in messages:
                if message.TxID is None:
                    logger.debug("Protocol: An ECU TxID is missing. Continue...")
                    continue

                if message.TxID == self.TX_ID_ENGINE:
                    self.mapECU[message.TxID] = ECU.ENGINE
                    found_engine = True
                elif message.TxID == self.TX_ID_TRANSMISSION:
                    self.mapECU[message.TxID] = ECU.TRANSMISSION
                # TODO: program more of these when we figure out their constants

            if not found_engine:
                # Last Resort Solution: Choose ECU with the most bits set (most PIDs supported)
                #   to be the engine...
                iBestBits = 0
                iTxID = None

                for message in messages:
                    iBits = BitArray(message.data).countSet()

                    if iBits > iBestBits:
                        iBestBits = iBits
                        iTxID = message.TxID

                self.mapECU[iTxID] = ECU.ENGINE

            # Any remaining TxIDs are unknown...
            for message in messages:
                if message.TxID not in self.mapECU:
                    self.mapECU[message.TxID] = ECU.UNKNOWN

    def isContiguousInts(listInts : list[int], iStart : int, iEnd : int):
        # Is a list of integers consecutive?
        if not listInts:
            return False
        if listInts[0] != iStart:
            return False
        if listInts[-1] != iEnd:
            return False

        # Examine consecutive integer pairs...
        zipPairs = zip(listInts, listInts[1:])
        if not all( [iVal1 + 1 == iVal2 for (iVal1, iVal2) in zipPairs] ):
            return False

        return True

    def parseFrameData(self, frame : Frame):
        # OVERRIDE in subclass for each protocol
        #
        # Receive a Frame object preloaded with the raw string line from the vehicle.
        #
        # Return a boolean. If fatal errors were found, this function should return False
        # and the Frame will be dropped.

        raise NotImplementedError()

    def parseMessage(self, message : Message):
        # OVERRIDE in subclass for each protocol
        #
        # Receive a Message object preloaded with a list of Frame objects.
        #
        # Return a boolean. If fatal errors were found, this function should return False
        # and the Message will be dropped.

        raise NotImplementedError()
