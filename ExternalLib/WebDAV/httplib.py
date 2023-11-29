"""HTTP client class

See the following URL for a description of the HTTP/1.0 protocol:
http://www.w3.org/hypertext/WWW/Protocols/
(I actually implemented it from a much earlier draft.)

Example:

from httplib import HTTP
h = HTTP('www.python.org')
h.putrequest('GET', '/index.html')
h.putheader('Accept', 'text/html')
h.putheader('Accept', 'text/plain')
h.endheaders()
errcode, errmsg, headers = h.getreply()
if errcode == 200:
    f = h.getfile()
    print f.read() # Print the raw HTML

<HEAD>
<TITLE>Python Language Home Page</TITLE>
[...many more lines...]
>>>

Note that an HTTP object is used for a single request -- to issue a
second request to the same server, you create a new HTTP object.
(This is in accordance with the protocol, which uses a new TCP
connection for each request.)
"""
import email
import socket
import string
import email as mimetools
import http.client

HTTP_VERSION = 'HTTP/1.0'
HTTP_PORT = 80


class HTTP:
    """This class manages a connection to an HTTP server."""

    def __init__(self, host = '', port = 0):
        """Initialize a new instance.

        If specified, `host' is the name of the remote host to which
        to connect.  If specified, `port' specifies the port to which
        to connect.  By default, httplib.HTTP_PORT is used.

        """
        self.debuglevel = 1   # DEBUG normally set 0. Set to 1 for now.
        self.file = None
        if host: self.connect(host, port)
        self._buffer=[]

    def set_debuglevel(self, debuglevel):
        """Set the debug output level.

        A non-false value results in debug messages for connection and
        for all messages sent to and received from the server.

        """
        self.debuglevel = debuglevel

    def connect(self, host, port = 0):
        """Connect to a host on a given port.

        Note:  This method is automatically invoked by __init__,
        if a host is specified during instantiation.

        """
        if not port:
            # i = string.find(host, ':')   # orig
            i = host.find(':')
            if i >= 0:
                host, port = host[:i], host[i+1:]
                # try: port = atoi(port)   # orig
                try: port = int(port)
                except string.atoi_error:
                    raise socket.error("nonnumeric port")
        if not port: port = HTTP_PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.debuglevel > 0: print('connect:', (host, port))
        self.sock.connect( (host, port) )

    def send(self, str_mess):
        """Send `str' to the server."""
        if self.debuglevel > 0: print('send:', repr(str_mess))
        if isinstance(str_mess,(bytes)):
            self.sock.send(str_mess)
        else:
            self.sock.send(str.encode(str_mess))


    def putrequest(self, request, selector):
        """Send a request to the server.

        `request' specifies an HTTP request method, e.g. 'GET'.
        `selector' specifies the object being requested, e.g.
        '/index.html'.

        """
        if not selector: selector = '/'
        # str = '%s %s %s\r\n' % (request, selector, HTTP_VERSION)   # orig
        # self.send(str)

        send_str = '%s %s %s\r\n' % (request, selector, HTTP_VERSION)
        self.send(str.encode(send_str))


    def putheader(self, header, *args):
        """Send a request header line to the server.

        For example: h.putheader('Accept', 'text/html')

        """
        # str = '%s: %s\r\n' % (header, string.joinfields(args,'\r\n\t'))   # orig
        assembled_str = ""
        if header in ["POST"]:
            assembled_str = header + ' ' + args[0]
        else:
            assembled_str = '%s: %s' % (header, '\r\n\t'.join(args) )
        # self.send(str)
        self._output(assembled_str)

    def _output(self, assembled_str):
        self._buffer.append(assembled_str)

    def endheaders(self):
        """Indicate that the last header line has been sent to the server."""
        if len(self._buffer) > 1:
            self._buffer.extend(("", ""))
            msg = "\r\n".join(self._buffer)
            del self._buffer
            self.send(msg)

    def getreply(self):
        """Get a reply from the server.

        Returns a tuple consisting of:
        - server response code (e.g. '200' if all goes well)
        - server response string corresponding to response code
        - any RFC822 headers in the response from the server

        """
        self.file = self.sock.makefile('rb')
        lines = self.file.readlines()
        line=lines[0]
        if self.debuglevel > 0: print('reply:', repr(line))
        try:
            # [ver, code, msg] = string.split(line, None, 2)
            [ver, code, msg] = str.split(line.decode(), None, 2)
        except ValueError:
            try:
                [ver, code] = str.split(line.decode(), None, 1)
                msg = ""
            except ValueError:
                self.headers = None
                return -1, line, self.headers
        if ver[:5] != 'HTTP/':
            self.headers = None
            return -1, line, self.headers
        errcode = int(code)
        errmsg = str.strip(msg)

        # self.headers = mimetools.message.Message(self.file, 0)   # orig

        # process headers into a dictionary.
        headers = {}
        if lines[1:]:
            for a_header in lines[1:-1]:
                header_key, header_value = a_header.decode().strip().split(':',1)
                headers[header_key]=header_value.strip()
        self.headers=headers

        # from email import message_from_string
        # from email import parser
        # from email.parser import BytesParser
        # message_as_bytes = b''.join(lines)
        #
        # request_line, headers_alone = message_as_bytes.split(b'\r\n', 1)
        #
        # self.headers = BytesParser().parsebytes(headers_alone)
        # myheaders = email.message_from_file(self.file)
        # self.headers = message_from_string((lines, 'ASCII').split('\r\n', 1)[1])

        return errcode, errmsg, self.headers

    def getfile(self):
        """Get a file object from which to receive data from the HTTP server.

        NOTE:  This method must not be invoked until getreplies
        has been invoked.

        """
        return self.file

    def close(self):
        """Close the connection to the HTTP server."""
        if self.file:
            self.file.close()
        self.file = None
        if self.sock:
            self.sock.close()
        self.sock = None


def test():
    """Test this module.

    The test consists of retrieving and displaying the Python
    home page, along with the error code and error string returned
    by the www.python.org server.

    """
    import sys
    import getopt
    opts, args = getopt.getopt(sys.argv[1:], 'd')
    dl = 0
    for o, a in opts:
        if o == '-d': dl = dl + 1
    host = 'www.python.org'
    selector = '/'
    if args[0:]: host = args[0]
    if args[1:]: selector = args[1]
    h = HTTP()
    h.set_debuglevel(dl)
    h.connect(host)
    h.putrequest('GET', selector)
    h.endheaders()
    errcode, errmsg, headers = h.getreply()
    print('errcode =', errcode)
    print('errmsg  =', errmsg)
    print()
    if headers:
        for header in headers.headers: print(string.strip(header))
    print()
    print(h.getfile().read())


if __name__ == '__main__':
    test()
