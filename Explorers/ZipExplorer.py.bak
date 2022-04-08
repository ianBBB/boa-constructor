#-----------------------------------------------------------------------------
# Name:        ZipExplorer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing Explorers.ZipExplorer'
import os, zipfile, gzip, time
from cStringIO import StringIO

import wx

from Utils import _

import ExplorerNodes, FileExplorer
from Models import EditorModels, EditorHelper

from ExternalLib import tarfile

def isZip(file):
    return os.path.splitext(file)[1] == '.zip'

wxID_ZIPOPEN = wx.NewId()

class ZipController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wx.Menu()

        self.setupMenu(self.menu, self.list,
            [ (wxID_ZIPOPEN, _('Open'), self.OnOpenItems, '-'),
              (-1, '-', None, '') ] + self.clipMenuDef)

        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = []
        self.menu.Destroy()


class ZipExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        for clipnode in nodes:
            if mode == 'cut':
                node.copyFromFS(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFromFS(clipnode)

class ZipItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'zip'
    ArchiveClass = zipfile.ZipFile
    InfoClass = zipfile.ZipInfo

    def __init__(self, name, resourcepath, clipboard, isFolder, imgIdx, parent,
          zipFileNode, ChildClass):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent)
        self.isFolder = isFolder
        self.zipFileNode = zipFileNode
        ##self.lineSep = None # meaning binary
        self.ChildClass = ChildClass
        self.compression = zipfile.ZIP_DEFLATED

    def isFolderish(self):
        return self.isFolder

    def createChildNode(self, name, resourcepath, isFolder):

        imgIdx = isFolder and EditorHelper.imgFolder or \
              EditorHelper.imgTextModel
        if not isFolder:
            from Models import Controllers
            imgIdx = Controllers.identifyFile(name, localfs=False)[0].imgIdx
        zin = self.ChildClass(name, resourcepath and resourcepath+'/'+name or name,
              self.clipboard, isFolder, imgIdx, self, self.zipFileNode, self.ChildClass)
        zin.category = self.category
        return zin

    def newInfoClass(self, name):
        info = self.InfoClass(name)
        info.compress_type = self.compression
        return info

    def splitBaseDir(self, file):
        if not file:
            return '', '', True
        segs = file.split('/')
        # ends on /
        if segs[-1] == '':
            base = segs[-2]
            dir = '/'.join(segs[:-2])
            isdir = 1
        else:
            base = segs[-1]
            dir = '/'.join(segs[:-1])
            isdir = 0
        return base, dir, isdir

    def openList(self, resourcepath=None):
        if resourcepath is None: resourcepath = self.resourcepath
        res = []
        files = self.zipFileNode.getFiles(resourcepath)
        for file in files:
            base, dir, isdir = self.splitBaseDir(file)

            res.append(self.createChildNode(base, dir, self.zipFileNode.isDir(file)) )
        return res

    def getArcDir(self):
        if self.isFolderish():
            return self.resourcepath
        else:
            return os.path.dirname(self.resourcepath)

    def walkFS(self, (files, excludes), dirname, names):
        for name in names:
            if name not in excludes:
                filename = os.path.join(dirname, name)
                if os.path.isfile(filename):
                    files.append(filename)

    def copyFromFS(self, fsNode, fn=''):
        if not fn:
            fn = os.path.basename(fsNode.resourcepath)

        if fsNode.isFolderish():
            fsFiles = []
            fsDir = fsNode.resourcepath
            fsDirDir = os.path.dirname(fsNode.resourcepath)
            os.path.walk(fsDir, self.walkFS, (fsFiles, ()))
            new = []
            replace = []
            for fn in fsFiles:
                if os.path.isabs(self.resourcepath):
                    pref = ''
                else:
                    pref = self.resourcepath + '/'
                destName = pref+fn[len(fsDirDir)+1:]
                if destName in self.zipFileNode.allFileNames:
                    replace.append( (destName, fn) )
                else:
                    new.append( (destName, fn) )
            # replace existing
            filesData = [ (arcname, '', open(filename, 'rb').read())
                          for arcname, filename in replace ]
            self.replaceFilesInArchive(filesData)

            # append new
            if new:
                zf = self.ArchiveClass(self.zipFileNode.resourcepath, 'a', self.compression)
                try:
                    for arcname, filename in new:
                        zi = self.newInfoClass(arcname)
                        zf.writestr(zi, open(filename, 'rb').read())
                finally:
                    zf.close()
                self.zipFileNode.allFiles = None
        else:
            data = fsNode.load(mode='rb')
            # if already in archive, must be replaced, else can be appended
            #arcDir = os.path.dirname(self.resourcepath)
            destName = '/'.join([self.getArcDir(), fn])
            if destName in self.zipFileNode.allFileNames:
                # XXX prompt?
                self.replaceFilesInArchive([(destName, '', data)])
            else:
                zf = self.ArchiveClass(self.zipFileNode.resourcepath, 'a', self.compression)
                try:
                    zi = self.newInfoClass(destName)
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zi.file_size = len(data)
                    zi.date_time = time.localtime(fsNode.stdAttrs['modify-date'])[:6]
                    zf.writestr(zi, data)
                finally:
                    zf.close()
                self.zipFileNode.allFiles = None

    def copyToFS(self, fsFolderNode):
        fn = os.path.join(fsFolderNode.resourcepath, self.name)

        zf = self.ArchiveClass(self.zipFileNode.resourcepath,
                               compression=self.compression)
        try:
            if self.isFolderish():
                try: os.mkdir(fn)
                except OSError: pass
                files = self.zipFileNode.getFiles(self.resourcepath, True)
                for arcName in files:
                    fn = os.path.join(fsFolderNode.resourcepath, arcName)
                    try: os.makedirs(os.path.dirname(fn))
                    except OSError: pass
                    open(fn, 'wb').write(zf.read(arcName))
            else:
                open(fn, 'wb').write(zf.read(self.resourcepath))
        finally:
            zf.close()

    def newFolder(self, name):
        zf = self.ArchiveClass(self.zipFileNode.resourcepath, 'a', self.compression)
        try:
            ad = self.getArcDir()
            if ad: ad +='/'
            newArcName = '%s%s/'%(ad, name)
            zi = self.newInfoClass(newArcName)
            zi.file_size = 0
            zi.flag_bits = 0x02
            zi.date_time = time.localtime()[:6]
            zf.writestr(zi, '')
            self.zipFileNode.allFiles = None
        finally:
            zf.close()
        return name
        #raise Exception, 'The zipfile module does not suppport adding empty folders'

    def newBlankDocument(self, name=''):
        zf = self.ArchiveClass(self.zipFileNode.resourcepath, 'a', self.compression)
        try:
            ad = self.getArcDir()
            if ad: ad +='/'
            newArcName = '%s%s'%(ad, name)
            zi = self.newInfoClass(newArcName)
            zi.file_size = 0
            zi.date_time = time.localtime()[:6]
            zf.writestr(zi, '')
            self.zipFileNode.allFiles = None
        finally:
            zf.close()
        return name

    def load(self, mode='rb'):
        zf = self.ArchiveClass(self.zipFileNode.resourcepath)
        try:
            return zf.read(self.resourcepath)
        finally:
            zf.close()

    def save(self, filename, data, mode='wb', overwriteNewer=True):
        self.replaceFilesInArchive([(self.resourcepath, filename, data)])

    def renameItem(self, name, newName):
        arcDir = self.getArcDir()
        oldfile = '/'.join([arcDir, name])
        newfile = '/'.join([arcDir, newName])
        self.replaceFilesInArchive([(oldfile, newfile, None)])

    def replaceFilesInArchive(self, filesData):
        # There seems to be no way to replace a zip entry.
        # Here the whole archive is recreated
        zipStream = StringIO(open(self.zipFileNode.resourcepath, 'rb').read())
        zfSrc = self.ArchiveClass(zipStream, 'r')
        try:
            changed = False
            zfDst = self.ArchiveClass(self.zipFileNode.resourcepath, 'w', self.compression)
            try:
                for zi in zfSrc.infolist():
                    for fn, nfn, data in filesData:
                        if zi.filename == fn:
                            changed = True
                            if nfn:
                                zi.filename = nfn
                            if data is None:
                                zipData = data = zfSrc.read(fn)
                            else:
                                zipData = data
                            break
                    else:
                        zipData = zfSrc.read(zi.filename)
                    zi.size = zi.file_size = len(zipData)
                    zfDst.writestr(zi, zipData)
            finally:
                zfDst.close()
        finally:
            zfSrc.close()

        if changed:
            self.zipFileNode.allFiles = None


    def getNodeFromPath(self, respath):
        base, dir, isdir = self.splitBaseDir(respath)
        return self.createChildNode(base, dir, self.zipFileNode.isDir(respath))

