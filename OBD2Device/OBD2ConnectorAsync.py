############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# OBD2ConnectorAsync.py
#
# Copyright 2021-2023 Keven L. Ates (atescomp@gmail.com)
#
# This file is part of the Onboard Diagnostics II Advanced (pyOBDA) system.
#
# This file was rewritten from the project "python-OBD" file "obd/asynchronous.py"
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


import time
import threading
import logging

from .Response import Response
from .OBD2Connector import OBD2Connector

logger = logging.getLogger(__name__)


class OBD2ConnectorAsync(OBD2Connector):
    """
    Class representing an OBD-II connection with it's assorted commands and sensors.

    This class uses an asynchronous value reporting process.
    """

    def __init__(self, strPort:str = "", iBaudRate:int = 0, strProtocol:str = "", bFast:bool = True,
                 fTimeout:float = 0.1, bCheckVoltage:bool = True, bStartLowPower:bool = False,
                 fDelayCmds:float = 0.25):
        self.__thread = None
        super(OBD2ConnectorAsync, self).__init__(
            strPort, iBaudRate, strProtocol, bFast, fTimeout, bCheckVoltage, bStartLowPower
        )
        self.__dictCommands = {}   # key = OBDCommand, value = Response
        self.__dictCallbacks = {}  # key = OBDCommand, value = list of Functions
        self.__bRunning = False
        self.__bWasRunning = False  # used with __enter__() and __exit__()
        self.__fDelayCmds = fDelayCmds

    @property
    def running(self):
        return self.__bRunning

    def start(self):
        """
        Start the async update loop.
        """

        if not self.isConnected():
            logger.info("Async thread not started because no connection was made")
            return

        if len(self.__dictCommands) == 0:
            logger.info("Async thread not started because no commands were registered")
            return

        if self.__thread is None:
            logger.info("Starting async thread")
            self.__bRunning = True
            self.__thread = threading.Thread(target=self.run)
            self.__thread.daemon = True
            self.__thread.start()

    def stop(self):
        """
        Stop the async update loop.
        """

        if self.__thread is not None:
            logger.info("Stopping async thread...")
            self.__bRunning = False
            self.__thread.join()
            self.__thread = None
            logger.info("Async thread stopped")

    def paused(self):
        """
        A stub function for semantic purposes only

        Enables code such as:
            with connection.paused() as was_running
        """

        return self

    def __enter__(self):
        """
        Pauses (stop) the async loop while recording the old state.
        """
        self.__bWasRunning = self.__bRunning
        self.stop()
        return self.__bWasRunning

    def __exit__(self, exc_type, exc_value, traceback):
        # Resume the update loop if it was running when __enter__ was called

        if not self.__bRunning and self.__bWasRunning:
            self.start()

        return False  # ...don't suppress exceptions

    def close(self):
        """
        Close the connection.
        """

        self.stop()
        super(OBD2ConnectorAsync, self).close()

    def watch(self, cmd, callback=None, force=False):
        """
        Watch the given command for continuous updating.

        When watched, query() will return that command's latest value.
        Optional callbacks can be given which will be fired upon every new value.
        """

        # Don't change the dict while the daemon thread is iterating...
        if self.__bRunning:
            logger.warning("Can't watch() while running, please use stop()")
            return

        if not force and not self.isCmdUsable(cmd, False):
            # self.test_cmd() will print warnings
            return

        # Create new command being watched, store the command...
        if cmd not in self.__dictCommands:
            logger.info("Watching command: %s" % str(cmd))
            self.__dictCommands[cmd] = Response()  # ...give it an initial value
            self.__dictCallbacks[cmd] = []  # ...create an empty list

        # If a callback was given, push it...
        if hasattr(callback, "__call__") and (callback not in self.__dictCallbacks[cmd]):
            logger.info("subscribing callback for command: %s" % str(cmd))
            self.__dictCallbacks[cmd].append(callback)

    def unwatch(self, cmd, callback=None):
        """
        Stop watching a specific command (and optionally, a specific callback) being updated.

        If no callback is specified, all callbacks for that command are dropped.
        """

        # Don't change the dict while the daemon thread is iterating...
        if self.__bRunning:
            logger.warning("Can't unwatch() while running, please use stop()")
            return

        logger.info("Unwatching command: %s" % str(cmd))

        if cmd in self.__dictCommands:
            bRemoveCmd = True
            # If a callback was specified...
            if hasattr(callback, "__call__") and (callback in self.__dictCallbacks[cmd]):
                bRemoveCmd = False
                # ...remove the callback...
                self.__dictCallbacks[cmd].remove(callback)

                # If all callbacks have been removed...
                if len(self.__dictCallbacks[cmd]) == 0:
                    bRemoveCmd = True

            # If complete removal is indicated...
            if bRemoveCmd:
                # ...remove the command from callbacks...
                self.__dictCallbacks.pop(cmd, None)
                    # ...remove the command entirely...
                self.__dictCommands.pop(cmd, None)

    def unwatch_all(self):
        """
        Stop watching all commands and callbacks being updated.
        """

        # Don't change the dict while the daemon thread is iterating...
        if self.__bRunning:
            logger.warning("Can't unwatch_all() while running, please use stop()")
            return

        logger.info("Unwatching all commands")
        self.__dictCommands = {}
        self.__dictCallbacks = {}

    def query(self, cmd, force=False):
        """
        Non-blocking query function.

        Only commands that have been watched will return valid responses
        """

        if cmd in self.__dictCommands:
            return self.__dictCommands[cmd]
        else:
            return Response()

    def run(self):
        """
        The Daemon Thread for the asynchronous process.
        """

        # Loop until the stop signal is received...
        while self.__bRunning:

            if len(self.__dictCommands) > 0:
                # Loop over the requested commands: send and collect the response...
                for c in self.__dictCommands:
                    if not self.isConnected():
                        logger.info("Async thread terminated because device disconnected")
                        self.__bRunning = False
                        self.__thread = None
                        return

                    # Force, since commands are checked for support in watch()...
                    r = super(OBD2ConnectorAsync, self).query(c, bForce=True)

                    # Store the response...
                    self.__dictCommands[c] = r

                    # Fire the callbacks, if there are any...
                    for callback in self.__dictCallbacks[c]:
                        callback(r)
                time.sleep(self.__fDelayCmds)

            else:
                time.sleep(0.25)  # ...idle
