#-----------------------------------------------------------------------------
# Name:        CtrlAlign.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/09/11
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ControlAlignmentFrame

import wx

from Utils import _

# XXX Add 'Center in window' option

def create(parent):
    return ControlAlignmentFrame(parent)

[wxID_CONTROLALIGNMENTFRAME, wxID_CONTROLALIGNMENTFRAMECANCELBTN, 
 wxID_CONTROLALIGNMENTFRAMEOKBTN, wxID_CONTROLALIGNMENTFRAMEPANEL1, 
 wxID_CONTROLALIGNMENTFRAMERADIOBOX1, wxID_CONTROLALIGNMENTFRAMERADIOBOX2, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(6)]

class ControlAlignmentFrame(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_CONTROLALIGNMENTFRAME,
              name='ControlAlignmentFrame', parent=prnt, pos=wx.Point(341, 140),
              size=wx.Size(328, 219), style=wx.DEFAULT_DIALOG_STYLE,
              title='Alignment')
        self.SetClientSize(wx.Size(320, 192))

        self.panel1 = wx.Panel(id=wxID_CONTROLALIGNMENTFRAMEPANEL1,
              name='panel1', parent=self, pos=wx.Point(0, 0), size=wx.Size(320,
              192), style=wx.TAB_TRAVERSAL)

        self.radioBox1 = wx.RadioBox(choices=[_('No change'), _('Left sides'),
              _('Centers'), _('Right sides'), _('Space equally')],
              id=wxID_CONTROLALIGNMENTFRAMERADIOBOX1, label=_('Horizontal'),
              majorDimension=1, name='radioBox1', parent=self.panel1,
              pos=wx.Point(8, 8), size=wx.Size(144, 144),
              style=wx.RA_SPECIFY_COLS)

        self.okBtn = wx.Button(id=wxID_CONTROLALIGNMENTFRAMEOKBTN,
              label=_('OK'), name='okBtn', parent=self.panel1, pos=wx.Point(160,
              160), size=wx.Size(72, 24), style=0)
        self.okBtn.Bind(wx.EVT_BUTTON, self.OnOkbtnButton,
              id=wxID_CONTROLALIGNMENTFRAMEOKBTN)

        self.cancelBtn = wx.Button(id=wxID_CONTROLALIGNMENTFRAMECANCELBTN,
              label=_('Cancel'), name='cancelBtn', parent=self.panel1,
              pos=wx.Point(240, 160), size=wx.Size(72, 24), style=0)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancelbtnButton,
              id=wxID_CONTROLALIGNMENTFRAMECANCELBTN)

        self.radioBox2 = wx.RadioBox(choices=[_('No change'), _('Tops'),
              _('Centers'), _('Bottoms'), _('Space equally')],
              id=wxID_CONTROLALIGNMENTFRAMERADIOBOX2, label=_('Vertical'),
              majorDimension=1, name='radioBox2', parent=self.panel1,
              pos=wx.Point(160, 8), size=wx.Size(152, 144),
              style=wx.RA_SPECIFY_COLS)

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
        for sel in self.selection:
            domove = False
            newX, newY = sel.position.x, sel.position.y

            if self.choices[hor] == _('Left sides'):
                if sel != firstSel:
                    domove = True
                    newX = firstSelPos.x
            elif self.choices[hor] == _('Centers'):
                if sel != firstSel:
                    domove = True
                    newX = firstSelPos.x + firstSel.size.x / 2 - sel.size.x / 2
            elif self.choices[hor] == _('Right sides'):
                if sel != firstSel:
                    domove = True
                    newX = firstSelPos.x + firstSel.size.x - sel.size.x
            elif self.choices[hor] == _('Space equally'):
                if sel != firstSel and sel != lastSel:
                    domove = True
                    newX = (lastSelPos.x - firstSelPos.x) / (selSize-1) * selIdx \
                           + firstSelPos.x
#            elif self.choices[hor] == 'Center in window': pass # not implemented

            if self.choices[ver] == _('Tops'):
                if sel != firstSel:
                    domove = True
                    newY = firstSelPos.y
            elif self.choices[ver] == _('Centers'):
                if sel != firstSel:
                    domove = True
                    newY = firstSelPos.y + firstSel.size.y / 2 - sel.size.y / 2
            elif self.choices[ver] == _('Bottoms'):
                if sel != firstSel:
                    domove = True
                    newY = firstSelPos.y + firstSel.size.y - sel.size.y
            elif self.choices[ver] == _('Space equally'):
                if sel != firstSel and sel != lastSel:
                    domove = True
                    newY = (lastSelPos.y - firstSelPos.y) / (selSize-1) * selIdx \
                           + firstSelPos.y
#            elif self.choices[ver] == 'Center in window': pass

            if domove:
                sel.position = wx.Point(int(round(newX)), int(round(newY)))
                sel.dragging = True
                sel.moveRelease()
                sel.positionUpdate()

            selIdx = selIdx + 1

        self.EndModal(wx.OK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wx.CANCEL)


if __name__ == '__main__':
    app = wx.PySimpleApp()

    dlg = ControlAlignmentFrame(None, [])
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
