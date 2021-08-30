#Boa:Dialog:ArtProviderBrowser

import wx

from Utils import _

import PaletteStore

ClientIds = ['wx.ART_TOOLBAR', 'wx.ART_MENU', 'wx.ART_FRAME_ICON', 'wx.ART_CMN_DIALOG', 
             'wx.ART_HELP_BROWSER', 'wx.ART_MESSAGE_BOX', 'wx.ART_BUTTON', 'wx.ART_OTHER']

def attachStandardArtIds():
    clids = [c[3:] for c in ClientIds]
    for n in wx.__dict__.keys():
        if n.startswith('ART_') and n not in clids:
            val = wx.__dict__[n]
            if isinstance(val, basestring):
                PaletteStore.artProviderArtIds.append(val)

attachStandardArtIds()

def create(parent):
    return ArtProviderBrowser(parent)

[wxID_ARTPROVIDERBROWSER, wxID_ARTPROVIDERBROWSERARTID, 
 wxID_ARTPROVIDERBROWSERBTNCANCEL, wxID_ARTPROVIDERBROWSERBTNFILEDLG, 
 wxID_ARTPROVIDERBROWSERBTNOK, wxID_ARTPROVIDERBROWSERCLIENTID, 
 wxID_ARTPROVIDERBROWSERIMGSIZE, wxID_ARTPROVIDERBROWSERLISTCTRL, 
] = [wx.NewId() for _init_ctrls in range(8)]

class ArtProviderBrowser(wx.Dialog):
    def _init_coll_boxSizer3_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.artId, 0, border=8, flag=wx.TOP)
        parent.AddSizer(self.boxSizer4, 0, border=8,
              flag=wx.GROW | wx.BOTTOM | wx.TOP)

    def _init_coll_boxSizer4_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.clientId, 1, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.imgSize, 0, border=0, flag=wx.ALIGN_RIGHT)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.listCtrl, 1, border=15,
              flag=wx.GROW | wx.RIGHT | wx.LEFT | wx.TOP)
        parent.AddSizer(self.boxSizer2, 0, border=0, flag=0)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.boxSizer3, 0, border=15, flag=wx.LEFT)
        parent.AddWindow(self.btnOK, 0, border=15,
              flag=wx.LEFT | wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT)
        parent.AddWindow(self.btnCancel, 0, border=15,
              flag=wx.LEFT | wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT)
        parent.AddWindow(self.btnFileDlg, 0, border=15,
              flag=wx.LEFT | wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT)

    def _init_utils(self):
        # generated method, don't edit
        self.imageList = wx.ImageList(height=16, width=16)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer3 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer4 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)
        self._init_coll_boxSizer3_Items(self.boxSizer3)
        self._init_coll_boxSizer4_Items(self.boxSizer4)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_ARTPROVIDERBROWSER,
              name='ArtProviderBrowser', parent=prnt, pos=wx.Point(515, 325),
              size=wx.Size(598, 416),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('ArtProvider Browser'))
        self._init_utils()
        self.SetClientSize(wx.Size(590, 389))
        self.Center(wx.BOTH)

        self.btnOK = wx.Button(id=wx.ID_OK, label=_('OK'), name='btnOK',
              parent=self, pos=wx.Point(318, 338), size=wx.Size(75, 23),
              style=0)

        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='btnCancel', parent=self, pos=wx.Point(408, 338),
              size=wx.Size(75, 23), style=0)

        self.btnFileDlg = wx.Button(id=wxID_ARTPROVIDERBROWSERBTNFILEDLG,
              label=_('File Dialog...'), name='btnFileDlg', parent=self,
              pos=wx.Point(498, 338), size=wx.Size(75, 23), style=0)
        self.btnFileDlg.Bind(wx.EVT_BUTTON, self.OnBtnfiledlgButton,
              id=wxID_ARTPROVIDERBROWSERBTNFILEDLG)

        self.listCtrl = wx.ListCtrl(id=wxID_ARTPROVIDERBROWSERLISTCTRL,
              name='listCtrl', parent=self, pos=wx.Point(15, 15),
              size=wx.Size(560, 308), style=wx.LC_SMALL_ICON | wx.LC_ALIGN_TOP)
        self.listCtrl.SetImageList(self.imageList, wx.IMAGE_LIST_SMALL)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnListCtrlListItemSelected,
              id=wxID_ARTPROVIDERBROWSERLISTCTRL)

        self.clientId = wx.Choice(choices=self.clientIdChoices,
              id=wxID_ARTPROVIDERBROWSERCLIENTID, name='clientId', parent=self,
              pos=wx.Point(15, 360), size=wx.Size(177, 21), style=0)
        self.clientId.SetToolTip(_('Client id'))

        self.artId = wx.TextCtrl(id=wxID_ARTPROVIDERBROWSERARTID, name='artId',
              parent=self, pos=wx.Point(15, 331), size=wx.Size(288, 21),
              style=0, value='')
        self.artId.SetToolTip(_('Art id for bitmap'))

        self.imgSize = wx.ComboBox(choices=['wx.DefaultSize', '(16, 16)',
              '(32, 32)'], id=wxID_ARTPROVIDERBROWSERIMGSIZE, name='imgSize',
              parent=self, pos=wx.Point(200, 360), size=wx.Size(103, 21),
              style=0, value='wx.DefaultSize')
        self.imgSize.SetToolTip(_('Image size'))

        self._init_sizers()

    def __init__(self, parent, artId, clientId, size):
        self.clientIdChoices = []
        self.clientIdChoices = ClientIds

        self._init_ctrls(parent)
        
        # used for selection, match if possible
        if artId:
            if artId[0] in ('"', "'"):
                artIdVal = artId[1:-1]
            elif artId.startswith('u"') or artId.startswith("u'"):
                artIdVal = artId[2:-1]
            else:
                artIdVal = artId
        
        self.artId.SetValue(artId)
        if clientId.strip():
            if not self.clientId.SetStringSelection(clientId):
                self.clientId.Append(clientId)
                self.clientId.SetStringSelection(clientId)
        else:
            self.clientId.Select(0)
        if size.strip():
            self.imgSize.SetValue(size)
        else:
            self.imgSize.SetValue('wx.DefaultSize')

        idx = 0
        selIdx = -1
        for aid in PaletteStore.artProviderArtIds:
            imgIdx = self.imageList.Add(wx.ArtProvider.GetBitmap(aid, wx.ART_TOOLBAR, (16, 16)))
            self.listCtrl.InsertImageStringItem(idx, aid, imgIdx)
            if aid == artIdVal:
                self.listCtrl.SetItemState(idx, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
                selIdx = idx
        if selIdx != -1:
            self.listCtrl.EnsureVisible(selIdx)
            
            idx += 1

    def OnBtnfiledlgButton(self, event):
        self.EndModal(wx.ID_YES)

    def OnListCtrlListItemSelected(self, event):
        self.artId.SetValue("'"+event.GetText()+"'")


if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
