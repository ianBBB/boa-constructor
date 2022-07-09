#-----------------------------------------------------------------------------
# Name:        SSHExplorer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Explorers.SSHExplorer'

import os, sys

import wx

import Preferences, Utils
from Utils import _

import ExplorerNodes
from Models import Controllers, EditorHelper
from ProcessProgressDlg import ProcessProgressDlg

wxID_SSHOPEN = wx.NewId()

class SSHController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wx.Menu()

        self.setupMenu(self.menu, self.list,
              [ (wxID_SSHOPEN, 'Open', self.OnOpenItems, '-'),
                (-1, '-', None, '') ] + self.clipMenuDef)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = []
        self.menu.Destroy()

class SSHCatNode(ExplorerNodes.CategoryNode):
    itemProtocol = 'ssh'
    defName = 'SSH'
    defaultStruct = {'username': '',
                     'cipher': '3des',
                     'host': '',
                     'root': '~'}
    def __init__(self, clipboard, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, 'SSH', ('explorer', 'ssh'),
              clipboard, config, parent)
        self.bookmarks = bookmarks

    def createChildNode(self, name, props):
        root = props['root']
        #if root and root[0] != '/':
        #    root = '/'+root
        itm = SSHItemNode(name, props, root, self.clipboard, True,
              EditorHelper.imgNetDrive)
        itm.category = name
        itm.bookmarks = self.bookmarks
        return itm

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryDictCompanion(catNode.treename, self)
        return comp

class SSHItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'ssh'
    connection = False
    def __init__(self, name, props, resourcepath, clipboard, isFolder, imgIdx):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, None, props)
        self.isFolder = isFolder

    def isFolderish(self):
        return self.isFolder

    def getURI(self):
