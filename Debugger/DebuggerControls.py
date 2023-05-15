import os, pprint
from reprlib import Repr

import wx
import wx.lib.stattext

import Preferences, Utils
from Preferences import IS
from Utils import _

from Explorers import Explorer

from Debugger.Breakpoint import bplist

SEL_STATE = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED

class DebuggerListCtrl(wx.ListView, Utils.ListCtrlSelectionManagerMix):
    def __init__(self, parent, wId):
        wx.ListView.__init__(self, parent, wId,
              style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES | wx.CLIP_CHILDREN)
        Utils.ListCtrlSelectionManagerMix.__init__(self)

wxID_STACKVIEW = wx.NewIdRef(count=1)
class StackViewCtrl(DebuggerListCtrl):
    def __init__(self, parent, flist, debugger):
        DebuggerListCtrl.__init__(self, parent, wxID_STACKVIEW)

        self.InsertColumn(0, _('Frame'), wx.LIST_FORMAT_LEFT, 150)
        self.InsertColumn(1, _('Line'), wx.LIST_FORMAT_LEFT, 35)
        self.InsertColumn(2, _('Code'), wx.LIST_FORMAT_LEFT, 300)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnStackItemSelected, id=wxID_STACKVIEW)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnGotoSource)

        self.flist = flist
        self.debugger = debugger
        self.stack = []

    def load_stack(self, stack, index=None):
        import linecache

        self.stack = stack
        data = []

        pos = 0
        count = self.GetItemCount()
        for entry in stack:
            lineno = entry['lineno']
            modname = entry['modname']
            filename = entry['client_filename']
            funcname = entry['funcname']
            sourceline = linecache.getline(filename, lineno)
            sourceline = sourceline.strip()
            if funcname in ("?", "", None):
                #item = "%s, line %d: %s" % (modname, lineno, sourceline)
                attrib = modname
            else:
                #item = "%s.%s(), line %d: %s" % (modname, funcname,
                #                                 lineno, sourceline)
                # XXX methods will be shown as "module.function"
                # when maybe they ought to be shown as "module.class.method".
                attrib = modname + '.' + funcname
            #if pos == index:
            #    item = "> " + item
            if pos >= count:
                # Insert.
                self.InsertItem(pos, attrib)
                count = count + 1
            else:
                # Update.
                self.SetStringItem(pos, 0, attrib, -1)
            self.SetStringItem(pos, 1, repr(lineno), -1)
            self.SetStringItem(pos, 2, sourceline, -1)
            pos = pos + 1

        while pos < count:
            self.DeleteItem(count - 1)
            count = count - 1

    def OnStackItemSelected(self, event):
        selection = self.getSelection()
        stacklen = len(self.stack)
        if 0 <= selection < stacklen:
            self.debugger.invalidatePanes()
            self.debugger.updateSelectedPane()

    def selectCurrentEntry(self):
        selection = self.getSelection()
        newsel = self.GetItemCount() - 1
        if newsel != selection:
            if selection >= 0:
                item = self.GetItem(selection)
                item.m_state = item.m_state & ~wx.LIST_STATE_SELECTED
                self.SetItem(item)
            if newsel >= 0:
                item = self.GetItem(newsel)
                item.m_state = item.m_state | wx.LIST_STATE_SELECTED
                self.SetItem(item)
        if newsel >= 0:
            self.EnsureVisible(newsel)

    def OnGotoSource(self, event=None):
        selection = self.getSelection()
        if selection != -1:
            entry = self.stack[selection]
            lineno = entry['lineno']
            modname = entry['modname']
            filename = entry['client_filename']
            if not filename:
                return

            editor = self.debugger.editor
            editor.SetFocus()
            try:
                editor.openOrGotoModule(filename)
            except Explorer.TransportLoadError as err:
                serverPath = entry['filename']
                if serverPath[0] == '<' and serverPath[-1] == '>':
                    wx.LogError(_('Not a source file: %s, probably an executed '
                               'string.')%serverPath)
                    return

                res = wx.MessageBox(_('Could not open file: %s.\n\nIf This is a '
                      'server path for which you\nhave not defined a mapping '
                      'click "Yes" to browse to the file to the mapping can '
                      'be computed.\nPress "No" to open the path dialog.')%filename,
                      _('File Open Error, try to compute path?'),
                      wx.ICON_WARNING | wx.YES_NO | wx.CANCEL)
                if res == wx.YES:
                    clientPath = editor.openFileDlg(curfile=os.path.basename(filename))
                    if clientPath:
                        clientPath = prevClientPath = Explorer.splitURI(clientPath)[2]
                        prevServerPath = serverPath
                        while True:
                            serverPath, serverBase = os.path.split(serverPath)
                            clientPath, clientBase = os.path.split(clientPath)

                            if serverBase != clientBase:
                                paths = self.debugger.serverClientPaths[:]
                                paths.append( (prevServerPath, prevClientPath) )
                                if self.debugger.OnPathMappings(paths=paths):
                                    self.refreshClientFilenames()
                                break

                            if not serverPath or not clientPath:
                                wx.LogError(_('Paths are identical'))
                                break

                            prevClientPath = clientPath
                            prevServerPath = serverPath

                elif res == wx.NO:
                    if self.debugger.OnPathMappings():
                        self.refreshClientFilenames()
                return

            model = editor.getActiveModulePage().model
            view = model.getSourceView()
            if view is not None:
                view.focus()
                view.SetFocus()
                view.selectLine(lineno - 1)

    def refreshClientFilenames(self):
        for entry in self.stack:
            entry['client_filename'] = \
                  self.debugger.serverFNToClientFN(entry['filename'])


