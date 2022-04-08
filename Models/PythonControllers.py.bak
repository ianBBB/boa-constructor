#-----------------------------------------------------------------------------
# Name:        PythonControllers.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002/02/09
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.PythonControllers'

import os, sys, time, imp, marshal, stat

import wx

import Preferences, Utils, Plugins
from Preferences import keyDefs
from Utils import _

import PaletteStore

import Controllers
from Controllers import SourceController, EditorController, addTool
import EditorHelper, EditorModels, PythonEditorModels

from Views import EditorViews, AppViews, SourceViews, PySourceView, OGLViews, ProfileView

from ModRunner import ProcessModuleRunner
import ErrorStack

import methodparse, sourceconst

# TODO: Profile, Cyclops and other file runners should use the command-line
# TODO: parameters whenever possible

class ModuleController(SourceController):
    Model = PythonEditorModels.ModuleModel
    DefaultViews    = [PySourceView.PythonSourceView, EditorViews.ExploreView]
    AdditionalViews = [EditorViews.HierarchyView, EditorViews.ModuleDocView,
                       EditorViews.ToDoView, OGLViews.UMLView,
                       PySourceView.PythonDisView] + SourceController.AdditionalViews

    activeApp = None

    runAppBmp = 'Images/Debug/RunApp.png'
    runBmp = 'Images/Debug/Run.png'
    compileBmp = 'Images/Debug/Compile.png'
    debugBmp = 'Images/Debug/Debug.png'
    profileBmp = 'Images/Debug/Profile.png'

    def actions(self, model):
        actions = [
              ('-', None, '', ''),
              (_('Import module into Shell'), self.OnImportInShell, '-', ''),
              (_('Reload module in Shell'), self.OnReloadInShell, '-', ''),
              ('-', None, '', ''),
              (_('Set command-line parameters'), self.OnSetRunParams, '-', ''),
              (_('Toggle use input stream'), self.OnToggleUseInputStream, '-', ''),
              (_('Run application'), self.OnRunApp, self.runAppBmp, 'RunApp'),
              (_('Run module'), self.OnRun, self.runBmp, 'RunMod'),
              (_('Debug application'), self.OnDebugApp, self.debugBmp, 'Debug'),
              (_('Debug module'), self.OnDebug, '-', ''),
              (_('Step in'), self.OnDebugStepIn, '-', 'DebugStep'),
              (_('Step over'), self.OnDebugStepOver, '-', 'DebugOver'),
              (_('Step out'), self.OnDebugStepOut, '-', 'DebugOut'),
              (_('Pause debug'), self.OnDebugPause, '-', 'DebugPause'),
              (_('Stop debug'), self.OnDebugStop, '-', 'DebugStop'),
              ('-', None, '-', ''),
              (_('Profile'), self.OnProfile, self.profileBmp, ''),
              (_('Check source'), self.OnCheckSource, self.compileBmp, 'CheckSource'),
              (_('Cyclops'), self.OnCyclops, '-', ''),
              ('-', None, '', ''),
              (_('Reindent whole file'), self.OnReindent, '-', ''),
              ('-', None, '', '')]

        if hasattr(model, 'app') and model.app:
            actions.append((_('Switch to app'), self.OnSwitchApp, '-', 'SwitchToApp'))
        else:
            actions.extend(
             [(_('Add to an open application'), self.OnAddToOpenApp, '-', ''),
              (_('Associate with an open application'), self.OnAssosiateWithOpenApp, '-', '')])

        try:
            imp.find_module('pychecker')
        except ImportError:
            pass
        else:
            actions.extend([
                  (_('Run PyChecker'), self.OnRunPyChecker, '-', ''),
                  (_('Configure PyChecker'), self.OnConfigPyChecker, '-', '')])

        return SourceController.actions(self, model) + actions

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved, modelParent)

    def createNewModel(self, modelParent=None):
        if modelParent:
            name = self.editor.getValidName(self.Model, modelParent.absModulesPaths())
        else:
            name = self.editor.getValidName(self.Model)

        model = self.createModel('', name, '', False, modelParent)
        model.transport = self.newFileTransport('', name)
        self.activeApp = modelParent

        return model, name

    def afterAddModulePage(self, model):
        if self.activeApp and Preferences.autoAddToApplication:
            self.activeApp.addModule(model.filename, '')

        model.new()

    def OnProfile(self, event):
        model = self.getModel()
        if self.checkUnsaved(model): return

        try:
            statFile, modtime, profDir = model.profile()
        except Exception, err:
            wx.LogError(str(err))
            return

        if modtime is not None:
            curmodtime = os.stat(statFile)[stat.ST_MTIME]
            if curmodtime == modtime:
                wx.LogError(_('Stats file date unchanged, check for errors in script.'))
                return
        elif not os.path.exists(statFile):
            wx.LogError(_('Stats file not found, check for errors in script.'))
            return

        self.editor.setStatus(_('Loading stats...'))
        stats = marshal.load(open(statFile, 'rb'))

        resName = _('Profile stats: %s')%time.strftime('%H:%M:%S', 
              time.localtime(time.time()))
        if not model.views.has_key(resName):
            resultView = self.editor.addNewView(resName,
              ProfileView.ProfileStatsView)
        else:
            resultView = model.views[resName]
        resultView.tabName = resName
        resultView.stats = stats
        resultView.profDir = profDir
        self.editor.setStatus(_('Refreshing view...'))
        resultView.refresh()
        resultView.focus()
        self.editor.setStatus(_('Profiling complete.'))

    def OnCheckSource(self, event):
        model = self.getModel()
        self.editor.setStatus(_('Compiling...'))
        if model.compile():
            self.editor.setStatus(_('There were errors'), 'Warning')
        else:
            self.editor.setStatus(_('Compiled successfully'))

        if Preferences.runPyLintOnCheckSource:
            self.editor.setStatus(_('Running lint...'))
            warnings = model.runLint()
            if warnings and self.editor.erroutFrm:
                self.editor.erroutFrm.updateCtrls(warnings, [], 'Warning',
                    os.path.dirname(model.assertLocalFile()))
                self.editor.erroutFrm.display(len(warnings))
            self.editor.setStatus(_('Lint completed'))

    def OnSetRunParams(self, event):
        model = self.getModel()
        dlg = wx.TextEntryDialog(self.editor, _('Parameters:'),
          _('Command-line parameters'), model.lastRunParams)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                model.lastRunParams = dlg.GetValue()
                # update running debuggers debugging this module
                debugger = self.editor.debugger
                if debugger and debugger.filename == model.localFilename():
                    if model.lastRunParams:
                        params = methodparse.safesplitfields(model.lastRunParams, ' ')
                    else:
                        params = []
                    self.editor.debugger.setParams(params)
        finally:
            dlg.Destroy()

    def OnRun(self, event):
        self.OnRunApp(event, self.getModel())

    def OnRunApp(self, event=None, runModel=None):
        model = self.getModel()
        if self.checkUnsaved(model): return
        
        try:
            Preferences.getPythonInterpreterPath()
        except Exception, err:
            wx.LogError(str(err))
            return
        
        wx.BeginBusyCursor()
        try:
            if runModel is None:
                if model.app:
                    runModel = model.app
                else:
                    runModel = model
            runModel.run(runModel.lastRunParams, self.execStart, self.execFinish)
        finally:
            wx.EndBusyCursor()

