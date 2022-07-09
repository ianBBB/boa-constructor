#-----------------------------------------------------------------------------
# Name:        ZopeCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001/02/04
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing ZopeLib.ZopeCompanions'

import os

import wx

from Explorers.ExplorerNodes import ExplorerCompanion
from PropEdit.PropertyEditors import PropertyEditor
from PropEdit import InspectorEditorControls
import PaletteStore
import methodparse, RTTI

from ZopeLib import Client, ExtMethDlg
from ZopeLib.DateTime import DateTime

# XXX This creation logic should be in the model, the companions should only
# XXX manage prperties

#---Property editors------------------------------------------------------------

class ZopePropEdit(PropertyEditor):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx,
      width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion,
          propWrapper, idx, width)
    def initFromComponent(self):
        self.value = self.getCtrlValue()
    def persistValue(self, value):
        pass
##    def getCtrlValue(self):
##        return ''#self.getter(self.obj)
##    def getValue(self):
##        return ''
##    def setValue(self, value):
##        self.value = value


class EvalZopePropEdit(ZopePropEdit):
    def valueToIECValue(self):
        return `self.value`

    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.TextCtrlIEC(self, `self.value`)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = eval(self.editorCtrl.getValue(), {})
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class StrZopePropEdit(ZopePropEdit):
    def valueToIECValue(self):
        return self.value
#        return eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = self.editorCtrl.getValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class BoolZopePropEdit(ZopePropEdit):
    boolValMap = {'on': 'True', '': 'False', '1': 'True', '0': 'False'}
    boolKeyMap = {'true': 'on', 'false': ''}
    def valueToIECValue(self):
##        return self.boolValMap[self.value]
        if self.value:
            return self.value and self.getValues()[1] or self.getValues()[0]
        else:
            return self.getValues()[0]
    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.CheckBoxIEC(self, self.valueToIECValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.valueToIECValue())
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        return ['False', 'True']
    def getValue(self):
        if self.editorCtrl:
            self.value = self.boolKeyMap[self.editorCtrl.getValue().lower()]
##            if v == 'true'
##            self.value = self.getValues().index(self.editorCtrl.getValue())
        return self.value

class ReadOnlyZopePropEdit(ZopePropEdit):
    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.BevelIEC(self, str(self.value))
        self.editorCtrl.createControl(self.parent, self.idx, self.width)


#-------------------------------------------------------------------------------

class ZopeConnection:
    def connect(self, host, port, user, password):
#        self.svr = rpc.rpc_server(host, port, user, password)
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def parseInstanceListToTypeLst(self, instLstStr):
        instLstStr = instLstStr[1:-1]
        instLst = methodparse.safesplitfields(instLstStr, ',')
        tpeLst = []
        for inst in instLst:
            key, val = inst[1:-1].split(', ')
            val = val[1:].split(' ')[0]
            tpeLst.append( (key, val) )
        return tpeLst

    def call(self, objPath, method, **kw):
        try:
            wx.BeginBusyCursor()
            try:
                if objPath and objPath[0] != '/': objPath = '/'+objPath
                url = 'http://%s:%d%s/%s' % (self.host, self.port, objPath, method)
                return Client.call(*(url, self.user, self.password), **kw)
            finally:
                wx.EndBusyCursor()
        except Client.ServerError, rex:
            return None, rex

    def callkw(self, objPath, method, kw):
        try:
            wx.BeginBusyCursor()
            try:
                if objPath and objPath[0] != '/': objPath = '/'+objPath
                url = 'http://%s:%d%s/%s' % (self.host, self.port, objPath, method)
                return Client.call(*(url, self.user, self.password), **kw)
            finally:
                wx.EndBusyCursor()
        except Client.ServerError, rex:
            return None, rex

#---Companion classes for creating and inspecting Zope objects------------------

