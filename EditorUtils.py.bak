import os, time, threading, socket

import wx

import Preferences, Utils
from Utils import _

#-----Toolbar-------------------------------------------------------------------

class MyToolBar(wx.ToolBar):
    def __init__(self, *_args, **_kwargs):
        wx.ToolBar.__init__(self, _kwargs['parent'], _kwargs['id'],
          style=wx.TB_HORIZONTAL | wx.NO_BORDER|Preferences.flatTools)
        self.toolLst = []
        self.toolCount = 0
        self.SetToolBitmapSize((16, 16))

    def AddTool(self, id, bitmap, toggleBitmap=wx.NullBitmap, shortHelpString='', isToggle=False):
        wx.ToolBar.AddTool(self, id, bitmap, toggleBitmap, isToggle=isToggle,
            shortHelpString=shortHelpString)

        self.toolLst.append(id)
        self.toolCount = self.toolCount + 1

    def AddTool2(self, id, bitmapname, shortHelpString='', toggleBitmap=wx.NullBitmap, isToggle=False):
        self.AddTool(id, Preferences.IS.load(bitmapname), toggleBitmap, shortHelpString, isToggle)

    def AddSeparator(self):
        wx.ToolBar.AddSeparator(self)
        self.toolLst.append(-1)
        self.toolCount = self.toolCount + 1

    def DeleteTool(self, id):
        wx.ToolBar.DeleteTool(self, id)
        self.toolLst.remove(id)
        self.toolCount = self.toolCount - 1

    def ClearTools(self):
        posLst = range(self.toolCount)
        posLst.reverse()
        for pos in posLst:
            self.DeleteToolByPos(pos)

        self.DisconnectToolIds()

        self.toolLst = []
        self.toolCount = 0

    def GetToolPopupPosition(self, id):
        margins = self.GetToolMargins()
        toolSize = self.GetToolSize()
        xPos = margins.x
        for tId in self.toolLst:
            if tId == id:
                return wx.Point(xPos, margins.y + toolSize.y)

            if tId == -1:
                xPos = xPos + self.GetToolSeparation()
            else:
                xPos = xPos + toolSize.x

        return wx.Point(0, 0)

    def PopupToolMenu(self, toolId, menu):
        self.PopupMenu(menu, self.GetToolPopupPosition(toolId))

    def DisconnectToolIds(self):
        for wid in self.toolLst:
            if wid != -1:
                self.GetParent().Disconnect(wid)

class EditorToolBar(MyToolBar):
    pass


# fields
sbfIcon, sbfBrwsBtns, sbfStatus, sbfCrsInfo, sbfProgress = range(5)

class EditorStatusBar(wx.StatusBar):
    """ Displays information about the current view. Also global stats/
        progress bar etc. """
    maxHistorySize = 250
    def __init__(self, *_args, **_kwargs):
        wx.StatusBar.__init__(self, _kwargs['parent'], _kwargs['id'], style=wx.ST_SIZEGRIP)
        self.SetFieldsCount(6)
        if wx.Platform == '__WXGTK__':
            imgWidth = 21
        else:
            imgWidth = 16

        self.SetStatusWidths([imgWidth, 36, 400, 25, 150, -1])

        rect = self.GetFieldRect(sbfIcon)
        self.img = wx.StaticBitmap(self, -1,
            Preferences.IS.load('Images/Shared/BoaLogo.png'),
            (rect.x+1, rect.y+1), (16, 16))
        self.img.Bind(wx.EVT_LEFT_DCLICK, self.OnShowHistory)

        rect = self.GetFieldRect(sbfBrwsBtns)
        #self.historyBtns = wx.SpinButton(self, -1, (rect.x+1, rect.y+1),
