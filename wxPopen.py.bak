import time
from cStringIO import StringIO

import wx

class ProcessRunnerMix:
    def __init__(self, input, handler=None):
        if handler is None:
            handler = self
        self.handler = handler
        handler.Bind(wx.EVT_IDLE, self.OnIdle)
        handler.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)

        input.reverse() # so we can pop
        self.input = input

        self.reset()

    def reset(self):
        self.process = None
        self.pid = -1
        self.output = []
        self.errors = []
        self.inputStream = None
        self.errorStream = None
        self.outputStream = None
        self.outputFunc = None
        self.errorsFunc = None
        self.finishedFunc = None
        self.finished = False
        self.responded = False

    def execute(self, cmd):
        self.process = wx.Process(self.handler)
        self.process.Redirect()

        self.pid = wx.Execute(cmd, wx.EXEC_NOHIDE, self.process)

        self.inputStream = self.process.GetOutputStream()
        self.errorStream = self.process.GetErrorStream()
        self.outputStream = self.process.GetInputStream()

        #self.OnIdle()
        wx.WakeUpIdle()

    def setCallbacks(self, output, errors, finished):
        self.outputFunc = output
        self.errorsFunc = errors
        self.finishedFunc = finished

    def detach(self):
        if self.process is not None:
            self.process.CloseOutput()
            self.process.Detach()
            self.process = None

    def kill(self):
        if self.process is not None:
            self.process.CloseOutput()
            if wx.Process.Kill(self.pid, wx.SIGTERM) != wx.KILL_OK:
                wx.Process.Kill(self.pid, wx.SIGKILL)
            self.process = None

    def updateStream(self, stream, data):
        if stream and stream.CanRead():
            if not self.responded:
                self.responded = True
            text = stream.read()
            data.append(text)
            return text
        else:
            return None

    def updateInpStream(self, stream, input):
        if stream and input:
            line = input.pop()
            stream.write(line)

    def updateErrStream(self, stream, data):
        return self.updateStream(stream, data)

    def updateOutStream(self, stream, data):
        return self.updateStream(stream, data)

    def OnIdle(self, event=None):
        if self.process is not None:
            self.updateInpStream(self.inputStream, self.input)
            e = self.updateErrStream(self.errorStream, self.errors)
            if e is not None and self.errorsFunc is not None:
                wx.CallAfter(self.errorsFunc, e)
            o = self.updateOutStream(self.outputStream, self.output)
            if o is not None and self.outputFunc is not None:
                wx.CallAfter(self.outputFunc, o)

            #wxWakeUpIdle()
            #time.sleep(0.001)

    def OnProcessEnded(self, event):
        self.OnIdle()

        if self.process:
            self.process.Destroy()
            self.process = None

        self.finished = True

        # XXX doesn't work ???
        #self.handler.Disconnect(-1, wxEVT_IDLE)

        if self.finishedFunc:
            wx.CallAfter(self.finishedFunc)

class ProcessRunner(wx.EvtHandler, ProcessRunnerMix):
    def __init__(self, input):
        wx.EvtHandler.__init__(self)
        ProcessRunnerMix.__init__(self, input)

def wxPopen3(cmd, input, output, errors, finish, handler=None):
    p = ProcessRunnerMix(input, handler)
    p.setCallbacks(output, errors, finish)
    p.execute(cmd)
    return p

def _test():
    app = wx.PySimpleApp()
    f = wx.Frame(None, -1, 'asd')#, style=0)
    f.Show()

    def output(v):
        print 'OUTPUT:', v
    def errors(v):
        print 'ERRORS:', v
    def fin():
        p = locals().get('p')
        if p: p.Close()
        f.Close()
        print 'FINISHED'


    def spin(p):
        while not p.finished:
            wx.Yield()
            time.sleep(0.01)

    def evt(self, event):
        input = []
        p = wxPopen3('''c:\\python23\\python.exe -c "print '*'*5000"''',
                 input, output, errors, fin, f)
        print p.pid

    app.MainLoop()

if __name__ == '__main__':
    _test()
