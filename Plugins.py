#-----------------------------------------------------------------------------
# Name:        Plugins.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

#import os, glob, new, pprint
import os, glob, pprint
import types

import Preferences, Utils
from Utils import _

# MVC
from Models import EditorHelper, Controllers
# Components
import PaletteStore
# Explorers
from Explorers import ExplorerNodes


class PluginError(Exception):
    pass

class SkipPlugin(PluginError):
    """ Special error, used to abort importing plugins early if they depend
    on modules not loaded

    Warning indicating problem is displayed """

class SkipPluginSilently(SkipPlugin):
    """ Special error, used to abort importing plugins early if they depend
    on modules not available.

    Plugin is skipped silently.
    Used when user can do nothing about the problem (like switching platforms ;)
    """

def importFromPlugins(name):
    # find module
    pluginsPath = Preferences.pyPath + '/Plug-ins'
    paths = [pluginsPath]
    if Preferences.extraPluginsPath:
        paths.append(Preferences.extraPluginsPath)
    pluginRcPath = Preferences.rcPath+ '/Plug-ins'
    if Preferences.rcPath != Preferences.pyPath and os.path.isdir(pluginRcPath):
        paths.append(pluginRcPath)

    modname = name.replace('.', '/') + '.py'
    for pth in paths:
        modpath = os.path.join(pth, modname)
        if os.path.isfile(modpath):
            break
    else:
        raise ImportError(_('Module %s could not be found in Plug-ins')%modname)

    # mod = new.module(name)
    mod = types.ModuleType(name)

    exec(modpath, mod.__dict__)

    return mod

def transportInstalled(transport):
    return transport in eval(
         Utils.createAndReadConfig('Explorer').get('explorer', 
                                                   'installedtransports'),{})

def readPluginsState(section):
    cfg = Utils.createAndReadConfig('Explorer')
    if cfg.has_section(section):
        if cfg.has_option(section, 'ordered'):
            ordered = eval(cfg.get(section, 'ordered'), {})
        else:
            ordered = []
        if cfg.has_option(section, 'disabled'):
            disabled = eval(cfg.get(section, 'disabled'), {})
        else:
            disabled = []
        return ordered, disabled
    else:
        return [], []
    
def writePluginsState(section, ordered, disabled):
    cfg = Utils.createAndReadConfig('Explorer')
    if not cfg.has_section(section):
        cfg.add_section(section)
    cfg.set(section, 'ordered', pprint.pformat(ordered))
    cfg.set(section, 'disabled', pprint.pformat(disabled))
    
    Utils.writeConfig(cfg)
    
def buildPluginExecList():
    if not Preferences.pluginSections:
        return []

    pluginExecList = []
    pluginPathGlobs = []
    for sect, path in zip(Preferences.pluginSections, Preferences.pluginPaths):
        pluginState = readPluginsState(sect)
        pluginPathGlobs.append( (os.path.join(path, '*.plug-in.py'), pluginState) )

    for globPath, (ordered, disabled) in pluginPathGlobs:
        globList = glob.glob(globPath)

        insIdx = 0
        orderedPlugins = []
        for pluginName in ordered:
            pluginFilename = os.path.join(os.path.dirname(globPath),
                                          pluginName)+'.plug-in.py'
            try:
                idx = globList.index(pluginFilename)
            except ValueError:
                #wx.LogWarning('Ordered plugin: %s not found: %'%pluginFilename)
                pass
            else:
                del globList[idx]
                globList.insert(insIdx, pluginFilename)
                insIdx = insIdx + 1
                orderedPlugins.append(pluginFilename)

        disabledPlugins = []
        for pluginName in disabled:
            disabledPlugins.append(os.path.join(os.path.dirname(globPath),
                                                pluginName)+'.plug-in.py')

        for pluginFilename in globList:
            pluginExecList.append( (pluginFilename,
                                    pluginFilename in orderedPlugins,
                                    pluginFilename not in disabledPlugins) )
    return pluginExecList

def assureConfigFile(filename, data):
    if not os.path.exists(filename):
        open(filename, 'w').write(data)

def updateRcFile(rcFile, propName, propSrcValue):
    from Explorers.PrefsExplorer import UsedModuleSrcBsdPrefColNode
    import moduleparse

    prefsRcFile = os.path.join(Preferences.rcPath, rcFile)
    m = moduleparse.Module(rcFile, open(prefsRcFile).readlines())
    prefsRcNode = UsedModuleSrcBsdPrefColNode('', ('*',), prefsRcFile, -1, None,
                                              Preferences, True)
    newProp = (propName, propSrcValue, m.globals[propName])
    prefsRcNode.save(propName, newProp)


