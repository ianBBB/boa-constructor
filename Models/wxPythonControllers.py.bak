#-----------------------------------------------------------------------------
# Name:        wxPythonControllers.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002/02/09
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.wxPythonControllers'

import os

import Preferences, Utils, Plugins
from Preferences import keyDefs
from Utils import _

import PaletteStore

import Controllers
from Controllers import addTool
from PythonControllers import BaseAppController, ModuleController
import EditorHelper, wxPythonEditorModels
from Views import EditorViews, AppViews, Designer, DataView, SizersView

class AppController(BaseAppController):
    Model = wxPythonEditorModels.AppModel

    def afterAddModulePage(self, model):
        frmMod = self.editor.addNewPage('Frame', FrameController, model)

        frmNme = os.path.splitext(os.path.basename(frmMod.filename))[0]
        model.new(frmNme)


class BaseFrameController(ModuleController):
    DefaultViews = ModuleController.DefaultViews + [EditorViews.ExploreEventsView]

    designerBmp = 'Images/Shared/Designer.png'

    def actions(self, model):
        return ModuleController.actions(self, model) + [
              (_('Frame Designer'), self.OnDesigner, self.designerBmp, 'Designer')]

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, main, self.editor, saved, modelParent)

    def createNewModel(self, modelParent=None):
        if modelParent:
            name = self.editor.getValidName(self.Model, modelParent.absModulesPaths())
        else:
            name = self.editor.getValidName(self.Model)

        model = self.createModel('', name, name[7:-3], False, modelParent)
        model.transport = self.newFileTransport('', model.filename)

        self.activeApp = modelParent

        return model, name

    def getModelParams(self, model):
        tempComp = self.Model.Companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        params['id'] = Utils.windowIdentifier(model.main, '')
        params['title'] = `model.main`
        return params

    def afterAddModulePage(self, model):
        model.new(self.getModelParams(model))

        if self.activeApp and self.activeApp.data and Preferences.autoAddToApplication:
            self.activeApp.addModule(model.filename, '')

    def OnDesigner(self, event):
        self.showDesigner()

    def _cancelView(self, view, name):
        view.focus()
        view.saveOnClose = False
        view.deleteFromNotebook('Source', name)

    def _cancelDesigner(self, views):
        if views.has_key('Designer'):
            views['Designer'].saveOnClose = False
            views['Designer'].close()

        if views.has_key('Data'):
            self._cancelView(views['Data'], 'Data')

    def showDesigner(self):
        # Just show if already opened
        modulePage = self.editor.getActiveModulePage()
        model = modulePage.model
        if model.views.has_key('Designer'):
            if model.views.has_key('Data'):
                model.views['Data'].focus()
            model.views['Designer'].restore()
            return

        dataView = None
        sizersView = None
        try:
            cwd = os.getcwd()
            mwd = Utils.getModelBaseDir(model)
            if mwd and mwd.startswith('file://'): os.chdir(mwd[7:])

            try:
                # update any view modifications
                model.refreshFromViews()

                model.initModule()
                model.readComponents()

                try:
                    # add or focus data view
                    if not model.views.has_key('Data'):
                        dataView = DataView.DataView(modulePage.notebook,
                             self.editor.inspector, model, self.editor.compPalette)
                        dataView.addToNotebook(modulePage.notebook)
                        model.views['Data'] = dataView
                        dataView.initialize()
                    else:
                        dataView = model.views['Data']
                except:
                    if model.views.has_key('Data'):
                        self._cancelView(model.views['Data'], 'Data')
                    raise

                dataView.focus()
                dataView.refreshCtrl()

                try:
                    # add or focus frame designer
                    if not model.views.has_key('Designer'):
                        designer = Designer.DesignerView(self.editor,
                              self.editor.inspector, model,
                              self.editor.compPalette, model.Companion,
                              dataView)
                        model.views['Designer'] = designer
                        designer.refreshCtrl()
                except:
                    self._cancelDesigner(model.views)
                    raise

                if Preferences.dsUseSizers:
                    try:
                        # add sizer view
                        if not model.views.has_key('Sizers'):
                            sizersView = SizersView.SizersView(modulePage.notebook,
                                 self.editor.inspector, model,
                                 self.editor.compPalette, model.views['Designer'])
                            sizersView.addToNotebook(modulePage.notebook)
                            model.views['Sizers'] = sizersView
                            sizersView.initialize()
                        else:
                            sizersView = model.views['Sizers']
                    except:
                        if model.views.has_key('Sizers'):
                            self._cancelView(model.views['Sizers'], 'Sizers')
                        self._cancelDesigner(model.views)
                        raise

                    sizersView.refreshCtrl()

                # Showing triggers selection of the frame in the Inspector
                model.views['Designer'].Show()
                # Make source read only
                model.views['Source'].disableSource(True)

                self.editor.setStatus(_('Designer session started.'))

            finally:
                os.chdir(cwd)

        except Exception, error:
            self.editor.setStatus(\
                _('An error occured while opening the Designer: %s')%str(error),
                  'Error')
            self.editor.statusBar.progress.SetValue(0)
            raise

