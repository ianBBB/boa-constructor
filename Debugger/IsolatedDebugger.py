#----------------------------------------------------------------------------
# Name:         IsolatedDebugger.py
# Purpose:      A Bdb-based debugger (tracer) that can be operated by
#               another process
#
# Authors:      Shane Hathaway, Riaan Booysen
#
# Created:      November 2000
# RCS-ID:       $Id$
# Copyright:    (c) 2000 - 2007 : Shane Hathaway, Riaan Booysen
# Licence:      GPL
#----------------------------------------------------------------------------

# import sys, thread, threading, Queue
import sys
import _thread
import threading
import queue
import time
from os import chdir
from os import path
import bdb
from bdb import Bdb, BdbQuit, Breakpoint
from reprlib import Repr
# from repr import Repr
# from types import TupleType


# XXX Extend breakpoints to break on exception (like conditional breakpoints)

__traceable__ = 0      # Never trace the tracer.
bdb.__traceable__ = 0


class DebugError(Exception):
    """Incorrect operation of the debugger"""

class BreakpointError(DebugError):
    """Incorrect operation on a breakpoint"""


class DebuggerConnection:
    """A debugging connection that can be operated via RPC.
    """

    def __init__(self, ds):
        """Creates a DebuggerConnection that wraps around a DebugServer."""
        self._ds = ds

    def _callNoWait(self, func_name, do_return, *args, **kw):
        sm = MethodCall(func_name, args, kw, do_return)
        sm.setWait(0)
        self._ds.queueServerMessage(sm)

    def _callMethod(self, func_name, do_return, *args, **kw):
        sm = MethodCall(func_name, args, kw, do_return)

        sm.setupEvent()

        self._ds.queueServerMessage(sm)
        # # DEBUG MESSAGE
        # sys.stdout.write('#_callMethod queueServerMessage ')
        # sys.stdout.flush()
        # Block.
        res = sm.getResult()
        # # DEBUG MESSAGE
        # sys.stdout.write('#_callMethod getResult ')
        # sys.stdout.flush()
        return res

    ### Non-blocking calls.

    def allowEnvChanges(self, allow=1):
        """Allows the debugger to set sys.path, sys.argv, and
        use os.chdir().
        """
        self._ds._allow_env_changes = allow

    def run(self, cmd, globals=None, locals=None):
        """Starts debugging.  Stops the process at the
        first source line.  Non-blocking.
        """
        self._callNoWait('run', 1, cmd, globals, locals)

    def runFile(self, filename, params=(), autocont=0, add_paths=()):
        """Starts debugging.  Stops the process at the
        first source line.  Use the autocont parameter to proceed immediately
        rather than stop.  Non-blocking.
        """
        self._callNoWait('runFile', 1, filename, params, autocont, add_paths)
    
    def post_mortem(self):
        """ Inspecting tracebacks in the debugger 
        """
        self._callMethod('post_mortem', 0)

    def set_continue(self, full_speed=0):
        """Proceeds until a breakpoint or program stop.
        Non-blocking.
        """
        self._callNoWait('set_continue', 1, full_speed)

    def set_step(self):
        """Steps to the next instruction.  Non-blocking.
        """
        self._callNoWait('set_step', 1)

    def set_step_out(self):
        """Proceeds until the process returns from the current
        stack frame.  Non-blocking."""
        self._callNoWait('set_step_out', 1)

    def set_step_over(self):
        """Proceeds to the next source line in the current frame
        or above.  Non-blocking."""
        self._callNoWait('set_step_over', 1)

    def set_step_jump(self, lineno):
        """Updates the lineno of the bottom frame.  Non-blocking."""
        self._callMethod('set_step_jump', 0, lineno)
    
    def set_pause(self):
        """Stops as soon as possible.  Non-blocking and immediate.
        """
        self._ds.stopAnywhere()

    def set_quit(self):
        """Attempts to quits debugging, executing only the try/finally
        handlers.  Non-blocking.
        """
        self._callNoWait('set_quit', 1)

    def set_disconnect(self):
        """Raises a BdbQuit exception in the current thread then
        allows other threads to continue.  Non-blocking.
        """
        self._callNoWait('set_disconnect', 1)

    def setAllBreakpoints(self, brks):
        """brks is a list of mappings containing the keys:
        filename, lineno, temporary, enabled, and cond.
        Non-blocking and immediate."""
        self._ds.setAllBreakpoints(brks)

    def addBreakpoint(self, filename, lineno, temporary=0,
                      cond='', enabled=1, ignore=0):
        """Sets a breakpoint.  Non-blocking and immediate.
        """
        self._ds.addBreakpoint(filename, lineno, temporary,
                               cond, enabled, ignore)

    def enableBreakpoints(self, filename, lineno, enabled=1):
        """Sets the enabled flag for all breakpoints on a given line.
        Non-blocking and immediate.
        """
        self._ds.enableBreakpoints(filename, lineno, enabled)

    def ignoreBreakpoints(self, filename, lineno, ignore=0):
        """Sets the ignore flag for all breakpoints on a given line.
        Non-blocking and immediate.
        """
        self._ds.ignoreBreakpoints(filename, lineno, ignore)

    def conditionalBreakpoints(self, filename, lineno, cond=''):
        """Sets the break condition for all breakpoints on a given line.
        Non-blocking.
        """
        self._ds.conditionalBreakpoints(filename, lineno, cond)

    def clearBreakpoints(self, filename, lineno):
        """Clears all breakpoints on a line.
        Non-blocking and immediate.
        """
        self._ds.clearBreakpoints(filename, lineno)

    def adjustBreakpoints(self, filename, lineno, delta):
        """Moves all applicable breakpoints when delta lines are added or
        deleted.
        Non-blocking and immediate.
        """
        self._ds.adjustBreakpoints(filename, lineno, delta)

    ### Blocking methods.

    def pprintVarValue(self, name, frameno):
        """Pretty-prints the value of name.  Blocking."""
        return self._callMethod('pprintVarValue', 0, name, frameno)

    def getStatusSummary(self):
        """Returns a mapping containing the keys:
          exc_type, exc_value, stack, frame_stack_len, running.
        Also returns and empties the stdout and stderr buffers.
        stack is a list of mappings containing the keys:
          filename, lineno, funcname, modname.
        breaks contains the breakpoint statistics information
          for all current breakpoints.
        The most recent stack entry will be at the last
        of the list.  Blocking.
        """
        return self._callMethod('getStatusSummary', 0)

    def proceedAndRequestStatus(self, command, temp_breakpoint=0, args=()):
        """Executes one non-blocking command then returns
        getStatusSummary().  Blocking."""

        # # TODO DEBUG
        # sys.stdout.write('reached proceedAndRequestStatus')
        # sys.stdout.flush()

        if temp_breakpoint:
            self.addBreakpoint(temp_breakpoint[0], temp_breakpoint[1], 1)
        if command:
            allowed = ('set_continue', 'set_step', 'set_step_over',
                       'set_step_out', 'set_pause', 'set_quit',
                       'set_disconnect', 'set_step_jump')
            if command not in allowed:
                raise DebugError('Illegal command: %s' % command)
            getattr(self, command)(*args)
        ss = self.getStatusSummary()
        return ss

    def runFileAndRequestStatus(self, filename, params=(), autocont=0,
                                add_paths=(), breaks=()):


        # # TODO DEBUG
        # sys.stdout.write('reached runFileAndRequestStatus ')
        # sys.stdout.flush()


        """Calls setAllBreakpoints(), runFile(), and
        getStatusSummary().  Blocking."""
        self.setAllBreakpoints(breaks)

        self._callNoWait('runFile', 1, filename, params, autocont, add_paths)
        return self.getStatusSummary()

    def setupAndRequestStatus(self, autocont=0, breaks=()):
        """Calls setAllBreakpoints() and
        getStatusSummary().  Blocking."""

        self.setAllBreakpoints(breaks)
        if autocont:
            self.set_continue()
        else:
            self._ds.set_step()
        return self.getStatusSummary()

    def getSafeDict(self, locals, frameno):
        """Returns the repr-fied mappings of locals and globals in a
        tuple.  Blocking."""
        return self._callMethod('getSafeDict', 0, locals, frameno)

    def evaluateWatches(self, exprs, frameno):
        """Evalutes the watches listed in exprs and returns the
        results. Input is a tuple of mappings with keys name and
        local; output is a mapping of name -> svalue.  Blocking.
        """
        return self._callMethod('evaluateWatches', 0, exprs, frameno)

    def getWatchSubobjects(self, expr, frameno):
        """Returns a tuple containing the names of subobjects
        available through the given watch expression.  Blocking."""
        return self._callMethod('getWatchSubobjects', 0, expr, frameno)

