#-----------------------------------------------------------------------------
# Name:        ZopeFTP.py
# Purpose:     FTP interface into Zope
#
# Author:      Riaan Booysen
#
# Created:     2000/05/08
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

# pyright: ignore
# type: ignore

import socket
import ftplib, os


class ZopeFTPItem:
    def __init__(self, path = '', name = '', perms = '----------', id = 0, size = 0, date = ''):
        self.path = path
        self.name = name
        self.perms = perms
        self.id = id
        self.size = size
        self.date = date
        self.lines = []

    def __repr__(self):
        return '<%s %s, %s>' % (`self.__class__`, self.whole_name(), self.date)

    def read(self, line):
        # dos:
        # 08-15-01  09:20AM                  255 __init__.pyc
        # [date  ]  [time ]                  [size] [name]
        items = filter(None, line.split())
        # DOS format
        if len(items) == 4:
            try:
                self.date = ' '.join((items[0], items[1]))
                if items[2] == '<DIR>':
                    self.size = '0'
                    self.perms = 'd'+self.perms[1:]
                else:
                    self.size = items[2]
                self.name = items[3]

            except Exception, message:
                print 'Could not read:', line, message
        # UNIX format
        else:
            try:
                self.perms, dunno, owner, group, self.size = items[:5]
                self.date = ' '.join(items[5:8])
                self.name = ' '.join(items[8:])

            except Exception, message:
                print 'Could not read:', line, message

    def prepareAsFile(self, data):
        self.lines = data.split('\n')
        self.lines.reverse()

    def readline(self):
        try: return self.lines.pop()+'\n'
        except IndexError: return ''

    def isFolder(self):
        return self.perms[0] == 'd'

    def isSysObj(self):
        return (self.size == 0) and (self.perms == '----------')

    def whole_name(self):
        if self.path == '/': return '/%s' % self.name
        else: return '%s/%s' % (self.path, self.name)

    def obj_path(self):
        return '.'.join(self.path.split('/') + [self.name])

    def cmd(self, cmd):
        return '%s %s' % (cmd, self.whole_name())

class ZopeFTP:
    def __init__(self):
        self.ftp = None
        self.host = ''
        self.port = 21
        self.username = ''
        self.password = ''
        self.connected = False
        self.http_port = 8080

    def __del__(self):
        self.disconnect()

    def connect(self, username, password, host, port = 21, passive = 0):
        self.ftp = ftplib.FTP('')

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.passive = passive

        res = []
        res.append(self.ftp.connect(host, port))

        # Zope returns 'Login successful' even on wrong passwords :(
        res.append(self.ftp.login(username, password))

        self.connected = True

        self.ftp.set_pasv(passive)

        return '\n'.join(res)


    def disconnect(self):
        if self.ftp: self.ftp.quit()
        self.ftp = None
        self.connected = False

    # XXX ren to doc_item
    def add_doc(self, name, path):
        return ZopeFTPItem(path, name, '-rw-rw----', 0, '')

    def folder_item(self, name, path):
        return ZopeFTPItem(path, name, 'drw-rw----', 0, '')

    def add_folder(self, name, path):
        self.ftp.mkd('%s/%s' % (path, name))

    def dir(self, path):
        res = []
        lst = []
        self.ftp.dir(path, lst.append)
        for line in lst:
            zftpi = ZopeFTPItem()
            zftpi.read(line)
            zftpi.path = path
            res.append(zftpi)
        return res

    def download(self, server_filename, local_filename):
        f = open(local_filename, 'wb')
        self.ftp.retrbinary('RETR %s' % server_filename, f.write)
        f.close()

    def load(self, item):
        res = []
        self.ftp.retrlines(item.cmd('RETR'), res.append)
        return '\n'.join(res)

    def save(self, item, data):
        item.prepareAsFile(data)
        try:
            self.ftp.storlines(item.cmd('STOR'), item)
        except socket.error, err:
            # reconnect and retry if connection has failed
            if err[0] == 10054:
                self.connect(self.username, self.password, self.host, self.port, self.passive)
                self.ftp.storlines(item.cmd('STOR'), item)


    def upload(self, filename, dest_path, data=None):
        if data is None:
            data = open(filename, 'rb').read()
        self.save(ZopeFTPItem(dest_path, os.path.basename(filename)), data)

    def delete(self, item):
        if item.isFolder():
            self.ftp.rmd(item.whole_name())
            return True
        else:
            self.ftp.delete(item.whole_name())
            return False

    def rename(self, item, new_name):
        old_path = item.whole_name()
        new_path = os.path.dirname(old_path)+'/'+new_name
        self.ftp.rename(old_path, new_path)