[wxID_BREAKVIEW, wxID_BREAKSOURCE, wxID_BREAKEDIT, wxID_BREAKDELETE,
 wxID_BREAKENABLED, wxID_BREAKREFRESH, wxID_BREAKIGNORE] = Utils.wxNewIds(7)

class BreakViewCtrl(DebuggerListCtrl):
    def __init__(self, parent, debugger):
        DebuggerListCtrl.__init__(self, parent, wxID_BREAKVIEW)

        self.InsertColumn(0, _('Module'), wx.LIST_FORMAT_LEFT, 90)
        self.InsertColumn(1, _('Line'), wx.LIST_FORMAT_CENTER, 40)
        self.InsertColumn(2, _('Ignore'), wx.LIST_FORMAT_CENTER, 45)
        self.InsertColumn(3, _('Hits'), wx.LIST_FORMAT_CENTER, 45)
        self.InsertColumn(4, _('Condition'), wx.LIST_FORMAT_LEFT, 250)

        self.brkImgLst = wx.ImageList(16, 16)
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-red.png'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-yellow.png'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-gray.png'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-blue.png'))

        self.Bind(wx.EVT_LEFT_DCLICK, self.OnGotoSource)

        self.debugger = debugger

        self.menu = wx.Menu()

        self.menu.Append(wxID_BREAKSOURCE, _('Goto source'))
        self.menu.Append(wxID_BREAKREFRESH, _('Refresh'))
        self.menu.AppendSeparator()
        self.menu.Append(wxID_BREAKIGNORE, _('Edit ignore count'))
        self.menu.Append(wxID_BREAKEDIT, _('Edit condition'))
        self.menu.Append(wxID_BREAKDELETE, _('Delete'))
        self.menu.AppendSeparator()
        self.menu.Append(wxID_BREAKENABLED, _('Enabled'), '', True)

        self.menu.Check(wxID_BREAKENABLED, True)

        self.Bind(wx.EVT_MENU, self.OnGotoSourceRight, id=wxID_BREAKSOURCE)
        self.Bind(wx.EVT_MENU, self.OnRefresh, id=wxID_BREAKREFRESH)
        self.Bind(wx.EVT_MENU, self.OnEditIgnore, id=wxID_BREAKIGNORE)
        self.Bind(wx.EVT_MENU, self.OnEditCondition, id=wxID_BREAKEDIT)
        self.Bind(wx.EVT_MENU, self.OnDelete, id=wxID_BREAKDELETE)
        self.Bind(wx.EVT_MENU, self.OnToggleEnabled, id=wxID_BREAKENABLED)
        self.pos = None

        self.setPopupMenu(self.menu)

        self.AssignImageList(self.brkImgLst, wx.IMAGE_LIST_SMALL)

        self.bps = []
        self.stats_map = {}

    def destroy(self):
        self.menu.Destroy()
        self.brkImgLst = None

    def updateBreakpointStats(self, stats):
        """Received from debugger.

        stats is a list of mappings."""
        stats_map = {}
        for item in stats:
            fn = item['client_filename']
            lineno = item['lineno']
            stats_map[(fn, lineno)] = item
            if not bplist.hasBreakpoint(fn, lineno):
                # A hard breakpoint was hit and a new breakpoint was created.
                bplist.addBreakpoint(fn, lineno)
        self.stats_map = stats_map

    def refreshList(self):
        self.DeleteAllItems()
        bps = bplist.getBreakpointList()

        # Sort by filename and lineno.
        #TODO Don't sort at all for now. Fix this up later
        # bps.sort(lambda a, b:
        #          cmp((a['filename'], a['lineno']),
        #              (b['filename'], b['lineno'])))

        # Sort by filename and lineno.
        # bps.sort(key = lambda x:
        #          cmp((a['filename'], a['lineno']),
        #              (b['filename'], b['lineno'])))

        self.bps = bps
        for p in range(len(bps)):
            bp = bps[p]
            # setup prelim image
            imgIdx = 0
            if not bp['enabled']: imgIdx = 2
            elif bp['temporary']: imgIdx = 3

            # FIXME
            # self.InsertImageStringItem(
            #     p, os.path.basename(bp['filename']), imgIdx)
            # self.SetStringItem(p, 1, str(bp['lineno']))

            self.InsertItem(
                p, os.path.basename(bp['filename']), imgIdx)
            self.SetItem(p, 1, str(bp['lineno']))

            hits = ''
            ignore = ''
            cond = ''
            if self.stats_map:
                item = self.stats_map.get((bp['filename'], bp['lineno']), None)
                if item is not None:
                    hits = str(item['hits'])
                    ignore = str(item['ignore'])
                    cond = item['cond'] or ''

            # self.SetStringItem(p, 2, ignore)
            # self.SetStringItem(p, 3, hits)
            # self.SetStringItem(p, 4, cond)
            self.SetItem(p, 2, ignore)
            self.SetItem(p, 3, hits)
            self.SetItem(p, 4, cond)

    def addBreakpoint(self, filename, lineno):
        self.refreshList()

    def selectBreakpoint(self, filename, lineno):
        idx = 0
        for bp in self.bps:
            if bp['filename']==filename and bp['lineno']==lineno:
                self.SetItemState(idx, SEL_STATE, SEL_STATE)
                self.EnsureVisible(idx)
                return
            idx = idx + 1

    def OnGotoSource(self, event=None):
        sel = self.getSelection()
        if sel != -1:
            self.gotoSourceForItem(sel)

    def OnGotoSourceRight(self, event):
        sel = self.getSelection()
        if sel != -1:
            self.gotoSourceForItem(sel)

    def gotoSourceForItem(self, sel):
        bp = self.bps[sel]
        filename = bp['filename']
        if not filename:
            return
        editor = self.debugger.editor
        editor.SetFocus()
        model, ctrlr = editor.openOrGotoModule(filename)
        view = model.getSourceView()
        if view is not None:
            view.focus()
            view.GotoLine(bp['lineno'] - 1)

    def OnDelete(self, event):
        sel = self.getSelection()
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            bplist.deleteBreakpoints(filename, bp['lineno'])

            # Delete in debug server
            server_fn = self.debugger.clientFNToServerFN(filename)
            self.debugger.invokeInDebugger(
                'clearBreakpoints', (server_fn, bp['lineno']))

            # Unmark the breakpoint in the editor (if open)
            sourceView = self.debugger.getEditorSourceView(filename)
            if sourceView:
                sourceView.deleteBreakMarkers(bp['lineno'])

            #self.debugger.requestDebuggerStatus()
            self.refreshList()

    def OnRefresh(self, event):
        self.refreshList()

    def OnToggleEnabled(self, event):
        sel = self.getSelection()
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            lineno = bp['lineno']
            enabled = bp['enabled'] = not bp['enabled']
            bplist.enableBreakpoints(filename, lineno, enabled)
            server_fn = self.debugger.clientFNToServerFN(filename)
            self.debugger.invokeInDebugger(
                'enableBreakpoints', (server_fn, lineno, enabled))
            self.refreshList()

            sourceView = self.debugger.getEditorSourceView(filename)
            if sourceView:
                sourceView.deleteBreakMarkers(bp['lineno'])
                sourceView.setBreakMarker(bp)

    def getPopupMenu(self):
        wx.Yield()
        sel = self.getSelection()

        self.menu.Enable(wxID_BREAKSOURCE, sel != -1)
        self.menu.Enable(wxID_BREAKIGNORE, sel != -1)
        self.menu.Enable(wxID_BREAKEDIT, sel != -1)
        self.menu.Enable(wxID_BREAKDELETE, sel != -1)
        self.menu.Enable(wxID_BREAKENABLED, sel != -1)

        if sel != -1:
            bp = self.bps[sel]
            self.menu.Check(wxID_BREAKENABLED, bp['enabled'])

        return DebuggerListCtrl.getPopupMenu(self)

    def OnEditCondition(self, event):
        sel = self.getSelection()
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            lineno = bp['lineno']
            cond = bp['cond']

            dlg = wx.TextEntryDialog(self, _('Condition to break on:'),
                  _('Change condition'), cond)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    cond = dlg.GetValue().strip()

                    bplist.conditionalBreakpoints(filename, lineno, cond)
                    # Update debug server
                    server_fn = self.debugger.clientFNToServerFN(filename)
                    self.debugger.invokeInDebugger(
                        'conditionalBreakpoints', (server_fn, lineno, cond))

                    self.debugger.requestDebuggerStatus()
                    self.refreshList()
            finally:
                dlg.Destroy()

    def OnEditIgnore(self, event):
        sel = self.getSelection()
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            lineno = bp['lineno']
            ignore = bp['ignore']

            dlg = wx.TextEntryDialog(self, _('Number of hits to ignore:'),
                  _('Change ignore count'), repr(ignore))
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    ignore = int(dlg.GetValue())
                    # Update debugger list and debug server
                    bplist.ignoreBreakpoints(filename, lineno, ignore)
                    server_fn = self.debugger.clientFNToServerFN(filename)
                    self.debugger.invokeInDebugger(
                        'ignoreBreakpoints', (server_fn, lineno, ignore))

                    self.debugger.requestDebuggerStatus()
                    self.refreshList()
            finally:
                dlg.Destroy()

