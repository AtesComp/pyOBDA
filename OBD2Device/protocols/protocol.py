########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2015 Brendan Whitfield (bcw7044@rit.edu)                   #
#                                                                      #
########################################################################
#                                                                      #
# protocols/protocol.py                                                #
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

import logging
from binascii import hexlify

from OBD2Device.utils import isHex, BitArray

logger = logging.getLogger(__name__)

"""

Basic data models for all protocols to use

"""


class ECU_HEADER:
    """ Values for the ECU headers """
    ENGINE = b'7E0'


class ECU:
    """ constant flags used for marking and filtering messages """

    ALL = 0b11111111  # used by OBDCommands to accept messages from any ECU
    ALL_KNOWN = 0b11111110  # used to ignore unknown ECUs, since this lib probably can't handle them

    # each ECU gets its own bit for ease of making OR filters
    UNKNOWN = 0b00000001  # unknowns get their own bit, since they need to be accepted by the ALL filter
    ENGINE = 0b00000010
    TRANSMISSION = 0b00000100


class Frame(object):
    """ represents a single parsed line of OBD output """

    def __init__(self, raw):
        self.raw = raw
        self.data = bytearray()
        self.priority = None
        self.addr_mode = None
        self.rx_id = None
        self.tx_id = None
        self.type = None
        self.seq_index = 0  # only used when type = CF
        self.data_len = None


class Message(object):
    """ represents a fully parsed OBD message of one or more Frames (lines) """

    def __init__(self, frames):
        self.frames = frames
        self.ecu = ECU.UNKNOWN
        self.data = bytearray()

    @property
    def tx_id(self):
        if len(self.frames) == 0:
            return None
        else:
            return self.frames[0].tx_id

    def hex(self):
        return hexlify(self.data)

    def raw(self):
        """ returns the original raw input string from the adapter """
        return "\n".join([f.raw for f in self.frames])

    def parsed(self):
        """ boolean for whether this message was successfully parsed """
        return bool(self.data)

    def __eq__(self, other):
        if isinstance(other, Message):
            for attr in ["frames", "ecu", "data"]:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        else:
            return False


"""

Protocol objects are factories for Frame and Message objects. They are
largely stateless, with the exception of an ECU tagging system, which
is initialized by passing the response to an "0100" command.

Protocols are __called__ with a list of string responses, and return a
list of Messages.

"""


