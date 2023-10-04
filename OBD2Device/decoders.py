########################################################################
#                                                                      #
# python-OBD: A python OBD-II serial module derived from pyobd         #
#                                                                      #
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)                 #
# Copyright 2009 Secons Ltd. (www.obdtester.com)                       #
# Copyright 2009 Peter J. Creath                                       #
# Copyright 2016 Brendan Whitfield (brendan-w.com)                     #
#                                                                      #
########################################################################
#                                                                      #
# decoders.py                                                          #
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

import functools

from .UnitsAndScaling import Unit, UAS_IDS
from .Status import Status
from .StatusTest import StatusTest
from .Monitor import Monitor
from .MonitorTest import MonitorTest
from .Codes import Codes
from .Protocols.Message import Message

from .utils import *

import logging

logger = logging.getLogger(__name__)

'''
All decoders take the form:

def <name>(<list_of_messages>):
    ...
    return <value>

'''


# drop all messages, return None
def drop(_):
    return None


# data in, data out
def noop(listMessages : list[Message]):
    return listMessages[0].baData


# Hex in, BitArray out
def pid(listMessages : list[Message]):
    baHex = listMessages[0].baData[2:]
    return BitArray(baHex)


# returns the raw strings from the ELM
def raw_string(listMessages : list[Message]):
    return "\n".join([baMessage.raw() for baMessage in listMessages])


"""
Some decoders are simple and are already implemented in the Units And Scaling
tables (used mainly for Mode 06). The uas() decoder is a wrapper for any
Unit/Scaling in that table, simply to avoid redundant code.
"""


def uas(id_):
    """ get the corresponding decoder for this UAS ID """
    return functools.partial(decode_uas, id_=id_)


def decode_uas(listMessages : list[Message], iID):
    baMessage = listMessages[0].baData[2:]  # chop off mode and PID bytes
    return UAS_IDS[iID](baMessage)


"""
General sensor decoders
Return pint Quantities
"""