##    def updateBottomOfStackCodeObject(self, code):
##        """ Experimental
##        """
##        return self._callMethod('updateBottomOfStackCodeObject', 0, code)

class NonBlockingDebuggerConnection (DebuggerConnection):
    """Modifies call semantics in such a way that even blocking
    calls don't block but instead return None.
    Note that for each call, a new NonBlockingDebuggerConnection object
    has to be created.  Use setCallback() to receive notification when
    blocking calls are finished.
    """

    callback = None

    def setCallback(self, callback):
        self.callback = callback

    def _callMethod(self, func_name, do_return, *args, **kw):
        sm = MethodCall(func_name, args, kw, do_return)
        if self.callback:
            sm.setCallback(self.callback)
        self._ds.queueServerMessage(sm)
        return None


# Set exclusive mode to kill all existing debug servers whenever
# a new connection is created.  This helps avoid resource drains.
exclusive_mode = 1


class DebuggerController:
    """Interfaces between DebuggerConnections and DebugServers."""

    def __init__(self):
        self._debug_servers = {}
        self._next_server_id = 0
        self._server_id_lock = threading.Lock()
        self._message_timeout = None

    def _newServerId(self):
        self._server_id_lock.acquire()
        try:
            id = str(self._next_server_id)
            self._next_server_id = self._next_server_id + 1
        finally:
            self._server_id_lock.release()
        return id

    def createServer(self):
        """Returns a string which identifies a new DebugServer.
        """
        global exclusive_mode
        if exclusive_mode:
            # Kill existing servers.
            for id in self._debug_servers.keys():
                self.deleteServer(id)
        ds = DebugServer()
        id = self._newServerId()
        self._debug_servers[id] = ds
        return id

    def deleteServer(self, id):
        """Terminates the connection to the DebugServer."""
        try:
            ds = self._debug_servers[id]
            ds.set_quit()
            self._deleteServer(id)
        except: pass

    def _deleteServer(self, id):
        del self._debug_servers[id]

    def _getDebugServer(self, id):
        return self._debug_servers[id]

    def getMessageTimeout(self):
        return self._message_timeout


