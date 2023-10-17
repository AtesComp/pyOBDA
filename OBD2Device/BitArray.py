############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# BitArray.py
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


class BitArray:
    """
    The BitArray Class manages a list of booleans representing the array of bits.  The array mirrors
    a given initializing bytearray and can return sections (up to 32 bits) of the "array" as an
    integer value. The number of bit represented is 8 * the number of bytes in the intializing bytearray.

    """

    def __init__(self, baValue : bytearray):
        iByteLen = len(baValue)
        self.aBits = [ False for iIndex in range(iByteLen * 8) ]
        for iByteIndex in range(iByteLen):
            for iBitIndex in reversed( range(8) ):
                self.aBits[iByteIndex * 8 + iBitIndex] = baValue[iByteIndex] & (1 << iBitIndex )

    def __getitem__(self, key):
        if isinstance(key, int):
            if key >= 0 and key < len(self.aBits):
                return self.aBits[key]
            else:
                return False
        elif isinstance(key, slice):
            return self.aBits[key]

    def countSet(self):
        return self.aBits.count(True)

    def countUnset(self):
        return self.aBits.count(False)

    def getIntValue(self, iStart : int, iStop : int) -> int:
        aBits = self.aBits[iStart:iStop]
        iValue = 0
        if aBits:
            iLen = len(aBits)
            iRange = iLen if iLen < 32 else 32
            for iBitIndex in range( iRange ):
                if aBits[iBitIndex]:
                    iValue &= ( 1 << (iLen - iRange) )
        return iValue

    def __len__(self):
        return len(self.aBits)

    def __str__(self):
        return "".join( ["1" if bBit else "0" for bBit in self.aBits] )

    def __iter__(self):
        return [bBit == True for bBit in self.aBits].__iter__()