def count(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iCount = convertBEBytesToInt(baMessage)
    return iCount * Unit.count

# 0 to 100 %
def percent(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iPercent = baMessage[0]
    iPercent = iPercent * 100.0 / 255.0
    return iPercent * Unit.percent


# -100 to 100 %
def percentCentered(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iPercent = baMessage[0]
    iPercent = (iPercent - 128) * 100.0 / 128.0
    return iPercent * Unit.percent


# -40 to 215 C
def temperature(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iTemperature = convertBEBytesToInt(baMessage)
    iTemperature = iTemperature - 40
    return Unit.Quantity(iTemperature, Unit.celsius)  # non-multiplicative unit


# -128 to 128 mA
def currentCentered(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iCurrent = convertBEBytesToInt(baMessage[2:4])
    iCurrent = (iCurrent / 256.0) - 128
    return iCurrent * Unit.milliampere


# 0 to 1.275 volts
def sensorVoltage(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iVoltage = baMessage[0] / 200.0
    return iVoltage * Unit.volt


# 0 to 8 volts
def sensorVoltageBig(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iVoltage = convertBEBytesToInt(baMessage[2:4])
    iVoltage = (iVoltage * 8.0) / 65535
    return iVoltage * Unit.volt


# 0 to 765 kPa
def pressureFuel(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iPressure = baMessage[0]
    iPressure = iPressure * 3
    return iPressure * Unit.kilopascal


# 0 to 255 kPa
def pressure(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iPressure = baMessage[0]
    return iPressure * Unit.kilopascal


# -8192 to 8192 Pa
def pressureEvap(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iPressureHigh = calc2sCompliment(baMessage[0], 8)
    iPressureLow  = calc2sCompliment(baMessage[1], 8)
    iPressure = ((iPressureHigh * 256.0) + iPressureLow) / 4.0
    return iPressure * Unit.pascal


# 0 to 327.675 kPa
def pressureEvapAbs(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iPressure = convertBEBytesToInt(baMessage)
    iPressure = iPressure / 200.0
    return iPressure * Unit.kilopascal


# -32767 to 32768 Pa
def pressureEvapAlt(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iPressure = convertBEBytesToInt(baMessage)
    iPressure = iPressure - 32767
    return iPressure * Unit.pascal


# -64 to 63.5 degrees
def timingAdvance(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iTimeAdv = baMessage[0]
    iTimeAdv = (iTimeAdv - 128) / 2.0
    return iTimeAdv * Unit.degree


# -210 to 301 degrees
def timingInject(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iTiming = convertBEBytesToInt(baMessage)
    iTiming = (iTiming - 26880) / 128.0
    return iTiming * Unit.degree


# 0 to 2550 grams/sec
def max_maf(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iMaxMAF = baMessage[0]
    iMaxMAF = iMaxMAF * 10
    return iMaxMAF * Unit.gps


# 0 to 3212 Liters/hour
def getFuelRate(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iFuelRate = convertBEBytesToInt(baMessage)
    iFuelRate = iFuelRate * 0.05
    return iFuelRate * Unit.liters_per_hour


# O2 bit encoding
def getO2Sensors(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    bits = BitArray(baMessage)
    return (
        (),                 # bank 0 is invalid
        tuple(bits[:4]),    # bank 1
        tuple(bits[4:]),    # bank 2
    )

# O2 bit encoding
def getO2SensorsAlt(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    bits = BitArray(baMessage)
    return (
        (),  # bank 0 is invalid
        tuple(bits[:2]),   # bank 1
        tuple(bits[2:4]),  # bank 2
        tuple(bits[4:6]),  # bank 3
        tuple(bits[6:]),   # bank 4
    )


# PTO status
def statusAuxInput(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    return ( (baMessage[0] >> 7) & 1) == 1


# 0 to 25700 %
def getAbsoluteLoad(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iLoad = convertBEBytesToInt(baMessage)
    iLoad *= 100.0 / 255.0
    return iLoad * Unit.percent


def getELMVoltage(listMessages : list[Message]):
    # Not a normal OBD response, so get raw frame data
    strValue = listMessages[0].listFrames[0].strRaw
    # Some ELMs provide float Volts (example: listMessages[0].listFrames[0].strRaw => u'12.3V'
    strValue = strValue.lower()
    strValue = strValue.replace('v', '')

    try:
        return float(strValue) * Unit.volt
    except ValueError:
        logger.warning("Failed to parse ELM voltage")
        return None


'''
Special decoders
Return objects, lists, etc
'''


def getStatus(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    bits = BitArray(baMessage)

    #            ┌Components not ready
    #            |┌Fuel not ready
    #            ||┌Misfire not ready
    #            |||┌Spark vs. Compression
    #            ||||┌Components supported
    #            |||||┌Fuel supported
    #  ┌MIL      ||||||┌Misfire supported
    #  |         |||||||
    #  10000011 00000111 11111111 00000000
    #   [# DTC] X        [supprt] [-ready]

    status = Status()
    status.setValues(bits[0], bits.getIntValue(1, 8), int( bits[(8 + 4)] ) )

    # Load the 3 Base Tests (Component, Fuel, Misfire)...
    for iIndex, strName in enumerate( Codes.Test.Base[::-1] ):
        status.addTest( StatusTest( strName, bits[(8 + 5) + iIndex], not bits[(8 + 1) + iIndex] ) )

    enumIgnition = None
    # If Compression Ignition...
    if bits[12]:
        # Set Compression Tests (reverse for bit to index order)...
        enumIgnition = enumerate(Codes.Test.Compression[::-1])
    # Otherwise, Spark Ignition...
    else:
        # Set Spark Tests (reverse for bit to index order)...
        enumIgnition = enumerate(Codes.Test.Spark[::-1])
    # Load the Ignition Tests...
    for iIndex, strName in enumIgnition:
        status.addTest( StatusTest( strName, bits[(8 * 2) + iIndex], not bits[(8 * 3) + iIndex] ) )

    return status


def getFuelStatus(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    bits = BitArray(baMessage)

    strFuelStatus1 = ""
    strFuelStatus2 = ""

    if bits[0:8].count(True) == 1:
        if 7 - bits[0:8].index(True) < len(Codes.Status.Fuel):
            strFuelStatus1 = Codes.Status.Fuel[7 - bits[0:8].index(True)]
        else:
            logger.debug("Invalid Fuel Status 1st response (high bits set)")
    else:
        logger.debug("Invalid Fuel Status 1st response (multiple/no bits set)")

    if bits[8:16].count(True) == 1:
        if 7 - bits[8:16].index(True) < len(Codes.Status.Fuel):
            strFuelStatus2 = Codes.Status.Fuel[7 - bits[8:16].index(True)]
        else:
            logger.debug("Invalid Fuel Status 2nd response (high bits set)")
    else:
        logger.debug("Invalid Fuel Status 2nd response (multiple/no bits set)")

    if not strFuelStatus1 and not strFuelStatus2:
        return None
    else:
        return (strFuelStatus1, strFuelStatus2)


def getAirStatus(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    bits = BitArray(baMessage)

    strStatus : str = None
    if bits.countSet() == 1:
        strStatus = Codes.Status.Air[7 - bits[0:8].index(True)]
    else:
        logger.debug("Invalid Air Status response (multiple/no bits set)")

    return strStatus


def getOBDCompliance(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iByte = baMessage[0]

    strCompliance : str = None

    if iByte < len(Codes.Compliance):
        strCompliance = Codes.Compliance[iByte]
    else:
        logger.debug("Invalid OBD Compliance response (no entry)")

    return strCompliance


def getFuelType(listMessages : list[Message]):
    baMessage = listMessages[0].baData[2:]
    iByte = baMessage[0]  # TODO: Support 2nd fuel system

    strFuelType = None

    if iByte < len(Codes.FuelType):
        strFuelType = Codes.FuelType[iByte]
    else:
        logger.debug("Invalid Fuel Type response (no entry)")

    return strFuelType


def parseDTCCode(baBytes : bytearray):
    # Convert 2 byte integer into a DTC code

    # Check for valid code (ignore ELM padding)...
    if (len(baBytes) != 2) or (baBytes == (0, 0)):
        return None

    # BYTES: (16,      35      )
    # HEX:    0x41     0x23
    # BIN:    01000001 00100011
    #         [][][  in hex   ]
    #         | | |
    # DTC:    C 0 123

    strDTCCode = ['P', 'C', 'B', 'U'][baBytes[0] >> 6]  # 1st Byte: 2 high bits
    strDTCCode += str((baBytes[0] >> 4) & 0b0011)       # 1st Byte: next 2 lower bits
    strDTCCode += convertByteArrayToHexString(baBytes)[1:4]

    # Get DTC Code Description (or empty string)...
    return ( strDTCCode, Codes.Codes.get(strDTCCode, "") )


def getDTC(listMessages : list[Message]):
    # Convert a response message into a DTC code
    baMessage = listMessages[0].baData[2:]
    return parseDTCCode(baMessage)


def getDTCList(listMessages : list[Message]):
    # Convert a list of response messages into a list of DTC codes
    listCodes : list[tuple[str, str]] = []
    listBAMessage : list[bytearray] = []
    for message in listMessages:
        listBAMessage += message.baData[2:]

    # Process bytes in pairs...
    for iIndex in range(1, len(listBAMessage), 2):
        # Parse the byte pair code...
        tupDTC = parseDTCCode((listBAMessage[iIndex - 1], listBAMessage[iIndex]))

        if tupDTC is not None:
            listCodes.append(tupDTC)

    return listCodes


def parseMonitorTest(baTest : bytearray):
    monitorTest = MonitorTest()

    iTestID = baTest[1]

    if iTestID in MonitorTest.LABELS:
        monitorTest.strName = MonitorTest.LABELS[iTestID][0]
        monitorTest.strDesc = MonitorTest.LABELS[iTestID][1]
    else:
        logger.debug("Unknown Test ID")
        monitorTest.strName = "Unknown"
        monitorTest.strDesc = "Unknown"

    uas = UAS_IDS.get(baTest[2], None)

    # If decode failed...
    if uas is None:
        logger.debug("Unknown Units and Scaling ID")
        return None

    # Store test results...
    monitorTest.iTestID = iTestID
    monitorTest.uasValue = uas(baTest[3:5])  # convert bytes to actual values
    monitorTest.uasMin   = uas(baTest[5:7])
    monitorTest.uasMax   = uas(baTest[7:])

    return monitorTest


def getMonitor(listMessages : list[Message]):
    baMessage = listMessages[0].baData[1:] # ...skip only the mode byte
    # NOTE: Leave the MID byte as it may show up multiple times and make parsing easier.

    monitor = Monitor()

    # Are the number of bytes correct?
    iExtraBytes = len(baMessage) % 9
    if iExtraBytes != 0:
        logger.debug("Monitor message is NOT a 9 byte multiple. Truncating...")
        baMessage = baMessage[:len(baMessage) - iExtraBytes]

    # Process test results (9 bytes blocks)...
    for iIndex in range(0, len(baMessage), 9):
        # Process a 9 byte block and parse a new MonitorTest...
        test = parseMonitorTest( baMessage[iIndex : iIndex + 9] )
        if test is not None:
            monitor.addTest(test)

    return monitor


def decodeMessage(iMinLen : int):
    """ Extract an encoded string from multi-part messages """
    return functools.partial(decodeEncodedMessage, iMinLen=iMinLen)


def decodeEncodedMessage(listMessages : list[Message], iMinLen):
    baMessage = listMessages[0].baData[2:]

    if len(baMessage) < iMinLen:
        logger.debug("Invalid string {}. Discarding...", baMessage)
        return None

    # Encoded strings come in bundles of messages with leading null values to
    # pad out the string to the next full message size. We strip off the
    # leading null characters here and return the resulting string.
    #return baMessage.strip().strip(b'\x00' b'\x01' b'\x02' b'\\x00' b'\\x01' b'\\x02')
    return baMessage.strip().strip(b'\x00' b'\x01' b'\x02')

# Calibration Verification Numbers
def getCVN(listMessages : list[Message]):
    baMessage = decodeEncodedMessage(listMessages, 4)
    if baMessage is None:
        return None
    return convertByteArrayToHexString(baMessage)
