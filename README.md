# Onboard Diagnostics II Advanced: pyOBDA

The pyOBDA advances the previous pyOBD effort by restructuring the code and incorporating the rather simple and old ODB library directly.  It also removes many external library requirements.

## Installation Instructions

### Prerequisites:

First, install the following and make sure they work.

1. Python3

    A recent release is needed. Developement took place using the 3.8.x release series. Any 3.X release *should* work, but hasn't been tested. Under MacOSX 10.3 (panther), Python is installed by default. Installation instructions are available at the python website: [www.python.org](http://www.python.org)

2. OBD

    This is needed to communicate via the serial port. It is available as a pip package. Install it. Version 0.7.1 was used for development. It uses pyserial and pint included in its package. See the [Python OBD Docs](https://python-obd.readthedocs.io/)

3. WxPython

    WxPython is needed if you want to use the pretty graphical interface to sensor data and DTC management. It's available as a pip package. Install it. Version 4.2.1 was used for development. It can also be installed globally. For example, a debian linux box might install python3-wxgtk4.0.

### Installation:

After those requirements, installation is a snap. Simply download the release tarball and uncompress it. To "install" pyOBDA on the system, simply copy the release directory to wherever you want (i.e. /opt, /usr/local).

To use the `wx` interface, run **python3 pyobda.py**. If you're using MacOSX, substitute "pythonw" for "python".
