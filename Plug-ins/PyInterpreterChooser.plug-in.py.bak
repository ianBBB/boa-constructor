#-----------------------------------------------------------------------------
# Name:        PyInterpreterChooser.plug-in.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2003/07/20
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:PyInterpreterChooserDlg
import os, sys

import wx

from Utils import _, resetMinSize

PyCoreRegPath = 'SOFTWARE\\Python\\Pythoncore'

[wxID_PYINTERPRETERCHOOSERDLG, wxID_PYINTERPRETERCHOOSERDLGBTNCANCEL, 
 wxID_PYINTERPRETERCHOOSERDLGBTNOK, 
 wxID_PYINTERPRETERCHOOSERDLGGDCINSTALLPATH, 
 wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS, 
 wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT1, 
 wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT2, 
 wxID_PYINTERPRETERCHOOSERDLGTXTPYINTPPATH, 
] = [wx.NewId() for _init_ctrls in range(8)]

class PyInterpreterChooserDlg(wx.Dialog):
    def _init_coll_browserSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.lcInstallations, 1, border=10,
              flag=wx.GROW | wx.ALL)
        parent.AddWindow(self.gdcInstallPath, 1, border=10,
              flag=wx.GROW | wx.ALL)

    def _init_coll_buttonsSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.btnOK, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)
        parent.AddWindow(self.btnCancel, 0, border=10,
              flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_coll_mainSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText1, 0, border=10,
              flag=wx.EXPAND | wx.ALL)
        parent.AddSizer(self.browserSizer, 1, border=0, flag=wx.GROW)
        parent.AddWindow(self.staticText2, 0, border=10,
              flag=wx.EXPAND | wx.ALL)
        parent.AddWindow(self.txtPyIntpPath, 0, border=10,
              flag=wx.GROW | wx.ALL)
        parent.AddSizer(self.buttonsSizer, 0, border=0,
              flag=wx.ALIGN_RIGHT | wx.ALL)

    def _init_coll_lcInstallations_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT,
              heading=_('Version'), width=60)
        parent.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT,
              heading=_('Install Path'), width=170)

    def _init_sizers(self):
        # generated method, don't edit
        self.mainSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.browserSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.buttonsSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_mainSizer_Items(self.mainSizer)
        self._init_coll_browserSizer_Items(self.browserSizer)
        self._init_coll_buttonsSizer_Items(self.buttonsSizer)

        self.SetSizer(self.mainSizer)

    def _init_utils(self):
        # generated method, don't edit
        self.images = wx.ImageList(height=16, width=16)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_PYINTERPRETERCHOOSERDLG,
              name='PyInterpreterChooserDlg', parent=prnt, pos=wx.Point(548,
              354), size=wx.Size(532, 358),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('Python Interpreter Chooser'))
        self._init_utils()
        self.SetClientSize(wx.Size(524, 331))
        self.Center(wx.BOTH)

        self.staticText1 = wx.StaticText(id=wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT1,
              label=_('Found installations: (double click to select)'),
              name='staticText1', parent=self, pos=wx.Point(10, 10),
              size=wx.Size(203, 13), style=0)

        self.gdcInstallPath = wx.GenericDirCtrl(defaultFilter=0, dir='.',
              filter=self.installPathFilter,
              id=wxID_PYINTERPRETERCHOOSERDLGGDCINSTALLPATH,
              name='gdcInstallPath', parent=self, pos=wx.Point(272, 52),
              size=wx.Size(242, 146),
              style=wx.DIRCTRL_SHOW_FILTERS | wx.DIRCTRL_3D_INTERNAL | wx.NO_BORDER)

        self.lcInstallations = wx.ListView(id=wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS,
              name='lcInstallations', parent=self, pos=wx.Point(10, 52),
              size=wx.Size(242, 146), style=wx.SUNKEN_BORDER | wx.LC_REPORT,
              validator=wx.DefaultValidator)
        self._init_coll_lcInstallations_Columns(self.lcInstallations)
        self.lcInstallations.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
              self.OnLcinstallationsListItemActivated,
              id=wxID_PYINTERPRETERCHOOSERDLGLCINSTALLATIONS)

        self.staticText2 = wx.StaticText(id=wxID_PYINTERPRETERCHOOSERDLGSTATICTEXT2,
              label=_('Current interpreter path (Blank means sys.executable will be used.)'),
              name='staticText2', parent=self, pos=wx.Point(10, 218),
              size=wx.Size(504, 19), style=0)

        self.txtPyIntpPath = wx.TextCtrl(id=wxID_PYINTERPRETERCHOOSERDLGTXTPYINTPPATH,
              name='txtPyIntpPath', parent=self, pos=wx.Point(10, 257),
              size=wx.Size(504, 21), style=0, value=self.pythonInterpreterPath)

        self.btnOK = wx.Button(id=wx.ID_OK, label=_('OK'), name='btnOK',
              parent=self, pos=wx.Point(287, 298), size=wx.Size(101, 23),
              style=0)

        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='btnCancel', parent=self, pos=wx.Point(408, 298),
              size=wx.Size(106, 23), style=0)

        self._init_sizers()

    def __init__(self, parent, currentPyIntpPath=''):
        self.pythonInterpreterPath = ''
        self.pythonInterpreterPath = currentPyIntpPath
        self.installPathFilter = '(*.exe)|*.exe)'
        self.installPathFilter = self.getInstallPathFilter()

        self._init_ctrls(parent)
        
        # adjust sizes for different platforms
        resetMinSize(self)
        self.gdcInstallPath.SetMinSize(wx.Size(242, 146))
        self.SetSizerAndFit(self.mainSizer)

        self.populateFoundInstallations()

        self.gdcInstallPath.GetChildren()[0].Bind(wx.EVT_LEFT_DCLICK,
             self.OnGdcinstallpathLeftDclick)

    def populateFoundInstallations(self):
        paths = self.installedPaths = self.getInstallations()
        for idx, (version, path) in zip(range(len(paths)), paths):
            self.lcInstallations.InsertStringItem(idx, version)
            self.lcInstallations.SetStringItem(idx, 1, path)

        if not hasattr(sys, 'frozen'):
            # Bold the current installation
            li = self.lcInstallations.GetItem(0)
            f = li.GetFont()
            f.SetWeight(wx.BOLD)
            li.SetFont(f)
            self.lcInstallations.SetItem(li)

    def getInstallations(self):
        if hasattr(sys, 'frozen'):
            res = []
        else:
            res = [(self.sysBinVer, sys.executable)]

        import Preferences
        for path in Preferences.picExtraPaths:
            if os.path.exists(path):
                res.append( ('?', path) )

        # XXX search common locations on Linux and Mac?

        try:
            import _winreg as winreg
        except ImportError:
            return res

        # Windows, add pythons defined in registry
        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, PyCoreRegPath)
        except EnvironmentError:
            return res

        idx = 0
        versions = []
        try:
            while True:
                versions.append(winreg.EnumKey(reg, idx))
                idx += 1
        except EnvironmentError:
            pass

        if not hasattr(sys, 'frozen'):
            try: 
                versions.remove(self.sysBinVer)
            except ValueError: 
                pass

        for version in versions:
            try:
                reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     '%s\\%s'%(PyCoreRegPath, version))
            except EnvironmentError:
                continue
            try:
                pyIntpPath = os.path.join(winreg.QueryValue(reg, 'InstallPath'),
                                      'Python.exe')
            except WindowsError:
                continue
            
            if os.path.exists(pyIntpPath):
                try:
                    res.index( (version, pyIntpPath) )
                except ValueError:
                    res.append( (version, pyIntpPath) )

        return res

    def OnGdcinstallpathLeftDclick(self, event):
        event.Skip()
        currPath = self.gdcInstallPath.GetFilePath()
        self.updatePyIntpPath(currPath)

    def OnLcinstallationsListItemActivated(self, event):
        idx = self.lcInstallations.GetFirstSelected()
        path = self.lcInstallations.GetItem(idx, 1).GetText()
        self.updatePyIntpPath(path)

    def getInstallPathFilter(self):
        self.sysBinDir, self.sysBinName = os.path.split(sys.executable)
        self.sysBinVer = '%d.%d'%sys.version_info[:2]

        ext = '*%s'%os.path.splitext(self.sysBinName)[1]
        if ext == '*':
            return ''
        else:
            return '(%s)|%s'%(ext, ext)

    def updatePyIntpPath(self, path):
        if path == sys.executable:
            path = ''

        self.txtPyIntpPath.SetValue(path)




