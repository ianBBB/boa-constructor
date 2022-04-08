#-----------------------------------------------------------------------------
# Name:        FindResults.py
# Purpose:
#
# Author:      Tim Hochberg
#
# Created:     2001/29/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Tim Hochberg,
#              but substantially derived from code (c) by Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import os

import wx

from Views.EditorViews import ListCtrlView, CloseableViewMix
from Preferences import keyDefs
from Utils import _

class FindResults(ListCtrlView, CloseableViewMix):
    gotoLineBmp = 'Images/Editor/GotoLine.png'
    viewName = 'Find Results'

    def __init__(self, parent, model):
        CloseableViewMix.__init__(self, _('find results'))
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          ( (_('Goto match'), self.OnGoto, self.gotoLineBmp, ()),
            (_('Re-run query'), self.OnRerun, '-', 'Refresh')
          ) + self.closingActionItems, 0)

        self.InsertColumn(0, _('Module'), width = 100)
        self.InsertColumn(1, _('Line no'), wx.LIST_FORMAT_CENTRE, 40)
        self.InsertColumn(2, _('Col'), wx.LIST_FORMAT_CENTRE, 40)
        self.InsertColumn(3, _('Text'), width = 550)

        self.results = {}
        self.listResultIdxs = []
        self.tabName = 'Results'
        self.findPattern = ''
        self.active = True
        self.model = model
        self.rerunCallback = None
        self.rerunParams = ()

        #self.Bind(wx.EVT_IDLE, self.OnIdle)
        #self.doRefresh = 0

##    def _refresh(self):
##        self.refreshCtrl()
##        self.modified = False

    def refreshCtrl(self):
        wx.BeginBusyCursor()
        try:
            ListCtrlView.refreshCtrl(self)
            i = 0
            self.listResultIdxs = []
            for mod in self.results.keys():
                for result in self.results[mod]:
                    self.listResultIdxs.append((mod, result))
                    i = self.addReportItems(i, (os.path.basename(mod), `result[0]`,
                      `result[1]`, result[2].strip()) )

            self.model.editor.statusBar.setHint(_('%d matches of "%s".')%(i, self.findPattern))
            self.pastelise()
        finally:
            wx.EndBusyCursor()

    def refresh(self):
        self.refreshCtrl()
        #self.doRefresh = 1

##    def OnIdle(self, event):
##        if self.doRefresh:
##            self.doRefresh = 0
##            self._refresh()

    def OnGoto(self, event):
        if self.selected >= 0:
            modName = self.listResultIdxs[self.selected][0]
            if modName != self.model.filename:
                model, controller = self.model.editor.openOrGotoModule(modName)
            else:
                model = self.model
            srcView = model.views['Source']
            srcView.focus()
            foundInfo = self.listResultIdxs[self.selected][1]
            srcView.lastSearchPattern = self.findPattern
            srcView.lastSearchResults = self.results[modName]
            try:
                srcView.lastMatchPosition = self.results[modName].index(foundInfo)
            except:
                srcView.lastMatchPosition = 0
                print 'foundInfo not found'
            srcView.selectSection(foundInfo[0]-1, foundInfo[1]-1, self.findPattern)
            self.model.prevSwitch = self

    def OnRerun(self, event):
        if self.rerunCallback:
            self.rerunCallback(*self.rerunParams)
