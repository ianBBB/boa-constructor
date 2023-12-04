import os, sys, time, socket
import xmlrpc.client

import wx

import Preferences, Utils
from Utils import _
import trace
try:
    from ExternalLib import xmlrpclib
except ImportError:
    import xmlrpclib

from Debugger.DebugClient import DebugClient, MultiThreadedDebugClient, \
     EmptyResponseError, DebuggerTask, EVT_DEBUGGER_START, \
     wxEVT_DEBUGGER_START, wxEVT_DEBUGGER_EXC, wxEVT_DEBUGGER_STOPPED


KEEP_STREAMS_OPEN = 1
USE_TCPWATCH = 0
LOG_TRACEBACKS = 0


class TransportWithAuth (xmlrpclib.Transport):
    """Adds a proprietary but simple authentication header to the
    RPC mechanism.  NOTE: this requires xmlrpclib version 1.0.0."""

    def __init__(self, auth):
        self._auth = auth

    def send_user_agent(self, connection):
        xmlrpclib.Transport.send_user_agent(self, connection)
        connection.putheader("X-Auth", self._auth)

    def parse_response(self, f, sock=None):
        # read response from input file, and parse it
        # If there was no response, raise a special exception.
        got_data = 0

        p, u = self.getparser()

        while 1:
            if sock:
                response = sock.recv(1024)
            else:
                response = f.read(1024)
            if not response:
                break
            else:
                got_data = 1
            if self.verbose:
                print("body:", repr(response))
            p.feed(response)

        f.close()
        if not got_data:
            #raise EmptyResponseError, _('Empty response from debugger process')
            raise Exception ('Empty response from debugger process', EmptyResponseError)

        p.close()
        return u.close()

class UnknownError(Exception):
    pass

def spawnChild(monitor, process, args=''):
    """Returns an xmlrpclib.Server, a connection to an xml-rpc server,
    and the input and error streams.
    """
    # Start ChildProcessServerStart.py in a new process.
    if hasattr(sys, 'frozen'):
        script_fn = os.path.join(os.path.dirname(sys.executable), 'Debugger', 
              'ChildProcessServerStart.py')
    else:
        script_fn = os.path.join(os.path.dirname(__file__),
                             'ChildProcessServerStart.py')
    pyIntpPath = Preferences.getPythonInterpreterPath()
    cmd = '%s "%s" %s' % (pyIntpPath, script_fn, args)
    try:
        # pid = wx.Execute(cmd, wx.EXEC_NOHIDE, process)
        # pid = wx.Execute(cmd, wx.EXEC_SHOW_CONSOLE | wx.EXEC_ASYNC, process)


        pid = wx.Execute(cmd, wx.EXEC_SHOW_CONSOLE, process)

        # ## ZZZDEBUG This is a text entry point to add change the port, pid and auth. To be removed
        # alt_pid=0
        # alt_auth=''
        # alt_port=0
        # dlg = wx.TextEntryDialog(None, 'The debug thread re-direct', 'Change all three?', "no")
        # try:
        #     if dlg.ShowModal() == wx.ID_OK:
        #         result = dlg.GetValue()
        #         # Your code
        #         if not (result=="no"):
        #             alt_port, alt_auth, alt_pid = result.split(' ')
        #         # port = int(result)
        # finally:
        #     dlg.Destroy()
        #
        # if alt_pid:
        #     pid= int(alt_pid)

        line = ''
        if monitor.isAlive():
            istream = process.GetInputStream()
            estream = process.GetErrorStream()
            ostream = process.GetOutputStream()

            err = ''
            # read in the port and auth hash
            while monitor.isAlive() and line.find('\n') < 0:
                # don't take more time than the process we wait for ;)
                time.sleep(0.00001)
                if istream.CanRead():
                    # line = line + istream.read(1)

                    read_data = istream.read(1)
                    line = line + read_data.decode('utf-8')
                    # test for tracebacks on stderr
                if estream.CanRead():
                    b_err = estream.read()
                    err = b_err.decode('utf-8')
                    if LOG_TRACEBACKS:
                        if hasattr(sys, 'frozen'):
                            fn = os.path.join(os.path.dirname(sys.executable), 'DebugTracebacks.txt')
                        else:
                            fn = os.path.join(os.path.dirname(__file__), 'DebugTracebacks.txt')
                        open(fn, 'a').write(err)
                    errlines = err.split('\n')
                    while not errlines[-1].strip(): del errlines[-1]
                    try:
                        exctype, excvalue = errlines[-1].split(':')
                    except ValueError:
                        # XXX non standard output on stderr
                        # XXX possibly warnings
                        # XXX for now ignore it (it's non fatal)
                        
                        #raise UnknownError, errlines[-1]
                        continue
                        
                    while errlines and errlines[-1][:7] != '  File ':
                        del errlines[-1]
                    if errlines:
                        errfile = ' (%s)' % errlines[-1].strip()
                    else:
                        errfile = ''
                    try:
                        Error, val = __builtins__[exctype.strip()], (excvalue.strip()+errfile)
                    except KeyError:
                        Error, val = UnknownError, (exctype.strip()+':'+excvalue.strip()+errfile)
                    raise Exception( val, Error)

        if not KEEP_STREAMS_OPEN:
            process.CloseOutput()

        if monitor.isAlive():
            line = line.strip()
            if not line:
                raise Exception('The debug server address could not be read', RuntimeError)

            ## ZZZDEBUG
            # if alt_port:
            #     port =int(alt_port)
            #     auth = alt_auth
            # else:
            #     port, auth = line.strip().split()
            #     port = int(port.strip("0"))

            port, auth = line.strip().split()
            port = int(port.strip("0"))


            # ## ZZZDEBUG This is a text entry point to add change the port, if required. To be removed
            # dlg = wx.TextEntryDialog(None, 'The current port is : ' + repr(port), 'Change ports?', repr(port))
            # try:
            #     if dlg.ShowModal() == wx.ID_OK:
            #         result = dlg.GetValue()
            #         # Your code
            #         port = int(result)
            # finally:
            #     dlg.Destroy()

            if USE_TCPWATCH:
                # Start TCPWatch as a connection forwarder.
                #from thread import start_new_thread
                from threading import Thread
                new_port = 20202  # Hopefully free
                def run_tcpwatch(port1, port2):
                    os.system("tcpwatch -L %d:127.0.0.1:%d" % (
                        int(port1), int(port2)))
                Thread.start(run_tcpwatch, (new_port, port))
                time.sleep(3)
                port = new_port

            # trans = TransportWithAuth(auth)   # orig
            # server = xmlrpclib.Server(
            #     'http://127.0.0.1:%d' % port, trans)

            server = xmlrpc.client.ServerProxy('http://127.0.0.1:%d' % port)

            return server, istream, estream, pid, pyIntpPath
        else:
            raise Exception('The debug server failed to start', RuntimeError)
    except:
        if monitor.isAlive():
            process.CloseOutput()
        monitor.kill()
        raise


