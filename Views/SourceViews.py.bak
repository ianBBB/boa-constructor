#----------------------------------------------------------------------
# Name:        SourceViews.py
# Purpose:     Views for editing source code
#
# Author:      Riaan Booysen
#
# Created:     2000/05/05
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
print 'importing Views.SourceViews'

import time, os
from StringIO import StringIO

import wx
import wx.stc

from Preferences import keyDefs
import Utils
from Utils import _

import EditorViews, Search, Help, Preferences, Utils
from StyledTextCtrls import TextSTCMix, idWord, object_delim, eols as endOfLines

##endOfLines = {  wx.stc.STC_EOL_CRLF : '\r\n',
##                wx.stc.STC_EOL_CR : '\r',
##                wx.stc.STC_EOL_LF : '\n'}

markPlaceMrk, linePtrMrk = (1, 2)
markerCnt = 2

wxID_TEXTVIEW = wx.NewId()

[wxID_STC_WS, wxID_STC_EOL, wxID_STC_BUF, wxID_STC_IDNT,
 wxID_STC_EOL_MODE, wxID_STC_EOL_CRLF, wxID_STC_EOL_LF, wxID_STC_EOL_CR,
] = Utils.wxNewIds(8)

[wxID_CVT_EOL_LF, wxID_CVT_EOL_CRLF, wxID_CVT_EOL_CR] = Utils.wxNewIds(3)

