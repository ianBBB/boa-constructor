#-----------------------------------------------------------------------------
# Name:        PythonEditorModels.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002/02/09
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing Models.PythonEditorModels'

import os, sys, pprint, imp, stat, types, tempfile, codecs
from thread import start_new_thread
from time import time, localtime, strftime
from cStringIO import StringIO

import wx

import Preferences, Utils
from Utils import _

import EditorHelper, ErrorStack
from EditorModels import PersistentModel, SourceModel, EditorModel, BitmapFileModel

import relpath, sourceconst

# try to use new cProfile module
try:
    import cProfile
    prof = 'cProfile'
except ImportError:
    prof = 'profile'

(imgPyAppModel, imgModuleModel, imgPackageModel, imgSetupModel,
 imgPythonBinaryFileModel,
) = EditorHelper.imgIdxRange(5)

class SourcePseudoFile(Utils.PseudoFileOutStore):
    def readlines(self):
        return self.output

class ModuleModel(SourceModel):
    modelIdentifier = 'Module'
    defaultName = 'module'
    bitmap = 'Module.png'
    imgIdx = imgModuleModel
    ext = '.py'

    def __init__(self, data, name, editor, saved, app=None):
        self.app = app
        SourceModel.__init__(self, data, name, editor, saved)
        self.moduleName = os.path.split(self.filename)[1]
        self.lastRunParams = ''
        self.lastDebugParams = ''
        self.useInputStream = False

        if data:
            if Preferences.autoReindent:
                if not self.reindent(False):
                    self.update()
            else:
                self.update()

    def destroy(self):
        SourceModel.destroy(self)
        del self.app

    def load(self, notify = True):
        SourceModel.load(self, False)
        if Preferences.autoReindent:
            if not self.reindent():
                self.update()
        else:
            self.update()
        if notify: self.notify()

    def save(self, overwriteNewer=False):
        if Preferences.autoReindent:
            self.reindent(False)
        SourceModel.save(self, overwriteNewer)

    def saveAs(self, filename):
        oldFilename = self.filename
        SourceModel.saveAs(self, filename)
        if self.app:
            self.app.moduleSaveAsNotify(self, oldFilename, filename)
        self.moduleName = os.path.basename(filename)

        # update breakpoints
        from Debugger.Breakpoint import bplist
        bplist.renameFileBreakpoints(oldFilename, self.filename)
        if self.editor.debugger:
            self.editor.debugger.breakpts.refreshList()

        self.notify()

    _module = None
    def getModule(self):
        if self._module is None:
            wx.BeginBusyCursor()
            try:
                import moduleparse
                self._module = moduleparse.Module(
                    self.moduleName, self.getDataAsLines())
            finally:
                wx.EndBusyCursor()
        return self._module

    def initModule(self):
        # Don't parse the module until it's needed.
        self._module = None

    def refreshFromModule(self):
        """ Must call this method to apply changes made
        to the module object. """
        self.setDataFromLines(self.getModule().getEOLFixedLines())
        self.notify()

    def renameClass(self, oldname, newname):
        pass

    def update(self):
        self.initModule()
        EditorModel.update(self)

    def runInThread(self, filename, args, interpreterPath, inpLines=[],
                    execStart=None, execFinish=None):
        cwd = os.path.abspath(os.getcwd())
        newCwd = os.path.dirname(os.path.abspath(filename))
        os.chdir(newCwd)
        try:
            cmd = '"%s" %s %s'%(interpreterPath,
                  os.path.basename(filename), args)

            from ModRunner import PopenModuleRunner#, ExecFinishEvent

            runner = PopenModuleRunner(None, newCwd)
            runner.run(cmd, inpLines, execStart)
            #wx.PostEvent(self.editor, ExecFinishEvent(runner))
            if execFinish:
                wx.CallAfter(execFinish, runner)
        finally:
            if os: os.chdir(cwd)

    def run1(self, args = '', execStart=None, execFinish=None):
        """ Excecute the current saved image of the application. """
        if self.savedAs:
            filename = self.assertLocalFile()

            self.editor.statusBar.setHint(_('Running %s...')%filename)
            if Preferences.minimizeOnRun:
                self.editor.minimizeBoa()
            inpLines = []
            if self.useInputStream and self.editor.erroutFrm.inputPage:
                inpLines = StringIO(
                      self.editor.erroutFrm.inputPage.GetValue()).readlines()
                
            start_new_thread(self.runInThread, (filename, args,
                  Preferences.getPythonInterpreterPath(), inpLines,
                  execStart, execFinish))

            #self.runInThread(filename, args,
            #      Preferences.getPythonInterpreterPath(), inpLines,
            #      execStart, execFinish)

    def run(self, args = '', execStart=None, execFinish=None):
        """ Excecute the current saved image of the application. """
        if self.savedAs:
            filename = self.assertLocalFile()

            self.editor.statusBar.setHint(_('Running %s...')%filename)
            if Preferences.minimizeOnRun:
                self.editor.minimizeBoa()

            inpLines = []
            if self.useInputStream and self.editor.erroutFrm.inputPage:
                inpLines = StringIO(
                      self.editor.erroutFrm.inputPage.GetValue()).readlines()
                
            cwd = os.path.abspath(os.getcwd())
            newCwd = os.path.dirname(os.path.abspath(filename))
            interp = Preferences.getPythonInterpreterPath()
            basename = os.path.basename(filename)
            
            os.chdir(newCwd)
            try:
                cmd = '"%s" %s %s'%(interp, basename, args)
    
                from ModRunner import wxPopenModuleRunner
    
                runner = wxPopenModuleRunner(self.editor.erroutFrm, newCwd)
                runner.run(cmd, inpLines, execFinish)
                
                execStart(runner.pid, os.path.basename(interp), basename)

            finally:
                if os: os.chdir(cwd)

    # XXX Not used!
    def runAsScript(self):
        filename = self.assertLocalFile()
        execfile(filename)

    def compile(self):
        import ModRunner
        oldErr = sys.stderr
        sys.stderr = ErrorStack.RecFile()
        try:
            cmr = ModRunner.CompileModuleRunner(self.editor.erroutFrm)
            cmr.run(self.filename, self.data+'\n\n', self.modified)

            serr = ErrorStack.errorList(sys.stderr)

            cmr.checkError(serr, 'Compiled')
        finally:
            sys.stderr = oldErr

        return len(serr)

    def cyclops(self, args='', execStart=None, execFinish=None):
        """ Run the saved application thru Cyclops """
        if self.savedAs:
            cwd = os.path.abspath(os.getcwd())
            filename = self.assertLocalFile()
            os.chdir(os.path.dirname(filename))
            page = ''
            try:
                name = os.path.basename(filename)
                report = tempfile.mktemp()

                # execute Cyclops in Python with module as parameter
                command = '"%s" "%s" "%s" "%s"'%(
                      Preferences.getPythonInterpreterPath(),
                      Utils.toPyPath('RunCyclops.py'), name, report)
                wx.Execute(command, True)

                # read report that Cyclops generated
                page = open(report, 'r').read()
                os.remove(report)
            finally:
                os.chdir(cwd)
                return page
        else:
            wx.LogWarning(_('Save before running Cyclops'))
            raise Exception, _('Not saved yet!')

    def debug(self, params=None, cont_if_running=0, cont_always=0,
              temp_breakpoint=None):
        if self.savedAs:
            debugger = self.editor.debugger
            if not debugger:
                from Debugger import Debugger

                filename = self.assertLocalFile(self.filename)
                debugger = Debugger.DebuggerFrame(self.editor, filename)
                debugger.setDebugClient()
                if params is not None: # pass [] to clear parameters
                    debugger.setParams(params)
                self.editor.debugger = debugger
            debugger.Show()
            debugger.initSashes()
            debugger.ensureRunning(cont_if_running, cont_always,
                                   temp_breakpoint)

    def profile(self):
        filename = self.assertLocalFile()
        #statFile = os.path.splitext(filename)[0]+'.prof'
        statFile = tempfile.mktemp()
        if os.path.exists(statFile):
            modtime = os.stat(statFile)[stat.ST_MTIME]
        else:
            modtime = None
        profDir = os.path.dirname(filename)

        cwd = os.path.abspath(os.getcwd())
        os.chdir(profDir)
        try:
            profCmd = """"%s" -c "import %s;%s.run('execfile('+chr(34)+%s+chr(34)+')', '%s')" """.strip()

            cmd = profCmd % (`Preferences.getPythonInterpreterPath()`[1:-1], 
                  prof, prof, `os.path.basename(filename)`, `statFile`[1:-1])

            if hasattr(self, 'app'): app = self.app
            else: app = None

            from ModRunner import ExecuteModuleRunner
            runner = ExecuteModuleRunner(None, profDir)
            self.editor.statusBar.setHint('Profiling %s...'%filename)
            runner.run(cmd)
            self.editor.statusBar.setHint('Finished profiling.')

        finally:
            os.chdir(cwd)

        return statFile, modtime, profDir


    def addModuleInfo(self, prefs):
        # XXX Check that module doesn't already have an info block

        dollar = '$' # has to be obscured from CVS :)
        prefs['Name'] = self.moduleName
        prefs['Created'] = strftime('%Y/%m/%d', localtime(time()))
        prefs['RCS-ID'] = '%sId: %s %s' % (dollar, self.moduleName , dollar)

        self.data = (sourceconst.defInfoBlock % prefs) + self.data
        self.modified = True
        self.update()
        self.notify()

    def reindent(self, updateModulePage=True):
        from ExternalLib import reindent
        self.refreshFromViews()
        eol = Utils.getEOLMode(self.data)
        file = SourcePseudoFile(self.getDataAsLines())
        ri = reindent.Reindenter(file, eol=eol)
        try:
            if ri.run():
                file.output = []
                ri.write(file)

                newData = ''.join(file.output)
                modified = self.data != newData
                self.modified = self.modified or modified

                if modified:
                    self.data = newData
                    if updateModulePage:
                        self.editor.updateModulePage(self)
                    self.update()
                    self.notify()

                    self.editor.statusBar.setHint(
                     _('Code reformatted (indents and or EOL characters fixed)'))
                    return True
        except Exception, error:
            self.editor.statusBar.setHint(
             _('Reindent failed - %s : %s') % (error.__class__, str(error)) , 'Error')

        return False

    def getSimpleRunnerSrc(self):
        return sourceconst.simpleModuleRunSrc

    def disassembleSource(self):
        import dis
        try:
            code = compile(self.data, self.filename, 'exec')
        except:
            oldOut = sys.stdout
            sys.stdout = Utils.PseudoFileOutStore()
            try:
                print _("''' Code does not compile\n\n    Disassembly of Traceback:\n'''")
                try:
                    dis.distb(sys.exc_info()[2])
                except:
                    print _("''' Could not disassemble traceback '''\n")
                return sys.stdout.read()
            finally:
                sys.stdout = oldOut

        oldOut = sys.stdout
        sys.stdout = Utils.PseudoFileOutStore()
        try:
            try:
                dis.disco(code)
            except:
                raise
            return sys.stdout.read()
        finally:
            sys.stdout = oldOut

        return 'Invisible code'

    def runLint(self):
        filename = self.assertLocalFile()
        from ExternalLib import pylint
        import cStringIO
        pylint.pylint(cStringIO.StringIO(self.data), filename)
        if pylint.warnings:
            return ErrorStack.buildLintWarningList(pylint.warnings[:])

    def buildImportSearchPath(self):
        try: filename = self.assertLocalFile()
        except AssertionError: srchpath = []
        else: srchpath = [os.path.dirname(filename)]
        if self.app:
            try: appfilename = self.app.assertLocalFile()
            except AssertionError: pass
            else: srchpath.insert(0, os.path.dirname(appfilename))

        return srchpath

    def findModule(self, modName, impName=''):
        """ Tries it's best to locate given module name or raise ImportError """
        # first search std python modules
        stdPyPath = sys.path[1:]
        srchpath = stdPyPath[:]
        for name in modName.split('.'):
            try:
                file, path, (ext, mode, tpe) = imp.find_module(name, srchpath)
            except ImportError:
                if srchpath == stdPyPath:
                    # else search module and app dirs
                    srchpath = self.buildImportSearchPath()
                    file, path, (ext, mode, tpe) = imp.find_module(name, srchpath)
                else:
                    raise

            if srchpath == stdPyPath:
                srchpath = []

            if tpe == imp.PKG_DIRECTORY:
                srchpath.append(path)
                continue
            elif tpe == imp.PY_SOURCE:
                # handle from [package.]module import name
                return path, 'name'
            if tpe == imp.PY_COMPILED:
                self.editor.setStatus(_('Compiled file found, check sys.path!'),
                      'Warning', True)
                raise ImportError(_('Compiled file found'))
            else:
                raise ImportError(_('Unhandled import type'))
        # handle from package import module
        if srchpath and srchpath != stdPyPath:
            if impName:
                path = os.path.join(srchpath[-1], impName+'.py')
                if os.path.isfile(path):
                    return path, 'module'
            else:
                return srchpath[-1], 'package'

        #print '%s not found in %s'%(modName, `srchpath`)
        raise ImportError(_('Module not found'))

    def importInShell(self):
        modDir, modFile = os.path.split(self.assertLocalFile())
        modName = os.path.splitext(modFile)[0]
        if self.app:
            execDir = os.path.dirname(self.app.assertLocalFile())
            if execDir != modDir:
                p, m = os.path.split(relpath.relpath(execDir, self.assertLocalFile()))
                p = p.replace('/', '.')
                p = p.replace('\\', '.')
                pckName = p
                impExecStr = 'from %s import %s'%(pckName, modName)
            else:
                impExecStr = 'import %s'%modName

        else:
            execDir = modDir
            impExecStr = 'import %s'%modName

        shell = self.editor.shell
        if execDir not in sys.path:
            sys.path.append(execDir)
            shell.pushLine("print '## Appended to sys.path'")
        else:
            info = ''

        shell.pushLine(impExecStr, impExecStr)
        if shell.lastResult != 'stderr':
            return _('Import of %s successfull')%modName, 'Info'
        else:
            return _('Import of %s failed')%modName, 'Error'

    def reloadInShell(self):
        modDir, modFile = os.path.split(self.assertLocalFile())
        modName = os.path.splitext(modFile)[0]
        impExecStr = 'reload(%s)'%modName

        shell = self.editor.shell
        shell.pushLine(impExecStr, impExecStr)

        if shell.lastResult != 'stderr':
            return _('Reload of %s successfull')%modName, 'Info'
        else:
            return _('Reload of %s failed')%modName, 'Error'

    def findGlobalDict(self, name):
        s = name+' ='
        pos = self.data.find(s)
        if pos == -1:
            raise Exception, _('Global dict %s not found in the module, please add '\
                  '"%s = {}" as a global variable.')%(name, name)
        end = self.data.find('}\n', pos + len(s) +1) + 1
        if not end:
            end = self.data.find('}\r\n', pos + len(s) +1) + 1
            if not end:
                raise Exception, _('Global dict %s not terminated properly, please fix it.')%name
        return pos + len(s), end

    def readGlobalDict(self, name):
        start, end = self.findGlobalDict(name)
        try:
            return eval(Utils.toUnixEOLMode(self.data[start:end]), {'wx': wx})
        except Exception, err:
            raise Exception, _('"%s" must be a valid dictionary global dict.\nError: %s')%(name, str(err))

    def writeGlobalDict(self, name, dct):
        start, end = self.findGlobalDict(name)
        eol = Utils.getEOLMode(self.data)
        self.data = self.data[:start]+pprint.pformat(dct).replace('\n', eol)+\
              self.data[end:]

    def buildResourceSearchList(self):
        searchPath = [os.path.abspath(os.path.dirname(self.localFilename()))]
        if self.app:
            searchPath.append(os.path.abspath(os.path.dirname(self.app.localFilename())))
        return searchPath

    def loadResource(self, importName, searchPath):
        d={}
        syspath = sys.path[:]
        sys.path[:] = searchPath
        try:
            try:
                exec 'import %s'%importName in d
                exec 'reload(%s)'%importName in d
            finally:
                sys.path[:] = syspath
            imageMod = eval(importName, d)
            del d['__builtins__']
            rootModName, rootMod = d.items()[0]
        finally:
            #try: del sys.modules[importName]
            #except KeyError: pass
            del d

        return imageMod, rootModName, rootMod

    def assureResourceLoaded(self, importName, resources, searchPath=None,
                             specialAttrs=None, report=False):
        if searchPath is None:
            searchPath = self.buildResourceSearchList()

        try:
            f, fn, desc = Utils.find_dotted_module(importName, searchPath)
        except ImportError:
            if report:
                self.editor.setStatus(_('Could not find %s')%importName, 'Error')
            return False
        
        if f is None:
            return False
        
        f.close()
        
        import Controllers
        Model, main = Controllers.identifyFile(fn)
        for ResourceClass in Controllers.resourceClasses:
            if issubclass(Model, ResourceClass):
                try:
                    imageMod, rootName, rootMod = self.loadResource(importName, 
                                                                    searchPath)
                    resources[importName] = imageMod
                    specialAttrs[rootName] = rootMod
                    if report:
                        self.editor.setStatus(_('Loaded resource: %s')%importName)
                except ImportError:
                    self.editor.setStatus(_('Could not load %s')%importName, 'Error')
                    return False
                return True

        if report:
            self.editor.setStatus(_('%s is not a valid Resource Module')%importName, 'Error')
        return False
    
    def readResources(self, mod, cls, specialAttrs):
        resources = {}
        searchPath = self.buildResourceSearchList()
        for impName in mod.imports.keys():
            self.assureResourceLoaded(impName, resources, searchPath, specialAttrs)
        return resources



