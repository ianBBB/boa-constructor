#Boa:Dialog:KeyDefsDialog

import string

import wx

import Preferences, Utils
from Utils import _

class InvalidValueError(Exception): pass

[wxID_KEYDEFSDIALOG, wxID_KEYDEFSDIALOGALTFLAGCHB, 
 wxID_KEYDEFSDIALOGCANCELBTN, wxID_KEYDEFSDIALOGCTRLFLAGCHB, 
 wxID_KEYDEFSDIALOGKEYCODECBB, wxID_KEYDEFSDIALOGOKBTN, 
 wxID_KEYDEFSDIALOGSHIFTFLAGCHB, wxID_KEYDEFSDIALOGSHORTCUTTC, 
 wxID_KEYDEFSDIALOGSTATICBOX1, wxID_KEYDEFSDIALOGSTATICTEXT1, 
 wxID_KEYDEFSDIALOGSTATICTEXT2, 
] = [wx.NewId() for _init_ctrls in range(11)]

class KeyDefsDialog(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_KEYDEFSDIALOG, name='KeyDefsDialog',
              parent=prnt, pos=wx.Point(430, 271), size=wx.Size(298, 184),
              style=wx.DEFAULT_DIALOG_STYLE, title=self.entryTitle)
        self.SetClientSize(wx.Size(290, 157))

        self.staticBox1 = wx.StaticBox(id=wxID_KEYDEFSDIALOGSTATICBOX1,
              label='Flags', name='staticBox1', parent=self, pos=wx.Point(8, 8),
              size=wx.Size(136, 96), style=0)

        self.ctrlFlagChb = wx.CheckBox(id=wxID_KEYDEFSDIALOGCTRLFLAGCHB,
              label='wx.ACCEL_CTRL', name='ctrlFlagChb', parent=self,
              pos=wx.Point(16, 24), size=wx.Size(120, 19), style=0)
        self.ctrlFlagChb.Bind(wx.EVT_CHECKBOX, self.OnUpdateShortcut,
              id=wxID_KEYDEFSDIALOGCTRLFLAGCHB)

        self.altFlagChb = wx.CheckBox(id=wxID_KEYDEFSDIALOGALTFLAGCHB,
              label='wx.ACCEL_ALT', name='altFlagChb', parent=self,
              pos=wx.Point(16, 48), size=wx.Size(120, 19), style=0)
        self.altFlagChb.Bind(wx.EVT_CHECKBOX, self.OnUpdateShortcut,
              id=wxID_KEYDEFSDIALOGALTFLAGCHB)

        self.shiftFlagChb = wx.CheckBox(id=wxID_KEYDEFSDIALOGSHIFTFLAGCHB,
              label='wx.ACCEL_SHIFT', name='shiftFlagChb', parent=self,
              pos=wx.Point(16, 72), size=wx.Size(120, 19), style=0)
        self.shiftFlagChb.Bind(wx.EVT_CHECKBOX, self.OnUpdateShortcut,
              id=wxID_KEYDEFSDIALOGSHIFTFLAGCHB)

        self.keyCodeCbb = wx.ComboBox(choices=self.preDefKeys,
              id=wxID_KEYDEFSDIALOGKEYCODECBB, name='keyCodeCbb', parent=self,
              pos=wx.Point(152, 32), size=wx.Size(125, 21), style=0, value='')
        self.keyCodeCbb.Bind(wx.EVT_COMBOBOX, self.OnUpdateShortcutKeyCodeCbb,
              id=wxID_KEYDEFSDIALOGKEYCODECBB)
        self.keyCodeCbb.Bind(wx.EVT_TEXT, self.OnUpdateShortcutKeyCodeCbb,
              id=wxID_KEYDEFSDIALOGKEYCODECBB)

        self.staticText1 = wx.StaticText(id=wxID_KEYDEFSDIALOGSTATICTEXT1,
              label=_('Key code:'), name='staticText1', parent=self,
              pos=wx.Point(152, 16), size=wx.Size(120, 13), style=0)

        self.staticText2 = wx.StaticText(id=wxID_KEYDEFSDIALOGSTATICTEXT2,
              label=_('Shortcut text:'), name='staticText2', parent=self,
              pos=wx.Point(152, 64), size=wx.Size(120, 13), style=0)

        self.shortcutTc = wx.TextCtrl(id=wxID_KEYDEFSDIALOGSHORTCUTTC,
              name='shortcutTc', parent=self, pos=wx.Point(152, 80),
              size=wx.Size(124, 21), style=0, value='')

        self.okBtn = wx.Button(id=wxID_KEYDEFSDIALOGOKBTN, label=_('OK'),
              name='okBtn', parent=self, pos=wx.Point(120, 120),
              size=wx.Size(75, 23), style=0)
        self.okBtn.Bind(wx.EVT_BUTTON, self.OnOkbtnButton,
              id=wxID_KEYDEFSDIALOGOKBTN)

        self.cancelBtn = wx.Button(id=wxID_KEYDEFSDIALOGCANCELBTN,
              label=_('Cancel'), name='cancelBtn', parent=self, pos=wx.Point(200,
              120), size=wx.Size(75, 23), style=0)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancelbtnButton,
              id=wxID_KEYDEFSDIALOGCANCELBTN)

    def __init__(self, parent, entryName, accelEntry):
        #possibly raise exception for invalid format before creating the dialog
        # XXX fix when 2.5 is used for resource config values
        flags, keyCode, shortcut = eval(accelEntry, {'wx': wx})[0]

        self.preDefKeys = []
        self.preDefKeys = list(specialKeys.keys()) + otherKeys1 + otherKeys2
        self.entryTitle = 'Key binding definition:'
        self.entryTitle = _('Key binding definition: %s') % entryName

        self._init_ctrls(parent)

        self.SetAcceleratorTable(
              wx.AcceleratorTable([ Utils.setupCloseWindowOnEscape(self) ]))

        self.flagCtrls = ((self.ctrlFlagChb, wx.ACCEL_CTRL),
                          (self.altFlagChb, wx.ACCEL_ALT),
                          (self.shiftFlagChb, wx.ACCEL_SHIFT))

        for ctrl, flag in self.flagCtrls:
            ctrl.SetValue((flags & flag) == flag)

        if keyCode in valNameMap:
            self.keyCodeCbb.SetValue(valNameMap[keyCode])
        else:
            self.keyCodeCbb.SetValue(chr(keyCode))

        self.shortcutTc.SetValue(shortcut)

    def validateCtrls(self):
        flags = []
        for ctrl, flag in self.flagCtrls:
            if ctrl.GetValue():
                flags.append(flagValNames[flag][0])
        if flags:
            flags = ' | '.join(flags)
        else:
            flags = 'wx.ACCEL_NORMAL'

        keyCode = self.keyCodeCbb.GetValue()
        if not keyCode:
            raise InvalidValueError(_('Key code may not be blank'))
        if keyCode not in list(specialKeys.keys()) + otherKeys1 + otherKeys2:
            if len(keyCode) != 1 or keyCode not in string.ascII_letters+string.digits:
                raise InvalidValueError(_('Key code must either be a single character (letter or digit) or an identifier selected from the combobox'))
            keyCode = "ord('%s')" % keyCode.upper()

        shortcut = self.shortcutTc.GetValue()
        if not shortcut:
            raise InvalidValueError(_('Shortcut may not be blank, enter a concise description, e.g. Ctrl-Shift-S'))

        return "(%s, %s, '%s')," % (flags, keyCode, shortcut)

    def deriveShortcut(self, keyCode=None):
        segs = []
        for ctrl, flag in self.flagCtrls:
            if ctrl.GetValue():
                segs.append(flagValNames[flag][1])
        if keyCode is None:
            keyCode = self.keyCodeCbb.GetValue()
        if keyCode:
            segs.append(printableKeyCode(keyCode))

        self.shortcutTc.SetValue('-'.join(segs))

    def OnOkbtnButton(self, event):
        try:
            self.result = self.validateCtrls()
        except InvalidValueError as err:
            wx.MessageBox(str(err), _('Invalid value error'), wx.OK | wx.ICON_ERROR, self)
        else:
            self.EndModal(wx.ID_OK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnUpdateShortcut(self, event):
        self.deriveShortcut()

    def OnUpdateShortcutKeyCodeCbb(self, event):
        self.deriveShortcut(event.GetString())


def printableKeyCode(keyCode):
    if len(keyCode) >=8 and keyCode[:7] == 'wx.WXK_':
        return keyCode[7:].capitalize()
    else:
        return keyCode.upper()

flagValNames = {wx.ACCEL_CTRL:  ('wx.ACCEL_CTRL', 'Ctrl'),
                wx.ACCEL_ALT:   ('wx.ACCEL_ALT', 'Alt'),
                wx.ACCEL_SHIFT: ('wx.ACCEL_SHIFT', 'Shift')}

specialKeys = {'wx.WXK_BACK': wx.WXK_BACK, 'wx.WXK_TAB': wx.WXK_TAB, 
               'wx.WXK_RETURN': wx.WXK_RETURN, 'wx.WXK_ESCAPE': wx.WXK_ESCAPE, 
               'wx.WXK_SPACE': wx.WXK_SPACE, 'wx.WXK_DELETE': wx.WXK_DELETE}
# values 300+
otherKeys1 = ['wx.WXK_START', 'wx.WXK_LBUTTON', 'wx.WXK_RBUTTON',
     'wx.WXK_CANCEL', 'wx.WXK_MBUTTON', 'wx.WXK_CLEAR', 'wx.WXK_SHIFT']
# values 308+
otherKeys2 = ['wx.WXK_CONTROL', 'wx.WXK_MENU', 'wx.WXK_PAUSE',
     'wx.WXK_CAPITAL', 'wx.WXK_PRIOR', 'wx.WXK_NEXT', 'wx.WXK_END',
     'wx.WXK_HOME', 'wx.WXK_LEFT', 'wx.WXK_UP', 'wx.WXK_RIGHT',
     'wx.WXK_DOWN', 'wx.WXK_SELECT', 'wx.WXK_PRINT', 'wx.WXK_EXECUTE',
     'wx.WXK_SNAPSHOT', 'wx.WXK_INSERT', 'wx.WXK_HELP', 'wx.WXK_NUMPAD0',
     'wx.WXK_NUMPAD1', 'wx.WXK_NUMPAD2', 'wx.WXK_NUMPAD3',
     'wx.WXK_NUMPAD4', 'wx.WXK_NUMPAD5', 'wx.WXK_NUMPAD6',
     'wx.WXK_NUMPAD7', 'wx.WXK_NUMPAD8', 'wx.WXK_NUMPAD9',
     'wx.WXK_MULTIPLY', 'wx.WXK_ADD', 'wx.WXK_SEPARATOR',
     'wx.WXK_SUBTRACT', 'wx.WXK_DECIMAL', 'wx.WXK_DIVIDE', 'wx.WXK_F1',
     'wx.WXK_F2', 'wx.WXK_F3', 'wx.WXK_F4', 'wx.WXK_F5', 'wx.WXK_F6',
     'wx.WXK_F7', 'wx.WXK_F8', 'wx.WXK_F9', 'wx.WXK_F10', 'wx.WXK_F11',
     'wx.WXK_F12', 'wx.WXK_F13', 'wx.WXK_F14', 'wx.WXK_F15', 'wx.WXK_F16',
     'wx.WXK_F17', 'wx.WXK_F18', 'wx.WXK_F19', 'wx.WXK_F20', 'wx.WXK_F21',
     'wx.WXK_F22', 'wx.WXK_F23', 'wx.WXK_F24', 'wx.WXK_NUMLOCK',
     'wx.WXK_SCROLL', 'wx.WXK_PAGEUP', 'wx.WXK_PAGEDOWN', ]

# build reverse mapping
valNameMap = {}
for name, val in list(specialKeys.items()):
    valNameMap[val] = name
val = 300
for name in otherKeys1:
    valNameMap[val] = name
    val = val + 1
val = 308
for name in otherKeys2:
    valNameMap[val] = name
    val = val + 1

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = KeyDefsDialog(None, 'ContextHelp', "(wx.ACCEL_NORMAL, wx.WXK_F1, 'F1'),")
    try:
        if dlg.ShowModal() == wx.ID_OK:
            print(dlg.result)
    finally:
        dlg.Destroy()
    app.MainLoop()
