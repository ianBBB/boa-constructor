#-----------------------------------------------------------------------------
# Name:        ZoaClient.py
# Purpose:     Nicer interface to Zope's Client.py. Also, the zoa installer
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
# pyright: ignore
# type: ignore

import os

import Client

class ZClient:
    def __init__(self, url, user, passwd, timeout=None, argnames=()):
        self.__url = url
        self.__user = user
        self.__passwd = passwd
        self.__timeout = timeout
        self.__argnames = argnames
    def __request(self, methodname, *args, **kwargs):
        msg, res = apply(Client.Function(self.__url+'/'+methodname,
                  username=self.__user, password=self.__passwd,
                  timeout=self.__timeout, arguments=self.__argnames),
                args, kwargs)
        return res
    def __getattr__(self, name):
        return _MethodDisp(self.__request, name)

class _MethodDisp:
    def __init__(self, request, name):
        self.__request = request
        self.__name = name
    def __getattr__(self, name):
        return _MethodDisp(self.__request, '%s/%s' % (self.__name, name))
    def __call__(self, *args, **kwargs):
        return apply(self.__request, (self.__name,) + args, kwargs)

def installZopeScript(conninfo, name, body):
    url, user, passwd = conninfo
    z = ZClient(url, user, passwd)
    try:
        z.manage_addProduct.PythonScripts.manage_addPythonScript(id=name, file=body)
    except Client.ServerError, error:
        if error.http_code != 302:
            raise

def installZopeFolder(conninfo, name):
    url, user, passwd = conninfo
    z = ZClient(url, user, passwd)
    z.manage_addFolder(id=name)

def installFromFS(conninfo, filepath):
    name = os.path.basename(filepath)
    installZopeFolder(conninfo, name)

    url, user, passwd = conninfo
    conninfo = url+'/'+name, user, passwd
    os.path.walk(filepath, installList, (filepath, conninfo) )

def installList(info, dirname, names):
    if os.path.basename(dirname) == 'CVS':
        return

    fsPath, (url, user, passwd) = info

    reldir = dirname[len(fsPath)+1:]
    if reldir:
        url = '/'.join([url] + reldir.split(os.sep))

    info = (url, user, passwd)
    for item in names:
        name, ext = os.path.splitext(item)
        if ext == '.py':
            installZopeScript(info, name, open(os.path.join(dirname, item)).read())
        else:
            if item != 'CVS' and os.path.isdir(os.path.join(dirname, item)):
                installZopeFolder(info, item)
