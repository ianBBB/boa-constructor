# DDE support for Boa
# Ripped from PythonWin

# Note DDE requires PythonWin

# Add this code snippet to Boa.py to turn Boa into a dde server
##try: 
##    import ddeconn
##    dde = ddeconn.DDEApp('BoaConstructor', startupModules,
##          'sys.boa_ide.openOrGotoModule(%s)')
##    if dde.done:
##        print 'Transfered arguments to running Boa, exiting.'
##        sys.exit()
##except ImportError: 
##    pass

from pywin.mfc import object
from dde import *
import traceback
import string

class DDESystemTopic(object.Object):
    def __init__(self, app):
        self.app = app
        object.Object.__init__(self, CreateServerSystemTopic())
    def Exec(self, data):
        try:
            self.app.OnDDECommand(data)
        except:
            # The DDE Execution failed.
            print("Error executing DDE command.")
            traceback.print_exc()
            return 0

class DDEServer(object.Object):
    def __init__(self, app):
        self.app = app
        object.Object.__init__(self, CreateServer())
        self.topic = self.item = None

    def CreateSystemTopic(self):
        return DDESystemTopic(self.app)

    def Shutdown(self):
        self._obj_.Shutdown()
        self._obj_.Destroy()
        if self.topic is not None:
            self.topic.Destroy()
            self.topic = None
        if self.item is not None:
            self.item.Destroy()
            self.item = None

    def OnCreate(self):
        return 1

    def Status(self, msg):
        pass
        #print 'STATUS', msg

class DDEApp:
    def __init__(self, name, args, execStr):
        self.args = args
        self.svrName = name
        self.done = 0
        self.execStr = execStr
        self.InitDDE()

    def MakeExistingDDEConnection(self):
    # Use DDE to connect to an existing instance
    # Return None if no existing instance
        conv = CreateConversation(self.ddeServer)
        try:
            conv.ConnectTo(self.svrName, "System")
            return conv
        except error:
            return None

    def InitDDE(self):
        # Do all the magic DDE handling.
        self.ddeServer = DDEServer(self)
        self.ddeServer.Create(self.svrName, CBF_FAIL_SELFCONNECTIONS )
        try:
        # If there is an existing instance, pump the arguments to it
            dde = self.MakeExistingDDEConnection()
            if dde is not None and self.args:
                for arg in self.args:
                    dde.Exec(self.execStr % repr(arg))
                self.done = 1
        except:
            print('ERROR: There was an error during the DDE conversation.')
            traceback.print_exc()

    def OnDDECommand(self, data):
        import sys
        exec(data)
        