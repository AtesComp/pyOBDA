############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Frame.py
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


class Frame(object):
    # A Frame represents a single parsed line of OBD output

    def __init__(self, strRaw : str):
        self.strRaw : str = strRaw
        self.baData = bytearray()
        self.iPriority :int = None
        self.iAddrMode : int = None
        self.iRxID : int = None
        self.iTxID : int = None
        self.iType : int = None
        self.iOrder : int = 0  # ...only used with type CF
        self.iDataLen : int = None
