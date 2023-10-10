############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Connection.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
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

import AppSettings
import OBD2Device


# A simple Connection class to hold connection values...
class Connection():
    strPortNameDefault:str = "/dev/ttyUSB0"
    iDebugLevelDefault:int = 5

    def __init__(self, connect) : # connect is a Connection object
        self.setConnection(connect)

    def setConnection(self, connect) :
        self.PORTNAME:str = Connection.strPortNameDefault
        self.BAUD:int = 115200
        self.PROTOCOL:str = "6"
        self.FAST:bool = True
        self.TIMEOUT:float = 10.0
        self.CHECKVOLTS:bool = True
        self.RECONNECTS:int = 3
        AppSettings.DEBUG_LEVEL = Connection.iDebugLevelDefault
        OBD2Device.setLogging()
        if connect != None :
            self.PORTNAME = connect.PORTNAME
            self.BAUD = connect.BAUD
            self.PROTOCOL = connect.PROTOCOL
            self.FAST = connect.FAST
            self.TIMEOUT = connect.TIMEOUT
            self.CHECKVOLTS = connect.CHECKVOLTS
            self.RECONNECTS = connect.RECONNECTS

    def resetConnection(self):
        self.PORTNAME = Connection.strPortNameDefault
        self.BAUD = 115200
        self.PROTOCOL = "6"
        self.FAST = True
        self.TIMEOUT = 10.0
        self.CHECKVOLTS = True
        self.RECONNECTS = 3
        AppSettings.DEBUG_LEVEL = Connection.iDebugLevelDefault
        OBD2Device.setLogging()