class ZipFileNode(ZipItemNode):
    protocol = 'zip'
    ChildClass = ZipItemNode

    def __init__(self, name, resourcepath, clipboard, imgIdx, parent,
          bookmarks=None):
        if clipboard:
            zipClip = ZipExpClipboard(clipboard.globClip)
        else:
            zipClip = None
        ZipItemNode.__init__(self, name, resourcepath, zipClip, True,
            imgIdx, parent, self, self.ChildClass)
        self.allFiles = None
        self.allFileNames = []
        self.category = self.getTitle()+'://'

    def getURI(self):
        return '%s://%s' % (self.protocol, self.getTitle())

    def isFolderish(self):
        return True

    def isDir(self, path = ''):
        if path:
            return path[-1] == '/'
        else:
            return False

    def getArcDir(self):
        return ''

    def openList(self):
        self.updateFilelists()
        # Add implicit folder entries
        for filename in self.allFileNames[:]:
            if filename[-1] == '/':
                # don't build if zip has folder entries
                break
            while 1:
                filename = os.path.dirname(filename)
                path = filename +'/'
                if path == '/':
                    break
                if path not in self.allFileNames:
                    self.allFileNames.insert(0, path)
                    self.allFiles.insert(0, self.newInfoClass(path))

        return ZipItemNode.openList(self, '')

    def getFiles(self, base, nested=False):
        files = []
        if self.allFiles is None:
            self.updateFilelists()

        for file in self.allFiles:
            if file.filename[-1] == '/':
                fn = file.filename[:-1]
            else:
                fn = file.filename

            if nested:
                if fn.startswith(base):
                    files.append(file.filename)
            else:
                dir = os.path.dirname(fn)
                dirdir = os.path.dirname(dir)
                if dir and dirdir == base:
                    try: idx = files.index(dir+'/')
                    except ValueError: files.append(dir+'/')

                if dir == base:
                    try: files.index(file.filename)
                    except ValueError: files.append(file.filename)
        return files

    def updateFilelists(self):
        zf = self.ArchiveClass(self.resourcepath, 'r')
        try:
            self.compression = zf.compression
            self.allFiles = zf.infolist()
            self.allFileNames = [fl.filename for fl in self.allFiles]
        finally:
            zf.close()


