#-----------------------------------------------------------------------------
# Name:        DAVExplorer.py
# Purpose:     Classes for exploring DAV servers
#
# Author:      Riaan Booysen
#
# Created:     2001/06/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Explorers.DAVExplorer'

import os, sys
from xml.parsers import expat

import wx

#sys.path.append('..')
import ExplorerNodes
from Models import Controllers, EditorHelper
from ExternalLib.WebDAV import client
import RTTI, Utils
from Utils import _

# XXX Zope properties may contain invalid XML content strings (should be encoded)

class XMLListBuilder:
    def __init__(self, data):
        self.lists = []
        self.nodeStack = [self.lists]

        # Parse XML
        parser = expat.ParserCreate()

        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characterData

        try:
            xmlStart = data.find('<')
            if xmlStart == -1:
                raise Exception, _('Invalid XML response: %s') %str(data)
            xmlEnd = data.rfind('>')
            if xmlEnd == -1:
                raise Exception, _('Invalid XML response: %s') %str(data)
            self.status = parser.Parse(data[xmlStart:xmlEnd+1], 1)
        except:
            wx.MessageBox(Utils.html2txt(data), _('Error'), wx.ICON_ERROR)
            raise

    def startElement(self, name, attrs):
        #name = name.encode()
        id = []
        self.nodeStack[-1].append( (name, id) )
        self.nodeStack.append(id)

    def endElement(self, name):
        self.nodeStack = self.nodeStack[:-1]

    def characterData(self, data):
        if data.strip():
            #data = data.encode()
            self.nodeStack[-1].append(data)

#---Explorer classes------------------------------------------------------------

wxID_DAVOPEN, wxID_DAVINSPECT = Utils.wxNewIds(2)

class DAVController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wx.Menu()
        self.inspector = inspector

        self.setupMenu(self.menu, self.list,
              [ (wxID_DAVOPEN, _('Open'), self.OnOpenItems, '-'),
                (wxID_DAVINSPECT, _('Inspect'), self.OnInspectItem, '-'),
                (-1, '-', None, '') ] + self.clipMenuDef)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = ()
        self.menu.Destroy()

    def OnInspectItem(self, event):
        if self.list.node:
            # Create new companion for selection
            davItem = self.list.getSelection()
            davComp = DAVCompanion(davItem.name, davItem)
            davComp.updateProps()

            # Select in inspector
            self.inspector.selectObject(davComp, False, focusPage=1)


class DAVCatNode(ExplorerNodes.CategoryNode):
    itemProtocol = 'dav'
    defName = 'DAV'
    defaultStruct = {'username': '',
                     'passwd': '',
                     'host': 'localhost',
                     'port': '80',
                     'path': '/'}
    def __init__(self, clipboard, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, 'DAV', ('explorer', 'dav'),
              clipboard, config, parent)
        self.bookmarks = bookmarks

    def createParentNode(self):
        return self

    def createChildNode(self, name, props):
        itm = DAVItemNode(name, props, props['path'], self.clipboard,
              EditorHelper.imgNetDrive, self)
        itm.category = name
        itm.bookmarks = self.bookmarks
        return itm

    def createCatCompanion(self, catNode):
        comp = DAVCatDictCompanion(catNode.treename, self)
        return comp

class DAVCatDictCompanion(ExplorerNodes.CategoryDictCompanion):
    """ Prop validator for 'path' prop """
    def setPropHook(self, name, value, oldProp = None):
        ExplorerNodes.CategoryDictCompanion.setPropHook(self, name, value, oldProp)
        if name == 'path' and value and value != '/':
            if value[-1] != '/': raise Exception('DAV paths must end in "/"')
            if value[0] == '/': raise Exception('DAV paths shouldn\'t start with "/"')

class DAVItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'dav'
    connection = False
    def __init__(self, name, props, resourcepath, clipboard, imgIdx, parent):
        if not resourcepath:
            resourcepath = '/'
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent, props)
        self.initResource()

    def initResource(self):
        props = self.properties
        self.resource = client.Resource(('http://%(host)s:%(port)s/'%props)+\
              self.resourcepath, props['username'], props['passwd'])

    def getURI(self):
        return '%s://%s/%s' % (self.protocol, self.category, self.getTitle())

    def isFolderish(self):
        return self.resourcepath[-1] == '/'

    def createChildNode(self, name, props):
        if not name: name = '/'

        if name[-1] == '/':
            basename = os.path.basename(name[:-1])
            isFolder = True
        else:
            basename = os.path.basename(name)
            isFolder = False
        item = DAVItemNode(basename, props, name, self.clipboard,
              isFolder and EditorHelper.imgFolder or EditorHelper.imgTextModel, self)
        if not isFolder:
            item.imgIdx = \
                  Controllers.identifyFile(name, localfs=False)[0].imgIdx
        item.category = self.category
        item.bookmarks = self.bookmarks
        return item

    def openList(self):
        res = []
        resp = self.checkResp(self.resource.propfind('', 1))
        l = XMLListBuilder(resp.body).lists
        responses = l[0][1]
        if len(responses) > 0:
            for resp in l[0][1]:
                assert resp[1][0][0].strip().lower() == 'd:href',\
                      'Unexpected xml format'
                name = str(resp[1][0][1][0].strip())
                if len(name) > 1:
                    name = name[1:]
                    if name == self.resourcepath:
                        continue
                    res.append(self.createChildNode(name, self.properties))
        return res

    def copyFromFS(self, fsNode, fn=''):
        if fsNode.isFolderish():
            if not fn:
                fn = os.path.basename(fsNode.resourcepath[:-1])
            self.newFolder(fn)
        else:
            if not fn:
                fn = os.path.basename(fsNode.resourcepath)
            newNode = self.createChildNode(self.resourcepath+fn, self.properties)
            self.checkResp(newNode.resource.put(fsNode.load()))

    def copyToFS(self, fsFolderNode, fn=''):
        if self.isFolderish():
            if not fn:
                fn = os.path.basename(self.resourcepath[:-1])
            fsFolderNode.newFolder(fn)
        else:
            if not fn:
                fn = os.path.basename(self.resourcepath[:-1])
            open(os.path.join(fsFolderNode.resourcepath, fn), 'wb').write(self.load())

    def moveFileFrom(self, other):
        fn = os.path.basename(other.resourcepath)
        self.checkResp(other.resource.move(self.resourcepath + fn))

    def copyFileFrom(self, other):
        fn = os.path.basename(other.resourcepath)
        self.checkResp(other.resource.copy(self.resourcepath + fn))

    def deleteItems(self, names):
        absNames = []
        for name in names:
            self.checkResp(self.createChildNode(self.resourcepath+name,
                  self.properties).resource.delete())

    def renameItem(self, name, newName):
        self.checkResp(self.createChildNode(self.resourcepath+name,
            self.properties).resource.move(self.resourcepath+newName))

    def load(self, mode='rb'):
        try:
            return self.checkResp(self.resource.document_src.get()).body
        except Exception, error:
            raise ExplorerNodes.TransportLoadError(error, self.resourcepath)

    def save(self, filename, data, mode='wb', overwriteNewer=False):
        if filename != self.resourcepath:
            self.name = os.path.basename(filename)
            self.resourcepath = filename
            self.initResource()
        try:
            self.checkResp(self.resource.put(data))
        except Exception, error:
            raise ExplorerNodes.TransportSaveError(error, self.resourcepath)

    def newFolder(self, name):
        self.checkResp(self.createChildNode(self.resourcepath+name+'/',
              self.properties).resource.mkcol())

    def newBlankDocument(self, name):
        self.checkResp(self.createChildNode(self.resourcepath+name,
              self.properties).resource.put(' '))

    def getNodeFromPath(self, respath):
        return self.createChildNode(respath, self.properties)

    def checkResp(self, resp):
        assert resp.code < 300, '%s %d %s' %(resp.version, resp.code, resp.msg)
        return resp


class DAVExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        for clipnode in nodes:
            if mode == 'cut':
                node.copyFromFS(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFromFS(clipnode)

    def clipPaste_DAVExpClipboard(self, node, nodes, mode):
        for davNode in nodes:
            if mode == 'cut':
                node.moveFileFrom(davNode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFileFrom(davNode)

#---Companion classes-----------------------------------------------------------

from Companions.BaseCompanions import HelperDTC
from ExplorerNodes import ExplorerCompanion
from PropEdit import PropertyEditors
import RTTI
import types

class DAVContConfPropEdit(PropertyEditors.ContainerConfPropEdit):
    def getSubCompanion(self):
        return DAVSubCompanion

StringTypes = [types.StringType]
try: StringTypes.append(types.UnicodeType)
except: pass

class DAVPropReaderMixin:
    propMapping = {type(()) : DAVContConfPropEdit,
                   type([]) : DAVContConfPropEdit,
                   type('') : PropertyEditors.StrConfPropEdit,
                   'password' : PropertyEditors.PasswdStrConfPropEdit,
                   'default': PropertyEditors.EvalConfPropEdit}
    def getPropEditor(self, prop):
        return self.propMapping.get(type(self.GetProp(prop)),
              self.propMapping['default'])

    def buildItems(self, items, propList):
        #print propList
        for name, value in propList:
            if not value: value = ''
            elif type(value[0]) in StringTypes:
                value = str(value[0])

            items.append( (name.split(':')[1], value) )
        return items

class DAVCompanion(DAVPropReaderMixin, ExplorerCompanion):
    def __init__(self, name, davNode):
        ExplorerCompanion.__init__(self, name)
        self.davNode = davNode

    def getPropertyItems(self):
        l = XMLListBuilder(self.davNode.resource.getprops().body).lists

        items = []
        props = l[0][1][0][1]
        if len(props) > 1:
            for propSet in props[1:]:
                items = self.buildItems(items, propSet[1][0][1])
        return items

    def SetProp(self, name, value):
        raise Exception, _('Property editing not supported yet')

# XXX Helper is already slightly contaminated by the Designer
class DAVSubCompanion(DAVPropReaderMixin, HelperDTC):
    def __init__(self, name, designer, ownerCompanion, obj, ownerPropWrap):
        HelperDTC.__init__(self, name, designer, ownerCompanion, obj,
              ownerPropWrap)
        self.propItems = []

    def getPropList(self):
        propLst = []
        if type(self.obj) is types.ListType:
            props = self.obj
        else:
            props = [self.obj]
        subProps = self.buildItems([], props)
        for prop in subProps:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
                  self.GetProp, self.SetProp))
        self.propItems = subProps
        return {'constructor': [], 'properties': propLst}

    def GetProp(self, name):
        for prop in self.propItems:
            if prop[0] == name: return prop[1]

    def SetProp(self, name, value):
        raise Exception, _('Property editing not supported yet')

#-------------------------------------------------------------------------------
ExplorerNodes.register(DAVItemNode, clipboard=DAVExpClipboard,
      confdef=('explorer', 'dav'), controller=DAVController, category=DAVCatNode)
ExplorerNodes.fileOpenDlgProtReg.append('dav')
