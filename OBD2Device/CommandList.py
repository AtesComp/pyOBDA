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
# CommandList.py   commands                                            #
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

import logging

from .Command import Command
from .Protocols.ECU import ECU
from .decoders import *

logger = logging.getLogger(__name__)


# Class CommandList
#   Assemble the Command List tables by Mode
#   Allow access by 1. Name key and 2. Mode and PID indices

class CommandList(object):

    #
    # Command List Tables
    #
    #   The "Name" field will be used as the key for the sensor
    #   The commands MUST be in PID order--one command per PID--to allow for fast lookup using MODE_#[pid] lookup format
    #   See Command.py for the descriptions and purposes for each of these fields

    # NOTE: See https://en.wikipedia.org/wiki/OBD-II_PIDs

    # Mode 1 returns current Powertrain Diagnostic Data values
    #       Mode 1 is divided into three PID sections: A, B, and C.
    MODE_1 : list[Command] = [
        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU         Fast
        Command("PIDS_A"                        , "Supported PIDs [01-20]"                              , b"0100",     6, pid               , ECU.ENGINE, True ),
        Command("STATUS"                        , "Status since DTCs cleared"                           , b"0101",     6, getStatus         , ECU.ENGINE, True ),
        Command("FREEZE_DTC"                    , "DTC that triggered the freeze frame"                 , b"0102",     4, getDTCSingle      , ECU.ENGINE, True ),
        Command("FUEL_STATUS"                   , "Fuel System Status"                                  , b"0103",     4, getFuelStatus     , ECU.ENGINE, True ),
        Command("ENGINE_LOAD"                   , "Calculated Engine Load"                              , b"0104",     3, percent           , ECU.ENGINE, True ),
        Command("COOLANT_TEMP"                  , "Engine Coolant Temperature"                          , b"0105",     3, temperature       , ECU.ENGINE, True ),
        Command("SHORT_FUEL_TRIM_1"             , "Short Term Fuel Trim - Bank 1"                       , b"0106",     3, percentCentered   , ECU.ENGINE, True ),
        Command("LONG_FUEL_TRIM_1"              , "Long Term Fuel Trim - Bank 1"                        , b"0107",     3, percentCentered   , ECU.ENGINE, True ),
        Command("SHORT_FUEL_TRIM_2"             , "Short Term Fuel Trim - Bank 2"                       , b"0108",     3, percentCentered   , ECU.ENGINE, True ),
        Command("LONG_FUEL_TRIM_2"              , "Long Term Fuel Trim - Bank 2"                        , b"0109",     3, percentCentered   , ECU.ENGINE, True ),
        Command("FUEL_PRESSURE"                 , "Fuel Pressure"                                       , b"010A",     3, pressureFuel      , ECU.ENGINE, True ),
        Command("INTAKE_PRESSURE"               , "Intake Manifold Pressure"                            , b"010B",     3, pressure          , ECU.ENGINE, True ),
        Command("RPM"                           , "Engine RPM"                                          , b"010C",     4, uas(0x07)         , ECU.ENGINE, True ),
        Command("SPEED"                         , "Vehicle Speed"                                       , b"010D",     3, uas(0x09)         , ECU.ENGINE, True ),
        Command("TIMING_ADVANCE"                , "Timing Advance"                                      , b"010E",     3, timingAdvance     , ECU.ENGINE, True ),
        Command("INTAKE_TEMP"                   , "Intake Air Temp"                                     , b"010F",     3, temperature       , ECU.ENGINE, True ),
        Command("MAF"                           , "Mass Air Flow Rate (MAF)"                            , b"0110",     4, uas(0x27)         , ECU.ENGINE, True ),
        Command("THROTTLE_POS"                  , "Throttle Position"                                   , b"0111",     3, percent           , ECU.ENGINE, True ),
        Command("AIR_STATUS"                    , "Secondary Air Status"                                , b"0112",     3, getAirStatus      , ECU.ENGINE, True ),
        Command("O2_SENSORS"                    , "O2 Sensors Present"                                  , b"0113",     3, getO2Sensors      , ECU.ENGINE, True ),
        Command("O2_B1S1"                       , "O2: Bank 1 - Sensor 1 Voltage"                       , b"0114",     4, sensorVoltage     , ECU.ENGINE, True ),
        Command("O2_B1S2"                       , "O2: Bank 1 - Sensor 2 Voltage"                       , b"0115",     4, sensorVoltage     , ECU.ENGINE, True ),
        Command("O2_B1S3"                       , "O2: Bank 1 - Sensor 3 Voltage"                       , b"0116",     4, sensorVoltage     , ECU.ENGINE, True ),
        Command("O2_B1S4"                       , "O2: Bank 1 - Sensor 4 Voltage"                       , b"0117",     4, sensorVoltage     , ECU.ENGINE, True ),
        Command("O2_B2S1"                       , "O2: Bank 2 - Sensor 1 Voltage"                       , b"0118",     4, sensorVoltage     , ECU.ENGINE, True ),
        Command("O2_B2S2"                       , "O2: Bank 2 - Sensor 2 Voltage"                       , b"0119",     4, sensorVoltage     , ECU.ENGINE, True ),
        Command("O2_B2S3"                       , "O2: Bank 2 - Sensor 3 Voltage"                       , b"011A",     4, sensorVoltage     , ECU.ENGINE, True ),
        Command("O2_B2S4"                       , "O2: Bank 2 - Sensor 4 Voltage"                       , b"011B",     4, sensorVoltage     , ECU.ENGINE, True ),
        Command("OBD_COMPLIANCE"                , "OBD Standards Compliance"                            , b"011C",     3, getOBDCompliance  , ECU.ENGINE, True ),
        Command("O2_SENSORS_ALT"                , "O2 Sensors Present (alternate)"                      , b"011D",     3, getO2SensorsAlt   , ECU.ENGINE, True ),
        Command("AUX_INPUT_STATUS"              , "Auxiliary input status (power take off)"             , b"011E",     3, statusAuxInput    , ECU.ENGINE, True ),
        Command("RUN_TIME"                      , "Engine Run Time"                                     , b"011F",     4, uas(0x12)         , ECU.ENGINE, True ),

        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU         Fast
        Command("PIDS_B"                        , "Supported PIDs [21-40]"                              , b"0120",     6, pid               , ECU.ENGINE, True ),
        Command("DISTANCE_W_MIL"                , "Distance Traveled with MIL on"                       , b"0121",     4, uas(0x25)         , ECU.ENGINE, True ),
        Command("FUEL_RAIL_PRESSURE_VAC"        , "Fuel Rail Pressure (relative to vacuum)"             , b"0122",     4, uas(0x19)         , ECU.ENGINE, True ),
        Command("FUEL_RAIL_PRESSURE_DIRECT"     , "Fuel Rail Pressure (direct inject)"                  , b"0123",     4, uas(0x1B)         , ECU.ENGINE, True ),
        Command("O2_S1_WR_VOLTAGE"              , "02 Sensor 1 WR Lambda Voltage"                       , b"0124",     6, sensorVoltageBig  , ECU.ENGINE, True ),
        Command("O2_S2_WR_VOLTAGE"              , "02 Sensor 2 WR Lambda Voltage"                       , b"0125",     6, sensorVoltageBig  , ECU.ENGINE, True ),
        Command("O2_S3_WR_VOLTAGE"              , "02 Sensor 3 WR Lambda Voltage"                       , b"0126",     6, sensorVoltageBig  , ECU.ENGINE, True ),
        Command("O2_S4_WR_VOLTAGE"              , "02 Sensor 4 WR Lambda Voltage"                       , b"0127",     6, sensorVoltageBig  , ECU.ENGINE, True ),
        Command("O2_S5_WR_VOLTAGE"              , "02 Sensor 5 WR Lambda Voltage"                       , b"0128",     6, sensorVoltageBig  , ECU.ENGINE, True ),
        Command("O2_S6_WR_VOLTAGE"              , "02 Sensor 6 WR Lambda Voltage"                       , b"0129",     6, sensorVoltageBig  , ECU.ENGINE, True ),
        Command("O2_S7_WR_VOLTAGE"              , "02 Sensor 7 WR Lambda Voltage"                       , b"012A",     6, sensorVoltageBig  , ECU.ENGINE, True ),
        Command("O2_S8_WR_VOLTAGE"              , "02 Sensor 8 WR Lambda Voltage"                       , b"012B",     6, sensorVoltageBig  , ECU.ENGINE, True ),
        Command("COMMANDED_EGR"                 , "Commanded EGR"                                       , b"012C",     3, percent           , ECU.ENGINE, True ),
        Command("EGR_ERROR"                     , "EGR Error"                                           , b"012D",     3, percentCentered   , ECU.ENGINE, True ),
        Command("EVAPORATIVE_PURGE"             , "Commanded Evaporative Purge"                         , b"012E",     3, percent           , ECU.ENGINE, True ),
        Command("FUEL_LEVEL"                    , "Fuel Level Input"                                    , b"012F",     3, percent           , ECU.ENGINE, True ),
        Command("WARMUPS_SINCE_DTC_CLEAR"       , "Number of warm-ups since codes cleared"              , b"0130",     3, uas(0x01)         , ECU.ENGINE, True ),
        Command("DISTANCE_SINCE_DTC_CLEAR"      , "Distance traveled since codes cleared"               , b"0131",     4, uas(0x25)         , ECU.ENGINE, True ),
        Command("EVAP_VAPOR_PRESSURE"           , "Evaporative system vapor pressure"                   , b"0132",     4, pressureEvap      , ECU.ENGINE, True ),
        Command("BAROMETRIC_PRESSURE"           , "Barometric Pressure"                                 , b"0133",     3, pressure          , ECU.ENGINE, True ),
        Command("O2_S1_WR_CURRENT"              , "02 Sensor 1 WR Lambda Current"                       , b"0134",     6, currentCentered   , ECU.ENGINE, True ),
        Command("O2_S2_WR_CURRENT"              , "02 Sensor 2 WR Lambda Current"                       , b"0135",     6, currentCentered   , ECU.ENGINE, True ),
        Command("O2_S3_WR_CURRENT"              , "02 Sensor 3 WR Lambda Current"                       , b"0136",     6, currentCentered   , ECU.ENGINE, True ),
        Command("O2_S4_WR_CURRENT"              , "02 Sensor 4 WR Lambda Current"                       , b"0137",     6, currentCentered   , ECU.ENGINE, True ),
        Command("O2_S5_WR_CURRENT"              , "02 Sensor 5 WR Lambda Current"                       , b"0138",     6, currentCentered   , ECU.ENGINE, True ),
        Command("O2_S6_WR_CURRENT"              , "02 Sensor 6 WR Lambda Current"                       , b"0139",     6, currentCentered   , ECU.ENGINE, True ),
        Command("O2_S7_WR_CURRENT"              , "02 Sensor 7 WR Lambda Current"                       , b"013A",     6, currentCentered   , ECU.ENGINE, True ),
        Command("O2_S8_WR_CURRENT"              , "02 Sensor 8 WR Lambda Current"                       , b"013B",     6, currentCentered   , ECU.ENGINE, True ),
        Command("CATALYST_TEMP_B1S1"            , "Catalyst Temperature: Bank 1 - Sensor 1"             , b"013C",     4, uas(0x16)         , ECU.ENGINE, True ),
        Command("CATALYST_TEMP_B2S1"            , "Catalyst Temperature: Bank 2 - Sensor 1"             , b"013D",     4, uas(0x16)         , ECU.ENGINE, True ),
        Command("CATALYST_TEMP_B1S2"            , "Catalyst Temperature: Bank 1 - Sensor 2"             , b"013E",     4, uas(0x16)         , ECU.ENGINE, True ),
        Command("CATALYST_TEMP_B2S2"            , "Catalyst Temperature: Bank 2 - Sensor 2"             , b"013F",     4, uas(0x16)         , ECU.ENGINE, True ),

        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU          Fast
        Command("PIDS_C"                        , "Supported PIDs [41-60]"                              , b"0140",     6, pid               , ECU.ENGINE,  True ),
        Command("STATUS_DRIVE_CYCLE"            , "Monitor status this drive cycle"                     , b"0141",     6, getStatus         , ECU.ENGINE, True ),
        Command("CONTROL_MODULE_VOLTAGE"        , "Control module voltage"                              , b"0142",     4, uas(0x0B)         , ECU.ENGINE, True ),
        Command("ABSOLUTE_LOAD"                 , "Absolute load value"                                 , b"0143",     4, getAbsoluteLoad   , ECU.ENGINE, True ),
        Command("COMMANDED_EQUIV_RATIO"         , "Commanded equivalence ratio"                         , b"0144",     4, uas(0x1E)         , ECU.ENGINE, True ),
        Command("RELATIVE_THROTTLE_POS"         , "Relative throttle position"                          , b"0145",     3, percent           , ECU.ENGINE, True ),
        Command("AMBIANT_AIR_TEMP"              , "Ambient air temperature"                             , b"0146",     3, temperature       , ECU.ENGINE, True ),
        Command("THROTTLE_POS_B"                , "Absolute throttle position B"                        , b"0147",     3, percent           , ECU.ENGINE, True ),
        Command("THROTTLE_POS_C"                , "Absolute throttle position C"                        , b"0148",     3, percent           , ECU.ENGINE, True ),
        Command("ACCELERATOR_POS_D"             , "Accelerator pedal position D"                        , b"0149",     3, percent           , ECU.ENGINE, True ),
        Command("ACCELERATOR_POS_E"             , "Accelerator pedal position E"                        , b"014A",     3, percent           , ECU.ENGINE, True ),
        Command("ACCELERATOR_POS_F"             , "Accelerator pedal position F"                        , b"014B",     3, percent           , ECU.ENGINE, True ),
        Command("THROTTLE_ACTUATOR"             , "Commanded throttle actuator"                         , b"014C",     3, percent           , ECU.ENGINE, True ),
        Command("RUN_TIME_MIL"                  , "Time run with MIL on"                                , b"014D",     4, uas(0x34)         , ECU.ENGINE, True ),
        Command("TIME_SINCE_DTC_CLEARED"        , "Time since trouble codes cleared"                    , b"014E",     4, uas(0x34)         , ECU.ENGINE, True ),
        Command("MAX_VALUES_4"                  , "Max Vals: FuelAirEqRatio, O2V&A, In.Man.AbsPressure" , b"014F",     6, drop              , ECU.ENGINE, True ), # TODO: decode this
        Command("MAX_MAF"                       , "Maximum value for Mass Air Flow sensor"              , b"0150",     6, maxMAF            , ECU.ENGINE, True ),
        Command("FUEL_TYPE"                     , "Fuel Type"                                           , b"0151",     3, getFuelType       , ECU.ENGINE, True ),
        Command("ETHANOL_PERCENT"               , "Ethanol Fuel percent"                                , b"0152",     3, percent           , ECU.ENGINE, True ),
        Command("EVAP_VAPOR_PRESSURE_ABS"       , "Evap system absolute vapor pressure"                 , b"0153",     4, pressureEvapAbs   , ECU.ENGINE, True ),
        Command("EVAP_VAPOR_PRESSURE_ALT"       , "Evap system vapor pressure"                          , b"0154",     4, pressureEvapAlt   , ECU.ENGINE, True ),
        Command("SHORT_O2_TRIM_B1"              , "Short term secondary O2 trim - Bank 1"               , b"0155",     4, percentCentered   , ECU.ENGINE, True ), # TODO: decode seconds value for banks 3 and 4
        Command("LONG_O2_TRIM_B1"               , "Long term secondary O2 trim - Bank 1"                , b"0156",     4, percentCentered   , ECU.ENGINE, True ),
        Command("SHORT_O2_TRIM_B2"              , "Short term secondary O2 trim - Bank 2"               , b"0157",     4, percentCentered   , ECU.ENGINE, True ),
        Command("LONG_O2_TRIM_B2"               , "Long term secondary O2 trim - Bank 2"                , b"0158",     4, percentCentered   , ECU.ENGINE, True ),
        Command("FUEL_RAIL_PRESSURE_ABS"        , "Fuel rail absolute pressure"                         , b"0159",     4, uas(0x1B)         , ECU.ENGINE, True ),
        Command("RELATIVE_ACCEL_POS"            , "Relative accelerator pedal position"                 , b"015A",     3, percent           , ECU.ENGINE, True ),
        Command("HYBRID_BATTERY_REMAINING"      , "Hybrid battery pack remaining life"                  , b"015B",     3, percent           , ECU.ENGINE, True ),
        Command("OIL_TEMP"                      , "Engine oil temperature"                              , b"015C",     3, temperature       , ECU.ENGINE, True ),
        Command("FUEL_INJECT_TIMING"            , "Fuel injection timing"                               , b"015D",     4, timingInject      , ECU.ENGINE, True ),
        Command("FUEL_RATE"                     , "Engine fuel rate"                                    , b"015E",     4, getFuelRate       , ECU.ENGINE, True ),
        Command("EMISSION_REQ"                  , "Designed emission requirements"                      , b"015F",     3, drop              , ECU.ENGINE, True ),
    ]

    # Mode 2 is the same as Mode 1, but returns the Freeze Frame values for the Powertrain Diagnostic Data at the time the frame was set
    MODE_2 : list[Command] = []
    for cmd in MODE_1:
        cmd = cmd.clone()
        cmd.bsCmdID = b"02" + cmd.bsCmdID[2:]  # ...change the Mode: 0100 --> 0200
        cmd.strName = "FF_" + cmd.strName
        cmd.strDesc = "FF " + cmd.strDesc
        if cmd.funcDecoder == pid:
            cmd.funcDecoder = drop  # ...never send Mode 2 PID requests--use Mode 1 instead
        MODE_2.append(cmd)

    # Mode 3 contains a single command to get the Diagnostic Trouble Code (DTC) list
    MODE_3 : list[Command] = [
        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU          Fast
        Command("GET_DTC"                       , "Get DTCs"                                            , b"03"  ,     0, getDTCList        , ECU.ALL,     False),
    ]

    # Mode 4 contains a single command to clear and reset the system:
    #       1. clear the Diagnostic Trouble Code (DTC) list,
    #       2, clear the Freeze Frame data,
    #       3, clear all stored test data,
    #       4. resets all monitors, and
    #       5. turn the Check Engine Light off
    MODE_4 : list[Command] = [
        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU          Fast
        Command("CLEAR_DTC"                     , "Clear / Reset: DTCs, FF, tests, monitors, CEL"       , b"04",       0, drop              , ECU.ALL,     False),
    ]

    # Mode 5 is the Oxygen Sensor Monitoring Test results
    #       This information is not available on vehicles using the Controller Area Network (CAN) system.
    #       For CAN systems, use Mode 6.
    MODE_5 : list[Command] = []

    # Mode 6 is the On-board Monitoring Test results for specific monitored systems
    #       Mode 6 documents the PID as MID (Monitor ID).
    #       These are CAN only commands.
    MODE_6 : list[Command] = [
        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU          Fast
        Command("MIDS_A"                        , "Supported MIDs [01-20]"                              , b"0600",     0, pid               , ECU.ALL,     False),
        Command("MONITOR_O2_B1S1"               , "O2 Sensor Monitor Bank 1 - Sensor 1"                 , b"0601",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B1S2"               , "O2 Sensor Monitor Bank 1 - Sensor 2"                 , b"0602",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B1S3"               , "O2 Sensor Monitor Bank 1 - Sensor 3"                 , b"0603",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B1S4"               , "O2 Sensor Monitor Bank 1 - Sensor 4"                 , b"0604",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B2S1"               , "O2 Sensor Monitor Bank 2 - Sensor 1"                 , b"0605",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B2S2"               , "O2 Sensor Monitor Bank 2 - Sensor 2"                 , b"0606",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B2S3"               , "O2 Sensor Monitor Bank 2 - Sensor 3"                 , b"0607",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B2S4"               , "O2 Sensor Monitor Bank 2 - Sensor 4"                 , b"0608",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B3S1"               , "O2 Sensor Monitor Bank 3 - Sensor 1"                 , b"0609",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B3S2"               , "O2 Sensor Monitor Bank 3 - Sensor 2"                 , b"060A",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B3S3"               , "O2 Sensor Monitor Bank 3 - Sensor 3"                 , b"060B",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B3S4"               , "O2 Sensor Monitor Bank 3 - Sensor 4"                 , b"060C",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B4S1"               , "O2 Sensor Monitor Bank 4 - Sensor 1"                 , b"060D",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B4S2"               , "O2 Sensor Monitor Bank 4 - Sensor 2"                 , b"060E",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B4S3"               , "O2 Sensor Monitor Bank 4 - Sensor 3"                 , b"060F",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_B4S4"               , "O2 Sensor Monitor Bank 4 - Sensor 4"                 , b"0610",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 15) + [ # 11 - 1F Reserved
        Command("MIDS_B"                        , "Supported MIDs [21-40]"                              , b"0620",     0, pid               , ECU.ALL,     False),
        Command("MONITOR_CATALYST_B1"           , "Catalyst Monitor Bank 1"                             , b"0621",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_CATALYST_B2"           , "Catalyst Monitor Bank 2"                             , b"0622",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_CATALYST_B3"           , "Catalyst Monitor Bank 3"                             , b"0623",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_CATALYST_B4"           , "Catalyst Monitor Bank 4"                             , b"0624",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 12) + [ # 25 - 30 Reserved
        Command("MONITOR_EGR_B1"                , "EGR Monitor Bank 1"                                  , b"0631",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_EGR_B2"                , "EGR Monitor Bank 2"                                  , b"0632",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_EGR_B3"                , "EGR Monitor Bank 3"                                  , b"0633",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_EGR_B4"                , "EGR Monitor Bank 4"                                  , b"0634",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_VVT_B1"                , "VVT Monitor Bank 1"                                  , b"0635",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_VVT_B2"                , "VVT Monitor Bank 2"                                  , b"0636",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_VVT_B3"                , "VVT Monitor Bank 3"                                  , b"0637",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_VVT_B4"                , "VVT Monitor Bank 4"                                  , b"0638",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_EVAP_150"              , "EVAP Monitor (Cap Off / 0.150\")"                    , b"0639",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_EVAP_090"              , "EVAP Monitor (0.090\")"                              , b"063A",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_EVAP_040"              , "EVAP Monitor (0.040\")"                              , b"063B",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_EVAP_020"              , "EVAP Monitor (0.020\")"                              , b"063C",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_PURGE_FLOW"            , "Purge Flow Monitor"                                  , b"063D",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 2) + [ # 3E - 3F Reserved
        Command("MIDS_C"                        , "Supported MIDs [41-60]"                              , b"0640",     0, pid               , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B1S1"        , "O2 Sensor Heater Monitor Bank 1 - Sensor 1"          , b"0641",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B1S2"        , "O2 Sensor Heater Monitor Bank 1 - Sensor 2"          , b"0642",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B1S3"        , "O2 Sensor Heater Monitor Bank 1 - Sensor 3"          , b"0643",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B1S4"        , "O2 Sensor Heater Monitor Bank 1 - Sensor 4"          , b"0644",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B2S1"        , "O2 Sensor Heater Monitor Bank 2 - Sensor 1"          , b"0645",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B2S2"        , "O2 Sensor Heater Monitor Bank 2 - Sensor 2"          , b"0646",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B2S3"        , "O2 Sensor Heater Monitor Bank 2 - Sensor 3"          , b"0647",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B2S4"        , "O2 Sensor Heater Monitor Bank 2 - Sensor 4"          , b"0648",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B3S1"        , "O2 Sensor Heater Monitor Bank 3 - Sensor 1"          , b"0649",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B3S2"        , "O2 Sensor Heater Monitor Bank 3 - Sensor 2"          , b"064A",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B3S3"        , "O2 Sensor Heater Monitor Bank 3 - Sensor 3"          , b"064B",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B3S4"        , "O2 Sensor Heater Monitor Bank 3 - Sensor 4"          , b"064C",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B4S1"        , "O2 Sensor Heater Monitor Bank 4 - Sensor 1"          , b"064D",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B4S2"        , "O2 Sensor Heater Monitor Bank 4 - Sensor 2"          , b"064E",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B4S3"        , "O2 Sensor Heater Monitor Bank 4 - Sensor 3"          , b"064F",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_O2_HEATER_B4S4"        , "O2 Sensor Heater Monitor Bank 4 - Sensor 4"          , b"0650",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 15) + [ # 51 - 5F Reserved
        Command("MIDS_D"                        , "Supported MIDs [61-80]"                              , b"0660",     0, pid               , ECU.ALL,     False),
        Command("MONITOR_HEATED_CATALYST_B1"    , "Heated Catalyst Monitor Bank 1"                      , b"0661",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_HEATED_CATALYST_B2"    , "Heated Catalyst Monitor Bank 2"                      , b"0662",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_HEATED_CATALYST_B3"    , "Heated Catalyst Monitor Bank 3"                      , b"0663",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_HEATED_CATALYST_B4"    , "Heated Catalyst Monitor Bank 4"                      , b"0664",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 12) + [ # 65 - 70 Reserved
        Command("MONITOR_SECONDARY_AIR_1"       , "Secondary Air Monitor 1"                             , b"0671",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_SECONDARY_AIR_2"       , "Secondary Air Monitor 2"                             , b"0672",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_SECONDARY_AIR_3"       , "Secondary Air Monitor 3"                             , b"0673",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_SECONDARY_AIR_4"       , "Secondary Air Monitor 4"                             , b"0674",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 11) + [ # 75 - 7F Reserved
        Command("MIDS_E"                        , "Supported MIDs [81-A0]"                              , b"0680",     0, pid               , ECU.ALL,     False),
        Command("MONITOR_FUEL_SYSTEM_B1"        , "Fuel System Monitor Bank 1"                          , b"0681",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_FUEL_SYSTEM_B2"        , "Fuel System Monitor Bank 2"                          , b"0682",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_FUEL_SYSTEM_B3"        , "Fuel System Monitor Bank 3"                          , b"0683",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_FUEL_SYSTEM_B4"        , "Fuel System Monitor Bank 4"                          , b"0684",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_BOOST_PRESSURE_B1"     , "Boost Pressure Control Monitor Bank 1"               , b"0685",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_BOOST_PRESSURE_B2"     , "Boost Pressure Control Monitor Bank 1"               , b"0686",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 9) + [ # 87 - 8F Reserved
        Command("MONITOR_NOX_ABSORBER_B1"       , "NOx Absorber Monitor Bank 1"                         , b"0690",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_NOX_ABSORBER_B2"       , "NOx Absorber Monitor Bank 2"                         , b"0691",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 6) + [ # 92 - 97 Reserved
        Command("MONITOR_NOX_CATALYST_B1"       , "NOx Catalyst Monitor Bank 1"                         , b"0698",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_NOX_CATALYST_B2"       , "NOx Catalyst Monitor Bank 2"                         , b"0699",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 6) + [ # 9A - 9F Reserved
        Command("MIDS_F"                        , "Supported MIDs [A1-C0]"                              , b"06A0",     0, pid               , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_GENERAL"       , "Misfire Monitor General Data"                        , b"06A1",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_1"    , "Misfire Cylinder 1 Data"                             , b"06A2",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_2"    , "Misfire Cylinder 2 Data"                             , b"06A3",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_3"    , "Misfire Cylinder 3 Data"                             , b"06A4",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_4"    , "Misfire Cylinder 4 Data"                             , b"06A5",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_5"    , "Misfire Cylinder 5 Data"                             , b"06A6",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_6"    , "Misfire Cylinder 6 Data"                             , b"06A7",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_7"    , "Misfire Cylinder 7 Data"                             , b"06A8",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_8"    , "Misfire Cylinder 8 Data"                             , b"06A9",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_9"    , "Misfire Cylinder 9 Data"                             , b"06AA",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_10"   , "Misfire Cylinder 10 Data"                            , b"06AB",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_11"   , "Misfire Cylinder 11 Data"                            , b"06AC",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_MISFIRE_CYLINDER_12"   , "Misfire Cylinder 12 Data"                            , b"06AD",     0, getMonitor        , ECU.ALL,     False),
    ] + ([] * 2) + [ # AE - AF Reserved
        Command("MONITOR_PM_FILTER_B1"          , "PM Filter Monitor Bank 1"                            , b"06B0",     0, getMonitor        , ECU.ALL,     False),
        Command("MONITOR_PM_FILTER_B2"          , "PM Filter Monitor Bank 2"                            , b"06B1",     0, getMonitor        , ECU.ALL,     False),
    ]

    # Mode 7 contains a single command to get the DTCs for the current or last completed driving cycle
    #       These are the emission-related DTC "Pending Codes" detected after an ECM reset.
    MODE_7 : list[Command] = [
        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU          Fast
        Command("GET_CURRENT_DTC"               , "Get DTCs from the current / last driving cycle"      , b"07"  ,     0, getDTCList        , ECU.ALL,     False),
    ]

    # Mode 8 allows the bidirectional control of an On-board system, test or component.
    #       Typically, control limited to some evaporative emissions systems and allows the user to seal the system for leak testing.
    MODE_8 : list[Command] = []

    # Mode 9 gets the Vehicle Information
    #       This allows access to the Vehicle Identification Number (VIN) and Calibration Verification Numbers (CVN) from all emissions-related electronic modules.
    MODE_9 : list[Command] = [
        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU          Fast
        Command("PIDS_9A"                       , "Supported PIDs [01-20]"                              , b"0900",     7, pid               , ECU.ALL,     True ),
        Command("VIN_MESSAGE_COUNT"             , "VIN Message Count"                                   , b"0901",     3, count             , ECU.ENGINE,  True ),
        Command("VIN"                           , "Vehicle Identification Number"                       , b"0902",    22, decodeMessage(17) , ECU.ENGINE,  True ),
        Command("CALIBRATION_ID_MESSAGE_COUNT"  , "CID Message Count"                                   , b"0903",     3, count             , ECU.ALL,     True ),
        Command("CALIBRATION_ID"                , "Calibration ID (CID)"                                , b"0904",    18, decodeMessage(16) , ECU.ALL,     True ),
        Command("CVN_MESSAGE_COUNT"             , "CVN Message Count"                                   , b"0905",     3, count             , ECU.ALL,     True ),
        Command("CVN"                           , "Calibration Verification Numbers (CVN)"              , b"0906",    10, getCVN            , ECU.ALL,     True ),

    # NOTE: The following Mode 9 commands are untested
    #    #        Name                              Description                                              CmdID  Bytes  Decoder             ECU          Fast
    #    Command("PERF_TRACKING_MESSAGE_COUNT"   , "Performance Tracking Message Count"                  , b"0907",     3, count             , ECU.ALL,     True ),
    #    Command("PERF_TRACKING_SPARK"           , "In-use Performance Tracking: Spark Ignition"         , b"0908",     4, raw_string        , ECU.ALL,     True ),
    #    Command("ECU_NAME_MESSAGE_COUNT"        , "ECU Name Message Count"                              , b"0909",     3, count             , ECU.ALL,     True ),
    #    Command("ECU_NAME"                      , "ECU Name"                                            , b"090A",    20, raw_string        , ECU.ALL,     True ),
    #    Command("PERF_TRACKING_COMPRESSION"     , "In-use Performance Tracking: Compression Ignition"   , b"090B",     4, raw_string        , ECU.ALL,     True ),
    ]

    # Mode 10 is the emissions-related DTCs with permanent status after a clear / reset emission-related diagnostic information service
    #       This reports DTCs that are stored as "permanent codes" and are codes only the module can clear.
    #       Even if you’ve made a successful repair and have cleared the codes using Mode 4, these codes will remain in memory until the computer has completed
    #       its own system test.
    MODE_10 : list[Command] = []

    # Miscellanious ELM commands
    MISC : list[Command] = [
        #        Name                              Description                                              CmdID  Bytes  Decoder             ECU          Fast
        Command("ELM_VERSION"                   , "ELM327 Version Information"                          , b"ATI" ,     0, raw_string        , ECU.UNKNOWN, False),
        Command("ELM_VOLTAGE"                   , "ELM327 Detected Voltage"                             , b"ATRV",     0, getELMVoltage     , ECU.UNKNOWN, False),
    ]

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CommandList, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        # Set up command access by Mode and PID index...
        self.modes : list[list[Command|None]] = [
            [],
            CommandList.MODE_1,
            CommandList.MODE_2,
            CommandList.MODE_3,
            CommandList.MODE_4,
            [],
            CommandList.MODE_6,
            CommandList.MODE_7,
            [],
            CommandList.MODE_9,
        ]

        # Set up command access by Name key...
        for listMode in self.modes:
            for command in listMode:
                if command is not None:
                    self.__dict__[command.strName] = command

        for command in CommandList.MISC:
            if command is not None:
                self.__dict__[command.strName] = command

    # OVERRIDE class builtin __getitem__ method
    def __getitem__(self, key):
        # NOTE: The Commands in the Command List can be accessed by Name or by Mode and PID
        #       CMDS = CommandList()
        #       CMDS.RPM    <-- Name key
        #       CMDS["RPM"] <-- Name index
        #       CMDS[1][12] <-- Mode 1, PID 12 (RPM) indices

        if isinstance(key, int):
            return self.modes[key]
        elif isinstance(key, str):
            return self.__dict__[key]
        else:
            logger.warning("OBD commands can only be retrieved by Mode and PID index or by Name key")

    # OVERRIDE class builtin __len__ method
    def __len__(self):
        # Count the number of commands supported...
        return sum( [ len(listMode) for listMode in self.modes ] )

    # OVERRIDE class builtin __contains__ method...
    def __contains__(self, strName):
        # Find the Command containing the Name...
        return self.hasCmdName(strName)

    def getBaseCmds(self):
        # List the standard ELM327 supported commands...
        return [
            # 0100
            self.PIDS_A,
            self.PIDS_B,
            self.PIDS_C,
            #0200
            #   Freeze Frame: Use the 0100 PIDS
            # 03
            self.GET_DTC,
            # 04
            self.CLEAR_DTC,
            # 0600
            self.MIDS_A,
            self.MIDS_B,
            self.MIDS_C,
            self.MIDS_D,
            self.MIDS_E,
            self.MIDS_F,
            # 07
            self.GET_CURRENT_DTC,
            # 0900
            self.PIDS_9A,
            # MISC
            self.ELM_VERSION,
            self.ELM_VOLTAGE,
        ]

    def getPIDCmds(self) -> list[Command]:
        # Return a list of PID GET commands
        listPIDCommands : list[Command] = []
        for listMode in self.modes:
            listPIDCommands += [
                command for command in listMode if (
                    command and type(command) == Command and command.funcDecoder == pid
                )
            ]
        return listPIDCommands

    def hasCmd(self, command : Command):
        # Does command exist by Command object
        return True if command and command in self.__dict__.values() else False

    def hasCmdName(self, strName : str):
        # Does command exist by name?
        return strName.isupper() and strName in self.__dict__ and isinstance(self.__dict__[strName], Command)

    def hasPID(self, iMode : int, iPID : int):
        # Does command exist in Mode by PID?
        if (iMode < 0) or (iPID < 0):
            return False
        if iMode >= len(self.modes):
            return False
        if iPID >= len(self.modes[iMode]):
            return False

        # Check for reserved command...
        return self.modes[iMode][iPID] is not None