class ZopeCompanion(ExplorerCompanion, ZopeConnection):
    propMapping = {'string':          StrZopePropEdit,
                   'boolean':         BoolZopePropEdit,
                   'string:selection':StrZopePropEdit,
                   'default':         EvalZopePropEdit,
                   'readonly':        ReadOnlyZopePropEdit,}
    def __init__(self, name, objPath, localPath = ''):
        ExplorerCompanion.__init__(self, name)
        self.objPath = objPath
        self.localPath = localPath

    def getPropEditor(self, prop):
        return self.propMapping.get(self.getPropertyType(prop),
              self.propMapping['default'])

    def updateZopeProps(self):
        self.propItems = self.getPropertyItems()
        self.propMap = self.getPropertyMap()

    def getPropList(self):
        propLst = []
        for prop in self.propItems:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
                  self.GetProp, self.SetProp))
        return {'constructor':[], 'properties': propLst}

    def getObjectItems(self):
        mime, res = self.call(self.objPath, 'objectItems')
        return self.parseInstanceToTypeList(res)

    def getPropertyMap(self):
##        # [ {'id': <prop name>, 'type': <prop type>}, ... ]
        # This is a workaround for zope returning 2 prop map items incorrectly
        if len(self.propItems) == 2:
            mime, tpe1 = self.call(self.objPath, 'getPropertyType',
                  id=self.propItems[0][0])
            mime, tpe2 = self.call(self.objPath, 'getPropertyType',
                  id=self.propItems[1][0])
            return [ {'id': self.propItems[0][0], 'type': tpe1},
                     {'id': self.propItems[1][0], 'type': tpe2} ]
        else:
            mime, res = self.call(self.objPath, 'propertyMap')
            return eval(res, {})

    def getPropertyItems(self):
        # [ (<prop name>, <prop value>), ...]
        try:
            mime, res = self.call(self.objPath, 'propertyItems')
        except:
            #pass bci.
            return []
        return eval(res, {})

    def getPropertyType(self, name):
        for p in self.propMap:
            if p['id'] == name:
                if name == 'passwd':
                    return 'passwd'
                return p['type']
        return 'string'

    def setPropHook(self, name, value, oldProp):
        mime, res = self.callkw(self.objPath,
              'manage_changeProperties', {name: value})
        return True

    def addProperty(self, name, value, tpe):
        mime, res = self.call(self.objPath,
              'manage_addProperty', id=name, value=value, type = tpe)

    def delProperty(self, name):
        mime, res = self.call(self.objPath,
              'manage_delProperties', ids=[name])

class DTMLDocumentZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              'manage_addDTMLDocument', id = self.name)

class DTMLMethodZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              'manage_addDTMLMethod', id = self.name)

class FolderZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              'manage_addFolder', id = self.name)

class FileZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              'manage_addFile', id = self.name, file = '')

class ImageZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              'manage_addImage', id = self.name, file = '')

class CustomZopePropsMixIn:
    def getPropertyMap(self):
##        # [ {'id': <prop name>, 'type': <prop type>}, ... ]
        propMap = []
        for propName in self.propOrder:
            propMap.append( {'id': propName,
                             'type': self.propTypeMap[propName][0]} )
        return propMap

    def getPropertyItems(self):
        # [ (<prop name>, <prop value>), ...]
        propDict = self.getProps()
        propItems = []

        if self.propOrder is None:
            propOrder = propDict.keys()
            propOrder.sort()
        else:
            propOrder = self.propOrder

        for propName in propOrder:
            propItems.append( (propName, propDict[propName]) )
        return propItems

    def getPropertyType(self, name):
        return  self.propTypeMap[name][0]

class PythonScriptZC(CustomZopePropsMixIn, ZopeCompanion):
    def create(self):
        prodPath = '/manage_addProduct/PythonScripts/'
        mime, res = self.call(self.objPath, prodPath+'manage_addPythonScript',
              id=self.name, title='', params='', body='pass')

    def getProps(self):
        mime, res = self.call(self.objPath, 'document_src')
        props = {}
        lines = res.split('\n')[1:]
        cnt = 0
        for line in lines:
            cnt = cnt + 1
            line = line.strip()
            if line == '##':
                break
            pvt = line.find('=')
            name = line[2:pvt]
            if len(name) >5 and name[:5] == 'bind ':
                name = name[5:]
            value = line[pvt+1:]
            props[name] = value

        props['body'] = '/n'.join(lines[cnt:])

        return props

    def SetProp(self, name, value):
        props = self.getProps()
        props[name] = value

        if name == 'title':
            mime, res = self.call(self.objPath, 'ZPythonScriptHTML_editAction',
                REQUEST = '',
                title = props['title'],
                params = props['parameters'],
                body = props['body'])
        else:
            mime, res = self.call(self.objPath, 'ZBindingsHTML_editAction',
                name_context = props['context'],
                name_container = props['container'],
                name_m_self = props['script'],
                name_ns = props['namespace'],
                name_subpath = props['subpath'])

    propOrder = ('title', 'context', 'container', 'script', 'namespace', 'subpath')
    propTypeMap = {'title':     ('string', 'title'),
                   'context':   ('string', 'name_context'),
                   'container': ('string', 'name_container'),
                   'script':    ('string', 'name_m_self'),
                   'namespace': ('string', 'name_ns'),
                   'subpath':   ('string', 'name_subpath'),
                  }