#---Registration API------------------------------------------------------------

def registerFileType(Controller, Model=None, newName='', addToNew=True,
                     aliasExts=()):
    """ Registers an IDE filetype that can be created from the New Palette page 
    """
    if Model is None:
        Model = Controller.Model

    EditorHelper.modelReg[Model.modelIdentifier] = Model
    if aliasExts:
        for ext in aliasExts:
            EditorHelper.extMap[ext] = Model

    Controllers.modelControllerReg[Model] = Controller

    if addToNew:
        if not newName:
            newName = Model.modelIdentifier
        PaletteStore.newControllers[newName] = Controller
        PaletteStore.paletteLists['New'].append(newName)

def registerFileTypes(*args):
    """ Convenience function for registerFileType, allows multiple Controller args """
    for Controller in args:
        registerFileType(Controller)

def registerPalettePage(paletteName, paletteTitle):
    """ Register a new page on the Palette"""
    if paletteName not in PaletteStore.paletteLists:
        PaletteStore.paletteLists[paletteName] = []
        PaletteStore.palette.append([paletteTitle, '', 
                                     PaletteStore.paletteLists[paletteName]])

def registerComponent(paletteName, Control, controlName, Companion):
    """ Registers a (design-time) component on the Palette """
    if paletteName is not None:
        PaletteStore.paletteLists[paletteName].append(Control)
    PaletteStore.compInfo[Control] = [controlName, Companion]

def registerComponents(paletteName, *components):
    """ Convenience function for registerComponent, allows multiple component tuples """
    for component in components:
        registerComponent(paletteName, *component)
    
def registerTool(name, func, bmp='-', key=''):
    """ Register an item in the Tools menu """
    EditorHelper.editorToolsReg.append( (name, func, bmp, key) )

def registerLanguageSTCStyle(name, lang, STCClass, stylesFile, insertPos=None):
    """ Register an STC mixin class and config file parameters that can be 
        configured under Preferences with the STC Style Editor """
    if insertPos is not None:
        ExplorerNodes.langStyleInfoReg.insert(insertPos, 
              (name, lang, STCClass, stylesFile ))
    else:
        ExplorerNodes.langStyleInfoReg.append(
              (name, lang, STCClass, stylesFile ))

def registerPreference(pluginName, prefName, defPrefValSrc, docs=[], info=''):
    """ Define a plug-in preference. Added to prefs.plug-ins.rc.py in needed """

    def addBlankLine(module, lineNo):
        module.addLine('', lineNo)
        return lineNo + 1
        
    Preferences.exportedPluginProps.append(prefName)
    # quick exit when name already exists
    if hasattr(Preferences, prefName):
        return 
    
    pluginPrefs = os.path.join(Preferences.rcPath, 'prefs_plugins_rc.py')
    lines = [l.rstrip() for l in open(pluginPrefs).readlines()]
    import moduleparse
    m = moduleparse.Module(pluginName, lines)
    # if not m.globals.has_key(prefName):
    if prefName not in m.globals:
        breakLineNames = m.break_lines.values()
        if pluginName not in breakLineNames:
            lineNo = addBlankLine(m, len(lines))
            lineNo = addBlankLine(m, lineNo)
            m.addLine('#-%s%s'%(pluginName, '-' * (80-2-len(pluginName))), lineNo)
            lineNo = addBlankLine(m, lineNo + 1)
        else:
            for l, n in m.break_lines.items():
                if pluginName == n:
                    lineNo = l + 1
                    break
            else:
                lineNo = len(lines)
                
        if docs:
            for doc in docs:
                m.addLine('# %s'%doc, lineNo); lineNo += 1
        if info:
            m.addLine('## %s'%info, lineNo); lineNo += 1
        
        try:
            value = eval(defPrefValSrc, Preferences.__dict__)
        except Exception as err:
            raise PluginError(
                  (_('Could not create default value from "%s" for %s. (%s:%s)')%(
                  defPrefValSrc, prefName, err.__class__, err)))

        m.addLine('%s = %s'%(prefName, defPrefValSrc), lineNo)
        lineNo = addBlankLine(m, lineNo + 1)

        setattr(Preferences, prefName, value)
        open(pluginPrefs, 'wb').write(str.encode(os.linesep.join(m.source)))
    else:
        raise PluginError(
            _('%s not in Preferences, but is defined in globals of '
            'prefs_plugins_rc.py')%prefName)
    

    