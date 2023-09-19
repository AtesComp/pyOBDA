############################################################################
#
# Utility.py
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

DEBUG_LEVEL = 5  # ...debug everthing until told otherwise

STR_HELP_TEXT = \
            "Onboard Diagnostics II Advanced: pyOBDA\n" + \
            "pyOBDA uses the Python OBD library to manage the OBD2 connection.\n" + \
            "\n" + \
            "To setup a configuration for pyOBDA:\n" + \
            "Linux: create a config file in your HOME directory at .config/pyobda/\n" + \
            "    ~/.config/pyobda/config\n" + \
            "Mac: same as Linux.\n" + \
            "Windows: create a pyobda.ini file in the pyOBDA program directory\n" + \
            "    <path_to_pyOBDA>\\pyobda\\pyobda.ini\n" + \
            "\n" + \
            "In the config file, place similar text with your settings:\n" + \
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
            "\n" + \
            "Based on PyOBD:\n" + \
            "  (C) 2008-2009 SeCons Ltd. (www.obdtester.com)\n" + \
            "  (C) 2004 Charles Donour Sizemore (donour@uchicago.edu)\n" + \
            "  (C) 2021 Jure Poljsak (https://github.com/barracuda-fsh/pyobd)" + \
            "\n" + \
            "pyOBDA is free software! You can redistribute it and/or modify it under the terms of " + \
            "the GNU General Public License as published by the Free Software Foundation using " + \
            "either version 2 of the License, or (at your option) any later version.\n" + \
            "\n" + \
            "pyOBDA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY--" + \
            "without even the implied warranty of MEHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  " + \
            "See the GNU General Public License for more details.  You should have received a copy " + \
            "of the GNU General Public License along with PyOBD.  If not, write to the\n" + \
            "  Free Software Foundation, Inc.\n" + \
            "  59 Temple Place\n" + \
            "  Suite 330\n" + \
            "  Boston, MA  02111-1307  USA"
