############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# MonitorTest.py
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


class MonitorTest:

    # Monitor Test Labels

    LABELS = {
        # <TID>: (<name>, <description>)
        # 0x0 is reserved
        0x01: ("RTL_THRESHOLD_VOLTAGE", "Rich to lean sensor threshold voltage"),
        0x02: ("LTR_THRESHOLD_VOLTAGE", "Lean to rich sensor threshold voltage"),
        0x03: ("LOW_VOLTAGE_SWITCH_TIME", "Low sensor voltage for switch time calculation"),
        0x04: ("HIGH_VOLTAGE_SWITCH_TIME", "High sensor voltage for switch time calculation"),
        0x05: ("RTL_SWITCH_TIME", "Rich to lean sensor switch time"),
        0x06: ("LTR_SWITCH_TIME", "Lean to rich sensor switch time"),
        0x07: ("MIN_VOLTAGE", "Minimum sensor voltage for test cycle"),
        0x08: ("MAX_VOLTAGE", "Maximum sensor voltage for test cycle"),
        0x09: ("TRANSITION_TIME", "Time between sensor transitions"),
        0x0A: ("SENSOR_PERIOD", "Sensor period"),
        0x0B: ("MISFIRE_AVERAGE", "Average misfire counts for last ten driving cycles"),
        0x0C: ("MISFIRE_COUNT", "Misfire counts for last/current driving cycles"),
    }

    def __init__(self):
        self.tid = None
        self.name = None
        self.desc = None
        self.value = None
        self.min = None
        self.max = None

    @property
    def passed(self):
        if not self.is_null():
            return (self.value >= self.min) and (self.value <= self.max)
        else:
            return False

    def is_null(self):
        return (
            self.tid is None or
            self.value is None or
            self.min is None or
            self.max is None
        )

    def __str__(self):
        strPassed = "PASSED" if self.passed else "FAILED"
        return "%s : %s [%s]" % (self.desc, str(self.value), strPassed)
