#-----------------------------------------------------------------------------
# Name:        CtrlSize.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/09/11
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ControlSizeFrame

import wx

from Utils import _

def create(parent):
    return ControlSizeFrame(parent)

[wxID_CONTROLSIZEFRAME, wxID_CONTROLSIZEFRAMECANCELBTN, 
 wxID_CONTROLSIZEFRAMEHEIGHTTC, wxID_CONTROLSIZEFRAMEOKBTN, 
 wxID_CONTROLSIZEFRAMEPANEL1, wxID_CONTROLSIZEFRAMERADIOBOX1, 
 wxID_CONTROLSIZEFRAMERADIOBOX2, wxID_CONTROLSIZEFRAMEWIDTHTC, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(8)]

class ControlSizeFrame(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_CONTROLSIZEFRAME,
              name='ControlSizeFrame', parent=prnt, pos=wx.Point(417, 272),
              size=wx.Size(328, 204), style=wx.DEFAULT_DIALOG_STYLE,
              title=_('Size'))
        self.SetClientSize(wx.Size(320, 177))

        self.panel1 = wx.Panel(id=wxID_CONTROLSIZEFRAMEPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(320, 177),
              style=wx.TAB_TRAVERSAL)

        self.radioBox1 = wx.RadioBox(choices=[_('No change'),
              _('Shrink to smallest'), _('Grow to largest'), _('Width:')],
              id=wxID_CONTROLSIZEFRAMERADIOBOX1, label=_('Width'),
              majorDimension=1, name='radioBox1', parent=self.panel1,
              pos=wx.Point(8, 8), size=wx.Size(144, 128),
              style=wx.RA_SPECIFY_COLS)

        self.widthTC = wx.TextCtrl(id=wxID_CONTROLSIZEFRAMEWIDTHTC,
              name='widthTC', parent=self.panel1, pos=wx.Point(31, 104),
              size=wx.Size(112, 24), style=0, value='42')

        self.radioBox2 = wx.RadioBox(choices=[_('No change'),
              _('Shrink to smallest'), _('Grow to largest'), _('Height:')],
              id=wxID_CONTROLSIZEFRAMERADIOBOX2, label=_('Height'),
              majorDimension=1, name='radioBox2', parent=self.panel1,
              pos=wx.Point(160, 8), size=wx.Size(152, 128),
              style=wx.RA_SPECIFY_COLS)

        self.heightTC = wx.TextCtrl(id=wxID_CONTROLSIZEFRAMEHEIGHTTC,
              name='heightTC', parent=self.panel1, pos=wx.Point(183, 103),
              size=wx.Size(120, 24), style=0, value='42')

        self.okBtn = wx.Button(id=wxID_CONTROLSIZEFRAMEOKBTN, label=_('OK'),
              name='okBtn', parent=self.panel1, pos=wx.Point(160, 144),
              size=wx.Size(72, 24), style=0)
        self.okBtn.Bind(wx.EVT_BUTTON, self.OnOkbtnButton,
              id=wxID_CONTROLSIZEFRAMEOKBTN)

        self.cancelBtn = wx.Button(id=wxID_CONTROLSIZEFRAMECANCELBTN,
              label=_('Cancel'), name='cancelBtn', parent=self.panel1,
              pos=wx.Point(240, 144), size=wx.Size(72, 24), style=0)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancelbtnButton,
              id=wxID_CONTROLSIZEFRAMECANCELBTN)

    def __init__(self, parent, selection):
        self._init_ctrls(parent)
        self.choices = (_('No change'), _('No change'))
        self.selection = selection
        self.Centre(wx.BOTH)

    def OnOkbtnButton(self, event):
        hor = 0; ver = 1
        self.choices = (self.radioBox1.GetStringSelection(), self.radioBox2.GetStringSelection())

        selIdx = 0
        if len(self.selection):
            firstSel = self.selection[0]
            lastSel = self.selection[-1]
            firstSelPos = firstSel.position
            lastSelPos = lastSel.position
            selSize = len(self.selection)

        xSizes = []
        ySizes = []
        for sel in self.selection:
            xSizes.append( (sel.size.x, sel) )
            ySizes.append( (sel.size.y, sel) )
        xSizes.sort()
        ySizes.sort()

        for sel in self.selection:
            dosize = False
            newX, newY = sel.size.x, sel.size.y
            if self.choices[hor] == _('Shrink to smallest'):
                if sel != xSizes[0][1]:
                    dosize = True
                    newX = xSizes[0][0]
            elif self.choices[hor] == _('Grow to largest'):
                if sel != xSizes[-1][1]:
                    dosize = True
                    newX = xSizes[-1][0]
            elif self.choices[hor] == _('Width:'):
                dosize = True
                newX = int(self.widthTC.GetValue())

            if self.choices[ver] == _('Shrink to smallest'):
                if sel != ySizes[0][1]:
                    dosize = True
                    newY = ySizes[0][0]
            elif self.choices[ver] == _('Grow to largest'):
                if sel != ySizes[-1][1]:
                    dosize = True
                    newY = ySizes[-1][0]
            elif self.choices[ver] == _('Height:'):
                dosize = True
                newY = int(self.heightTC.GetValue())

            if dosize:
                sel.size = wx.Point(newX, newY)
                sel.OnSizeEnd2()
                sel.setSelection()
                sel.sizeUpdate()

            selIdx = selIdx + 1

        self.EndModal(wx.OK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wx.CANCEL)


if __name__ == '__main__':
    app = wx.App()

    dlg = ControlSizeFrame(None, [])
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
