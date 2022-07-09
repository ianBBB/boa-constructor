#Boa:Frame:RegexEditorFrm

import re

import wx
import wx.stc
from wx.lib.anchors import LayoutAnchors

import Preferences, Utils, Plugins
from Utils import _

reFlags = {'IGNORECASE': re.IGNORECASE, 'LOCALE': re.LOCALE,
           'MULTILINE': re.MULTILINE, 'DOTALL': re.DOTALL,
           'UNICODE': re.UNICODE, 'VERBOSE': re.VERBOSE}

def createRegexEditor(parent):
    return RegexEditorFrm(parent)

[wxID_REGEXEDITORFRM, wxID_REGEXEDITORFRMCLBFLAGS, 
 wxID_REGEXEDITORFRMLCGROUPS, wxID_REGEXEDITORFRMPANEL, 
 wxID_REGEXEDITORFRMRBACTION, wxID_REGEXEDITORFRMSTATICTEXT1, 
 wxID_REGEXEDITORFRMSTATICTEXT2, wxID_REGEXEDITORFRMSTATICTEXT3, 
 wxID_REGEXEDITORFRMSTATICTEXT4, wxID_REGEXEDITORFRMSTATICTEXT5, 
 wxID_REGEXEDITORFRMSTATUSBAR, wxID_REGEXEDITORFRMTXTMATCH, 
 wxID_REGEXEDITORFRMTXTREGEX, wxID_REGEXEDITORFRMTXTSTRING, 
] = [wx.NewId() for _init_ctrls in range(14)]

class RegexEditorFrm(wx.Frame, Utils.FrameRestorerMixin):
    def _init_coll_lcGroups_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT, heading='#',
              width=35)
        parent.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT, heading='Name',
              width=75)
        parent.InsertColumn(col=2, format=wx.LIST_FORMAT_LEFT, heading='Value',
              width=117)

    def _init_coll_statusBar_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(2)

        parent.SetStatusText(number=0, text='')
        parent.SetStatusText(number=1, text='')

        parent.SetStatusWidths([16, -1])

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_REGEXEDITORFRM, name='RegexEditorFrm',
              parent=prnt, pos=wx.Point(562, 278), size=wx.Size(503, 509),
              style=wx.DEFAULT_FRAME_STYLE, title=_('Regex Editor'))
        self.SetClientSize(wx.Size(495, 482))

        self.panel = wx.Panel(id=wxID_REGEXEDITORFRMPANEL, name='panel',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(495, 462),
              style=wx.TAB_TRAVERSAL)
        self.panel.SetAutoLayout(True)

        self.staticText1 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT1,
              label=_('Regular Expression'), name='staticText1',
              parent=self.panel, pos=wx.Point(8, 8), size=wx.Size(232, 13),
              style=0)

        self.txtRegex = wx.TextCtrl(id=wxID_REGEXEDITORFRMTXTREGEX,
              name='txtRegex', parent=self.panel, pos=wx.Point(8, 32),
              size=wx.Size(352, 120), style=wx.TE_MULTILINE, value='')
        self.txtRegex.SetConstraints(LayoutAnchors(self.txtRegex, True, True,
              True, False))
        self.txtRegex.Bind(wx.EVT_TEXT, self.OnUpdate,
              id=wxID_REGEXEDITORFRMTXTREGEX)

        self.staticText2 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT2,
              label=_('String'), name='staticText2', parent=self.panel,
              pos=wx.Point(8, 160), size=wx.Size(80, 13), style=0)

        self.txtString = wx.TextCtrl(id=wxID_REGEXEDITORFRMTXTSTRING,
              name='txtString', parent=self.panel, pos=wx.Point(8, 184),
              size=wx.Size(351, 112), style=wx.TE_MULTILINE, value='')
        self.txtString.SetConstraints(LayoutAnchors(self.txtString, True, True,
              True, False))
        self.txtString.Bind(wx.EVT_TEXT, self.OnUpdate,
              id=wxID_REGEXEDITORFRMTXTSTRING)

        self.staticText3 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT3,
              label=_('Match'), name='staticText3', parent=self.panel,
              pos=wx.Point(8, 304), size=wx.Size(80, 13), style=0)

        self.clbFlags = wx.CheckListBox(choices=['IGNORECASE', 'LOCALE',
              'MULTILINE', 'DOTALL', 'UNICODE', 'VERBOSE'],
              id=wxID_REGEXEDITORFRMCLBFLAGS, name='clbFlags',
              parent=self.panel, pos=wx.Point(375, 32), size=wx.Size(112, 120),
              style=0)
        self.clbFlags.SetConstraints(LayoutAnchors(self.clbFlags, False, True,
              True, False))
        self.clbFlags.Bind(wx.EVT_CHECKLISTBOX, self.OnUpdate,
              id=wxID_REGEXEDITORFRMCLBFLAGS)

        self.staticText4 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT4,
              label=_('Groups'), name='staticText4', parent=self.panel,
              pos=wx.Point(256, 304), size=wx.Size(64, 13), style=0)

        self.rbAction = wx.RadioBox(choices=[_('Search'), _('Match')],
              id=wxID_REGEXEDITORFRMRBACTION, label=_('Action'),
              majorDimension=1, name='rbAction', parent=self.panel,
              point=wx.Point(376, 176), size=wx.Size(112, 120),
              style=wx.RA_SPECIFY_COLS)
        self.rbAction.SetConstraints(LayoutAnchors(self.rbAction, False, True,
              True, False))
        self.rbAction.Bind(wx.EVT_RADIOBOX, self.OnUpdate,
              id=wxID_REGEXEDITORFRMRBACTION)

        self.statusBar = wx.StatusBar(id=wxID_REGEXEDITORFRMSTATUSBAR,
              name='statusBar', parent=self, style=wx.ST_SIZEGRIP)
        self.statusBar.SetPosition(wx.Point(0, 462))
        self.statusBar.SetSize(wx.Size(495, 20))
        self._init_coll_statusBar_Fields(self.statusBar)
        self.SetStatusBar(self.statusBar)

        self.staticText5 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT5,
              label=_('Flags'), name='staticText5', parent=self.panel,
              pos=wx.Point(378, 8), size=wx.Size(46, 13), style=0)
        self.staticText5.SetConstraints(LayoutAnchors(self.staticText5, False,
              True, True, False))

        self.txtMatch = wx.TextCtrl(id=wxID_REGEXEDITORFRMTXTMATCH,
              name='txtMatch', parent=self.panel, pos=wx.Point(8, 328),
              size=wx.Size(232, 128), style=wx.TE_MULTILINE, value='')
        self.txtMatch.SetConstraints(LayoutAnchors(self.txtMatch, True, True,
              False, True))

        self.lcGroups = wx.ListCtrl(id=wxID_REGEXEDITORFRMLCGROUPS,
              name='lcGroups', parent=self.panel, pos=wx.Point(256, 328),
              size=wx.Size(231, 128), style=wx.LC_REPORT)
        self.lcGroups.SetConstraints(LayoutAnchors(self.lcGroups, True, True,
              True, True))
        self._init_coll_lcGroups_Columns(self.lcGroups)

    def __init__(self, parent):
        self._init_ctrls(parent)

        self.SetIcon(Preferences.IS.load('Images/Icons/Bevel.ico'))

        self.statusImages = \
              [wx.ArtProvider.GetBitmap(artId, wx.ART_TOOLBAR, (16, 16))
               for artId in (wx.ART_ERROR, wx.ART_INFORMATION)]

        rect = self.statusBar.GetFieldRect(0)
        self.sbImage = wx.StaticBitmap(self.statusBar, -1, self.statusImages[0],
            (rect.x+1, rect.y+1), (16, 16))

        self.winConfOption = 'regexeditor'
        self.loadDims()

    def setDefaultDimensions(self):
        self.Center(wx.BOTH)

    def OnUpdate(self, event):
        string = self.txtString.GetValue()
        regex = self.txtRegex.GetValue()

        flags = 0
        for idx in range(self.clbFlags.GetCount()):
            if self.clbFlags.IsChecked(idx):
                flags |= reFlags[self.clbFlags.GetString(idx)]

        try:
            ro = re.compile(regex, flags)
        except Exception, err:
            self.statusBar.SetStatusText(_('Error: %s: %s')%(err.__class__, err), 1)
            self.sbImage.SetBitmap(self.statusImages[0])
            return

        if self.rbAction.GetSelection():
            mo = ro.match(string)
        else:
            mo = ro.search(string)

        self.setStatus(mo)
        self.lcGroups.DeleteAllItems()
        if not mo:
            self.txtMatch.SetValue('')
        else:
            s, e = mo.span()
            self.txtMatch.SetValue(string[s:e])

            # we want the named groups sorted in the order they appear in the re
            # so lets get the index, name and group into a list of tuples and
            # sort the list
            namedGroups = []
            for name, idx in ro.groupindex.items():
                namedGroups += [(idx, name, mo.group(name))]
            namedGroups.sort()

            # now add the sorted list items to lcGroups 
            for idx, name, group in namedGroups:
                self.lcGroups.InsertStringItem(idx-1, str(idx))
                self.lcGroups.SetStringItem(idx-1, 1, name)
                self.lcGroups.SetStringItem(idx-1, 2, group)

    def setStatus(self, mo):
        if mo:
            self.statusBar.SetStatusText(_('Match'), 1)
            self.sbImage.SetBitmap(self.statusImages[1])
        else:
            self.statusBar.SetStatusText(_('Failed to match'), 1)
            self.sbImage.SetBitmap(self.statusImages[0])


