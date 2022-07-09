#-----------------------------------------------------------------------------
# Name:        FTPExplorer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Explorers.FTPExplorer'

import os

import wx

import Preferences, Utils
from Utils import _

import ExplorerNodes
from Models import Controllers, EditorHelper
import ftplib

wxID_FTPOPEN = wx.NewId()

class FTPController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wx.Menu()

        self.setupMenu(self.menu, self.list,
              [ (wxID_FTPOPEN, _('Open'), self.OnOpenItems, '-'),
                (-1, '-', None, '') ] + self.clipMenuDef)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = ()
        self.menu.Destroy()


class FTPCatNode(ExplorerNodes.CategoryNode):
    itemProtocol = 'ftp'
    defName = 'FTP'
    defaultStruct = {'username': 'anonymous',
                     'passwd': '',
                     'host': 'localhost',
                     'port': 21,
                     'path': '/',
                     'passive': 0}
    def __init__(self, clipboard, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, 'FTP', ('explorer', 'ftp'),
              clipboard, config, parent)
        self.bookmarks = bookmarks

    def createParentNode(self):
        return self

    def createChildNode(self, name, props):
        ftpcn = FTPConnectionNode(name, props, props['path'], self.clipboard, self)
        ftpcn.bookmarks = self.bookmarks
        return ftpcn

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryDictCompanion(catNode.treename, self)
        return comp

class FTPItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'ftp'
    connection = True
    def __init__(self, name, props, resourcepath, clipboard, isFolder, imgIdx, parent, ftpConn, ftpObj, root):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx,
              parent, props)
        self.isFolder = isFolder
        self.ftpConn = ftpConn
        self.ftpObj = ftpObj
        self.root = root
        self.cache = {}

    def destroy(self):
        pass#self.cache = {}

    def isFolderish(self):
        return self.ftpObj.isFolder()

    def getURI(self):
        return '%s://%s%s%s' %(self.protocol, self.category,
              self.ftpObj.whole_name(), self.isFolderish() and '/' or '')

    def createChildNode(self, obj, root, respath=None, createConnection=False):
        if respath is None:
            respath=self.resourcepath+'/'+obj.name
        elif respath[0] != '/':
            respath = '/'+respath

        if createConnection:
            item = FTPConnectionNode(obj.name, self.properties, respath,
                self.clipboard, self)
        else:
            item = FTPItemNode(obj.name, self.properties, respath,
                  self.clipboard, False, -1 , self, self.ftpConn, obj, root)

        if item.isFolderish():
            item.imgIdx = EditorHelper.imgFolder
        else:
            item.imgIdx = Controllers.identifyFile(obj.name, localfs=False)[0].imgIdx
        item.category = self.category
        item.bookmarks = self.bookmarks
        return item

    def openList(self, root=None):
        items = self.ftpConn.dir(self.ftpObj.whole_name())

        if not root: root = self.root
        self.cache = {}
        result = []
        for obj in items:
            if obj.name in ('', '.', '..'):
                continue
            z = self.createChildNode(obj, self.root)
            if z:
                result.append(z)
                self.cache[obj.name] = z

        return result

    def deleteItems(self, names):
        for item in names:
            self.ftpConn.delete(self.cache[item].ftpObj)

    def renameItem(self, name, newName):
        self.ftpConn.rename(self.cache[name].ftpObj, newName)

    def newFolder(self, name):
        self.ftpConn.add_folder(name, self.resourcepath)

    def newBlankDocument(self, name):
        self.ftpConn.upload(name, self.resourcepath, ' ')

    def load(self, mode='rb'):
        try:
            return self.ftpConn.load(self.ftpObj)
        except Exception, error:
            raise ExplorerNodes.TransportLoadError(error, self.ftpObj.whole_name())

    def save(self, filename, data, mode='wb', overwriteNewer=False):
        if filename != self.currentFilename():
            self.ftpObj.path = os.path.dirname(filename)
            self.ftpObj.name = os.path.basename(filename)
        try:
            self.ftpConn.save(self.ftpObj, data)
        except Exception, error:
            raise ExplorerNodes.TransportSaveError(error, self.ftpObj.whole_name())

    def getNodeFromPath(self, respath):
        if not respath: respath = '/'

        isFolder = respath[-1] == '/'
        if isFolder:
            if respath != '/':
                respath = respath[:-1]
            return self.createChildNode(self.ftpConn.folder_item(os.path.dirname(respath),
                os.path.basename(respath)), self.root, respath)
        else:
            return self.createChildNode(self.ftpConn.add_doc(os.path.dirname(respath),
                os.path.basename(respath)), self.root, respath)


class FTPConnectionNode(FTPItemNode):
    def __init__(self, name, properties, respath, clipboard, parent):
        from ZopeLib import ZopeFTP

        ftpConn = ZopeFTP.ZopeFTP()
        if respath and respath[-1] == '/':
            ftpObj = ftpConn.folder_item(os.path.basename(respath),
                                         os.path.dirname(respath))
            isFolder = True
        else:
            ftpObj = ftpConn.add_doc(os.path.basename(respath),
                                         os.path.dirname(respath))
            isFolder = False

        FTPItemNode.__init__(self, '', properties, ftpObj.path, clipboard,
            isFolder, EditorHelper.imgNetDrive, parent, ftpConn, ftpObj, self)
        self.connected = False
        self.treename = name
        self.category = name

    def openList(self):
        self.testConnect()
        return FTPItemNode.openList(self, self)

    def load(self, mode='rb'):
        self.testConnect()
        return FTPItemNode.load(self, mode)

    def save(self, filename, data, mode='wb', overwriteNewer=False):
        self.testConnect()
        FTPItemNode.save(self, filename, data, mode, overwriteNewer)

    def createChildNode(self, obj, root, respath=None):
        return FTPItemNode.createChildNode(self, obj, root, respath, not self.connected)

    def testConnect(self):
        if not self.connected:
            try:
                props = self.properties
                self.ftpConn.connect(props['username'], props['passwd'],
                                     props['host'], props['port'],
                                     props['passive'])
            except Exception, message:
                wx.MessageBox(`message.args`, 'Error on connect')
                raise
            else:
                self.connected = True


class FTPExpClipboard(ExplorerNodes.ExplorerClipboard):
    def pasteFileSysFolder(self, folderpath, nodepath, ftpConn):
        ftpConn.add_folder(os.path.basename(folderpath), nodepath)
        files = os.listdir(folderpath)
        folder = os.path.basename(folderpath)
        newNodepath = nodepath+'/'+folder
        for file in files:
            file = os.path.join(folderpath, file)
            if os.path.isdir(file):
                self.pasteFileSysFolder(file, newNodepath, ftpConn)
            else:
                ftpConn.upload(file, newNodepath)

    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        nodepath = node.resourcepath
        for file in nodes:
            if file.isDir():
                self.pasteFileSysFolder(file.resourcepath, nodepath, node.ftpConn)
            else:
                node.ftpConn.upload(file.resourcepath, nodepath)

#-------------------------------------------------------------------------------
ExplorerNodes.register(FTPItemNode, clipboard=FTPExpClipboard,
      confdef=('explorer', 'ftp'), controller=FTPController, category=FTPCatNode)
ExplorerNodes.fileOpenDlgProtReg.append('ftp')
