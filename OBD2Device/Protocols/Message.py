############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Message.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten in part from the project "python-OBD" file
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

from binascii import hexlify

from .Frame import Frame
from .ECU import ECU


class Message(object):
    # A Message represents a fully parsed OBD message of one or more Frames

    def __init__(self, listFrames : list[Frame]):
        self.listFrames = listFrames
        self.iECU : int = ECU.UNKNOWN
        self.baData = bytearray()

    @property
    def TxID(self):
        if len(self.listFrames) == 0:
            return None
        else:
            return self.listFrames[0].iTxID

    def hex(self) -> bytes:
        return hexlify(self.baData)

    def raw(self) -> str:
        # Get the original raw input string from the adapter
        return "\n".join([frame.strRaw for frame in self.listFrames])

    def isParsed(self):
        # Is message parsed?
        return bool(self.baData)

    def __eq__(self, other):
        if isinstance(other, Message):
            for attr in ["frames", "ecu", "data"]:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        else:
            return False
