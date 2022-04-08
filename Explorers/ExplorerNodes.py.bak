#-----------------------------------------------------------------------------
# Name:        ExplorerNodes.py
# Purpose:     Explorer base classes for nodes, controllers and companions
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Explorers.ExplorerNodes'

import sys, os, time, stat, copy, pprint
from ConfigParser import ConfigParser, NoOptionError

import wx

import Preferences, Utils
from Utils import _

from Models import EditorHelper
import scrm

sensitive_properties = ('passwd', 'scp_pass')

# Folderish objects are creators
# Folderish objects are connected to a clipboard and maintain their children

# XXX Active models open in the editors should be returned on list queries

# XXX define a filtering interface

# XXX remove 'parent' refs

# Guidelines
#  Creation of a node should be cheap and not significant resources
#  Opening/getting the contents/sublists should start connections/resources

# Accelerator shortcuts


class GlobalClipper:
    def __init__(self):
        self.currentClipboard = None

class ClipboardException(Exception):
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

class ExplorerClipboard:
    """ """
    # XXX Base class should implement recursive traversal by using explorer intf

    def __init__(self, globClip):
        self.globClip = globClip
        self.clipNodes = []
        self.clipMode = ''
    def clipCut(self, node, nodes):
        self.globClip.currentClipboard = self
        self.clipNodes = nodes
        self.clipMode = 'cut'
    def clipCopy(self, node, nodes):
        self.globClip.currentClipboard = self
        self.clipNodes = nodes
        self.clipMode = 'copy'
    def clipPaste_Default(self, destNode, sourceNodes, clipMode):
        for srcNode in sourceNodes:
            destName = destNode.resourcepath+'/'+srcNode.name
            newDestNode = destNode.getNodeFromPath(destName)
            newDestNode.save(destName, srcNode.load())
            if clipMode == 'cut':
                # XXX delete items
                pass
    def clipPaste(self, node):
        if self.globClip.currentClipboard:
            methName = 'clipPaste_'+self.globClip.currentClipboard.__class__.__name__
            if hasattr(self, methName):
                clipMeth = getattr(self, methName)
            else:
                clipMeth = self.clipPaste_Default
            clipMeth(node, self.globClip.currentClipboard.clipNodes,
                  self.globClip.currentClipboard.clipMode)

class Controller:
    Node = None

    plugins = ()
    def __init__(self, editor):
        self.editor = editor

        self.plugins = [Plugin(self, editor) for Plugin in self.plugins]

    def editorUpdateNotify(self, info=''):
        pass

    def setupMenu(self, menu, win, menus, addPlugins=True):
        pluginMenuDefs = []
        if addPlugins:
            for plugin in self.plugins:
                pluginMenuDefs.extend(plugin.menuDefs())

        for wId, help, method, bmp in menus + pluginMenuDefs:
            if help != '-':
                if help[0] == '+':
                    canCheck = True
                    help = help[1:]
                else:
                    canCheck = False

                if type(method) in (type(()), type([])):
                    subMenu = wx.Menu()
                    self.setupMenu(subMenu, win, method)
                    menu.AppendMenu(wId, help, subMenu)
                else:
                    menu.Append(wId, help, '', canCheck)
                    win.Bind(wx.EVT_MENU, method, id=wId)
                    self.editor.Bind(wx.EVT_MENU, method, id=wId)
            else:
                menu.AppendSeparator()

    def destroy(self):
        # break circular references here
        pass

    def groupToggleCheckMenu(self, menu, menuDef, wCheckId):
        checked = not menu.IsChecked(wCheckId)
        self.groupCheckMenu(menu, menuDef, wCheckId, checked)

    def groupCheckMenu(self, menu, menuDef, wCheckId, checked):
        for wId, help, method, bmp in menuDef:
            if wId == wCheckId:
                menu.Check(wId, checked)
            else:
                menu.Check(wId, not checked)

    def getName(self, item):
        if item.treename:
            return item.treename
        elif item.name:
            return item.name

    def getNamesForSelection(self, idxs):
        res = []
        for idx in idxs:
            res.append(self.getName(self.list.items[idx]))
        return res

    def getNodesForSelection(self, idxs):
        res = []
        for idx in idxs:
            res.append(self.list.items[idx])
        return res

    def createNode(self, category, name, resourcepath, uri):
        return self.Node(name, resourcepath, None, -1, None, None,
              properties = {})


