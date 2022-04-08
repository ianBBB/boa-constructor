#----------------------------------------------------------------------------
# Name:         Debugger.py
# Purpose:      wxPython debugger, started as a port of IDLE's debugger
#               written by Guido van Rossum
#
# Authors:      Riaan Booysen, Shane Hathaway
#
# Created:      2000/01/11
# RCS-ID:       $Id$
# Copyright:    (c) 2000 - 2007 : Riaan Booysen, Shane Hathaway
# Licence:      GPL
#----------------------------------------------------------------------------

# XXX I must still try to see if it's not possible the change code while
# XXX debugging, reload sometimes works
# XXX Going to source code on an error

import sys, os

import wx

import Preferences, Utils
from Preferences import pyPath, IS, flatTools, keyDefs
from Utils import _

from DebuggerControls import StackViewCtrl, BreakViewCtrl, NamespaceViewCtrl,\
                             WatchViewCtrl, DebugStatusBar
import PathMappingDlg

from Breakpoint import bplist
from DebugClient import EVT_DEBUGGER_OK, EVT_DEBUGGER_EXC, \
     EVT_DEBUGGER_STOPPED, EmptyResponseError

# When an output window surpasses these limits, it will be trimmed.
TEXTCTRL_MAXLEN = 30000
TEXTCTRL_GOODLEN = 20000

STOP_GENTLY = 0

