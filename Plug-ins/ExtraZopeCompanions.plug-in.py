import wx

import Preferences, Utils, Plugins

if not Plugins.transportInstalled('ZopeLib.ZopeExplorer'):
    raise Plugins.SkipPlugin, 'Zope support is not enabled'

from ZopeLib.ZopeCompanions import ZopeCompanion, DBAdapterZC
from Models import EditorHelper, Controllers, XMLSupport, HTMLSupport
from ZopeLib import ZopeEditorModels

class PythonMethodZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              '/manage_addProduct/PythonMethod/manage_addPythonMethod',
              id=self.name, title='', params='', body='pass')

ZopeEditorModels.addZOAImage('Python Method', 'Images/ZOA/pymethod.png')
class ZopePythonMethodModel(ZopeEditorModels.ZopePythonSourceModel):
    modelIdentifier = 'ZopePythonMethod'
    defaultName = 'zopepythonmethod'
    bitmap = 'Module.png'
    imgIdx = ZopeEditorModels.ZOAIcons['Python Method']

Controllers.modelControllerReg[ZopePythonMethodModel] = ZopeEditorModels.ZopeController

class TransparentFolderZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              'manage_addProduct/TransparentFolder/manage_addTransparentFolder',
              id=self.name, title='')

class LocalFSZC(ZopeCompanion):
    def create(self):
        mime, res = self.call(self.objPath,
              'manage_addProduct/LocalFS/manage_addLocalFS',
              id=self.name, title='', basepath='')

from ZopeLib.ZopeExplorer import DirNode, ZopeConnection, zopeClassMap
from Views import PySourceView, SourceViews

class LFSNode(DirNode): pass
ZopeEditorModels.addZOAImage('Local File System', 'Images/ZOA/fs.png')

class LFNode(LFSNode):
    Model = ZopeEditorModels.ZopeEditorModel
    additionalViews = ()
    supportedViews = {'Module': (PySourceView.PythonSourceView,),
                      'HTML': (HTMLSupport.HTMLSourceView,),
                      'XML': (XMLSupport.XMLSourceView,),
                     }

    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, xmlrpcsvr,
          root, properties, metatype):
        Mod = Controllers.identifyFile(
              os.path.basename(resourcepath), localfs=False)[0]
        imgIdx = Mod.imgIdx
        self.defaultViews = self.supportedViews.get(Mod.modelIdentifier,
              (SourceViews.TextView,))

        LFSNode.__init__(self, name, resourcepath, clipboard, imgIdx,
              parent, xmlrpcsvr, root, properties, metatype)

    def load(self, mode='rb'):
        mode='rb'
        # XXX Can't seem to open with xml-rpc (use DAV for now)
        props = self.properties
        from ExternalLib.WebDAV.client import Resource
        r = Resource(('http://%(host)s:%(httpport)s/'+self.resourcepath) % props,
            props['username'], props['passwd'])
        return r.get().body

        #return self.getResource()()

    def save(self, filename, data, mode='wb'):
        mode='wb'
        props = self.properties
        zc = ZopeConnection()
        zc.connect(props['host'], props['httpport'],
                   props['username'], props['passwd'])
        from io import StringIO
        file = StringIO(data)
        dirname, file.name = os.path.split(filename)
        zc.callkw(dirname, 'manage_upload',
              {'file': file, 'Content-Type': 'multipart/form-data'} )

    def isFolderish(self):
        return False


class LFDirNode(LFSNode):
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, xmlrpcsvr,
          root, properties, metatype):
        LFSNode.__init__(self, name, resourcepath, clipboard,
              EditorHelper.imgFolder, parent, xmlrpcsvr, root, properties, metatype)

zopeClassMap.update({
      'Local File System': LFSNode,
      'LocalFS::directory': LFDirNode,
      'LocalFS::file': LFNode})

class ZODBCDAZC(DBAdapterZC):
    def create(self):
        dlg = wx.TextEntryDialog(None, 'Enter the Connection String',
              'Z ODBC DB Adapter', '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                connId = dlg.GetValue()
                mime, res = self.call(self.objPath, 'manage_addZODBCConnection',
                      id=self.name, title='', connection=connId, check=1)
        finally:
            dlg.Destroy()

ZopeEditorModels.addZOAImage('Z ODBC Database Connection', 'Images/ZOA/db.png')

import PaletteStore
PaletteStore.paletteLists['Zope'].extend(['Python Method',
      'LocalFS', 'Transparent Folder', 'ZODBCDA'] )
PaletteStore.compInfo.update({'Python Method': ['PythonMethod', PythonMethodZC],
    'LocalFS': ['LocalFS', LocalFSZC],
    'Transparent Folder': ['TransparentFolder', TransparentFolderZC],
    'ZODBCDA': ['ZODBCDA', ZODBCDAZC], })
