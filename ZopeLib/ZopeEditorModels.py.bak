#-----------------------------------------------------------------------------
# Name:        ZopeEditorModels.py
# Purpose:     Models for Zope objects that can be opened in the Editor
#
# Author:      Riaan Booysen
#
# Created:     2001/06/04
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing ZopeLib.ZopeEditorModels'

import os

import wx

import Preferences, Utils
from Preferences import keyDefs

from Models import EditorModels, EditorHelper, HTMLSupport

def addZOAIcon(metatype):
    ZOAIcons[metatype] = EditorHelper.imgCounter
    EditorHelper.imgCounter = EditorHelper.imgCounter + 1
def addZOAImage(metatype, filepath):
    ZOAImages.append( (metatype, filepath) )
    addZOAIcon(metatype)

# meta-type to image index mapping
ZOAIcons = {}
# meta-type: filename mapping for ZOA imagelist
ZOAImages = [\
 ('root', 'Images/ZOA/Zope.png'),
 ('Folder', 'Images/ZOA/Folder.png'),
 ('DTML Document', 'Images/ZOA/dtmldoc.png'),
 ('Image', 'Images/ZOA/Image.png'),
 ('File', 'Images/ZOA/File.png'),
 ('Mail Host', 'Images/ZOA/MailHost.png'),
 ('User Folder', 'Images/ZOA/UserFolder_icon.png'),
 ('User', 'Images/ZOA/User_icon.png'),
 ('Version', 'Images/ZOA/version.png'),
 ('Control Panel', 'Images/ZOA/ControlPanel_icon.png'),
 ('Debug Information', 'Images/ZOA/DebugManager_icon.png'),
 ('Version Management', 'Images/ZOA/VersionManagement_icon.png'),
 ('Database Management', 'Images/ZOA/DatabaseManagement_icon.png'),
 ('Product Help', 'Images/ZOA/ProductHelp_icon.png'),
 ('Help Topic', 'Images/ZOA/HelpTopic_icon.png'),
 ('Product Management', 'Images/ZOA/ProductFolder_icon.png'),
 ('Product', 'Images/ZOA/InstalledProduct_icon.png'),
 ('Z Class', 'Images/ZOA/ZClass_Icon.png'),
 ('Zope Factory', 'Images/ZOA/Factory_icon.png'),
 ('Zope Permission', 'Images/ZOA/Permission_icon.png'),
 ('Base Class', 'Images/ZOA/BaseClass.png'),
 ('Aggregation', 'Images/ZOA/attribute.png'),
 ('Broken Because Product is Gone', 'Images/ZOA/broken.png'),
 ('unknown', 'Images/ZOA/unknown.png'),
 ('Script (Python)', 'Images/ZOA/PythonScript.png'),
 ('External Method', 'Images/ZOA/extmethod.png'),
 ('DTML Method', 'Images/ZOA/dtmlmethod.png'),
 ('Z SQL Method', 'Images/ZOA/sqlmethod.png'),
 ('common', 'Images/ZOA/common.png'),
 ('Z Gadfly Database Connection', 'Images/ZOA/db.png'),
 ('ZCatalog', 'Images/ZOA/ZCatalog.png'),
 ('Vocabulary', 'Images/ZOA/Vocabulary.png'),
 ('WebDAV Lock Manager', 'Images/ZOA/davlocked.png'),
 ('Browser Id Manager', 'Images/ZOA/idmgr.png'),
 ('Session Data Manager', 'Images/ZOA/datamgr.png'),
 ('Site Error Log', 'Images/ZOA/error.png'),
 ('Temporary Folder', 'Images/ZOA/tempfolder.png'),
 ('BoaDebugger', 'Images/ZOA/boa.png'),
# ('CMF Site', 'Images/ZOA/portal.png'),
# ('Plone Site', 'Images/ZOA/plone_icon.png'),
]

EditorHelper.imgZopeExportFileModel = EditorHelper.imgCounter
EditorHelper.imgCounter = EditorHelper.imgCounter + 1

for m_type, file in ZOAImages:
    addZOAIcon(m_type)