wxID_PAGECHANGED = wx.NewId()
wxID_TOPPAGECHANGED = wx.NewId()
class DebuggerFrame(wx.Frame, Utils.FrameRestorerMixin):
    debug_client = None
    _destroyed = 0
    _closing = 0

    def __init__(self, editor, filename=None, slave_mode=1):
        wx.Frame.__init__(self, editor, -1, _('Debugger'),
         style=wx.DEFAULT_FRAME_STYLE | wx.CLIP_CHILDREN|Preferences.childFrameStyle)

        self.winConfOption = 'debugger'
        self.loadDims()

        self.editor = editor
        self.running = 0
        self.slave_mode = slave_mode
        if filename:
            self.setDebugFile(filename)
        else:
            self.filename = ''

        self.SetIcon(IS.load('Images/Icons/Debug.ico'))

        self.viewsImgLst = wx.ImageList(16, 16)
        self.viewsImgLst.Add(IS.load('Images/Debug/Stack.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Breakpoints.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Watches.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Locals.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Globals.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Output.png'))

        self.invalidatePanes()

        self.sb = DebugStatusBar(self)
        self.SetStatusBar(self.sb)

        self.toolbar = wx.ToolBar(self, -1,
              style=wx.TB_HORIZONTAL | wx.NO_BORDER|flatTools)
        self.SetToolBar(self.toolbar)

        self.runId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Debug.png', _('Debug/Continue - %s')%keyDefs['Debug'][2],
          self.OnDebug) #, runs in debugger, stops at breaks and exceptions'
        self.runFullSpdId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/DebugFullSpeed.png', _('Debug/Continue full speed'),
          self.OnDebugFullSpeed) #'stops only at hard (code) breaks and exceptions'
        self.stepId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Step.png', _('Step - %s')%keyDefs['DebugStep'][2],
          self.OnStep)
        self.overId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Over.png', _('Over - %s')%keyDefs['DebugOver'][2],
          self.OnOver)
        self.outId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Out.png', _('Out - %s')%keyDefs['DebugOut'][2],
          self.OnOut)
        self.jumpId = -1
        if sys.version_info[:2] >= (2, 3):
            self.jumpId = Utils.AddToolButtonBmpIS(self, self.toolbar,
              'Images/Debug/Jump.png', _('Jump to line'), self.OnJump)

        self.pauseId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Pause.png',  _('Pause'), self.OnPause)
        self.stopId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Stop.png',  _('Stop'), self.OnStop)
        self.toolbar.AddSeparator()
        self.sourceTraceId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/SourceTrace-Off.png',  _('Trace in source'),
          self.OnSourceTrace, '1')
        self.debugBrowseId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/DebugBrowse.png',  _('Debug browsing'),
          self.OnDebugBrowse, '1')
        if Preferences.psPythonShell == 'Shell':
            self.shellNamespaceId = Utils.AddToolButtonBmpIS(self, self.toolbar,
              'Images/Debug/ShellDebug.png',  _('Eval in shell'),
              self.OnDebugNamespace, '1')
        else:
            self.shellNamespaceId = -1
        self.toolbar.AddSeparator()
        self.pathMappingsId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/PathMapping.png', _('Edit client/server path mappings...'),
          self.OnPathMappings)
        self.splitOrientId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/SplitOrient.png', _('Toggle split orientation'),
          self.OnToggleSplitOrient)

        self.SetAcceleratorTable(wx.AcceleratorTable( [
          (keyDefs['Debug'][0], keyDefs['Debug'][1], self.runId),
          (keyDefs['DebugStep'][0], keyDefs['DebugStep'][1], self.stepId),
          (keyDefs['DebugOver'][0], keyDefs['DebugOver'][1], self.overId),
          (keyDefs['DebugOut'][0], keyDefs['DebugOut'][1], self.outId) ] ))

        self.toolbar.Realize()

        self.toolbar.ToggleTool(self.sourceTraceId, True)
        self.toolbar.ToggleTool(self.debugBrowseId, False)

        self.splitter = wx.SplitterWindow(self, -1,
               style=wx.SP_NOBORDER|Preferences.splitterStyle)

        (stackImgIdx, breaksImgIdx, watchesImgIdx, localsImgIdx,
                  globalsImgIdx) = range(5)

        # Create a Notebook
        self.nbTop = wx.Notebook(self.splitter, wxID_TOPPAGECHANGED)
        self.nbTop.SetImageList(self.viewsImgLst)

        self.stackView = StackViewCtrl(self.nbTop, None, self)
        self.nbTop.AddPage(self.stackView, _('Stack'), imageId=stackImgIdx)

        self.breakpts = BreakViewCtrl(self.nbTop, self)
        self.nbTop.AddPage(self.breakpts, _('Breakpoints'), imageId=breaksImgIdx)

        # Create a Notebook
        self.nbBottom = wx.Notebook(self.splitter, wxID_PAGECHANGED,
              style=wx.CLIP_CHILDREN)
        self.nbBottom.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChange, id=wxID_PAGECHANGED)
        self.nbBottom.SetImageList(self.viewsImgLst)

        self.watches = WatchViewCtrl(self.nbBottom, self.viewsImgLst, self)
        self.nbBottom.AddPage(self.watches, _('Watches'), imageId=watchesImgIdx)

        self.locs = NamespaceViewCtrl(self.nbBottom, self, 1, 'local')
        self.nbBottom.AddPage(self.locs, _('Locals'), imageId=localsImgIdx)

        self.globs = NamespaceViewCtrl(
            self.nbBottom, self, 0, 'global')

        self.nbBottom.AddPage(self.globs, _('Globals'), imageId=globalsImgIdx)

        self.splitter.SetMinimumPaneSize(40)

        self.splitter.SplitHorizontally(self.nbTop, self.nbBottom)
        self.splitter.SetSashPosition(175)
        self.splitter.SetSplitMode(wx.SPLIT_HORIZONTAL)

        self.mlc = 0
        self.frame = None

        self.lastStepView = None
        self.lastStepLineno = -1

        self.stepping_enabled = 1

        self.setParams([])

        self.setServerClientPaths([])

        self.Bind(EVT_DEBUGGER_OK, self.OnDebuggerOk, id=self.GetId())
        self.Bind(EVT_DEBUGGER_EXC, self.OnDebuggerException, id=self.GetId())
        self.Bind(EVT_DEBUGGER_STOPPED, self.OnDebuggerStopped, id=self.GetId())

        # used to indicate when the debugger start,
        # would be better if there was a start event in addition to the OK event
        self._pid = None
        self._erroutFrm = self.editor.erroutFrm

        self.stream_timer = wx.PyTimer(self.OnStreamTimer)
        self.stream_timer.Start(100)

        self.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.OnToolOver)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def destroy(self):
        if self._destroyed:
            return
        self._destroyed = 1

        self.breakpts.destroy()
        self.watches.destroy()
        self.locs.destroy()
        self.globs.destroy()
        self.sb.stateCols = None
        if self.stream_timer is not None:
            self.stream_timer.Stop()
            self.stream_timer = None

    def setDefaultDimensions(self):
        self.SetDimensions(0, Preferences.underPalette,
              Preferences.inspWidth, Preferences.bottomHeight)

    _sashes_inited = 0
    def initSashes(self):
        if not self._sashes_inited:
            s = self.GetSize()
            if s.x /float(s.y) > 1:
                mode = wx.SPLIT_HORIZONTAL
            else:
                mode = wx.SPLIT_VERTICAL
            self.splitter.SetSplitMode(mode)
            self.OnToggleSplitOrient()
            self._sashes_inited = 1

    def add_watch(self, name, local):
        self.watches.add_watch(name, local)
        self.nbBottom.SetSelection(0)
        self.invalidatePanes()
        self.updateSelectedPane()

    def OnPageChange(self, event):
        sel = event.GetSelection()
        if sel >= 0:
            self.updateSelectedPane(sel)
        event.Skip()

    def invalidatePanes(self):
        self.updated_panes = [0, 0, 0]

    def updateSelectedPane(self, pageno=-1, do_request=1, force=0):
        if pageno < 0:
            pageno = self.nbBottom.GetSelection()
        if not self.updated_panes[pageno] or force:
            frameno = self.stackView.getSelection()
            if pageno == 0:
                self.watches.showLoading()
                if do_request:
                    self.requestWatches(frameno)
            else:
                if pageno==1: self.locs.showLoading()
                else: self.globs.showLoading()
                if do_request:
                    self.requestDict((pageno==1), frameno)

    def requestWatches(self, frameno):
        ws = self.watches.watches
        exprs = []
        for name, local in ws:
            exprs.append({'name':name, 'local':local})
        if exprs:
            self.invokeInDebugger(
                'evaluateWatches', (exprs, frameno), 'receiveWatches')
        else:
            # No exprs, so no request is necessary.
            self.watches.load_dict(None)
            self.updated_panes[0] = 1

    def receiveWatches(self, status):
        frameno = status['frameno']
        if frameno == self.stackView.getSelection():
            self.updated_panes[0] = 1
            self.watches.load_dict(status['watches'])
        else:
            # Re-request.
            self.updateSelectedPane()

    def requestDict(self, locs, frameno):
        self.invokeInDebugger(
            'getSafeDict', (locs, frameno), 'receiveDict')

    def receiveDict(self, status):
        frameno = status['frameno']
        if frameno == self.stackView.getSelection():
            if status.has_key('locals'):
                self.updated_panes[1] = 1
                self.locs.load_dict(status['locals'])
            if status.has_key('globals'):
                self.updated_panes[2] = 1
                self.globs.load_dict(status['globals'])
        else:
            # Re-request.
            self.updateSelectedPane()

    def requestWatchSubobjects(self, name, local, pos):
        self.invokeInDebugger(
            'getWatchSubobjects', (name, self.stackView.getSelection()),
            'receiveWatchSubobjects', (name, local, pos))

    def receiveWatchSubobjects(self, subnames, name, local, pos):
        for subname in subnames:
            self.watches.add_watch('%s.%s' % (name, subname), local, pos)
            pos = pos + 1
        self.nbBottom.SetSelection(0)
        self.invalidatePanes()
        self.updateSelectedPane()

    def requestVarValue(self, name):
        self.invokeInDebugger(
            'pprintVarValue', (name, self.stackView.getSelection()),
            'receiveVarValue')

    def receiveVarValue(self, val):
        if val:
            self.editor.setStatus(val)

    def getVarValue(self, name):
        if not name.strip():
            return None
        self._hasReceivedVal = 0
        self._receivedVal = None
        self.invokeInDebugger(
            'pprintVarValue', (name, self.stackView.getSelection()),
            'receiveVarValue2')
        # XXX I'm not comfortable with this...
        try:
            while not self._hasReceivedVal:
                wx.Yield()
            return self._receivedVal
        finally:
            del self._hasReceivedVal
            del self._receivedVal

    def receiveVarValue2(self, val):
        self._receivedVal = val
        self._hasReceivedVal = 1

    def valueToOutput(self, name):
        val = self.getVarValue(name)
        self.editor.erroutFrm.outputTC.SetValue('')
        self.editor.erroutFrm.appendToOutput(val)