class EditorStyledTextCtrl(wx.stc.StyledTextCtrl, EditorViews.EditorView,
                           EditorViews.FindResultsAdderMixin):
    refreshBmp = 'Images/Editor/Refresh.png'
    undoBmp = 'Images/Shared/Undo.png'
    redoBmp = 'Images/Shared/Redo.png'
    cutBmp = 'Images/Shared/Cut.png'
    copyBmp = 'Images/Shared/Copy.png'
    pasteBmp = 'Images/Shared/Paste.png'
    findBmp = 'Images/Shared/Find.png'
    findAgainBmp = 'Images/Shared/FindAgain.png'
    findAgainPrevBmp = 'Images/Shared/FindAgainPrev.png'
    printBmp = 'Images/Shared/Print.png'

    defaultEOL = os.linesep

    def __init__(self, parent, wId, model, actions, defaultAction = -1):
        wx.stc.StyledTextCtrl.__init__(self, parent, wId, style=wx.CLIP_CHILDREN | wx.SUNKEN_BORDER)
        a =  ((_('Refresh'), self.OnRefresh, self.refreshBmp, 'Refresh'),
              ('-', None, '', ''),
              (_('Undo'), self.OnEditUndo, self.undoBmp, ''),
              (_('Redo'), self.OnEditRedo, self.redoBmp, ''),
              ('-', None, '', ''),
              (_('Cut'), self.OnEditCut, self.cutBmp, ''),
              (_('Copy'), self.OnEditCopy, self.copyBmp, ''),
              (_('Paste'), self.OnEditPaste, self.pasteBmp, ''),
              ('-', None, '', ''),
              (_('Find \ Replace'), self.OnFind, self.findBmp, 'Find'),
              (_('Find previous'), self.OnFindAgainPrev, self.findAgainPrevBmp, 'FindAgainPrev'),
              (_('Find next'), self.OnFindAgain, self.findAgainBmp, 'FindAgain'),
              (_('Print...'), self.OnPrint, self.printBmp, ''),
              (_('Mark place'), self.OnMarkPlace, '-', 'MarkPlace'),
              (_('Goto line'), self.OnGotoLine, '-', 'GotoLine'),
              (_('STC settings...'), self.OnSTCSettings, '-', ''),
              (_('Convert...'), self.OnConvert, '-', ''),
              ##('Toggle Record macro', self.OnRecordMacro, '-', ''),
              ##('Playback macro', self.OnPlaybackMacro, '-', ''),
              ##('-', None, '-', ''),
              ##('Translate selection (via HTTP)', self.OnTranslate, '-', ''),
              ##('Spellcheck selection (via HTTP)', self.OnSpellCheck, '-', ''),
              )

        EditorViews.EditorView.__init__(self, model, a + actions, defaultAction)

        self.eol = None
        self.eolsChecked = False

        self.pos = 0
        self.stepPos = 0
        self.nonUserModification  = False

        self.lastSearchResults = []
        self.lastSearchPattern = ''
        self.lastMatchPosition = None

        ## Install the handler for refreshs.
        if wx.Platform == '__WXGTK__' and Preferences.edUseCustomSTCPaintEvtHandler:
            self.paint_handler = Utils.PaintEventHandler(self)

        self.lastStart = 0
        self._blockUpdate = False
        self._marking = False

        markIdnt, markBorder, markCenter = Preferences.STCMarkPlaceMarker
        self.MarkerDefine(markPlaceMrk, markIdnt, markBorder, markCenter)
        markIdnt, markBorder, markCenter = Preferences.STCLinePointer
        self.MarkerDefine(linePtrMrk , markIdnt, markBorder, markCenter)
        self._linePtrHdl = None

        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick, id=wId)

        self.Bind(wx.stc.EVT_STC_MACRORECORD, self.OnRecordingMacro, id=wId)

        self.Bind(wx.EVT_MENU, self.OnSTCSettingsWhiteSpace, id=wxID_STC_WS)
        self.Bind(wx.EVT_MENU, self.OnSTCSettingsEOL, id=wxID_STC_EOL)
        self.Bind(wx.EVT_MENU, self.OnSTCSettingsBufferedDraw, id=wxID_STC_BUF)
        self.Bind(wx.EVT_MENU, self.OnSTCSettingsIndentGuide, id=wxID_STC_IDNT)

        self.Bind(wx.EVT_MENU, self.OnChangeEOLMode, id=wxID_STC_EOL_CRLF)
        self.Bind(wx.EVT_MENU, self.OnChangeEOLMode, id=wxID_STC_EOL_LF)
        self.Bind(wx.EVT_MENU, self.OnChangeEOLMode, id=wxID_STC_EOL_CR)

        self.Bind(wx.EVT_MENU, self.OnConvertEols, id=wxID_CVT_EOL_CRLF)
        self.Bind(wx.EVT_MENU, self.OnConvertEols, id=wxID_CVT_EOL_LF)
        self.Bind(wx.EVT_MENU, self.OnConvertEols, id=wxID_CVT_EOL_CR)

        self.Bind(wx.EVT_MIDDLE_UP, self.OnEditPasteSelection)

    def getModelData(self):
        return self.model.data

    def setModelData(self, data):
        self.model.data = data

    def saveNotification(self):
        if not Preferences.neverEmptyUndoBuffer:
            self.EmptyUndoBuffer()

    def refreshCtrl(self):
        self.pos = self.GetCurrentPos()
        selection = self.GetSelection()
        prevVsblLn = self.GetFirstVisibleLine()
        self._blockUpdate = True
        try:
            newData = self.getModelData()
            curData = Utils.stringFromControl(self.GetText())
            if newData != curData:
                resetUndo = not self.CanUndo() and not curData
                ro = self.GetReadOnly()
                self.SetReadOnly(False)
                self.SetText(Utils.stringToControl(newData))
                self.SetReadOnly(ro)
                if resetUndo:
                    self.EmptyUndoBuffer()
            self.GotoPos(self.pos)
            curVsblLn = self.GetFirstVisibleLine()
            self.LineScroll(0, prevVsblLn - curVsblLn)
            # XXX not preserving selection
            self.SetSelection(*selection)
        finally:
            self._blockUpdate = False

        if self.eol is None:
            self.eol = Utils.getEOLMode(newData, self.defaultEOL)

            self.SetEOLMode({'\r\n': wx.stc.STC_EOL_CRLF,
                             '\r':   wx.stc.STC_EOL_CR,
                             '\n':   wx.stc.STC_EOL_LF}[self.eol])

        if not self.eolsChecked:
            if Utils.checkMixedEOLs(newData):
                wx.LogWarning(_('Mixed EOLs detected in %s, please use '
                             'Edit->Convert... to fix this problem.')\
                             %os.path.basename(self.model.filename))
            self.eolsChecked = True


        self.SetSavePoint()
        self.nonUserModification = False
        self.updatePageName()

        self.updateFromAttrs()

    def updateFromAttrs(self):
        if self.model.transport:
            self.SetReadOnly(self.model.transport.stdAttrs['read-only'])

    def refreshModel(self):
        if self.isModified():
            self.model.modified = True
        self.nonUserModification = False

        pos = self.GetCurrentPos()
        prevVsblLn = self.GetFirstVisibleLine()
        sel = self.GetSelection()

        self.setModelData(Utils.stringFromControl(self.GetText()))

        self.GotoPos(pos)
        self.SetSelection(*sel)
        curVsblLn = self.GetFirstVisibleLine()
        self.LineScroll(0, prevVsblLn - curVsblLn)

        self.SetSavePoint()
        if wx.Platform == '__WXGTK__':
            # We are updating the model from the editor view.
            # this flag is to prevent  the model updating the view
            self.noredraw = 1
        EditorViews.EditorView.refreshModel(self)
        self.noredraw = 0

        # Remove from modified views list
        if self.model.viewsModified.count(self.viewName):
            self.model.viewsModified.remove(self.viewName)

        self.updateEditor()

    def gotoLine(self, lineno, offset = -1):
        self.GotoLine(lineno)
        vl = self.GetFirstVisibleLine()
        self.LineScroll(0, lineno -  vl)
        if offset != -1: self.SetCurrentPos(self.GetCurrentPos()+offset+1)
        self.EnsureVisible(lineno)

    def selectSection(self, lineno, start, word):
        self.gotoLine(lineno)
        length = len(word)
        startPos = self.PositionFromLine(lineno) + start
        endPos = startPos + length
        self.SetSelection(startPos, endPos)
        self.SetFocus()
        self.EnsureVisible(lineno)

    def selectLine(self, lineno):
        self.GotoLine(lineno)
        sp = self.PositionFromLine(lineno)
        # Dont do whole screen selection
        ep = max(0, self.PositionFromLine(lineno+1)-1)
        self.SetSelection(sp, ep)
        self.EnsureVisible(lineno)

    def insertCodeBlock(self, text):
        cp = self.GetCurrentPos()
        ln = self.LineFromPosition(cp)
        indent = cp - self.PositionFromLine(ln)
        lns = text.split('\n')
        text = (self.eol+Utils.getIndentedStrForLen(indent)).join(lns)

        selTxtPos = text.find('# Your code')
        self.InsertText(cp, text)
        #self.nonUserModification = True
        self.updateViewState()
        self.SetFocus()
        if selTxtPos != -1:
            self.SetSelection(cp + selTxtPos, cp + selTxtPos + 11)

    def isModified(self):
        return self.GetModify() or self.nonUserModification

