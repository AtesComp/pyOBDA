############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# ECU.py
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


class ECU:
    class HEADER:
        # Values for the ECU headers
        ENGINE = b'7E0'

    # Constant Flags
    #       Used for marking and filtering messages

    ALL       = 0b11111111  # ...used by OBDCommands to accept messages from any ECU
    ALL_KNOWN = 0b11111110  # ...used to ignore unknown ECUs

    # ECU Mask Bits
    #       Each ECU gets its own bit
    UNKNOWN      = 0b00000001  # ...unknowns get their own bit since they need to be accepted by the ALL filter
    ENGINE       = 0b00000010
    TRANSMISSION = 0b00000100
