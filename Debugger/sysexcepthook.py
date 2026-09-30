"""This script allows you to import, start and hook a DebugServer when
an uncaught exception occurs.

Once the DebugServer has started, you may connect to it via
Tools->Attach to debugger

To use, fix path_to_boa to point to your Boa installation, copy it anywhere
on your sys.path (site-packages is recommended) and import this module.

You may consider importing this module in sitecustomize.py (create it if needed)
if you use it often."""

path_to_boa = 'c:/path/to/boa'

import sys, traceback

def hook_debugger(tpe, val, tb):
    traceback.print_exception(tpe, val, tb)

    #if sys.modules.has_key('wxPython.wx'):
    import wx
    if wx.MessageBox('%s: %s\n\nStart DebugServer?'%(tpe, val),
          'Uncaught Exception', wx.ICON_ERROR | wx.YES_NO) == wx.NO:
        return

    if not hasattr(sys, 'debugger_control'):
        sys.path.append(path_to_boa)
        from Debugger.RemoteServer import start

        start(username='', password='')

    sys.debugger_control.post_mortem( (tpe, val, tb) )  # type: ignore[attr-defined]

sys.excepthook = hook_debugger

