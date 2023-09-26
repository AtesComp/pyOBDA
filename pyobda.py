#!/usr/bin/env python3
############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# pyobda.py
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

import wx

import AppSettings
from Frame import Frame

#
# The pyOBDA App
#
class OBDA_App(wx.App):
    def OnInit(self):
        # ====================
        # Setup Main Frame
        # ====================

        frame = Frame("OBD-II Advanced v" + AppSettings.VERSION)
        self.SetTopWindow(frame)
        frame.Center();
        frame.Show(True)

        return True

app = OBDA_App(0)
app.MainLoop()
