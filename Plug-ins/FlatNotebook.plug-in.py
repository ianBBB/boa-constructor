import wx

import Plugins
from Utils import _

try:
    import wx.lib.flatnotebook
except ImportError:
    raise Plugins.SkipPluginSilently, _('Module %s not found')%'wx.lib.flatnotebook'

from Companions.ContainerCompanions import BookCtrlDTC
from Companions.EventCollections import *

EventCategories['FlatNotebookEvent'] = \
 ('wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGED',
  'wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGING',
  'wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING',
  'wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSED',
  'wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CONTEXT_MENU')

commandCategories.append('FlatNotebookEvent')

class FlatNotebookDTC(BookCtrlDTC):
    bookCtrlName = 'wx.lib.flatnotebook.FlatNotebook'
    def __init__(self, name, designer, parent, ctrlClass):
        BookCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = \
            ['wx.lib.flatnotebook.FNB_VC71', 
             'wx.lib.flatnotebook.FNB_FANCY_TABS', 
             'wx.lib.flatnotebook.FNB_TABS_BORDER_SIMPLE', 
             'wx.lib.flatnotebook.FNB_NO_X_BUTTON',
             'wx.lib.flatnotebook.FNB_NO_NAV_BUTTONS', 
             'wx.lib.flatnotebook.FNB_MOUSE_MIDDLE_CLOSES_TABS',
             'wx.lib.flatnotebook.FNB_BOTTOM', 
             'wx.lib.flatnotebook.FNB_NODRAG', 
             'wx.lib.flatnotebook.FNB_VC8', 
             'wx.lib.flatnotebook.FNB_X_ON_TAB',
             'wx.lib.flatnotebook.FNB_BACKGROUND_GRADIENT', 
             'wx.lib.flatnotebook.FNB_COLORFUL_TABS',
             'wx.lib.flatnotebook.FNB_DCLICK_CLOSES_TABS'] + self.windowStyles

    def designTimeDefaults(self, position = wx.DefaultPosition, size = wx.DefaultSize):
        defs = BookCtrlDTC.designTimeDefaults(self, position = wx.DefaultPosition, size = wx.DefaultSize)
        defs['style'] |= wx.lib.flatnotebook.FNB_NO_X_BUTTON 
        defs['style'] &= ~(wx.lib.flatnotebook.FNB_X_ON_TAB|wx.lib.flatnotebook.FNB_DCLICK_CLOSES_TABS)
        return defs

    def designTimeControl(self, position, size, args = None):
        if args is not None:
            args['style'] |= wx.lib.flatnotebook.FNB_NO_X_BUTTON 
            args['style'] &= ~(wx.lib.flatnotebook.FNB_X_ON_TAB|wx.lib.flatnotebook.FNB_DCLICK_CLOSES_TABS)
        ctrl = BookCtrlDTC.designTimeControl(self, position, size, args)
        ctrl.Bind(wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGED, 
              self.OnPageChanged, id=ctrl.GetId())
        ctrl.SetWindowStyleFlag = lambda s: None
        return ctrl        

    def events(self):
        return BookCtrlDTC.events(self) + ['FlatNotebookEvent']
    
    def writeImports(self):
        return '\n'.join( (BookCtrlDTC.writeImports(self), 'import wx.lib.flatnotebook'))


Plugins.registerComponent('Library', wx.lib.flatnotebook.FlatNotebook, 
      'wx.lib.flatnotebook.FlatNotebook', FlatNotebookDTC)

def getFlatNotebookData():
    return \
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\
\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\x9bIDATH\x89cddbf\xa0%`\xa2\xa9\xe9\xf4\xb0\x80\x05\xc6\xf8\xf7\xf7\xcf\
\x7f\xbc.afa$\xc7\x02FF&f\x86\x7f\x7f\xff\xfc?~\xe48^\x85\xfb\xf6\xefc\xa8\
\xae\xad\xc6j16\xc7\xc1\x1c\xc4\x82\xa1\x03\x0f\xc0\xe6\x88\xe6\x86F\xac\x8e\
knh\xfc_\xdbP\xcf\x88\x12\x07V\xb6Vp\x1a\x99M\t@\xf1\xc1\xb1\xc3\xc7Pht\xb6\
\xa5\x8d%\x86\x01\xd8\xc4\x18\x18 A\x8aa\x01>\xe0\xe4\xe8\x845\x88\x08\x81\
\xa1\x9f\x0fF-\x18\xb5\x80r\x00\xcfh\xb0\x9cGm\xc08Z\xa3\x8dZ@1\x00\x006M0\
\x0b(3z\x16\x00\x00\x00\x00IEND\xaeB`\x82' 

Preferences.IS.registerImage('Images/Palette/wx.lib.flatnotebook.FlatNotebook.png', getFlatNotebookData())
