#Boa:Dialog:MaskedEditFormatCodesDlg

import wx
from wx.lib.anchors import LayoutAnchors

from Utils import _

formatCodes = [
 ('_', _('Allow spaces')),
 ('!', _('Force upper')),
 ('^', _('Force lower')),
 ('R', _('Right-align field(s)')),
 ('r', _('Right-insert in field(s) (implies R)')),
 ('<', _('Stay in field until explicit navigation out of it')),
 ('>', _('Allow insert/delete within partially filled fields')),
 (',', _('Allow comma to be typed as grouping character; auto-group/regroup digits in\ninteger fields (if result fits) when leaving such a field.')),
 ('-', _('Prepend and reserve leading space for sign to mask and allow signed values (negative #s shown in red by default)')),
 ('0', _('integer fields get leading zeros')),
 ('D', _('Date[/time] field')),
 ('T', _('Time field')),
 ('F', _('Auto-Fit: the control calulates its size from the length of the template mask')),
 ('V', _('Validate entered chars against ValidRegex, blocking invalid characters')),
 ('S', _('select entire field when navigating to new field')),
]

[wxID_MASKEDEDITFORMATCODESDLG, wxID_MASKEDEDITFORMATCODESDLGBTNCANCEL,
 wxID_MASKEDEDITFORMATCODESDLGBTNOK,
 wxID_MASKEDEDITFORMATCODESDLGCLBFORMATCODES,
 wxID_MASKEDEDITFORMATCODESDLGSTATICTEXT1,
 wxID_MASKEDEDITFORMATCODESDLGTCFORMATCODEPROPVAL,
] = [wx.NewIdRef(count=1) for _init_ctrls in range(6)]

class MaskedEditFormatCodesDlg(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_MASKEDEDITFORMATCODESDLG,
              name='MaskedEditFormatCodesDlg', parent=prnt, pos=wx.Point(433,
              218), size=wx.Size(436, 399),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('Masked Edit - Format Codes'))
        self.SetClientSize(wx.Size(428, 372))
        self.SetAutoLayout(True)
        self.Center(wx.BOTH)

        self.clbFormatCodes =wx.CheckListBox(choices=[],
              id=wxID_MASKEDEDITFORMATCODESDLGCLBFORMATCODES,
              name='clbFormatCodes', parent=self, pos=wx.Point(8, 33),
              size=wx.Size(413, 258), style=wx.LB_HSCROLL | wx.LB_SINGLE)
        self.clbFormatCodes.SetConstraints(LayoutAnchors(self.clbFormatCodes,
              True, True, True, True))
        self.clbFormatCodes.Bind(wx.EVT_CHECKLISTBOX, self.OnClbformatcodesChecklistbox, id=wxID_MASKEDEDITFORMATCODESDLGCLBFORMATCODES)

        self.tcFormatCodePropVal =wx.TextCtrl(id=wxID_MASKEDEDITFORMATCODESDLGTCFORMATCODEPROPVAL,
              name='tcFormatCodePropVal', parent=self, pos=wx.Point(8, 299),
              size=wx.Size(413, 25), style=0, value=self.formatCode)
        self.tcFormatCodePropVal.SetConstraints(LayoutAnchors(self.tcFormatCodePropVal,
              True, False, True, True))

        self.btnOK =wx.Button(id=wx.ID_OK, label=_('OK'), name='btnOK', parent=self,
              pos=wx.Point(261, 340), size=wx.Size(75, 23), style=0)
        self.btnOK.SetConstraints(LayoutAnchors(self.btnOK, False, False, True,
              True))

        self.btnCancel =wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='btnCancel', parent=self, pos=wx.Point(346, 340),
              size=wx.Size(75, 23), style=0)
        self.btnCancel.SetConstraints(LayoutAnchors(self.btnCancel, False,
              False, True, True))

        self.staticText1 =wx.StaticText(id=wxID_MASKEDEDITFORMATCODESDLGSTATICTEXT1,
              label=_('A string of formatting codes that modify behavior of the control.'),
              name='staticText1', parent=self, pos=wx.Point(8, 5),
              size=wx.Size(409, 24), style=wx.NO_BORDER | wx.ST_NO_AUTORESIZE)
        self.staticText1.SetConstraints(LayoutAnchors(self.staticText1, True,
              True, True, False))

    def __init__(self, parent, formatCode=''):
        self.formatCode = ''
        self.formatCode = formatCode

        self._init_ctrls(parent)

        if wx.Platform == '__WXGTK__': fontSize = 13
        else:                         fontSize = 9

        self.clbFormatCodes.SetFont(wx.Font(fontSize, wx.MODERN, wx.NORMAL, wx.BOLD))
        self.tcFormatCodePropVal.SetFont(wx.Font(fontSize+1, wx.MODERN, wx.NORMAL, wx.BOLD))

        for fc, desc in formatCodes:
            fmtCode = fc
            if len(fmtCode) < 4:
                fmtCode = ' %s  '%fmtCode

            self.clbFormatCodes.Append('%s - %s'%(fmtCode, desc))
            if formatCode.find(fc) != -1:
                self.clbFormatCodes.Check(self.clbFormatCodes.GetCount()-1, True)

        self.rebuildFmtCodePropVal()

    def rebuildFmtCodePropVal(self):
        r = []
        for idx in range(self.clbFormatCodes.GetCount()):
            if self.clbFormatCodes.IsChecked(idx):
                r.append(formatCodes[idx][0])

        self.tcFormatCodePropVal.SetValue(''.join(r))

    def getFormatCode(self):
        return self.tcFormatCodePropVal.GetValue()

    def OnClbformatcodesChecklistbox(self, event):
        self.rebuildFmtCodePropVal()



if __name__ == '__main__':
    app = wx.App()

    dlg = MaskedEditFormatCodesDlg(None, 'F_,-')
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
