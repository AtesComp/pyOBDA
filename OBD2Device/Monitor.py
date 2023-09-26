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
        self._tests = {}  # tid : MonitorTest

        # make the standard TIDs available as null monitor tests
        # until real data comes it. This also prevents things from
        # breaking when the user looks up a standard test that's null.
        null_test = MonitorTest()

        for tid in MonitorTest.LABELS:
            name = MonitorTest.LABELS[tid][0]
            self.__dict__[name] = null_test
            self._tests[tid] = null_test

    def add_test(self, test):
        self._tests[test.tid] = test
        if test.name is not None:
            self.__dict__[test.name] = test

    @property
    def tests(self):
        return [test for test in self._tests.values() if not test.is_null()]

    def __str__(self):
        if len(self.tests) > 0:
            return "\n".join([str(t) for t in self.tests])
        else:
            return "No tests to report"

    def __len__(self):
        return len(self.tests)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._tests.get(key, MonitorTest())
        elif isinstance(key, str):
            return self.__dict__.get(key, MonitorTest())
        else:
            logger.warning("Monitor Test results can only be retrieved by ID (int) or Name (str)")
