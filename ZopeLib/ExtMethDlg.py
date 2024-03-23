#-----------------------------------------------------------------------------
# Name:        ExtMethDlg.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ExtMethDlg

import os

import wx

def create(parent, zopepath):
    return ExtMethDlg(parent, zopepath)

class ExternalMethodFinder:
    def __init__(self, zopeDir):
        self.zopeDir = zopeDir
        if self.zopeDir:
            prodsDir = os.path.join(zopeDir, 'lib','python','Products')
            if not os.path.exists(prodsDir):
                prodsDir = os.path.join(zopeDir, 'Products')
                if not os.path.exists(prodsDir):
                    prodsDir = ''
        else:
            prodsDir = ''
        self.prodsDir = prodsDir

    def getModules(self):
        mods = self._addPyMods(os.path.join(self.zopeDir, 'Extensions'))

        if self.prodsDir:
            prods = os.listdir(self.prodsDir)
            for p in prods:
                if os.path.exists(os.path.join(self.prodsDir, p)) and \
                      os.path.exists(os.path.join(self.prodsDir, p, 'Extensions')):
                    mods.extend(self._addPyMods(os.path.join(self.prodsDir, p,
                          'Extensions'), p))
        return mods

    def _addPyMods(self, pypath, prod=''):
        from Explorers import Explorer
        Explorer.listdirEx(pypath, '.zexp')
        mods = []
        fls = Explorer.listdirEx(pypath, '.py')
        for file in fls:
            mods.append(prod +(prod and '.')+os.path.splitext(file)[0])
        return mods

    def getExtPath(self, module):
        modLst = module.split('.')
        if len(modLst) == 1:
            modpath = os.path.join(self.zopeDir, 'Extensions', modLst[0] + '.py')
        else:
            modpath = os.path.join(self.prodsDir, modLst[0], 'Extensions', modLst[1]+'.py')
        return modpath.replace('<LocalFS::directory>', '<LocalFS::file>')

    def getFunctions(self, module):
        from Explorers import Explorer
        extPath = self.getExtPath(module)

        src = Explorer.openEx(extPath).load()
        sep = src.count('\r\n') < src.count('\n') and '\n' or '\r\n'
        srclines = src.split(sep)

        import moduleparse
        module = moduleparse.Module('test', srclines)

        return module.functions.keys()


[wxID_EXTMETHDLG, wxID_EXTMETHDLGBTCANCEL, wxID_EXTMETHDLGBTOK, 
 wxID_EXTMETHDLGCBMODULE, wxID_EXTMETHDLGCHFUNCTION, wxID_EXTMETHDLGPANEL1, 
 wxID_EXTMETHDLGSTATICTEXT1, wxID_EXTMETHDLGSTATICTEXT2, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(8)]

class ExtMethDlg(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_EXTMETHDLG, name='ExtMethDlg',
              parent=prnt, pos=wx.Point(363, 248), size=wx.Size(267, 141),
              style=wx.DEFAULT_DIALOG_STYLE, title='Add External Method')
        self.SetClientSize(wx.Size(259, 114))

        self.panel1 = wx.Panel(id=wxID_EXTMETHDLGPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(259, 114),
              style=wx.TAB_TRAVERSAL)

        self.staticText1 = wx.StaticText(id=wxID_EXTMETHDLGSTATICTEXT1,
              label='Module:', name='staticText1', parent=self.panel1,
              pos=wx.Point(8, 16), size=wx.Size(56, 13), style=0)

        self.staticText2 = wx.StaticText(id=wxID_EXTMETHDLGSTATICTEXT2,
              label='Function:', name='staticText2', parent=self.panel1,
              pos=wx.Point(8, 48), size=wx.Size(56, 13), style=0)

        self.cbModule = wx.ComboBox(choices=[], id=wxID_EXTMETHDLGCBMODULE,
              name='cbModule', parent=self.panel1, pos=wx.Point(72, 8),
              size=wx.Size(176, 21), style=0, value='')
        self.cbModule.Bind(wx.EVT_COMBOBOX, self.OnCbmoduleCombobox,
              id=wxID_EXTMETHDLGCBMODULE)

        self.chFunction = wx.ComboBox(choices=[], id=wxID_EXTMETHDLGCHFUNCTION,
              name='chFunction', parent=self.panel1, pos=wx.Point(72, 40),
              size=wx.Size(176, 21), style=0, value='')
        self.chFunction.Bind(wx.EVT_COMBOBOX, self.OnChfunctionCombobox,
              id=wxID_EXTMETHDLGCHFUNCTION)

        self.btOK = wx.Button(id=wxID_EXTMETHDLGBTOK, label='OK', name='btOK',
              parent=self.panel1, pos=wx.Point(96, 80), size=wx.Size(72, 24),
              style=0)
        self.btOK.Bind(wx.EVT_BUTTON, self.OnBtokButton, id=wxID_EXTMETHDLGBTOK)

        self.btCancel = wx.Button(id=wxID_EXTMETHDLGBTCANCEL, label='Cancel',
              name='btCancel', parent=self.panel1, pos=wx.Point(176, 80),
              size=wx.Size(72, 24), style=0)
        self.btCancel.Bind(wx.EVT_BUTTON, self.OnBtcancelButton,
              id=wxID_EXTMETHDLGBTCANCEL)

    def __init__(self, parent, zopeDir):
        self._init_ctrls(parent)

        self.emf = ExternalMethodFinder(zopeDir)

        for mod in self.emf.getModules():
            self.cbModule.Append(mod)

    def OnBtokButton(self, event):
        self.EndModal(wx.ID_OK)

    def OnBtcancelButton(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnCbmoduleCombobox(self, event):
        if self.emf.zopeDir:
            self.chFunction.Clear()
            mod = self.cbModule.GetStringSelection()

            functions = self.emf.getFunctions(mod)

            for func in functions:
                self.chFunction.Append(func)

    def OnChfunctionCombobox(self, event):
        pass


if __name__ == '__main__':
    app = wx.App()
    dlg = create(None, '.')
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