#        return ExplorerNodes.ExplorerNode.getURI(self) + (self.isFolder and '/' or '')
        title = self.getTitle()
        if title and title[0] != '/':
            title = '/' + title
        if self.isFolder:
            title = title + '/'
        return '%s://%s%s'%(self.protocol, self.category, title)

    def createChildNode(self, name, isFolder, props, respath=''):
        if not respath:
            respath = self.resourcepath+'/'+name
        item = SSHItemNode(name, props, respath, self.clipboard,
              isFolder, isFolder and EditorHelper.imgFolder or \
              EditorHelper.imgTextModel)
        if not isFolder:
            item.imgIdx = Controllers.identifyFile(name, localfs=False)[0].imgIdx
        item.category = self.category
        item.bookmarks = self.bookmarks
        return item

    def openList(self):
        res = []
        ls = self.execCmd("ls -la '%s'" % self.resourcepath)[1:]
        for line in ls:
            name = line.split(' ')[-1].strip()
            if name and name[-1] == '/':
                name = name[:-1]
            if name not in ('.', '..'):
                res.append(self.createChildNode(name, line[0] == 'd', self.properties))
        return res

    def execCmd(self, cmd):
        dlg = ProcessProgressDlg(None,
            self.sshCmd(cmd), _('SSH listing'), linesep = '\012')
        try:
            if dlg.ShowModal() == wx.OK:
                return dlg.output
        finally:
            dlg.Destroy()

        return []

    def sshCmd(self, command):
        return 'ssh -v -l %(username)s -c %(cipher)s %(host)s '% self.properties+\
                command

    def remotePath(self, filename):
        return '%(username)s@%(host)s:'%self.properties + self.resourcepath+\
               (filename and '/'+filename or '')

    def execSCP(self, cmd):
        dlg = ProcessProgressDlg(None, cmd, 'SCP copy', linesep = '\012')
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

    def copyFromFS(self, fsNode, fn=''):
        if not fn:
            fn = os.path.basename(fsNode.resourcepath)
        cwd = os.getcwd()
        os.chdir(os.path.dirname(fsNode.resourcepath))
        try:
            cmd = 'scp "%s" "%s"' % (os.path.basename(fsNode.resourcepath),
                                 self.remotePath(fn))
            self.execSCP(cmd)
        finally:
            os.chdir(cwd)

    def copyToFS(self, fsFolderNode, fn=''):
        if not fn:
            fn = os.path.basename(self.resourcepath)
        cwd = os.getcwd()
        os.chdir(fsFolderNode.resourcepath)
        try:
            cmd = 'scp "%s" "%s"' % (self.remotePath(''), fn)
            self.execSCP(cmd)
        finally:
            os.chdir(cwd)

    def moveFileFrom(self, other):
        fn = os.path.basename(other.resourcepath)
        self.execCmd("mv '%s' '%s'" % (other.resourcepath,
                                   self.resourcepath + '/' + fn))

    def copyFileFrom(self, other):
        fn = os.path.basename(other.resourcepath)
        self.execCmd("cp '%s' '%s'" % (other.resourcepath,
                                   self.resourcepath + '/' + fn))

    def deleteItems(self, names):
        absNames = []
        for name in names:
            absNames.append(self.resourcepath + '/' +name)
        self.execCmd("rm -rf '%s'" % ' '.join(absNames))

    def renameItem(self, name, newName):
        self.execCmd("mv '%s' '%s'" % (self.resourcepath + '/' + name,
                                   self.resourcepath + '/' + newName))

    def newFolder(self, name):
        self.execCmd("mkdir '%s'" % (self.resourcepath + '/' + name))

    def newBlankDocument(self, name):
        self.execCmd("echo \" \" > '%s'" % (self.resourcepath + '/' + name))

    def load(self, mode='rb'):
        from FileExplorer import FileSysNode
        import tempfile
        fn = tempfile.mktemp()
        p, n = os.path.split(fn)
        fn = os.path.join(p, 'X'+n)
        try:
            self.copyToFS(FileSysNode('', os.path.dirname(fn), None, -1, None, None), os.path.basename(fn))
            if os.path.exists(fn):
                try:
                    return open(fn, mode).read()
                finally:
                    os.remove(fn)
            else:
                raise ExplorerNodes.TransportLoadError(
                      _('File was not downloaded locally.'), self.resourcepath)
        except Exception, error:
            raise ExplorerNodes.TransportLoadError(error, self.resourcepath)

    def save(self, filename, data, mode='wb', overwriteNewer=False):
        from FileExplorer import FileSysNode
        import tempfile
        name = os.path.basename(self.resourcepath)
        fn = tempfile.mktemp()
        p, n = os.path.split(fn)
        fn = os.path.join(p, 'X'+n)
        try:
            open(fn, mode).write(data)
            try:
                parentDir = os.path.dirname(self.resourcepath)
                parentName = os.path.basename(parentDir)
                parentSSHNode = self.createChildNode(parentName, 1,
                      self.properties, parentDir)
                parentSSHNode.copyFromFS(FileSysNode('', fn, None, -1), name)
            finally:
                os.remove(fn)
        except Exception, error:
            raise ExplorerNodes.TransportSaveError(error, self.resourcepath)

##    def getNodeFromPath(self, respath):
##        if not respath: respath = '/'
##
##        isFolder = respath[-1] == '/'
##        if isFolder:
##            respath = respath[:-1]
##        return self.createChildNode(os.path.basename(respath), isFolder,
##              self.properties, '/'+respath)

    def getNodeFromPath(self, respath):
        if not respath: respath = '/'

        if not respath.startswith('~/'):
            respath = '/' + respath
        isFolder = respath[-1] == '/'
        if isFolder:
            respath = respath[:-1]
        return self.createChildNode(os.path.basename(respath), isFolder,
              self.properties, respath)

class SSHExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        for clipnode in nodes:
            if mode == 'cut':
                node.copyFromFS(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFromFS(clipnode)

    def clipPaste_SSHExpClipboard(self, node, nodes, mode):
        for sshNode in nodes:
            if mode == 'cut':
                node.moveFileFrom(sshNode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFileFrom(sshNode)

#-------------------------------------------------------------------------------
ExplorerNodes.register(SSHItemNode, clipboard=SSHExpClipboard,
      confdef=('explorer', 'ssh'), controller=SSHController, category=SSHCatNode)
ExplorerNodes.fileOpenDlgProtReg.append('ssh')
