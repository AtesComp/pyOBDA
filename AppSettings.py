############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# AppSettings.py
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

VERSION = "1.5.0"

ID_ABOUT  = 101
ID_EXIT   = 110
ID_CONFIG = 500
ID_CLEAR  = 501
ID_GETC   = 502
ID_RESET  = 503
ID_LOOK   = 504
ALL_ON    = 505
ALL_OFF   = 506

ID_DISCONNECT = 507
ID_HELP_ABOUT = 508
ID_HELP_VISIT = 509
ID_HELP_ORDER = 510

CHAR_CHECK   = u'\u2713'
CHAR_BALLOTX = u'\u2717'
CHAR_CROSSX  = u'\u274C'
CHAR_QMARK   = u'\u003F'

# Debug Setting for wx Trace Page
#   Debug events are sent to the Trace Page for display.
#   The DEBUG_LEVEL controls what Debug Events will be sent to the Trace Page:
#   0 = No Debug Events (least verbose)
#       to
#   5 = All Debug Events (most verbose)
DEBUG_LEVEL = 5  # ...default - debug everthing, changed by config

STR_HELP_TEXT = \
    "Onboard Diagnostics II Advanced:  pyOBDA  Version " + VERSION + "\n" + \
    "  (C) 2021-2023 Keven L. Ates (atescomp@gmail.com)\n" + \
    "\n" + \
    "To setup a configuration for pyOBDA:\n" + \
    "  Linux: create a config file in your HOME directory at .config/pyobda/\n" + \
    "    ~/.config/pyobda/config\n" + \
    "  Mac: same as Linux\n" + \
    "  Windows: create a pyobda.ini file in the pyOBDA program directory\n" + \
    "    <path_to_pyOBDA>\\pyobda\\pyobda.ini\n" + \
    "\n" + \
    "In the config file, place similar following text with your settings:\n" + \
    "----------------------------------------\n" + \
    "[OBD]\n" + \
    "PORT=/dev/ttyUSB0\n" + \
    "BAUD=115200\n" + \
    "PROTOCOL=6\n" + \
    "FAST=True\n" + \
    "CHECKVOLTS=True\n" + \
    "TIMEOUT=2\n" + \
    "RECONNECTS=5\n" + \
    "[DEBUG]\n" + \
    "LEVEL=1\n" + \
    "----------------------------------------\n" + \
    "\n" + \
    "Based on PyOBD and python-obd\n" + \
    "  PyOBD:\n" + \
    "    (C) 2008-2009 SeCons Ltd. (www.obdtester.com)\n" + \
    "    (C) 2004 Charles Donour Sizemore (donour@uchicago.edu)\n" + \
    "    (C) 2021 Jure Poljsak (https://github.com/barracuda-fsh/pyobd)\n" + \
    "  python-obd:\n" + \
    "    (C) 2004 Donour Sizemore (donour@uchicago.edu)\n" + \
    "    (C) 2009 Secons Ltd. (www.obdtester.com)\n" + \
    "    (C) 2009 Peter J. Creath\n" + \
    "    (C) 2016 Brendan Whitfield (brendan-w.com)\n" + \
    "\n" + \
    "pyOBDA is free software! You can redistribute it and/or modify it under the terms of " + \
    "the GNU General Public License as published by the Free Software Foundation using " + \
    "either version 2 of the License, or (at your option) any later version.\n" + \
    "\n" + \
    "pyOBDA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY--" + \
    "without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  " + \
    "See the GNU General Public License for more details.  You should have received a copy " + \
    "of the GNU General Public License along with PyOBD.  If not, write to the\n" + \
    "  Free Software Foundation, Inc.\n" + \
    "  59 Temple Place\n" + \
    "  Suite 330\n" + \
    "  Boston, MA  02111-1307  USA"
