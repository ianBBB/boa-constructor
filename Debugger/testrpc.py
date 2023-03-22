import os, sys
sys.path[0:0] = [os.pardir]

from ChildProcessClient import spawnChild
import wx
from time import sleep
import threading

class Monitor:
    def isAlive(self):
        return 1
monitor = Monitor()


process = wx.Process()
process.Redirect()

def pollStreams():
    stream = process.GetInputStream()
    if not stream.eof():
        print('<<' + stream.read() + '>>')
    stream = process.GetErrorStream()
    if not stream.eof():
        print('<<<' + stream.read() + '>>>')

poll_streams = 1

def streamPollThread():
    while poll_streams:
        pollStreams()
        sleep(0.15)

print('spawning...')
s, input, output, processId = spawnChild(monitor, process)

t = threading.Thread(target=streamPollThread)
t.setDaemon(1)
t.start()

print('starting... (via %s)' % s)
status = s.runFileAndRequestStatus('test.py', (), 0, (),
                                   ({'filename':'test.py',
                                     'lineno':15,
                                     'cond':'',
                                     'enabled':1,
                                     'temporary':0},
                                    ))
print(status)
print('running...')
status = s.proceedAndRequestStatus('set_continue')
sleep(0.5)
print(status)
poll_streams = 0
sleep(0.3)

# Should stop in the middle of the process.
