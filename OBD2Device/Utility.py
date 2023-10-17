############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# OBD2Connector.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file "obd/utils.py"
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
import string

logger = logging.getLogger(__name__)


class Utility:
    """
    The Utility Class is a placeholder class for class methods used elsewhere.
    """

    @classmethod
    def convertBEBytesToInt(cls, baBytes: bytearray) -> int:
        """
        Convert a big-endian bytearray into a single integer.
        The bytearray is limited to the first 4 least significant bytes as any larger bytes would be
        outside an integer's 32 bit limit.
        """

        iValue = 0
        iOffset = 0
        iLen = len(baBytes)
        iLen = 4 if iLen > 4 else iLen
        for iByte in reversed(baBytes[0:iLen]):
            iValue += iByte * (2 ** iOffset)
            iOffset += 8
        return iValue

    @classmethod
    def convertByteArrayToHexString(cls, baMessage: bytearray):
        """
        Convert a bytearray into a Hex string with leading 0s if needed.
        """

        strHex = ""
        for iByte in baMessage:
            strHexByte = hex(iByte)[2:]
            strHex += ("0" * (2 - len(strHexByte))) + strHexByte
        return strHex

    @classmethod
    def calc2sCompliment(cls, iValue: int, iBitCount: int):
        """
        Calculate the 2's compliment an integer value.
        """

        if ( ( iValue & ( 1 << (iBitCount - 1) ) ) != 0 ):
            iValue = iValue - (1 << iBitCount)
        return iValue

    @classmethod
    def isHex(cls, strHex: str):
        """
        Does a string represent a hex value?
        """

        return all( [strChar in string.hexdigits for strChar in strHex] )
