# pyright: ignore
# type: ignore

import wx
from wx.lib.activexwrapper import MakeActiveXClass
import win32com.client.gencache

try:
    acrobatModule = win32com.client.gencache.EnsureModule(
          '{CA8A9783-280D-11CF-A24D-444553540000}', 0x0, 1, 3)
except Exception, error:
    raise ImportError, error

wxComPdfPtr = MakeActiveXClass(acrobatModule.Pdf)
class wxComPdf(wxComPdfPtr):
    def __init__(self, parent = None, id = -1, pos=wx.DefaultPosition,
          size=wx.DefaultSize, style=0, name=''):
        wxComPdfPtr.__init__(self, parent, id, pos, size, style)
        self.SetName(name)
