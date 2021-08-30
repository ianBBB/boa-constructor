#-----------------------------------------------------------------------------
# Name:        FileExplorer.py
# Purpose:     Classes for filesystem exploring
#
# Author:      Riaan Booysen
#
# Created:     2001/03/06
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print('importing Explorers.FileExplorer')

import os, time, stat, sys

import wx

import Preferences, Utils
from Utils import _

from . import ExplorerNodes
from Models import Controllers, EditorHelper
from PropEdit import PropertyEditors, InspectorEditorControls

class FileSysCatNode(ExplorerNodes.CategoryNode):
#    protocol = 'config.file'
    itemProtocol = 'file'
    defName, defaultStruct = Preferences.explorerFileSysRootDefault
    def __init__(self, clipboard, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, _('Filesystem'), ('explorer', 'file'),
              clipboard, config, parent)
        self.bookmarks = bookmarks

        if not self.entries and wx.Platform == '__WXMSW__':
            drives = {}
            for x in range(ord('C'), ord('Z')+1):
                driveName = '%s:\\'%(chr(x))
                if os.path.exists(driveName):
                    drives[driveName] = driveName

            self.entries = drives
            self.updateConfig()
            wx.LogMessage(_('%d drives added to the filesystem definition.')%len(drives))

    def createParentNode(self):
        return self.parent

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryStringCompanion(catNode.treename, self)
        return comp

    def createChildNode(self, entry, value, forceFolder=True):
        if forceFolder: Node = NonCheckPyFolderNode
        else: Node = FileSysNode

        node = Node(entry, value, self.clipboard, -1, self, self.bookmarks)
        if node.isFolderish():
            node.imgIdx = EditorHelper.imgFSDrive
        else:
            node.imgIdx = Controllers.identifyFile(value #localfs=node.filter == 'BoaFiles'
                                                  )[0].imgIdx
        return node

##    def newItem(self):
##        name = ExplorerNodes.CategoryNode.newItem()
##        self.entries[name] = copy.copy(self.defaultStruct)
##        self.updateConfig()
##        return name

    def renameItem(self, name, newName):
        if newName in self.entries:
            raise Exception(_('Name exists'))
        self.entries[newName] = newName
        del self.entries[name]
        self.updateConfig()

    def getNodeFromPath(self, respath, forceFolder=True):
        cn = self.createChildNode(os.path.basename(respath), respath, forceFolder)
        return cn


(wxID_FSOPEN, wxID_FSTEST, wxID_FSNEW, wxID_FSNEWFOLDER, wxID_FSCVS, wxID_FSSVN,
 wxID_FSBOOKMARK, wxID_FSFINDINFILES, wxID_FSFINDFILES, wxID_FSFILTERIMAGES,
 wxID_FSSETASCWD, wxID_FSNEWZIP, wxID_FSINSPECT,
) = Utils.wxNewIds(13)

(wxID_FSFILTER, wxID_FSFILTERBOAMODULES, wxID_FSFILTERSTDMODULES,
 wxID_FSFILTERINTMODULES, wxID_FSFILTERALLMODULES,
) = Utils.wxNewIds(5)

filterDescrOrd = ['BoaFiles', 'StdFiles', 'BoaIntFiles', 'ImageFiles', 'AllFiles']

filterDescr = {'BoaFiles': (_('Boa files'), wxID_FSFILTERBOAMODULES),
               'StdFiles': (_('Standard files'), wxID_FSFILTERSTDMODULES),
               'BoaIntFiles': (_('Internal files'), wxID_FSFILTERINTMODULES),
               'ImageFiles': (_('Image files'), wxID_FSFILTERIMAGES),
               'AllFiles': (_('All files'), wxID_FSFILTERALLMODULES)}

# XXX CVS and Zip support must also move to registering
class FileSysController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    bookmarkBmp = 'Images/Shared/Bookmark.png'
    findBmp = 'Images/Shared/Find.png'
    inspectBmp = 'Images/Shared/Inspector.png'

    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.Controller.__init__(self, editor)
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        self.editor = editor
        self.inspector = inspector

        self.list = list
