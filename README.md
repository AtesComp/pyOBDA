# Onboard Diagnostics II Advanced: pyOBDA

The pyOBDA advances the previous [pyOBD](https://github.com/barracuda-fsh/pyobd) and [python-obd](https://github.com/brendan-w/python-OBD) projects by restructuring, combining, and rewriting their code into a single, uniform application.  It also has minimal external library requirements.

Additional P and U Code Classes and Codes are added (see Codes.py). Of course, they may not be available for your vehicle. Use "Codes -> Code Lookup" to browse the codes.

The project includes an ELM327.pdf and an ISO_15765-4.pdf for reference material. See the `/docs` directory.

For information on the older python-obd specs, see the [Python OBD Docs](https://python-obd.readthedocs.io/)

## Installation Instructions

### 1. Install Requirements:

Install the following required dependencies.

* **Python3** - A recent Python3 release is needed. Developement took place using the 3.8.x release series. Any 3.X release *should* work, but hasn't been tested. Under MacOSX 10.3 (panther), Python is installed by default. Installation instructions are available at the python website: [www.python.org](http://www.python.org)

* **wxPython** - The "wxPython" library is needed if you want to use the pretty graphical interface to sensor data and DTC management. It's available as a pip package. Install it. Version 4.2.1 was used for development. It can also be installed globally. For example, a debian linux box might install python3-wxgtk4.0. See: [wxPython](https://wxpython.org/) (PyPI: see https://pypi.org/project/wxPython/).
```shell
    sudo apt install python3-wxgtk4.0
    # OR
    pip install wxPython
```

* **pyserial** - The "pyserial" library is required to connect a computer to a vehicle's OBD II port. See: [pyserial](https://github.com/pyserial/pyserial) (PyPI: see https://pypi.org/project/pyserial/).
```shell
    sudo apt install python3-serial
    # OR
    pip install pyserial
```

* **Pint** - The "pint" library is required for universal unit and scale values. See: [pint](https://github.com/hgrecco/pint) (PyPI: see https://pypi.org/project/Pint/).
```shell
    sudo apt install python3-pint
    # OR
    pip install Pint
```

If using pip, a shorter way to install the requirements:
```shell
    cd to/dir/pyobda
    pip install -r requirements.txt
```

### 2. Install pyOBDA:

After installing the above requirements, "install" pyOBDA on your system.

Download the release and uncompress it. Copy the uncompressed directory to wherever you want (i.e. /opt, /usr/local).

To use software, in the directory, run **python3 pyobda.py**. If you're using MacOSX, run **pythonw pyobda.py**.
```shell
    cd to/dir/pyobda
    ./pyobda.py
```

Modern Python uses Virtual Environments to protect your system. See [Python3 venv](https://docs.python.org/3/library/venv.html). As an alternative, do the following:
```shell
  # To install...
    python -m venv ${HOME}/venv/pyobda # or a general purpose venv
    ${HOME}/venv/pyobda/bin/activate # or the general purpose venv's activate
    cd to/dir/pyobda
    pip install -r requirements.txt
    ./pyobda.py

  # When done...
    deactivate

  # To reuse...
    cd to/dir/pyobda
    ${HOME}/venv/pyobda/bin/activate
    ./pyobda.py
```

### 3. Configuration

#### Configuration Items

pyOBDA uses a configuration file to manage it connection and operation.

The OBD II configuration items are:

 * **PORT** - a computer port connecting the ELM device
 * **BAUD** - the Baud Rate used to communicate using the port
 * **PROTOCOL** - an ELM protocol used to communicate with the vehicle
 * **FAST** - support the ELM fast command response
 * **CHECKVOLTS** - validate the ELM connection voltage
 * **TIMEOUT** - the (fractional) seconds to wait for the connection response
 * **RECONNECTS** - the number of times to try a connection before giving up
 * **DELAY** - the (fractional) seconds to wait between page updates for sensors (1.0 sec min)

Debug configuration items are:

 * **LEVEL** - a debugging verbosity level from 0 (None) to 5 (most verbose)

#### OS Configuration File

For your OS, edit the file in the following locations:
 * Linux: create a config file in the pyOBDA configuration directory
```shell
    ~/.config/pyobda/config
```
 * Mac: same as Linux

 * Windows: create a pyobda.ini file in the pyOBDA program directory
```shell
    <path_to_pyOBDA>\pyobda\pyobda.ini
```

In the config file, place similar following text with your settings:
```ini
    [OBD]
    PORT = /dev/ttyUSB0
    BAUD = 115200
    PROTOCOL = 6
    FAST = True
    CHECKVOLTS = True
    TIMEOUT = 2.0
    RECONNECTS = 5
    DELAY = 1.0

    [DEBUG]
    LEVEL = 1
```

All done! Have fun!