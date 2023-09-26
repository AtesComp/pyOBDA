############################################################################
#
# Python Onboard Diagnostics II Advanced
#
# ListCtrl.py
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

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

# An extended wx.ListCtrl class that auto-resizes the column boxes on resize...
class ListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(
        self, parent, id, pos = wx.DefaultPosition,
        size = wx.DefaultSize, style = 0):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style)
        ListCtrlAutoWidthMixin.__init__(self)
