#Boa:Dialog:AttachDlg

import pprint

import wx
import wx.grid

from Utils import _

from Debugger.PathsPanel import PathsPanel

def create(parent):
    return AttachDlg(parent)

[wxID_ATTACHDLG, wxID_ATTACHDLGCANCEL_BUTTON, wxID_ATTACHDLGHELP_BUTTON, 
 wxID_ATTACHDLGHOST_CTRL, wxID_ATTACHDLGOK_BUTTON, 
 wxID_ATTACHDLGPASSWORD_CTRL, wxID_ATTACHDLGPATHSPANEL, 
 wxID_ATTACHDLGPORT_CTRL, wxID_ATTACHDLGREM_PASS_CTRL, 
 wxID_ATTACHDLGSTATICTEXT1, wxID_ATTACHDLGSTATICTEXT2, 
 wxID_ATTACHDLGSTATICTEXT3, wxID_ATTACHDLGSTATICTEXT4, 
 wxID_ATTACHDLGUSERNAME_CTRL, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(14)]

class AttachDlg(wx.Dialog):
    _custom_classes = {'wx.Panel': ['PathsPanel'],}

    rem_host = None
    rem_port = None
    rem_user = None
    rem_pass = None
    rem_pths = None

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_ATTACHDLG, name='AttachDlg',
              parent=prnt, pos=wx.Point(270, 335), size=wx.Size(527, 391),
              style=wx.DEFAULT_DIALOG_STYLE, title=_('Attach to debugger'))
        self.SetClientSize(wx.Size(519, 364))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.staticText1 = wx.StaticText(id=wxID_ATTACHDLGSTATICTEXT1,
              label=_('Host'), name='staticText1', parent=self, pos=wx.Point(16,
              24), size=wx.Size(56, 16), style=0)

        self.staticText2 = wx.StaticText(id=wxID_ATTACHDLGSTATICTEXT2,
              label=_('Port'), name='staticText2', parent=self, pos=wx.Point(16,
              56), size=wx.Size(56, 16), style=0)

        self.staticText3 = wx.StaticText(id=wxID_ATTACHDLGSTATICTEXT3,
              label=_('Username'), name='staticText3', parent=self,
              pos=wx.Point(16, 88), size=wx.Size(56, 16), style=0)

        self.staticText4 = wx.StaticText(id=wxID_ATTACHDLGSTATICTEXT4,
              label=_('Password'), name='staticText4', parent=self,
              pos=wx.Point(16, 120), size=wx.Size(56, 16), style=0)

        self.host_ctrl = wx.TextCtrl(id=wxID_ATTACHDLGHOST_CTRL,
              name='host_ctrl', parent=self, pos=wx.Point(80, 16),
              size=wx.Size(160, 24), style=0, value=self.host)

        self.port_ctrl = wx.TextCtrl(id=wxID_ATTACHDLGPORT_CTRL,
              name='port_ctrl', parent=self, pos=wx.Point(80, 48),
              size=wx.Size(48, 24), style=0, value=self.port)

        self.username_ctrl = wx.TextCtrl(id=wxID_ATTACHDLGUSERNAME_CTRL,
              name='username_ctrl', parent=self, pos=wx.Point(80, 80),
              size=wx.Size(96, 24), style=0, value=self.user)

        self.password_ctrl = wx.TextCtrl(id=wxID_ATTACHDLGPASSWORD_CTRL,
              name='password_ctrl', parent=self, pos=wx.Point(80, 112),
              size=wx.Size(96, 24), style=wx.TE_PASSWORD, value=self.pwd)

        self.ok_button = wx.Button(id=wxID_ATTACHDLGOK_BUTTON, label=_('OK'),
              name='ok_button', parent=self, pos=wx.Point(266, 323),
              size=wx.Size(72, 24), style=0)
        self.ok_button.Bind(wx.EVT_BUTTON, self.OnOkButton,
              id=wxID_ATTACHDLGOK_BUTTON)

        self.cancel_button = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='cancel_button', parent=self, pos=wx.Point(346, 323),
              size=wx.Size(72, 24), style=0)

        self.help_button = wx.Button(id=wxID_ATTACHDLGHELP_BUTTON, label=_('Help'),
              name='help_button', parent=self, pos=wx.Point(426, 323),
              size=wx.Size(72, 24), style=0)
        self.help_button.Bind(wx.EVT_BUTTON, self.OnHelpButton,
              id=wxID_ATTACHDLGHELP_BUTTON)

        self.rem_pass_ctrl = wx.CheckBox(id=wxID_ATTACHDLGREM_PASS_CTRL,
              label=_('Remember'), name='rem_pass_ctrl', parent=self,
              pos=wx.Point(184, 120), size=wx.Size(73, 13), style=0)
        self.rem_pass_ctrl.SetValue(False)

        self.pathsPanel = PathsPanel(id=wxID_ATTACHDLGPATHSPANEL,
              name='pathsPanel', parent=self, pos=wx.Point(8, 144),
              size=wx.Size(504, 168), style=wx.TAB_TRAVERSAL)

    def __init__(self, editor):
        import Utils
        conf = Utils.createAndReadConfig('Explorer')
        self.writeConfig = Utils.writeConfig

        if conf and conf.has_section('debugger.remote'):
            host = conf.get('debugger.remote', 'host')
            port = conf.get('debugger.remote', 'port')
            user = conf.get('debugger.remote', 'user')
            pwd = eval(conf.get('debugger.remote', 'passwd'))
            if pwd is not None:
                from Explorers import scrm
                pwd = scrm.scramble(pwd)
            paths = eval(conf.get('debugger.remote', 'paths'))
        else:
            host, port, user, pwd, paths = self.rem_host, self.rem_port, \
                  self.rem_user, self.rem_pass, self.rem_pths
        self.conf = conf

        self.host = '127.0.0.1'
        if host is not None: self.host = host

        self.port = '26200'
        if port is not None: self.port = port

        self.user = ''
        if user is not None: self.user = user

        self.pwd = ''
        if pwd is not None: self.pwd = pwd

        self.paths = []
        if paths is not None: self.paths[:] = paths

        self._init_ctrls(editor)
        self.editor = editor

        self.pathsPanel.init_paths(self.paths)

        self.Center(wx.BOTH)

        try:
            from Preferences import IS
            self.SetIcon(IS.load('Images/Icons/Debug.ico'))
        except Exception:#ImportError: # for testing standalone
            pass

    def OnOkButton(self, event):
        paths = self.pathsPanel.read_paths()

        host = self.host_ctrl.GetValue()
        port = self.port_ctrl.GetValue()
        user = self.username_ctrl.GetValue()
        pw = self.password_ctrl.GetValue()

        if __name__ == '__main__':
            self.EndModal(wx.OK)
            return

        if self.conf:
            if not self.conf.has_section('debugger.remote'):
                self.conf.add_section('debugger.remote')
            self.conf.set('debugger.remote', 'host', host)
            self.conf.set('debugger.remote', 'port', port)
            self.conf.set('debugger.remote', 'user', user)
            if self.rem_pass_ctrl.GetValue():
                from Explorers import scrm
                self.conf.set('debugger.remote', 'passwd', repr(scrm.scramble(pw)))
            else:
                self.conf.set('debugger.remote', 'passwd', 'None')
            self.conf.set('debugger.remote', 'paths', pprint.pformat(paths))

            self.writeConfig(self.conf)
        else:
            AttachDlg.rem_host = host
            AttachDlg.rem_port = port
            AttachDlg.rem_user = user
            if self.rem_pass_ctrl.GetValue():
                AttachDlg.rem_pass = pw
            else:
                AttachDlg.rem_pass = None
            AttachDlg.rem_pths = paths

        from Debugger.Debugger import DebuggerFrame
        from RemoteClient import RemoteClient

        debugger = DebuggerFrame(self.editor, slave_mode=0)
        client = RemoteClient(debugger, host, port, user, pw)
        debugger.setDebugClient(client)
        debugger.setServerClientPaths(paths)
        if user:
            debugger.setTitleInfo('%s@%s:%s' % (user, host, port))
        else:
            debugger.setTitleInfo('%s:%s' % (host, port))

        self.editor.debugger = debugger
        debugger.doDebugStep()
        debugger.Show(True)

        self.EndModal(wx.OK)

    def OnHelpButton(self, event):
        pass

    def OnCloseWindow(self, event):
        self.editor = None
        self.Destroy()
        event.Skip()

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import sys; sys.path.append('..')
    app = wx.App()

    dlg = create(None)
    try:
        dlg.ShowModal()
        print (dlg.pathsPanel.read_paths())
    finally:
        dlg.Destroy()

    app.MainLoop()

    dlg = create(None)
    try:
        dlg.ShowModal()
        print (dlg.pathsPanel.read_paths())
    finally:
        dlg.Destroy()

    app.MainLoop()
