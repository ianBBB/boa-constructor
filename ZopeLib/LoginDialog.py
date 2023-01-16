#-----------------------------------------------------------------------------
# Name:        LoginDialog.py
# Purpose:     Dialog to get zope detail
#
# Author:      Riaan Booysen
#
# Created:     2000/05/06
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:LoginDialog

import wx

def create(parent):
    return LoginDialog(parent)

[wxID_LOGINDIALOG, wxID_LOGINDIALOGBUTTON1, wxID_LOGINDIALOGBUTTON2, 
 wxID_LOGINDIALOGFTPPORTTC, wxID_LOGINDIALOGHOSTTC, 
 wxID_LOGINDIALOGHTTPPORTTC, wxID_LOGINDIALOGPANEL1, 
 wxID_LOGINDIALOGPASSWORDTC, wxID_LOGINDIALOGSTATICTEXT1, 
 wxID_LOGINDIALOGSTATICTEXT2, wxID_LOGINDIALOGSTATICTEXT3, 
 wxID_LOGINDIALOGSTATICTEXT4, wxID_LOGINDIALOGSTATICTEXT5, 
 wxID_LOGINDIALOGUSERNAMETC, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(14)]

class LoginDialog(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_LOGINDIALOG, name='LoginDialog',
              parent=prnt, pos=wx.Point(421, 324), size=wx.Size(239, 215),
              style=wx.DEFAULT_DIALOG_STYLE, title='Open connection')
        self.SetClientSize(wx.Size(231, 188))

        self.panel1 = wx.Panel(id=wxID_LOGINDIALOGPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(231, 188),
              style=wx.TAB_TRAVERSAL)

        self.staticText2 = wx.StaticText(id=wxID_LOGINDIALOGSTATICTEXT2,
              label='Host:', name='staticText2', parent=self.panel1,
              pos=wx.Point(8, 12), size=wx.Size(24, 12), style=0)

        self.staticText3 = wx.StaticText(id=wxID_LOGINDIALOGSTATICTEXT3,
              label='FTP Port:', name='staticText3', parent=self.panel1,
              pos=wx.Point(8, 40), size=wx.Size(52, 12), style=0)

        self.staticText4 = wx.StaticText(id=wxID_LOGINDIALOGSTATICTEXT4,
              label='User name:', name='staticText4', parent=self.panel1,
              pos=wx.Point(8, 96), size=wx.Size(56, 12), style=0)

        self.staticText5 = wx.StaticText(id=wxID_LOGINDIALOGSTATICTEXT5,
              label='Password:', name='staticText5', parent=self.panel1,
              pos=wx.Point(8, 124), size=wx.Size(48, 12), style=wx.TE_PASSWORD)

        self.hostTC = wx.TextCtrl(id=wxID_LOGINDIALOGHOSTTC, name='hostTC',
              parent=self.panel1, pos=wx.Point(72, 4), size=wx.Size(148, 24),
              style=0, value='127.0.0.1')

        self.ftpPortTC = wx.TextCtrl(id=wxID_LOGINDIALOGFTPPORTTC,
              name='ftpPortTC', parent=self.panel1, pos=wx.Point(72, 32),
              size=wx.Size(148, 24), style=0, value='8021')

        self.usernameTC = wx.TextCtrl(id=wxID_LOGINDIALOGUSERNAMETC,
              name='usernameTC', parent=self.panel1, pos=wx.Point(72, 88),
              size=wx.Size(148, 24), style=0, value='')

        self.passwordTC = wx.TextCtrl(id=wxID_LOGINDIALOGPASSWORDTC,
              name='passwordTC', parent=self.panel1, pos=wx.Point(72, 116),
              size=wx.Size(148, 24), style=wx.TE_PASSWORD, value='')

        self.button1 = wx.Button(id=wxID_LOGINDIALOGBUTTON1, label='OK',
              name='button1', parent=self.panel1, pos=wx.Point(36, 156),
              size=wx.Size(76, 24), style=0)
        self.button1.Bind(wx.EVT_BUTTON, self.OnButton1Button,
              id=wxID_LOGINDIALOGBUTTON1)

        self.button2 = wx.Button(id=wxID_LOGINDIALOGBUTTON2, label='Cancel',
              name='button2', parent=self.panel1, pos=wx.Point(116, 156),
              size=wx.Size(76, 24), style=0)
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2Button,
              id=wxID_LOGINDIALOGBUTTON2)

        self.staticText1 = wx.StaticText(id=wxID_LOGINDIALOGSTATICTEXT1,
              label='HTTP Port:', name='staticText1', parent=self.panel1,
              pos=wx.Point(8, 68), size=wx.Size(56, 12), style=0)

        self.httpPortTC = wx.TextCtrl(id=wxID_LOGINDIALOGHTTPPORTTC,
              name='httpPortTC', parent=self.panel1, pos=wx.Point(72, 60),
              size=wx.Size(148, 24), style=0, value='8080')

    def __init__(self, parent):
        self._init_utils()
        self._init_ctrls(parent)
        self.Centre(wx.BOTH)

    def setup(self, host, ftpport, httpport, username, password):
        self.hostTC.SetValue(host)
        self.ftpPortTC.SetValue(str(ftpport))
        self.httpPortTC.SetValue(str(httpport))
        self.usernameTC.SetValue(username)
        self.passwordTC.SetValue(password)

    def getup(self):
        return self.hostTC.GetValue(), int(self.ftpPortTC.GetValue()), \
          int(self.httpPortTC.GetValue()), self.usernameTC.GetValue(), \
          self.passwordTC.GetValue()


    def OnButton1Button(self, event):
        self.EndModal(wx.OK)

    def OnButton2Button(self, event):
        self.EndModal(wx.CANCEL)