#                                                  (rect.width-2, rect.height-2))
        self.historyBtnBack = wx.BitmapButton(self, -1,
              Preferences.IS.load('Images/Shared/PreviousSmall.png'),
              (rect.x+1, rect.y+1), (int(round(rect.width/2.0))-1, rect.height-2))
        self.historyBtnFwd = wx.BitmapButton(self, -1,
              Preferences.IS.load('Images/Shared/NextSmall.png'),
              (rect.x+1+int(round(rect.width/2.0)), rect.y+1), (int(round(rect.width/2.0))-1, rect.height-2))

        #self.historyBtns.SetToolTipString('Browse the Traceback/Error/Output window history.')
        tip = _('Browse the Traceback/Error/Output window history.')
        self.historyBtnBack.SetToolTipString(tip)
        self.historyBtnFwd.SetToolTipString(tip)
        #self.historyBtns.Bind(wx.EVT_SPIN_DOWN, self.OnErrOutHistoryBack, id=self.historyBtns.GetId())
        #self.historyBtns.Bind(wx.EVT_SPIN_UP, self.OnErrOutHistoryFwd, id=self.historyBtns.GetId())
        self.historyBtnBack.Bind(wx.EVT_BUTTON, self.OnErrOutHistoryBack, id=self.historyBtnBack.GetId())
        self.historyBtnFwd.Bind(wx.EVT_BUTTON, self.OnErrOutHistoryFwd, id=self.historyBtnFwd.GetId())

        self.erroutFrm = None

        self.progress = wx.Gauge(self, -1, 100)
        self.linkProgressToStatusBar()

        self.images = {'Info': Preferences.IS.load('Images/Shared/Info.png'),
                       'Warning': Preferences.IS.load('Images/Shared/Warning.png'),
                       'Error': Preferences.IS.load('Images/Shared/Error.png')}
        self.history = []
        self._histcnt = 0

    def destroy(self):
        self.images = None

    def setHint(self, hint, msgType='Info', ringBell=False):
        """ Show a status message in the statusbar, optionally rings a bell.

        msgType can be 'Info', 'Warning' or 'Error'
        """
        if not self.images:
            return
        self._histcnt = self._histcnt - 1
        if hint.strip():
            self.history.append( (msgType, time.strftime('%H:%M:%S',
              time.localtime(time.time())), hint, ringBell) )
        if len(self.history) > self.maxHistorySize:
            del self.history[0]

        self.SetStatusText(hint, sbfStatus)
        self.img.SetToolTipString(hint)
        self.img.SetBitmap(self.images[msgType])
        if ringBell: wx.Bell()

    def OnEditorNotification(self, event):
        self.setHint(event.message)

    logDlgs = {'Info': wx.LogMessage,
               'Warning': wx.LogWarning,
               'Error': wx.LogError}
    def OnShowHistory(self, event):
        hist = self.history[:]
        hp = HistoryPopup(self.GetParent(), hist, self.images)

    def linkProgressToStatusBar(self):
        rect = self.GetFieldRect(sbfProgress)
        self.progress.SetDimensions(rect.x+1, rect.y+1, rect.width -2, rect.height -2)

    def setColumnPos(self, value):
        self.SetStatusText(str(value), sbfCrsInfo)

    def OnErrOutHistoryBack(self, event):
        if self.erroutFrm:
            self.erroutFrm.stepBackInHistory()

    def OnErrOutHistoryFwd(self, event):
        if self.erroutFrm:
            self.erroutFrm.stepFwdInHistory()


def HistoryPopup(parent, hist, imgs):
    f = wx.MiniFrame(parent, -1, _('Editor status history'), size = (350, 200))
    lc = wx.ListCtrl(f, style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_NO_HEADER)
    lc.il = wx.ImageList(16, 16)
    idxs = {}
    for tpe, img in imgs.items():
        idxs[tpe] = lc.il.Add(img)
    lc.SetImageList(lc.il, wx.IMAGE_LIST_SMALL)
    lc.InsertColumn(0, _('Time'))
    lc.InsertColumn(1, _('Message'))
    lc.SetColumnWidth(0, 75)
    lc.SetColumnWidth(1, 750)
    for tpe, tme, msg, _bell in hist:
        lc.InsertImageStringItem(0, tme, idxs[tpe])
        lc.SetStringItem(0, 1, msg)
    f.Center()
    f.Show()
    wx.PostEvent(f, wx.SizeEvent(f.GetSize()))
    return f


#-----Model hoster--------------------------------------------------------------


wxID_MODULEPAGEVIEWCHANGE, wxID_MODULEPAGECLOSEVIEW = Utils.wxNewIds(2)

class ModulePage:
    """ Represents a notebook on a page of the top level notebook hosting
        the model instance. """
    def __init__(self, parent, model, defViews, views, idx, editor):
        self.editor = editor
        self.defViews = [(v, wx.NewId()) for v in defViews]
        self.adtViews = [(v, wx.NewId()) for v in views]
        self.viewIds = []
        self.model = model
        self.parent = parent
        self.notebook = wx.Notebook(parent, -1, style=wx.WANTS_CHARS | wx.CLIP_CHILDREN)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChange, id=self.notebook.GetId())
        self.tIdx = idx
        self.updatePageName()

        self.windowId = wx.NewId()
        self.editor.winMenu.Append(self.windowId, self.getMenuLabel(),
              _('Switch to highlighted file'))
        self.editor.Bind(wx.EVT_MENU, self.editor.OnGotoModulePage, id=self.windowId)
        self.notebook.Bind(wx.EVT_MENU, self.OnDirectActionClose, id=wxID_MODULEPAGECLOSEVIEW)
        self.notebook.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        Class = model.__class__