class ClassModel(ModuleModel):
    """ Represents access to 1 maintained main class in the module.
        This class is identified by the 3rd header entry  #Boa:Model:Class """
    def __init__(self, data, name, main, editor, saved, app = None):
        self.main = main
        self.mainConstr = None
        ModuleModel.__init__(self, data, name, editor, saved, app)

    def renameMain(self, oldName, newName):
        self.getModule().renameClass(oldName, newName)
        self.main = newName

        idx = 0
        for line in self.getModule().source:
            if line:
                if line[0] != '#': break

                header = line.strip().split(':')
                if (len(header) == 3) and (header[0] == sourceconst.boaIdent):
                    self.getModule().source[idx] = \
                    ':'.join((header[0], header[1], newName))
                    break
            else: break
            idx = idx + 1

class ImportRelationshipMix:
    def buildImportRelationshipDict(self, modules):
        relationships = {}

        tot = len(modules)
        self.editor.statusBar.progress.SetRange(tot)
        try:
            prog = 0
            totLOC = 0
            classCnt = 0
            # XXX Rewrite in terms of transport
            for module in modules:
                self.editor.statusBar.progress.SetValue(prog)
                prog = prog + 1
                self.editor.setStatus('Parsing '+module+'...')
                #module = self.modules[moduleName]
                #filename = self.normaliseModuleRelativeToApp(module[2])
                if module[:7] != 'file://':
                    print '%s skipped, only local files supported for Imports View'
                else:
                    module = module[7:]
                try: f = open(module)
                except IOError:
                    print "couldn't load %s" % module
                    continue
                else:
                    data = f.read()
                    f.close()
                    name = os.path.splitext(os.path.basename(module))[0]
                    model = ModuleModel(data, name, self.editor, 1)
                    relationships[name] = model.getModule() #.imports

                totLOC = totLOC + model.getModule().loc
                classCnt = classCnt + len(model.getModule().classes)

            #print 'Project LOC: %d,\n%d classes in %d modules.'%(totLOC, classCnt, len(modules))
        finally:
            self.editor.statusBar.progress.SetValue(0)
            self.editor.statusBar.setHint('')
        return relationships