#---------------------------------------------------------------------------

    def setParams(self, params):
        self.params = params

    def setDebugFile(self, filename):
        self.filename = filename
        title = '%s - %s' % (os.path.basename(filename), filename)
        self.setTitleInfo(title)

    def setTitleInfo(self, info):
        pidinfo = ''
        if self.debug_client:
            pid = self.debug_client.getProcessId()
            if pid:
                pidinfo = '(%s) ' % pid
        title = _('Debugger %s- %s') % (pidinfo, info)
        self.SetTitle(title)

    def setDebugClient(self, client=None):
        if client is None:
            from ChildProcessClient import ChildProcessClient
            client = ChildProcessClient(self, Preferences.debugServerArgs)
        self.debug_client = client

    def setServerClientPaths(self, paths):
        self.serverClientPaths = paths


    def invokeInDebugger(self, m_name, m_args=(), r_name=None, r_args=()):
        """
        Invokes a method asynchronously in the debugger,
        possibly expecting a debugger event to be generated
        when finished.
        """
        self.debug_client.invokeOnServer(m_name, m_args, r_name, r_args)

    def killDebugger(self):
        if self._destroyed:
            return
        self.running = 0
        if self.debug_client:
            try:
                self.debug_client.kill()
            except:
                print _('Error on killing debugger: %s: %s')%sys.exc_info()[:2]
        self.clearViews()

    def OnDebuggerStopped(self, event):
        """Called when a debugger process stops."""
        show_dialog = 0
        if self.running:
            show_dialog = 1
        self.killDebugger()
        if self._closing:
            # Close the window.
            self.destroy()
            self.Destroy()
        elif show_dialog:
            wx.MessageBox(_('The debugger process stopped prematurely.'),
                  _('Debugger stopped'), wx.OK | wx.ICON_EXCLAMATION | wx.CENTRE)

        if self._pid:
            self._erroutFrm.processFinished(self._pid)
            self._pid = None

    def OnStreamTimer(self, event=None):
        if self.stream_timer:
            self.updateErrOutWindow()

    def updateErrOutWindow(self):
        if self.debug_client:
            info = self.debug_client.pollStreams()
            if info and self.editor:
                stdout_text, stderr_text = info
                if stdout_text:
                    self.editor.erroutFrm.appendToOutput(stdout_text)
                if stderr_text:
                    self.editor.erroutFrm.appendToErrors(stderr_text)

    def OnDebuggerOk(self, event):
        if self._destroyed:
            return

        if self._pid is None and self.debug_client:
            self._pid = self.debug_client.getProcessId()
            script = os.path.basename(self.filename)
            intp = os.path.basename(self.debug_client.pyIntpPath)
            if intp:
                self._erroutFrm.processStarted(intp, self._pid, script, 'Debug')

        self.restoreDebugger()
        self.enableStepping()
        receiver_name = event.GetReceiverName()
        if receiver_name is not None:
            rcv = getattr(self, receiver_name)
            rcv( *( (event.GetResult(),) + event.GetReceiverArgs()) )

    def OnDebuggerException(self, event):
        if self._destroyed:
            return

        self.enableStepping()
        t, v = event.GetExc()
        if isinstance(v, EmptyResponseError):
            if not self.debug_client or not self.debug_client.isAlive():
                # If the debugger was killed, this exception is normal.
                return

        self.restoreDebugger()
        if hasattr(t, '__name__'):
            t = t.__name__
        msg = '%s: %s.' % (t, v)

        confirm = wx.MessageBox(_('%s\n\nStop debugger?')%msg,
                  _('Debugger Communication Exception'),
                  wx.YES_NO | wx.YES_DEFAULT | wx.ICON_EXCLAMATION |
                  wx.CENTRE) == wx.YES

        if confirm:
            self.killDebugger()

    def runProcess(self, autocont=0):
        self.running = 1
        self.sb.updateState(_('Waiting...'), 'busy')
        brks = bplist.getBreakpointList()
        for brk in brks:
            brk['filename'] = self.clientFNToServerFN(brk['filename'])
        if self.slave_mode:
            # Work with a child process.
            add_paths = simplifyPathList(pyPath)
            add_paths = map(self.clientFNToServerFN, add_paths)
            filename = self.clientFNToServerFN(self.filename)
            self.invokeInDebugger(
                'runFileAndRequestStatus',
                (filename, self.params or [], autocont, add_paths, brks),
                'receiveDebuggerStatus')
        else:
            # Work with a peer or remote process.
            self.invokeInDebugger(
                'setupAndRequestStatus',
                (autocont, brks),
                'receiveDebuggerStatus')

        # InProcessClient TODO: setup the execution environment
        # the way it used to be done.

    def proceedAndRequestStatus(self, command, temp_breakpoint=None, args=()):
        # Non-blocking.
        self.sb.updateState(_('Running...'), 'busy')
        if not temp_breakpoint:
            temp_breakpoint = 0
        self.invokeInDebugger('proceedAndRequestStatus',
                              (command, temp_breakpoint, args),
                              'receiveDebuggerStatus')

    def clientFNToServerFN(self, filename):
        """Converts a filename on the client to a filename on the server.

        Currently just turns file URLs into paths.  If you want to be able to
        set breakpoints when running the client in a different environment
        from the server, you'll need to expand this.
        """
        # XXX should we .fncache this? Files changing names are undefined
        # XXX during the lifetime of the debugger

        from Explorers.Explorer import splitURI, getTransport
        from Explorers.ExplorerNodes import all_transports

        prot, category, filepath, filename = splitURI(filename)
        if prot == 'zope':
            node = getTransport(prot, category, filepath, all_transports)
            if node:
                props = node.properties
                return 'zopedebug://%s:%s/%s/%s'%(props['host'],
                      props['httpport'], filepath, node.metatype)
            else:
                raise Exception(_('No Zope connection for: %s')%filename)
        elif prot == 'zopedebug':
            raise Exception(_('"zopedebug" is a server filename protocol'))
        else:
        #if prot == 'file':
            if self.serverClientPaths:
                normFilepath = os.path.normcase(filepath)
                for serverPath, clientPath in self.serverClientPaths:
                    normClientPath = os.path.normcase(clientPath)
                    if normFilepath.startswith(normClientPath):
                        return serverPath+normFilepath[len(normClientPath):]
            return filepath

    def serverFNToClientFN(self, filename):
        """Converts a filename on the server to a filename on the client.

        Currently just generates URLs.  If you want to be able to
        set breakpoints when running the client in a different environment
        from the server, you'll need to expand this.
        """
        from Explorers.Explorer import splitURI
        if self.serverClientPaths:
            normFilepath = os.path.normcase(filename)
            for serverPath, clientPath in self.serverClientPaths:
                normServerPath = os.path.normcase(serverPath)
                if normFilepath.startswith(normServerPath):
                    return splitURI(clientPath+normFilepath[len(normServerPath):])[3]

        return splitURI(filename)[3]


    def deleteBreakpoints(self, filename, lineno):
        fn = self.clientFNToServerFN(filename)
        self.invokeInDebugger('clearBreakpoints', (fn, lineno))
        self.breakpts.refreshList()

    def adjustBreakpoints(self, filename, lineno, delta):
        fn = self.clientFNToServerFN(filename)
        self.invokeInDebugger('adjustBreakpoints', (fn, lineno, delta))
        self.breakpts.refreshList()

    def setBreakpoint(self, filename, lineno, tmp):
        fn = self.clientFNToServerFN(filename)
        self.invokeInDebugger('addBreakpoint', (fn, lineno, tmp))
        self.breakpts.refreshList()

    def requestDebuggerStatus(self):
        self.sb.updateState('Waiting...', 'busy')
        self.invokeInDebugger('getStatusSummary', (),
                              'receiveDebuggerStatus')

    def receiveDebuggerStatus(self, info):
        self.updateErrOutWindow()

        self.setDebugFile(self.filename)

        # Determine the current lineno, filename, and
        # funcname from the stack.

        # Update call stack
        stack = info['stack']
        # Translate server filenames to client filenames.
        for frame in stack:
            frame['client_filename'] = (
                self.serverFNToClientFN(frame['filename']))

        # Determine the current lineno, filename, and
        # funcname from the stack.
        if stack:
            bottom = stack[-1]
            filename = bottom['client_filename']
            funcname = bottom['funcname']
            lineno = bottom['lineno']
            base = os.path.basename(filename)
        else:
            filename = funcname = lineno = base = ''

        # Show running status.
        self.running = info['running']
        if self.running:
            message = "%s:%s" % (base, lineno)
            if funcname != "?":
                message = "%s: %s()" % (message, funcname)
        else:
            message = _('Finished.')
        self.sb.updateInstructionPtr(message)

        # Show exception information.
        exc_type = info.get('exc_type', None)
        exc_value = info.get('exc_value', None)
        if exc_type is not None:
            m1 = exc_type
            if exc_value is not None:
                try:
                    m1 = "%s: %s" % (m1, str(exc_value))
                except:
                    m1 = 'internal error'
            self.sb.updateState(m1)
        else:
            self.sb.updateState(_('Ready.'), 'info')

        # Load the stack view.
        sv = self.stackView
        if sv:
            i = info['frame_stack_len']
            sv.load_stack(stack, i)
            sv.selectCurrentEntry()

        # Update breakpoints view with stats.
        breaks = info['breaks']
        for item in breaks:
            item['client_filename'] = self.serverFNToClientFN(
                item['filename'])
        self.breakpts.updateBreakpointStats(breaks)

        self.breakpts.refreshList()

        # If at a breakpoint, display status.
        if bplist.hasBreakpoint(filename, lineno):
            bplist.clearTemporaryBreakpoints(filename, lineno)
            self.sb.updateState(_('Breakpoint.'), 'break')
            self.breakpts.selectBreakpoint(filename, lineno)

        self.selectSourceLine(filename, lineno)

        # All info in watches, locals, and globals panes is now invalid.
        self.invalidatePanes()
        # Update the currently selected pane.
        self.updateSelectedPane()
        # Receive stream data even if the user isn't looking.
        self.updateErrOutWindow()

        self.restoreDebugger()
        self.refreshTools()

    def restoreDebugger(self):
        if self.editor:
            if self.editor.palette.IsShown():
                if self.editor.palette.IsIconized():
                    self.editor.palette.restore()
                    self.editor.restore()
            elif self.editor.IsIconized():
                self.editor.restore()

    def clearStepPos(self):
        if self.lastStepView is not None:
            if hasattr(self.lastStepView, 'clearStepPos'):
                self.lastStepView.clearStepPos(self.lastStepLineno)
            self.lastStepView = None

    def getEditorSourceView(self, filename):
        if self.editor.modules.has_key(filename):
            return self.editor.modules[filename].model.getSourceView()
        else:
            return None

    def selectSourceLine(self, filename, lineno):
        if self.isSourceTracing():
            self.clearStepPos()
            if not filename:
                return

            #self.editor.SetFocus()
            try:
                self.editor.openOrGotoModule(filename)
            except Exception, err:
                self.editor.setStatus(
                      _('Debugger: Failed to open file %s')%filename, 'Error')
            else:
                model = self.editor.getActiveModulePage().model
                view = model.getSourceView()
                if view is not None:
                    view.focus(False)
                    #view.selectLine(lineno - 1)
                    view.GotoLine(lineno - 1)
                    if hasattr(view, 'setStepPos'):
                        view.setStepPos(lineno - 1)
                    else:
                        view.selectLine(lineno - 1)
                    self.lastStepView = view
                    self.lastStepLineno = lineno - 1

    def isSourceTracing(self):
        return self.toolbar.GetToolState(self.sourceTraceId)

    def isDebugBrowsing(self):
        return self.toolbar.GetToolState(self.debugBrowseId) and self.running

    #def isInShellNamepace(self):
    #    return self.toolbar.GetToolState(self.shellNamespaceId)

    def isRunning(self):
        return self.running

    def ensureRunning(self, cont_if_running=0, cont_always=0,
                      temp_breakpoint=None):
        """Starts the debugger if it is not currently running.

        If cont_always or if the debugger is already running and
        cont_if_running is set, the debugger is put in set_continue
        mode.
        """
        if self.isRunning():
            if cont_if_running or cont_always:
                self.doDebugStep('set_continue', temp_breakpoint)
        else:
            # Assume temp. breakpoint is already in bplist.
            self.runProcess(cont_always)

    def enableTools(self, stepping, running):
        for wid, enabled in ((self.runId, stepping),
                             (self.runFullSpdId, stepping),
                             (self.stepId, stepping),
                             (self.overId, stepping),
                             (self.outId, stepping),
                             (self.jumpId, stepping),
                             (self.pauseId, not stepping),
                             (self.stopId, running),
                             (self.debugBrowseId, running),
                             (self.shellNamespaceId, running)):
            if wid != -1:
                self.toolbar.EnableTool(wid, enabled)

    def refreshTools(self):
        self.enableTools(self.stepping_enabled, self.running)

    def enableStepping(self):
        self.stepping_enabled = 1
        self.refreshTools()

    def disableStepping(self):
        self.stepping_enabled = 0
        self.refreshTools()

    def doDebugStep(self, method=None, temp_breakpoint=None, args=()):
        if self.stepping_enabled:
            self.disableStepping()
            self.clearStepPos()
            self.invalidatePanes()
            self.updateSelectedPane(do_request=0)
            if not self.isRunning():
                self.runProcess()
            elif method:
                self.proceedAndRequestStatus(method, temp_breakpoint, args)
        else:
            if temp_breakpoint:
                self.setBreakpoint(temp_breakpoint[0], temp_breakpoint[1], 1)

    def OnDebug(self, event):
        if Preferences.minimizeOnDebug:
            self.editor.minimizeBoa()
        self.doDebugStep('set_continue')

    def OnDebugFullSpeed(self, event):
        if Preferences.minimizeOnDebug:
            self.editor.minimizeBoa()
        self.doDebugStep('set_continue', args=(1,))

    def OnStep(self, event):
        self.doDebugStep('set_step')

    def OnOver(self, event):
        self.doDebugStep('set_step_over')

    def OnOut(self, event):
        self.doDebugStep('set_step_out')

    def OnPause(self, event):
        # Only meaningful when running.
        if not self.stepping_enabled:
            self.invokeInDebugger('set_pause')

    def OnStop(self, event):
        if STOP_GENTLY:
            self.clearStepPos()
            self.enableStepping()
            self.invalidatePanes()
            self.updateSelectedPane(do_request=0)
            self.proceedAndRequestStatus('set_quit')
        else:
            self.killDebugger()

    def OnJump(self, event):
        idx = len(self.stackView.stack)-1
        if idx < 0:
            wx.LogError(_('No stack available!'))
            return

        self.stackView.Select(idx)
        self.stackView.OnGotoSource()
        dlg = wx.TextEntryDialog(self, _('Enter line number to jump to:'),
              _('Debugger - Jump'), str(self.stackView.stack[idx]['lineno']))
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return

            lineno = int(dlg.GetValue())
        finally:
            dlg.Destroy()

        #self.doDebugStep('set_step_jump', args=(lineno,))
        self.clearStepPos()
        self.invalidatePanes()
        self.updateSelectedPane(do_request=0)
        if not self.isRunning():
            self.runProcess()
        else:
            self.proceedAndRequestStatus('set_step_jump', None, (lineno,))

    def OnSourceTrace(self, event):
        pass

    def OnDebugBrowse(self, event):
        pass

    def clearViews(self):
        self.clearStepPos()
        self.stackView.load_stack([])
        self.watches.load_dict({})
        self.locs.load_dict({})
        self.globs.load_dict({})
        self.sb.updateState(_('Ready.'), 'info')
        self.refreshTools()

    def OnCloseWindow(self, event):
        self._closing = 1
        if self.debug_client:
            was_alive = self.debug_client.isAlive()
        try:
            self.killDebugger()
        finally:
            # closing must succeed
            if self.editor:
                try:
                    if self.isInShellNamepace():
                        self.editor.shell.debugShell(0, None)
                except:
                    pass
                    #cls, err = sys.exc_info()[:2]
                self.editor.debugger = None
                self.editor = None
            if not was_alive:
                self.destroy()
                self.Destroy()
            # else wait for an OnDebuggerStopped message

    def isInShellNamepace(self):
        if self.shellNamespaceId == -1:
            return False
        else:
            return self.toolbar.GetToolState(self.shellNamespaceId)

    def OnDebugNamespace(self, event):
        self.editor.OnSwitchShell()
        self.editor.shell.debugShell(self.isInShellNamepace(), self)

    def OnToggleSplitOrient(self, event=None):
        if self.splitter.GetSplitMode() == wx.SPLIT_HORIZONTAL:
            self.splitter.SetSplitMode(wx.SPLIT_VERTICAL)
            self.splitter.SplitVertically(self.nbTop, self.nbBottom)
            sashpos = self.splitter.GetClientSize().x / 2
        else:
            self.splitter.SetSplitMode(wx.SPLIT_HORIZONTAL)
            self.splitter.SplitHorizontally(self.nbTop, self.nbBottom)
            sashpos = self.splitter.GetClientSize().y / 2
        self.splitter.SetSashPosition(sashpos)

    def OnPathMappings(self, event=None, paths=None):
        if paths is None:
            paths = self.serverClientPaths[:]

        newPaths = PathMappingDlg.showPathsMappingDlg(self, paths)
        if newPaths is not None:
            self.serverClientPaths = newPaths
            return True
        else:
            return False

    def OnToolOver(self, event):
        pass



def simplifyPathList(data,
                     SequenceTypes=(type(()), type([])),
                     ExcludeTypes=(type(None),) ):
    # Takes a possibly nested structure and turns it into a flat tuple.
    if type(data) in SequenceTypes:
        newdata = []
        for d in data:
            nd = simplifyPathList(d)
            if nd:
                newdata.extend(nd)
        return newdata
    elif type(data) in ExcludeTypes:
        return ()
    else:
        return list(str(data).split(os.pathsep))
