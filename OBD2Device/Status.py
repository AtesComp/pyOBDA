############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Status.py
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

from .StatusTest import StatusTest
from .Codes import Codes


class Status:
    def __init__(self):
        self.MIL = False
        self.DTC_count = 0
        self.ignition_type = ""

        # make sure each test is available by name
        # until real data comes it. This also prevents things from
        # breaking when the user looks up a standard test that's null.
        null_test = StatusTest()
        for name in Codes.Test.Base + Codes.Test.Spark + Codes.Test.Compression:
            if name:  # filter out None/reserved tests
                self.__dict__[name] = null_test
