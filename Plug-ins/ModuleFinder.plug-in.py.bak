#Boa:Dialog:ModuleFinderDlg

import sys, imp

import wx

import Preferences
import Utils
from Utils import _, resetMinSize

#-------------------------------------------------------------------------------

[wxID_MODULEFINDERDLG, wxID_MODULEFINDERDLGCANCELBTN, 
 wxID_MODULEFINDERDLGOKBTN, wxID_MODULEFINDERDLGSTATICTEXT1, 
 wxID_MODULEFINDERDLGTXTMODULENAME, 
] = [wx.NewId() for _init_ctrls in range(5)]

class ModuleFinderDlg(wx.Dialog):
    def _init_coll_mainSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText1, 0, border=10,
              flag=wx.ALL | wx.EXPAND)
        parent.AddWindow(self.txtModuleName, 0, border=10,
              flag=wx.EXPAND | wx.RIGHT | wx.LEFT)
        parent.AddSizer(self.buttonsSizer, 0, border=10,
              flag=wx.ALIGN_RIGHT | wx.ALL)

    def _init_coll_buttonsSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.okBtn, 0, border=10, flag=wx.RIGHT)
        parent.AddWindow(self.cancelBtn, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.mainSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.buttonsSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_mainSizer_Items(self.mainSizer)
        self._init_coll_buttonsSizer_Items(self.buttonsSizer)

        self.SetSizer(self.mainSizer)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_MODULEFINDERDLG,
              name='ModuleFinderDlg', parent=prnt, pos=wx.Point(858, 575),
              size=wx.Size(317, 135),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('Module finder for sys.path'))
        self.SetClientSize(wx.Size(309, 106))
        self.Center(wx.BOTH)

        self.staticText1 = wx.StaticText(id=wxID_MODULEFINDERDLGSTATICTEXT1,
              label=_('Module name:'), name='staticText1', parent=self,
              pos=wx.Point(10, 10), size=wx.Size(289, 16), style=0)

        self.txtModuleName = wx.TextCtrl(id=wxID_MODULEFINDERDLGTXTMODULENAME,
              name='txtModuleName', parent=self, pos=wx.Point(10, 36),
              size=wx.Size(289, 21), style=0, value='')

        self.okBtn = wx.Button(id=wx.ID_OK, label=_('OK'), name='okBtn',
              parent=self, pos=wx.Point(139, 67), size=wx.Size(75, 23),
              style=0)
        self.okBtn.SetDefault()

        self.cancelBtn = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='cancelBtn', parent=self, pos=wx.Point(224, 67),
              size=wx.Size(75, 23), style=0)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)

        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(Preferences.IS.load('Images/ModuleFinder.png'))
        self.SetIcon(icon)
        
        # adjust sizes for different platforms
        resetMinSize(self)
        self.SetMinSize(wx.Size(309, 106))
        self.SetSizerAndFit(self.mainSizer)

#-------------------------------------------------------------------------------

def openModuleFinder(editor):
    dlg = ModuleFinderDlg(editor)
    try:
        while dlg.ShowModal() == wx.ID_OK:
            modName = dlg.txtModuleName.GetValue()
            try:
                f, filename, (ext, mode, type) = \
                      Utils.find_dotted_module(modName)#, sys.path)
            except ImportError, err:
                wx.LogError(_('%s not found on sys.path (%s).')%(modName, str(err)))
            else:
                if f is not None:
                    f.close()
                if filename:
                    if type == imp.PKG_DIRECTORY:
                        editor.openOrGotoModule(os.path.join(filename, '__init__.py'))
                    elif type in (imp.PY_SOURCE, imp.C_EXTENSION):
                        editor.openOrGotoModule(filename)
                return
    finally:
        dlg.Destroy()


if wx.Platform == '__WXMSW__':
    keyIdent = 'ModuleFinder'
    Preferences.keyDefs[keyIdent] = (wx.ACCEL_ALT, ord('M'), 'Alt-M')
else:
    keyIdent = ''

import Plugins
Plugins.registerTool(_('Module finder'), openModuleFinder,
                     'Images/ModuleFinder.png', keyIdent)

#-------------------------------------------------------------------------------

def getModuleFinderImgData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\x1aIDATx\x9c\xa5\x93]j\xc30\x10\x84?\x95\x1c@\xd7\xf1\x12\x08\xd5\
\x89J\xf0[J\x7f\xc2\xe6-\x94\x9eH\x10\x12\xd6\xd7\xc9\x01\n\xdb\x07[\x8a\x9d\
\xba$\xa5\x0bb\xd7\x1efX\xcd\xa0\x10c\xe4?\xb5(C\xbbn\xfd\x1a\xdc\x7f\xec\
\xc3]\x02\xed\xba\xf5\xf4\x98\x90\xa5`\'\xab\x1d\xf0["\x8b\xdf\xc8\xb2\x14\
\x8c^d\x8eX\x85u\xab>.;\x9a\xab\xaa\xab\xaa\x03\xae:\xc5\xdd\xddu\xdbc1\xc6\
\x8b\x00N%\xfb\xf0\xc7\xdd\xabH\xc1q&\x02\xd5D;\x19\xf9\x90\xd9l6@\x00\x9c\
\x00\x98\x19"\x82\xad.\xd7\xcb\xe4z\x95\x872\xc8R\x86\xa9\x90\x03\xd6uH\xd3T\
\xbcx3\xae*0\xb8>"\x1b\xd24X\xd7U|\x94\xce\xfc\x06i\x95\xd8\xedv\x13\xb2\x88\
\xa0\xaa\xe4\xc3\xfc\x06\x13\x0fJt9g\x10A\x00U%\xa5D#\x00\x82\x1d\xa7\x1e\
\xfcHa\xae\xbfA\x9f\n\xfd\x19\xa7\x10\x86\x8f\x9b\xf5\xf5\xf2\xcc\xab\x0f\
\x1e\x0f-\xc6\x18\x18\x1e\x93\xdfs\xae7\x891\x12\xfe\xfa\x1a\x9f\xceg/\x9b\
\xbc\x8fM\xbc\xb7>c\x0c\x84\xb3\x97\xf9\x1b\xa7\x9e\xfe\x8e\xda\xadz\x91\x00\
\x00\x00\x00IEND\xaeB`\x82'

Preferences.IS.registerImage('Images/ModuleFinder.png', getModuleFinderImgData())
