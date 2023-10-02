############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# ELM327.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file "obd/__init__.py"
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
#
# For more documentation, visit:
#   http://python-obd.readthedocs.org/en/latest/
#
############################################################################

from .Protocols import ECU
from .utils import scanSerialPorts

from .OBD2Connector import OBD2Connector
from .OBD2ConnectorAsync import OBD2ConnectorAsync
from .ConnectionStatus import ConnectionStatus
from .CommandList import CommandList
from .Command import Command
from .Response import Response
from .UnitsAndScaling import Unit

import logging

#
# Logging Levels
# ===========================================================================================================
# Level             Numeric value   What it means / When to use it
#
# logging.NOTSET          0         When set on a logger, indicates that ancestor loggers are to be consulted
#                                   to determine the effective level. If that still resolves to NOTSET, then
#                                   all events are logged. When set on a handler, all events are handled.
#
# logging.DEBUG          10         Detailed information, typically only of interest to a developer trying to
#                                   diagnose a problem.
#
# logging.INFO           20         Confirmation that things are working as expected.
#
# logging.WARNING        30         An indication that something unexpected happened, or that a problem might
#                                   occur in the near future (e.g. ‘disk space low’). The software is still
#                                   working as expected.
#
# logging.ERROR          40         Due to a more serious problem, the software has not been able to perform
#                                   some function.
#
# logging.CRITICAL       50         A serious error, indicating that the program itself may be unable to
#                                   continue running.

import AppSettings

logger = logging.getLogger(__name__)
#logger.setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()  # ...send output to stderr
console_handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
logger.addHandler(console_handler)

def setLogging():
    iLevel:int = 50 - AppSettings.DEBUG_LEVEL * 10
    if iLevel == 0:
        iLevel = 10
    logger.setLevel(iLevel)