# XXX Expose classes' dicts as indented items

wxID_NSVIEW = wx.NewIdRef(count=1)
class NamespaceViewCtrl(DebuggerListCtrl):
    def __init__(self, parent, debugger, is_local, name):
        DebuggerListCtrl.__init__(self, parent, wxID_NSVIEW)

        self.InsertColumn(0, _('Attribute'), wx.LIST_FORMAT_LEFT, 125)
        self.InsertColumn(1, _('Value'), wx.LIST_FORMAT_LEFT, 200)

        self.is_local = is_local

        self.menu = wx.Menu()

        idAs = wx.NewIdRef(count=1)
        idA = wx.NewIdRef(count=1)
        self.menu.Append(idAs, _('Add as watch'))
        self.menu.Append(idA, _('Add a %s watch') % name)
        self.Bind(wx.EVT_MENU, self.OnAddAsWatch, id=idAs)
        self.Bind(wx.EVT_MENU, self.OnAddAWatch, id=idA)
        outputId = wx.NewIdRef(count=1)
        self.menu.Append(outputId, _('Write value to Output'))
        self.Bind(wx.EVT_MENU, self.OnValueToOutput, id=outputId)

        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)

        self.pos = None

        self.setPopupMenu(self.menu)

        self.repr = Repr()
        self.repr.maxstring = 100
        self.repr.maxother = 100
        self.names = []

        self.debugger = debugger

    def destroy(self):
        self.menu.Destroy()

    def showLoading(self):
        self.DeleteAllItems()
        self.InsertItem(0, '...')

    def load_dict(self, nsdict, force=0):
        self.DeleteAllItems()

        if not nsdict:
            pass
        else:
            self.names = list(nsdict.keys())
            self.names.sort()
            row = 0
            for name in self.names:
                svalue = nsdict[name]

                self.InsertItem(row, name)
                self.SetStringItem(row, 1, svalue, -1)

                row = row + 1

    def OnAddAsWatch(self, event):
        selected = self.getSelection()
        if selected != -1:
            name = self.names[selected]
            self.debugger.add_watch(name, self.is_local)

    def OnAddAWatch(self, event):
        self.debugger.add_watch('', self.is_local)

    def OnValueToOutput(self, event):
        selected = self.getSelection()
        if selected != -1:
            name = self.names[selected]
            self.debugger.valueToOutput(name)

    def OnDoubleClick(self, event):
        if event.ControlDown():
            self.OnValueToOutput(event)
        else:
            self.OnAddAsWatch(event)