#-------------------------------------------------------------------------------

def openRegexEditor(editor):
    frame = createRegexEditor(editor)
    frame.Show()

Plugins.registerTool(_('Regex editor'), openRegexEditor, 'Images/RegexEditor.png')

#-------------------------------------------------------------------------------

def getRegexEditorImgData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x00\x9cIDAT(\x91\x95\x91Q\r\xc40\x0cC}\xa7\x01\x08\x84A0\xa4B\x18\x94Bh\xa1\
\x8c\x81!\x14B\x19t\x1f\xb9\x9bn\xd5mj\xfd\x95H~\xb2\xa3\xbcZk\x18V\xcey\x01\
\xb0\xef\xfb PJY|\x92df\x0fV\x92\xb5V\x00\x1f\xc0\xcc\xd6u}\x00\xcc\xcc\x81\
\xf7`\x99S\xd3\xc0\xf2\xbbH\xda\xb6\x8d_\xa5\x94\x00\xc4\x18o\x13H\xba\x83\
\xa4\x93\x00\x1c\xfb\x9f\xd0\x91!\x84\x89\x1bHJ\x92\xd4%\\\x00I!\x04I^\xcc\
\x81.\xe7R\xc9o=\xd7\xb9Jw\x9a\xf8t\x0f\x94R\x86\x12r\xce\x83V\xd7\x01\x03\
\x95D\x18\x17\xaf\xf7E\x00\x00\x00\x00IEND\xaeB`\x82' 


Preferences.IS.registerImage('Images/RegexEditor.png', getRegexEditorImgData())