class ServerMessage:
    def setupEvent(self):
        self.event = threading.Event()

    def wait(self, timeout=None):
        if hasattr(self, 'event'):
            self.event.wait()

    def doExecute(self): return 0
    def doReturn(self): return 0
    def doExit(self): return 0
    def execute(self, ds): pass

class MethodCall (ServerMessage):
    def __init__(self, func_name, args, kw, do_return):
        self.func_name = func_name
        self.args = args
        self.kw = kw
        self.do_return = do_return
        self.waiting = 1

    def setWait(self, val):
        self.waiting = val

    def doExecute(self):
        return 1

    def execute(self, ob):
        try:
            result = getattr(ob, self.func_name)(*self.args, **self.kw)
            a=result
        except (SystemExit, BdbQuit):
            raise
        except:
            if hasattr(self, 'callback'):    # orig
            # if 'callback' in self:
                self.callback.notifyException()
            else:
                if self.waiting:
                    self.exc = sys.exc_info()
                else:
                    # No one will see this message otherwise.
                    import traceback
                    traceback.print_exc()
        else:
            if hasattr(self, 'callback'):    # orig
            # if 'callback' in self:
                self.callback.notifyReturn(result)
            else:
                self.result = result

        # if 'event' in self:     # orig
        #     self.event.set()

        if hasattr(self, 'event'):
            self.event.set()


    def doReturn(self):
        return self.do_return

    def setCallback(self, callback):
        self.callback = callback

    def getResult(self, timeout=None):
        self.wait()
        # # DEBUG MESSAGE
        # sys.stdout.write('#getResult wait ')
        # sys.stdout.flush()
        if hasattr(self, 'exc'):
            try:
                raise self.exc[0](self.exc[1], self.exc[2])
            finally:
                # Circ ref
                del self.exc

        # if 'result' not in self:            #orig
        #     raise DebugError('Timed out while waiting for debug server.')
        # return self.result

        if not hasattr(self, 'result'):
            raise DebugError('Timed out while waiting for debug server.')
        return self.result

class ThreadChoiceLock:
    """A reentrant lock designed for simply choosing a thread.
    It is always released when you call release()."""

    def __init__(self):
        self._owner = None
        self._block = _thread.allocate_lock()

    def acquire(self, blocking=1):
        me = _thread.get_ident()
        if self._owner == me:
            return 1
        rc = self._block.acquire(blocking=True)
        if rc:
            self._owner = me
        return rc

    def release(self):
        me = _thread.get_ident()
        assert me == self._owner, "release of unacquired lock"
        self._owner = None
        self._block.release()

    def releaseIfOwned(self):
        me = _thread.get_ident()
        if me == self._owner:
            self.release()


_orig_syspath = sys.path