##        if controllers.has_key('cvs'):
##            self.cvsController = controllers['cvs']
##        else:
##            self.cvsController = None

        self.menu = wx.Menu()

        self.fileMenuDef = [
              (wxID_FSOPEN, _('Open'), self.OnOpenItems, '-'),
              (-1, '-', None, ''),
              (wxID_FSINSPECT, _('Inspect'), self.OnInspectItem, self.inspectBmp),
              (-1, '-', None, ''),
        ] + self.clipMenuDef + [
              (wxID_FSSETASCWD, _('Set as os.cwd'), self.OnSetAsSysCwd, '-'),
              (-1, '-', None, ''),
              (wxID_FSFINDINFILES, _('Find'), self.OnFindFSItem, self.findBmp),
        ]

        if 'zip' in controllers:
            self.newMenuDef.append(
             (wxID_FSNEWZIP, _('Empty zip archive'), self.OnEmptyZipArchive, '-') )
        if 'tar.gz' in controllers:
            self.newMenuDef.append(
             (wxID_FSNEWZIP, _('Empty tar.gz archive'), self.OnEmptyTarGzipArchive, '-') )

        self.setupMenu(self.menu, self.list, self.fileMenuDef)

        filters = []
        for filter in filterDescrOrd:
            descr, wid = filterDescr[filter]
            filters.append( (wid, '+'+descr, self.OnFilterFSItems , '-') )

        self.fileFilterMenuDef = filters
        self.fileFilterMenu = wx.Menu()
        self.setupMenu(self.fileFilterMenu, self.list, self.fileFilterMenuDef, False)

        # Check default option
        self.fileFilterMenu.Check(wxID_FSFILTERBOAMODULES, True)

        self.menu.Append(wxID_FSFILTER, _('Filter'), self.fileFilterMenu)

        # XXX this should not be done here
        if 'cvs' in controllers:
            self.menu.Append(wxID_FSCVS, 'CVS', controllers['cvs'].fileCVSMenu)
        if 'svn' in controllers:
            self.menu.Append(wxID_FSSVN, 'SVN', controllers['svn'].fileSVNMenu)

        self.toolbarMenus = [self.fileMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.fileFilterMenuDef = []
        self.fileMenuDef = []
        self.toolbarMenus = []
        self.menu.Destroy()

    def OnTest(self, event):
        print((self.list.node.clipboard.globClip.currentClipboard))

    def OnFilterFSItems(self, event):
        evtid = event.GetId()
        self.groupCheckMenu(self.fileFilterMenu, self.fileFilterMenuDef, evtid, True)
        for filter in filterDescrOrd:
            descr, wid = filterDescr[filter]
            if wid == evtid:
                self.list.node.setFilter(filter)
                self.list.refreshCurrent()
                break

    def addFindResults(self, pattern, mapResults):
        """ mapResult is map of tuples in this form
            {'Module':  ('Line no', 'Col', 'Text'), ...}
        """
        nd = self.list.node
        if not isinstance( self.list.node, ResultsFolderNode ):
            self.list.node = ResultsFolderNode(_('Results'), nd.resourcepath,
                  nd.clipboard, -1, nd, nd.bookmarks)

        mapFindInFileCount = {}
        for oFindRes in list(mapResults.keys()):
            if len( mapResults[oFindRes] ):
                mapFindInFileCount[oFindRes] = len( mapResults[oFindRes] )
        self.list.node.results = map(None, list(mapFindInFileCount.values()),
                                           list(mapFindInFileCount.keys()) )
        self.list.node.lastSearch = pattern
        self.list.refreshCurrent()

    def OnFindFSItem(self, event):
        # XXX This is nasty, redesign
        self.list.addFindResults = self.addFindResults

        import FindReplaceDlg
        dlg = FindReplaceDlg.FindReplaceDlg(self.list, self.editor.finder, self.list, 0)
        dlg.SetWorkingFolder(self.list.node.resourcepath)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

    def OnSetAsSysCwd(self, event):
        node = self.list.getSelection()
        if node: path = node.resourcepath
        else: path  = self.list.node.resourcepath

        if os.path.isfile(path): path = os.path.split(path)[0]
        os.chdir(path)

        self.editor.setStatus(_('Updated os.cwd to %s')%path, ringBell=True)

    def OnEmptyZipArchive(self, event):
        # must move to zip
        files = os.listdir(self.list.node.resourcepath)
        newName = Utils.getValidName(files, 'archive', 'zip')
        import zipfile
        zipfile.ZipFile(os.path.join(self.list.node.resourcepath, newName), 'w',
              zipfile.ZIP_DEFLATED).close()

        self.list.refreshCurrent()
        self.list.selectItemNamed(newName)
        self.list.EnsureVisible(self.list.selected)

    def OnEmptyTarGzipArchive(self, event):
        pass

    def OnInspectItem(self, event):
        if self.list.node:
            item = self.list.getSelection()
            if item:
                comp = FileSysCompanion(item.name, item)
                comp.updateProps()
                self.inspector.selectObject(comp, False, focusPage=1)



class FileSysAttrPropEdit(PropertyEditors.PropertyEditor):
    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.BeveledLabelIEC(self,
              self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValue())

    def getDisplayValue(self):
        return self.value


class FileSysCompanion(ExplorerNodes.ExplorerCompanion):
    def __init__(self, name, fsNode):
        ExplorerNodes.ExplorerCompanion.__init__(self, name)
        self.fsNode = fsNode

    def getPropEditor(self, prop):
        return FileSysAttrPropEdit

    timeFmt = '%a, %d %b %Y %H:%M:%S'
    def getPropertyItems(self):
        res = []
        attrs = self.fsNode.stdAttrs

        for date in ('creation-date', 'modify-date', 'access-date'):
            value = attrs[date]
            if value:
                res.append( (date,
                             time.strftime(self.timeFmt, time.localtime(value))) )

        value = attrs['read-only']
        res.append( ('read-only', value and 'True' or 'False') )

        value = attrs['size']
        if value:
            res.append( ('size', str(value)) )

        return res


class FileSysExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        # XXX Delayed cut (delete on paste or move) should clear the clipboard
        # XXX or refresh clipboard with new paths and clear 'cut' mode
        for clipnode in nodes:
            if mode == 'cut':
                node.moveFileFrom(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFileFrom(clipnode)

    clipPaste_DefaultClipboard = clipPaste_FileSysExpClipboard

    def _genericFSPaste(self, node, nodes, mode):
        for other in nodes:
            other.copyToFS(node)

    def clipPaste_ZopeEClip(self, node, nodes, mode):
        # XXX Pasting a cut from Zope does not delete the cut items from Zope
        for zopeNode in nodes:
            zopeNode.downloadToFS(os.path.join(node.resourcepath, zopeNode.name))

    def clipPaste_FTPExpClipboard(self, node, nodes, mode):
        # XXX Pasting a cut from FTP does not delete the cut items from FTP
        for file in nodes:
            file.ftpConn.download(file.resourcepath,
                  os.path.join(node.resourcepath, file.name))

    clipPaste_SSHExpClipboard = _genericFSPaste
    clipPaste_ZipExpClipboard = _genericFSPaste
    clipPaste_DAVExpClipboard = _genericFSPaste

class FileSysNode(ExplorerNodes.ExplorerNode):
    protocol = 'file'
    filter = 'BoaFiles'
    lastSearch = ''
    subExplorerReg = {'file': [], 'folder': []}
    connection = False
    pathSep = os.sep
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent=None,
          bookmarks=None, properties={}):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent, properties or {})
        self.bookmarks = bookmarks
        self.exts = list(EditorHelper.extMap.keys()) + list(EditorHelper.inspectableFilesReg.keys())
        self.entries = []

        # XXX not used ?
        self.doCVS = True
        self.doZip = True
        self.allowedProtocols = ['*']
        self.updateStdAttrs()

    def destroy(self):
        self.entries = []

    def isDir(self):
        return os.path.isdir(self.resourcepath)

    def isFolderish(self):
        return self.isDir() or list(filter(lambda se, rp=self.resourcepath,
              ap=self.allowedProtocols : (ap == ['*'] or se[0].protocol in ap) and se[1](rp),
              self.subExplorerReg['file']))

    def createParentNode(self):
        parent = os.path.abspath(os.path.join(self.resourcepath, '..'))
        if parent[-2:] == '..':
            parent = parent[:-2]
        return FileSysNode(os.path.basename(parent), parent, self.clipboard,
                  EditorHelper.imgFolder, self, self.bookmarks)

    def createChildNode(self, file, filename = ''):
        if not filename:
            filename = os.path.join(self.resourcepath, file)

        ext = os.path.splitext(filename)[1].lower()
        exts, extSubTypes = self.getFilterExts()
        # Files
        if ('.*' in exts or ext in exts) and os.path.isfile(filename):
            for Other, otherIdFunc, imgIdx in self.subExplorerReg['file']:
                if '*' in self.allowedProtocols or \
                      Other.protocol in self.allowedProtocols:
                    if otherIdFunc(filename):
                        return 'fol', Other(file, filename, self.clipboard,
                              imgIdx, self, self.bookmarks)
            Model = Controllers.identifyFile(filename)[0]
            if ext in extSubTypes:
                for SubTypeModel in extSubTypes[ext]:
                    if issubclass(Model, SubTypeModel):
                        break
                else:
                    return '', None
            return 'mod', FileSysNode(file, filename, self.clipboard,
              Model.imgIdx, self, self.bookmarks, {})
              #{'datetime': time.strftime('%a %b %d %H:%M:%S %Y',
              #             time.gmtime(os.stat(filename)[stat.ST_MTIME]))})
        # Directories
        elif os.path.isdir(filename):
            for other, otherIdFunc, imgIdx in self.subExplorerReg['folder']:
                if self.filter == 'BoaFiles' and \
                  '*' in self.allowedProtocols or '*' in self.allowedProtocols or \
                      other.protocol in self.allowedProtocols:
                    if otherIdFunc(filename):
                        return 'fol', other(file, filename, self.clipboard,
                              imgIdx, self, self.bookmarks)
            return 'fol', FileSysNode(file, filename, self.clipboard,
                  EditorHelper.imgFolder, self, self.bookmarks)
        else:
            return '', None

    def openList(self):
        try:
            #----------------------------------------
            # A hack for locally-encoded filesystems:
            # We need to convert filesystem names
            # from local encoding to unicode
            if isinstance(self.resourcepath, str):
                # files = os.listdir(self.resourcepath.decode(
                #       sys.getfilesystemencoding()))
                from pathlib import Path
                files = os.listdir(
                    Path(self.resourcepath))
            else: # unicode or other
                files = os.listdir(self.resourcepath)
            #---------------------------------------- 
        except Exception as err:
            raise ExplorerNodes.TransportError(err)
        files.sort()
        entries = {'mod': [], 'fol': []}

        for file in files:
            tp, node = self.createChildNode(file)
            if node:
                entries[tp].append(node)

        self.entries = entries['fol'] + entries['mod']
        return self.entries

    def deleteItems(self, names):
        for name in names:
            path = os.path.join(self.resourcepath, name)
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)

    def renameItem(self, name, newName):
        oldfile = os.path.join(self.resourcepath, name)
        newfile = os.path.join(self.resourcepath, newName)
        os.rename(oldfile, newfile)

    def newFolder(self, name):
        os.mkdir(os.path.join(self.resourcepath, name))
        return name

    def newBlankDocument(self, name=''):
        newpath = os.path.join(self.resourcepath, name)
        if not os.path.exists(newpath):
            open(newpath, 'w').write(' ')
        return name

    def copyFileFrom(self, node):
        """ Copy node into self (only called for folders)"""
        import shutil
        if not node.isDir():
            if node.resourcepath == os.path.join(self.resourcepath, node.name):
                newNameBase = os.path.join(self.resourcepath, 'copy%s_of_'+node.name)
                num = ''
                while True:
                    newName = newNameBase%num
                    if os.path.exists(newName):
                        try: num = str(int(num) + 1)
                        except: num = '2'
                    else:
                        shutil.copy(node.resourcepath, newName)
                        break
            else:
                shutil.copy(node.resourcepath, self.resourcepath)
