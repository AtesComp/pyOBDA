############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Response.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file "obd/OBDResponse.py"
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


import time

from .UnitAndScale import Unit


# Response class for OBD2 Commands

class Response:

    def __init__(self, command=None, messages=None):
        self.command = command
        self.messages = messages if messages else []
        self.value = None
        self.time = time.time()

    @property
    def unit(self):
        # for backwards compatibility
        #from Device import Unit  # local import to avoid cyclic-dependency
        if isinstance(self.value, Unit.Quantity):
            return str(self.value.u)
        elif self.value is None:
            return None
        else:
            return str(type(self.value))

    def isNull(self):
        return (not self.messages) or (self.value == None)

    def __str__(self):
        return str(self.value)
