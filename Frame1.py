# -*- coding: utf-8 -*-
#Boa:Frame:Frame1

import wx
import sys

def create(parent):
    return Frame1(parent)

[wxID_FRAME1] = [wx.NewIdRef() for _init_ctrls in range(1)]

class Frame1(wx.Frame):
    def _init_ctrls(self, prnt):
        wx.Frame.__init__(self, title='Frame1', pos=wx.Point(-1, -1), size=wx.Size(-1, -1), name='', style=wx.DEFAULT_FRAME_STYLE, parent=prnt, id=wxID_FRAME1)

    def __init__(self, parent):
        self._init_ctrls(parent)
        print('t1')
        sys.stdout.write('t2')
