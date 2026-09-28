# pyright: ignore
# type: ignore

import base64
import xmlrpc.client

class TransportWithAuthentication (xmlrpc.client.Transport):
    """Adds a proprietary but simple authentication header to the
    RPC mechanism."""

    def __init__(self, user, pw):
        xmlrpc.client.Transport.__init__(self)
        auth_bytes = ('%s:%s' % (user, pw)).encode('utf-8')
        auth_token = base64.b64encode(auth_bytes).decode('ascii')
        self._auth = 'Basic %s' % auth_token

    def send_headers(self, connection, headers):
        xmlrpc.client.Transport.send_headers(self, connection, headers)
        connection.putheader("Authentication", self._auth)


from DebugClient import DebugClient, MultiThreadedDebugClient, \
     DebuggerTask

class RemoteClient (MultiThreadedDebugClient):

    server = None
    pyIntpPath = ''

    def __init__(self, win, host, port, user, pw):
        DebugClient.__init__(self, win)
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw

    def invoke(self, m_name, m_args):
        if self.server is None:
            trans = TransportWithAuthentication(self.user, self.pw)
            url = 'http://%s:%d/RemoteDebug' % (
                self.host, int(self.port))
            self.server = xmlrpc.client.ServerProxy(url, transport=trans)
        m = getattr(self.server, m_name)
        result = m(*m_args)
        return result

    def kill(self):
        if self.server is not None:
            # Let the debugged process know about the disconnect.
            self.taskHandler.addTask(
                self.server.set_disconnect, ())
        self.server = None

    def pollStreams(self):
        pass

    def isAlive(self):
        return self.server is not None
