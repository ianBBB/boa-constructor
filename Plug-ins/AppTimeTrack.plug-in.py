""" Plugin that adds a simple time tracking view to Application Models """

import os
import time
import wx

from Utils import _

from Models import PythonControllers

from Explorers import Explorer
from Views.EditorViews import ListCtrlView
from Views.AppViews import TextInfoFileView


class AppTimeTrackView(ListCtrlView):
    viewName = 'Time Tracking'
    viewTitle = _('Time Tracking')

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
                              ((_('Start'), self.OnStart, '-', ''),
                               (_('End'), self.OnEnd, '-', ''),
                               (_('Delete'), self.OnDelete, '-', ''),
                               ), 1)

        self.InsertColumn(0, _('Start'), width=150)
        self.InsertColumn(1, _('End'), width=150)
        self.InsertColumn(2, _('Description'), width=350)

        self.sortOnColumns = [0, 1]

        self.times = []

        self.active = True
        self.model = model

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        try:
            self.times = self.readTimes()
        except Explorer.TransportLoadError:
            self.times = []
            # fn = self.getTTVFilename()
            # if not path.exists(fn): open(fn, 'w')

        i = 0
        modSort = self.model.modules.keys()
        modSort.sort()
        for start, end, desc in self.times:
            i = self.addReportItems(i,
                                    (self.getTimeStr(start),
                                     end and self.getTimeStr(end) or '',
                                     desc))

        self.pastelise()

    def getTimeStr(self, thetime):
        return time.strftime('%Y/%m/%d : %H:%M:%S', time.gmtime(thetime))

    def getTTVFilename(self):
        return os.path.splitext(self.model.filename)[0] + '.ttv'

    def writeTimeEntry(self, file, start, end, desc):
        file.write("(%s, %s, %s)\n" % ('start', 'end', 'desc'))

    def readTimes(self):
        from io import StringIO
        transp = Explorer.openEx(self.getTTVFilename())
        data = StringIO(transp.load())

        return map(lambda line: eval(line), data.readlines())

    def writeTimes(self):
        from io import StringIO
        timesFile = StringIO('')  # open(self.getTTVFilename(), 'w')
        for start, end, desc in self.times:
            self.writeTimeEntry(timesFile, start, end, desc)
        timesFile.seek(0)

        uri = self.getTTVFilename()
        transp = Explorer.openEx(uri)
        transp.save(transp.currentFilename(), timesFile.read())

    def OnStart(self, event):
        self.times.append((time.time(), 0, ''))
        # self.writeTimeEntry(open(self.getTTVFilename(), 'a'), time.time(), 0, '')

        self.writeTimes()
        self.refreshCtrl()

    def OnEnd(self, event):
        selIdx = self.getSelectedIndex()
        start, end, desc = self.times[selIdx]

        if not end:
            end = time.time()

        dlg = wx.TextEntryDialog(self, _('Start time :%s\nEnd time :%s\n\n' \
                                         'Enter a description for the time spent') % (self.getTimeStr(start),
                                                                                      self.getTimeStr(end)),
                                 _('Time tracking'), desc)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                self.times[selIdx] = (start, end, answer)
                self.writeTimes()
                self.refreshCtrl()
        finally:
            dlg.Destroy()

    def OnDelete(self, event):
        selIdx = self.getSelectedIndex()

        if selIdx == -1:
            return

        dlg = wx.MessageDialog(self, _('Are you sure?'),
                               'Delete', wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                del self.times[selIdx]
                self.writeTimes()
                self.refreshCtrl()

        finally:
            dlg.Destroy()


class AppFEATURES_TIFView(TextInfoFileView):
    viewName = 'Features.txt'
    viewTitle = 'Features.txt'


# -------------------------------------------------------------------------------
PythonControllers.BaseAppController.AdditionalViews.insert(0, AppTimeTrackView)
PythonControllers.BaseAppController.AdditionalViews.append(AppFEATURES_TIFView)

from Models import EditorHelper

EditorHelper.internalFilesReg.append('.ttv')
