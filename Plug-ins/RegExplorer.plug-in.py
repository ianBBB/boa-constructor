#-----------------------------------------------------------------------------
# Name:        RegExplorer.py
# Purpose:     Classes for exploring the windows registry
#
# Author:      Riaan Booysen
#
# Created:     2001/06/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import string, os, sys

import wx

import Preferences, Utils, Plugins

from Explorers import ExplorerNodes
from Models import EditorModels, EditorHelper
import RTTI

try:
    import _winreg
except ImportError:
    raise Plugins.SkipPluginSilently ('Requires windows')

#---Explorer classes------------------------------------------------------------

wxID_REGOPEN, wxID_REGINSPECT = Utils.wxNewIds(2)

class RegController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wx.Menu()
        self.inspector = inspector

        self.setupMenu(self.menu, self.list,
              [ (wxID_REGOPEN, 'Open', self.OnOpenItems, '-'),
                (wxID_REGINSPECT, 'Inspect', self.OnInspectItem, '-'),
                (-1, '-', None, '') ] + self.clipMenuDef)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = ()
        self.menu.Destroy()

    def OnInspectItem(self, event):
        if self.list.node:
            # Create new companion for selection
            regItem = self.list.getSelection()
            regComp = RegCompanion(regItem.name, regItem)
            regComp.updateProps()

            # Select in inspector
            self.inspector.restore()
            if self.inspector.pages.GetSelection() != 1:
                self.inspector.pages.SetSelection(1)
            self.inspector.selectObject(regComp, False)


class RegCatNode(ExplorerNodes.CategoryNode):
    itemProtocol = 'reg'
    defName = 'Registry'
    defaultStruct = {'path': 'HKEY_LOCAL_MACHINE',
                     'computername': ''}
    def __init__(self, clipboard, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, 'Registry', ('explorer', 'reg'),
              clipboard, config, parent)
        self.bookmarks = bookmarks

    def createParentNode(self):
        return self

    def createChildNode(self, name, props):
        itm = RegItemNode(name, props, props['path'], self.clipboard,
              EditorHelper.imgFolder, self)
        itm.category = name
        itm.bookmarks = self.bookmarks
        return itm

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryDictCompanion(catNode.treename, self)
        return comp


class RegItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'reg'
    connection = False
    def __init__(self, name, props, resourcepath, clipboard, imgIdx, parent):
        if not resourcepath:
            resourcepath = '/'
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent, props)

        self.hkey = None

    def initHkey(self):
        if self.resourcepath.find('\\') == -1:
            key, subkey = self.resourcepath, None
        else:    
            key, subkey = str.split(self.resourcepath, '\\', 1)
        key =_winreg.__dict__[key]
        if self.properties['computername']:
            compName = self.properties['computername']
        else:
            compName = None

        #hdl = _winreg.ConnectRegistry(compName, )
        self.hkey = _winreg.CreateKey(key, subkey)


    def getURI(self):
        return '%s://%s' % (self.protocol, self.resourcepath)

    def isFolderish(self):
        return True

    def createChildNode(self, name, props):
        newname = os.path.join(self.resourcepath, name)
        #isFolder = tpe == 'key'
        item = RegItemNode(name, props, newname, self.clipboard,
              EditorHelper.imgFolder, self)
        item.category = self.category
        item.bookmarks = self.bookmarks
        return item

    def enumReg(self, func, key):
        idx = 0
        res = []
        #vals = []
        #for res, func in ((keys, _winreg.EnumKey), (vals, _winreg.EnumValue)):
        while 1:
            try: res.append(func(key, idx))
            except EnvironmentError: break
            else: idx = idx + 1
        return res

    def openList(self):
        self.initHkey()

        idx = 0
        res = []
        for skey in self.enumReg(_winreg.EnumKey, self.hkey):
            res.append(self.createChildNode(skey, self.properties))

        return res

    def deleteItems(self, names):
        pass

    def renameItem(self, name, newName):
        pass

    def load(self, mode='rb'):
        return ''

    def save(self, filename, data, mode='wb'):
        pass

    def newFolder(self, name):
        # add key
        pass

    def newBlankDocument(self, name):
        # add blank string
        pass

    def getNodeFromPath(self, respath):
        return self.createChildNode(respath, self.properties)


class RegExpClipboard(ExplorerNodes.ExplorerClipboard):
    pass

#---Companion classes-----------------------------------------------------------

from Companions.BaseCompanions import HelperDTC
from PropEdit import PropertyEditors
import RTTI
import types

class RegPropReaderMixin:
    propMapping = {'default': PropertyEditors.EvalConfPropEdit}
    def getPropEditor(self, prop):
        return self.propMapping.get(type(self.GetProp(prop)),
              self.propMapping['default'])

    def buildItems(self, items, propList):
        #print propList
        for name, value in propList:
            if not value: value = ''
            elif types.StringType is type(value[0]):
                value = value[0]

            items.append( (str.split(name, ':')[1], value) )
        return items

class RegCompanion(RegPropReaderMixin, ExplorerNodes.ExplorerCompanion):
    def __init__(self, name, regNode):
        ExplorerNodes.ExplorerCompanion.__init__(self, name)
        self.regNode = regNode

    def getPropertyItems(self):
        res = []
        self.regNode.initHkey()
        for name, val, tpe in self.regNode.enumReg(_winreg.EnumValue, self.regNode.hkey):
            res.append( (name, val) )
        return res

    def SetProp(self, name, value):
        raise 'Property editing not supported yet'


#-------------------------------------------------------------------------------
ExplorerNodes.register(RegItemNode, clipboard=RegExpClipboard,
      confdef=('explorer', 'reg'), controller=RegController, category=RegCatNode)
