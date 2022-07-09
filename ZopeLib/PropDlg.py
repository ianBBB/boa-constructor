#Boa:Dialog:NewPropDlg

import wx

def create(parent):
    return NewPropDlg(parent)

[wxID_NEWPROPDLG, wxID_NEWPROPDLGBTCANCEL, wxID_NEWPROPDLGBTOK, 
 wxID_NEWPROPDLGCHTYPE, wxID_NEWPROPDLGPANEL1, wxID_NEWPROPDLGSTATICTEXT1, 
 wxID_NEWPROPDLGSTATICTEXT2, wxID_NEWPROPDLGSTATICTEXT3, 
 wxID_NEWPROPDLGTCPROPNAME, wxID_NEWPROPDLGTCVALUE, 
] = [wx.NewId() for _init_ctrls in range(10)]

class NewPropDlg(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_NEWPROPDLG, name='NewPropDlg',
              parent=prnt, pos=wx.Point(359, 240), size=wx.Size(221, 169),
              style=wx.DEFAULT_DIALOG_STYLE, title='New property')
        self.SetClientSize(wx.Size(213, 142))

        self.panel1 = wx.Panel(id=wxID_NEWPROPDLGPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(213, 142),
              style=wx.TAB_TRAVERSAL)

        self.staticText1 = wx.StaticText(id=wxID_NEWPROPDLGSTATICTEXT1,
              label='Name:', name='staticText1', parent=self.panel1,
              pos=wx.Point(8, 16), size=wx.Size(40, 16), style=0)

        self.tcPropName = wx.TextCtrl(id=wxID_NEWPROPDLGTCPROPNAME,
              name='tcPropName', parent=self.panel1, pos=wx.Point(56, 8),
              size=wx.Size(144, 24), style=0, value='')

        self.staticText3 = wx.StaticText(id=wxID_NEWPROPDLGSTATICTEXT3,
              label='Value:', name='staticText3', parent=self.panel1,
              pos=wx.Point(8, 48), size=wx.Size(40, 13), style=0)

        self.tcValue = wx.TextCtrl(id=wxID_NEWPROPDLGTCVALUE, name='tcValue',
              parent=self.panel1, pos=wx.Point(56, 40), size=wx.Size(144, 24),
              style=0, value='')

        self.staticText2 = wx.StaticText(id=wxID_NEWPROPDLGSTATICTEXT2,
              label='Type:', name='staticText2', parent=self.panel1,
              pos=wx.Point(8, 80), size=wx.Size(40, 13), style=0)

        self.chType = wx.Choice(choices=['boolean', 'date', 'float', 'int',
              'lines', 'long', 'string', 'text', 'tokens', 'selection',
              'multiple selection'], id=wxID_NEWPROPDLGCHTYPE, name='chType',
              parent=self.panel1, pos=wx.Point(56, 72), size=wx.Size(144, 21),
              style=0)
        self.chType.SetSelection(6)
        self.chType.SetToolTip('Property type')

        self.btOK = wx.Button(id=wxID_NEWPROPDLGBTOK, label='OK', name='btOK',
              parent=self.panel1, pos=wx.Point(48, 112), size=wx.Size(72, 24),
              style=0)
        self.btOK.Bind(wx.EVT_BUTTON, self.OnBtokButton, id=wxID_NEWPROPDLGBTOK)

        self.btCancel = wx.Button(id=wxID_NEWPROPDLGBTCANCEL, label='Cancel',
              name='btCancel', parent=self.panel1, pos=wx.Point(128, 112),
              size=wx.Size(72, 24), style=0)
        self.btCancel.Bind(wx.EVT_BUTTON, self.OnBtcancelButton,
              id=wxID_NEWPROPDLGBTCANCEL)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnBtokButton(self, event):
        self.EndModal(wx.ID_OK)

    def OnBtcancelButton(self, event):
        self.EndModal(wx.ID_CANCEL)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    frame.Show(True)
    app.MainLoop()
