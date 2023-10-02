############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# Monitor.py
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

from .MonitorTest import MonitorTest

logger = logging.getLogger(__name__)


class Monitor:
    def __init__(self):
        self._testsByID : dict[int, MonitorTest] = {}  # iTestID : MonitorTest
        self._testsByName : dict[str, MonitorTest] = {}

        # Initialize the standard Test IDs as null monitor tests. This fills the display with
        # managable data when the user looks up a test that is missing actual data.
        null_test = MonitorTest()

        for iTestID in MonitorTest.LABELS:
            strName = MonitorTest.LABELS[iTestID][0]
            self._testsByName[strName] = null_test
            self._testsByID[iTestID] = null_test

    def addTest(self, test : MonitorTest):
        self._testsByID[test.iTestID] = test
        if test.strName is not None:
            self._testsByName[test.strName] = test

    @property
    def tests(self) -> list[MonitorTest]:
        return [ test for test in self._testsByID.values() if not test.isNull() ]

    def __str__(self):
        if len(self.tests) > 0:
            return "\n".join([str(t) for t in self.tests])
        else:
            return "Monitor: No tests to report."

    def __len__(self):
        return len(self.tests)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._testsByID.get(key, MonitorTest())
        elif isinstance(key, str):
            return self._testsByName.get(key, MonitorTest())
        else:
            logger.warning("Monitor Test results can only be retrieved by ID (int) or Name (str)")
