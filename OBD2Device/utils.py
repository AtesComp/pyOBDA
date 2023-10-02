########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2015 Brendan Whitfield (bcw7044@rit.edu)                   #
#                                                                      #
########################################################################
#                                                                      #
# utils.py                                                             #
#                                                                      #
# This file is part of python-OBD (a derivative of pyOBD)              #
#                                                                      #
# python-OBD is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# python-OBD is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with python-OBD.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                      #
########################################################################

import errno
import glob
import logging
import string
import sys

import serial

logger = logging.getLogger(__name__)


class BitArray:
    """
    Class for representing bitarrays (inefficiently)

    There's a nice C-optimized lib for this: https://github.com/ilanschnell/bitarray
    but python-OBD doesn't use it enough to be worth adding the dependency.
    But, if this class starts getting used too much, we should switch to that lib.
    """

    def __init__(self, baValue : bytearray):
        iLen = len(baValue) * 8
        self.aBits = [ False for iIndex in range(iLen) ]
        for iByteIndex in range(iLen):
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
        return len(self.strBits)

    def __str__(self):
        return self.strBits

    def __iter__(self):
        return [b == "1" for b in self.strBits].__iter__()


def convertBEBytesToInt(baBytes : bytearray) -> int:
    # Convert a big-endian byte array into a single integer
    iValue = 0
    iOffset = 0
    for iByte in reversed(baBytes):
        iValue += iByte * (2 ** iOffset)
        iOffset += 8
    return iValue


def convertByteArrayToHexString(baMessage : bytearray):
    strHex = ""
    for iByte in baMessage:
        strHexByte = hex(iByte)[2:]
        strHex += ("0" * (2 - len(strHexByte))) + strHexByte
    return strHex


def calc2sCompliment(iValue, iBitCount):
    # Calculate the 2's compliment an integer value
    if ( ( iValue & ( 1 << (iBitCount - 1) ) ) != 0 ):
        iValue = iValue - (1 << iBitCount)
    return iValue


def isHex(strHex : str):
    # Does a string represent a hex value?
    return all( [strChar in string.hexdigits for strChar in strHex] )



def isPortAvailable(strPort : str):
    # Is a port available?
    try:
        serialPort = serial.Serial(strPort)
        serialPort.close()  # ...explicit close
        # Available...
        return True
    except serial.SerialException:
        pass
    except OSError as e:
        # If NOT a No Entry (File or Directory) error...
        if e.errno != errno.ENOENT:
            # ...throw that error...
            raise e
    # Otherwise, not available...
    return False


def scanSerialPorts():
    # Scan for available serial ports

    # Get all possible ports...
    listPortsPossible : list[str]  = []
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        listPortsPossible += glob.glob("/dev/rfcomm[0-9]*")
        listPortsPossible += glob.glob("/dev/ttyUSB[0-9]*")
    elif sys.platform.startswith('win'):
        listPortsPossible += ["\\.\COM%d" % i for i in range(256)]
    elif sys.platform.startswith('darwin'):
        listPortsExclude = [
            '/dev/tty.Bluetooth-Incoming-Port',
            '/dev/tty.Bluetooth-Modem'
        ]
        listPortsPossible += [port for port in glob.glob('/dev/tty.*') if port not in listPortsExclude]
    #listPortsPossible += glob.glob('/dev/pts/[0-9]*') # for OBDSim?

    listPortsAvailable : list[str] = []
    for strPort in listPortsPossible:
        if isPortAvailable(strPort):
            listPortsAvailable.append(strPort)

    return listPortsAvailable
