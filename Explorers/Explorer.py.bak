#----------------------------------------------------------------------
# Name:        Explorer.py
# Purpose:     Controls to explore and initialise different data sources
#
# Author:      Riaan Booysen
#
# Created:     2000/11/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

print 'importing Explorers'

from os import path
import os, sys
import time, glob, fnmatch
from types import ClassType

import wx

import Preferences, Utils
from Preferences import IS
from Utils import _

from Models import EditorHelper

import ExplorerNodes
from ExplorerNodes import TransportError, TransportLoadError, TransportSaveError
from ExplorerNodes import TransportCategoryError

#---Explorer utility functions--------------------------------------------------

def makeCategoryEx(protocol, name='', struct=None):
    """ """
    for cat in ExplorerNodes.all_transports.entries:
        if hasattr(cat, 'itemProtocol') and cat.itemProtocol == protocol:
            catName = cat.newItem()
            if name:
                cat.renameItem(catName, name)
            else:
                name = catName

            if struct:
                cat.entries[name].clear()
                cat.entries[name].update(struct)
                cat.updateConfig()

            return name

    raise TransportCategoryError, _('No category found for protocol %s')%protocol

def openEx(filename, transports=None):
    """ Returns a transport node for the given uri """
    prot, category, respath, filename = splitURI(filename)
    if transports is None and ExplorerNodes.all_transports:
        transports = ExplorerNodes.all_transports
    return getTransport(prot, category, respath, transports)

def listdirEx(filepath, extfilter = ''):
    """ Returns a list of transport nodes for given folderish filepath """
    return [n.treename for n in openEx(filepath).openList()
            if not extfilter or \
               os.path.splitext(n.treename)[1].lower() == extfilter]

# XXX Handle compound URIs by splitting on the first 2 :// and calling
# XXX splitURI again recursively ??
def splitURI(filename):
    protsplit = filename.split('://')
    # check FS (No prot defaults to 'file')
    if len(protsplit) == 1:
        return 'file', '', filename, 'file://'+filename
    else:
        itemLen = len(protsplit)
        if ExplorerNodes.uriSplitReg.has_key( (protsplit[0], itemLen) ):
            return ExplorerNodes.uriSplitReg[(protsplit[0], itemLen)]\
                   (*([filename]+protsplit[1:]))

        else:
            prot, filepath = protsplit
            idx = filepath.find('/')
            if idx == -1:
                raise TransportCategoryError(_('Category not found'), filepath)
            else:
                category, respath = filepath[:idx], filepath[idx+1:]
            return prot, category, respath, filename

def getTransport(prot, category, respath, transports):
    if ExplorerNodes.transportFindReg.has_key(prot):
        return ExplorerNodes.transportFindReg[prot](category, respath, transports)
    elif category:
        return findCatExplorerNode(prot, category, respath, transports)
    else:
        raise TransportError(_('Unhandled transport'), (prot, category, respath))


def findCatExplorerNode(prot, category, respath, transports):
    for cat in transports.entries:
        if hasattr(cat, 'itemProtocol') and cat.itemProtocol == prot:
            itms = cat.openList()
            for itm in itms:
                if itm.name == category or itm.treename == category:
                    # connect if not a stateless protocol
                    #if itm.connection:
                    #    itm.openList()
                    return itm.getNodeFromPath(respath)
    raise TransportError(_('Catalog transport could not be found: %s || %s')%(category, respath))

#-------------------------------------------------------------------------------

(wxID_PFE, wxID_PFT, wxID_PFL) = Utils.wxNewIds(3)

