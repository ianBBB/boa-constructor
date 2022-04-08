#Boa:Dialog:PathsMappingDlg

import pprint

import wx

from Utils import _

from PathsPanel import PathsPanel

def create(parent):
    return PathsMappingDlg(parent)

[wxID_PATHSMAPPINGDLG, wxID_PATHSMAPPINGDLGCANCELBTN, 
 wxID_PATHSMAPPINGDLGOKBTN, wxID_PATHSMAPPINGDLGPATHSPANEL, 
] = [wx.NewId() for _init_ctrls in range(4)]

class PathsMappingDlg(wx.Dialog):
    _custom_classes = {'wx.Panel': ['PathsPanel'],}
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_PATHSMAPPINGDLG,
              name='PathsMappingDlg', parent=prnt, pos=wx.Point(345, 257),
              size=wx.Size(489, 293), style=wx.DEFAULT_DIALOG_STYLE,
              title=_('Edit client/sever paths mapping'))
        self.SetClientSize(wx.Size(481, 266))

        self.pathsPanel = PathsPanel(id=wxID_PATHSMAPPINGDLGPATHSPANEL,
              name='pathsPanel', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(480, 216), style=wx.TAB_TRAVERSAL)

        self.okBtn = wx.Button(id=wx.ID_OK, label=_('OK'), name='okBtn',
              parent=self, pos=wx.Point(320, 232), size=wx.Size(75, 23),
              style=0)
        self.okBtn.Bind(wx.EVT_BUTTON, self.OnOkbtnButton,
              id=wxID_PATHSMAPPINGDLGOKBTN)

        self.cancelBtn = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='cancelBtn', parent=self, pos=wx.Point(400, 232),
              size=wx.Size(75, 23), style=0)

    def __init__(self, parent, paths):
        self._init_ctrls(parent)

        self.pathsPanel.init_paths(paths)

        import Utils
        self.conf = Utils.createAndReadConfig('Explorer')
        self.writeConfig = Utils.writeConfig

    def OnOkbtnButton(self, event):
        if self.conf:
            paths = self.pathsPanel.read_paths()

            if self.conf.has_section('debugger.remote'):
                self.conf.set('debugger.remote', 'paths', pprint.pformat(paths))
                self.writeConfig(self.conf)

        self.EndModal(wx.ID_OK)


def showPathsMappingDlg(parent, paths):
    dlg = PathsMappingDlg(parent, paths)
    try:
        if dlg.ShowModal() != wx.ID_OK:
            return None
        else:
            return dlg.pathsPanel.read_paths()
    finally:
        dlg.Destroy()



if __name__ == '__main__':
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    print showPathsMappingDlg(None, [('1', '2'), ('3', '4')])
    app.MainLoop()