##    def execFinish1(self, runner):
##        model = self.getModel()
##        editor = model.editor
##        if editor.erroutFrm:
##            if editor.palette.IsShown():
##                editor.palette.restore()
##            editor.restore()
##
##            runner.init(editor.erroutFrm)
##            errs = runner.recheck()
##
##            editor.erroutFrm.processFinished(runner.pid)
##
##            if errs:
##                editor.statusBar.setHint('Finished execution, there were errors', 'Warning')
##            else:
##                editor.statusBar.setHint('Finished execution.')

    def execStart(self, pid, program, script):
        editor = self.editor
        if editor.erroutFrm:
            self.editor.erroutFrm.processStarted(program, pid, script)

    def execFinish(self, runner):
        editor = self.editor
        if editor.erroutFrm:
            if editor.palette.IsShown():
                editor.palette.restore()
            editor.restore()

            runner.init(editor.erroutFrm)
            errs = runner.recheck()

            editor.erroutFrm.processFinished(runner.pid)

            if errs:
                editor.statusBar.setHint(_('Finished execution, there were errors'),
                                           'Warning')
            else:
                editor.statusBar.setHint(_('Finished execution.'))


    def OnDebug(self, event):
        self.OnDebugApp(event, self.getModel())

    def OnDebugApp(self, event=None, debugModel=None):
        model = self.getModel()
        if self.checkUnsaved(model): return
        if debugModel is None:
            if model.app:
                debugModel = model.app
            else:
                debugModel = model

        if debugModel.lastRunParams:
            params = methodparse.safesplitfields(debugModel.lastRunParams, ' ')
        else:
            params = None
        debugModel.debug(params, cont_if_running=1)

    def OnDebugStepIn(self, event):
        if self.editor.debugger:
            self.editor.debugger.OnStep(event)

    def OnDebugStepOver(self, event):
        if self.editor.debugger:
            self.editor.debugger.OnOver(event)

    def OnDebugStepOut(self, event):
        if self.editor.debugger:
            self.editor.debugger.OnOut(event)

    def OnDebugPause(self, event):
        if self.editor.debugger:
            self.editor.debugger.OnPause(event)

    def OnDebugStop(self, event):
        if self.editor.debugger:
            self.editor.debugger.OnStop(event)

    def OnSwitchApp(self, event):
        model = self.getModel()
        if model and isinstance(model, PythonEditorModels.ModuleModel) and model.app:
            # does this ensure correct app is reconnected?
            appmodel, controller = self.editor.openOrGotoModule(model.app.filename)

            if appmodel.prevSwitch and appmodel.prevSwitch.model:
                appmodel.prevSwitch.focus()
                appmodel.prevSwitch = None
            else:
                appmodel.views['Application'].focus()

    def OnRunPyChecker(self, event):
        model = self.getModel()
        if model:
            if self.checkUnsaved(model): return
            filename = model.assertLocalFile()
            cwd = os.path.abspath(os.getcwd())
            newCwd = os.path.dirname(filename)
            os.chdir(newCwd)
            oldErr = sys.stderr
            oldSysPath = sys.path[:]
            try:
                sys.path.append(Preferences.pyPath)
                cmd = '"%s" "%s" %s'%(sys.executable,
                      os.path.join(Preferences.pyPath, 'ExternalLib',
                      'pychecker_custom.py'), os.path.basename(filename))

                ProcessModuleRunner(self.editor.erroutFrm, newCwd).run(cmd,
                      ErrorStack.PyCheckerErrorParser, 'PyChecker', 'Warning',
                      True)
            finally:
                sys.path = oldSysPath
                sys.stderr = oldErr
                os.chdir(cwd)

    def OnConfigPyChecker(self, event):
        model = self.getModel()
        if model:
            home = os.environ.get('HOME')
            if home:
                appDir = home
                appConfig = home+'/.pycheckrc'
            else:
                filename = model.assertLocalFile()
                appDir = os.path.dirname(filename)
                appConfig = appDir+'/.pycheckrc'
            if not os.path.exists(appConfig):
                dlg = wx.MessageDialog(self.editor, _('The PyChecker configuration file '
                  'can not be found. Copy the default file here?'),
                  _('Config file not found'), wx.YES_NO | wx.ICON_QUESTION)
                try:
                    if dlg.ShowModal() == wx.ID_YES:
                        from pychecker import Config
                        open(appConfig, 'w').write(Config.outputRc(Config.Config()))
                    else:
                        return
                finally:
                    dlg.Destroy()

            from Explorers.PrefsExplorer import SourceBasedPrefColNode
            SourceBasedPrefColNode('PyChecker', ('*',), appConfig, -1, None).open(self.editor)

    def OnCyclops(self, event):
        model = self.getModel()
        if model:
            if self.checkUnsaved(model): return
            self.editor.setStatus(_('Running Cyclops on %s ...')%model.filename)
            wx.BeginBusyCursor()
            try:
                report = model.cyclops()
            finally:
                wx.EndBusyCursor()

            resName = _('Cyclops report: %s')%time.strftime('%H:%M:%S', time.localtime(time.time()))
            if not model.views.has_key(resName):
                resultView = self.editor.addNewView(resName, EditorViews.CyclopsView)
            else:
                resultView = model.views[resName]
            resultView.tabName = resName
            resultView.report = report
            resultView.refresh()
            resultView.focus()

    def OnReindent(self, event):
        model = self.getModel()
        if model:
            model.reindent()

    def OnTabNanny(self, event):
        model = self.getModel()
        if model:
            model.tabnanny()

    def chooseOpenApp(self, model, msg, capt):
        openApps = self.editor.getAppModules()
        if not openApps:
            wx.MessageBox(_('No open applications.'), style=wx.ICON_ERROR)
            return
        chooseApps = {}
        for app in openApps:
            chooseApps[os.path.basename(app.filename)] = app
        dlg = wx.SingleChoiceDialog(self.editor, msg, capt, chooseApps.keys())
        try:
            if dlg.ShowModal() == wx.ID_OK:
                return chooseApps[dlg.GetStringSelection()]
            else:
                return None
        finally:
            dlg.Destroy()

    def OnAddToOpenApp(self, event):
        model = self.getModel()
        if model:
            app = self.chooseOpenApp(model,
                  _('Select application to add the current file to'),
                  _('Add to Application'))

            if app:
                if model.savedAs: src = None
                else: src = model.getDataAsLines()

                app.addModule(model.filename, '', src)
                model.app = app
                self.editor.setupToolBar()

    def OnAssosiateWithOpenApp(self, event):
        model = self.getModel()
        if model:
            app = self.chooseOpenApp(model,
                  _('Select application to associate the current file with'),
                  _('Associate with Application'))

            if app:
                model.app = app
                self.editor.setupToolBar()


    def OnSave(self, event):
        SourceController.OnSave(self, event)
        if Preferences.checkSourceOnSave:
            self.OnCheckSource(event)

    def OnSaveAs(self, event):
        SourceController.OnSaveAs(self, event)
        if Preferences.checkSourceOnSave:
            self.OnCheckSource(event)

    def OnImportInShell(self, event):
        model = self.getModel()
        if model:
            msg, status  = model.importInShell()
            self.editor.setStatus(msg, status)

    def OnReloadInShell(self, event):
        model = self.getModel()
        if model:
            msg, status  = model.reloadInShell()
            self.editor.setStatus(msg, status)

    def OnToggleUseInputStream(self, event):
        model = self.getModel()
        if model:
            model.useInputStream = not model.useInputStream
            if model.useInputStream:
                self.editor.erroutFrm.displayInput(True)
                wx.LogMessage(_('Using input stream for running'))
            else:
                wx.LogMessage(_('Not using input stream for running'))

