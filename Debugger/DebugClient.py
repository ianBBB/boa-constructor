import sys

from Debugger.Tasks import ThreadedTaskHandler

import wx

'''wxPython debugging client code.  This runs in the IDE.
A debug client connects to a debug server, generally in a different
process.  The debug server does the dirty work of stepping and
stopping at breakpoints.
'''

wxEVT_DEBUGGER_OK = wx.NewIdRef(count=1)
wxEVT_DEBUGGER_EXC = wx.NewIdRef(count=1)
wxEVT_DEBUGGER_START = wx.NewIdRef(count=1)
wxEVT_DEBUGGER_STOPPED = wx.NewIdRef(count=1)

EVT_DEBUGGER_OK = wx.PyEventBinder(wxEVT_DEBUGGER_OK)
EVT_DEBUGGER_EXC = wx.PyEventBinder(wxEVT_DEBUGGER_EXC)
EVT_DEBUGGER_START = wx.PyEventBinder(wxEVT_DEBUGGER_START)
EVT_DEBUGGER_STOPPED = wx.PyEventBinder(wxEVT_DEBUGGER_STOPPED)


class EmptyResponseError (Exception):
    """Empty debugger response"""


class DebuggerCommEvent(wx.PyCommandEvent):
    receiver_name = None
    receiver_args = ()
    result = None
    task = None
    t = None
    v = None
    tb = ('', 0)


    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)

    def SetResult(self, result):
        # self.result = result # orig
        DebuggerCommEvent.result = result

    def GetResult(self):
        # return self.result # orig
        return DebuggerCommEvent.result

    def SetTask(self, task):
        DebuggerCommEvent.task = task

    def GetTask(self):
        # return self.task
        return DebuggerCommEvent.task # orig

    def SetReceiverName(self, name):
        # self.receiver_name = name
        DebuggerCommEvent.receiver_name = name

    def GetReceiverName(self):
        # return self.receiver_name
        return DebuggerCommEvent.receiver_name

    def SetReceiverArgs(self, args):
        # self.receiver_args = args
        DebuggerCommEvent.receiver_args = args

    def GetReceiverArgs(self):
        # return self.receiver_args
        return DebuggerCommEvent.receiver_args

    def SetExc(self, t, v):
        # self.t, self.v = t, v
        DebuggerCommEvent.t, DebuggerCommEvent.v = t, v

    def GetExc(self):
        # return self.t, self.v
        return DebuggerCommEvent.t, DebuggerCommEvent.v


class DebugClient:
    """The base class expected to be used by all DebugClients.
    """
    def __init__(self, win):
        self.win_id = win.GetId()
        self.event_handler = win.GetEventHandler()

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        """Invokes an event on the debug server."""
        raise NotImplementedError

    def kill(self):
        """Terminates the debugger."""
        raise NotImplementedError

    def getProcessId(self):
        """Returns the process ID if this client is connected to another
        process."""
        return 0

    def createEvent(self, typ):
        """Creates an event."""
        return DebuggerCommEvent(typ, self.win_id)

    def postEvent(self, evt):
        """Adds an event to the event queue."""
        if self.event_handler:
            self.event_handler.AddPendingEvent(evt)

    def pollStreams(self):
        """Returns the data sent to stdout and stderr."""
        return ('', '')


class DebuggerTask:
    """Calls invoke() on a debug client then posts an event on return.
    """
    def __init__(self, client, m_name, m_args=(), r_name='', r_args=()):
        self.client = client
        self.m_name = m_name
        self.m_args = m_args
        self.r_name = r_name
        self.r_args = r_args

    def __repr__(self):
        return '<DebuggerTask: %s:%s:%s:%s>'%(self.m_name, self.m_args,
                                              self.r_name, self.r_args)

    def __call__(self):
        evt = None
        try:

            # result = self.client.invoke(b'proceedAndRequestStatus', self.m_args)   # orig
            result = self.client.invoke(self.m_name, self.m_args)

        except:
            t, v = sys.exc_info()[:2]
            evt = self.client.createEvent(wxEVT_DEBUGGER_EXC)
            evt.SetExc(t, v)
        else:
            if self.r_name:
                evt = self.client.createEvent(wxEVT_DEBUGGER_OK)
                evt.SetReceiverName(self.r_name)
                evt.SetReceiverArgs(self.r_args)
                evt.SetResult(result)
        if evt:
            self.client.postEvent(evt)


class MultiThreadedDebugClient (DebugClient):

    taskHandler = ThreadedTaskHandler()

    def invoke(self, m_name, m_args):
        raise NotImplementedError

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        task = DebuggerTask(self, m_name, m_args, r_name, r_args)
        self.taskHandler.addTask(task)