class ExternalMethodZC(CustomZopePropsMixIn, ZopeCompanion):
    def create(self):
        prodPath = '/manage_addProduct/ExternalMethod/'
        dlg = ExtMethDlg.ExtMethDlg(None, self.localPath)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                mime, res = self.call(self.objPath,
                      prodPath+'manage_addExternalMethod',
                      id = self.name, title = '',
                      function = dlg.chFunction.GetValue(),
                      module = dlg.cbModule.GetValue())
        finally:
            dlg.Destroy()

    def getProps(self):
        path, name = os.path.split(self.objPath)
        mime, res = self.call(path, 'zoa/props/ExternalMethod', name=name)
        return eval(res, {})

    def SetProp(self, name, value):
        props = self.getProps()
        props[name] = value

        mime, res = self.call(self.objPath, 'manage_edit',
            title = props['title'],
            module = props['module'],
            function = props['function'])

    propOrder = ('title', 'module', 'function')
    propTypeMap = {'title':     ('string', 'title'),
                   'module':    ('string', 'module'),
                   'function':  ('string', 'function'),
                  }

class MailHostZC(CustomZopePropsMixIn, ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addMailHost', id=self.name)

    def getProps(self):
        mime, res = self.call(self.objPath, 'zoa/props/MailHost')
        return eval(res, {})

    def SetProp(self, name, value):
        props = self.getProps()
        if props[name] != value:
            props[name] = value
        else:
            return

        mime, res = self.call(self.objPath, 'manage_makeChanges',
              title=props['title'],
              smtp_host=props['smtp_host'],
              smtp_port=props['smtp_port'])

    propOrder = ('title', 'smtp_host', 'smtp_port')
    propTypeMap = {'title': ('string', 'title'),
                   'smtp_host': ('string', 'smtp_host'),
                   'smtp_port': ('int', 'smtp_port')}

class ZCatalogZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              'manage_addProduct/ZCatalog/manage_addZCatalog',
              id = self.name, title = '')