class FrameController(BaseFrameController):
    Model = wxPythonEditorModels.FrameModel

class DialogController(BaseFrameController):
    Model = wxPythonEditorModels.DialogModel

class MiniFrameController(BaseFrameController):
    Model = wxPythonEditorModels.MiniFrameModel

class MDIParentController(BaseFrameController):
    Model = wxPythonEditorModels.MDIParentModel

class MDIChildController(BaseFrameController):
    Model = wxPythonEditorModels.MDIChildModel

class PopupWindowController(BaseFrameController):
    Model = wxPythonEditorModels.PopupWindowModel
    def getModelParams(self, model):
        tempComp = self.Model.Companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        return params

class PopupTransientWindowController(BaseFrameController):
    Model = wxPythonEditorModels.PopupTransientWindowModel
    def getModelParams(self, model):
        tempComp = self.Model.Companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        return params

class FramePanelController(BaseFrameController):
    Model = wxPythonEditorModels.FramePanelModel
    def getModelParams(self, model):
        tempComp = self.Model.Companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        params['id'] = Utils.windowIdentifier(model.main, '')
        return params

class WizardController(DialogController):
    Model = wxPythonEditorModels.WizardModel

class PyWizardPageController(FramePanelController):
    Model = wxPythonEditorModels.PyWizardPageModel
    def getModelParams(self, model):
        tempComp = self.Model.Companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        return params

class WizardPageSimpleController(FramePanelController):
    Model = wxPythonEditorModels.WizardPageSimpleModel
    def getModelParams(self, model):
        tempComp = self.Model.Companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        return params


#-------------------------------------------------------------------------------

Preferences.paletteTitle = Preferences.paletteTitle +' - wxPython GUI Builder'

# this registers the class browser under Tools
import ClassBrowser
# registers resource support
import ResourceSupport

Controllers.appModelIdReg.append(wxPythonEditorModels.AppModel.modelIdentifier)

for name, Ctrlr in [
      ('wx.App', AppController),
      ('wx.Frame', FrameController),
      ('wx.Dialog', DialogController),
      ('wx.MiniFrame', MiniFrameController),
      ('wx.MDIParentFrame', MDIParentController),
      ('wx.MDIChildFrame', MDIChildController),
      ('wx.PopupWindow', PopupWindowController),
      ('wx.PopupTransientWindow', PopupTransientWindowController),
      ('wx.FramePanel', FramePanelController),
      ('wx.wizard.Wizard', WizardController),
      ('wx.wizard.PyWizardPage', PyWizardPageController),
      ('wx.wizard.WizardPageSimple', WizardPageSimpleController),
    ]:
    Plugins.registerFileType(Ctrlr, newName=name)
