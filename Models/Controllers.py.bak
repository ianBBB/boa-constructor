#-----------------------------------------------------------------------------
# Name:        Controllers.py
# Purpose:     Controller classes for the MVC pattern
#
# Author:      Riaan Booysen
#
# Created:     2001/13/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.Controllers'

import os, codecs

import wx

import Preferences, Utils
from Preferences import keyDefs, IS
from Utils import _

import EditorHelper, PaletteStore, EditorModels

from Views import EditorViews, SourceViews, DiffView

from Explorers import ExplorerNodes

addTool = Utils.AddToolButtonBmpIS


class BaseEditorController:
    """ Between user and model operations

    Provides interface to add new and open existing models
    Manages toolbar and menu actions
    Custom classes should define Model operations as events
    """
    docked = True

    Model           = None
    DefaultViews    = []
    AdditionalViews = []

    plugins = ()

    def __init__(self, editor):
        self.editor = editor
        self.evts = []

        self.plugins = [Plugin(self) for Plugin in self.plugins]

    def getModel(self):
        return self.editor.getActiveModulePage().model

    def createModel(self, source, filename, name, editor, saved, modelParent=None):
        pass

    def createNewModel(self, modelParent=None):
        pass

    def afterAddModulePage(self, model):
        pass

    def newFileTransport(self, name, filename):
        from Explorers.FileExplorer import FileSysNode
        return FileSysNode(name, filename, None, -1, None, None, properties = {})

    def addEvt(self, wId, meth):
        self.editor.Bind(wx.EVT_MENU, meth, id=wId)
        self.evts.append(wId)

    def disconnectEvts(self):
        for wId in self.evts:
            self.editor.Disconnect(wId)
        self.evts = []

    def addMenu(self, menu, wId, label, accls, code=(), bmp=''):
        Utils.appendMenuItem(menu, wId, label, code, bmp)
        if code:
            accls.append( (code[0], code[1], wId) )

#-------------------------------------------------------------------------------
    def actions(self, model):
        """ Override to define Controller/Model actions

        Should return a list of tuples in this form:
        [('Name', self.OnEvent, 'BmpPath', 'KeyDef'), ...]
        """
        return []

    def addActions(self, toolbar, menu, model):
        actions = self.actions(model)
        for plugin in self.plugins:
            actions.extend(plugin.actions(model))

        accls = []

        for name, event, bmp, key in actions:
            if name != '-':
                wId = wx.NewId()
                self.addEvt(wId, event)
                if key: code = keyDefs[key]
                else:   code = ()
                self.addMenu(menu, wId, name, accls, code, bmp)
            else:
                menu.AppendSeparator()

            if bmp:
                if bmp != '-':
                    addTool(self.editor, toolbar, bmp, name, event)
                elif name == '-' and bmp == '-':
                    toolbar.AddSeparator()

        return accls


class EditorController(BaseEditorController):
    closeBmp = 'Images/Editor/Close.png'

    def actions(self, model):
        return BaseEditorController.actions(self, model) + \
               [(_('Close'), self.OnClose, self.closeBmp, 'Close')]

    def OnClose(self, event):
        self.editor.closeModulePage(self.editor.getActiveModulePage())

class PersistentController(EditorController):
    saveBmp = 'Images/Editor/Save.png'
    saveAsBmp = 'Images/Editor/SaveAs.png'

    def actions(self, model):
        return EditorController.actions(self, model) + \
               [(_('Reload'), self.OnReload, '-', ''),
                (_('Save'), self.OnSave, self.saveBmp, 'Save'),
                (_('Save as...'), self.OnSaveAs, self.saveAsBmp, 'SaveAs'),
                ('-', None, '', ''),
                (_('Toggle read-only'), self.OnToggleReadOnly, '-', ''),
                (_('NDiff files...'), self.OnNDiffFile, '-', '')]

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def createNewModel(self, modelParent=None):
        name = self.editor.getValidName(self.Model)
        model = self.createModel('', name, '', False)
        model.transport = self.newFileTransport('', name)
        model.new()

        return model, name

    def checkUnsaved(self, model, checkModified=False):
        if not model.savedAs or checkModified and (model.modified or \
              len(model.viewsModified)):
            wx.LogError(_('Cannot perform this action on an unsaved%s module')%(
                  checkModified and '/modified' or '') )
            return True
        else:
            return False

    def OnSave(self, event):
        try:
            self.editor.activeModSaveOrSaveAs()
        except ExplorerNodes.TransportModifiedSaveError, err:
            errStr = err.args[0]
            if errStr == 'Reload':
                self.OnReload(event)
            elif errStr == 'Cancel':
                pass
            else:
                wx.LogError(str(err))
        except ExplorerNodes.TransportSaveError, err:
            wx.LogError(str(err))

    def OnSaveAs(self, event):
        try:
            self.editor.activeModSaveOrSaveAs(forceSaveAs=True)
        except ExplorerNodes.TransportModifiedSaveError, err:
            errStr = err.args[0]
            if errStr == 'Reload':
                self.OnReload(event)
            elif errStr == 'Cancel':
                pass
            else:
                wx.LogError(str(err))
        except ExplorerNodes.TransportSaveError, err:
            wx.LogError(str(err))

    def OnReload(self, event):
        model = self.getModel()
        if model:
            if not model.savedAs:
                wx.MessageBox(_('Cannot reload, this file has not been saved yet.'),
                             _('Reload'), wx.OK | wx.ICON_ERROR)
                return

            if model.hasUnsavedChanges() and \
                  wx.MessageBox(_('There are unsaved changes.\n'\
                                  'Are you sure you want to reload?'),
                                _('Confirm reload'), wx.YES_NO | wx.ICON_WARNING) != wx.YES:
                return
            try:
                model.load()

                self.editor.updateModuleState(model)
            except ExplorerNodes.TransportLoadError, error:
                wx.LogError(str(error))

    def OnToggleReadOnly(self, event):
        model = self.getModel()
        if model and model.transport and model.transport.stdAttrs.has_key('read-only'):
            model.transport.updateStdAttrs()
            ro = model.transport.stdAttrs['read-only']
            model.transport.setStdAttr('read-only', not ro)

            if model.views.has_key('Source'):
                model.views['Source'].updateFromAttrs()

            self.editor.updateModuleState(model)
        else:
            wx.LogError(_('Read-only not supported on this transport'))

    def OnNDiffFile(self, event=None, filename=''):
        model = self.getModel()
        model.refreshFromViews()
        if model:
            if self.checkUnsaved(model): return
            if not filename:
                filename = self.editor.openFileDlg(curfile=os.path.basename(model.filename))
            if filename:
                tbName = 'Diff with : '+filename
                if not model.views.has_key(tbName):
                    resultView = self.editor.addNewView(tbName,
                          DiffView.PythonSourceDiffView)
                else:
                    resultView = model.views[tbName]

                resultView.tabName = tbName
                resultView.diffWith = filename
                resultView.refresh()
                resultView.focus()


