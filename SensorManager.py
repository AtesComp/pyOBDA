############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# SensorManager.py
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

from Sensor import Sensor

from OBD2Device.CommandList import CommandList

class SensorManager:
    CMDS = CommandList()

    SENSOR_GROUP_A = 0
    SENSOR_GROUP_B = 2
    SENSOR_GROUP_C = 3

    # NOTE: See https://en.wikipedia.org/wiki/OBD-II_PIDs
    SENSORS = [
    #
    # PID_A Commands...
    #
    [
        Sensor("    Supported PIDs [01-20]", CMDS.PIDS_A, ""),                          # 00  bitarray
        Sensor("    Status Since Clear DTC", CMDS.STATUS, ""),                          # 01  special
        Sensor("          Freeze Frame DTC", CMDS.FREEZE_DTC, ""),                      # 02  special
        Sensor("        Fuel System Status", CMDS.FUEL_STATUS, ""),                     # 03  (1st sys str, 2nd sys str)
        Sensor(" Calc'ed Engine Load Value", CMDS.ENGINE_LOAD, "%"),                    # 04  percent
        Sensor("       Coolant Temperature", CMDS.COOLANT_TEMP, "degC"),                # 05  degC, degF
        Sensor("    Short Term Fuel Trim 1", CMDS.SHORT_FUEL_TRIM_1, "%"),              # 06  percent
        Sensor("     Long Term Fuel Trim 1", CMDS.LONG_FUEL_TRIM_1, "%"),               # 07  percent
        Sensor("    Short Term Fuel Trim 2", CMDS.SHORT_FUEL_TRIM_2, "%"),              # 08  percent
        Sensor("     Long Term Fuel Trim 2", CMDS.LONG_FUEL_TRIM_2, "%"),               # 09  percent
        Sensor("             Fuel Pressure", CMDS.FUEL_PRESSURE, "kPa"),                # 0A  kilopascal, psi
        Sensor("  Intake Manifold Pressure", CMDS.INTAKE_PRESSURE, "kPa"),              # 0B  kilopascal, psi
        Sensor("                Engine RPM", CMDS.RPM, "rpm"),                          # 0C  rpm
        Sensor("             Vehicle Speed", CMDS.SPEED, "kph"),                        # 0D  kph, mph
        Sensor("            Timing Advance", CMDS.TIMING_ADVANCE, "degree"),            # 0E  degree
        Sensor("    Intake Air Temperature", CMDS.INTAKE_TEMP, "degC"),                 # 0F  degC, degF
        Sensor("  Mass Air Flow Rate (MAF)", CMDS.MAF, "gps"),                          # 10  gps (grams/sec), lb/min
        Sensor("         Throttle Position", CMDS.THROTTLE_POS, "%"),                   # 11  percent
        Sensor("      Secondary Air Status", CMDS.AIR_STATUS, ""),                      # 12  str
        Sensor("        O2 Sensors Present", CMDS.O2_SENSORS, ""),                      # 13  special
        Sensor("          O2 Sensor: 1 - 1", CMDS.O2_B1S1, "volt"),                     # 14  volt
        Sensor("          O2 Sensor: 1 - 2", CMDS.O2_B1S2, "volt"),                     # 15  volt
        Sensor("          O2 Sensor: 1 - 3", CMDS.O2_B1S3, "volt"),                     # 16  volt
        Sensor("          O2 Sensor: 1 - 4", CMDS.O2_B1S4, "volt"),                     # 17  volt
        Sensor("          O2 Sensor: 2 - 1", CMDS.O2_B2S1, "volt"),                     # 18  volt
        Sensor("          O2 Sensor: 2 - 2", CMDS.O2_B2S2, "volt"),                     # 19  volt
        Sensor("          O2 Sensor: 2 - 3", CMDS.O2_B2S3, "volt"),                     # 1A  volt
        Sensor("          O2 Sensor: 2 - 4", CMDS.O2_B2S4, "volt"),                     # 1B  volt
        Sensor("            OBD Compliance", CMDS.OBD_COMPLIANCE, ""),                  # 1C  str
        Sensor("    Alt O2 Sensors Present", CMDS.O2_SENSORS_ALT, ""),                  # 1D  special
        Sensor("     Auxilary Input Status", CMDS.AUX_INPUT_STATUS, ""),                # 1E  boolean
        Sensor("           Engine Run Time", CMDS.RUN_TIME, "sec"),                     # 1F  sec, min
    ],
    #
    # PID_B Commands...
    #
    [
        Sensor("    Supported PIDs [21-40]", CMDS.PIDS_B, ""),                          # 20  bitarray
        Sensor("      Distance with MIL ON", CMDS.DISTANCE_W_MIL, "kilo"),              # 21  kilometer, miles
        Sensor("  Fuel Rail Pressure (vac)", CMDS.FUEL_RAIL_PRESSURE_VAC, "kph"),       # 22  kilopascal, psi
        Sensor("  Fuel Rail Pressure (dir)", CMDS.FUEL_RAIL_PRESSURE_DIRECT, "kph"),    # 23  kilopascal, psi
        Sensor("O2 Sensor 1 WR Lambda Volt", CMDS.O2_S1_WR_VOLTAGE, "volt"),            # 24  volt
        Sensor("O2 Sensor 2 WR Lambda Volt", CMDS.O2_S2_WR_VOLTAGE, "volt"),            # 25  volt
        Sensor("O2 Sensor 3 WR Lambda Volt", CMDS.O2_S3_WR_VOLTAGE, "volt"),            # 26  volt
        Sensor("O2 Sensor 4 WR Lambda Volt", CMDS.O2_S4_WR_VOLTAGE, "volt"),            # 27  volt
        Sensor("O2 Sensor 5 WR Lambda Volt", CMDS.O2_S5_WR_VOLTAGE, "volt"),            # 28  volt
        Sensor("O2 Sensor 6 WR Lambda Volt", CMDS.O2_S6_WR_VOLTAGE, "volt"),            # 29  volt
        Sensor("O2 Sensor 7 WR Lambda Volt", CMDS.O2_S7_WR_VOLTAGE, "volt"),            # 2A  volt
        Sensor("O2 Sensor 8 WR Lambda Volt", CMDS.O2_S8_WR_VOLTAGE, "volt"),            # 2B  volt
        Sensor("             Commanded EGR", CMDS.COMMANDED_EGR, "%"),                  # 2C  percent
        Sensor("                 EGR Error", CMDS.EGR_ERROR, "%"),                      # 2D  percent
        Sensor("  Cmnded Evaporative Purge", CMDS.EVAPORATIVE_PURGE, "%"),              # 2E  percent
        Sensor("          Fuel Level Input", CMDS.FUEL_LEVEL, "%"),                     # 2F  percent
        Sensor("# Warm-ups Since Clear DTC", CMDS.WARMUPS_SINCE_DTC_CLEAR, ""),         # 30  count
        Sensor("  Distance Since Clear DTC", CMDS.DISTANCE_SINCE_DTC_CLEAR, "kilo"),    # 31  kilometer, mile
        Sensor("   Evap Sys Vapor Pressure", CMDS.EVAP_VAPOR_PRESSURE, "kPa"),          # 32  kilopascal, psi
        Sensor("       Barometric Pressure", CMDS.BAROMETRIC_PRESSURE, "kPa"),          # 33  kilopascal, psi
        Sensor("O2 Sensor 1 WR Lambda Curr", CMDS.O2_S1_WR_CURRENT, "mA"),              # 34  milliampere
        Sensor("O2 Sensor 2 WR Lambda Curr", CMDS.O2_S2_WR_CURRENT, "mA"),              # 35  milliampere
        Sensor("O2 Sensor 3 WR Lambda Curr", CMDS.O2_S3_WR_CURRENT, "mA"),              # 36  milliampere
        Sensor("O2 Sensor 4 WR Lambda Curr", CMDS.O2_S4_WR_CURRENT, "mA"),              # 37  milliampere
        Sensor("O2 Sensor 5 WR Lambda Curr", CMDS.O2_S5_WR_CURRENT, "mA"),              # 38  milliampere
        Sensor("O2 Sensor 6 WR Lambda Curr", CMDS.O2_S6_WR_CURRENT, "mA"),              # 39  milliampere
        Sensor("O2 Sensor 7 WR Lambda Curr", CMDS.O2_S7_WR_CURRENT, "mA"),              # 3A  milliampere
        Sensor("O2 Sensor 8 WR Lambda Curr", CMDS.O2_S8_WR_CURRENT, "mA"),              # 3B  milliampere
        Sensor(" Cat Temp: Bank 1 Sensor 1", CMDS.CATALYST_TEMP_B1S1, "degC"),          # 3C  degC, degF
        Sensor(" Cat Temp: Bank 2 Sensor 1", CMDS.CATALYST_TEMP_B2S1, "degC"),          # 3D  degC, degF
        Sensor(" Cat Temp: Bank 1 Sensor 2", CMDS.CATALYST_TEMP_B1S2, "degC"),          # 3E  degC, degF
        Sensor(" Cat Temp: Bank 2 Sensor 2", CMDS.CATALYST_TEMP_B2S2, "degC"),          # 3F  degC, degF
    ],
    #
    # PID_C Commands...
    #
    [
        Sensor("    Supported PIDs [41-60]", CMDS.PIDS_C, ""),                          # 40  bitarray
        Sensor("Monitor Status Drive Cycle", CMDS.STATUS_DRIVE_CYCLE, ""),              # 41  special
        Sensor("    Control Module Voltage", CMDS.CONTROL_MODULE_VOLTAGE, "volt"),      # 42  volt
        Sensor("       Absolute Load Value", CMDS.ABSOLUTE_LOAD, "%"),                  # 43  percent
        Sensor("     Commanded Equiv Ratio", CMDS.COMMANDED_EQUIV_RATIO, "ratio"),      # 44  ratio
        Sensor("Relative Throttle Position", CMDS.RELATIVE_THROTTLE_POS, "%"),          # 45  percent
        Sensor("   Ambient Air Temperature", CMDS.AMBIANT_AIR_TEMP, "degC"),            # 46  degC, degF
        Sensor("   Abs Throttle Position B", CMDS.THROTTLE_POS_B, "%"),                 # 47  percent
        Sensor("   Abs Throttle Position C", CMDS.THROTTLE_POS_C, "%"),                 # 48  percent
        Sensor("    Accel Pedal Position D", CMDS.ACCELERATOR_POS_D, "%"),              # 49  percent
        Sensor("    Accel Pedal Position E", CMDS.ACCELERATOR_POS_E, "%"),              # 4A  percent
        Sensor("    Accel Pedal Position F", CMDS.ACCELERATOR_POS_F, "%"),              # 4B  percent
        Sensor(" Comnded Throttle Actuator", CMDS.THROTTLE_ACTUATOR, "%"),              # 4C  percent
        Sensor("          Time with MIL ON", CMDS.RUN_TIME_MIL, "sec"),                 # 4D  sec, min
        Sensor("    Time Since DTC Cleared", CMDS.TIME_SINCE_DTC_CLEARED, "sec"),       # 4E  sec, min
        Sensor("     4 Systems: Max Values", CMDS.MAX_VALUES_4, ""),                    # 4F  bytes: ratio, V, mA, kPa
        Sensor("  Mass Air Flow: Max Value", CMDS.MAX_MAF, "gps"),                      # 50  gps (grams/sec), lb/min
        Sensor("                 Fuel Type", CMDS.FUEL_TYPE, ""),                       # 51  str
        Sensor("      Ethanol Fuel Percent", CMDS.ETHANOL_PERCENT, "%"),                # 52  percent
        Sensor("Abs EvapSys Vapor Pressure", CMDS.EVAP_VAPOR_PRESSURE_ABS, "kPa"),      # 53  kilopascal
        Sensor("Alt EvapSys Vapor Pressure", CMDS.EVAP_VAPOR_PRESSURE_ALT, "kPa"),      # 54  kilopascal
        Sensor(" Short Term 2nd O2 Trim B1", CMDS.SHORT_O2_TRIM_B1, "%"),               # 55  percent
        Sensor("  Long Term 2nd O2 Trim B1", CMDS.LONG_O2_TRIM_B1, "%"),                # 56  percent
        Sensor(" Short Term 2nd O2 Trim B2", CMDS.SHORT_O2_TRIM_B2, "%"),               # 57  percent
        Sensor("  Long Term 2nd O2 Trim B2", CMDS.LONG_O2_TRIM_B2, "%"),                # 58  percent
        Sensor("  Fuel Rail Pressure (abs)", CMDS.FUEL_RAIL_PRESSURE_ABS, "kPa"),       # 59  kilopascal
        Sensor("  Rel Accel Pedal Position", CMDS.RELATIVE_ACCEL_POS, "%"),             # 5A  percent
        Sensor("      Hybrid Battery: Life", CMDS.HYBRID_BATTERY_REMAINING, "%"),       # 5B  percent
        Sensor("    Engine Oil Temperature", CMDS.OIL_TEMP, "degC"),                    # 5C  degC, degF
        Sensor("     Fuel Injection Timing", CMDS.FUEL_INJECT_TIMING, "degree"),        # 5D  degree
        Sensor("          Engine Fuel Rate", CMDS.FUEL_RATE, "lph"),                    # 5E  liters/hour, gallons/hour
        Sensor("     Vehicle Emission Reqs", CMDS.EMISSION_REQ, ""),                    # 5F  unknown, Bit Encoded
    ]
    #
    # ...END SENSORS
    #
    ]