(wxID_CLIPCUT, wxID_CLIPCOPY, wxID_CLIPPASTE, wxID_CLIPDELETE, wxID_CLIPRENAME,
 wxID_CLIPNEWFOLDER, wxID_CLIPNEWBLANKDOC, wxID_CLIPRELOAD, wxID_CLIPBOOKMARK,
 wxID_CLIPCOPYPATH, wxID_CLIPNEWMENU) = Utils.wxNewIds(11)

# XXX Maybe needs to be called StandardControllerMixin ??
class ClipboardControllerMix:
    cutBmp = 'Images/Shared/Cut.png'
    copyBmp = 'Images/Shared/Copy.png'
    pasteBmp = 'Images/Shared/Paste.png'
    deleteBmp = 'Images/Shared/Delete.png'
    bookmarkBmp = 'Images/Shared/Bookmark.png'
    def __init__(self):
        self.newMenuDef = [
         (wxID_CLIPNEWFOLDER, 'Folder', self.OnNewFolder, '-'),
         (wxID_CLIPNEWBLANKDOC, 'Blank document', self.OnNewBlankDoc, '-'),
        ]
        self.clipMenuDef = [ (wxID_CLIPRELOAD, _('Reload'), self.OnReloadItems, '-'),
         (-1, '-', None, '-'),
         (wxID_CLIPCUT, _('Cut'), self.OnCutItems, self.cutBmp),
         (wxID_CLIPCOPY, _('Copy'), self.OnCopyItems, self.copyBmp),
         (wxID_CLIPPASTE, _('Paste'), self.OnPasteItems, self.pasteBmp),
         (-1, '-', None, ''),
         (wxID_CLIPDELETE, _('Delete'), self.OnDeleteItems, self.deleteBmp),
         (wxID_CLIPRENAME, _('Rename'), self.OnRenameItems, '-'),
         (-1, '-', None, ''),
         (wxID_CLIPNEWMENU, _('New'), self.newMenuDef, '-'),
         (-1, '-', None, '-'),
         (wxID_CLIPBOOKMARK, _('Bookmark'), self.OnBookmarkItems, self.bookmarkBmp),
         (wxID_CLIPCOPYPATH, _('Copy path(s) to clipboard'), self.OnCopyPath, '-'),
        ]
    def destroy(self):
        self.clipMenuDef = []

    def OnCutItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            self.list.node.clipCut(nodes)

    def OnCopyItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            self.list.node.clipCopy(nodes)

    def OnPasteItems(self, event):
        if self.list.node:
            wx.BeginBusyCursor()
            try:
                self.list.node.clipPaste()
                self.list.refreshCurrent()
            finally:
                wx.EndBusyCursor()

    def OnDeleteItems(self, event):
        if self.list.node:
            wx.BeginBusyCursor()
            try:
                idxs = self.list.getMultiSelection()
                for item in self.getNodesForSelection(idxs):
                    self.editor.explorerDeleteNotify(item.getURI())
                names = self.getNamesForSelection(idxs)
                self.list.node.deleteItems(names)
                self.list.refreshCurrent()
            finally:
                wx.EndBusyCursor()

    def OnRenameItems(self, event):
        self.list.EditLabel(self.list.selected)

    def OnOpenItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if not node.isFolderish():
                    self.list.openNodeInEditor(node, self.editor,
                          self.editor.explorerStore.recentFiles)
                          #explorer.tree.recentFiles)


    def selectNewItem(self, name):