class DebugServer (Bdb):

    # frame is set only while paused.
    frame = None

    # exc_info is set only while paused and an exception occurred.
    exc_info = None

    # starting_trace is set to make sure sys.set_trace() gets called before
    # resuming user code.
    starting_trace = 0

    # ignore_stopline is the line number we should *not* stop on.
    ignore_stopline = -1

    # autocont is set by runFile() if the debugger should enter set_continue
    # mode right after starting.
    autocont = 0

    # _allow_env_changes governs whether sys.path, etc. can be modified.
    _allow_env_changes = 0

    # quitting is set to true when the user clicks the stop button.
    quitting = 0

    # stopframe can hold several values:
    #   None: Stop anywhere
    #   frame object: Stop in that frame
    #   (): Stop nowhere

    def __init__(self):
        Bdb.__init__(self)
        self.fncache = {}
        self.botframe = None

        self.__queue = queue.Queue(0)

        # self._lock governs which thread the debugger will stop in.
        self._lock = ThreadChoiceLock()

        self.repr = repr = Repr()
        repr.maxstring = 100
        repr.maxother = 100
        self.maxdict2 = 1000

        self._running = 0
        self.cleanupServer()
        self.stopframe = ()  # Don't stop unless requested to do so.

    def queueServerMessage(self, sm):
        self.__queue.put(sm)

    def cleanupServer(self):
        self.reset()
        self.frame = None
        self.ignore_stopline = -1
        self.autocont = 0
        self.exc_info = None
        self.starting_trace = 0
        self.fncache.clear()
        self._lock.releaseIfOwned()

    def servicerThread(self):
        """Bootstraps the debugger server loop."""
        while 1:
            try:
                self.eventLoop()
            except:
                # ??
                import traceback
                traceback.print_exc()
            self.quitting = 0

    def eventLoop(self):
        while not self.quitting:
            if not self.executeOneEvent():
                break  # event requested a return

    def executeOneEvent(self):
        # The heart of this whole mess.  Fetches a message and executes
        # it in the current frame.
        # Should not catch exceptions.
        sm = self.__queue.get()
        if sm.doExecute():
            sm.execute(self)
        if sm.doExit():
            _thread.exit()
        if sm.doReturn():
            # Return to user code
            self.beforeResume()
            if self.starting_trace:
                self.starting_trace = 0
                sys.settrace(self.trace_dispatch)
            return 0
        return 1

    def beforeResume(self):
        """Frees references before jumping back into user code."""
        self.frame = None
        self.exc_info = None

    # Bdb overrides.
    def canonic(self, filename):
        canonic = self.fncache.get(filename, None)
        if not canonic:
            if ((filename[:1] == '<' and filename[-1:] == '>') or
                filename.find('://') >= 0):
                # Don't change URLs or special filenames
                canonic = filename
            elif filename.startswith('Python expression'):
                canonic = '<Python expression: %s>'%filename[:17]
            else:
                canonic = path.abspath(filename)

            self.fncache[filename] = canonic
        return canonic

    def getFilenameAndLine(self, frame):
        """Returns the filename and line number for the frame.
        """

        # filename = self.canonic(frame.f_code.co_filename)   # orig


        if 'fn' in frame.f_globals.keys():
            filename = self.canonic(frame.f_globals['fn'])
        else:
            filename = self.canonic(frame.f_code.co_filename)   # orig

        # DEBUG CODE
        # with open(r"C:\Users\Ian-17\Dropbox\Ians\technical\Boa Constructor\Testarea\general\temp\frame.txt", "w") as file:
        #     # Write a string to the file
        #     file.write(filename)

        return filename, frame.f_lineno

    def getFrameNames(self, frame):
        """Returns the module and function name for the frame.
        """
        try:
            modname = frame.f_globals['__name__']
        except KeyError:
            modname = ''
        if modname is None:
            modname = ''
        funcname = frame.f_code.co_name
        return modname, funcname

    def isTraceable(self, frame):
        return frame.f_globals.get('__traceable__', 1)

    def break_here(self, frame):
        filename, lineno = self.getFilenameAndLine(frame)
        if not (filename in self.breaks):
            return 0

        if not lineno in self.breaks[filename]:
            return 0
        # flag says ok to delete temp. bp
        (bp, flag) = bdb.effective(filename, lineno, frame)
        if bp:
            self.currentbp = bp.number
            if (flag and bp.temporary):
                self.do_clear(str(bp.number))
            self.afterBreakpoint(frame)
            return 1
        else:
            return 0

    def break_anywhere(self, frame):
        filename, lineno = self.getFilenameAndLine(frame)
        # return self.breaks.has_key(filename)     #orig
        return (filename in self.breaks)

    def stop_here(self, frame):
        # Redefine stopping.
        if frame is self.botframe:
            # Don't stop in the bottom frame.
            return 0
        sf = self.stopframe
        if (sf is None):
            # Stop anywhere.
            return self.isTraceable(frame)
        # elif sf is ():
        elif (type(sf) is tuple) and (len(sf) == 0):
            # Stop nowhere.
            return 0
        # else stop in a specific frame.
        if (frame is sf and frame.f_lineno != self.ignore_stopline):
            # Stop in the current frame unless we're on
            # ignore_stopline.
            return self.isTraceable(frame)
        # Stop at any frame that called stopframe.
        f = sf
        while f:
            if frame is f:
                return self.isTraceable(frame)
            f = f.f_back
        return 0

    def add_trace_hooks(self, frame):
        root_frame = None
        f = frame
        td = self.trace_dispatch
        while f:
            f.f_trace = td
            root_frame = f
            f = f.f_back
            if f is self.botframe:
                break
        if self.botframe is None:
            # Make the entire stack visible.
            self.botframe = root_frame

    def remove_trace_hooks(self):
        sys.settrace(None)
        try:
            raise Exception('gen_exc_info')
        except:
            frame = sys.exc_info()[2].tb_frame
            while frame:
                # Clear all the f_trace attributes
                # that were created while processing with a
                # settrace callback enabled.
                del frame.f_trace
                if frame is self.botframe:
                    break
                frame = frame.f_back

    def set_continue(self, full_speed=0):
        """Only stop at breakpoints, exceptions or when finished.
        """
        self.stopframe = ()
        self.returnframe = None
        self.quitting = 0

        if full_speed:
            # run without debugger overhead
            self.starting_trace = 0
            self.remove_trace_hooks()
        else:
            self.starting_trace = 1

        # Allow a stop in any thread.
        self._lock.releaseIfOwned()

    def set_disconnect(self):
        """Debugging client disconnected.  Raise a quit exception in just
        this thread, but allow other threads to continue.
        """
        self.set_continue(1)
        raise BdbQuit('Client disconnected')

    def set_traceable(self, enable=1):
        """Allows user code to enable/disable tracing without changing the
        stepping mode.
        """
        sys.settrace(None)
        self._running = 1
        if enable:
            # Add trace hooks.
            try:
                raise Exception('gen_exc_info')
            except:
                frame = sys.exc_info()[2].tb_frame.f_back
            self.add_trace_hooks(frame)
            sys.settrace(self.trace_dispatch)
        else:
            # Remove trace hooks and allow other threads to capture the lock.
            self.remove_trace_hooks()
            self._lock.releaseIfOwned()

    def hard_break_here(self, frame):
        """Indicates whether the debugger should stop at a hard breakpoint.

        Returns a (filename, lineno) tuple if the debugger should also
        set a soft breakpoint.
        """
        filename, lineno = self.getFilenameAndLine(frame)
        brks = self.breaks.get(filename, None)
        if brks is None or lineno not in brks:
            # No soft breakpoint has been set, so plan to add the soft
            # breakpoint and stop.
            return (filename, lineno)
        # Let the soft breakpoint control whether the hard breakpoint
        # takes effect.
        return self.break_here(frame)

    def set_trace(self):
        """Start debugging from the caller's frame.

        Called by hard breakpoints.
        """
        try:
            raise Exception('gen_exc_info')
        except:
            frame = sys.exc_info()[2].tb_frame.f_back
        stop = self.hard_break_here(frame)
        if not stop:
            # The user has disabled this breakpoint.
            return
        if not self._lock.acquire(0):
            # The debugger is busy in another thread.
            return

        if isinstance(stop, tuple):
            # Add a soft breakpoint here so the user can manage the breakpoint.
            filename, lineno = stop
            self.set_break(filename, lineno)
        self._running = 1
        self.add_trace_hooks(frame)
        # Get sys.settrace() called when resuming.
        self.starting_trace = 1
        self.afterBreakpoint(frame)
        # Pause in the frame
        self.user_line(frame)

    def afterBreakpoint(self, frame):
        # Set a default stepping mode.
        self.set_step()

    def set_internal_breakpoint(self, filename, lineno, temporary=0,
                                cond=None):
        # if not self.breaks.has_key(filename):    #orig
        if filename not in self.breaks:
            self.breaks[filename] = []
        list = self.breaks[filename]
        if not lineno in list:
            list.append(lineno)

    def set_break(self, filename, lineno, temporary=0, cond=None):
        filename = self.canonic(filename)
        self.set_internal_breakpoint(filename, lineno, temporary, cond)
        # Note that we can't reliably verify a filename anymore.
        return bdb.Breakpoint(filename, lineno, temporary, cond)

    def do_clear(self, bpno):
        self.clear_bpbynumber(bpno)

    def clearTemporaryBreakpoints(self, filename, lineno):
        filename = self.canonic(filename)
        # if not self.breaks.has_key(filename):
        if filename not in self.breaks:
            return
        if lineno not in self.breaks[filename]:
            return
        # If all bp's are removed for that file,line
        # pair, then remove the breaks entry
        for bp in Breakpoint.bplist[filename, lineno][:]:
            if bp.temporary:
                bp.deleteMe()
        # if not Breakpoint.bplist.has_key((filename, lineno)):
        if not ((filename, lineno) in Breakpoint.bplist):
            self.breaks[filename].remove(lineno)
        if not self.breaks[filename]:
            del self.breaks[filename]

    # Bdb callbacks.

    def user_line(self, frame):
        # This method is called when we stop or break at a line
        if not self._lock.acquire(0):
            # Already working in another thread.
            return
        if self.autocont:
            self.autocont = 0
            self.set_continue()
            return
        self.stopframe = ()  # Don't stop.
        self.ignore_stopline = -1
        self.frame = frame
        self.exc_info = None
        filename, lineno = self.getFilenameAndLine(frame)
        self.clearTemporaryBreakpoints(filename, lineno)
        self.eventLoop()

    def user_return(self, frame, return_value):
        # This method is called when stepping in or next,
        # but not when stepping out.
        frame.f_locals['__return__'] = return_value
        self.user_line(frame)

    def user_exception(self, frame, exc_info):
        # This method should be used to automatically stop
        # when specific exception types occur.
        #self.ignore_stopline = -1
        #self.frame = frame
        #self.exc_info = exc_info
        #self.eventLoop()
        pass

    ### Utility methods.
    def stopAnywhere(self):
        self.stopframe = None
        self.returnframe = None

    def runFile(self, filename, params, autocont, add_paths):
        d = {'__name__': '__main__',
             '__doc__': 'Debugging',
             '__builtins__': __builtins__,}

        fn = self.canonic(filename)
        if self._allow_env_changes:
            bn = path.basename(fn)
            dn = path.dirname(fn)
            sys.argv = [bn] + list(params)
            if not add_paths:
                add_paths = []
            sys.path = [dn] + list(add_paths) + list(_orig_syspath)
            chdir(dn)

        self.autocont = autocont

        file_code=open(fn).read()
        cmd_str='exec(' + repr(file_code) +')'
        self.run(cmd_str, {
            'fn': fn, 'd': d, '__debugger__': self})

    def run(self, cmd, globals=None, locals=None):
        try:
            self._running = 1
            try:
                Bdb.run(self, cmd, globals, locals)
            except (BdbQuit, SystemExit):
                pass
            except:
                import traceback
                traceback.print_exc()
                if self._lock.acquire(0):
                    # Provide post-mortem analysis.
                    self.exc_info = sys.exc_info()
                    self.frame = self.exc_info[2].tb_frame
                    self.quitting = 0
                    self.eventLoop()
        finally:
            sys.settrace(None)  # Just to be sure
            self.quitting = 1
            self._running = 0
            self.cleanupServer()

    def isRunning(self):
        return self._running
    
    def post_mortem(self, exc_info=None):
        if exc_info is None:
            self.exc_info = sys.exc_info()
        else:
            self.exc_info = exc_info
            
        if self.exc_info[2] is not None:
            self.frame = self.exc_info[2].tb_frame
        else:
            self.frame = None    

        self._running = 1
        self.quitting = 0
        self.eventLoop()

    def set_step_out(self):
        """Stop when returning from the topmost frame."""
        frame = self.getFrameByNumber(-1)
        if frame is not None:
            self.stopframe = frame.f_back
            self.returnframe = None
            self.quitting = 0
        else:
            raise DebugError('No current frame')

    def set_step_over(self):
        """Stop on the next line in the topmost frame or in one of its callers.
        """
        frame = self.getFrameByNumber(-1)
        if frame is not None:
            # ignore_stopline is brittle for scripts.
            #self.ignore_stopline = frame.f_lineno
            self.set_next(frame)
        else:
            raise DebugError('No current frame')
        
    def set_step_jump(self, lineno):
        """ Adjust the linenumber attribute of the bottom frame """
        frame = self.getFrameByNumber(-1)
        if frame is not None:
            frame.f_lineno = lineno
        else:
            raise DebugError('No current frame')
    

    ### Breakpoint control.
    def setAllBreakpoints(self, brks):
        """brks is a list of mappings containing the keys:
        filename, lineno, temporary, enabled, and cond.
        Non-blocking."""
        self.clear_all_breaks()
        if brks:
            for brk in brks:
                self.addBreakpoint(**brk)

    def addBreakpoint(self, filename, lineno, temporary=0,
                      cond='', enabled=1, ignore=0):
        """Sets a breakpoint.  Non-blocking.
        """
        bp = self.set_break(filename, lineno, temporary, cond)
        if type(bp) == type(''):
            # Note that checking for string type is strange. Argh.
            raise BreakpointError(bp)
        elif bp is not None and not enabled:
            bp.disable()
        bp.ignore = ignore

    def enableBreakpoints(self, filename, lineno, enabled=1):
        """Sets the enabled flag for all breakpoints on a given line.
        Non-blocking.
        """
        bps = self.get_breaks(filename, lineno)
        if bps:
            for bp in bps:
                if enabled: bp.enable()
                else: bp.disable()

    def ignoreBreakpoints(self, filename, lineno, ignore=0):
        """Sets the ignore count for all breakpoints on a given line.
        Non-blocking.
        """
        bps = self.get_breaks(filename, lineno)
        if bps:
            for bp in bps:
                bp.ignore = ignore

    def conditionalBreakpoints(self, filename, lineno, cond=''):
        """Sets the break condition for all breakpoints on a given line.
        Non-blocking.
        """
        bps = self.get_breaks(filename, lineno)
        if bps:
            for bp in bps:
                bp.cond = cond

    def clearBreakpoints(self, filename, lineno):
        """Clears all breakpoints on a line.
        Non-blocking.
        """
        msg = self.clear_break(filename, lineno)
        if msg is not None:
            raise BreakpointError(msg)

    def adjustBreakpoints(self, filename, lineno, delta):
        """Moves all applicable breakpoints when delta lines are added or
        deleted.
        Non-blocking.
        """
        # This can be more efficient, but for now sticking to the bdb interface
        # Unfortunately this must be done on a low level
        filename = self.canonic(filename)
        breaklines = self.get_file_breaks(filename)
        bplist = bdb.Breakpoint.bplist
        set_breaks = []
        # store reference and remove from (fn, ln) refed dict.
        for line in breaklines[:]:
            if line > lineno:
                set_breaks.append(self.get_breaks(filename, line))
                breaklines.remove(line)
                del bplist[filename, line]
        # put old break at new place and renumber
        for brks in set_breaks:
            for brk in brks:
                brk.line = brk.line + delta
                breaklines.append(brk.line)
                # merge in moved breaks
                # if bplist.has_key((filename, brk.line)):     #orig
                if (filename, brk.line) in bplist:
                    bplist[filename, brk.line].append(brk)
                else:
                    bplist[filename, brk.line] = [brk]
        # reorder lines
        breaklines.sort()

    def getStackInfo(self):
        try:
            if self.exc_info is not None:
                exc_type, exc_value, exc_tb = self.exc_info
                try:
                    exc_type = exc_type.__name__
                except AttributeError:
                    # Python 2.x -> ustr()?
                    exc_type = "%s" % str(exc_type)
                if exc_value is not None:
                    exc_value = str(exc_value)

                stack, frame_stack_len = self.get_stack(
                    exc_tb.tb_frame, exc_tb)
            else:
                exc_type = None
                exc_value = None
                stack, frame_stack_len = self.get_stack(
                    self.frame, None)
            # Remove debugger's own stack.
            for index in range(len(stack)):
                g = stack[index][0].f_globals
                if g.get('__debugger__', None) is self:
                    stack = stack[index + 1:]
                    frame_stack_len = frame_stack_len - (index + 1)
                    break
            return exc_type, exc_value, stack, frame_stack_len
        finally:
            exc_tb = None
            stack = None

    def getFrameByNumber(self, frameno):
        """Gets the specified frame number from the stack.

        Returns None if the stack is not available.
        """
        try:
            stack = self.getStackInfo()[2]
            if stack:
                if frameno >= len(stack):
                    # Should we be doing this?
                    frameno = len(stack) - 1
                return stack[frameno][0]
            else:
                return None
        finally:
            stack = None

    def getFrameNamespaces(self, frame):
        """Returns the locals and globals for a frame.

        Can be overridden for high-level scripts.
        """
        return frame.f_globals, frame.f_locals

    def getExtendedFrameInfo(self):
        try:
            (exc_type, exc_value, stack,
             frame_stack_len) = self.getStackInfo()
            stack_summary = []
            for frame, lineno in stack:
                filename, lineno = self.getFilenameAndLine(frame)
                modname, funcname = self.getFrameNames(frame)
                stack_summary.append(
                    {'filename':filename, 'lineno':lineno,
                     'funcname':funcname, 'modname':modname})

            result = {'stack':stack_summary,
                      'frame_stack_len':frame_stack_len,
                      'running':self._running and 1 or 0}
            if exc_type:
                result['exc_type'] = exc_type
            if exc_value:
                result['exc_value'] = exc_value
            return result
        finally:
            frame = None
            stack = None

    def getBreakpointStats(self):
        rval = []
        for bps in bdb.Breakpoint.bplist.values():
            for bp in bps:
                filename = bp.file  # Already canonic
                rval.append({'filename':filename,
                             'lineno':bp.line,
                             'cond':bp.cond or '',
                             'temporary':bp.temporary and 1 or 0,
                             'enabled':bp.enabled and 1 or 0,
                             'hits':bp.hits or 0,
                             'ignore':bp.ignore or 0,
                             })
        return rval

    def getStatusSummary(self):
        rval = self.getExtendedFrameInfo()
        rval['breaks'] = self.getBreakpointStats()
        return rval

    def getSafeDict(self, locals, frameno):
        if locals:
            rname = 'locals'
        else:
            rname = 'globals'
        frame = self.getFrameByNumber(frameno)
        if frame is None:
            return {'frameno':frameno, rname:{}}
        globalsDict, localsDict = self.getFrameNamespaces(frame)
        if locals:
            d = self.safeReprDict(localsDict)
        else:
            d = self.safeReprDict(globalsDict)
        return {'frameno':frameno, rname:d}

    def evaluateWatches(self, exprs, frameno):
        frame = self.getFrameByNumber(frameno)
        if frame is None:
            return {'frameno':frameno, 'watches':{}}
        globalsDict, localsDict = self.getFrameNamespaces(frame)
        rval = {}
        for info in exprs:
            name = info['name']
            local = info['local']
            if local:
                primaryDict = localsDict
            else:
                primaryDict = globalsDict
            if name in primaryDict:
                value = primaryDict[name]
            else:
                try:
                    value = eval(name, globalsDict, localsDict)
                # except Exception, message:
                #     value = '??? (%s)' % message
                except Exception as message:
                        value = '??? (%s)' %message

            svalue = self.safeRepr(value)
            rval[name] = svalue
        return {'frameno':frameno, 'watches':rval}

    def getWatchSubobjects(self, expr, frameno):
        """Returns a tuple containing the names of subobjects
        available through the given watch expression."""
        frame = self.getFrameByNumber(frameno)
        if frame is None:
            return []
        globalsDict, localsDict = self.getFrameNamespaces(frame)
        try: inst_items = dir(eval(expr, globalsDict, localsDict))
        except: inst_items = []
        try: clss_items = dir(eval(expr, globalsDict, localsDict)
                              .__class__)
        except: clss_items = []
        return inst_items + clss_items

    def pythonShell(self, code, globalsDict, localsDict, name='<debug>'):
        from io import StringIO

        _ts, sys.stdout = sys.stdout, StringIO('')
        try:
            co = compile(code, name, 'single')
            # exec co in globalsDict, localsDict
            exec(co, globalsDict, localsDict)

            return sys.stdout.getvalue()
# lame attempt at handling None values
##            res = sys.stdout.getvalue()
##            if not res:
##                try:
##                    if eval(co, globalsDict, localsDict) is None:
##                        return 'None'
##                except:
##                    pass
##            return res
                    
        finally:
            sys.stdout = _ts

    def pprintVarValue(self, expr, frameno):
        frame = self.getFrameByNumber(frameno)
        if frame is None:
            return 'error: no current frame'
        else:
            try:
                globalsDict, localsDict = self.getFrameNamespaces(frame)
                return self.pythonShell(expr, globalsDict, localsDict)
            except:
                t, v = sys.exc_info()[:2]
                import traceback
                return ''.join(traceback.format_exception_only(t, v))

    def safeRepr(self, s):
        return self.repr.repr(s)

    def safeReprDict(self, dict):
        rval = {}
        l = dict.items()
        if len(l) >= self.maxdict2:
            l = l[:self.maxdict2]
        for key, value in l:
            rval[str(key)] = self.safeRepr(value)
        return rval

##    def updateBottomOfStackCodeObject(self, code):
##        frame = self.getFrameByNumber(-1)
##        if frame is not None:
##            frame.f_lineno = lineno
##            self.quitting = 0
##        else:
##            raise DebugError('No current frame')
        