class ZopeEditorModel(EditorModels.BasePersistentModel):
    modelIdentifier = 'Zope'
    def __init__(self, data, name, editor, saved, zopeObject):
        EditorModels.BasePersistentModel.__init__(self, data, name, editor, saved)
        self.transport = zopeObject  #this is the instance of our node now

    def load(self, notify = True):
        EditorModels.BasePersistentModel.load(self, notify)

        self.modified = False
        self.savedAs = True
        self.saved = True

    def save(self, overwriteNewer=False):
        """ This is perhaps not the best style, but here all exceptions
            on saving are caught and transformed to TransportSaveErrors.
            To much maintenance for every Node type to add exceptions
        """
        from ExternalLib.xmlrpclib import Fault
        try:
            EditorModels.BasePersistentModel.save(self, overwriteNewer)
        except Fault, err:
            from Explorers import ExplorerNodes
            raise ExplorerNodes.TransportSaveError(Utils.html2txt(err.faultString),
                self.transport.resourcepath)

class ZopeBlankEditorModel(ZopeEditorModel):
    """ Objects which are not loaded and saved and does not have a 'Main' view,
        but which should still be able to host views """
    def load(self, notify = True):
        self.modified = False
        self.savedAs = True
        self.saved = True
    def getPageName(self):
        if self.filename[-1] == '/':
            return os.path.basename(self.filename[:-1])
        else:
            return ZopeEditorModel.getPageName(self)


class ZopeDocumentModel(ZopeEditorModel):
    modelIdentifier = 'ZopeDocument'
    defaultName = 'zopedoc'
    bitmap = 'Package.png'

    saveBmp = 'Images/Editor/Save.png'

    def __init__(self, data, name, editor, saved, zopeObject):
        ZopeEditorModel.__init__(self, data, name, editor, saved, zopeObject)
        self.savedAs = True

    def saveAs(self, filename):
        raise Exception, 'Save as not supported'

    def getPageName(self):
        if self.transport.name == 'index_html':
            return '%s (%s)' % (self.transport.name,
                  self.transport.resourcepath.split('/')[-2])
        else:
            return self.transport.name

class ZopeDTMLDocumentModel(ZopeDocumentModel):
    imgIdx = ZOAIcons['DTML Document']

class ZopeDTMLMethodModel(ZopeDocumentModel):
    imgIdx = ZOAIcons['DTML Method']

class ZopeSQLMethodModel(ZopeDocumentModel):
    imgIdx = ZOAIcons['Z SQL Method']

class ZopePythonSourceModel(ZopeDocumentModel):
    modelIdentifier = 'ZopePythonSource'
    def __init__(self, data, name, editor, saved,  zopeObject):
        ZopeDocumentModel.__init__(self, data, name, editor, saved,  zopeObject)
        self._module = None

    def getModule(self):
        if self._module is None:
            import moduleparse
            wx.BeginBusyCursor()
            try:
                self._module = moduleparse.Module(
                    self.transport.whole_name, self.data.split('\012'))
            finally:
                wx.EndBusyCursor()
        return self._module

class ZopePythonScriptModel(ZopePythonSourceModel):
    modelIdentifier = 'ZopePythonScript'
    defaultName = 'zopepythonscript'
    bitmap = 'Package.png'
    imgIdx = ZOAIcons['Script (Python)']

class ZopeExternalMethodModel(ZopePythonSourceModel):
    modelIdentifier = 'ZopeExternalMethod'
    defaultName = 'zopeexternalmethod'
    bitmap = 'Package.png'
    imgIdx = ZOAIcons['External Method']

    def getModule(self):
        if self._module is None:
            self.moduleName = self.transport.resourcepath
        return ZopePythonSourceModel.getModule(self)

#class ZopeLocalFSFileModel(ZopeEditorModel):

class ZopeSiteErrorLogModel(ZopeBlankEditorModel):
    modelIdentifier = 'ZopeSiteErrorLog'
    defaultName = 'zopesiteerrorlog'
    imgIdx = ZOAIcons['Site Error Log']

class ZopeHelpTopicModel(ZopeBlankEditorModel):
    modelIdentifier = 'ZopeHelpTopic'
    defaultName = 'zopehelptopic'
    imgIdx = ZOAIcons['Help Topic']