class BaseExplorerTree(wx.TreeCtrl):
    def __init__(self, parent, images):
        wx.TreeCtrl.__init__(self, parent, wxID_PFT, style=wx.TR_HAS_BUTTONS | wx.CLIP_CHILDREN)#|wxNO_BORDER)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnOpen, id=wxID_PFT)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnOpened, id=wxID_PFT)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnClose, id=wxID_PFT)
        self.SetImageList(images)
        self.itemCache = None

        self.buildTree()

    def buildTree(self):
        pass

    def destroy(self):
        pass

    def openDefaultNodes(self):
        rootItem = self.GetRootItem()
        self.SetItemHasChildren(rootItem, True)
        self.Expand(rootItem)
        return rootItem

    def getChildren(self):
        children = []
        selection = self.GetSelection()
        child, cookie = self.GetFirstChild(selection)
        while child.IsOk():
            children.append(child)
            child, cookie = self.GetNextChild(selection, cookie)
        return children

    def getChildrenNames(self):
        return [self.GetItemText(id) for id in self.getChildren()]

    def getChildNamed(self, node, name):
        if not node.IsOk():
            return None
        
        child, cookie = self.GetFirstChild(node)

        while child.IsOk() and self.GetItemText(child) != name:
            child, cookie = self.GetNextChild(node, cookie)
        return child

    def OnOpened(self, event):
        pass

    def OnOpen(self, event):
        item = event.GetItem()
        if self.IsExpanded(item): return
        data = self.GetPyData(item)
        hasFolders = True
        if data:
            wx.BeginBusyCursor()
            try:
                self.DeleteChildren(item)
                if self.itemCache:
                    lst = self.itemCache[:]
                else:
                    lst = data.openList()
                hasFolders = False
                for itm in lst:
                    if itm.isFolderish():
                        hasFolders = True
                        new = self.AppendItem(item, itm.treename or itm.name,
                              itm.imgIdx, -1, wx.TreeItemData(itm))
                        self.SetItemHasChildren(new, True)
                        if itm.bold:
                            self.SetItemBold(new, True)
                        if itm.refTree:
                            itm.treeitem = new
                        if itm.colour:
                            self.SetItemTextColour(new, itm.colour)
            finally:
                wx.EndBusyCursor()

        self.SetItemHasChildren(item, True)#hasFolders)

    def OnClose(self, event):
        item = event.GetItem()
        data = self.GetPyData(item)
        data.closeList()

def importTransport(moduleName):
    try:
        __import__(moduleName, globals())
    except ImportError, error:
        if Preferences.pluginErrorHandling == 'raise':
            raise
        wx.LogWarning(_('%s not installed: %s') %(moduleName, str(error)))
        ExplorerNodes.failedModules[moduleName] = str(error)
        return True
    else:
        ExplorerNodes.installedModules.append(moduleName)
        return False


