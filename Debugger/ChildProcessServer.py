import sys, os, time
import threading
from time import sleep

from IsolatedDebugger import DebugServer, DebuggerConnection
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


# The process uses the Debugger dir as the main script dir
# here we add the boa root so that Boa modules can be imported.
boa_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if boa_root not in sys.path:
    sys.path.insert(0, boa_root)

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

serving = 1

debug_server = None
connection = None


def streamFlushThread():
    while 1:
        sys.stdout.flush()
        sys.stderr.flush()
        sleep(0.15)  # 150 ms


def main(args=None):
    global debug_server, connection, serving

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

    server = SimpleXMLRPCServer(
        ('127.0.0.1', 0), allow_none=True, requestHandler=RequestHandler
    )
    server.register_introspection_functions()
    server.register_instance(connection)

    port = int(server.server_address[1])

    # Keep a two-token startup line for compatibility with older client parsing.
    sys.stdout.write('%010d -%s' % (port, os.linesep))
    sys.stdout.flush()

    # Provide a hard breakpoint hook.  Use it like this:
    # if hasattr(sys, 'breakpoint'): sys.breakpoint()
    sys.breakpoint = debug_server.set_trace
    sys.debugger_control = debug_server
    sys.boa_debugger = debug_server


    def serveForever(server):
        server.serve_forever()

    def startDaemon(target, args=()):
        t = threading.Thread(target=target, args=args)
        t.daemon = True
        t.start()

    startDaemon(serveForever, (server,))
    startDaemon(streamFlushThread)
    startDaemon(debug_server.servicerThread)

    while serving:
        time.sleep(0.1)

    sys.exit(0)


if __name__ == '__main__':
    main()