class Protocol(object):
    # override in subclass for each protocol

    ELM_NAME = ""  # the ELM's name for this protocol (ie, "SAE J1939 (CAN 29/250)")
    ELM_ID = ""  # the ELM's ID for this protocol (ie, "A")

    # the TX_IDs of known ECUs
    TX_ID_ENGINE = None
    TX_ID_TRANSMISSION = None

    def __init__(self, lines_0100):
        # Construct a protocol object
        #
        # Uses a list of raw strings from the vehicle to determine the ECU layout.

        # Create the default, empty map...
        #   Example: self.TX_ID_ENGINE : ECU.ENGINE
        self.ecu_map = {}

        if (self.TX_ID_ENGINE is not None):
            self.ecu_map[self.TX_ID_ENGINE] = ECU.ENGINE

        if (self.TX_ID_TRANSMISSION is not None):
            self.ecu_map[self.TX_ID_TRANSMISSION] = ECU.TRANSMISSION

        # Parse the "0100" data into messages...
        # NOTE: At this point, the "ecu" property will be UNKNOWN
        messages = self(lines_0100) # ...__call__(lines_0100)

        # Read the messages and assemble the map...
        # NOTE: Subsequent runs will be tagged correctly
        self.populate_ecu_map(messages)

        # Log the ecu map...
        for tx_id, ecu in self.ecu_map.items():
            names = [k for k, v in ECU.__dict__.items() if v == ecu]
            names = ", ".join(names)
            logger.debug("map ECU %d --> %s" % (tx_id, names))

    def __call__(self, lines) -> list[Message]:
        # Main function
        #
        # Accept a list of raw strings from the vehicle, split by lines

        #
        # Preprocess
        #
        # NOTE: Non-hex (non-OBD) lines shouldn't go through the big parsers since they are
        #       typically messages such as: "NO DATA", "CAN ERROR", "UNABLE TO CONNECT", etc.,
        #       so sort them into two lists.
        obd_lines = []
        non_obd_lines = []

        for line in lines:
            line_no_spaces = line.replace(' ', '')
            if isHex(line_no_spaces):
                obd_lines.append(line_no_spaces)
            else:
                non_obd_lines.append(line)  # pass the original, un-scrubbed line

        #
        # Handle Valid OBD Lines
        #

        # Parse each frame (each line)...
        frames = []
        for line in obd_lines:

            frame = Frame(line)

            # Subclass function to parse the lines into Frames...
            # NOTE: Drop frames that couldn't be parsed.
            if self.parse_frame(frame):
                frames.append(frame)

        # Group frames by transmitting ECU...
        frames_by_ECU = {}
        for frame in frames:
            if frame.tx_id not in frames_by_ECU:
                frames_by_ECU[frame.tx_id] = [frame]
            else:
                frames_by_ECU[frame.tx_id].append(frame)

        # Parse frames into whole messages...
        messages:list[Message] = []
        for ecu in sorted(frames_by_ECU.keys()):

            # Create new message object with a copy of the raw data and frames
            #   addressed for this ecu...
            message = Message(frames_by_ECU[ecu])

            # Subclass function to assemble frames into Messages...
            if self.parse_message(message):
                # Mark the appropriate ECU ID...
                message.ecu = self.ecu_map.get(ecu, ECU.UNKNOWN)
                messages.append(message)

        #
        # Handle Invalid Lines (probably from the ELM)
        #

        for line in non_obd_lines:
            # Give each line its own message object...
            # NOTE: Messages are ECU.UNKNOWN by default.
            messages.append( Message( [ Frame(line) ] ) )

        return messages

    def populate_ecu_map(self, messages):
        # Given a list of messages from different ECUS (in response to the 0100 PID listing command),
        # associate each tx_id to an ECU ID constant
        #
        # This is mostly concerned with finding the engine.

        # Filter out messages that don't contain any data...
        # NOTE: This will prevent ELM responses from being mapped to ECUs
        messages = [m for m in messages if m.parsed()]

        #
        # Populate the map...
        #
        # If no response...
        if len(messages) == 0:
            pass
        # If one response, mark it as the engine regardless...
        elif len(messages) == 1:
            self.ecu_map[messages[0].tx_id] = ECU.ENGINE
        # Otherwise...
        else:
            # The engine is important!
            # If not found, use a fallback...
            found_engine = False

            # I any tx_ids are exact matches to the expected values, record them...
            for m in messages:
                if m.tx_id is None:
                    logger.debug("parse_frame failed to extract TX_ID")
                    continue

                if m.tx_id == self.TX_ID_ENGINE:
                    self.ecu_map[m.tx_id] = ECU.ENGINE
                    found_engine = True
                elif m.tx_id == self.TX_ID_TRANSMISSION:
                    self.ecu_map[m.tx_id] = ECU.TRANSMISSION
                # TODO: program more of these when we figure out their constants

            if not found_engine:
                # Last Resort Solution: Choose ECU with the most bits set (most PIDs supported)
                #   to be the engine...
                best = 0
                tx_id = None

                for message in messages:
                    bits = BitArray(message.data).num_set()

                    if bits > best:
                        best = bits
                        tx_id = message.tx_id

                self.ecu_map[tx_id] = ECU.ENGINE

            # Any remaining tx_ids are unknown...
            for m in messages:
                if m.tx_id not in self.ecu_map:
                    self.ecu_map[m.tx_id] = ECU.UNKNOWN

    def parse_frame(self, frame):
        # Override in subclass for each protocol
        #
        # Receive a Frame object preloaded with the raw string line from the vehicle.
        #
        # Return a boolean. If fatal errors were found, this function should return False
        # and the Frame will be dropped.

        raise NotImplementedError()

    def parse_message(self, message):
        # Override in subclass for each protocol
        #
        # Receive a Message object preloaded with a list of Frame objects.
        #
        # Return a boolean. If fatal errors were found, this function should return False
        # and the Message will be dropped.

        raise NotImplementedError()