if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = PyInterpreterChooserDlg(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()

#-------------------------------------------------------------------------------

# warn the user if the Preferences.pythonInterpreterPath is not valid
def checkInterpreter():
    if hasattr(sys, 'frozen') and not Preferences.pythonInterpreterPath:
        wx.LogWarning(_('No interpreter set to run programs with.\n'
                      'Please set it up as soon as possible via:\n'
                      'Tools->Python interpreter chooser'))
wx.CallAfter(checkInterpreter)

#-------------------------------------------------------------------------------

import Preferences, Utils, Plugins

def openPyInterpChooser(editor):
    dlg = PyInterpreterChooserDlg(editor, Preferences.pythonInterpreterPath)
    try:
        if dlg.ShowModal() != wx.ID_OK:
            return

        pyIntpPath = dlg.txtPyIntpPath.GetValue()

        if pyIntpPath != Preferences.pythonInterpreterPath:
            Plugins.updateRcFile('prefs.rc.py', 'pythonInterpreterPath', repr(pyIntpPath))

            for ver, path in dlg.installedPaths:
                if path == pyIntpPath:
                    break
            else:
                for path in Preferences.picExtraPaths:
                    if path == pyIntpPath:
                        break
                else:
                    Plugins.updateRcFile('prefs.plug-ins.rc.py', 'picExtraPaths',
                        repr(Preferences.picExtraPaths+[pyIntpPath]))
    finally:
        dlg.Destroy()

_('Additional locations to choose the Python Interpreter Path from.')

Plugins.registerPreference('PyInterpreterChooser', 'picExtraPaths', '[]',
                          ['Additional locations to choose the Python '
                            'Interpreter Path from.'])
Plugins.registerTool(_('Python interpreter chooser'), openPyInterpChooser,
                       'Images/PyInterpreterChooser.png')

#-------------------------------------------------------------------------------

def getPyInterpreterChooserImgData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x01}IDAT(\x91uR!\x92\x1bA\x0cl\xe7\xfc\x00AC=A?\x88~\x90}\xc2\xc0@\xff\xe0\
\xc6,p\xf3\x03\x85\x1d\xdc\x1fXf\x81\x13f\xd8a\x07\x87\x1a9`\xd6\xf69\xa9\
\xa8\x06\xa8Fj\xa9\xba\xd5\xb8\xde\xa2\x14W\x85;J\xf1\xeb\x7f""6\xd7\xeb\xf5\
t:E\x84jd\xc2\x1d$\x80RJ\xc1?\x91\x99\xdb\x91\x91T\xad\xee\xb5\xd6\xab\xfbF\
\xa4\x93\xfc\xd8*""\x02\xe0\x01\x00*\x89Z7$2\x17\x11133\x1b\r\xaa:Fl2\xb3Vw\
\x7f^\r(\x01\xa0w\xdb\xef\xe7; 3_\xc8PE\xef\x10\x01\x00*\x96\t\xed\x0b\xda/L\
\x82\xdd\xee=\x13f&"\xbdw\x92[*\xd4\x01\x80@\x0e\xc6\x05\x1a\xb83 \x03x\x08\
\xb0U\xf5\xf4\\k\x05\x00\xbc"\x0b\xbc"\x81[\xe5\x11\x9f\x8e\xafG*B\xa1\xe3\
\x05\xfabE\x0bu\xa5!bO\x80A\xb1&HP\xe1\xb5Lb\xe9\xe1\t%H\xb8?\x1dd\x8b\xc3\
\xa1\x9b\xc9\xac.bf\x94\xa8\xaf\xad\xfcX\xbb\xcd\xe6\xbb\xb2C\xfd\x97z<^.\
\x171kmi\x12?\xbf\xbe\xef\xbfC:H\xb4ff\xb6\xdb\xed"BD\xce\xe7\xf3\xdb\xdb\
\xb7\xd5\x1a\xcb\xb2\xcc\xd3\x8c\xcf\xa8\x871i\x1c\x0b$z7\xb36~\xc8\xdb\xa5[\
k>\x81\xbfq\xbb\xeb\xc7\xa4\rz\x00\x14e\xdd\xd0Z\x9be\xaf\x8aU\x9c\x04\xf5\
\x06\xab\x98\xa6y\xe0{\xef\x9b\x88\x18&!\x19\x1aJ\x00\xeap\xac\x06\xc3_\xb6\
\xf9\x03t}\xfb\xbaG1\'\x18\x00\x00\x00\x00IEND\xaeB`\x82' 


Preferences.IS.registerImage('Images/PyInterpreterChooser.png', getPyInterpreterChooserImgData())
    
