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
#   "obd/protocols/protocol_unknown.py"
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

from .Protocol import Protocol


class UnknownProtocol(Protocol):
    # Class representing an unknown protocol
    #
    # Used for an ELM connection when the vehicle has NOT responded.

    ELM_NAME = "UNKNOWN"
    ELM_ID = "-1"

    def parseFrameData(self, frame):
        return True  # ...default

    def parseMessage(self, message):
        return True  # ...default
