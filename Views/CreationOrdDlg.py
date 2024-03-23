#Boa:Dialog:CreationOrderDlg

import wx

import Preferences, Utils
from Utils import _

def create(parent):
    return CreationOrderDlg(parent)

[wxID_CREATIONORDERDLG, wxID_CREATIONORDERDLGBBDOWN, 
 wxID_CREATIONORDERDLGBBDOWNLAST, wxID_CREATIONORDERDLGBBUP, 
 wxID_CREATIONORDERDLGBBUPFIRST, wxID_CREATIONORDERDLGBTCANCEL, 
 wxID_CREATIONORDERDLGBTOK, wxID_CREATIONORDERDLGCONTEXTHELPBUTTON1, 
 wxID_CREATIONORDERDLGLBOBJECTS, wxID_CREATIONORDERDLGPANEL1, 
 wxID_CREATIONORDERDLGSTATICBOX1, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(11)]

class CreationOrderDlg(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_CREATIONORDERDLG,
              name='CreationOrderDlg', parent=prnt, pos=wx.Point(396, 265),
              size=wx.Size(280, 281), style=wx.DEFAULT_DIALOG_STYLE,
              title=_('Change creation order'))
        self.SetClientSize(wx.Size(272, 254))

        self.panel1 = wx.Panel(id=wxID_CREATIONORDERDLGPANEL1, name='panel1',
              parent=self, pos=wx.Point(1, 1), size=wx.Size(270, 252),
              style=wx.TAB_TRAVERSAL)
        self.panel1.SetHelpText(_('This dialog manages the order of controls on the level (share a parent). When the parent is recreated, the objects will be recreated in the new order.'))

        self.staticBox1 = wx.StaticBox(id=wxID_CREATIONORDERDLGSTATICBOX1,
              label=_('Current creation/tab order'), name='staticBox1',
              parent=self.panel1, pos=wx.Point(8, 0), size=wx.Size(256, 208),
              style=0)

        self.lbObjects = wx.ListBox(choices=[],
              id=wxID_CREATIONORDERDLGLBOBJECTS, name='lbObjects',
              parent=self.panel1, pos=wx.Point(16, 16), size=wx.Size(200, 184),
              style=wx.LB_EXTENDED)

        self.bbUpFirst = wx.BitmapButton(bitmap=self.bmpUpFirst,
              id=wxID_CREATIONORDERDLGBBUPFIRST, name='bbUpFirst',
              parent=self.panel1, pos=wx.Point(224, 40), size=wx.Size(24, 24),
              style=wx.BU_AUTODRAW)
        self.bbUpFirst.Bind(wx.EVT_BUTTON, self.OnBbUpFirstButton,
              id=wxID_CREATIONORDERDLGBBUPFIRST)

        self.bbUp = wx.BitmapButton(bitmap=self.bmpUp,
              id=wxID_CREATIONORDERDLGBBUP, name='bbUp', parent=self.panel1,
              pos=wx.Point(224, 72), size=wx.Size(24, 24),
              style=wx.BU_AUTODRAW)
        self.bbUp.Bind(wx.EVT_BUTTON, self.OnBbupButton,
              id=wxID_CREATIONORDERDLGBBUP)

        self.bbDown = wx.BitmapButton(bitmap=self.bmpDown,
              id=wxID_CREATIONORDERDLGBBDOWN, name='bbDown', parent=self.panel1,
              pos=wx.Point(224, 104), size=wx.Size(24, 24),
              style=wx.BU_AUTODRAW)
        self.bbDown.Bind(wx.EVT_BUTTON, self.OnBbdownButton,
              id=wxID_CREATIONORDERDLGBBDOWN)

        self.bbDownLast = wx.BitmapButton(bitmap=self.bmpDownLast,
              id=wxID_CREATIONORDERDLGBBDOWNLAST, name='bbDownLast',
              parent=self.panel1, pos=wx.Point(224, 136), size=wx.Size(24, 24),
              style=wx.BU_AUTODRAW)
        self.bbDownLast.Bind(wx.EVT_BUTTON, self.OnBbDownLastButton,
              id=wxID_CREATIONORDERDLGBBDOWNLAST)

        self.btOK = wx.Button(id=wxID_CREATIONORDERDLGBTOK, label=_('OK'),
              name='btOK', parent=self.panel1, pos=wx.Point(112, 224),
              size=wx.Size(72, 24), style=0)
        self.btOK.Bind(wx.EVT_BUTTON, self.OnBtokButton,
              id=wxID_CREATIONORDERDLGBTOK)

        self.btCancel = wx.Button(id=wxID_CREATIONORDERDLGBTCANCEL,
              label=_('Cancel'), name='btCancel', parent=self.panel1,
              pos=wx.Point(192, 224), size=wx.Size(72, 24), style=0)
        self.btCancel.Bind(wx.EVT_BUTTON, self.OnBtcancelButton,
              id=wxID_CREATIONORDERDLGBTCANCEL)

        self.contextHelpButton1 = wx.ContextHelpButton(parent=self.panel1,
              pos=wx.Point(8, 229), size=wx.Size(20, 19), style=wx.BU_AUTODRAW)

    def __init__(self, parent, controls, allctrls):
        self.bmpUp = Preferences.IS.load('Images/Shared/up.png')
        self.bmpDown = Preferences.IS.load('Images/Shared/down.png')
        self.bmpUpFirst = Preferences.IS.load('Images/Shared/UpFirst.png')
        self.bmpDownLast = Preferences.IS.load('Images/Shared/DownLast.png')
        self._init_ctrls(parent)

        self.ctrlIdxs, self.ctrlNames = [], []
        controls.sort()
        for idx, name in controls:
            self.ctrlIdxs.append(idx)
            self.ctrlNames.append(name)

        self.allCtrlIdxs, self.allCtrlNames = [], []
        allctrls.sort()
        for idx, name in allctrls:
            self.allCtrlIdxs.append(idx)
            self.allCtrlNames.append(name)

        self.lbObjects.InsertItems(self.ctrlNames, 0)

    def OnBbUpFirstButton(self, event):
        selItems = self.lbObjects.GetSelections()
        if not selItems or selItems[0] < 1: return
        for item in selItems:
            self.moveObject(item, item - selItems[0])

    def OnBbupButton(self, event):
        selItems = self.lbObjects.GetSelections()
        if not selItems or selItems[0] < 1: return
        for item in selItems:
            self.moveObject(item, item - 1)

    def OnBbdownButton(self, event):
        selItems = self.lbObjects.GetSelections()
        cnt = len(selItems)
        if not selItems or selItems[cnt-1] > ( len(self.ctrlNames) - 2 ): return
        for i in range( cnt ):
            item = selItems[cnt - i - 1]
            self.moveObject(item, item + 1)

    def OnBbDownLastButton(self, event):
        selItems = self.lbObjects.GetSelections()
        cnt = len(selItems)
        if not selItems or selItems[cnt-1] > ( len(self.ctrlNames) - 2 ): return
        shift = len(self.ctrlNames) - 1 - selItems[cnt - 1]
        for i in range( cnt ):
            item = selItems[cnt - i - 1]
            self.moveObject(item, item + shift)

    def OnBtokButton(self, event):
        self.EndModal(wx.ID_OK)

    def OnBtcancelButton(self, event):
        self.EndModal(wx.ID_CANCEL)

    def moveObject(self, selIdx, newIdx):
        if selIdx != newIdx:
            lbSel = newIdx
            #if newIdx > selIdx:
            #    newIdx, selIdx = selIdx, newIdx
            name = self.ctrlNames[selIdx]
            newName = self.ctrlNames[newIdx]
            del self.ctrlNames[selIdx]
            self.allCtrlNames.remove(name)
            self.lbObjects.Delete(selIdx)

            self.ctrlNames.insert(newIdx, name)
            self.allCtrlNames.insert(self.allCtrlNames.index(newName), name)
            self.lbObjects.InsertItems([name], newIdx)

            self.lbObjects.SetSelection(lbSel)

            return True
        else:
            return False


if __name__ == '__main__':
    app = wx.App()

    dlg = CreationOrderDlg(None, [(0, 'ctrl1'), (1, 'ctrl2'), (5, 'ctrl3')],
                    [(0, 'ctrl1'), (1, 'ctrl2'), (2, 'ctrl4'), (3, 'ctrl5'), (5, 'ctrl3')])
    try:
        dlg.ShowModal()
        print zip(dlg.allCtrlIdxs, dlg.allCtrlNames)
    finally:
        dlg.Destroy()
