############################################################################
#
# Connection.py
#
# Copyright 2023 Keven L. Ates (atescomp@gmail.com)
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
# along with pyOBDA; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
############################################################################

# A simple Connection class to hold connection values...
class Connection():
    strPortNameDefault = "/dev/ttyUSB0"
    iDebugLevelDefault = 5

    def __init__(self, connect) :
        self.setConnection(connect)

    def setConnection(self, connect) :
        if connect != None :
            self.PORTNAME = connect.PORTNAME
            self.PORT = connect.PORT
            self.BAUD = connect.BAUD
            self.PROTOCOL = connect.PROTOCOL
            self.FAST = connect.FAST
            self.CHECKVOLTS = connect.CHECKVOLTS
            self.TIMEOUT = connect.TIMEOUT
            self.RECONNECTS = connect.RECONNECTS
        else :
            self.PORTNAME = None
            self.PORT = None
            self.BAUD = None
            self.PROTOCOL = None
            self.FAST = None
            self.CHECKVOLTS = None
            self.TIMEOUT = None
            self.RECONNECTS = None

    def resetConnection(self):
        global DEBUG_LEVEL

        self.PORTNAME = Connection.strPortNameDefault
        self.BAUD = 115200
        self.PROTOCOL = "6"
        self.FAST = True
        self.CHECKVOLTS = True
        self.TIMEOUT = 10
        self.RECONNECTS = 3
        DEBUG_LEVEL = Connection.iDebugLevelDefault