class ExplorerStore:
    def __init__(self, editor):
        self._ref_all_transp = False

        conf = Utils.createAndReadConfig('Explorer')
        self.importExplorers(conf)

        # Create clipboards for all registered nodes
        self.clipboards = {'global': ExplorerNodes.GlobalClipper()}
        for Clss, info in ExplorerNodes.explorerNodeReg.items():
            Clip = info['clipboard']
            if type(Clip) is ClassType:
                self.clipboards[Clss.protocol] = Clip(self.clipboards['global'])

        # Root node and transports
        self.boaRoot = ExplorerNodes.RootNode('Boa Constructor')

        self.openEditorFiles = \
            ExplorerNodes.nodeRegByProt['boa.open-models'](editor, self.boaRoot)

        self.transports = ExplorerNodes.ContainerNode('Transport', EditorHelper.imgFolder)
        self.transports.entriesByProt = {}
        self.transports.bold = True

        if ExplorerNodes.all_transports is None:
            ExplorerNodes.all_transports = self.transports
            self._ref_all_transp = True

        self.recentFiles = ExplorerNodes.MRUCatNode(self.clipboards, conf, None,
            self.transports, self)

        self.bookmarks = ExplorerNodes.BookmarksCatNode(self.clipboards, conf,
            None, self.transports, self)

        self.pluginNodes = [
          ExplorerNodes.nodeRegByProt[prot](self.clipboards['file'], None, self.bookmarks)
          for prot in ExplorerNodes.explorerRootNodesReg]

        self.preferences = \
              ExplorerNodes.nodeRegByProt['boa.prefs.group'](self.boaRoot)

        assert self.clipboards.has_key('file'), _('File system transport must be loaded')

        # root level of the tree
        self.boaRoot.entries = [self.openEditorFiles, self.recentFiles, self.bookmarks,
              self.transports] + self.pluginNodes + [self.preferences]

        # Populate transports with registered node categories
        # Protocol also has to be defined in the explorer section of the config
        transport_order = eval(conf.get('explorer', 'transportstree'), {})
        for name in transport_order:
            for Clss in ExplorerNodes.explorerNodeReg.keys():
                if Clss.protocol == name:
                    Cat = ExplorerNodes.explorerNodeReg[Clss]['category']
                    if not Cat: break

                    Clip = ExplorerNodes.explorerNodeReg[Clss]['clipboard']
                    if type(Clip) == type(''):
                        clip = self.clipboards[Clip]
                    elif self.clipboards.has_key(Clss.protocol):
                        clip = self.clipboards[Clss.protocol]
                    else:
                        clip = None

                    confSect, confItem = ExplorerNodes.explorerNodeReg[Clss]['confdef']
                    if conf.has_option(confSect, confItem):
                        try:
                            cat = Cat(clip, conf, None, self.bookmarks)
                            self.transports.entries.append(cat)
                            self.transports.entriesByProt[Cat.itemProtocol] = cat
                        except Exception, error:
                            wx.LogWarning(_('Transport category %s not added: %s')\
                                   %(Cat.defName, str(error)))
                    break

    def importExplorers(self, conf):
        """ Import names defined in the config files to register them """
        installTransports = ['Explorers.PrefsExplorer', 'Explorers.EditorExplorer'] +\
              eval(conf.get('explorer', 'installedtransports'), {})

        warned = False
        for moduleName in installTransports:
            warned = warned | importTransport(moduleName)
        if warned:
            wx.LogWarning(_('One or more transports could not be loaded, if the problem '
                         'is not rectifiable,\nconsider removing the transport under '
                         'Preferences->Plug-ins->Transports. Click "Details"'))

    def initInstalledControllers(self, editor, list):
        """ Creates controllers for built-in, plugged-in and installed nodes
            in the order specified by installedModules """

        controllers = {}
        links = []
        for instMod in ['Explorers.ExplorerNodes', 'PaletteMapping'] + \
              ExplorerNodes.installedModules:
            for Clss, info in ExplorerNodes.explorerNodeReg.items():
                if Clss.__module__ == instMod and info['controller']:
                    Ctrlr = info['controller']
                    if type(Ctrlr) == type(''):
                        links.append((Clss.protocol, Ctrlr))
                    else:
                        controllers[Clss.protocol] = Ctrlr(editor, list,
                              editor.inspector, controllers)

        for protocol, link in links:
            controllers[protocol] = controllers[link]

        return controllers

    def destroy(self):
        if self._ref_all_transp:
            ExplorerNodes.all_transports = None

        self.transports = None
        self.clipboards = None
        self.bookmarks.cleanup()
        self.bookmarks = None
        self.boaRoot = None


class ExplorerTree(BaseExplorerTree):
    def __init__(self, parent, images, store):
        self.store = store
        BaseExplorerTree.__init__(self, parent, images)

    def buildTree(self):
        rootItem = self.AddRoot('', EditorHelper.imgBoaLogo, -1,
              wx.TreeItemData(self.store.boaRoot))

    def destroy(self):
        self.defaultBookmarkItem = None

    def openDefaultNodes(self):
        rootItem = BaseExplorerTree.openDefaultNodes(self)

        bktn = self.getChildNamed(rootItem, 'Bookmarks')
        self.Expand(bktn)

        trtn = self.getChildNamed(rootItem, 'Transport')
        self.Expand(trtn)

        self.defaultBookmarkItem = self.getChildNamed(bktn,
              self.store.bookmarks.getDefault())