class PackageModel(ModuleModel, ImportRelationshipMix):
    """ Must be constructed in a valid path, name being filename, actual
        name will be derived from path """

    modelIdentifier = 'Package'
    defaultName = 'package'
    bitmap = 'Package.png'
    imgIdx = imgPackageModel
    pckgIdnt = '__init__.py'
    ext = '.py'

    def __init__(self, data, name, editor, saved, app=None):
        ModuleModel.__init__(self, data, name, editor, saved, app)
        self.packagePath = os.path.split(self.filename)[0]
        self.packageName = os.path.split(self.packagePath)[1]
        self.savedAs = True
        self.modified = False

    def openPackage(self, name):
        if self.views.has_key('Folder'):
            notebook = self.views['Folder']
        else:
            notebook = None
        self.editor.openOrGotoModule(os.path.join(self.packagePath, name,
              self.pckgIdnt), notebook=notebook)

    def openFile(self, name):
        if self.views.has_key('Folder'):
            notebook = self.views['Folder']
        else:
            notebook = None
        self.editor.openOrGotoModule(os.path.join(self.packagePath,
              name + self.ext), notebook=notebook)

    def generateFileList(self):
        """ Generate a list of modules and packages in the package path """

        from Explorers.Explorer import openEx
        transp = openEx(self.packagePath)

        filtered = []
        for item in transp.openList():
            if item.treename != '__init__.py' and \
                  (os.path.splitext(item.treename)[1] == self.ext or \
                   item.imgIdx == imgPackageModel):
                filtered.append(item)
        return filtered

    def getPageName(self):
        return self.packageName

    def buildImportRelationshipDict(self):
        mods = []
        for module in self.generateFileList():
            mods.append('file://'+module.resourcepath)

        return ImportRelationshipMix.buildImportRelationshipDict(self, mods)

