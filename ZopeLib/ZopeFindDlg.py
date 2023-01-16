#-----------------------------------------------------------------------------
# Name:        ZopeFindDlg.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ZopeFindDlg

import wx

def create(parent):
    return ZopeFindDlg(parent)

[wxID_ZOPEFINDDLG, wxID_ZOPEFINDDLGBUTTON1, wxID_ZOPEFINDDLGBUTTON2,
 wxID_ZOPEFINDDLGMETATYPE, wxID_ZOPEFINDDLGOBJIDS, wxID_ZOPEFINDDLGRECURSE,
 wxID_ZOPEFINDDLGSEARCHTEXT, wxID_ZOPEFINDDLGSTATICTEXT1,
 wxID_ZOPEFINDDLGSTATICTEXT2, wxID_ZOPEFINDDLGSTATICTEXT3,
] = [wx.NewIdRef(count=1) for _init_ctrls in range(10)]

class ZopeFindDlg(wx.Dialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_ZOPEFINDDLG, name='ZopeFindDlg',
              parent=prnt, pos=wx.Point(653, 438), size=wx.Size(319, 188),
              style=wx.DEFAULT_DIALOG_STYLE, title='Zope find dialog')
        self._init_utils()
        self.SetClientSize(wx.Size(311, 161))
        self.Center(wx.BOTH)

        self.staticText1 =wx.StaticText(id=wxID_ZOPEFINDDLGSTATICTEXT1,
              label='Find objects of type:', name='staticText1', parent=self,
              pos=wx.Point(8, 8), size=wx.Size(120, 16), style=0)

        self.metaType =wx.Choice(choices=['All types'],
              id=wxID_ZOPEFINDDLGMETATYPE, name='metaType', parent=self,
              pos=wx.Point(136, 8), size=wx.Size(168, 21), style=0,
              validator=wx.DefaultValidator)
        self.metaType.SetSelection(0)
        self.metaType.Enable(False)

        self.staticText2 =wx.StaticText(id=wxID_ZOPEFINDDLGSTATICTEXT2,
              label='with ids:\n(comma separated)', name='staticText2',
              parent=self, pos=wx.Point(8, 40), size=wx.Size(120, 32), style=0)

        self.objIds =wx.TextCtrl(id=wxID_ZOPEFINDDLGOBJIDS, name='objIds',
              parent=self, pos=wx.Point(136, 40), size=wx.Size(168, 21), style=0,
              value='')

        self.staticText3 =wx.StaticText(id=wxID_ZOPEFINDDLGSTATICTEXT3,
              label='containing:', name='staticText3', parent=self,
              pos=wx.Point(8, 72), size=wx.Size(72, 16), style=0)

        self.searchText =wx.TextCtrl(id=wxID_ZOPEFINDDLGSEARCHTEXT,
              name='searchText', parent=self, pos=wx.Point(136, 72),
              size=wx.Size(168, 21), style=0, value='')

        self.button1 =wx.Button(id=wx.ID_OK, label='Find', name='button1',
              parent=self, pos=wx.Point(144, 128), size=wx.Size(75, 23), style=0)

        self.button2 =wx.Button(id=wx.ID_CANCEL, label='Cancel', name='button2',
              parent=self, pos=wx.Point(228, 128), size=wx.Size(76, 23), style=0)

        self.recurse =wx.CheckBox(id=wxID_ZOPEFINDDLGRECURSE, label='recurse',
              name='recurse', parent=self, pos=wx.Point(8, 104), size=wx.Size(73,
              13), style=0)
        self.recurse.SetValue(True)

    def __init__(self, parent):
        self._init_ctrls(parent)

        self.button1.SetFocus()
        self.objIds.SetFocus()


if __name__ == '__main__':
    app =wx.PySimpleApp()
    wx.InitAllImageHandlers()
    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