##                names = map(lambda n: n.name, self.entries)
##                dir, name = os.path.split(self.resourcepath)
##                name, ext = os.path.splitext(name)
##                name = Util.getValidName(names, name, ext)
##                shutil.copy(node.resourcepath, name)
##            else:
##            shutil.copy(node.resourcepath, self.resourcepath)
        else:
            shutil.copytree(node.resourcepath, os.path.join(self.resourcepath, node.name))

    def moveFileFrom(self, node):
        # Moving into directory being moved should not be allowed
        sp = os.path.normpath(node.resourcepath)
        dp = os.path.normpath(self.resourcepath)
        if dp[:len(sp)] == sp:
            raise Exception('Cannot move into itself')

        self.copyFileFrom(node)
        if not node.isFolderish():
            os.remove(node.resourcepath)
        else:
            import shutil
            shutil.rmtree(node.resourcepath)

    def setFilter(self, filter):
        self.__class__.filter = filter

    def getFilterExts(self):
        return {'BoaFiles': (self.exts, {}),
                'StdFiles': (self.exts, {}),
                'BoaIntFiles': (EditorHelper.internalFilesReg, {}),
                'ImageFiles': (EditorHelper.imageExtReg,
                               EditorHelper.imageSubTypeExtReg),
                'AllFiles': (['.*'], {})}.get(self.filter, (self.exts, {}))

    def load(self, mode='rb'):
        try:
            data = open(self.resourcepath, mode).read()
            self.updateStdAttrs()
            return data
        except IOError as error:
            raise ExplorerNodes.TransportLoadError(error, self.resourcepath)

    def save(self, filename, data, mode='wb', overwriteNewer=False):
        if self.resourcepath != filename:
            self.resourcepath = filename
            self.name = os.path.basename(self.resourcepath)
        try:
            if not overwriteNewer and self.fileIsNewer():
                raise ExplorerNodes.TransportModifiedSaveError(_('This file has '
                  'been saved by someone else since it was loaded'),
                  self.resourcepath)
            open(self.resourcepath, mode).write(data)
        except IOError as error:
            raise ExplorerNodes.TransportSaveError(error, self.resourcepath)
        self.updateStdAttrs()

    def getNodeFromPath(self, respath):
        name = os.path.basename(respath)
        return self.createChildNode(name, respath)

    def updateStdAttrs(self):
        exists = os.path.exists(self.resourcepath)
        self.stdAttrs['read-only'] = exists and \
              not os.access(self.resourcepath, os.W_OK)
        self.stdAttrs['modify-date'] = exists and \
              os.stat(self.resourcepath)[stat.ST_MTIME] or 0.0
        self.stdAttrs['creation-date'] = exists and \
              os.stat(self.resourcepath)[stat.ST_CTIME] or 0.0
        self.stdAttrs['access-date'] = exists and \
              os.stat(self.resourcepath)[stat.ST_ATIME] or 0.0
        self.stdAttrs['size'] = exists and \
              os.stat(self.resourcepath)[stat.ST_SIZE] or 0

    def setStdAttr(self, attr, value=None):
        if attr == 'read-only':
            os.chmod(self.resourcepath, value and 0o444 or 0o666)

        self.updateStdAttrs()

    def fileIsNewer(self):
        return (os.path.exists(self.resourcepath) and \
            os.stat(self.resourcepath)[stat.ST_MTIME] or 0.0) > \
            self.stdAttrs['modify-date']

