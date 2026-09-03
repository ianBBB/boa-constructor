import wx

import Preferences, Utils, Plugins
from Companions import BaseCompanions
from PropEdit import PropertyEditors

try:
    import wx.lib.plot
except ImportError:
    raise Plugins.SkipPlugin('PyPlot can not be imported (it probably requires Numeric)')

class PlotCanvasDTC(BaseCompanions.WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        BaseCompanions.WindowDTC.__init__(self, name, designer, parent, ctrlClass)

    def writeImports(self):
        return 'import wx.lib.plot'

    def onlyPersistProps(self):
        return BaseCompanions.WindowDTC.onlyPersistProps(self) + \
               ['EnableZoom']

    def applyRunTime(self):
        return BaseCompanions.WindowDTC.applyRunTime(self) + \
               ['EnableZoom']

#-------------------------------------------------------------------------------

import Plugins

Plugins.registerComponent('Library', wx.lib.plot.PlotCanvas,
                          'wx.lib.plot.PlotCanvas', PlotCanvasDTC)

def getPlotCanvasData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\
\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\xc8IDATx\x9c\xb5VY\x0e\x85 \x10k\x89\xf7\xbf\x13'\xeb\xfbq\xe1\x01\xb3\
\xb80\x891\x08\xb6\xa53\x8cR\x92\xb00\xca*\xe0Z\xeb:\x82\x03\x1c\x00\xb6\xcc\
\x0b$\xcd\xb9\xc8\xe1\x14\xc1\x9b4\r\x04\x87ZI\xae\xf2\xac\x90\x81\xa0_\x94U\
o\x89)\xd1\x82\x1c\xb8=7T\x11I\x9b\x8c\xbc\xae\xe6\x91\xb7\xc9\xd0\xa2A\xa6t\
\x92\x10r\xc1\x81\xec9h\xc1\xf7;!\x08\xb1\xad\xb1E=8:[\x82\xdc\xc5\x16u\xe3?\
\xf0\xc6.+n\xb5\x8aiB%7\xcb\xe5Z\xa7\x1dd^EQ\xb5X\x11Z\xc4\xae$_\x13xdO\xc2%\
h\xd5\xf7\xbdi6\xbeM\x10\xf5\xa5\xcc\x0eS\xed\x1a\x98\xf7\xaaO\t\x9e\xe6\xe3\
$h?s_FY\t\x0e\x00\\\xfd\xdb\xf2\x03D\x18iL\x82$\x10\xc0\x00\x00\x00\x00IEND\
\xaeB`\x82"

Preferences.IS.registerImage('Images/Palette/wx.lib.plot.PlotCanvas.png', getPlotCanvasData())
