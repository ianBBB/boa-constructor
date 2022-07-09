#-----------------------------------------------------------------------------
# Name:        EditorExplorer.py
# Purpose:
#
# Author:      Riaan Booysem
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
import os

import wx

import Preferences, Utils
from Utils import _

import ExplorerNodes
from Models import EditorHelper

[wxID_EDTGOTO, wxID_EDTRELOAD, wxID_EDTCLOSE, wxID_EDTCLOSEALL, wxID_EDTMOVEUP,
 wxID_EDTMOVEDOWN, wxID_EDTCOPYPATH] = Utils.wxNewIds(7)

class EditorController(ExplorerNodes.Controller):
    closeBmp = 'Images/Editor/Close.png'
    moveUpBmp = 'Images/Shared/up.png'
    moveDownBmp = 'Images/Shared/down.png'

    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.Menu()

        self.editorMenuDef = [
           (wxID_EDTGOTO, _('Goto'), self.OnGotoModel, '-'),
           (-1, '-', None, ''),
           (wxID_EDTRELOAD, _('Refresh'), self.OnReloadItems, '-'),
           (-1, '-', None, '-'),
           (wxID_EDTCLOSE, _('Close'), self.OnCloseModels, self.closeBmp),
           (wxID_EDTCLOSEALL, _('Close all'), self.OnCloseAllModels, '-'),
           (-1, '-', None, ''),
           (wxID_EDTMOVEUP, _('Move up'), self.OnMoveModelUp, self.moveUpBmp),
           (wxID_EDTMOVEDOWN, _('Move down'), self.OnMoveModelDown, self.moveDownBmp),
           (-1, '-', None, '-'),
           (wxID_EDTCOPYPATH, _('Copy filepath(s) to clipboard'), self.OnCopyPath, '-'),
        ]

        self.setupMenu(self.menu, self.list, self.editorMenuDef)
        self.toolbarMenus = [self.editorMenuDef]

    def destroy(self):
        self.editorMenuDef = ()
        self.toolbarMenus = ()
        self.menu.Destroy()

    def editorUpdateNotify(self, info=''):
        self.OnReloadItems()

    def OnReloadItems(self, event=None):
        if self.list.node:
            self.list.refreshCurrent()

    def OnCloseModels(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            for node in nodes:
                self.editor.closeModulePage(node.modulePage)

    def moveModel(self, node, idx, direc):
        page = self.editor.tabs.GetPage(idx)
        text = self.editor.tabs.GetPageText(idx)
        imgIdx = self.editor.tabs.GetPageImage(idx)
        self.editor.tabs.RemovePage(idx)
        self.editor.tabs.InsertPage(idx+direc, page, text, False, imgIdx)

        # swap the two tIdx's
        for modPage in self.editor.modules.values():
            if modPage.tIdx == idx:
                modPage.tIdx = idx + direc
            elif modPage.tIdx == idx + direc:
                modPage.tIdx = idx

        self.list.refreshCurrent()
        self.list.selectItemByIdx(idx+direc-1)

    def OnMoveModelUp(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only move 1 at a time'))
            else:
                node = nodes[0]
                idx = node.modulePage.tIdx
                if idx == 2:
                    wx.LogError(_('Already at the beginning'))
                else:
                    self.moveModel(node, idx, -1)

    def OnMoveModelDown(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only move 1 at a time'))
            else:
                node = nodes[0]
                idx = node.modulePage.tIdx
                if idx == self.editor.tabs.GetPageCount() -1:
                    wx.LogError(_('Already at the end'))
                else:
                    self.moveModel(node, idx, 1)

    def OnGotoModel(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only goto 1 at a time'))
            else:
                nodes[0].open(self.editor)

    def OnCopyPath(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            paths = []
            for node in nodes:
                paths.append(node.resourcepath)
            Utils.writeTextToClipboard(os.linesep.join(paths))

    def OnCloseAllModels(self, event):
        if self.list.node:
            for node in self.list.items:
                self.editor.closeModulePage(node.modulePage)

class OpenModelsNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.open-models'
    def __init__(self, editor, parent):
        ExplorerNodes.ExplorerNode.__init__(self, _('Editor'), '', None,
              EditorHelper.imgOpenEditorModels, None, {})
        self.editor = editor
        self.bold = True
        self.vetoSort = True

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return True

    def createChildNode(self, name, modulePage):
        return OpenModelItemNode(modulePage.updatePageName(), name, modulePage, self)

    def openList(self):
        res = []
        mods = []
        for name, modPage in self.editor.modules.items():
            mods.append( (modPage.tIdx, name, modPage) )

        mods.sort()
        for idx, name, modPage in mods:
            res.append(self.createChildNode(name, modPage))
        return res


class OpenModelItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.model'
    def __init__(self, name, resourcepath, modulePage, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None,
              modulePage.model.imgIdx, parent, {})
        self.modulePage = modulePage
        self.model = modulePage.model

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return False

    def open(self, editor):
        if not os.path.split(self.resourcepath)[0]:
            # unsaved, manually get info and switch to page
            modPage = editor.modules[self.resourcepath]
            modPage.focus()
            model = modPage.model
            ctrlr = editor.getControllerFromModel(model)
            return model, ctrlr
        else:
            return editor.openOrGotoModule(self.resourcepath)


class ModelViewItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.view'
    def __init__(self, name, model, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, '', None,
              EditorHelper.imgFolder, parent, {})
        self.model = model

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return True

    def openList(self):
        res = []
        for item in self.model.views[self.name].explore():
            res.append(ViewItemNode(item, '', None, -1, self, {}))
        return res

class ViewItemNode(ExplorerNodes.ExplorerNode):
    def open(self, editor):
        pass

#-------------------------------------------------------------------------------

wxID_NEWCREATE = wx.NewId()
class EditorNewController(ExplorerNodes.Controller):
    createBmp = 'Images/Editor/Close.png'

    def __init__(self, editor, list):
        ExplorerNodes.Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.Menu()

        self.editorMenuDef = ( (wxID_NEWCREATE, 'Create', self.OnCreate, '-'), )

        self.setupMenu(self.menu, self.list, self.editorMenuDef)
        self.toolbarMenus = [self.editorMenuDef]

    def destroy(self):
        self.editorMenuDef = ()
        self.toolbarMenus = ()
        self.menu.Destroy()

    def OnCreate(self, event):
        print 'Create'

class NewPaletteNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.new-palette'
    def __init__(self, editor, parent):
        ExplorerNodes.ExplorerNode.__init__(self, 'Editor', '', None,
              EditorHelper.imgOpenEditorModels, None, {})
        self.editor = editor
        self.bold = True
        self.vetoSort = True

    def isFolderish(self):
        return True

    def createChildNode(self, name, modulePage):
        return NewPaletteItemNode(modulePage.updatePageName(), name, modulePage, self)

    def openList(self):
        res = []
        mods = []
        for name, modPage in self.editor.modules.items():
            mods.append( (modPage.tIdx, name, modPage) )

        mods.sort()
        for idx, name, modPage in mods:
            res.append(self.createChildNode(name, modPage))
        return res


class NewPaletteItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'boa.new-item'
    def __init__(self, name, resourcepath, modulePage, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None,
              modulePage.model.imgIdx, parent, {})

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def isFolderish(self):
        return False

#-------------------------------------------------------------------------------
ExplorerNodes.register(OpenModelsNode, controller=EditorController)
