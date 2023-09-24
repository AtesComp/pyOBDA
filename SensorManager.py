############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# SensorManager.py
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

from Sensor import Sensor

from OBD2Device.CommandList import CommandListObj

class SensorManager:
    SENSOR_GROUP_A = 0
    SENSOR_GROUP_B = 2
    SENSOR_GROUP_C = 3

    SENSORS = [
    #
    # PID_A Commands...
    #
    [
        Sensor("    Supported PIDs [01-20]", CommandListObj.PIDS_A, ""),                          # 00  bitarray
        Sensor("    Status Since Clear DTC", CommandListObj.STATUS, ""),                          # 01  special
        Sensor("          Freeze Frame DTC", CommandListObj.FREEZE_DTC, ""),                      # 02  special
        Sensor("        Fuel System Status", CommandListObj.FUEL_STATUS, ""),                     # 03  (1st sys str, 2nd sys str)
        Sensor(" Calc'ed Engine Load Value", CommandListObj.ENGINE_LOAD, "%"),                    # 04  percent
        Sensor("       Coolant Temperature", CommandListObj.COOLANT_TEMP, "degC"),                # 05  degC, degF
        Sensor("    Short Term Fuel Trim 1", CommandListObj.SHORT_FUEL_TRIM_1, "%"),              # 06  percent
        Sensor("     Long Term Fuel Trim 1", CommandListObj.LONG_FUEL_TRIM_1, "%"),               # 07  percent
        Sensor("    Short Term Fuel Trim 2", CommandListObj.SHORT_FUEL_TRIM_2, "%"),              # 08  percent
        Sensor("     Long Term Fuel Trim 2", CommandListObj.LONG_FUEL_TRIM_2, "%"),               # 09  percent
        Sensor("             Fuel Pressure", CommandListObj.FUEL_PRESSURE, "kPa"),                # 0A  kilopascal, psi
        Sensor("  Intake Manifold Pressure", CommandListObj.INTAKE_PRESSURE, "kPa"),              # 0B  kilopascal, psi
        Sensor("                Engine RPM", CommandListObj.RPM, "rpm"),                          # 0C  rpm
        Sensor("             Vehicle Speed", CommandListObj.SPEED, "kph"),                        # 0D  kph, mph
        Sensor("            Timing Advance", CommandListObj.TIMING_ADVANCE, "degree"),            # 0E  degree
        Sensor("    Intake Air Temperature", CommandListObj.INTAKE_TEMP, "degC"),                 # 0F  degC, degF
        Sensor("  Mass Air Flow Rate (MAF)", CommandListObj.MAF, "gps"),                          # 10  gps (grams/sec), lb/min
        Sensor("         Throttle Position", CommandListObj.THROTTLE_POS, "%"),                   # 11  percent
        Sensor("      Secondary Air Status", CommandListObj.AIR_STATUS, ""),                      # 12  str
        Sensor("        O2 Sensors Present", CommandListObj.O2_SENSORS, ""),                      # 13  special
        Sensor("          O2 Sensor: 1 - 1", CommandListObj.O2_B1S1, "volt"),                     # 14  volt
        Sensor("          O2 Sensor: 1 - 2", CommandListObj.O2_B1S2, "volt"),                     # 15  volt
        Sensor("          O2 Sensor: 1 - 3", CommandListObj.O2_B1S3, "volt"),                     # 16  volt
        Sensor("          O2 Sensor: 1 - 4", CommandListObj.O2_B1S4, "volt"),                     # 17  volt
        Sensor("          O2 Sensor: 2 - 1", CommandListObj.O2_B2S1, "volt"),                     # 18  volt
        Sensor("          O2 Sensor: 2 - 2", CommandListObj.O2_B2S2, "volt"),                     # 19  volt
        Sensor("          O2 Sensor: 2 - 3", CommandListObj.O2_B2S3, "volt"),                     # 1A  volt
        Sensor("          O2 Sensor: 2 - 4", CommandListObj.O2_B2S4, "volt"),                     # 1B  volt
        Sensor("            OBD Compliance", CommandListObj.OBD_COMPLIANCE, ""),                  # 1C  str
        Sensor("    Alt O2 Sensors Present", CommandListObj.O2_SENSORS_ALT, ""),                  # 1D  special
        Sensor("     Auxilary Input Status", CommandListObj.AUX_INPUT_STATUS, ""),                # 1E  boolean
        Sensor("           Engine Run Time", CommandListObj.RUN_TIME, "sec"),                     # 1F  sec, min
    ],
    #
    # PID_B Commands...
    #
    [
        Sensor("    Supported PIDs [21-40]", CommandListObj.PIDS_B, ""),                          # 20  bitarray
        Sensor("      Distance with MIL ON", CommandListObj.DISTANCE_W_MIL, "kilo"),              # 21  kilometer, miles
        Sensor("  Fuel Rail Pressure (vac)", CommandListObj.FUEL_RAIL_PRESSURE_VAC, "kph"),       # 22  kilopascal, psi
        Sensor("  Fuel Rail Pressure (dir)", CommandListObj.FUEL_RAIL_PRESSURE_DIRECT, "kph"),    # 23  kilopascal, psi
        Sensor("O2 Sensor 1 WR Lambda Volt", CommandListObj.O2_S1_WR_VOLTAGE, "volt"),            # 24  volt
        Sensor("O2 Sensor 2 WR Lambda Volt", CommandListObj.O2_S2_WR_VOLTAGE, "volt"),            # 25  volt
        Sensor("O2 Sensor 3 WR Lambda Volt", CommandListObj.O2_S3_WR_VOLTAGE, "volt"),            # 26  volt
        Sensor("O2 Sensor 4 WR Lambda Volt", CommandListObj.O2_S4_WR_VOLTAGE, "volt"),            # 27  volt
        Sensor("O2 Sensor 5 WR Lambda Volt", CommandListObj.O2_S5_WR_VOLTAGE, "volt"),            # 28  volt
        Sensor("O2 Sensor 6 WR Lambda Volt", CommandListObj.O2_S6_WR_VOLTAGE, "volt"),            # 29  volt
        Sensor("O2 Sensor 7 WR Lambda Volt", CommandListObj.O2_S7_WR_VOLTAGE, "volt"),            # 2A  volt
        Sensor("O2 Sensor 8 WR Lambda Volt", CommandListObj.O2_S8_WR_VOLTAGE, "volt"),            # 2B  volt
        Sensor("             Commanded EGR", CommandListObj.COMMANDED_EGR, "%"),                  # 2C  percent
        Sensor("                 EGR Error", CommandListObj.EGR_ERROR, "%"),                      # 2D  percent
        Sensor("  Cmnded Evaporative Purge", CommandListObj.EVAPORATIVE_PURGE, "%"),              # 2E  percent
        Sensor("          Fuel Level Input", CommandListObj.FUEL_LEVEL, "%"),                     # 2F  percent
        Sensor("# Warm-ups Since Clear DTC", CommandListObj.WARMUPS_SINCE_DTC_CLEAR, ""),         # 30  count
        Sensor("  Distance Since Clear DTC", CommandListObj.DISTANCE_SINCE_DTC_CLEAR, "kilo"),    # 31  kilometer, mile
        Sensor("   Evap Sys Vapor Pressure", CommandListObj.EVAP_VAPOR_PRESSURE, "kPa"),          # 32  kilopascal, psi
        Sensor("       Barometric Pressure", CommandListObj.BAROMETRIC_PRESSURE, "kPa"),          # 33  kilopascal, psi
        Sensor("O2 Sensor 1 WR Lambda Curr", CommandListObj.O2_S1_WR_CURRENT, "mA"),              # 34  milliampere
        Sensor("O2 Sensor 2 WR Lambda Curr", CommandListObj.O2_S2_WR_CURRENT, "mA"),              # 35  milliampere
        Sensor("O2 Sensor 3 WR Lambda Curr", CommandListObj.O2_S3_WR_CURRENT, "mA"),              # 36  milliampere
        Sensor("O2 Sensor 4 WR Lambda Curr", CommandListObj.O2_S4_WR_CURRENT, "mA"),              # 37  milliampere
        Sensor("O2 Sensor 5 WR Lambda Curr", CommandListObj.O2_S5_WR_CURRENT, "mA"),              # 38  milliampere
        Sensor("O2 Sensor 6 WR Lambda Curr", CommandListObj.O2_S6_WR_CURRENT, "mA"),              # 39  milliampere
        Sensor("O2 Sensor 7 WR Lambda Curr", CommandListObj.O2_S7_WR_CURRENT, "mA"),              # 3A  milliampere
        Sensor("O2 Sensor 8 WR Lambda Curr", CommandListObj.O2_S8_WR_CURRENT, "mA"),              # 3B  milliampere
        Sensor(" Cat Temp: Bank 1 Sensor 1", CommandListObj.CATALYST_TEMP_B1S1, "degC"),          # 3C  degC, degF
        Sensor(" Cat Temp: Bank 2 Sensor 1", CommandListObj.CATALYST_TEMP_B2S1, "degC"),          # 3D  degC, degF
        Sensor(" Cat Temp: Bank 1 Sensor 2", CommandListObj.CATALYST_TEMP_B1S2, "degC"),          # 3E  degC, degF
        Sensor(" Cat Temp: Bank 2 Sensor 2", CommandListObj.CATALYST_TEMP_B2S2, "degC"),          # 3F  degC, degF
    ],
    #
    # PID_C Commands...
    #
    [
        Sensor("    Supported PIDs [41-60]", CommandListObj.PIDS_C, ""),                          # 40  bitarray
        Sensor("Monitor Status Drive Cycle", CommandListObj.STATUS_DRIVE_CYCLE, ""),              # 41  special
        Sensor("    Control Module Voltage", CommandListObj.CONTROL_MODULE_VOLTAGE, "volt"),      # 42  volt
        Sensor("       Absolute Load Value", CommandListObj.ABSOLUTE_LOAD, "%"),                  # 43  percent
        Sensor("     Commanded Equiv Ratio", CommandListObj.COMMANDED_EQUIV_RATIO, "ratio"),      # 44  ratio
        Sensor("Relative Throttle Position", CommandListObj.RELATIVE_THROTTLE_POS, "%"),          # 45  percent
        Sensor("   Ambient Air Temperature", CommandListObj.AMBIANT_AIR_TEMP, "degC"),            # 46  degC, degF
        Sensor("   Abs Throttle Position B", CommandListObj.THROTTLE_POS_B, "%"),                 # 47  percent
        Sensor("   Abs Throttle Position C", CommandListObj.THROTTLE_POS_C, "%"),                 # 48  percent
        Sensor("    Accel Pedal Position D", CommandListObj.ACCELERATOR_POS_D, "%"),              # 49  percent
        Sensor("    Accel Pedal Position E", CommandListObj.ACCELERATOR_POS_E, "%"),              # 4A  percent
        Sensor("    Accel Pedal Position F", CommandListObj.ACCELERATOR_POS_F, "%"),              # 4B  percent
        Sensor(" Comnded Throttle Actuator", CommandListObj.THROTTLE_ACTUATOR, "%"),              # 4C  percent
        Sensor("          Time with MIL ON", CommandListObj.RUN_TIME_MIL, "sec"),                 # 4D  sec, min
        Sensor("    Time Since DTC Cleared", CommandListObj.TIME_SINCE_DTC_CLEARED, "sec"),       # 4E  sec, min
        #Sensor("               Unsupported", CommandListObj.UNSUPPORTED, ""),                     # 4F  unknown
        Sensor("  Mass Air Flow: Max Value", CommandListObj.MAX_MAF, "gps"),                      # 50  gps (grams/sec), lb/min
        Sensor("                 Fuel Type", CommandListObj.FUEL_TYPE, ""),                       # 51  str
        Sensor("      Ethanol Fuel Percent", CommandListObj.ETHANOL_PERCENT, "%"),                # 52  percent
        Sensor("Abs EvapSys Vapor Pressure", CommandListObj.EVAP_VAPOR_PRESSURE_ABS, "kPa"),      # 53  kilopascal
        Sensor("Alt EvapSys Vapor Pressure", CommandListObj.EVAP_VAPOR_PRESSURE_ALT, "kPa"),      # 54  kilopascal
        Sensor(" Short Term 2nd O2 Trim B1", CommandListObj.SHORT_O2_TRIM_B1, "%"),               # 55  percent
        Sensor("  Long Term 2nd O2 Trim B1", CommandListObj.LONG_O2_TRIM_B1, "%"),                # 56  percent
        Sensor(" Short Term 2nd O2 Trim B2", CommandListObj.SHORT_O2_TRIM_B2, "%"),               # 57  percent
        Sensor("  Long Term 2nd O2 Trim B2", CommandListObj.LONG_O2_TRIM_B2, "%"),                # 58  percent
        Sensor("  Fuel Rail Pressure (abs)", CommandListObj.FUEL_RAIL_PRESSURE_ABS, "kPa"),       # 59  kilopascal
        Sensor("  Rel Accel Pedal Position", CommandListObj.RELATIVE_ACCEL_POS, "%"),             # 5A  percent
        Sensor("      Hybrid Battery: Life", CommandListObj.HYBRID_BATTERY_REMAINING, "%"),       # 5B  percent
        Sensor("    Engine Oil Temperature", CommandListObj.OIL_TEMP, "degC"),                    # 5C  degC, degF
        Sensor("     Fuel Injection Timing", CommandListObj.FUEL_INJECT_TIMING, "degree"),        # 5D  degree
        Sensor("          Engine Fuel Rate", CommandListObj.FUEL_RATE, "lph"),                    # 5E  liters/hour, gallons/hour
        #Sensor("               Unsupported", CommandListObj.UNSUPPORTED, ""),                     # 5F  unknown
    ]
    #
    # ...END SENSORS
    #
    ]
