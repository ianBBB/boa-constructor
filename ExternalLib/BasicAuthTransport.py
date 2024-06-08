from base64 import *
import string
import base64
from ExternalLib.WebDAV import httplib
import ExternalLib.xmlrpclib as xmlrpclib


class BasicAuthTransport(xmlrpclib.Transport):
    def __init__(self,username=None,password=None):
        self.username=username
        self.password=password
        self.verbose=0
    def request(self,host,handler,request_body,verbose=0):
        h=httplib.HTTP(host)
        h.putrequest("POST",handler)
        h.putheader("Host",host)
        h.putheader("User-Agent",self.user_agent)
        h.putheader("Content-Type","text/xml")
        h.putheader("Content-Length",str(len(request_body)))
        if self.username is not None and self.password is not None:
            h.putheader("AUTHORIZATION", "Basic %s" % str.replace(str(base64.encodestring("%s:%s" % (self.username, self.password))),"\012", ""))
        h.endheaders()
        if request_body:
            h.send(request_body)

        errcode, errmsg, headers = h.getreply()
        #print 'getreply ok'

        if errcode != 200:
            raise xmlrpclib.ProtocolError(host + handler,errcode,errmsg,headers)
        return self.parse_response(h.getfile())