##        # XXX This is broken, select and rename somehow fires before internal
##        # XXX states are updated
##        return
        self.list.selectItemNamed(name)
        self.list.EnsureVisible(self.list.selected)
        self.list.EditLabel(self.list.selected)

    def OnNewFolder(self, event):
        if self.list.node:
            name = Utils.getValidName(self.list.getAllNames(), 'Folder')
            wx.BeginBusyCursor()
            try:
                self.list.node.newFolder(name)
            finally:
                wx.EndBusyCursor()
            self.list.refreshCurrent()
            self.selectNewItem(name)


    def OnNewBlankDoc(self, event):
        if self.list.node:
            name = Utils.getValidName(self.list.getAllNames(), 'BlankDoc')
            wx.BeginBusyCursor()
            try:
                self.list.node.newBlankDocument(name)
            finally:
                wx.EndBusyCursor()
            self.list.refreshCurrent()
            self.selectNewItem(name)

    def OnReloadItems(self, event):
        if self.list.node:
            self.list.refreshCurrent()

    def OnBookmarkItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if node.bookmarks:
                    node.bookmarks.add(node.getURI())
                    self.editor.statusBar.setHint(
                          _('Bookmarked %s')% node.resourcepath, 'Info')
            else:
                node = self.list.node
                if not nodes and node.bookmarks:
                    node.bookmarks.add(node.getURI())
                    self.editor.setStatus(_('Bookmarked %s')% node.getURI())

    def OnCopyPath(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            paths = []
            for node in nodes:
                paths.append(node.getURI())
            Utils.writeTextToClipboard(os.linesep.join(paths))

            self.editor.setStatus(_('Path(s) copied to clipboard'))

class TransportError(Exception):
    def __str__(self):
        try:
            return str(self.args[0])
        except:
            return str(self.args)

class TransportLoadError(TransportError):
    pass
class TransportSaveError(TransportError):
    pass
class TransportModifiedSaveError(TransportSaveError):
    pass

class TransportCategoryError(TransportError):
    def __init__(self, msg='', filepath=None):
        TransportError.__init__(self, msg, filepath)
        self.msg = msg
        self.filepath = filepath


    def __str__(self):
        if self.filepath:
            return '%s: %s' % (self.msg, self.filepath)
        else:
            return self.msg


class ExplorerNode:
    """ Base class for items in the explorer. """
    # Protocol identifier, used to associate with controller
    protocol = ''
    images = None
    viewMode = 'list'
    pathSep = '/'
    # Is it a stateless protocol or does it require a connection
    connection = False
    filter = ''
    # Should the node keep a reference to it's possible tree item
    refTree = False
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent=None, properties=None):
        self.name = name
        self.resourcepath = resourcepath
        self.imgIdx = imgIdx
        if properties is None: properties = {}
        self.properties = properties
        self.clipboard = clipboard
        self.parent = parent
        self.treename = name
        self.treeitem = None
        self.bold = False
        self.colour = None
        self.vetoRequery = False
        self.vetoSort = False
        self.upImgIdx = EditorHelper.imgFolderUp
        self.parentOpensChildren = False
        self.ignoreParentDir = False
        self.category = ''
        self.stdAttrs = {'size': 0,
                         'creation-date': 0.0,
                         'modify-date': 0.0,
                         'access-date': 0.0,
                         'read-only': 0}
##    def __del__(self): pass
##        print '__del__', self.__class__.__name__
    def destroy(self):pass
    def createParentNode(self): return self.parent
    def createChildNode(self, value): pass
    def openList(self): pass
    def closeList(self): pass
    def isFolderish(self): return False
    def getTitle(self):
        if self.resourcepath: return self.resourcepath
        else: return self.name
    def getURI(self):
        return '%s://%s%s'%(self.protocol, self.category, self.getTitle())
    def getDescription(self):
        return self.getURI()
    def notifyBeginLabelEdit(self, event):
        if event.GetLabel() == '..': event.Veto()
    def getNodeFromPath(self, respath):
        return None
    def setFilter(self, filter):
        pass
#---Default item actions--------------------------------------------------------
    def open(self, editor):
        return editor.openOrGotoModule(self.getURI(), transport = self)
    def openParent(self, editor): return False
    def checkOpenInEditor(self): return False

#---Methods on sub items--------------------------------------------------------
    def deleteItems(self, names): pass
    def renameItem(self, name, newName): pass
    def newFolder(self, name): pass
    def newBlankDocument(self, name): pass

#---Clipboard methods-----------------------------------------------------------
    def clipCut(self, nodes):
        self.clipboard.clipCut(self, nodes)
    def clipCopy(self, nodes):
        self.clipboard.clipCopy(self, nodes)
    def clipPaste(self):
        self.clipboard.clipPaste(self)

    def canAdd(self, paletteName):
        return False

