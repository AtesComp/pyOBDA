############################################################################
#
# Sensor.py
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

from obd import commands

class Sensor:
    def __init__(self, strSensorName, strSensorCommand, strSensorUnit):
        self.name = strSensorName
        self.cmd = strSensorCommand
        self.unit = strSensorUnit

class Manager:
    SENSOR_GROUP_A = 0
    SENSOR_GROUP_B = 2
    SENSOR_GROUP_C = 3

    SENSORS = [
    #
    # PID_A Commands...
    #
    [
        Sensor("    Supported PIDs [01-20]", commands.PIDS_A, ""),                          # 00  bitarray
        Sensor("    Status Since Clear DTC", commands.STATUS, ""),                          # 01  special
        Sensor("          Freeze Frame DTC", commands.FREEZE_DTC, ""),                      # 02  special
        Sensor("        Fuel System Status", commands.FUEL_STATUS, ""),                     # 03  (1st sys str, 2nd sys str)
        Sensor(" Calc'ed Engine Load Value", commands.ENGINE_LOAD, "%"),                    # 04  percent
        Sensor("       Coolant Temperature", commands.COOLANT_TEMP, "degC"),                # 05  degC, degF
        Sensor("    Short Term Fuel Trim 1", commands.SHORT_FUEL_TRIM_1, "%"),              # 06  percent
        Sensor("     Long Term Fuel Trim 1", commands.LONG_FUEL_TRIM_1, "%"),               # 07  percent
        Sensor("    Short Term Fuel Trim 2", commands.SHORT_FUEL_TRIM_2, "%"),              # 08  percent
        Sensor("     Long Term Fuel Trim 2", commands.LONG_FUEL_TRIM_2, "%"),               # 09  percent
        Sensor("             Fuel Pressure", commands.FUEL_PRESSURE, "kPa"),                # 0A  kilopascal, psi
        Sensor("  Intake Manifold Pressure", commands.INTAKE_PRESSURE, "kPa"),              # 0B  kilopascal, psi
        Sensor("                Engine RPM", commands.RPM, "rpm"),                          # 0C  rpm
        Sensor("             Vehicle Speed", commands.SPEED, "kph"),                        # 0D  kph, mph
        Sensor("            Timing Advance", commands.TIMING_ADVANCE, "degree"),            # 0E  degree
        Sensor("    Intake Air Temperature", commands.INTAKE_TEMP, "degC"),                 # 0F  degC, degF
        Sensor("  Mass Air Flow Rate (MAF)", commands.MAF, "gps"),                          # 10  gps (grams/sec), lb/min
        Sensor("         Throttle Position", commands.THROTTLE_POS, "%"),                   # 11  percent
        Sensor("      Secondary Air Status", commands.AIR_STATUS, ""),                      # 12  str
        Sensor("        O2 Sensors Present", commands.O2_SENSORS, ""),                      # 13  special
        Sensor("          O2 Sensor: 1 - 1", commands.O2_B1S1, "volt"),                     # 14  volt
        Sensor("          O2 Sensor: 1 - 2", commands.O2_B1S2, "volt"),                     # 15  volt
        Sensor("          O2 Sensor: 1 - 3", commands.O2_B1S3, "volt"),                     # 16  volt
        Sensor("          O2 Sensor: 1 - 4", commands.O2_B1S4, "volt"),                     # 17  volt
        Sensor("          O2 Sensor: 2 - 1", commands.O2_B2S1, "volt"),                     # 18  volt
        Sensor("          O2 Sensor: 2 - 2", commands.O2_B2S2, "volt"),                     # 19  volt
        Sensor("          O2 Sensor: 2 - 3", commands.O2_B2S3, "volt"),                     # 1A  volt
        Sensor("          O2 Sensor: 2 - 4", commands.O2_B2S4, "volt"),                     # 1B  volt
        Sensor("            OBD Compliance", commands.OBD_COMPLIANCE, ""),                  # 1C  str
        Sensor("    Alt O2 Sensors Present", commands.O2_SENSORS_ALT, ""),                  # 1D  special
        Sensor("     Auxilary Input Status", commands.AUX_INPUT_STATUS, ""),                # 1E  boolean
        Sensor("           Engine Run Time", commands.RUN_TIME, "sec"),                     # 1F  sec, min
    ],
    #
    # PID_B Commands...
    #
    [
        Sensor("    Supported PIDs [21-40]", commands.PIDS_B, ""),                          # 20  bitarray
        Sensor("      Distance with MIL ON", commands.DISTANCE_W_MIL, "kilo"),              # 21  kilometer, miles
        Sensor("  Fuel Rail Pressure (vac)", commands.FUEL_RAIL_PRESSURE_VAC, "kph"),       # 22  kilopascal, psi
        Sensor("  Fuel Rail Pressure (dir)", commands.FUEL_RAIL_PRESSURE_DIRECT, "kph"),    # 23  kilopascal, psi
        Sensor("O2 Sensor 1 WR Lambda Volt", commands.O2_S1_WR_VOLTAGE, "volt"),            # 24  volt
        Sensor("O2 Sensor 2 WR Lambda Volt", commands.O2_S2_WR_VOLTAGE, "volt"),            # 25  volt
        Sensor("O2 Sensor 3 WR Lambda Volt", commands.O2_S3_WR_VOLTAGE, "volt"),            # 26  volt
        Sensor("O2 Sensor 4 WR Lambda Volt", commands.O2_S4_WR_VOLTAGE, "volt"),            # 27  volt
        Sensor("O2 Sensor 5 WR Lambda Volt", commands.O2_S5_WR_VOLTAGE, "volt"),            # 28  volt
        Sensor("O2 Sensor 6 WR Lambda Volt", commands.O2_S6_WR_VOLTAGE, "volt"),            # 29  volt
        Sensor("O2 Sensor 7 WR Lambda Volt", commands.O2_S7_WR_VOLTAGE, "volt"),            # 2A  volt
        Sensor("O2 Sensor 8 WR Lambda Volt", commands.O2_S8_WR_VOLTAGE, "volt"),            # 2B  volt
        Sensor("             Commanded EGR", commands.COMMANDED_EGR, "%"),                  # 2C  percent
        Sensor("                 EGR Error", commands.EGR_ERROR, "%"),                      # 2D  percent
        Sensor("  Cmnded Evaporative Purge", commands.EVAPORATIVE_PURGE, "%"),              # 2E  percent
        Sensor("          Fuel Level Input", commands.FUEL_LEVEL, "%"),                     # 2F  percent
        Sensor("# Warm-ups Since Clear DTC", commands.WARMUPS_SINCE_DTC_CLEAR, ""),         # 30  count
        Sensor("  Distance Since Clear DTC", commands.DISTANCE_SINCE_DTC_CLEAR, "kilo"),    # 31  kilometer, mile
        Sensor("   Evap Sys Vapor Pressure", commands.EVAP_VAPOR_PRESSURE, "kPa"),          # 32  kilopascal, psi
        Sensor("       Barometric Pressure", commands.BAROMETRIC_PRESSURE, "kPa"),          # 33  kilopascal, psi
        Sensor("O2 Sensor 1 WR Lambda Curr", commands.O2_S1_WR_CURRENT, "mA"),              # 34  milliampere
        Sensor("O2 Sensor 2 WR Lambda Curr", commands.O2_S2_WR_CURRENT, "mA"),              # 35  milliampere
        Sensor("O2 Sensor 3 WR Lambda Curr", commands.O2_S3_WR_CURRENT, "mA"),              # 36  milliampere
        Sensor("O2 Sensor 4 WR Lambda Curr", commands.O2_S4_WR_CURRENT, "mA"),              # 37  milliampere
        Sensor("O2 Sensor 5 WR Lambda Curr", commands.O2_S5_WR_CURRENT, "mA"),              # 38  milliampere
        Sensor("O2 Sensor 6 WR Lambda Curr", commands.O2_S6_WR_CURRENT, "mA"),              # 39  milliampere
        Sensor("O2 Sensor 7 WR Lambda Curr", commands.O2_S7_WR_CURRENT, "mA"),              # 3A  milliampere
        Sensor("O2 Sensor 8 WR Lambda Curr", commands.O2_S8_WR_CURRENT, "mA"),              # 3B  milliampere
        Sensor(" Cat Temp: Bank 1 Sensor 1", commands.CATALYST_TEMP_B1S1, "degC"),          # 3C  degC, degF
        Sensor(" Cat Temp: Bank 2 Sensor 1", commands.CATALYST_TEMP_B2S1, "degC"),          # 3D  degC, degF
        Sensor(" Cat Temp: Bank 1 Sensor 2", commands.CATALYST_TEMP_B1S2, "degC"),          # 3E  degC, degF
        Sensor(" Cat Temp: Bank 2 Sensor 2", commands.CATALYST_TEMP_B2S2, "degC"),          # 3F  degC, degF
    ],
    #
    # PID_C Commands...
    #
    [
        Sensor("    Supported PIDs [41-60]", commands.PIDS_C, ""),                          # 40  bitarray
        Sensor("Monitor Status Drive Cycle", commands.STATUS_DRIVE_CYCLE, ""),              # 41  special
        Sensor("    Control Module Voltage", commands.CONTROL_MODULE_VOLTAGE, "volt"),      # 42  volt
        Sensor("       Absolute Load Value", commands.ABSOLUTE_LOAD, "%"),                  # 43  percent
        Sensor("     Commanded Equiv Ratio", commands.COMMANDED_EQUIV_RATIO, "ratio"),      # 44  ratio
        Sensor("Relative Throttle Position", commands.RELATIVE_THROTTLE_POS, "%"),          # 45  percent
        Sensor("   Ambient Air Temperature", commands.AMBIANT_AIR_TEMP, "degC"),            # 46  degC, degF
        Sensor("   Abs Throttle Position B", commands.THROTTLE_POS_B, "%"),                 # 47  percent
        Sensor("   Abs Throttle Position C", commands.THROTTLE_POS_C, "%"),                 # 48  percent
        Sensor("    Accel Pedal Position D", commands.ACCELERATOR_POS_D, "%"),              # 49  percent
        Sensor("    Accel Pedal Position E", commands.ACCELERATOR_POS_E, "%"),              # 4A  percent
        Sensor("    Accel Pedal Position F", commands.ACCELERATOR_POS_F, "%"),              # 4B  percent
        Sensor(" Comnded Throttle Actuator", commands.THROTTLE_ACTUATOR, "%"),              # 4C  percent
        Sensor("          Time with MIL ON", commands.RUN_TIME_MIL, "sec"),                 # 4D  sec, min
        Sensor("    Time Since DTC Cleared", commands.TIME_SINCE_DTC_CLEARED, "sec"),       # 4E  sec, min
        #Sensor("               Unsupported", commands.UNSUPPORTED, ""),                     # 4F  unknown
        Sensor("  Mass Air Flow: Max Value", commands.MAX_MAF, "gps"),                      # 50  gps (grams/sec), lb/min
        Sensor("                 Fuel Type", commands.FUEL_TYPE, ""),                       # 51  str
        Sensor("      Ethanol Fuel Percent", commands.ETHANOL_PERCENT, "%"),                # 52  percent
        Sensor("Abs EvapSys Vapor Pressure", commands.EVAP_VAPOR_PRESSURE_ABS, "kPa"),      # 53  kilopascal
        Sensor("Alt EvapSys Vapor Pressure", commands.EVAP_VAPOR_PRESSURE_ALT, "kPa"),      # 54  kilopascal
        Sensor(" Short Term 2nd O2 Trim B1", commands.SHORT_O2_TRIM_B1, "%"),               # 55  percent
        Sensor("  Long Term 2nd O2 Trim B1", commands.LONG_O2_TRIM_B1, "%"),                # 56  percent
        Sensor(" Short Term 2nd O2 Trim B2", commands.SHORT_O2_TRIM_B2, "%"),               # 57  percent
        Sensor("  Long Term 2nd O2 Trim B2", commands.LONG_O2_TRIM_B2, "%"),                # 58  percent
        Sensor("  Fuel Rail Pressure (abs)", commands.FUEL_RAIL_PRESSURE_ABS, "kPa"),       # 59  kilopascal
        Sensor("  Rel Accel Pedal Position", commands.RELATIVE_ACCEL_POS, "%"),             # 5A  percent
        Sensor("      Hybrid Battery: Life", commands.HYBRID_BATTERY_REMAINING, "%"),       # 5B  percent
        Sensor("    Engine Oil Temperature", commands.OIL_TEMP, "degC"),                    # 5C  degC, degF
        Sensor("     Fuel Injection Timing", commands.FUEL_INJECT_TIMING, "degree"),        # 5D  degree
        Sensor("          Engine Fuel Rate", commands.FUEL_RATE, "lph"),                    # 5E  liters/hour, gallons/hour
        #Sensor("               Unsupported", commands.UNSUPPORTED, ""),                     # 5F  unknown
    ]
    #
    # ...END SENSORS
    #
    ]