class BaseExplorerList(wx.ListCtrl, Utils.ListCtrlSelectionManagerMix):
    def __init__(self, parent, filepath, pos=wx.DefaultPosition,
          size=wx.DefaultSize, updateNotify=None, style=0, menuFunc=None):
        wx.ListCtrl.__init__(self, parent, wxID_PFL, pos=pos, size=size,
              style=wx.LC_LIST | wx.LC_EDIT_LABELS | wx.CLIP_CHILDREN | style)
        Utils.ListCtrlSelectionManagerMix.__init__(self)

        self.filepath = filepath
        self.idxOffset = 0
        self.updateNotify = updateNotify
        self.node = None
        self.menuFunc = menuFunc

        self.selected = -1

        self.items = None
        self.currImages = None

        self._destr = False

        self.setLocalFilter()

    def destroy(self):
        if self._destr: return

        self.DeleteAllItems()

        if self.node:
            self.node.destroy()
        self.currImages = None
        self.items = None
        self.node = None
        self._destr = True

#    def EditLabel(self, index):
#        wx.Yield()
#
#        try: return wx.ListCtrl.EditLabel(self, index)
#        except AttributeError: return 0

    def getPopupMenu(self):
        return self.menuFunc()

#---Selection-------------------------------------------------------------------
    def selectItemNamed(self, name):
        for idx in range(self.GetItemCount()):
            item = self.GetItem(idx)
            if item.GetText() == name:
                item.SetState(wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)
                self.SetItem(item)
                self.EnsureVisible(idx)
                self.selected = idx
                return item

    def selectItemByIdx(self, idx):
        item = self.GetItem(idx)
        item.SetState(wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)
        self.SetItem(item)
        self.selected = idx
        return item

    def hasItemNamed(self, name):
        for idx in range(self.GetItemCount()):
            if self.GetItemText(idx) == name:
                return True
        return False

    def getAllNames(self):
        names = []
        for idx in range(self.GetItemCount()):
            name = self.GetItemText(idx)
            if name != '..':
                names.append(name)
        return names

    def getSelection(self):
        # XXX Fix, this can return IndexErrors !!!
        if self.selected >= self.idxOffset:
            return self.items[self.selected-self.idxOffset]
        else:
            return None

    def getMultiSelection(self):
        """ Returns list of indexes that map back to node list """
        res = []
        # if deselection occured, ignore item state and return []
        if self.selected == -1:
            return res
        for idx in range(self.idxOffset, self.GetItemCount()):
            if self.GetItemState(idx, wx.LIST_STATE_SELECTED):
                res.append(idx-self.idxOffset)
        return res

    def setLocalFilter(self, filter='*'):
        if glob.has_magic(filter):
            self.localFilter = filter
        else:
            self.localFilter = '*'

    def refreshCurrent(self):
        self.refreshItems(self.currImages, self.node)

    def refreshItems(self, images, explNode):
        """ Display ExplorerNode items """

        # Try to get the file listing before changing anything.
        self.selected = -1

        if self.node:
            self.node.destroy()

        self.node = explNode
        self.SetImageList(images, wx.IMAGE_LIST_SMALL)
        self.currImages = images

        # Setup a blank list
        self.DeleteAllItems()
        self.items = []
        self.InsertImageStringItem(self.GetItemCount(), '..', explNode.upImgIdx)

        wx.BeginBusyCursor()
        try: items = explNode.openList()
        finally: wx.EndBusyCursor()

        # Build a filtered, sorted list
        orderedList = []
        for itm in items:
            name = itm.treename or itm.name
            if itm.isFolderish() or fnmatch.fnmatch(name, self.localFilter):
                if Preferences.exCaseInsensitiveSorting:
                    sortName = name.lower()
                else:
                    sortName = name
                orderedList.append( (not itm.isFolderish(), sortName, name, itm) )
        if not explNode.vetoSort :
            orderedList.sort()

        # Populate the ctrl
        self.idxOffset = 1
        for dummy, dummy, name, itm in orderedList:
            self.items.append(itm)
            self.InsertImageStringItem(self.GetItemCount(), name, itm.imgIdx)

        self.filepath = explNode.resourcepath

        if self.updateNotify:
            self.updateNotify()

    def openNodeInEditor(self, item, editor, recentFiles):
        if self.node.parentOpensChildren:
            res = self.node.open(item, editor)
        else:
            res = item.open(editor)

        if res and len(res) == 2:
            mod, ctrlr = res

            if recentFiles and mod:
                recentFiles.add(mod.filename)

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex
        event.Skip()

    def OnItemDeselect(self, event):
        if not self.GetSelectedItemCount():
            self.selected = -1
        event.Skip()