class PythonBinaryFileModel(PersistentModel):
    modelIdentifier = 'PythonBinary'
    defaultName = ''
    bitmap = 'PythonBinary.png'
    imgIdx = imgPythonBinaryFileModel
    ext = '.pybin'

SimpleTypes = [types.StringType, types.IntType, types.FloatType, types.NoneType,
               types.DictionaryType, types.ListType, types.TupleType]
try: SimpleTypes.append(types.UnicodeType)
except AttributeError: pass

FunctionTypes = [types.FunctionType, types.BuiltinFunctionType]

MethodTypes = [types.MethodType, types.BuiltinMethodType]
PrivMethodTypeNames = ['method_descriptor', 'method-wrapper']

class PyExtTypeData:
    def __init__(self, Type):
        self.methods = []
        self.attrs = {}
        for name in dir(Type):
            attr = getattr(Type, name)
            AttrType = type(attr)
            if AttrType in MethodTypes or \
                  AttrType.__name__ in PrivMethodTypeNames:
                self.methods.append(name)
            else:
                self.attrs[name] = attr

class PyExtModuleData:
    def __init__(self, module):
        self.classes = {}
        self.functions = {}
        self.attrs = {}
        self.modules = {}
        for name in dir(module):
            attr = getattr(module, name)
            AttrType = type(attr)
            if AttrType in SimpleTypes:
                self.attrs[name] = attr
            elif AttrType is types.ClassType:
                self.classes[name] = PyExtTypeData(attr)
            elif AttrType in FunctionTypes:
                self.functions[name] = attr
            elif AttrType is types.ModuleType:
                self.modules[name] = PyExtModuleData(attr)
            elif hasattr(attr, '__class__'):
                self.classes[name] = PyExtTypeData(attr)
            else:
                # fallback attributes
                self.attrs[name] = attr


