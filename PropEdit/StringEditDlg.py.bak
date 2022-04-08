#Boa:Dialog:StringEditDlg

import wx

from Utils import _

def create(parent):
    return StringEditDlg(parent, 'test')

[wxID_STRINGEDITDLG, wxID_STRINGEDITDLGBUTTON1, wxID_STRINGEDITDLGBUTTON2, 
 wxID_STRINGEDITDLGI18NCB, wxID_STRINGEDITDLGSTRINGTC, 
] = [wx.NewId() for _init_ctrls in range(5)]

class StringEditDlg(wx.Dialog):
    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stringTC, 1, border=10, flag=wx.GROW | wx.ALL)
        parent.AddSizer(self.boxSizer2, 0, border=10, flag=wx.ALL | wx.GROW)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.i18nCB, 1, border=0, flag=wx.ALL | wx.GROW)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=wx.ALL | wx.GROW)
        parent.AddWindow(self.button1, 0, border=0, flag=wx.ALIGN_RIGHT)
        parent.AddSpacer(wx.Size(8, 8), border=10, flag=0)
        parent.AddWindow(self.button2, 0, border=0, flag=wx.ALIGN_RIGHT)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_STRINGEDITDLG, name='StringEditDlg',
              parent=prnt, pos=wx.Point(519, 228), size=wx.Size(411, 324),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('String Edit Dialog'))
        self.SetClientSize(wx.Size(403, 297))

        self.stringTC = wx.TextCtrl(id=wxID_STRINGEDITDLGSTRINGTC,
              name='stringTC', parent=self, pos=wx.Point(10, 10),
              size=wx.Size(383, 233), style=wx.TE_MULTILINE, value='')

        self.button1 = wx.Button(id=wx.ID_OK, label=_('OK'), name='button1',
              parent=self, pos=wx.Point(235, 263), size=wx.Size(75, 23),
              style=0)

        self.button2 = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='button2', parent=self, pos=wx.Point(318, 263),
              size=wx.Size(75, 23), style=0)

        self.i18nCB = wx.CheckBox(id=wxID_STRINGEDITDLGI18NCB, label='I18N',
              name='i18nCB', parent=self, pos=wx.Point(10, 263),
              size=wx.Size(217, 24), style=0)
        self.i18nCB.SetValue(False)

        self._init_sizers()

    def __init__(self, parent, strSrc, companion):
        self._init_ctrls(parent)
        
        self.i18nCB.SetValue(strSrc.startswith('_('))
        self.stringTC.SetValue(companion.eval(strSrc))

    def getStrSrc(self):
        strSrc = `self.stringTC.GetValue()`
        if self.i18nCB.GetValue():
            return'_(%r)'%self.stringTC.GetValue()
        else:
            return repr(self.stringTC.GetValue())
            
        

if __name__ == '__main__':
    app = wx.PySimpleApp()

    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
