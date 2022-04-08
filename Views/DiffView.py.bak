#-----------------------------------------------------------------------------
# Name:        DiffView.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/17/07
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys, linecache, traceback, shutil
from cStringIO import StringIO

import wx
import wx.stc

from ExternalLib import ndiff
from EditorViews import EditorView, CloseableViewMix
from StyledTextCtrls import PythonStyledTextCtrlMix
import Preferences, Utils
from Utils import _

uniqueFile1Mrk = 1
uniqueFile2Mrk = 2
newToBothMrk = 3
maskMarkSet = 1 << uniqueFile1Mrk | 1 << uniqueFile2Mrk | 1 << newToBothMrk

def ndiff_lcompare(a, b):
    """ Copy of ndiff.fcompare, works on lines instread of files """

    cruncher = ndiff.SequenceMatcher(ndiff.IS_LINE_JUNK, a, b)
    for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
        if tag == 'replace':
            ndiff.fancy_replace(a, alo, ahi, b, blo, bhi)
        elif tag == 'delete':
            ndiff.dump('-', a, alo, ahi)
        elif tag == 'insert':
            ndiff.dump('+', b, blo, bhi)
        elif tag == 'equal':
            ndiff.dump(' ', a, alo, ahi)
        else:
            raise ValueError, _('unknown tag %r')%tag

    return 1


class DiffPSOut(Utils.PseudoFile):
    def write(self, s):
##        cp = self.output.GetCurrentPos()
##        cl = self.output.GetLineFromPos(cp)
##        mrk = self.output.MarkerGet(cl)
        if s not in ('+', '-', ' ', '?'):
            self.output.AddText(s)
        elif s[0] == '+':
            self.output.MarkerAdd(self.output.GetLineCount()-1, uniqueFile2Mrk)
        elif s[0] == '-':
            self.output.MarkerAdd(self.output.GetLineCount()-1, uniqueFile1Mrk)
        elif s[0] == '?':
            self.output.MarkerAdd(self.output.GetLineCount()-1, newToBothMrk)

class DiffView(EditorView):
    def genCustomPage(self, page):
        return self.report

class PythonSourceDiffView(wx.stc.StyledTextCtrl, EditorView, 
                           PythonStyledTextCtrlMix, CloseableViewMix):
    viewName = 'Diff'
    viewTitle = _('Diff')
    
    refreshBmp = 'Images/Editor/Refresh.png'
    prevBmp = 'Images/Shared/Previous.png'
    nextBmp = 'Images/Shared/Next.png'
    def __init__(self, parent, model):
        wxID_PYTHONSOURCEDIFFVIEW = wx.NewId()

        wx.stc.StyledTextCtrl.__init__(self, parent, wxID_PYTHONSOURCEDIFFVIEW,
          style = wx.CLIP_CHILDREN | wx.SUNKEN_BORDER)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEDIFFVIEW, 0)
        CloseableViewMix.__init__(self, _('diffs'))
        EditorView.__init__(self, model,
          ( (_('Refresh'), self.OnRefresh, self.refreshBmp, 'Refresh'), ) +
            self.closingActionItems +
          ( ('-', None, '', ''),
            (_('Previous difference'), self.OnPrev, self.prevBmp, ''),
            (_('Next difference'), self.OnNext, self.nextBmp, ''),
            (_('Apply all changes'), self.OnApplyAllChanges, '-', '') ), -1)

        self.SetMarginType(1, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginWidth(1, 16)
        markIdnt, markBorder, markCenter = Preferences.STCDiffRemovedMarker
        self.MarkerDefine(uniqueFile1Mrk, markIdnt, markBorder, markCenter)
        markIdnt, markBorder, markCenter = Preferences.STCDiffAddedMarker
        self.MarkerDefine(uniqueFile2Mrk, markIdnt, markBorder, markCenter)
        markIdnt, markBorder, markCenter = Preferences.STCDiffChangesMarker
        self.MarkerDefine(newToBothMrk, markIdnt, markBorder, markCenter)

        self.SetMarginSensitive(1, True)
        wx.stc.EVT_STC_MARGINCLICK(self, wxID_PYTHONSOURCEDIFFVIEW, self.OnMarginClick)

        self.tabName = 'Diff'
        self.diffWith = ''
        self.currSearchLine = 1

        ## Install the handler for refreshs.
        if wx.Platform == '__WXGTK__' and Preferences.edUseCustomSTCPaintEvtHandler:
            self.paint_handler = Utils.PaintEventHandler(self)

        self.active = True

        self.lineIndex = []

    def refreshCtrl(self):
        from Explorers.Explorer import openEx
        self.SetReadOnly(False)
        self.ClearAll()
        if self.diffWith:
            saveout = sys.stdout
            try:
                sys.stdout = DiffPSOut(self)
                try:
                    src = StringIO(self.model.data).readlines()
                    # XXX could sometimes use data from file open in IDE ???
                    dst = StringIO(openEx(self.diffWith).load('rb')).readlines()
#                    self.model.editor.app.saveStdio = sys.stdout, sys.stderr
                    ndiff_lcompare(src, dst)
                except:
                    (sys.last_type, sys.last_value,
                     sys.last_traceback) = sys.exc_info()
                    linecache.checkcache()
                    traceback.print_exc()
            finally:
                sys.stdout = saveout
        self.SetReadOnly(True)

    def gotoLine(self, lineno, offset = -1):
        self.GotoLine(lineno)
        vl = self.GetFirstVisibleLine()
        self.LineScroll(0, lineno -  vl)
        if offset != -1: self.SetCurrentPos(self.GetCurrentPos()+offset+1)

    def OnUpdateUI(self, event):
        if Preferences.braceHighLight:
            PythonStyledTextCtrlMix.OnUpdateUI(self, event)

    def OnRefresh(self, event):
        self.refreshModel()

    def OnMarginClick(self, event):
        if event.GetMargin() == 1:
            ln = self.LineFromPosition(event.GetPosition())

    def OnPrev(self, event):
        self.currSearchLine = self.MarkerPrevious(self.currSearchLine,
          maskMarkSet) - 1
        self.gotoLine(self.currSearchLine + 1)

    def OnNext(self, event):
        self.currSearchLine = self.MarkerNext(self.currSearchLine,
          maskMarkSet) + 1
        self.gotoLine(self.currSearchLine - 1)

    def OnApplyAllChanges(self, event):
        # XXX Could be changed to work for all protocols
        filename = self.model.checkLocalFile()
        if self.diffWith:
            diffWith = self.model.checkLocalFile(self.diffWith) 
            if Utils.yesNoDialog(self, _('Are you sure?'),
                  _('Replace %s with %s?')% (filename, diffWith)):
                shutil.copyfile(diffWith, filename)
                # reload
                self.model.load()
                self.deleteFromNotebook('Source', self.tabName)
