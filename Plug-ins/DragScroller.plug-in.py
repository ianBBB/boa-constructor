import wx

import Preferences, Plugins
from Utils import _
"""
A DragScroller scrolls a wx.ScrollWindow in the direction and speed of a mouse drag

To use this plug-in in the Designer you'd need to define the mouse click events
you want to use for the drag scroller (from it's scrollwindow) and add code like 
this to start and stop the dragging.

# designer code

        ...
        self.dragScroller = wx.lib.dragscroller.DragScroller(rate=35, scrollwin=None)
        ...
        self.scrollWindow.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.scrollWindow.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

# your code:
    
        ...
        self._init_ctrls(parent)

        self.scroller.SetScrollWindow(self.scrollwindow)
    ...
    def OnRightDown(self, event):
        self.scroller.Start(event.GetPosition())

    def OnRightUp(self, event):
        self.scroller.Stop()

"""

try:
    import wx.lib.dragscroller
except ImportError:
    raise Plugins.SkipPluginSilently, _('Module %s not found')%'wx.lib.dragscroller'

from Companions import UtilCompanions
from PropEdit import PropertyEditors

#-------------------------------------------------------------------------------
# DragScroller
# wx.lib.dragscroller.DragScroller

class DragScrollerDTC(UtilCompanions.UtilityDTC):
    handledConstrParams = ('id',)
    def __init__(self, name, designer, objClass):
        UtilCompanions.UtilityDTC.__init__(self, name, designer, objClass)
        self.editors['Sensitivity'] = PropertyEditors.BITPropEditor

    def constructor(self):
        return {'ScrollWindow': 'scrollwin', 'UpdateRate': 'rate'}

    def designTimeSource(self):
        return {'scrollwin': 'None', 'rate': '35'}

    def writeImports(self):
        return 'import wx.lib.dragscroller'

#-------------------------------------------------------------------------------

def getDragScrollerData():
    return \
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\
\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x01QIDATH\x89\xb5V\xdb\x8d\xc3 \x10\x9c\x05\x17\xe0\x94c+i\xc0R\xaa\x8d\xe4\
\xcf\xdc\x87-(\xc7\x15$s\x1f\xb9\xe50\x81\xe0\\\xce+!\xc0Z\xcd\xb0\xb3\x0fY\
\xc4X\xeci\r\x00\xf0~\xe3\x1e\xe0b\xac4zq\x93\xfb\x08\xac?\xf5 \x1f\xef\xf4\
\xb3G\x7f\xea\x01\x00\xe6\x1d\x90\xe1<T}Ddu\xdfL0\x9c\x07\x8c\x97\xf1%\x89\
\x9f=\xdc\xe4p\xfd\xba\x86oM\xd1;\x03\xde\x1d\xbb@2^\xc6\'?\x95%\xb6j\x04\
\xfa\xe2\xe1<\xe0p8\xac\xee\xa9\x91\x84\x9b\\\xc8E\x95@A\xc6\xcb\x18^\x1c\
\x9fS\x12?{t\xc7\x0e~\xf6u\x82\x92\x0c\xb1\xa59Q\xf0\xee\xd8\xfd:\xfd4\x1a\
\xdd\xe4\xc2j\xdb\x96nr$\xc9\xb6m\x8b\x8bd\xf0W\x0c\xfd\x06\x80bl\x9e &\xd1\
\xbdt\xd6\x1d@\x00\xe7#\t\x14c\xcb\x12\xd5J2\'c.\x07"\xc6\x82\xf7\x1bK\x9d\
\xfc\x8a$\x06\xd7NV\x12\x11\x81\x18+\xd52\x8d\xabgY\x96\xd5=\xb5?E\x10G\xf2n\
\x93m\x8a \x8e\xa4V\xba$C\xb3\xa9\xbd5\xecj}\x01|0\xec\xb6Xn\xd8\x85\x1c\xfc\
\'Q\x00\x8fs\x90\xea\xa7C+\xb7\x97\xfc\xe3\xa5\xb6\x92(\xd6/\x9e+\xe9\x9e\
\xf3/Y H\xf5+\x81k\x8d\xe7\xf4\xce\xca\xb4w\x0ed\xef\xdf\x96o\x88zW)\xc2N\
\xbe\xfb\x00\x00\x00\x00IEND\xaeB`\x82' 

Plugins.registerComponent('Library', wx.lib.dragscroller.DragScroller, 
                          'wx.lib.dragscroller.DragScroller', DragScrollerDTC)

Preferences.IS.registerImage('Images/Palette/wx.lib.dragscroller.DragScroller.png', 
                             getDragScrollerData())