#---Block commands--------------------------------------------------------------

    def reselectSelectionAsBlock(self):
        selStartPos, selEndPos = self.GetSelection()
        selStartLine = self.LineFromPosition(selStartPos)
        startPos = self.PositionFromLine(selStartLine)
        selEndLine = self.LineFromPosition(selEndPos-1)#to handle cursor under sel
        endPos = self.GetLineEndPosition(selEndLine)
        startPos = self.PositionFromLine(selStartLine)
        self.SetSelection(startPos, endPos)
        return selStartLine, selEndLine

    def processSelectionBlock(self, func):
        if self.GetUseTabs():
            indtBlock = '\t'
        else:
            indtBlock = self.GetTabWidth()*' '

        self.BeginUndoAction()
        try:
            sls, sle = self.reselectSelectionAsBlock()
            lines = StringIO(self.GetSelectedText()).readlines()
            text = ''.join(func(lines, indtBlock))
            self.ReplaceSelection(text)
            self.SetSelection(self.PositionFromLine(sls),
                              self.GetLineEndPosition(sle))
        finally:
            self.EndUndoAction()

    def getSelectionAsLineNumbers(self):
        selStartPos, selEndPos = self.GetSelection()
        selStartLine = self.LineFromPosition(selStartPos)
        selEndLine = self.LineFromPosition(selEndPos)

        return range(self.LineFromPosition(selStartPos),
              self.LineFromPosition(selEndPos))

#-------------------------------------------------------------------------------
    def setLinePtr(self, lineNo):
        if self._linePtrHdl:
            self.MarkerDeleteHandle(self._linePtrHdl)
            self._linePtrHdl = None
        if lineNo >= 0:
            # XXX temp while handle returns None
            self.MarkerDeleteAll(linePtrMrk)

            self._linePtrHdl = self.MarkerAdd(lineNo, linePtrMrk)

    def gotoBrowseMarker(self, marker):
        self.GotoLine(marker)
        self.setLinePtr(marker)
        EditorViews.EditorView.gotoBrowseMarker(self, marker)

