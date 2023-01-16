import sys, os, time
# import random, sha, threading
import random
import hashlib
import threading
from time import sleep
# from SocketServer import TCPServer
import socketserver

from IsolatedDebugger import DebugServer, DebuggerConnection
from Tasks import ThreadedTaskHandler

# The process uses the Debugger dir as the main script dir
# here we add the boa root so that Boa modules can be imported.
boa_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if boa_root not in sys.path:
    sys.path.insert(0, boa_root)

try:
    from ExternalLib.xmlrpcserver import RequestHandler
except ImportError:
    from ExternalLib.xmlrpcserver import RequestHandler

serving = 1

debug_server = None
connection = None
auth_str = ''
task_handler = ThreadedTaskHandler()


class DebugRequestHandler (RequestHandler):

    def _authenticate(self):
        h = self.headers
        if auth_str and (not h.has_key('x-auth')
                         or h['x-auth'] != auth_str):
            # raise Exception, 'Unauthorized: X-Auth header missing or incorrect'
            raise Exception ('Unauthorized: X-Auth header missing or incorrect')

    def call(self, method, params):
        # Override of xmlrpcserver.RequestHandler.call()
        self._authenticate()
        if method == 'exit_debugger':
            global serving
            serving = 0
            return 1
        else:
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
        task_handler.addTask(self.finish_request,
                             args=(request, client_address))

# class TaskingTCPServer(TaskingMixIn, TCPServer): pass
class TaskingTCPServer(TaskingMixIn, socketserver.TCPServer): pass


def streamFlushThread():
    while 1:
        sys.stdout.flush()
        sys.stderr.flush()
        sleep(0.15)  # 150 ms


def main(args=None):
    global auth_str, debug_server, connection, serving

    # Create the debug server.
    if args is None:
        args = sys.argv[1:]
    if args and '--zope' in args:
        from ZopeScriptDebugServer import ZopeScriptDebugServer
        debug_server = ZopeScriptDebugServer()
    else:
        debug_server = DebugServer()
    connection = DebuggerConnection(debug_server)
    connection.allowEnvChanges()  # Allow changing of sys.path, etc.

    # Create an authentication string, always 40 characters.
    # auth_str = sha.new(str(random.random())).hexdigest()
    auth_str = hashlib.sha256(str(random.random()).encode('utf-8')).hexdigest()

    # port is 0 to allocate any port.
    server = TaskingTCPServer(('', 0), DebugRequestHandler)
    port = int(server.socket.getsockname()[1])

    # Tell the client what port to connect to and the auth string to send.
    sys.stdout.write('%010d %s%s' % (port, auth_str, os.linesep))
    sys.stdout.flush()

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
    startDaemon(streamFlushThread)
    startDaemon(debug_server.servicerThread)

    # Serve until the stdin pipe closes.
    #print 'serving until stdin returns EOF'
    #sys.stdin.read()

    while serving:
        time.sleep(0.1)

    sys.exit(0)


if __name__ == '__main__':
    main()