class ExplorerList(BaseExplorerList):
    pass

class BaseExplorerSplitter(wx.SplitterWindow):
    def __init__(self, parent, modimages, editor, store,
          XList=ExplorerList, XTree=ExplorerTree):
        wx.SplitterWindow.__init__(self, parent, wxID_PFE,
              style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE)# | wxNO_3D | wxSP_3D)

        self.editor = editor
        self.store = store
        self.list, self.listContainer = self.createList(XList, '')
        self.modimages = modimages

        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnOpen, id=self.list.GetId())

        self.list.Bind(wx.EVT_LEFT_DOWN, self.OnListClick)

        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelect, id=wxID_PFL)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselect, id=wxID_PFL)

        self.tree, self.treeContainer = self.createTree(XTree, modimages)

        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.OnSelecting, id=wxID_PFT)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelect, id=wxID_PFT)

        self.controllers = self.initInstalledControllers()

        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit, id=wxID_PFL)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndLabelEdit, id=wxID_PFL)

        self.SplitVertically(self.treeContainer, self.listContainer,
              Preferences.exDefaultTreeWidth)

        self.SetMinimumPaneSize(self.GetSashSize())

        self.list.SetFocus()

    def createTree(self, XTree, modimages):
        tree = XTree(self, modimages, self.store)
        return tree, tree

    def createList(self, XList, name):
        list = XList(self, name, updateNotify=self.OnUpdateNotify,
              menuFunc=self.getMenu)
        return list, list

    def addTools(self, toolbar):
        if self.list.node and self.controllers.has_key(self.list.node.protocol):
            prot = self.list.node.protocol
            tbMenus = []
            for menuLst in self.controllers[prot].toolbarMenus:
                tbMenus.extend(list(menuLst))

            for wID, name, meth, bmp in tbMenus:
                if name == '-' and not bmp:
                    toolbar.AddSeparator()
                elif bmp != '-':
                    if name[0] == '+':
                        # XXX Add toggle button
                        name = name [1:]
                    Utils.AddToolButtonBmpObject(self.editor, toolbar,
                          IS.load(bmp), name, meth)

    def getMenu(self):
        if self.list.node and self.controllers.has_key(self.list.node.protocol):
            return self.controllers[self.list.node.protocol].menu
        else:
            return None

    def destroy(self):
        if not self.editor:
            return
        self.modimages = None
        self.list.Enable(False)
        self.list.destroy()
        self.tree.Enable(False)
        self.tree.destroy()
        unqDct = {}
        for contr in self.controllers.values():
            unqDct[contr] = None
        for contr in unqDct.keys():
            contr.destroy()
        self.controllers = None
        self.list = None
        self.editor = None

    def editorUpdateNotify(self):
        if self.list.node and self.controllers.has_key(self.list.node.protocol):
            self.controllers[self.list.node.protocol].editorUpdateNotify()

    def selectTreeItem(self, item):
        data = self.tree.GetPyData(item)
        title = self.tree.GetItemText(item)
        if data:
            imgs = data.images
            if not imgs: imgs = self.modimages
            self.list.refreshItems(imgs, data)
            title = data.getTitle()

        self.editor.SetTitle('%s - Explorer - %s' % (self.editor.editorTitle, title))

    def initInstalledControllers(self):
        return self.store.initInstalledControllers(self.editor, self.list)

    def OnUpdateNotify(self):
        tItm = self.tree.GetSelection()
        # XXX this should be smarter, only refresh on folderish name change
        # XXX add or remove
        if not self.selecting and self.tree.IsExpanded(tItm):
            self.tree.Collapse(tItm)
            self.tree.Expand(tItm)

        # XXX this is ugly :(
        # only update toolbar when the explorer is active
        if self.editor.tabs.GetSelection() == 1:
            self.editor.setupToolBar(1)

    def OnSelecting(self, event):
        self.selecting = True

    def OnSelect(self, event):
        # Event is triggered twice, work around with flag
        if self.selecting:
            item = event.GetItem()
            try:
                self.selectTreeItem(item)
            finally:
                self.selecting = False
                event.Skip()

    def OnOpen(self, event):
        tree, list = self.tree, self.list
        if list.selected != -1:
            name = list.GetItemText(self.list.selected)
            nd = list.node
            if name == '..':
                if not nd.openParent(self.editor):
                    treeItem = tree.GetItemParent(tree.GetSelection())
                    if treeItem.IsOk():
                        tree.SelectItem(treeItem)
            else:
##                if event and event.AltDown() and \
##                      self.controllers.has_key(list.node.protocol):
##                    ctrlr = self.controllers[list.node.protocol]
##                    if hasattr(ctrlr, 'OnInspectItem'):
##                        event.Skip()
##                        ctrlr.OnInspectItem(None)
##                        return
                item = list.items[list.selected-1]
                if item.isFolderish():
                    tItm = tree.GetSelection()
                    if not tree.IsExpanded(tItm):
                        tree.itemCache = self.list.items
                        try: tree.Expand(tItm)
                        finally: tree.itemCache = None
                    chid = tree.getChildNamed(tree.GetSelection(), name)
                    tree.SelectItem(chid)
                else:
                    list.openNodeInEditor(item, self.editor, self.store.recentFiles)

    def OnKeyPressed(self, event):
        key = event.GetKeyCode()
        if key == 13:
            self.OnOpen(event)
        else:
            event.Skip()

    def OnListClick(self, event):
        palette = self.editor.palette

        if palette.componentSB.selection and self.list.node and \
              self.list.node.canAdd(palette.componentSB.prevPage.name):
            name, desc, Compn = palette.componentSB.selection
            newName = self.list.node.newItem(name, Compn)
            try:
                self.list.refreshCurrent()
                self.list.selectItemNamed(newName)
            finally:
                palette.componentSB.selectNone()
        else:
            event.Skip()

    def OnBeginLabelEdit(self, event):
        self.oldLabelVal = event.GetText()
        if self.list.node:
            self.list.node.notifyBeginLabelEdit(event)

        if event.IsAllowed():
            event.Skip()

    def OnEndLabelEdit(self, event):
        newText = event.GetText()
        renameNode = self.list.getSelection()
        assert renameNode, _('There must be a selection to rename')
        oldURI = renameNode.getURI()
        if newText != self.oldLabelVal:
            event.Skip()
            try:
                self.list.node.renameItem(self.oldLabelVal, newText)
            except:
                wx.CallAfter(self.list.refreshCurrent)
                raise
            self.list.refreshCurrent()
            # XXX Renames on files with unsaved changes should have opt out
            # XXX Maybe load renamedNode from openEx
            self.list.selectItemNamed(newText)
            renamedNode = self.list.getSelection()
            # XXX Type changes and unknown types are not handled!
            if renamedNode:
                self.editor.explorerRenameNotify(oldURI, renamedNode)
        else:
            event.Skip()

    def OnItemSelect(self, event):
        self.list.OnItemSelect(event)
        if self.list.node:
            sel = self.list.getSelection()
            if not sel: sel = self.list.node
            self.editor.statusBar.setHint(sel.getDescription())

    def OnItemDeselect(self, event):
        self.list.OnItemDeselect(event)
        if self.list.node:
            self.editor.statusBar.setHint(self.list.node.getDescription())

    def OnSplitterDoubleClick(self, event):
        pass

class ExplorerSplitter(BaseExplorerSplitter): pass
