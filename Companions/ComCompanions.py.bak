from BaseCompanions import WindowDTC, UtilityDTC
from Constructors import EmptyConstr
from EventCollections import *
import PaletteStore

PaletteStore.paletteLists['COM'] = []

class wxComModule:
    def __init__(self, GUID = '{00000000-0000-0000-0000-000000000000}', LCID = 0x0, Major = 0, Minor = 0):
        self._ComModule = None
        self._GUID = GUID
        self._LCID = LCID
        self._Major = Major
        self._Minor = Minor

    def GetGUID(self):
        return self._GUID
    def SetGUID(self, GUID):
        self._GUID = GUID

    def GetLCID(self):
        return self._LCID
    def SetLCID(self, LCID):
        self._LCID = LCID

    def GetMajor(self):
        return self._Major
    def SetMajor(self, Major):
        self._Major = Major

    def GetMinor(self):
        return self._Minor
    def SetMinor(self, Minor):
        self._Minor = Minor

    def GetComModule(self):
        if self._ComModule:
            return self._ComModule

    def EnsureModule(self):
        pass
        #self._ComModule = win32com.client.gencache.EnsureModule(self._GUID, self._LCID, self._Major, self._Minor)

class ComModuleDTC(EmptyConstr, UtilityDTC):
    pass

class ComCtrlDTC(WindowDTC):
    GUID = '{00000000-0000-0000-0000-000000000000}'
    comModule = 'comModule'
    comImports = 'ComImports'

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'from wx.lib.bcrtl.activex.%s import %s' % (
                            self.comModule, self.comImports)) )

    def designTimeControl(self, position, size, args = None):
        dtc = WindowDTC.designTimeControl(self, position, size, args)
        dtc.Enable(False)
        return dtc

# Com objects are individually tested and added (or not) to the palette so that
# only components which are installed on the user's machine will be added to
# the Palette

# Acrobat PDF control
try:
    from wx.lib.bcrtl.activex.acrobat import wxComPdf
except ImportError, error:
    print 'Acrobat not registered', error
else:
    class PdfComCDTC(ComCtrlDTC):
        GUID = '{CA8A9783-280D-11CF-A24D-444553540000}'
        comModule = 'acrobat'
        comImports = 'wxComPdf'

    PaletteStore.paletteLists['COM'].append(wxComPdf)
    PaletteStore.compInfo[wxComPdf] = ['AcrobatPdf', PdfComCDTC]

# Internet Explorer webbrowser
try:
    #from wx.lib.bcrtl.activex.IE import *
    from bcrtl.activex.IE import *
except ImportError, error:
    print 'Internet Explorer not registered', error
else:
    EventCategories['WebBrowserEvent'] = (EVT_CWB_BEFORENAVIGATE,
     EVT_CWB_TITLECHANGE, EVT_CWB_DOWNLOADBEGIN, EVT_CWB_PROPERTYCHANGE,
     EVT_CWB_COMMANDSTATECHANGE, EVT_CWB_FRAMEBEFORENAVIGATE,
     EVT_CWB_WINDOWACTIVATE, EVT_CWB_NEWWINDOW, EVT_CWB_DOWNLOADCOMPLETE,
     EVT_CWB_WINDOWRESIZE, EVT_CWB_WINDOWMOVE, EVT_CWB_PROGRESSCHANGE,
     EVT_CWB_FRAMENEWWINDOW, EVT_CWB_STATUSTEXTCHANGE,
     EVT_CWB_FRAMENAVIGATECOMPLETE, EVT_CWB_QUIT, EVT_CWB_NAVIGATECOMPLETE,
    )

    class WebBrowserComCDTC(ComCtrlDTC):
        GUID = '{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}'
        comModule = 'IE'
        comImports = '*'
        def events(self):
            return ComCtrlDTC.events(self) + ['WebBrowserEvent']

    PaletteStore.paletteLists['COM'].append(wxComWebBrowser)
    PaletteStore.compInfo[wxComWebBrowser] = ['IEWebBrowser', WebBrowserComCDTC]



# If any controls successfully installed add the page to the Palette
if len(PaletteStore.paletteLists['COM']):
    PaletteStore.palette.append(['COM', 'Editor/Tabs/COM', PaletteStore.paletteLists['COM']])
