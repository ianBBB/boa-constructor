#Boa:Frame:BomTempFrame

import wx


def create(parent):
    return BomTempFrame(parent)


[wxID_BOMTEMPFRAME, wxID_BOMTEMPFRAMEBUTTON1] = [wx.NewIdRef(count=1) for _init_ctrls in range(2)]


class BomTempFrame(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_BOMTEMPFRAME, name='', parent=prnt,
              pos=wx.Point(120, 120), size=wx.Size(360, 160),
              style=wx.DEFAULT_FRAME_STYLE, title='BOM Temp Frame')
        self.SetClientSize(wx.Size(352, 133))

        self.button1 = wx.Button(id=wxID_BOMTEMPFRAMEBUTTON1,
              label='BOM-tolerant test file', name='button1', parent=self,
              pos=wx.Point(88, 48), size=wx.Size(176, 24), style=0)
        self.button1.Bind(wx.EVT_BUTTON, self.OnButton1Button,
              id=wxID_BOMTEMPFRAMEBUTTON1)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnButton1Button(self, event):
        wx.MessageBox('This file started with a UTF-8 BOM before #Boa:.')


if __name__ == '__main__':
    app = wx.App()
    frame = create(None)
    frame.Show()
    app.MainLoop()