wxID_WATCHVIEW = wx.NewIdRef(count=1)
class WatchViewCtrl(DebuggerListCtrl):
    def __init__(self, parent, images, debugger):
        DebuggerListCtrl.__init__(self, parent, wxID_WATCHVIEW)

        self.InsertColumn(0, _('Attribute'), wx.LIST_FORMAT_LEFT, 125)
        self.InsertColumn(1, _('Value'), wx.LIST_FORMAT_LEFT, 200)

        self.repr = Repr()
        self.repr.maxstring = 60
        self.repr.maxother = 60
        self.debugger = debugger

        self.watches = []

        self.AssignImageList(images, wx.IMAGE_LIST_SMALL)

        self.menu = wx.Menu()

        wid = wx.NewIdRef(count=1)
        self.menu.Append(wid, _('Add local watch'))
        self.Bind(wx.EVT_MENU, self.OnAddLocal, id=wid)
        wid = wx.NewIdRef(count=1)
        self.menu.Append(wid, _('Add global watch'))
        self.Bind(wx.EVT_MENU, self.OnAddGlobal, id=wid)
        self.editId = wx.NewIdRef(count=1)
        self.menu.Append(self.editId, _('Edit watch'))
        self.Bind(wx.EVT_MENU, self.OnEdit, id=self.editId)
        self.outputId = wx.NewIdRef(count=1)
        self.menu.Append(self.outputId, _('Write value to Output'))
        self.Bind(wx.EVT_MENU, self.OnValueToOutput, id=self.outputId)
        self.deleteId = wx.NewIdRef(count=1)
        self.menu.Append(self.deleteId, _('Delete'))
        self.Bind(wx.EVT_MENU, self.OnDelete, id=self.deleteId)
        self.expandId = wx.NewIdRef(count=1)
        self.menu.Append(self.expandId, _('Expand'))
        self.Bind(wx.EVT_MENU, self.OnExpand, id=self.expandId)
        wid = wx.NewIdRef(count=1)
        self.menu.Append(wid, _('Delete All'))
        self.Bind(wx.EVT_MENU, self.OnDeleteAll, id=wid)

        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)

        self.pos = None

        self.setPopupMenu(self.menu)

    def destroy(self):
        self.menu.Destroy()

    def add_watch(self, name, local, pos=-1):
        if name:
            if pos < 0 or pos >= len(self.watches):
                self.watches.append((name, local))
                pos = len(self.watches)-1
            else:
                self.watches.insert(pos, (name, local))
        else:
            dlg = wx.TextEntryDialog(
                self, 'Expression:', 'Add a watch:', '')
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    self.watches.append((dlg.GetValue(), local))
                    pos = len(self.watches)-1
            finally:
                dlg.Destroy()
        #self.SetItemState(pos, SEL_STATE, SEL_STATE)
        #self.EnsureVisible(pos)

    def showLoading(self):
        self.load_dict(None, loading=1)

    def load_dict(self, svalues, force=0, loading=0):
        count = self.GetItemCount()
        row = 0
        for name, local in self.watches:
            if svalues:
                svalue = svalues.get(name, '???')
            elif loading:
                svalue = '...'
            else:
                svalue = '???'
            if local:
                idx = 3
            else:
                idx = 4
            if row >= count:
                # Insert.
                self.InsertItem(row, name, idx)
                count = count + 1
            else:
                # Update.
                self.SetItem(row, 0, name, idx)
            self.SetItem(row, 1, svalue, idx)
            row = row + 1
        while row < count:
            self.DeleteItem(count - 1)
            count = count - 1

    def OnAddLocal(self, event):
        self.add_watch('', True)
        self.debugger.updateSelectedPane(force=1)

    def OnAddGlobal(self, event):
        self.add_watch('', False)
        self.debugger.updateSelectedPane(force=1)

    def OnEdit(self, event):
        selected = self.getSelection()

        if selected != -1:
            name, local = self.watches[selected]
            dlg = wx.TextEntryDialog(
                self, _('Expression:'), _('Edit watch:'), name)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    self.watches[selected] = (dlg.GetValue(), local)
                    self.debugger.updateSelectedPane(force=1)
            finally:
                dlg.Destroy()

    def OnDelete(self, event):
        selected = self.getSelection()
        if selected != -1:
            del self.watches[selected]
            self.DeleteItem(selected)
            self.debugger.updateSelectedPane(force=1)

    def OnDeleteAll(self, event):
        del self.watches[:]
        self.DeleteAllItems()

    def OnExpand(self, event):
        selected = self.getSelection()
        if selected != -1:
            name, local = self.watches[selected]
            self.debugger.requestWatchSubobjects(name, local, selected + 1)

    def getPopupMenu(self):
        sel = self.getSelection()

        self.menu.Enable(self.editId, sel != -1)
        self.menu.Enable(self.deleteId, sel != -1)
        self.menu.Enable(self.expandId, sel != -1)

        return DebuggerListCtrl.getPopupMenu(self)

    def OnValueToOutput(self, event):
        selected = self.getSelection()

        if selected != -1:
            name = self.watches[selected][0]
            self.debugger.valueToOutput(name)

    def OnDoubleClick(self, event):
        if event.ControlDown():
            self.OnValueToOutput(event)
        else:
            self.OnEdit(event)


class DebugStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1, style=0)
        self.SetFieldsCount(2)
        self.SetMinHeight(30)
        #self.SetStatusWidths([-1, -1, 16])

        self.stateCols = {'except': wx.Colour(0xFF, 0xFF, 0x44),#wxNamedColour('yellow'),
                          'info':   wx.Colour('white'),
                          'break':  wx.Colour(0xFF, 0x44, 0x44),#wxNamedColour('red'),
                          'busy':   wx.Colour(0xBB, 0xE0, 0xFF)}

        self.instr_ptr = wx.lib.stattext.GenStaticText(self, -1, ' ',
              style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.instr_ptr.SetBackgroundColour(wx.Colour(0xEE, 0xEE, 0xEE))
        self._setCtrlDims(self.instr_ptr, self.GetFieldRect(0))

        self.state = wx.lib.stattext.GenStaticText(self, -1, _('Ready.'),
              style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.state.SetBackgroundColour(self.stateCols['info'])
        self._setCtrlDims(self.state, self.GetFieldRect(1))

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        (w,h) = dc.GetTextExtent('X')
        h = int(h * 1.8)
        self.SetSize(wx.Size(100, h))

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def _setCtrlDims(self, ctrl, rect):
        ctrl.SetSize(rect.x+2, rect.y+2, rect.width-4, rect.height-4)

    def updateState(self, message, sts_type='except'):
        if message:
            self.state.SetBackgroundColour(self.stateCols[sts_type])
        else:
            self.state.SetBackgroundColour(self.stateCols['info'])
        self.state.SetLabel(message)
        self.state.SetToolTip(message)

        self._setCtrlDims(self.state, self.GetFieldRect(1))

    def updateInstructionPtr(self, status):
        self.instr_ptr.SetLabel(status)
        self._setCtrlDims(self.instr_ptr, self.GetFieldRect(0))

    def OnSize(self, event):
        self._setCtrlDims(self.instr_ptr, self.GetFieldRect(0))
        self._setCtrlDims(self.state, self.GetFieldRect(1))