class ResultsFolderNode(FileSysNode):
    results = []
    def openList(self):
        self.parentOpensChildren = True
        self.results.sort()
        self.results.reverse()
        entries = []

        for occrs, filename in self.results:
            tp, node = self.createChildNode('(%d) %s'%(occrs, filename),
                  os.path.join(self.resourcepath, filename))
            if node:
                entries.append(node)

        self.entries = entries
        return self.entries

    def openParent(self, editor):
        editor.explorer.tree.SelectItem(editor.explorer.tree.GetSelection())
        return True

    def open(self, node, editor):
        mod, cntrl = node.open(editor)
        view = mod.getSourceView()
        if view:
            view.doFind(self.lastSearch)
            view.doNextMatch()
        return mod, cntrl

    def getTitle(self):
        return _('Find results for %s in %s') % (self.lastSearch, self.resourcepath)

class NonCheckPyFolderNode(FileSysNode):
    def isFolderish(self):
        return True

class CurWorkDirNode(FileSysNode):
    protocol = 'os.cwd'
    def __init__(self, clipboard, parent, bookmarks):
        self.cwd = os.path.abspath(os.getcwd())
        FileSysNode.__init__(self, 'os.cwd', self.cwd, clipboard,
              EditorHelper.imgPathFolder, parent)
        self.bookmarks = bookmarks
        self.bold = True
        #self.setFilter('AllFiles')

    def openList(self):
        self.cwd = self.resourcepath = os.path.abspath(os.getcwd())
        return FileSysNode.openList(self)

    def getTitle(self):
        return 'os.cwd://%s'%self.cwd
    def getURI(self):
        return self.getTitle()

def uriSplitFile(filename, filepath):
    return 'file', '', filepath, filename

def findFileExplorerNode(category, respath, transports):
    for tp in transports.entries:
        if tp.itemProtocol == 'file':
            return tp.getNodeFromPath(respath, forceFolder=False)
    raise ExplorerNodes.TransportError(
          _('FileSysCatNode not found in transports %s')%transports.entries)

#-------------------------------------------------------------------------------
ExplorerNodes.register(FileSysNode, clipboard=FileSysExpClipboard,
      confdef=('explorer', 'file'), controller=FileSysController,
      category=FileSysCatNode)
ExplorerNodes.register(CurWorkDirNode, clipboard='file', controller='file',
      root=True)
ExplorerNodes.fileOpenDlgProtReg.append('file')
ExplorerNodes.uriSplitReg[('file', 2)] = uriSplitFile
ExplorerNodes.uriSplitReg[('os.cwd', 2)] = uriSplitFile
ExplorerNodes.transportFindReg['file'] = findFileExplorerNode
