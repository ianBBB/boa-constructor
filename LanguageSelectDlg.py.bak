#Boa:Dialog:LanguageSelectDlg

import wx
import Utils
from Preferences import IS


from ExternalLib import langlistctrl

def create(parent):
    return LanguageSelectDlg(parent)

[wxID_LANGUAGESELECTDLG, wxID_LANGUAGESELECTDLGBUTTON2, 
 wxID_LANGUAGESELECTDLGLANGCTRLCONTAINER, wxID_LANGUAGESELECTDLGLANGFILTERRB, 
 wxID_LANGUAGESELECTDLGOKBTN, wxID_LANGUAGESELECTDLGSTATICTEXT1, 
] = [wx.NewId() for _init_ctrls in range(6)]

class LanguageSelectDlg(wx.Dialog):
    def _init_coll_mainSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText1, 0, border=8, flag=wx.ALL)
        parent.AddSizer(self.middleSizer, 1, border=8, flag=wx.ALL | wx.EXPAND)
        parent.AddSizer(self.buttonSizer, 0, border=0, flag=wx.ALIGN_RIGHT)

    def _init_coll_buttonSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.okBtn, 0, border=8, flag=wx.ALL)
        parent.AddWindow(self.button2, 0, border=8, flag=wx.ALL)

    def _init_coll_middleSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.langCtrlContainer, 1, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.langFilterRB, 0, border=8, flag=wx.LEFT)

    def _init_sizers(self):
        # generated method, don't edit
        self.mainSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.buttonSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.middleSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_mainSizer_Items(self.mainSizer)
        self._init_coll_buttonSizer_Items(self.buttonSizer)
        self._init_coll_middleSizer_Items(self.middleSizer)

        self.SetSizer(self.mainSizer)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_LANGUAGESELECTDLG,
              name='LanguageSelectDlg', parent=prnt, pos=wx.Point(591, 400),
              size=wx.Size(446, 266),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title='Language selection')
        self.SetClientSize(wx.Size(438, 239))
        self.Center(wx.BOTH)

        self.staticText1 = wx.StaticText(id=wxID_LANGUAGESELECTDLGSTATICTEXT1,
              label=u'Choose a language that will be used for translation in the IDE.\nThe IDE will require a restart for the change to take effect.',
              name='staticText1', parent=self, pos=wx.Point(8, 8),
              size=wx.Size(422, 26), style=0)

        self.langCtrlContainer = wx.Panel(id=wxID_LANGUAGESELECTDLGLANGCTRLCONTAINER,
              name='langCtrlContainer', parent=self, pos=wx.Point(8, 50),
              size=wx.Size(196, 142), style=wx.TAB_TRAVERSAL)
        self.langCtrlContainer.SetMinSize(wx.Size(196, 142))
        self.langCtrlContainer.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.langCtrlContainer.Bind(wx.EVT_SIZE, self.OnLangCtrlContainerSize)

        self.langFilterRB = wx.RadioBox(choices=['Boa IDE translated languages',
              'Available languages on your system', 'All languages'],
              id=wxID_LANGUAGESELECTDLGLANGFILTERRB, label='Filter',
              majorDimension=1, name='langFilterRB', parent=self,
              pos=wx.Point(212, 50), size=wx.Size(218, 104),
              style=wx.RA_SPECIFY_COLS)
        self.langFilterRB.Bind(wx.EVT_RADIOBOX, self.OnLangFilterRBRadiobox,
              id=wxID_LANGUAGESELECTDLGLANGFILTERRB)

        self.okBtn = wx.Button(id=wxID_LANGUAGESELECTDLGOKBTN, label='OK',
              name='okBtn', parent=self, pos=wx.Point(264, 208),
              size=wx.Size(75, 23), style=0)
        self.okBtn.Bind(wx.EVT_BUTTON, self.OnOkBtnButton,
              id=wxID_LANGUAGESELECTDLGOKBTN)

        self.button2 = wx.Button(id=wx.ID_CANCEL, label='Cancel',
              name='button2', parent=self, pos=wx.Point(355, 208),
              size=wx.Size(75, 23), style=0)

        self._init_sizers()

    def __init__(self, parent, lang=wx.LANGUAGE_DEFAULT, filter='boa', 
              boaLangs=(wx.LANGUAGE_DEFAULT,)):
        self._init_ctrls(parent)

        self.filterMap = {'boa': langlistctrl.LC_ONLY, 
                          'available': langlistctrl.LC_AVAILABLE, 
                          'all': langlistctrl.LC_ALL}
                        
        self.filterIdxMap = {0: 'boa', 
                             1: 'available', 
                             2: 'all'}
        self.boaLangs = boaLangs
        self.langCtrl = langlistctrl.LanguageListCtrl(self.langCtrlContainer, -1, 
              filter=self.filterMap[filter], only=boaLangs, select=lang,
              style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.SUNKEN_BORDER)
        
        # reset min sizes for all controls except the language selector
        Utils.resetMinSize(self, (self.langCtrlContainer,))
        
        # set language selector size
        self.OnLangCtrlContainerSize()
        
        # now set the sizer properly
        self.SetSizerAndFit(self.mainSizer)
        
        self.SetIcon(IS.load('Images/Icons/LanguageSelect.ico'))
        

    def OnLangCtrlContainerSize(self, event=None):
        #if event: event.Skip()
        self.langCtrl.SetSize(self.langCtrlContainer.GetSize())

    def OnLangFilterRBRadiobox(self, event):
        self.langCtrl.SetUpFilter(
            self.filterMap[self.filterIdxMap[self.langFilterRB.GetSelection()]],
            self.boaLangs)

    def GetLanguageInfo(self):
        lang = self.langCtrl.GetLanguage()
        ident = langlistctrl.GetWxIdentifierForLanguage(lang)
        
        return lang, ident

    def OnOkBtnButton(self, event):
        if self.langCtrl.GetLanguage() is None:
            wx.LogError('No language selected.')
        else:
            self.EndModal(wx.ID_OK)


if __name__ == '__main__':
    # stand alone
    app = wx.PySimpleApp()
    dlg = LanguageSelectDlg(None, lang=wx.LANGUAGE_ENGLISH, 
          boaLangs=(wx.LANGUAGE_AFRIKAANS, wx.LANGUAGE_DEFAULT, 
              wx.LANGUAGE_ENGLISH, wx.LANGUAGE_SPANISH))
    try:
        if dlg.ShowModal() == wx.ID_OK:
            print dlg.GetLanguageInfo()
    finally:
        dlg.Destroy()
    app.MainLoop()
else:
    # boa
    import Preferences, About, Plugins
    
    langs = [l for l, a in About.translations]
    langs.extend([wx.LANGUAGE_ENGLISH, wx.LANGUAGE_DEFAULT])
    
    def showChooseIDELanguage(editor):
        dlg = LanguageSelectDlg(editor, lang=Preferences.i18nLanguage, 
              boaLangs=langs)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                lang, ident = dlg.GetLanguageInfo()
                Preferences.i18nLanguage = lang
                Plugins.updateRcFile('prefs.rc.py', 'i18nLanguage', 'wx.'+ident)
        finally:
            dlg.Destroy()
    
    Plugins.registerTool('Choose IDE Language', showChooseIDELanguage, 'Images/Editor/LanguageSelect.png')
    