#---Persistance (loading and saving)--------------------------------------------
    def assertFilename(self, filename):
        """ Utility function to strip and assert the protocol from the uri """
        from Explorers.Explorer import splitURI
        prot, cat, res, uri = splitURI(filename)
        assert self.protocol==prot, _('Illegal protocol change')
        return res
    def currentFilename(self):
        return self.assertFilename(self.getURI())

    def load(self, mode='r'):
        """ Return item data from appropriate transport """
        return None
    def save(self, filename, data, mode='w'):
        """ Persist data on appropriate transport. Should handle renames """
        pass
#---Standard attrs, read-only, mod date, create date, etc.----------------------
    def updateStdAttrs(self): pass
    def setStdAttr(self, attr, value): pass


#class NoneExplorerNode(ExplorerNode):
#    """ Represents an undefined transport. """
#    protocol = 'none'


class CachedNodeMixin:
    """ Only read from datasource when uninitialised or invalidated
        Not used yet
    """
    def __init__(self):
        self.valid = False
        self.cache = None

    def openList(self):
        if self.valid:
            return self.cache
        else:
            # define this method
            self.cache = self.openList_cache()

            self.valid = True
            return self.cache

class ContainerNode(ExplorerNode):
    protocol = 'fol'
    def __init__(self, name, imgIdx):
        ExplorerNode.__init__(self, name, '', None, imgIdx, None)
        self.entries = []
        self.vetoRequery = True
        self.vetoSort = True
    def destroy(self): pass
    def isFolderish(self): return True
    def createParentNode(self): return self
    def createChildNode(self, value): return value
    def openList(self): return self.entries
    def getTitle(self): return self.name
    def notifyBeginLabelEdit(self, event):
        event.Veto()

class RootNode(ContainerNode):
    protocol = 'root'
    def __init__(self, name, imgIdx=EditorHelper.imgBoaLogo):
        ContainerNode.__init__(self, name, imgIdx)

cat_section = 0
cat_option = 1
class CategoryNode(ExplorerNode):
    protocol = 'config'
    defName = 'config'
    defaultStruct = {}
    itemProtocol = ''
    entries = {}
    sharedEntries = {}
    def __init__(self, name, resourcepath, clipboard, config, parent, imgIdx=EditorHelper.imgFolder):
        ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, parent)
        self.config = config
        self.bold = True
        if not self.protocol in self.sharedEntries:
            self.sharedEntries[self.itemProtocol] = copy.copy(self.entries)
        self.entries = self.sharedEntries[self.itemProtocol]
        self.refresh()

    def destroy(self):
        pass

    def isFolderish(self):
        return True

    def getTitle(self):
        return self.name

    def getConfigValue(self):
        try:
            return eval(self.config.get(self.resourcepath[cat_section],
                        self.resourcepath[cat_option]), {})
        except NoOptionError, err:
            return self.entries

    def refresh(self):
        # Important: To keep the explorer list and the inspector in sync,
        #            the reference to self.entries should only be updated
        #            and not reassigned
        if type(self.entries) == type({}):
            self.entries.clear()
            self.entries.update(self.getConfigValue())
            # unscramble sensitive properties
            for item in self.entries.keys():
                if type(self.entries[item]) == type({}):
                    dict = self.entries[item]
                    for name in dict.keys():
                        if name in sensitive_properties:
                            dict[name] = scrm.scramble(dict[name])[2:]

    def openList(self):
        res = []
        entries = self.entries.keys()
        entries.sort()
        for entry in entries:
            node = self.createChildNode(entry, self.entries[entry])
            if node:
                res.append(node)
        return res

    def deleteItems(self, names):
        for name in names:
            try:
                del self.entries[name]
            except KeyError:
                wx.LogWarning(_('Could not find %s in %s for deletion')%(name,
                      self.entries.keys()))
        self.updateConfig()

    illegal_substrs = ('://', '::', '/', '\\')
    def renameItem(self, name, newName):
        for ill_substr in self.illegal_substrs:
            if newName.find(ill_substr) != -1:
                raise Exception, _('Contains invalid string sequence or char: "%s"')%ill_substr
        if newName in self.entries:
            raise Exception, _('Name exists')
        self.entries[newName] = self.entries[name]
        del self.entries[name]
        self.updateConfig()

    def newItem(self):
        name = Utils.getValidName(self.entries.keys(), self.defName)
        self.entries[name] = copy.copy(self.defaultStruct)
        self.updateConfig()
        return name

    def updateConfig(self):
        assert type(self.entries) is type(self.__class__.entries), \
               _('Entries type %s invalid, expected %s')%(str(type(self.entries)),
                                              str(type(self.__class__.entries)))
        self.config.set(self.resourcepath[cat_section],
                  self.resourcepath[cat_option], pprint.pformat(self.entries))
        Utils.writeConfig(self.config)

    def copyCatFrom(self, node):
        name = Utils.getValidName(self.entries.keys(), node.name or node.treename)
        self.entries[name] = copy.copy(node.properties)
        self.updateConfig()


