#-----------------------------------------------------------------------------
# Name:        ProfileView.py
# Purpose:     View that displays sortable profile statistics, linked to code
#
# Author:      Riaan Booysen
#
# Created:     2000/05/17
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Views.ProfileView'

import marshal, os

import wx

from Utils import _

from EditorViews import ListCtrlView, CloseableViewMix

class ProfileStatsView(ListCtrlView, CloseableViewMix):
    viewName = 'Profile stats'
    viewTitle = _('Profile stats')
    
    gotoLineBmp = 'Images/Editor/GotoLine.png'
    calleesBmp = 'Images/Editor/Callees.png'
    callersBmp = 'Images/Editor/Callers.png'
    saveAsBmp = 'Images/Editor/SaveAs.png'

    def __init__(self, parent, model):
        CloseableViewMix.__init__(self, _('stats'))
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT | wx.LC_SINGLE_SEL,
          ( (_('Goto line'), self.OnGoto, self.gotoLineBmp, ''),
            ('-', None, '', ''),
            (_('Callers (called this function)'), self.OnCallers, self.callersBmp, ''),
            (_('Callees (are called by this function)'), self.OnCallees, self.calleesBmp, ''),
            ('-', None, '', '') ) +
            self.closingActionItems +
          ( (_('Save stats'), self.OnSaveStats, self.saveAsBmp, ''),
            ), 0)

        self.InsertColumn(0, 'module')
        self.InsertColumn(1, 'line')
        self.InsertColumn(2, 'function')
        self.InsertColumn(3, 'ncalls')
        self.InsertColumn(4, 'tottime')
        self.InsertColumn(5, 'totpercall')
        self.InsertColumn(6, 'cumtime')
        self.InsertColumn(7, 'cumpercall')
        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 30)
        self.SetColumnWidth(2, 100)
        self.SetColumnWidth(3, 50)
        self.SetColumnWidth(4, 60)
        self.SetColumnWidth(5, 60)
        self.SetColumnWidth(6, 60)
        self.SetColumnWidth(7, 60)

        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)

        self.sortAscend = False
        self.sortCol = 0
        self.all_callees = None

        self.active = True
        self.stats = None
        self.profDir = ''

    def sortCmp(self, item1, item2):
        res = 1
        if item1 < item2: res = -1
        elif item1 == item2: res = 0

        if not self.sortAscend:
            return res * -1
        else:
            return res

    def sortFunction(self, itemIdx1, itemIdx2):
        item1 = self.statKeyList[itemIdx1]
        item2 = self.statKeyList[itemIdx2]
        return self.sortCmp(item1, item2)

    def sortNCalls(self, itemIdx1, itemIdx2):
        item1 = self.stats[self.statKeyList[itemIdx1]][0]
        item2 = self.stats[self.statKeyList[itemIdx2]][0]
        return self.sortCmp(item1, item2)

    def sortTotTime(self, itemIdx1, itemIdx2):
        item1 = self.stats[self.statKeyList[itemIdx1]][2]
        item2 = self.stats[self.statKeyList[itemIdx2]][2]
        return self.sortCmp(item1, item2)

    def sortTotPerCall(self, itemIdx1, itemIdx2):
        key1 = self.statKeyList[itemIdx1]
        key2 = self.statKeyList[itemIdx2]
        ncalls1 = self.stats[key1][0]
        ncalls2 = self.stats[key2][0]
        if ncalls1 and ncalls2:
            item1 = self.stats[key1][2] / ncalls1
            item2 = self.stats[key2][2] / ncalls2
            return self.sortCmp(item1, item2)
        else:
            return 0

    def sortCumTime(self, itemIdx1, itemIdx2):
        item1 = self.stats[self.statKeyList[itemIdx1]][3]
        item2 = self.stats[self.statKeyList[itemIdx2]][3]
        return self.sortCmp(item1, item2)

    def sortCumPerCall(self, itemIdx1, itemIdx2):
        if self.stats[self.statKeyList[itemIdx1]][0] and \
          self.stats[self.statKeyList[itemIdx2]][0]:
            item1 = self.stats[self.statKeyList[itemIdx1]][3]/ \
              self.stats[self.statKeyList[itemIdx1]][0]
            item2 = self.stats[self.statKeyList[itemIdx2]][3]/ \
              self.stats[self.statKeyList[itemIdx2]][0]
            return self.sortCmp(item1, item2)
        else: return 0

    def calc_callees(self):
        """ from pstats """
        if self.all_callees: return
        self.all_callees = all_callees = {}
        for func in self.stats.keys():
            if not all_callees.has_key(func):
                all_callees[func] = {}
            cc, nc, tt, ct, callers = self.stats[func]
            for func2 in callers.keys():
                if not all_callees.has_key(func2):
                    all_callees[func2] = {}
                all_callees[func2][func] = callers[func2]
        return

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        if self.stats:
            self.statKeyList = self.stats.keys()
            self.statKeyList.sort()
            i = 0
            for filename, lineno, funcname in self.statKeyList:
                stats = self.stats[(filename, lineno, funcname)]
                i = self.addReportItems(i, (os.path.basename(filename), str(lineno),
                      funcname, '%d' % stats[0], '%f' % stats[2],
                      stats[0] and '%f' % (stats[2]/stats[0]) or '',
                      '%f' % stats[3],
                      stats[0] and '%f' % (stats[3]/stats[0]) or ''))
                self.SetItemData(i-1, i-1)
        self.pastelise()

    def getStatIdx(self):
        for i in range(self.GetItemCount()):
            if self.GetItemState(i, wx.LIST_STATE_SELECTED):
                return self.GetItemData(i)
        idx = self.GetItemData(i)
        return idx

    def OnGoto(self, event):
        if self.selected > -1:
            idx = self.getStatIdx()
            key = self.statKeyList[idx]
            if key[0] == '<string>':
                wx.LogMessage(_("Eval'd or exec'd code, no module."))
                return
            if os.path.isabs(key[0]):
                model, controller = self.model.editor.openOrGotoModule(key[0])
            else:
                model, controller = self.model.editor.openOrGotoModule(
                      os.path.join(self.profDir, key[0]))

            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].gotoLine(key[1]-1)

    def OnCallers(self, event):
        if self.selected > -1:
            idx = self.getStatIdx()
            callDct = self.stats[self.statKeyList[idx]][4]

            called = [`x[1]`+': '+x[0][2]+' | '+os.path.basename(os.path.splitext(x[0][0])[0])
                      for x in callDct.items()]
            dlg = wx.SingleChoiceDialog(self.model.editor, _('Choose a function:'),
              _('%s was called by...') % self.statKeyList[idx][2], called)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    idx = called.index(dlg.GetStringSelection())
                    key = callDct.keys()[idx]

                    for i in range(self.GetItemCount()):
                        if self.statKeyList[self.GetItemData(i)] == key:
                            self.SetItemState(i,
                              wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                              wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                            self.EnsureVisible(i)
            finally:
                dlg.Destroy()

    def OnCallees(self, event):
        if self.selected > -1:
            idx = self.getStatIdx()
            key = self.statKeyList[idx]
#            callDct = self.stats[key][4]

            self.calc_callees()
            if self.all_callees.has_key(key):
                callDct = self.all_callees[key]

                called = [`x[1]`+': '+x[0][2]+' | '+os.path.basename(os.path.splitext(x[0][0])[0])
                          for x in callDct.items()]
                 
                dlg = wx.SingleChoiceDialog(self.model.editor, _('Choose a function:'),
                  _('%s called...') % self.statKeyList[idx][2], called)
                try:
                    if dlg.ShowModal() == wx.ID_OK:
                        idx = called.index(dlg.GetStringSelection())
                        key = callDct.keys()[idx]

                        for i in range(self.GetItemCount()):
                            if self.statKeyList[self.GetItemData(i)] == key:
                                self.SetItemState(i,
                                  wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                                self.EnsureVisible(i)
                finally:
                    dlg.Destroy()

    def OnColClick(self, event):
        if self.sortCol != event.m_col:
            self.sortAscend = False
        else:
            self.sortAscend = not self.sortAscend

        self.sortCol = event.m_col

        if event.m_col in (0, 1, 2):
            self.SortItems(self.sortFunction)
        elif event.m_col == 3:
            self.SortItems(self.sortNCalls)
        elif event.m_col == 4:
            self.SortItems(self.sortTotTime)
        elif event.m_col == 5:
            self.SortItems(self.sortTotPerCall)
        elif event.m_col == 6:
            self.SortItems(self.sortCumTime)
        elif event.m_col == 7:
            self.SortItems(self.sortCumPerCall)
        self.pastelise()

    def OnSaveStats(self, event):
        fn, suc = self.model.editor.saveAsDlg(\
          os.path.splitext(self.model.filename)[0]+'.prof', 'BoaIntFiles')
        if suc and self.stats:
            from Explorers.Explorer import openEx
            transport = openEx(fn)
            transport.save(transport.currentFilename(), marshal.dumps(self.stats), 'wb')
