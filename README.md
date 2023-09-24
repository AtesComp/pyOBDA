# Onboard Diagnostics II Advanced: pyOBDA

The pyOBDA advances the previous [pyOBD](https://github.com/barracuda-fsh/pyobd) and [python-obd](https://github.com/brendan-w/python-OBD) projects by restructuring, combining, and rewriting their code into a single, uniform application.  It also removes several unneeded external library requirements.

For information on the older python-obd specs, see the [Python OBD Docs](https://python-obd.readthedocs.io/)

## Installation Instructions

### Prerequisites:

First, install the following and make sure they work.

1. Python3

    A recent Python3 release is needed. Developement took place using the 3.8.x release series. Any 3.X release *should* work, but hasn't been tested. Under MacOSX 10.3 (panther), Python is installed by default. Installation instructions are available at the python website: [www.python.org](http://www.python.org)

2. wxPython

    The "wxPython" library is needed if you want to use the pretty graphical interface to sensor data and DTC management. It's available as a pip package. Install it. Version 4.2.1 was used for development. It can also be installed globally. For example, a debian linux box might install python3-wxgtk4.0.

3. pyserial

    The "pyserial" library is required to connect a computer to a vehicle's OBD II port. See: [pyserial](https://github.com/pyserial/pyserial)

4. pint

    The "pint" library is required for universal unit and scale values. See: [pint](https://github.com/hgrecco/pint)

### Installation:

After those requirements, installation is a snap. Simply download the release tarball and uncompress it. To "install" pyOBDA on the system, simply copy the release directory to wherever you want (i.e. /opt, /usr/local).

To use the `wx` interface, run **python3 pyobda.py**. If you're using MacOSX, run **pythonw pyobda.py**.