class ZopeExportFileModel(EditorModels.BasePersistentModel):
    modelIdentifier = 'ZopeExport'
    defaultName = 'zexp'
    bitmap = 'ZopeExport.png'
    global EditorHelper
    imgIdx = EditorHelper.imgZopeExportFileModel
    ext = '.zexp'
    fileModes = ('rb', 'wb')

EditorHelper.modelReg[ZopeExportFileModel.modelIdentifier] = ZopeExportFileModel
EditorHelper.extMap[ZopeExportFileModel.ext] = ZopeExportFileModel
EditorHelper.extMap['.dtml'] = HTMLSupport.HTMLFileModel

#-Controllers------------------------------------------------------------------
from Models import Controllers

class ZopeExportFileController(Controllers.UndockedController):
    Model = ZopeExportFileModel
    DefaultViews = []
    AdditionalViews = []
    def __init__(self, editor):
        Controllers.UndockedController.__init__(self, editor)

    def display(self, model):
        from Explorers import ExplorerNodes
        transports = ExplorerNodes.all_transports
        for cat in transports.entries:
            if cat.itemProtocol == 'zope':
                itms = cat.openList()
                localZopes = {}
                for itm in itms:
                    lp = itm.properties['localpath']
                    if lp: localZopes[itm.treename] = itm.properties
                if not localZopes:
                    wx.MessageBox('''No locally reachable Zopes found.
(Hint: Set the localpath property of the Zope connection)''')
                else:
                    dlg = wx.SingleChoiceDialog(self.editor,
                        "To which Zope's import directory should this file be copied?",
                        'Choose Zope instance', localZopes.keys())
                    try:
                        if dlg.ShowModal() == wx.ID_OK:
                            selected = dlg.GetStringSelection()
                            props = localZopes[selected]
                            zexppath = (props['localpath'] +'/import/' +\
                                os.path.basename(model.transport.resourcepath)).replace(
                                '<LocalFS::directory>', '<LocalFS::file>')

                            model.load()
                            model.saveAs(zexppath)

                            self.editor.setStatus(\
                                  '.zexp file copied. Ready to import in Zope.')
                    finally:
                        dlg.Destroy()


# XXX Zope Controllers should create from the palette, Zope Companions should
# XXX manage only inspection

wxID_ZOPEINSPECT, wxID_ZOPEVIEWBRWS = Utils.wxNewIds(2)

class ZopeController(Controllers.PersistentController):
    DefaultViews = []
    AdditionalViews = []

    inspectBmp = 'Images/Shared/Inspector.png'
    viewInBrowserBmp = 'Images/ZOA/ViewInBrowser.png'

    def __init__(self, editor, Model):
        Controllers.PersistentController.__init__(self, editor)
        self.Model = Model

    def actions(self, model):
        return Controllers.PersistentController.actions(self, model) + [
          ('Inspect', self.OnInspect, self.inspectBmp, ''), # F11?
          ('View in browser', self.OnViewInBrowser, self.viewInBrowserBmp, '')]

    def createModel(self, source, filename, main, saved, transport):
        return self.Model(source, filename, self.editor, saved, transport)

    def createNewModel(self, modelParent=None):
        pass

    def OnInspect(self, event):
        model = self.getModel()
        model.editor.explorer.controllers['zope'].doInspectZopeItem(
              model.transport)

    def OnViewInBrowser(self, event):
        model = self.getModel()
        model.editor.explorer.controllers['zope'].openSelItemInBrowser(
              zopeItem=model.transport)

#-------------------------------------------------------------------------------

Preferences.paletteTitle = Preferences.paletteTitle +' - Zope Editor'

Controllers.modelControllerReg.update( {
    ZopeExportFileModel: ZopeExportFileController,
    ZopeBlankEditorModel: ZopeController,
    ZopeDocumentModel: ZopeController,
    ZopeDTMLDocumentModel: ZopeController,
    ZopeDTMLMethodModel: ZopeController,
    ZopeSQLMethodModel: ZopeController,
    ZopePythonSourceModel: ZopeController,
    ZopePythonScriptModel: ZopeController,
    ZopeExternalMethodModel: ZopeController,
    ZopeEditorModel: ZopeController,
    ZopeSiteErrorLogModel: ZopeController,
    ZopeHelpTopicModel: ZopeController,
})