class SQLMethodZC(CustomZopePropsMixIn, ZopeCompanion):
    def create(self):
        dlg = wx.TextEntryDialog(None, 'Enter the Connection Id', 'Z SQL Method', '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                connId = dlg.GetValue()
                mime, res = self.call(self.objPath,
                    'manage_addProduct/ZSQLMethods/manage_addZSQLMethod',
                    id=self.name, title='', connection_id=connId,
                    arguments='', template='')
        finally:
            dlg.Destroy()

    def getProps(self):
        mime, res = self.call(self.objPath, 'zoa/props/SQLMethod')
        return eval(res, {})

    def SetProp(self, name, value):
        props = self.getProps()
        if props[name] != value:
            props[name] = value
        else:
            return

        if name in ('title', 'connection_id'):
            mime, res = self.call(self.objPath, 'manage_edit',
                title = props['title'],
                connection_id = props['connection_id'],
                arguments = props['arguments'],
                template = props['template'])
        else:
            mime, res = self.call(self.objPath, 'manage_advanced',
                max_rows = props['max_rows'],
                max_cache = props['max_cache'],
                cache_time = props['cache_time'],
                class_file = props['class_file'],
                class_name = props['class_name'])

    propOrder = ('title', 'connection_id', 'max_rows', 'max_cache',
                'cache_time', 'class_file', 'class_name')

    propTypeMap = {'title':           ('string', 'title'),
                   'connection_id':   ('string', 'connection_id'),
                   'arguments':       ('string', 'arguments'),
                   'max_rows':        ('int', 'max_rows'),
                   'max_cache':       ('int', 'max_cache'),
                   'cache_time':      ('int', 'cache_time'),
                   'class_file':      ('string', 'class_file'),
                   'class_name':      ('string', 'class_name'),}

class DBAdapterZC(CustomZopePropsMixIn, ZopeCompanion):
    def getProps(self):
        mime, res = self.call(self.objPath, 'zoa/props/DBAdapter')
        return eval(res, {})

    def SetProp(self, name, value):
        props = self.getProps()
        if props[name] != value:
            props[name] = value
        else:
            return

        mime, res = self.call(self.objPath, 'manage_edit',
            title = props['title'],
            connection_string = props['connection_string'],)

    propOrder = ('title', 'connection_string')

    propTypeMap = {'title':     ('string', 'title'),
                   'connection_string':   ('string', 'connection_string'),}

class GadflyDAZC(DBAdapterZC):
    def create(self):
        dlg = wx.TextEntryDialog(None, 'Enter the Data Source',
              'Z Gadfly DB Adapter', '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                connId = dlg.GetValue()
                mime, res = self.call(self.objPath, 'manage_addZGadflyConnection',
                      id=self.name, title='', connection=connId, check=1)
        finally:
            dlg.Destroy()

class VersionZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addProduct/OFSP/manage_addVersion',
              id = self.name, title = '')

class UserZC(CustomZopePropsMixIn, ZopeCompanion):
    def getProps(self):
        path, name = os.path.split(self.objPath)
        mime, res = self.call(path, 'zoa/props/User', name=name)
        return eval(res, {})

    def SetProp(self, name, value):
        pass

    def create(self):
        dlg = wx.TextEntryDialog(None, 'Enter the username:\n(The password will '\
              'be set to this username and\ncan be updated in the Inspector)',
              'New User', '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                username = dlg.GetValue()
                mime, res = self.call(self.objPath, 'manage_users',
                   submit='Add', name=username, password=username, confirm=username)
        finally:
            dlg.Destroy()

    propOrder = ('id', 'roles', 'domains')
    propTypeMap = {'id':     ('readonly', 'id'),
                   'roles':   ('readonly', 'roles'),
                   'domains': ('readonly', 'domains'),
                   #'passwd':    ('string', 'passwd'),
                  }

class UserFolderZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath, 'manage_addUserFolder')

class SiteErrorLogZC(CustomZopePropsMixIn, ZopeCompanion):
    def getProps(self):
        mime, res = self.call(self.objPath, 'zoa/props/SiteErrorLog')
        return eval(res, {})

    def SetProp(self, name, value):
        props = self.getProps()
        if props[name] != value:
            props[name] = value
        else:
            return

        mime, res = self.call(self.objPath, 'setProperties',
              keep_entries=props['keep_entries'],
              copy_to_zlog=props['copy_to_zlog'],
              ignored_exceptions=props['ignored_exceptions'])

    propOrder = ('keep_entries', 'copy_to_zlog', 'ignored_exceptions')
    propTypeMap = {'keep_entries': ('int', 'keep_entries'),
                   'copy_to_zlog': ('boolean', 'copy_to_zlog'),
                   'ignored_exceptions': ('default', 'ignored_exceptions')}

#---Palette registration--------------------------------------------------------

PaletteStore.paletteLists['Zope'].extend(['Folder', 'DTML Document', 'DTML Method',
      'External Method', 'Script (Python)',
      'File', 'Image', 'Mail Host', 'ZCatalog', 'User Folder', 'User', 'Version',
      'Z SQL Method', 'Z Gadfly Database Connection'] )

PaletteStore.compInfo.update({'DTML Document': ['DTMLDocument', DTMLDocumentZC],
    'DTML Method': ['DTMLMethod', DTMLMethodZC],
    'Folder': ['Folder', FolderZC],
    'File': ['File', FileZC],
    'Image': ['Image', ImageZC],
    'External Method': ['ExternalMethod', ExternalMethodZC],
    'Script (Python)': ['PythonScript', PythonScriptZC],
    'Mail Host': ['MailHost', MailHostZC],
    'ZCatalog': ['ZCatalog', ZCatalogZC],
    'Z SQL Method': ['SQLMethod', SQLMethodZC],
    'User Folder': ['UserFolder', UserFolderZC],
    'Version': ['Version', VersionZC],
    'Z Gadfly Database Connection': ['GadflyDA', GadflyDAZC],
    'User' : ['User', UserZC],
    'Site Error Log':['SiteErrorLog', SiteErrorLogZC],
})