EditorHelper.imgZipFileModel = \
      EditorHelper.addPluginImgs('Images/Modules/ZipFile.png')
class ZipFileModel(EditorModels.EditorModel):
    modelIdentifier = 'ZipFile'
    defaultName = 'zip'
    bitmap = 'ZipFile.png'
    imgIdx = EditorHelper.imgZipFileModel
    ext = '.zip'

def uriSplitZip(filename, zipfile, zipentry):
    return 'zip', zipfile, zipentry, filename

def findZipExplorerNode(category, respath, transports):
    zf = ZipFileNode(os.path.basename(category), category, None, -1, None, None)
    zf.openList()
    return zf.getNodeFromPath(respath)

#-------------------------------------------------------------------------------
# Register zip files as a subtype of file explorers
FileExplorer.FileSysNode.subExplorerReg['file'].append(
      (ZipFileNode, isZip, EditorHelper.imgZipFileModel))
ExplorerNodes.register(ZipItemNode, clipboard=ZipExpClipboard,
      controller=ZipController)
ExplorerNodes.uriSplitReg[('zip', 3)] = uriSplitZip
ExplorerNodes.transportFindReg['zip'] = findZipExplorerNode
ExplorerNodes.fileOpenDlgProtReg.append('zip')
EditorHelper.modelReg[ZipFileModel.modelIdentifier] = ZipFileModel
EditorHelper.binaryFilesReg.append('.zip')