(wxID_CATNEW, wxID_CATINSPECT, wxID_CATCOPY, wxID_CATDELETE, wxID_CATRENAME,
 wxID_CATRELOAD) = Utils.wxNewIds(6)

class CategoryController(Controller):
    newBmp = 'Images/Shared/NewItem.png'
    inspectBmp = 'Images/Shared/Inspector.png'
    deleteBmp = 'Images/Shared/Delete.png'

    copyBmp = 'Images/Shared/Copy.png'

    def __init__(self, editor, list, inspector, controllers, menuDefs = []):
        Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.Menu()
        self.inspector = inspector

        self.catMenuDef = [ (wxID_CATNEW, _('New'), self.OnNewItem, self.newBmp),
                            (wxID_CATINSPECT, _('Inspect'), self.OnInspectItem, self.inspectBmp),
                            (wxID_CATRELOAD, _('Reload'), self.OnReloadItems, '-'),
                            (-1, '-', None, ''),
                            (wxID_CATCOPY, _('Create copy'), self.OnCreateCopy, self.copyBmp),
                            (-1, '-', None, ''),
                            (wxID_CATDELETE, _('Delete'), self.OnDeleteItems, self.deleteBmp),
                            (wxID_CATRENAME, _('Rename'), self.OnRenameItem, '-') ]

        self.setupMenu(self.menu, self.list, self.catMenuDef + menuDefs)
        self.toolbarMenus = [self.catMenuDef + menuDefs]

    def destroy(self):
        self.catMenuDef = ()
        self.toolbarMenus = ()
        self.menu.Destroy()

    def OnInspectItem(self, event):
        if self.list.node:
            # Create new companion for selection
            catItem = self.list.getSelection()
            if not catItem: return
            catComp = self.list.node.createCatCompanion(catItem)
            catComp.updateProps()

            self.inspector.selectObject(catComp, False, focusPage=1, restore=True)

    def OnNewItem(self, event):
        if self.list.node:
            name = self.list.node.newItem()
            self.list.refreshCurrent()
            self.list.selectItemNamed(name)
            self.OnInspectItem(event)
            #self.list.EditLabel(self.list.selected)


    def OnDeleteItems(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            names = self.getNamesForSelection(ms)
            self.list.node.deleteItems(names)
            self.list.refreshCurrent()

    def OnRenameItem(self, event):
        self.list.EditLabel(self.list.selected)

    def OnReloadItems(self, event):
        if self.list.node:
            self.list.refreshCurrent()

    def OnCreateCopy(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                self.list.node.copyCatFrom(node)

            self.list.refreshCurrent()

class BookmarksCatNode(CategoryNode):
    """ Stores folderish references to any transport protocol """
    #protocol = 'config.bookmark'
    defName = _('Bookmark')
    defaultStruct = Preferences.explorerFileSysRootDefault[1]
    refTree = True
    def __init__(self, clipboards, config, parent, catTransports, tree=None,
          name=_('Bookmarks'), confSpec=('explorer', 'bookmarks')):
        CategoryNode.__init__(self, name, confSpec, None, config, parent)
        self.catTransports = catTransports
        self.tree = tree
        self.treeitem = None
        self.clipboards = clipboards
        self.imgIdx = EditorHelper.imgFolderBookmark

    def cleanup(self):
        self.catTransports = None
        self.tree = None
        self.clipboards = None

    def createChildNode(self, name, value):
        if type(value) == type({}):
            return SubBookmarksCatNode(self, name, value)
        else:
            from Explorers.Explorer import splitURI, getTransport, TransportError
            prot, cat, res, uri = splitURI(value)
            try:
                node = getTransport(prot, cat, res, self.catTransports)
            except TransportError:
                # XXX should return broken link items
                #print 'transport not found %s %s %s' %(prot, cat, res)
                return None
            if node.isFolderish():
                if prot == 'file':
                    node.imgIdx = EditorHelper.imgFSDrive
                elif prot == 'zope':
                    node.imgIdx = EditorHelper.imgZopeConnection
                else:
                    node.imgIdx = EditorHelper.imgNetDrive

            node.treename = name
            return node

    def getDefault(self):
        return self.config.get(self.resourcepath[0], 'defaultbookmark')

    def add(self, respath):
        respath=str(respath)
        if respath[-1] in ('/', '\\'):
            name = os.path.splitext(os.path.basename(respath[:-1]))[0]
        else:
            name = os.path.splitext(os.path.basename(respath))[0]
        if name in self.entries:
            name = Utils.getValidName(self.entries.keys(), name)
        self.entries[name] = respath
        self.updateConfig()

        self.refreshTree()

    def refreshTree(self):
        return
        # XXX if under bookmarks when adding bookmarks, tree is rebuilt and
        # XXX position in tree is lost
        # XXX At least update list when Bookmarks node is selected.

        #if self.tree and self.treeitem and self.treeitem.IsOk():
        #    if self.tree.IsExpanded(self.treeitem):
        #        self.tree.CollapseAndReset(self.treeitem)
        #        self.tree.Expand(self.treeitem)

    def createCatCompanion(self, catNode):
        return BookmarkCategoryStringCompanion(catNode.treename, self)

    def copyCatFrom(self, node):
        name = Utils.getValidName(self.entries.keys(), node.name or node.treename)
        self.entries[name] = node.resourcepath
        self.updateConfig()

class SubBookmarksCatNode(BookmarksCatNode):
    def __init__(self, parent, name, bookmarks):
        self._entries = bookmarks
        BookmarksCatNode.__init__(self, parent.clipboards, parent.config,
              parent, parent.catTransports, parent.tree)
        self.bold = False
        self.name = self.treename = name

    def refresh(self):
        self.entries = self._entries

    def getURI(self):
        return '%s/%s'%(self.parent.getURI(), self.name)

    def updateConfig(self):
        self.parent.updateConfig()

class MRUCatNode(BookmarksCatNode):
    protocol = 'recent.files'
    defName = _('Recent files')
    entries = []
    defaultStruct = ''
    def __init__(self, clipboards, config, parent, catTransports, tree):
        BookmarksCatNode.__init__(self, clipboards, config, parent,
              catTransports, tree, _('Recent files'), ('explorer', 'recentfiles'))
        self.vetoSort = True
        self.imgIdx = EditorHelper.imgRecentFiles
        self.ignoreParentDir = True

    def openList(self):
        res = []
        for entry in self.entries:
            try:
                node = self.createChildNode(entry)
            except Exception, err:
                node = None

            if node:
                res.append(node)
            else:
                self.entries.remove(entry)
        return res

    def add(self, respath):
        if respath in self.entries:
            self.entries.remove(respath)

        self.entries.insert(0, respath)

        if len(self.entries) > Preferences.exRecentFilesListSize:
            self.entries[Preferences.exRecentFilesListSize:] = []

        self.updateConfig()

        self.refreshTree()

    def createChildNode(self, fullpath):
        from Explorers.Explorer import splitURI, getTransport, TransportError
        prot, cat, res, uri = splitURI(fullpath)
        try:
            node = getTransport(prot, cat, res, self.catTransports)
        except TransportError:
            return None
        node.name = node.treename = fullpath
        return node

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def refresh(self):
        self.entries[:] = self.getConfigValue()

(wxID_MRUOPEN, wxID_MRURELOAD, wxID_MRUREMOVE) = Utils.wxNewIds(3)

class MRUCatController(Controller):
    deleteBmp = 'Images/Shared/Delete.png'

    def __init__(self, editor, list, inspector, controllers, menuDefs = []):
        Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.Menu()
        self.inspector = inspector

        self.mruMenuDef = [
            (wxID_MRUOPEN, _('Open'), self.OnOpenItems, '-'),
            (-1, '-', None, '-'),
            (wxID_MRURELOAD, _('Reload'), self.OnReloadItems, '-'),
            (-1, '-', None, ''),
            (wxID_MRUREMOVE, _('Remove'), self.OnRemoveItems, self.deleteBmp)
        ]

        self.setupMenu(self.menu, self.list, self.mruMenuDef + menuDefs)
        self.toolbarMenus = [self.mruMenuDef + menuDefs]

        self.recentItemsMenuIds = {}

    def destroy(self):
        self.mruMenuDef = ()
        self.toolbarMenus = ()
        self.menu.Destroy()

    def createRecentFilesMenu(self):
        # XXX not finished yet
        self.recentItemsMenuIds = {}
        menu = wx.Menu()
        for node in self.list.node.openList():
            if node.name not in self.recentItemsMenuIds.values():
                wid = wx.NewId()
                self.recentItemsMenuIds[wid] = node.name
                self.list.Bind(wx.EVT_MENU, self.OnMRUMenuItemSelect, id=wid)
            else:
                for wid, name in self.recentItemsMenuIds.items():
                    if name == node.name:
                        break
                else:
                    continue
            menu.Append(wid, node.name)
        return menu

    def OnOpenItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if not node.isFolderish():
                    node.open(self.editor)

    def OnReloadItems(self, event):
        if self.list.node:
            self.list.refreshCurrent()

    def OnRemoveItems(self, event):
        if self.list.node:
            names = self.list.getMultiSelection()
            names.sort()
            names.reverse()
            self.list.node.deleteItems(names)
            self.list.refreshCurrent()

    def OnMRUMenuItemSelect(self, event):
        wid = event.GetId()
        self.recentItemsMenuIds[wid]


#---Companions------------------------------------------------------------------

from Companions.BaseCompanions import Companion
from PropEdit.PropertyEditors import StrConfPropEdit, EvalConfPropEdit, PasswdStrConfPropEdit
import RTTI
import types

class ExplorerCompanion(Companion):
    def __init__(self, name):
        Companion.__init__(self, name)
        # list of (name, value) tuples
        self.propItems = []
        self.designer = None
        self.control = None
        self.mutualDepProps = ()
    def constructor(self):
        return {}
    def extraConstrProps(self):
        return {}
    def events(self):
        return ()
    def getEvents(self):
        return ()
    def getPropEditor(self, prop):
        return None
    def getPropOptions(self, prop):
        return ()
    def getPropNames(self, prop):
        return ()
    def checkTriggers(self, name, oldValue, value):
        pass
    def persistProp(self, name, setterName, value):
        pass
    def propIsDefault(self, name, setterName):
        return True
    def persistedPropVal(self, name, setterName):
        return ''

    def getPropList(self):
        propLst = []
        for prop in self.propItems:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
                  self.GetProp, self.SetProp))
        return {'constructor':[], 'properties': propLst}

    def findProp(self, name):
        for idx in range(len(self.propItems)):
            if self.propItems[idx][0] == name:
                return self.propItems[idx], idx
        else:
            return None, -1

    def GetProp(self, name):
        return self.findProp(name)[0][1]

    def SetProp(self, name, value):
        prop, idx = self.findProp(name)
        if self.setPropHook(name, value, prop):
            self.propItems[idx] = (name, value) + prop[2:]

    def GetClass(self, dummy=None):
        # XXX Add protocol from transport
        return 'Explorer Item'

    def SetClass(self, value):
        pass

    def updateProps(self):
        self.propItems = self.getPropertyItems()

    def addProperty(self, name, value, tpe):
        pass

    def delProperty(self, name):
        pass

    def setPropHook(self, name, value, oldProp = None):
        """ Override to do something before a property is set """
        pass

    def getPropertyItems(self):
        """ Override this to read the properties of the object, and return it

            Should return a list of tuples where the first two items are the
            property name and value, the rest of the items may store other
            propery information. """
        return []

