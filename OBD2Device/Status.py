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

import logging

from .StatusTest import StatusTest
from .Codes import Codes

logger = logging.getLogger(__name__)


class Status:
    def __init__(self):
        self.bMIL = False
        self.iDTC = 0
        self.strIgnitionType = ""
        self._testsByName : dict[str, StatusTest] = {}

        # make sure each test is available by name
        # until real data comes it. This also prevents things from
        # breaking when the user looks up a standard test that's null.
        testNull = StatusTest()
        for strName in Codes.Test.Base + Codes.Test.Spark + Codes.Test.Compression:
            if strName:  # filter out None/reserved tests
                self._testsByName[strName] = testNull

    def addTest(self, test : StatusTest):
        if test.strName is not None:
            self._testsByName[test.strName] = test

    @property
    def tests(self) -> list[StatusTest]:
        return [ test for test in self._testsByName.values() if not test.isNull() ]

    def __str__(self):
        if len(self.tests) > 0:
            return "\n".join([str(t) for t in self.tests])
        else:
            return "Status: No tests to report."

    def __len__(self):
        return len(self.tests)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._testsByName.get(key, StatusTest())
        else:
            logger.warning("Status Test results can only be retrieved by Name (str)")