#-------------------------------------------------------------------------------

def isTarGzip(file):
    name, ext = os.path.splitext(file)
    return ext == '.tgz' or ext == '.gz' and os.path.splitext(name)[1] == '.tar'

class TarGzipController(ZipController): pass

class TarGzipInfoMixin:
    InfoClass = tarfile.TarInfo
    def newInfoClass(self, name):
        info = ZipItemNode.newInfoClass(self, name)
        info.filename = name
        if name[-1] == '/':
            info.type = tarfile.DIRTYPE
        return info

class TarGzipItemNode(TarGzipInfoMixin, ZipItemNode):
    protocol = 'tar.gz'
    ArchiveClass = tarfile.TarFileCompat


class TarGzipFileNode(TarGzipInfoMixin, ZipFileNode):
    protocol = 'tar.gz'
    ArchiveClass = tarfile.TarFileCompat
    ChildClass = TarGzipItemNode

    def isDir(self, path=''):
        if path:
            try: idx = self.allFileNames.index(path)
            except ValueError: return path[-1] == '/'
            return self.allFiles[idx].isdir()
        else:
            return False

EditorHelper.imgTarGzipFileModel = \
      EditorHelper.addPluginImgs('Images/Modules/TarGzipFile.png')
class TarGzipFileModel(EditorModels.EditorModel):
    modelIdentifier = 'TarGzipFile'
    defaultName = 'tar'
    bitmap = 'TarGzipFile.png'
    imgIdx = EditorHelper.imgTarGzipFileModel
    ext = '.gz'

def uriSplitTarGzip(filename, gzipfile, gzipentry):
    return 'tar.gz', gzipfile, gzipentry, filename

def uriSplitTGZ(filename, gzipfile, gzipentry):
    return 'tgz', gzipfile, gzipentry, filename

def findTarGzipExplorerNode(category, respath, transports):
    gzf = TarGzipFileNode(os.path.basename(category), category, None, -1, None, None)
    gzf.openList()
    return gzf.getNodeFromPath(respath)

#-------------------------------------------------------------------------------
# Register gzip files as a subtype of file explorers
FileExplorer.FileSysNode.subExplorerReg['file'].append(
      (TarGzipFileNode, isTarGzip, EditorHelper.imgZipFileModel))
ExplorerNodes.register(TarGzipItemNode, clipboard=ZipExpClipboard,
      controller=TarGzipController)
ExplorerNodes.uriSplitReg[('tar.gz', 3)] = uriSplitTarGzip
ExplorerNodes.uriSplitReg[('tgz', 3)] = uriSplitTGZ
ExplorerNodes.transportFindReg['tar.gz'] = findTarGzipExplorerNode
ExplorerNodes.transportFindReg['tgz'] = findTarGzipExplorerNode
ExplorerNodes.fileOpenDlgProtReg.extend(['tar.gz', 'tgz'])
EditorHelper.modelReg[TarGzipFileModel.modelIdentifier] = TarGzipFileModel
EditorHelper.binaryFilesReg.extend(['.gz', '.tgz'])
EditorHelper.extMap['.tgz'] = TarGzipFileModel