#-------Canned events-----------------------------------------------------------

    def OnRefresh(self, event):
        self.refreshModel()

    def OnEditCut(self, event):
        self.Cut()

    def OnEditCopy(self, event):
        self.Copy()

    def OnEditPaste(self, event):
        self.Paste()

    def OnEditPasteSelection(self, event):
        # XXX I'm limiting this to GTK for the moment, too non standard for MSW
        # XXX Maybe this should rather be a preference
        if wx.Platform == '__WXGTK__':
            text = self.GetSelectedText()
            pos = self.PositionFromPoint(event.GetPosition())
            self.InsertText(pos, text)
            self.SetSelection(pos, pos + len(text))

    def OnEditUndo(self, event):
        self.Undo()

    def OnEditRedo(self, event):
        self.Redo()

    # XXX
    def doFind(self, pattern):
        self.lastSearchResults = Search.findInText(\
          self.GetText().split(self.eol), pattern, False)
        self.lastSearchPattern = pattern
        if len(self.lastSearchResults):
            self.lastMatchPosition = 0

    def doNextMatch(self):
        if self.lastMatchPosition is not None and \
          len(self.lastSearchResults) > self.lastMatchPosition:
            pos = self.lastSearchResults[self.lastMatchPosition]
            self.model.editor.addBrowseMarker(self.GetCurrentLine())
            self.selectSection(pos[0], pos[1], self.lastSearchPattern)
            self.lastMatchPosition = self.lastMatchPosition + 1
        else:
            dlg = wx.MessageDialog(self.model.editor,
                  'No%smatches'% (self.lastMatchPosition is not None and ' further ' or ' '),
                  'Find in module', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.lastMatchPosition = None

    def OnFind(self, event):
        import FindReplaceDlg
        FindReplaceDlg.find(self, self.model.editor.finder, self)

    def OnFindAgain(self, event):
        import FindReplaceDlg
        FindReplaceDlg.findAgain(self, self.model.editor.finder, self, False)
        
    def OnFindAgainPrev(self, event):
        import FindReplaceDlg
        FindReplaceDlg.findAgain(self, self.model.editor.finder, self, True)

    def OnMarkPlace(self, event):
        if self._marking : return
        self._marking = True
        try:
            lineno = self.LineFromPosition(self.GetCurrentPos())
            self.MarkerAdd(lineno, markPlaceMrk)
            self.model.editor.addBrowseMarker(lineno)
            self.model.editor.setStatus(_('Code marker added to Browse History'), ringBell=True)
            # Encourage a redraw
            wx.Yield()
            time.sleep(0.125)
            self.MarkerDelete(lineno, markPlaceMrk)
        finally:
            self._marking = False


    def OnGotoLine(self, event):
        dlg = wx.TextEntryDialog(self, _('Enter line number:'), _('Goto line'), '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetValue():
                    try:
                        lineNo = int(dlg.GetValue()) - 1
                    except ValueError:
                        wx.LogError(_('Integer line number required'))
                    else:
                        self.GotoLine(lineNo)
        finally:
            dlg.Destroy()

    def OnUpdateUI(self, event):
        if hasattr(self, 'pageIdx'):
            self.updateViewState()
            l, col = self.GetCurLine()
            self.model.editor.statusBar.setColumnPos(col)

##    def OnTranslate(self, event):
##        # XXX web service no longer works
##        import TranslateDlg
##        dlg = TranslateDlg.create(None, self.GetSelectedText())
##        try:
##            if dlg.ShowModal() == wx.OK and len(dlg.translated) > 1:
##                self.ReplaceSelection(dlg.translated[1])
##        finally:
##            dlg.Destroy()
##
##    def OnSpellCheck(self, event):
##        # XXX web service no longer works
##        import TranslateDlg
##        self.model.editor.setStatus('Spell checking...', 'Warning')
##        wx.BeginBusyCursor()
##        try:
##            self.ReplaceSelection(TranslateDlg.spellCheck(self.GetSelectedText()))
##        finally:
##            wx.EndBusyCursor()
##        self.model.editor.setStatus('Spelling checked', 'Info')

    def OnMarginClick(self, event):
        pass


#---STC Settings----------------------------------------------------------------

    def OnSTCSettings(self, event):
        menu = wx.Menu()
        menu.Append(wxID_STC_WS, _('View Whitespace'), '', 1) #checkable
        menu.Check(wxID_STC_WS, self.GetViewWhiteSpace())
        menu.Append(wxID_STC_BUF, _('Buffered draw'), '', 1) #checkable
        menu.Check(wxID_STC_BUF, self.GetBufferedDraw())
        menu.Append(wxID_STC_IDNT, _('Use indentation guides'), '', 1) #checkable
        menu.Check(wxID_STC_IDNT, self.GetIndentationGuides())
        menu.Append(wxID_STC_EOL, _('View EOL symbols'), '', 1) #checkable
        menu.Check(wxID_STC_EOL, self.GetViewEOL())
        menu.AppendSeparator()

        eolModeMenu = wx.Menu()
        eolModeMenu.Append(wxID_STC_EOL_CRLF, 'CRLF', '', kind=wx.ITEM_RADIO)
        eolModeMenu.Check(wxID_STC_EOL_CRLF, self.GetEOLMode() == wx.stc.STC_EOL_CRLF)
        eolModeMenu.Append(wxID_STC_EOL_LF, 'LF', '', kind=wx.ITEM_RADIO)
        eolModeMenu.Check(wxID_STC_EOL_LF, self.GetEOLMode() == wx.stc.STC_EOL_LF)
        eolModeMenu.Append(wxID_STC_EOL_CR, 'CR', '', kind=wx.ITEM_RADIO)
        eolModeMenu.Check(wxID_STC_EOL_CR, self.GetEOLMode() == wx.stc.STC_EOL_CR)

        menu.AppendMenu(wxID_STC_EOL_MODE, _('EOL mode'), eolModeMenu)

        s = self.GetClientSize()

        self.PopupMenuXY(menu, s.x/2, s.y/2)
        menu.Destroy()

    def OnSTCSettingsWhiteSpace(self, event):
        self.SetViewWhiteSpace(Utils.getEventChecked(event))

    def OnSTCSettingsEOL(self, event):
        self.SetViewEOL(Utils.getEventChecked(event))

    def OnSTCSettingsBufferedDraw(self, event):
        self.SetBufferedDraw(Utils.getEventChecked(event))

    def OnSTCSettingsIndentGuide(self, event):
        self.SetIndentationGuides(Utils.getEventChecked(event))

    def OnChangeEOLMode(self, event):
        eol = {wxID_STC_EOL_CRLF: wx.stc.STC_EOL_CRLF,
               wxID_STC_EOL_LF:   wx.stc.STC_EOL_LF,
               wxID_STC_EOL_CR:   wx.stc.STC_EOL_CR}[event.GetId()]

        self.SetEOLMode(eol)

#-------------------------------------------------------------------------------
    def OnConvert(self, event):
        menu = wx.Menu()
        menu.Append(wxID_CVT_EOL_CRLF, _('EOLs to CRLF'))
        menu.Append(wxID_CVT_EOL_LF,   _('EOLs to LF'))
        menu.Append(wxID_CVT_EOL_CR,   _('EOLs to CR'))

        s = self.GetClientSize()

        self.PopupMenuXY(menu, s.x/2, s.y/2)
        menu.Destroy()

    def OnConvertEols(self, event):
        eol, viewEOL = {wxID_CVT_EOL_CRLF: (wx.stc.STC_EOL_CRLF, '\r\n'),
                        wxID_CVT_EOL_LF:   (wx.stc.STC_EOL_LF, '\n'),
                        wxID_CVT_EOL_CR:   (wx.stc.STC_EOL_CR, '\r')}[event.GetId()]

        self.ConvertEOLs(eol)
        self.SetEOLMode(eol)
        self.eol = viewEOL
        

#---Macro recording/playback----------------------------------------------------
    _recordingMacro = False
    _recordedMacro = False
    stcMacroCmds = ()
    def OnRecordMacro(self, event):
        if self._recordingMacro:
            self.model.editor.setStatus('Macro recorded', ringBell=True)
            self.StopRecord()
            self._recordedMacro = True
        else:
            self.model.editor.setStatus('Recording macro...', 'Warning')
            self.stcMacroCmds = []
            self.StartRecord()

        self._recordingMacro = not self._recordingMacro

    def OnPlaybackMacro(self, event):
        if self._recordedMacro:
            for stcMsg, stcLPrm in self.stcMacroCmds:
                self.CmdKeyExecute(stcMsg)
            self.model.editor.setStatus('Macro executed')

    def OnRecordingMacro(self, event):
        data = (event.GetMessage(), event.GetLParam())
        self.model.editor.setStatus('Recording macro: %s'%str(data), 'Warning')
        self.stcMacroCmds.append(data)

    def OnPrint(self, event):
        import STCPrinting

        dlg = STCPrinting.STCPrintDlg(self.model.editor, self, self.model.filename)
        dlg.ShowModal()
        dlg.Destroy()


class TextView(EditorStyledTextCtrl, TextSTCMix):
    viewName = 'Text'
    viewTitle = _('Text')
    
    def __init__(self, parent, model, actions=()):
        EditorStyledTextCtrl.__init__(self, parent, wxID_TEXTVIEW, model,
              actions, -1)
        TextSTCMix.__init__(self, wxID_TEXTVIEW)
        self.active = True

#-------------------------------------------------------------------------------

from Explorers import ExplorerNodes
ExplorerNodes.langStyleInfoReg.append(('Text', 'text', TextSTCMix, 'stc-styles.rc.cfg'))
