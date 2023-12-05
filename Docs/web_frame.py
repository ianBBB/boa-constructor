# -*- coding: utf-8 -*-
#Boa:Frame:Web_Page

import wx

def create(parent):
    return Web_Page(parent)

[wxID_WEB_PAGE] = [wx.NewIdRef() for _init_ctrls in range(1)]

class Web_Page(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_WEB_PAGE, name='Web_Page', parent=prnt,
              pos=wx.Point(533, 226), size=wx.Size(1098, 636),
              style=wx.DEFAULT_FRAME_STYLE, title='Python Help')
        self.SetClientSize(wx.Size(1082, 597))

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.browser =wx.html2.WebView.New(self) 
        sizer.Add(self.browser, 1, wx.EXPAND, 10) 
        self.SetSizer(sizer) 
        self.SetSize((700, 700))     