##        if not editor.defaultAdtViews.has_key(cls):
##            cls = model.__class__.__bases__[0]

        tot = len(defViews) ##+ len(editor.defaultAdtViews.get(Class, []))
        if tot:
            stepsDone = 50.0
            editor.statusBar.progress.SetValue(int(stepsDone))
            step = (100 - stepsDone) / tot
            for View in defViews:
                self.addView(View)
                stepsDone = stepsDone + step
                editor.statusBar.progress.SetValue(int(stepsDone))

##            for View in editor.defaultAdtViews.get(Class, []):
##                self.addView(View)
##                stepsDone = stepsDone + step
##                editor.statusBar.progress.SetValue(int(stepsDone))

        if defViews:
            self.default = defViews[0].viewName
        else:
            self.default = None

        self.viewMenu = self.viewSelectionMenu()

        editor.statusBar.progress.SetValue(0)

    def destroy(self):
        """ Destroy all views, notepad pages and the view notebook."""
        self.disconnectEvts()
        self.editor.Disconnect(self.windowId)

        self.editor.winMenu.Delete(self.windowId)

        self.viewMenu.Destroy()

        for view in self.model.views.values():
            if view:
                view.close()
        self.notebook.DeleteAllPages()

        self.model.destroy()
        self.model = None

        self.notebook.Destroy()

##    def __del__(self):
##        print '__del__', self.__class__.__name__

    def __repr__(self):
        return '<%s: %s, %d>' %(self.__class__.__name__, os.path.basename(self.model.filename), self.tIdx)

    def updatePageName(self):
        """ Return a name that is decorated with () meaning never been saved
            and/or * meaning model modified ~ meaning view modified. """

        pageName = self.model.getPageName()

        if not self.model.savedAs: sa1, sa2 = '(', ')'
        else: sa1 = sa2 = ''

        if len(self.model.viewsModified): vm = '~'
        else: vm = ''

        if self.model.modified: m = '*'
        else: m = ''

        if self.model.transport and self.model.transport.stdAttrs['read-only']:
            ro = ' (read only)'
        else: ro = ''

        self.pageName = '%s%s%s%s%s%s%s%s' % (m, vm, sa1, pageName, ro, sa2, vm, m)

        return self.pageName

    def getActiveView(self, idx=None):
        if idx is None: idx = self.notebook.GetSelection()
        if idx == -1: return None

        for name, view in self.model.views.items():
            if view.pageIdx == idx:
                return view

        return None