###################################################################


class ChildProcessClient(MultiThreadedDebugClient):

    server = None       # An xmlrpclib.Server instance
    processId = 0
    process = None      # A wx.Process
    input_stream = None
    error_stream = None
    pyIntpPath = None
    
    def __init__(self, win, process_args=''):
        self.process_args = process_args
        DebugClient.__init__(self, win)
        win.Bind(EVT_DEBUGGER_START, self.OnDebuggerStart, id=self.win_id)

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        task = DebuggerTask(self, m_name, m_args, r_name, r_args)
        if self.server is None:
            # Start the process, making sure the spawn occurs
            # in the main thread *only*.
            evt = self.createEvent(wxEVT_DEBUGGER_START)
            evt.SetTask(task)
            self.postEvent(evt)
        else:
            self.taskHandler.addTask(task)

    def invoke(self, m_name, m_args):
        # m = getattr(self.server, m_name)    # orig
        # result = m(*m_args)    # orig
        # return result    # orig

        # m = getattr(self.server, 'system.listMethods')
        # result = m()
        # print(repr(result))

        m = getattr(self.server, m_name)
        result = m(*m_args)
        # ## ZZZDEBUG
        # print(repr(result))
        return result





    def isAlive(self):
        return (self.process is not None)

    def kill(self):
        server = self.server
        if server is not None:
            def call_exit(server=server):
                try:
                    server.exit_debugger()
                except (EmptyResponseError, socket.error):
                    # Already stopped.
                    pass
            self.taskHandler.addTask(call_exit)
            self.server = None
        self.input_stream = None
        self.error_stream = None
        process = self.process
        self.process = None
        if process is not None:
            # process.Detach()
            if KEEP_STREAMS_OPEN:
                process.CloseOutput()

##    def __del__(self):
##        pass#self.kill()
#TODO stream read in bytes. these need to be converted to strings for the stdXX_text vars
    def pollStreams(self):
        stderr_text = ''
        stream = self.error_stream
        if stream is not None and stream.CanRead():
            stderr_text = stream.read()
        stdin_text = ''
        stream = self.input_stream
        if stream is not None and stream.CanRead():
            stdin_text = stream.read()
        # print(stdin_text, stderr_text)
        return (stdin_text, stderr_text)

    def getProcessId(self):
        """Returns the process ID if this client is connected to another
        process."""
        return self.processId

    def OnDebuggerStart(self, evt):
        try:
            wx.BeginBusyCursor()
            try:
                if self.server is None:
                    # Start the subprocess.
                    process = wx.Process(self.event_handler, self.win_id)
                    process.Redirect()
                    self.process = process

                    # wx.EVT_END_PROCESS(self.event_handler, self.win_id,
                    #                    self.OnProcessEnded)  # original

                    self.event_handler.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)

                    (self.server, self.input_stream, self.error_stream,
                     self.processId, self.pyIntpPath) = spawnChild(
                        self, process, self.process_args)


                    # ## ZZZDEBUG This is a text entry point to add change the pid, if required. To be removed
                    # dlg = wx.TextEntryDialog(None, 'The current pid is : ' + repr(self.processId), 'Change PID?', repr(self.processId))
                    # try:
                    #     if dlg.ShowModal() == wx.ID_OK:
                    #         self.processId = int(dlg.GetValue())
                    #         # Your code
                    # finally:
                    #     dlg.Destroy()

                self.taskHandler.addTask(evt.GetTask())
            except:
                t, v, tb = sys.exc_info()
                evt = self.createEvent(wxEVT_DEBUGGER_EXC)
                evt.SetExc(t, v)
                self.postEvent(evt)
                if LOG_TRACEBACKS:
                    import traceback
                    fn = os.path.join(os.path.dirname(__file__), 'DebugTracebacks.txt')
                    open(fn, 'a').write(''.join(traceback.format_exception(t, v, tb)))
                del tb
        finally:
            wx.EndBusyCursor()

    def OnProcessEnded(self, evt):
        self.pollStreams()
        self.server = None
        self.kill()
        evt = self.createEvent(wxEVT_DEBUGGER_STOPPED)
        self.postEvent(evt)


if __name__ == '__main__':
    a = wx.App()
    f = wx.Frame(None, -1, '')
    f.Show()
    cpc = ChildProcessClient(f)
    cpc.OnDebuggerStart(None)
    a.MainLoop()
