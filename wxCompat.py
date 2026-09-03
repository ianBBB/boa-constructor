# -*- coding: utf-8 -*-
# Compatibility layer for older wx naming conventions

import wx

wxDIALOG_MODAL = getattr(wx, 'DIALOG_MODAL', getattr(wx, 'wxDIALOG_MODAL', 1))

wxDIALOG_MODELESS = getattr(wx, 'DIALOG_MODELESS', getattr(wx, 'wxDIALOG_MODELESS', 0))

try:
    from wx.tools.img2py import crunch_data
except (ImportError, AttributeError):
    try:
        from ExternalLib.wxtools import crunch_data
    except (ImportError, AttributeError):
        def crunch_data(data, compressed=1):
            return data