##        name = self.notebook.GetPageText(idx)
##        if name and name[0] == '~': name = name[1:-1]
##        try:
##            return self.model.views[name]
##        except KeyError:
##            return None

    def viewSelectionMenu(self):
        menu = wx.Menu()
        for View, wId in self.defViews:
            menu.Append(wId, Utils.getViewTitle(View))
        menu.AppendSeparator()
        for View, wId in self.adtViews:
            menu.Append(wId, Utils.getViewTitle(View), '', View not in self.adtViews)

        return menu

    def connectEvts(self):
        for view, wId in self.defViews:
            self.editor.Bind(wx.EVT_MENU, self.editor.OnSwitchedToView, id=wId)
        for view, wId in self.adtViews:
            self.editor.Bind(wx.EVT_MENU, self.editor.OnToggleView, id=wId)

    def disconnectEvts(self):
        if self.model:
            for view, wId in self.defViews + self.adtViews:
                self.editor.Disconnect(wId)

    def setActiveViewsMenu(self):
        viewClss = [x.__class__ for x in self.model.views.values()]
        for view, wId in self.adtViews:
            self.viewMenu.Check(wId, view in viewClss)

    def addView(self, View, viewName=''):
        """ Add a view to the model and display it as a page in the notebook
            of view instances."""
        if not viewName: 
            viewName = View.viewName
            viewTitle = Utils.getViewTitle(View)
        else:
            viewTitle = viewName

        if wx.Platform == '__WXGTK__':
            panel, view = Utils.wxProxyPanel(self.notebook, View, self.model)
            self.model.views[viewName] = view
            if View.docked:
                self.model.views[viewName].addToNotebook(self.notebook, viewTitle,
                        panel=panel)
        else:
            view = View(self.notebook, self.model)
            self.model.views[viewName] = view
            if View.docked:
                self.model.views[viewName].addToNotebook(self.notebook, viewTitle)

        return self.model.views[viewName]

    def refresh(self):
        pass
        # self.notebook.Refresh()

    def focus(self):
        """ Make this model page the currently selected page. """
        self.parent.SetSelection(self.tIdx)

    def removedPage(self, idx):
        """ Called on all ModulePages after a sibling ModulePage deletion.
            Decrements tIdx if bigger than idx. """
        if idx < self.tIdx:
            self.tIdx = self.tIdx - 1

    def addedPage(self, idx):
        if idx <= self.tIdx:
            self.tIdx = self.tIdx + 1

    def saveAs(self, filename):
        newFilename, success = self.editor.saveAsDlg(filename)
        if success:
            self.model.saveAs(newFilename)
            self.editor.updateModulePage(self.model, filename)
            self.editor.updateTitle()
        return success

    def saveOrSaveAs(self, forceSaveAs=False):
        model = self.model
        editor = self.editor
        if forceSaveAs or not model.savedAs:
            oldName = model.filename
            if self.saveAs(oldName) and (oldName != model.filename):
                self.rename(oldName, model.filename)

                editor.statusBar.setHint(_('%s saved.')%\
                      os.path.basename(model.filename))
        else:
            from Explorers.ExplorerNodes import TransportModifiedSaveError
            try:
                model.save()
            except TransportModifiedSaveError, err:
                choice = wx.MessageBox(_('%s\nDo you want to overwrite these '
                  'changes (Yes), reload your file (No) or cancel this operation '
                  '(Cancel)?')%str(err), _('Overwrite newer file warning'),
                  wx.YES_NO | wx.CANCEL | wx.ICON_WARNING)
                if choice == wx.YES:
                    model.save(overwriteNewer=True)
                elif choice == wx.NO:
                    raise TransportModifiedSaveError('Reload')
                elif choice == wx.CANCEL:
                    raise TransportModifiedSaveError('Cancel')

            editor.updateModulePage(model)
            editor.updateTitle()

            editor.statusBar.setHint(_('%s saved.')%\
                  os.path.basename(model.filename))

    def OnPageChange(self, event):
        viewIdx = event.GetSelection()
        if event.GetOldSelection() != viewIdx or wx.Platform == '__WXGTK__':
            self.editor.setupToolBar(viewIdx=viewIdx)
            view = self.getActiveView(viewIdx)
            if hasattr(view, 'OnPageActivated'):
                view.OnPageActivated(event)
        event.Skip()

    def OnRightDown(self, event):
        actView = self.getActiveView()

        doDirectMenuPopup = False
        for View, wid in self.adtViews:
            if isinstance(actView, View):
                doDirectMenuPopup = True
                break

        if not doDirectMenuPopup:
            from Views.EditorViews import CloseableViewMix
            if isinstance(actView, CloseableViewMix):
                doDirectMenuPopup = True

        if doDirectMenuPopup:
            directMenu = wx.Menu()
            directMenu.Append(wxID_MODULEPAGECLOSEVIEW, _('Close active view'))

            self.notebook.PopupMenu(directMenu, event.GetPosition())
            directMenu.Destroy()
            return

    def OnDirectActionClose(self, event):
        actView = self.getActiveView()

        for View, wid in self.adtViews:
            if isinstance(actView, View):
                actView.deleteFromNotebook(self.default, actView.viewName)

                self.editor.mainMenu.Check(wid, False)
                return

        from Views.EditorViews import CloseableViewMix
        if isinstance(actView, CloseableViewMix):
            actView.OnClose(None)

    def rename(self, oldName, newName):
        del self.editor.modules[oldName]
        self.editor.modules[newName] = self

        item = self.editor.winMenu.FindItemById(self.windowId)
        item.SetText(self.getMenuLabel())
        self.editor.editorUpdateNotify()

    def getMenuLabel(self):
        return '%s (%s)'%(os.path.basename(self.model.filename),
                          self.model.filename)


socketPort = 50007
selectTimeout = 0.25
class Listener(threading.Thread):
    def __init__(self, editor, closed):
        #self.queue = queue
        self.editor = editor
        self.closed = closed
        threading.Thread.__init__(self)

    def run(self, host='127.0.0.1', port=socketPort):
        import socket
        from select import select
        # Open a socket and listen.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except socket.error, err:
            self.closed.set()
            return

        s.listen(5)
        while 1:
            while 1:
                # Listen for 0.25 s, then check if closed is set. In that case,
                # end thread by returning.
                ready, dummy, dummy = select([s],[],[], selectTimeout)
                if self.closed.isSet():
                    return
                if ready:
                    break

            # Accept a connection, read the data and put it into the queue.
            conn, addr = s.accept()
            l = []
            while 1:
                data = conn.recv(1024)
                if not data: break
                l.append(data)
            name = ''.join(l)
            if name.strip():
                wx.CallAfter(self.editor.openOrGotoModule, name)
            conn.close()


def socketFileOpenServerListen(editor):
    closed = threading.Event()
    listener = Listener(editor, closed)
    listener.start()
    return closed, listener


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = HistoryPopup(None, (), {})
    app.MainLoop()