def ToolsOnAttachToDebugger(editor):
    from Debugger.RemoteDialog import create
    rmtDlg = create(editor)
    rmtDlg.ShowModal()
    rmtDlg.Destroy()

class BaseAppController(ModuleController):
    DefaultViews    = [AppViews.AppView] + ModuleController.DefaultViews
    AdditionalViews = [AppViews.AppModuleDocView, AppViews.AppToDoView,
                       EditorViews.ToDoView,
                       OGLViews.ImportsView, EditorViews.CVSConflictsView,
                       AppViews.AppREADME_TIFView, AppViews.AppCHANGES_TIFView,
                       AppViews.AppTODO_TIFView, AppViews.AppBUGS_TIFView]

    saveAllBmp = 'Images/Editor/SaveAll.png'

    def actions(self, model):
        return ModuleController.actions(self, model) + [
              (_('Save modified modules'), self.OnSaveAll, self.saveAllBmp, ''),
              (_('Compare apps'), self.OnCmpApps, '-', ''),
              (_('View crash log as traceback'), self.OnCrashLog, '-', '')]

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, main, self.editor, saved,
           self.editor.modules)

    def createNewModel(self, modelParent=None):
        appName = self.editor.getValidName(self.Model)
        main = appName[7:-3]
        appModel = self.createModel('', appName, main, False)
        appModel.transport = self.newFileTransport(main, appName)

        return appModel, appName

    def OnSaveAll(self, event):
        model = self.getModel()
        if model:
            for modulePage in self.editor.modules.values():
                mod = modulePage.model
                if mod != model:
                    if hasattr(mod, 'app') and mod.app == model and \
                      (mod.modified or len(mod.viewsModified)):
                        if len(mod.viewsModified):
                            mod.refreshFromViews()
                        modulePage.saveOrSaveAs()
                else:
                    appModPage = modulePage
            appModPage.saveOrSaveAs()

    def OnCmpApps(self, event):
        model = self.getModel()
        if model:
            fn = self.editor.openFileDlg()
            if fn:
                filename = model.assertLocalFile(fn)
                tbName = 'App. Compare : '+filename
                if not model.views.has_key(tbName):
                    from Views.AppViews import AppCompareView
                    resultView = self.editor.addNewView(tbName, AppCompareView)
                else:
                    resultView = model.views[tbName]

                resultView.tabName = tbName
                resultView.compareTo = filename
                resultView.refresh()
                resultView.focus()

    def OnCrashLog(self, event):
        model = self.getModel()
        if model:
            wx.BeginBusyCursor()
            try:
                model.crashLog()
            finally:
                wx.EndBusyCursor()