class CategoryCompanion(ExplorerCompanion):
    """ Inspectable objects, driven from config files """
    propMapping = {type('') : StrConfPropEdit,
                   'password' : PasswdStrConfPropEdit,
                   'default': EvalConfPropEdit}
    try:
        propMapping[type(u'')] = StrConfPropEdit
    except:
        pass
    def __init__(self, name, catNode):
        ExplorerCompanion.__init__(self, name)
        self.catNode = catNode

    def getPropEditor(self, prop):
        if prop in sensitive_properties:
            return self.propMapping['password']
        else:
            return self.propMapping.get(type(self.GetProp(prop)), self.propMapping['default'])


class CategoryDictCompanion(CategoryCompanion):
    def getPropertyItems(self):
        return self.catNode.entries[self.name].items()

    def setPropHook(self, name, value, oldProp = None):
        # scramble sensitive properties before saving
        try:
            if not self.name in self.catNode.entries:
                raise Exception(_('%s not found in the config, renaming config '
                          'entries while Inspecting is not allowed.')%self.name)

            entry = self.catNode.entries[self.name]
            entry[name] = value

        finally:
            scrams = []
            for entry in self.catNode.entries.values():
                for key in entry.keys():
                    if key in sensitive_properties:
                        val = entry[key]
                        entry[key] = scrm.scramble(val)
                        scrams.append((entry, key, val))

            self.catNode.updateConfig()

            # unscramble sensitive properties
            for entry, key, val in scrams:
                entry[key] = val

        return True

