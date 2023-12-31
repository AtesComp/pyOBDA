############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# StatusTest.py
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


class StatusTest():
    def __init__(self, strName : str = "", bAvailable : bool = False, bComplete: bool = False):
        self.strName = strName
        self.bAvailable = bAvailable
        self.bComplete = bComplete

    def __str__(self):
        strAvailable = "Available" if self.bAvailable else "Unavailable"
        strComplete = "Complete" if self.bComplete else "Incomplete"
        return "Test %s: %s, %s" % (self.strName, strAvailable, strComplete)

    def isNull(self):
        return (
            self.strName is None or
            self.strName is ""
        )