class SourceController(PersistentController):
    AdditionalViews = [EditorViews.CVSConflictsView]

    def OnDiffFile(self, event, diffWithFilename=''):
        model = self.getModel()
        if model:
            if self.checkUnsaved(model): return
            if not diffWithFilename:
                diffWithFilename = self.editor.openFileDlg()
            filename = model.assertLocalFile(filename)

    def OnPatchFile(self, event, patchFilename=''):
        model = self.getModel()
        if model:
            if self.checkUnsaved(model): return
            if not patchFilename:
                patchFilename = self.editor.openFileDlg()
            filename = model.assertLocalFile(filename)

class TextController(PersistentController):
    Model           = EditorModels.TextModel
    DefaultViews    = [SourceViews.TextView]
    AdditionalViews = []

class UndockedController(BaseEditorController):
    docked          = False
    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def display(self, model):
        """ Override to display undocked interface """

class BitmapFileController(UndockedController):
    Model           = EditorModels.BitmapFileModel
    DefaultViews    = []
    AdditionalViews = []

    def display(self, model):
        from ZopeLib import ImageViewer
        ImageViewer.create(self.editor).showImage(model.filename, model.transport)

# XXX move to a new module PythonComControllers
class MakePyController(BaseEditorController):
    docked          = False
    Model           = None
    DefaultViews    = []
    AdditionalViews = []

    def createNewModel(self, modelParent=None):
        return None, None

    def display(self, model):
        import makepydialog
        dlg = makepydialog.create(self.editor)
        try:
            if dlg.ShowModal() == wx.ID_OK and dlg.generatedFilename:
                self.editor.openOrGotoModule(dlg.generatedFilename)
        finally:
            dlg.Destroy()

#-------------------------------------------------------------------------------

def identifyFilename(filename):
    dummy, name = os.path.split(filename)
    base, ext = os.path.splitext(filename)
    lext = ext.lower()

    if fullnameTypes.has_key(name):
        return fullnameTypes[name]
    if not ext and base.upper() == base:
        return EditorModels.TextModel, '', lext
    if EditorHelper.extMap.has_key(lext):
        return EditorHelper.extMap[lext], '', lext
    if lext in EditorHelper.internalFilesReg:
        return EditorModels.InternalFileModel, '', lext
    return None, '', lext

def identifyFile(filename, source=None, localfs=True):
    """ Return appropriate model for given source file.
        Assumes header will be part of the first continious comment block """
    Model, main, lext = identifyFilename(filename)
    if Model is not None:
        return Model, main

    if lext == defaultExt:
        BaseModel = DefaultModel
    else:
        BaseModel = EditorModels.UnknownFileModel

    if source is None and not localfs:
        if lext in EditorHelper.inspectableFilesReg.keys():
            return EditorHelper.inspectableFilesReg[lext], ''
        else:
            return BaseModel, ''
    elif lext in EditorHelper.inspectableFilesReg.keys():
        BaseModel = EditorHelper.inspectableFilesReg[lext]
        if source is not None:
            return identifySource[lext](source.split('\n'))
        elif not Preferences.exInspectInspectableFiles:
            return BaseModel, ''
        if os.path.exists(filename):
            f = open(filename)
            try:
                while 1:
                    line = f.readline()
                    if not line: break
                    line = line.strip()
                    if line.startswith(codecs.BOM_UTF8):
                        line = line[len(codecs.BOM_UTF8):]
                    if line and headerStartChar.has_key(lext):
                        if line[0] != headerStartChar[lext]:
                            return BaseModel, ''
                        headerInfo = identifyHeader[lext](line)
                        if headerInfo[0] != BaseModel:
                            return headerInfo
                return BaseModel, ''
            finally:
                f.close()
    return BaseModel, ''


#-Registration of this modules classes---------------------------------------
modelControllerReg = {EditorModels.TextModel: TextController,
                      EditorModels.BitmapFileModel: BitmapFileController}

# Default filetype
DefaultController = TextController
DefaultModel = EditorModels.TextModel
defaultExt = EditorModels.TextModel.ext

# Model identifiers for application type files
appModelIdReg = []

# Dictionaries of functions keyed on file extension
headerStartChar = {}
identifyHeader = {}
identifySource = {}
# dictionary of filetypes recognised by the whole name
fullnameTypes = {}

# Classed from which the Designer can load resources
resourceClasses = []
