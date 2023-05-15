import sys, os
import threading
import base64
import time
from socketserver import TCPServer

from IsolatedDebugger import DebugServer, DebuggerConnection
from Tasks import ThreadedTaskHandler


try:
    from ExternalLib.xmlrpcserver import RequestHandler
except ImportError:
    # Add parent directory to the path search.
    sys.path[0:0] = [os.pardir]
    from ExternalLib.xmlrpcserver import RequestHandler


debug_server = None
connection = None
auth_str = ''
task_handler = ThreadedTaskHandler()


class DebugRequestHandler (RequestHandler):

    def _authenticate(self):
        # TODO Debugging
        time.sleep(20)
        h = self.headers
        if auth_str:
            s = h.get('authentication')
            if not s or s.split()[-1] != auth_str:
                raise Exception('Unauthorized: Authentication header missing or incorrect')

    def call(self, method, params):
        # Override of xmlrpcserver.RequestHandler.call()
        # TODO Debugging
        time.sleep(20)
        self._authenticate()
        m = getattr(connection, method)
        result = m(*params)
        if result is None:
            result = 0
        return result

    def log_message(self, format, *args):
        pass


class TaskingMixIn:
    """Mix-in class to handle each request in a task thread."""

    def process_request(self, request, client_address):
        """Start a task to process the request."""

        # TODO Debugging
        time.sleep(20)

        task_handler.addTask(self.finish_request,
                             args=(request, client_address))

class TaskingTCPServer(TaskingMixIn, TCPServer):
    allow_reuse_address = 1


def start(username, password, host='127.0.0.1', port=26200,
          server_type='zope'):
    global auth_str, debug_server, connection

    if debug_server is not None:
        raise RuntimeError('The debug server is already running')

    # Create the debug server.
    if server_type == 'zope':
        from ZopeScriptDebugServer import ZopeScriptDebugServer
        ds = ZopeScriptDebugServer()
    elif server_type == 'basic':
        ds = DebugServer()
    else:
        raise ValueError('Unknown debug server type: %s' % server_type)

    connection = DebuggerConnection(ds)
    connection.allowEnvChanges()  # Allow changing of sys.path, etc.

    # Create an authentication string.
    auth_str = base64.encodestring('%s:%s' % (username, password)).strip()

    debug_server = ds
    server = TaskingTCPServer((host, port), DebugRequestHandler)
    port = int(server.socket.getsockname()[1])

    # Provide a hard breakpoint hook.  Use it like this:
    # if hasattr(sys, 'breakpoint'): sys.breakpoint()
    sys.breakpoint = debug_server.set_trace
    sys.debugger_control = debug_server
    sys.boa_debugger = debug_server

    def serve_forever(server):
        while 1:
            server.handle_request()

    def startDaemon(target, args=()):
        t = threading.Thread(target=target, args=args)
        t.setDaemon(1)
        t.start()

    startDaemon(serve_forever, (server,))
    #startDaemon(debug_server.servicerThread)

    # print >> sys.stderr, "Debug server listening on %s:%s" % tuple(
    #     server.socket.getsockname()[:2])
    sys.stderr.write("Debug server listening on %s:%s" % tuple(
        server.socket.getsockname()[:2]))

    try:
        import atexit
    except ImportError:
        pass
    else:
        atexit.register(server.socket.close)

def stop():
    global debug_server, connection
    debug_server = None
    connection = None