class PythonExtensionFileModel(PythonBinaryFileModel):
    modelIdentifier = 'PythonExtension'
    defaultName = ''
    bitmap = 'PythonBinary.png'
    imgIdx = imgPythonBinaryFileModel
    ext = '.pyd'

    def __init__(self, data, name, editor, saved):
        # XXX data not read as binary anyway
        PythonBinaryFileModel.__init__(self, '', name, editor, True)

        filename = self.checkLocalFile()
        dirName, pydName = os.path.split(filename)
        modName = os.path.splitext(pydName)[0]
        sys.path.insert(0, dirName)
        try:
            self.module = __import__(modName)
        finally:
            del sys.path[0]

        self.moduleData = PyExtModuleData(self.module)

class PythonCompiledFileModel(PythonBinaryFileModel):
    modelIdentifier = 'PythonCompiled'
    defaultName = ''
    bitmap = 'PythonBinary.png'
    imgIdx = imgPythonBinaryFileModel
    ext = '.pyc'


class BaseAppModel(ClassModel, ImportRelationshipMix):
    def __init__(self, data, name, main, editor, saved, openModules):
        self.moduleModels = {}
        self.textInfos = {}
        self.unsavedTextInfos = []
        self.modules = {}
        self.app = self
        ClassModel.__init__(self, data, name, main, editor, saved, self)
        if data:
            self.update()
            self.notify()

        # Connect all open modules to this app obj if they are defined in
        # the app's modules
        import Controllers
        abspaths = self.absModulesPaths()
        for modPage in openModules.values():
            if modPage.model.modelIdentifier not in Controllers.appModelIdReg \
                  and hasattr(modPage.model, 'app') and \
                  modPage.model.filename in abspaths:
                modPage.model.app = self

    def absModulesPaths(self):
        modules = self.modules.keys()
        abspaths = []
        for moduleName in modules:
            abspaths.append(self.normaliseModuleRelativeToApp(self.modules[moduleName][2]))
        return abspaths

    def convertToUnixPath(self, filename):
        # Don't convert absolute windows paths, will stay illegal until saved
        if os.path.splitdrive(filename)[0] != '':
            return filename
        else:
            return filename.replace('\\', '/')

    def save(self, overwriteNewer=False):
        ClassModel.save(self, overwriteNewer)
        for tin in self.unsavedTextInfos:
            fn = os.path.join(os.path.dirname(self.filename), tin)
            data = self.textInfos[tin]
            if data:
                from Explorers.Explorer import openEx, TransportError
                try:
                    f = openEx(fn)
                    f.save(f.currentFilename(), data)
                except TransportError, err:
                    pass
        self.unsavedTextInfos = []

    def saveAs(self, filename):
        for mod in self.modules.keys():
            self.modules[mod][2] = self.convertToUnixPath(\
              relpath.relpath(os.path.dirname(filename),
              self.normaliseModuleRelativeToApp(self.modules[mod][2])))

        self.writeModules()

        ClassModel.saveAs(self, filename)

        self.notify()

    def findImports(self):
        impPos = self.data.find(sourceconst.defImport.strip())
        impPos = self.data.find('import', impPos + 1)

        # XXX Add if not found
        if impPos == -1: raise Exception, _('Module import list not found in application')
        impEnd = self.data.find('\012', impPos + len('import') +1) + 1
        if impEnd == -1: raise Exception, _('Module import list not terminated')
        return impPos + len('import'), impEnd

    def idModel(self, name, src=None):
        # XXX This should be cached until rename or delete
        absPath = self.normaliseModuleRelativeToApp(self.modules[name][2])
        import Controllers

        from Explorers.Explorer import splitURI
        prot, cat, res, fn = splitURI(absPath)

        if src is None:
            if self.editor.modules.has_key(name):
                self.moduleModels[name], main = identifySource(
                    self.editor.modules[name].model.getDataAsLines())
            if self.editor.modules.has_key(absPath):
                self.moduleModels[name], main = identifySource(
                    self.editor.modules[absPath].model.getDataAsLines())
            else:
                try: self.moduleModels[name], main = \
                           Controllers.identifyFile(res, localfs=prot=='file')
                except: pass
        else:
            self.moduleModels[name], main = identifySource(src)

    def readModules(self):
        self.modules = self.readGlobalDict('modules')

        for mod in self.modules.keys():
            self.idModel(mod)

    def writeModules(self, notify=True):
        self.writeGlobalDict('modules', self.modules)

        self.modified = True
        self.editor.updateTitle()
        self.editor.updateModulePage(self)

        if notify: self.notify()

    def viewAddModule(self):
        fn = self.editor.openFileDlg()
        if fn:
            self.addModule(fn, '')

    def addModule(self, filename, descr, source=None):
        name, ext = os.path.splitext(os.path.basename(filename))
        if self.modules.has_key(name):
            raise Exception(_('Module name exists in application'))
        if self.savedAs:
            relative = relpath.relpath(os.path.dirname(self.filename), filename)
        else:
            relative = filename
        self.modules[name] = [0, descr, self.convertToUnixPath(relative)]

        self.idModel(name, source)

        self.writeModules()

    def removeModule(self, name):
        if not self.modules.has_key(name): raise Exception, _('No such module in application')

        del self.modules[name]
        self.writeModules()

    def editModule(self, oldname, newname, main, descr):
        relpath = self.modules[oldname][2]
        if oldname != newname:
            del self.modules[oldname]
        self.modules[newname] = [main, descr, relpath]
        self.writeModules()

    def splitProtFile(self, uri):
        protsplit = uri.split('://')
        if len(protsplit) == 1:
            return 'file', uri
        elif len(protsplit) == 2:
            return protsplit
        else:
            raise Exception, 'Unhandled protocol %s'%uri

    def moduleFilename(self, name):
        """ Return absolute filename of the given module """
        if not self.modules.has_key(name):
            raise Exception, _('No such module in application: ')+name

        prot, modFilename = self.splitProtFile(self.modules[name][2])
        if self.savedAs:
            if os.path.isabs(modFilename) or prot != 'file':
                absPath = self.modules[name][2]
            else:
                appProt, appFilename = self.splitProtFile(self.filename)
                absPath = appProt+'://'+self.convertToUnixPath(os.path.normpath(
                      os.path.join(os.path.dirname(appFilename), modFilename)))
        else:
            #absPath = name + ModuleModel.ext
            absPath = self.modules[name][2]
        return absPath

    def updateAutoCreateImports(self, oldName, newName):
        """ Rename module in import list.

            Only autocreated modules should be on this list.
            The module is modified and the model is not updated"""
        module = self.getModule()
        if module.imports.has_key(oldName):
            impLine = module.imports[oldName][0]-1
            # read in the import line
            line = module.source[impLine]
            impIndent = line.find('import')
            imports = line[7+impIndent:].strip().split(', ')
            impIdx = imports.index(oldName)
            imports[impIdx] = newName
            module.imports[newName] = module.imports[oldName]
            del module.imports[oldName]
            module.source[impLine] = 'import '+', '.join(imports)
            return impIdx
        return None

    def updateMainFrameModuleRefs(self, oldName, newName):
        """ Replace references to old main module with new main module """
        module = self.getModule()
        block = module.classes[sourceconst.boaClass].methods['OnInit']
        mainDef = 'self.main = %s.'
        fndOldStr = mainDef % oldName
        repNewStr = mainDef % newName

        for idx in range(block.start, block.end):
            line = module.source[idx]
            newLine = line.replace(fndOldStr, repNewStr)
            if newLine != line:
                module.source[idx] = newLine

    def changeMainFrameModule(self, newMainFrameModule):
        """ Select a new main frame module """
        if len(self.viewsModified):
            self.refreshFromViews()

        # determine which module is the main module
        module = self.getModule()
        #for mod, props in filter(lambda v: v[1][0], self.modules.items()):
        for mod, props in [i for i in self.modules.items() if i[1][0]]:
            impLine = module.imports[mod][0]-1
            line = module.source[impLine]
            impIndent = line.find('import')
            imports = line[7+impIndent:].split(', ')
            if len(imports) and imports[0] == mod:
                try:
                    impIdx = imports.index(newMainFrameModule)
                except ValueError:
                    impIdx = 0
                del imports[impIdx]

                imports.insert(0, newMainFrameModule)
                module.source[impLine] = impIndent*' '+'import '+', '.join(imports)

                self.updateMainFrameModuleRefs(mod, newMainFrameModule)
                self.refreshFromModule()

                # Update autocreation status
                props[0] = 0
                self.modules[newMainFrameModule][0] = 1
                self.writeModules(False)

                self.update()
                self.notify()
                break
        else:
            raise Exception, _('No main frame module found in application')

    def moduleSaveAsNotify(self, module, oldFilename, newFilename):
        if module != self:
            newName, ext = os.path.splitext(os.path.basename(newFilename))
            oldName = os.path.splitext(os.path.basename(oldFilename))[0]

            if not self.modules.has_key(oldName):
                raise Exception, _('Module does not exists in application')

            if self.savedAs:
                relative = relpath.relpath(os.path.dirname(self.filename), newFilename)
            else:
                relative = newFilename

            if newName != oldName:
                self.modules[newName] = self.modules[oldName]
                del self.modules[oldName]
            self.modules[newName][2] = self.convertToUnixPath(relative)

            # Check if it's autocreated module
            if self.modules[newName][0]:
                if len(self.viewsModified):
                    self.refreshFromViews()

                impIdx = self.updateAutoCreateImports(oldName, newName)

                if impIdx is not None:
                    # check if it's the main module, first in the import list is
                    # always the main module
                    if not impIdx:
                        self.updateMainFrameModuleRefs(oldName, newName)

                    # preserve modified modules
                    mods = self.modules
                    self.refreshFromModule()
                    self.modules = mods

            self.writeModules()
            self.update()

    def crashLog(self):
        err = ErrorStack.crashError(os.path.splitext(self.assertLocalFile())[0]+'.trace')
        if err:
            frm = self.editor.erroutFrm
            if frm:
                frm.updateCtrls(err)
                frm.display(err)
                return frm
        else:
            wx.LogError(_('Trace file not found. Run with command line param -T'))
            return None

    def openModule(self, name):
        from Explorers.Explorer import TransportError
        try:
            return self.editor.openOrGotoModule(self.moduleFilename(name), self)
        except TransportError, err:
            if str(err) == 'Unhandled transport' and err[1][0] == 'none':
                if wx.MessageBox(_('Unsaved file no longer open in the Editor.\n'
                      'Remove it from application modules ?'), _('Missing file'),
                      wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                    self.removeModule(name)
                return None, None
            else:
                raise

    def normaliseModuleRelativeToApp(self, relFilename):
        """ Normalise relative paths to absolute paths """
        if not self.savedAs or relFilename.startswith('none://'):
            return relFilename
        else:
            protsplit = self.filename.split('://')
            if len(protsplit) == 1:
                prot, appFilename = 'file', self.filename
            elif len(protsplit) == 2:
                prot, appFilename = protsplit
            elif len(protsplit) == 3:
                prot, archive, appFilename = protsplit
            else:
                raise Exception, _('Unhandled protocol during normalisation:%s')%protsplit

            if prot == 'zip':
                return relFilename
            
            normedpath = os.path.normpath(os.path.join(os.path.dirname(appFilename),
                  relFilename))
            if prot == 'file':
                return '%s://%s' %(prot, normedpath)
            else:
                return '%s://%s' %(prot, normedpath.replace('\\', '/'))

    def buildImportRelationshipDict(self):
        return ImportRelationshipMix.buildImportRelationshipDict(self,
               self.absModulesPaths())

    def update(self):
        self.readModules()
        ClassModel.update(self)

    def loadTextInfo(self, viewName):
        from Explorers.Explorer import openEx, TransportError
        fn = os.path.join(os.path.dirname(self.filename), viewName)
        ti = openEx(fn)
        try:
            data = ti.load()
        except TransportError, err:
            data = ''
        self.textInfos[viewName] = data

class PyAppModel(BaseAppModel):
    modelIdentifier = 'PyApp'
    defaultName = 'PyApp'
    bitmap = 'PythonApplication.png'
    imgIdx = imgPyAppModel

    def getDefaultData(self):
        return (sourceconst.defEnvPython + sourceconst.defSig + \
                sourceconst.defPyApp) %{'modelIdent': self.modelIdentifier,
                                        'main': 'main'}

class SetupModuleModel(ModuleModel):
    modelIdentifier = 'setup'
    defaultName = 'Setup'
    bitmap = 'Setup.png'
    imgIdx = imgSetupModel
    def __init__(self, data, name, editor, saved, app=None):
        ModuleModel.__init__(self, data, name, editor, saved, app)
        if data:
            self.update()
            self.notify()

    def getDefaultData(self):
        return (sourceconst.defSetup_py) % {'name': 'default', 'version': '0.1',
                                            'scripts': ''}

    def getPageName(self):
        return 'setup (%s)' % os.path.basename(os.path.dirname(self.filename))

   
##    def saveAs(self, filename):
##        # catch image type changes
##        newExt = os.path.splitext(filename)[1].lower()
##        oldExt = os.path.splitext(self.filename)[1].lower()
##        updateViews = 0
##        if newExt != oldExt:
##            updateViews = 1
##            bmp = wx.BitmapFromImage(wx.ImageFromStream(StringIO(self.data)))
##            fn = tempfile.mktemp(newExt)
##            try:
##                bmp.SaveFile(fn, self.extTypeMap[newExt])
##            except KeyError:
##                raise Exception, '%s image file types not supported'%newExt
##            try:
##                # convert data to new image format
##                self.data = open(fn, 'rb').read()
##            finally:
##                os.remove(fn)
##
##        # Actually save the file
##        PersistentModel.saveAs(self, filename)


#-------------------------------------------------------------------------------

def identifyHeader(headerStr):
    header = headerStr.split(':')
    if len(header) and (header[0] == sourceconst.boaIdent) and \
          EditorHelper.modelReg.has_key(header[1]):
        return EditorHelper.modelReg[header[1]], header[2]
    return ModuleModel, ''

def identifySource(source):
    """ Return appropriate model for given Python source.
        The logic is a copy paste from above func """
    for line in source:
        if line:
            if line.startswith(codecs.BOM_UTF8):
                line = line[len(codecs.BOM_UTF8):]
            
            if line[0] != '#':
                return ModuleModel, ''

            headerInfo = identifyHeader(line.strip())

            if headerInfo[0] != ModuleModel:
                return headerInfo
        else:
            return ModuleModel, ''
    return ModuleModel, ''    


#-------------------------------------------------------------------------------

EditorHelper.modelReg[PythonBinaryFileModel.modelIdentifier] = PythonBinaryFileModel
EditorHelper.inspectableFilesReg['.py'] = ModuleModel