class PyAppController(BaseAppController):
    Model = PythonEditorModels.PyAppModel

    def afterAddModulePage(self, model):
        model.new()

class PackageController(ModuleController):
    Model = PythonEditorModels.PackageModel
    DefaultViews = [EditorViews.PackageView] + ModuleController.DefaultViews
    AdditionalViews = ModuleController.AdditionalViews + [OGLViews.ImportsView]

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def createNewModel(self, modelParent=None):
        name = '__init__.py'
        filename, success = self.editor.saveAsDlg(name)
        if success:
            model = self.createModel(sourceconst.defPackageSrc, filename, '', False)
            model.transport = self.newFileTransport(name, filename)
            model.save()

            return model, filename
        else:
            return None, None

    def new(self):
        pass

    def afterAddModulePage(self, model):
        pass

class PythonExtensionController(EditorController):
    Model = PythonEditorModels.PythonExtensionFileModel
    DefaultViews = [EditorViews.ExplorePythonExtensionView]
    AdditionalViews = []

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def createNewModel(self, modelParent=None):
        raise Exception, _('Cannot create a new Python Extension, use distutils to build it')

    def new(self):
        pass


class SetupController(ModuleController):
    Model = PythonEditorModels.SetupModuleModel

    DefaultViews = ModuleController.DefaultViews + [EditorViews.DistUtilManifestView]

    def actions(self, model):
        actions = [
              ('-', None, '', ''),
              ('setup.py with parameters', self.OnSetupParams, '-', ''),
              ('setup.py build', self.OnSetupBuild, '-', ''),
              ('setup.py clean', self.OnSetupClean, '-', ''),
              ('setup.py install', self.OnSetupInstall, '-', ''),
              ('setup.py sdist', self.OnSetupSDist, '-', ''),
              ('setup.py bdist', self.OnSetupBDist, '-', '')]

        if wx.Platform == '__WXGTK__':
            actions.append(('setup.py bdist_rpm', self.OnSetupBDist_RPM, '-', ''))
        else:
            actions.append(('setup.py bdist_wininst', self.OnSetupBDist_WinInst, '-', ''))

        try:
            imp.find_module('py2exe')
        except ImportError:
            pass
        else:
            actions.append(('setup.py py2exe', self.OnSetupPy2Exe, 'Images/Editor/Build.png', ''))

        return ModuleController.actions(self, model) + actions

    def createNewModel(self, modelParent=None):
        name = 'setup.py'
        model = self.createModel(sourceconst.defSetup_py, name, '', False)
        model.transport = self.newFileTransport('', name)
        model.new()

        return model, name

    def runDistUtilsCmd(self, cmd):
        model = self.getModel()
        if not model.savedAs:
            wx.LogError(_('Cannot run distutils on an unsaved module'))
            return

        cwd = os.path.abspath(os.getcwd())
        filename = model.assertLocalFile()
        filedir = os.path.dirname(filename)
        os.chdir(filedir)
        try:
            ProcessModuleRunner(self.editor.erroutFrm, filedir).run(\
            '"%s" setup.py %s'%(`Preferences.getPythonInterpreterPath()`[1:-1], cmd),
            caption=_('Running distutil command...'))
        finally:
            os.chdir(cwd)

    def OnSetupBuild(self, event):
        self.runDistUtilsCmd('build')
    def OnSetupClean(self, event):
        self.runDistUtilsCmd('clean')
    def OnSetupInstall(self, event):
        self.runDistUtilsCmd('install')
    def OnSetupSDist(self, event):
        self.runDistUtilsCmd('sdist')
    def OnSetupBDist(self, event):
        self.runDistUtilsCmd('bdist')
    def OnSetupBDist_WinInst(self, event):
        self.runDistUtilsCmd('bdist_wininst')
    def OnSetupBDist_RPM(self, event):
        self.runDistUtilsCmd('bdist_rpm')
    def OnSetupParams(self, event):
        dlg = wx.TextEntryDialog(self.editor, _('Edit setup.py arguments'),
                                _('Distutils setup'), '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.runDistUtilsCmd(dlg.GetValue())
        finally:
            dlg.Destroy()

    def OnSetupPy2Exe(self, event):
        self.runDistUtilsCmd('py2exe')

#-------------------------------------------------------------------------------

Preferences.paletteTitle = Preferences.paletteTitle +' - Python IDE'
Controllers.headerStartChar['.py'] = '#'
Controllers.identifyHeader['.py'] = PythonEditorModels.identifyHeader
Controllers.identifySource['.py'] = PythonEditorModels.identifySource

Controllers.appModelIdReg.append(PythonEditorModels.PyAppModel.modelIdentifier)

Controllers.fullnameTypes.update({
    '__init__.py': (PythonEditorModels.PackageModel, '', '.py'),
    'setup.py':    (PythonEditorModels.SetupModuleModel, '', '.py'),
})

Plugins.registerFileType(PyAppController, newName='PythonApp')
Plugins.registerFileTypes(ModuleController, PackageController)
Plugins.registerFileType(SetupController, newName='Setup')
Plugins.registerFileType(PythonExtensionController, addToNew=False)

# Python extensions to the Explorer

# Register Packages as a File Explorer sub type
from Explorers import ExplorerNodes, FileExplorer

def isPackage(filename):
    return os.path.exists(os.path.join(filename, PythonEditorModels.PackageModel.pckgIdnt))

FileExplorer.FileSysNode.subExplorerReg['folder'].append(
  (FileExplorer.FileSysNode, isPackage, PythonEditorModels.PackageModel.imgIdx),
)

class SysPathNode(ExplorerNodes.ExplorerNode):
    protocol = 'sys.path'
    def __init__(self, clipboard, parent, bookmarks):
        ExplorerNodes.ExplorerNode.__init__(self, 'sys.path', '', clipboard,
              EditorHelper.imgPathFolder, parent)
        self.bookmarks = bookmarks
        self.bold = True
        self.vetoSort = True

    def isFolderish(self):
        return True

    def createChildNode(self, shpth, pth):
        return FileExplorer.FileSysNode(shpth, pth, self.clipboard,
              EditorHelper.imgPathFolder, self, self.bookmarks)

    def refresh(self):
        self.entries = []
        pythonDir = os.path.dirname(sys.executable)
        for pth in sys.path:
            pth = os.path.abspath(pth)
            shortPath = pth
            if pth:
                if pth[0:len(pythonDir)] == pythonDir:
                    shortPath = pth[len(pythonDir):]
                    if not shortPath:
                        shortPath = '<Python root>'
                if (shortPath, pth) not in self.entries and os.path.isdir(pth):
                    self.entries.append( (shortPath, pth) )

    def openList(self):
        self.refresh()
        res = []
        for short, entry in self.entries:
            res.append(self.createChildNode(short, entry))
        return res

if not hasattr(sys, 'frozen'):
    ExplorerNodes.register(SysPathNode, clipboard='file', controller='file', root=True)


# Hook debugger attaching to Tools menu
Plugins.registerTool(
 _('Attach to debugger'), ToolsOnAttachToDebugger, 'Images/Shared/Debugger.png')