class CategoryStringCompanion(CategoryCompanion):
    def getPropertyItems(self):
        return [ ('Item', self.catNode.entries[self.name]) ]

    def setPropHook(self, name, value, oldProp = None):
        self.catNode.entries[self.name] = value
        self.catNode.updateConfig()

class BookmarkCategoryStringCompanion(CategoryStringCompanion):
    def setPropHook(self, name, value, oldProp = None):
        if value == '{}': value = {}
        CategoryStringCompanion.setPropHook(self, name, value, oldProp)

def uriSplitNone(filename, filepath):
    return 'none', '', filepath, filename

#-Registry for explorer nodes-------------------------------------------------
# Successfully loaded modules from the
# Explorer.*.cfg [explorers] installedtransports import list are recorded here.
# Explorer Plug-ins bypassing the Explorer imports should add themselves
# to this list to have their controller classes hooked into the IDE
installedModules = []
# Dict of modules that failed to load, name: error
failedModules = {}

# Registry for language styles which can be edited under Preferences.Source
langStyleInfoReg = []
# Registry for extra protocols available in the file open dialog
fileOpenDlgProtReg = []
# Registry for splitting uris
uriSplitReg = {('none', 2): uriSplitNone}
# Registry for functions to locate connections
transportFindReg = {}

# Global reference to container for all transport protocols
# The first Explorer Tree created will define this
all_transports = None

# Main registries for ExplorerNode classes
explorerNodeReg = {}
nodeRegByProt = {}
# List of protocols that don't have Category nodes, and must be created
# at the top level of the tree
explorerRootNodesReg = []


def register(Node, clipboard=None, confdef=('', ''), controller=None,
             category=None, root=False):
    """ Register a new explorer Node.

    clipboard  : Clipboard class or protocol name (string) of existing clipboard
    confdef    : (section, option) tuple for the config file
    controller : Controller class or protocol name (string) of existing controller
    category   : Category node class for node when added as a transport to the tree
    root       : Non category/transport nodes can be installed in the tree root
    """

    explorerNodeReg[Node] = {'clipboard': clipboard, 'confdef': confdef,
                             'controller': controller, 'category': category}
    nodeRegByProt[Node.protocol] = Node

    if root:
        explorerRootNodesReg.append(Node.protocol)

def isTransportAvailable(conf, section, prot):
    return conf.has_option(section, prot) and (prot in nodeRegByProt)


#-------------------------------------------------------------------------------

register(CategoryNode, controller=CategoryController)
register(MRUCatNode, controller=MRUCatController)
