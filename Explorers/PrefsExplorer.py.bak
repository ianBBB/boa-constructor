#-----------------------------------------------------------------------------
# Name:        PrefsExplorer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001/06/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2005
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Explorers.PrefsExplorer'
import os, sys, glob, pprint, imp
import types

import wx

import Preferences, Utils, Plugins
from Utils import _

import ExplorerNodes
from Models import EditorHelper
from Views import STCStyleEditor
import methodparse, relpath

class PreferenceGroupNode(ExplorerNodes.ExplorerNode):
    """ Represents a group of preference collections """
    protocol = 'prefs.group'
    defName = 'PrefsGroup'
    def __init__(self, name, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, name, None,
              EditorHelper.imgPrefsFolder, None)

        self.vetoSort = True
        self.preferences = []

    def isFolderish(self):
        return True

    def openList(self):
        return self.preferences

    def notifyBeginLabelEdit(self, event):
        event.Veto()

class BoaPrefGroupNode(PreferenceGroupNode):
    """ The Preference node in the Explorer """
    protocol = 'boa.prefs.group'
    customPrefs = [] # list of tuples ('name', 'file')
    def __init__(self, parent):
        PreferenceGroupNode.__init__(self, _('Preferences'), parent)
        self.bold = True

        prefImgIdx = EditorHelper.imgSystemObj
        stcPrefImgIdx = EditorHelper.imgPrefsSTCStyles

        self.source_pref = PreferenceGroupNode(_('Source'), self)

        self.source_pref.preferences = [
            UsedModuleSrcBsdPrefColNode(_('Default settings'),
                Preferences.exportedSTCProps, os.path.join(Preferences.rcPath,
                'prefs_rc.py'), prefImgIdx, self, Preferences, True)]

        for name, lang, STCClass, stylesFile in ExplorerNodes.langStyleInfoReg:
            if not os.path.isabs(stylesFile):
                stylesFile = os.path.join(Preferences.rcPath, stylesFile)
            self.source_pref.preferences.append(STCStyleEditPrefsCollNode(
                  name, lang, STCClass, stylesFile, stcPrefImgIdx, self))
        self.preferences.append(self.source_pref)

        self.general_pref = UsedModuleSrcBsdPrefColNode(_('General'),
            Preferences.exportedProperties, os.path.join(Preferences.rcPath,
            'prefs_rc.py'), prefImgIdx, self, Preferences)
        self.preferences.append(self.general_pref)

        self.platform_pref = UsedModuleSrcBsdPrefColNode(_('Platform specific'),
            Preferences.exportedProperties2, os.path.join(Preferences.rcPath,
            'prefs_%s_rc.py' % Preferences.thisPlatform),
            prefImgIdx, self, Preferences)
        self.preferences.append(self.platform_pref)

        self.keys_pref = KeyDefsSrcPrefColNode(_('Key bindings'), ('*',),
            os.path.join(Preferences.rcPath, 'prefs_keys_rc.py'), prefImgIdx,
            self, Preferences.keyDefs)
        self.preferences.append(self.keys_pref)

        for name, filename in self.customPrefs:
            if not os.path.isabs(filename):
                filename = os.path.join(Preferences.rcPath, filename)
            self.preferences.append(UsedModuleSrcBsdPrefColNode(name,
            ('*',), filename, prefImgIdx, self, Preferences))

##        self.pychecker_pref = SourceBasedPrefColNode('PyChecker',
##            ('*',), Preferences.pyPath+'/.pycheckrc', prefImgIdx, self)
##        self.preferences.append(self.pychecker_pref)

        self.plugin_pref = PreferenceGroupNode(_('Plug-ins'), self)

        self.core_plugpref = UsedModuleSrcBsdPrefColNode(_('Core support'),
            Preferences.exportedCorePluginProps, os.path.join(Preferences.rcPath,
            'prefs_rc.py'), prefImgIdx, self, Preferences, True)
        self.plugin_plugpref = UsedModuleSrcBsdPrefColNode(_('Preferences'), Preferences.exportedPluginProps,#('*',),
            os.path.join(Preferences.rcPath, 'prefs_plugins_rc.py'), prefImgIdx,
            self, Preferences, True)
        self.files_plugpref = PluginFilesGroupNode()
        self.transp_plugpref = PreferenceGroupNode(_('Transports'), self)
        self.transp_plugpref.preferences = [
            TransportPluginsLoadOrderGroupNode(),
            TransportPluginsTreeDisplayOrderGroupNode(),
        ]

        self.plugin_pref.preferences = [
            self.files_plugpref,
            self.transp_plugpref,
            self.core_plugpref,
            self.plugin_plugpref,
        ]

        self.preferences.insert(1, self.plugin_pref)

        self.help_pref = HelpConfigBooksPGN()

        self.preferences.insert(2, self.help_pref)


class PreferenceCollectionNode(ExplorerNodes.ExplorerNode):
    """ Represents an inspectable preference collection """
    protocol = 'prefs'
    def __init__(self, name, props, resourcepath, imgIdx, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None,
              imgIdx, None, props)

    def open(self, editor):
        """ Populate inspector with preference items """
        comp = PreferenceCompanion(self.name, self)
        comp.updateProps()

        # Select in inspector
        editor.inspector.restore()
        if editor.inspector.pages.GetSelection() != 1:
            editor.inspector.pages.SetSelection(1)
        editor.inspector.selectObject(comp, False)
        return None, None

    def isFolderish(self):
        return False

    def load(self):
        raise Exception, _('Not implemented')

    def save(self, filename, data):
        pass

    def notifyBeginLabelEdit(self, event):
        event.Veto()

class STCStyleEditPrefsCollNode(PreferenceCollectionNode):
    protocol = 'stc.prefs'
    def __init__(self, name, lang, STCclass, resourcepath, imgIdx, parent):
        PreferenceCollectionNode.__init__(self, name, {}, resourcepath, imgIdx, parent)
        self.language = lang
        self.STCclass = STCclass

    def open(self, editor):
        # build list of all open STC's in the Editor
        openSTCViews = []
        for modPge in editor.modules.values():
            for view in modPge.model.views.values():
                if isinstance(view, self.STCclass):
                    openSTCViews.append(view)

        # also check the shell
        if Preferences.psPythonShell == 'Shell':
            if isinstance(editor.shell, self.STCclass):
                openSTCViews.append(editor.shell)
        #elif Preferences.psPythonShell == 'PyCrust':
        #    if self.language == 'python':
        #        openSTCViews.append(editor.shell.shellWin)

        dlg = STCStyleEditor.STCStyleEditDlg(editor, self.name, self.language,
              self.resourcepath, openSTCViews)
        try: dlg.ShowModal()
        finally: dlg.Destroy()

        return None, None

    def getURI(self):
        return '%s://%s' %(PreferenceCollectionNode.getURI(self), self.language)


class SourceBasedPrefColNode(PreferenceCollectionNode):
    """ Preference collection represented by the global names in python module

    Only names which are also defined in properties are returned
    except when properties is a special match all tuple; ('*',)

    This only applies to names assigned to values ( x = 123 ) not to global
    names defined by classes functions and imports.
    """
    def __init__(self, name, props, resourcepath, imgIdx, parent, showBreaks=True):
        PreferenceCollectionNode.__init__(self, name, props, resourcepath,
              imgIdx, parent)
        self.showBreakLines = showBreaks

    def load(self):
        # All preferences are local
        import moduleparse

        module = moduleparse.Module(self.name,
              open(self.resourcepath).readlines())

        values = []
        comments = []
        options = []
        # keep only names defined in the property list
        for name in module.global_order[:]:
            if name[0] == '_' or self.properties != ('*',) and \
                  name not in self.properties:
                module.global_order.remove(name)
                del module.globals[name]
            else:
                # XXX Should handle multiline assign
                code = '\n'.join(module.source[\
                      module.globals[name].start-1 : \
                      module.globals[name].end])

                # Extract value
                s = code.find('=')
                if s != -1:
                    values.append(code[s+1:].strip())
                else:
                    values.append('')

                # Read possible comment/help or options
                comment = []
                option = ''
                idx = module.globals[name].start-2
                while idx >= 0:
                    line = module.source[idx].strip()
                    if len(line) > 11 and line[:11] == '## options:':
                        option = line[11:].strip()
                        idx = idx - 1
                    elif len(line) > 8 and line[:8] == '## type:':
                        option = '##'+line[8:].strip()
                        idx = idx - 1
                    elif line and line[0] == '#':
                        comment.append(line[1:].lstrip())
                        idx = idx - 1
                    else:
                        break
                comment.reverse()
                comments.append(_('\n'.join(comment)))
                options.append(option)

        breaks = {}
        if self.showBreakLines: 
            for k, v in module.break_lines.items():
                breaks[k] = _(v)

        return (module.global_order, values, module.globals, comments, options,
                breaks)

    def save(self, filename, data):
        """ Updates one property """
        src = open(self.resourcepath).readlines()
        src[data[2].start-1] = '%s = %s\n' % (data[0], data[1])
        open(self.resourcepath, 'w').writelines(src)

class UsedModuleSrcBsdPrefColNode(SourceBasedPrefColNode):
    """ Also update the value of a global attribute of an imported module """
    def __init__(self, name, props, resourcepath, imgIdx, parent, module,
          showBreaks=True):
        SourceBasedPrefColNode.__init__(self, name, props, resourcepath, imgIdx,
              parent, showBreaks)
        self.module = module

    def save(self, filename, data):
        SourceBasedPrefColNode.save(self, filename, data)
        if hasattr(self.module, data[0]):
            setattr(self.module, data[0], eval(data[1], vars(Preferences)))

class KeyDefsSrcPrefColNode(PreferenceCollectionNode):
    """ Preference collection representing the key bindings """
    def __init__(self, name, props, resourcepath, imgIdx, parent, keyDefs):
        PreferenceCollectionNode.__init__(self, name, props, resourcepath,
              imgIdx, parent)
        self.showBreakLines = True
        self._editor = None

    def open(self, editor):
        PreferenceCollectionNode.open(self, editor)
        self._editor = editor

    def load(self):
        import moduleparse

        src = open(self.resourcepath).readlines()
        module = moduleparse.Module(self.name, src)

        # find keydefs
        keydefs = {}
        names = []
        values = []
        start = end = idx = -1
        for line in src:
            idx = idx + 1
            line = line.strip()
            if line == 'keyDefs = {':
                start = idx
            elif start != -1 and line:
                if line[-1] == '}':
                    end = idx
                    break
                elif line[0] != '#':
                    colon = line.find(':')
                    if colon == -1: raise Exception(_('Invalid KeyDef item: %s')%line)
                    name = line[:colon].rstrip()[1:-1]
                    val = line[colon+1:].lstrip()
                    keydefs[name] = moduleparse.CodeBlock(val, idx+1, idx+1)
                    names.append(name)
                    values.append(val)

        return (names, values, keydefs, ['']*len(keydefs),
              ['## keydef']*len(keydefs), module.break_lines)

    def save(self, filename, data):
        """ Updates one key:val in keydefs dict """

        # Update source file
        src = open(self.resourcepath).readlines()
        src[data[2].start-1] = \
              "  '%s'%s: %s\n" % (data[0], (12 - len(data[0]))*' ', data[1])
        open(self.resourcepath, 'w').writelines(src)
        # Update dictionary
        Preferences.keyDefs[data[0]] = eval(data[1], vars(Preferences))[0]
        # Update editor menus
        self._editor.setupToolBar()
        self._editor.updateStaticMenuShortcuts()
        self._editor.shell.bindShortcuts()


class ConfigBasedPrefsColNode(PreferenceCollectionNode):
    """ Preferences driven by config files """
    pass


#---Companions------------------------------------------------------------------

from PropEdit import PropertyEditors, InspectorEditorControls

class KeyDefConfPropEdit(PropertyEditors.ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        import KeyDefsDlg
        dlg = KeyDefsDlg.KeyDefsDialog(self.parent, self.name, self.value)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.editorCtrl.value = dlg.result
                self.inspectorPost(False)
        finally:
            dlg.Destroy()

    def getDisplayValue(self):
        try:
            return eval(self.value, {'wx': wx})[0][2]
        except Exception, err:
            return str(err)


class LanguagesConfPropEdit(PropertyEditors.ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.ChoiceIEC(self, self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)
  
    def getValues(self):
        all = [n for n in dir(wx) if n.startswith('LANGUAGE_') ]
        avl = []
        for n in all:
            try: 
                if wx.Locale.IsAvailable(getattr(wx, n)):
                    avl.append('wx.'+n)
            except wx.PyAssertionError: 
                # invalid language assertions
                pass
            except AttributeError:
                # wx version < 2.7
                avl.append('wx.'+n)
        return avl
        
class PreferenceCompanion(ExplorerNodes.ExplorerCompanion):
    def __init__(self, name, prefNode, ):
        ExplorerNodes.ExplorerCompanion.__init__(self, name)
        self.prefNode = prefNode

        self._breaks = {}

    typeMap = {}
    customTypeMap = {'filepath': PropertyEditors.FilepathConfPropEdit,
                     'dirpath': PropertyEditors.DirpathConfPropEdit,
                     'keydef': KeyDefConfPropEdit,
                     'languages': LanguagesConfPropEdit}
                     
    def getPropEditor(self, prop):
        # XXX Using name equality to identify _breaks' prop edit is ugly !
        for aProp in self.propItems:
            if aProp[0] == prop: break
        else:
            raise Exception(_('Property "%s" not found')%prop)

        srcVal = aProp[1]
        opts = aProp[4]

        if prop in self._breaks.values():
            return None

        if opts:
            if opts[:2] == '##':
                return self.customTypeMap.get(opts[2:].strip(), None)
            else:
                return PropertyEditors.EnumConfPropEdit

        if srcVal.lower() in ('true', 'false'):
            return PropertyEditors.BoolConfPropEdit

        try:
            val = eval(srcVal, vars(Preferences))
        except Exception, error:
            return PropertyEditors.StrConfPropEdit

        if isinstance(val, wx.Colour):
            return PropertyEditors.ColourConfPropEdit
        return self.typeMap.get(type(val), PropertyEditors.StrConfPropEdit)

    def getPropertyHelp(self, propName):
        for prop in self.propItems:
            if prop[0] == propName: return prop[3]
        else:
            return propName

    def getPropertyItems(self):
        order, vals, props, comments, options, self._breaks = self.prefNode.load()

        # remove empty break lines (-----------------------)
        for lineNo in self._breaks.keys():
            if not self._breaks[lineNo]:
                del self._breaks[lineNo]

        breakLinenos = self._breaks.keys()
        breakLinenos.sort()
        if len(breakLinenos):
            breaksIdx = 0
        else:
            breaksIdx = None

        res = []
        for name, value, comment, option in map(None, order, vals, comments, options):
            if breaksIdx is not None:
                # find closest break above property
                while breaksIdx < len(breakLinenos)-1 and \
                      props[name].start > breakLinenos[breaksIdx+1]:
                    breaksIdx += 1

                if breaksIdx >= len(breakLinenos):
                    breaksIdx = None

                if breaksIdx is not None and props[name].start > breakLinenos[breaksIdx]:
                    res.append( (self._breaks[breakLinenos[breaksIdx]], '', None, '', '') )
                    breaksIdx += 1
                    #if breaksIdx == len(self._breaks) -1:
                    #    breaksIdx = None
                    #else:
                    #    breaksIdx = breaksIdx + 1
            res.append( (name, value, props[name], comment, option) )
        return res

    def setPropHook(self, name, value, oldProp):
        # XXX validate etc.
        try:
            eval(value, vars(Preferences))
        except Exception, error:
            wx.LogError('Error: '+str(error))
            return False
        else:
            newProp = (name, value) + oldProp[2:]
            self.prefNode.save(name, newProp)
            return True

    def persistedPropVal(self, name, setterName):
        if name in self._breaks.values():
            return 'PROP_CATEGORY'
        else:
            return None

    def getPropOptions(self, name):
        for prop in self.propItems:
            if prop[0] == name:
                strOpts = prop[4]
                if strOpts and strOpts[:2] != '##':
                    return self.eval(strOpts)
                else:
                    return ()
        else:
            return ()

    def getPropNames(self, name):
        for prop in self.propItems:
            if prop[0] == name:
                strOpts = prop[4]
                if strOpts and strOpts[:2] != '##':
                    return methodparse.safesplitfields(strOpts, ',')
                else: return ()
        else:
            return ()

    def eval(self, expr):
        import PaletteMapping
        return PaletteMapping.evalCtrl(expr, vars(Preferences))

##    def GetProp(self, name):
##        ExplorerNodes.ExplorerCompanion.GetProp(self, name)
##        return self.findProp(name)[0][1]

class CorePluginsGroupNode(PreferenceGroupNode):
    """ """
    protocol = 'prefs.group.plug-in.core'
    defName = 'CorePluginPrefsGroup'
    def __init__(self):
        name = _('Core support')
        PreferenceGroupNode.__init__(self, name, None)

        self.vetoSort = True
        self.preferences = []

    def isFolderish(self):
        return True

    def openList(self):
        return self.preferences

    def notifyBeginLabelEdit(self, event):
        event.Veto()

def getPluginSection(pluginFile):
    pluginPath = os.path.dirname(pluginFile)
    return Preferences.pluginSections[
              Preferences.pluginPaths.index(pluginPath)]

class PluginFileExplNode(ExplorerNodes.ExplorerNode):
    """  """
    def __init__(self, name, enabled, status, resourcepath, imgIdx):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None,
              imgIdx, None, {})
        self.pluginEnabled = enabled
        self.pluginStatus = status

    def open(self, editor):
        """  """
        if self.pluginEnabled:
            msg = _('Disable')
        else:
            msg = _('Enable')

        if wx.MessageBox('%s %s?'%(msg, self.name), _('Confirm Toggle Plug-in'),
              wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            section = getPluginSection(self.resourcepath)
            ordered, disabled = Plugins.readPluginsState(section)

            if self.pluginEnabled:
                disabled.append(self.name)
            else:
                try:
                    disabled.remove(self.name)
                except ValueError:
                    pass

            #Plugins.writeInitPluginGlobals(initPluginPath, initPluginGlobals)
            Plugins.writePluginsState(section, ordered, disabled)

            editor.explorer.list.refreshCurrent()

        return None, None

    def getURI(self):
        return '%s (%s)'%(ExplorerNodes.ExplorerNode.getURI(self),
                          self.pluginStatus)

    def isFolderish(self):
        return False

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def changeOrder(self, direction):
        section = getPluginSection(self.resourcepath)
        #initPluginPath = os.path.dirname(self.resourcepath)
        ordered, disabled = Plugins.readPluginsState(section)
        #ordered = initPluginGlobals['__ordered__']
        try:
            idx = ordered.index(self.name)
        except ValueError:
            idx = len(ordered)+1
        else:
            del ordered[idx]
        idx = max(idx + direction, 0)
        if idx <= len(ordered):
            ordered.insert(idx, self.name)
        #Plugins.writeInitPluginGlobals(initPluginPath, initPluginGlobals)
        Plugins.writePluginsState(section, ordered, disabled)


class PluginFilesGroupNode(PreferenceGroupNode):
    """ Represents a group of preference collections """
    protocol = 'prefs.group.plug-in.files'
    defName = 'PluginFilesPrefsGroup'
    def __init__(self):
        name = _('Plug-in files')
        PreferenceGroupNode.__init__(self, name, None)

    def openList(self):
        res = []
        splitext = os.path.splitext
        for filename, ordered, enabled in Plugins.buildPluginExecList():
            if os.path.basename(filename) == '__init__.plug-in.py':
                continue

            name = splitext(splitext(os.path.basename(filename))[0])[0]
            if not enabled:
                name = splitext(name)[0]
                status = _('Disabled')
                imgIdx = EditorHelper.imgSystemObjDisabled
            else:
                fn = filename.lower()
                if Preferences.failedPlugins.has_key(fn):
                    kind, msg = Preferences.failedPlugins[fn]
                    if kind == 'Skipped':
                        status = _('Skipped plug-in: %s')% msg
                        imgIdx = EditorHelper.imgSystemObjPending
                    else:
                        status = _('Broken plug-in: %s')% msg
                        imgIdx = EditorHelper.imgSystemObjBroken
                elif fn in Preferences.installedPlugins:
                    if ordered:
                        status = _('Installed, ordered')
                        imgIdx = EditorHelper.imgSystemObjOrdered
                    else:
                        status = _('Installed')
                        imgIdx = EditorHelper.imgSystemObj
                else:
                    status = _('Pending restart')
                    imgIdx = EditorHelper.imgSystemObjPending

            res.append(PluginFileExplNode(name, enabled, status, filename, imgIdx))
        return res


class PluginFilesGroupNodeController(ExplorerNodes.Controller):
    moveUpBmp = 'Images/Shared/up.png'
    moveDownBmp = 'Images/Shared/down.png'

    itemDescr = _('item')

    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.Menu()

        [wxID_PF_TOGGLE, wxID_PF_OPEN, wxID_PF_UP, wxID_PF_DOWN] = Utils.wxNewIds(4)

        self.transpMenuDef = [ (wxID_PF_TOGGLE, _('Toggle Enable/Disabled'),
                                self.OnToggleState, '-'),
                               (wxID_PF_OPEN, _('Open plug-in file'),
                                self.OnOpenPlugin, '-'),
                               (-1, '-', None, ''),
                               (wxID_PF_UP, _('Move up'),
                                self.OnMovePluginUp, self.moveUpBmp),
                               (wxID_PF_DOWN, _('Move down'),
                                self.OnMovePluginDown, self.moveDownBmp),
                             ]

        self.setupMenu(self.menu, self.list, self.transpMenuDef)
        self.toolbarMenus = [self.transpMenuDef]

    def destroy(self):
        self.transpMenuDef = []
        self.toolbarMenus = []
        self.menu.Destroy()

    def OnToggleState(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            for node in nodes:
                node.open(self.editor)

    def OnOpenPlugin(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            for node in nodes:
                self.editor.openOrGotoModule(node.resourcepath)

    def OnMovePluginUp(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only move 1 at a time'))
            else:
                node = nodes[0]
                idx = self.list.items.index(node)
                if idx == 0:
                    wx.LogError(_('Already at the beginning'))
                else:
                    name = node.name
                    node.changeOrder(-1)
                    self.list.refreshCurrent()
                    self.list.selectItemNamed(name)

    def OnMovePluginDown(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only move 1 at a time'))
            else:
                node = nodes[0]
                idx = self.list.items.index(node)
##                if idx >= len(self.list.items) -1:
##                    wx.LogError('Already at the end')
##                else:
                name = node.name
                node.changeOrder(1)
                self.list.refreshCurrent()
                self.list.selectItemNamed(name)



class TransportPluginExplNode(ExplorerNodes.ExplorerNode):
    """  """
    protocol = 'transport'
    def __init__(self, name, status, imgIdx):
        ExplorerNodes.ExplorerNode.__init__(self, name, '%s (%s)'%(name, status),
              None, imgIdx, None, {})
        self.status = status


    def open(self, editor):
        return None, None

class TransportPluginsController(ExplorerNodes.Controller):
    addItemBmp = 'Images/Shared/NewItem.png'
    removeItemBmp = 'Images/Shared/DeleteItem.png'
    moveUpBmp = 'Images/Shared/up.png'
    moveDownBmp = 'Images/Shared/down.png'

    itemDescr = _('item')

    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.Menu()

        [wxID_TP_NEW, wxID_TP_DEL, wxID_TP_UP, wxID_TP_DOWN] = Utils.wxNewIds(4)

        self.transpMenuDef = [ (wxID_TP_NEW, _('Add new %s')%self.itemDescr,
                                self.OnNewTransport, self.addItemBmp),
                               (wxID_TP_DEL, _('Remove %s')%self.itemDescr,
                                self.OnDeleteTransport, self.removeItemBmp),
                               (-1, '-', None, ''),
                               (wxID_TP_UP, _('Move up'),
                                self.OnMoveTransportUp, self.moveUpBmp),
                               (wxID_TP_DOWN, _('Move down'),
                                self.OnMoveTransportDown, self.moveDownBmp),
                             ]

        self.setupMenu(self.menu, self.list, self.transpMenuDef)
        self.toolbarMenus = [self.transpMenuDef]

    def destroy(self):
        self.transpMenuDef = []
        self.toolbarMenus = []
        self.menu.Destroy()

    def editorUpdateNotify(self, info=''):
        self.OnReloadItems()

    def OnReloadItems(self, event=None):
        if self.list.node:
            self.list.refreshCurrent()

    def moveTransport(self, node, idx, direc):
        names = []
        for item in self.list.items:
            names.append(item.name)

        name = names[idx]
        del names[idx]
        names.insert(idx + direc, name)

        self.list.node.updateOrder(names)

        self.list.refreshCurrent()
        self.list.selectItemByIdx(idx+direc+1)

    def OnMoveTransportUp(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only move 1 at a time'))
            else:
                node = nodes[0]
                idx = self.list.items.index(node)
                if idx == 0:
                    wx.LogError(_('Already at the beginning'))
                else:
                    self.moveTransport(node, idx, -1)

    def OnMoveTransportDown(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only move 1 at a time'))
            else:
                node = nodes[0]
                idx = self.list.items.index(node)
                if idx >= len(self.list.items) -1:
                    wx.LogError(_('Already at the end'))
                else:
                    self.moveTransport(node, idx, 1)

    def OnNewTransport(self, event):
        pass

    def OnDeleteTransport(self, event):
        pass

class TransportPluginsLoadOrderController(TransportPluginsController):
    itemDescr = _('Transport module')

    def OnNewTransport(self, event):
        dlg = wx.TextEntryDialog(self.list, _('Enter the fully qualified Python '\
               'object path to \nthe Transport module. E.g. Explorers.FileExplorer'),
               _('New Transport'), '')
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            transportModulePath = dlg.GetValue()
        finally:
            dlg.Destroy()

        if not self.list.node.checkValidModulePath(transportModulePath):
            if wx.MessageBox(_('Cannot locate the specified module path,\n'\
                         'are you sure you want to continue?'),
                         _('Module not found'),
                         wx.YES_NO | wx.ICON_EXCLAMATION) == wx.NO:
                return

        names = []
        for item in self.list.items:
            names.append(item.name)

        names.append(transportModulePath)

        self.list.node.updateOrder(names)

        self.list.refreshCurrent()

    def OnDeleteTransport(self, event):
        selNames = self.list.getMultiSelection()
        nodes = self.getNodesForSelection(selNames)

        names = []
        for item in self.list.items:
            names.append(item.name)

        for item in nodes:
            names.remove(item.name)

        self.list.node.updateOrder(names)

        self.list.refreshCurrent()

class TransportPluginsTreeDisplayOrderController(TransportPluginsController):
    itemDescr = _('Transports tree node')

    def OnNewTransport(self, event):
        dlg = wx.TextEntryDialog(self.list, _('Enter the protocol identifier. E.g. '\
               'ftp, ssh'), _('New Transports Tree Node'), '')
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            protocol = dlg.GetValue()
        finally:
            dlg.Destroy()

        names = []
        for item in self.list.items:
            names.append(item.name)

        names.append(protocol)

        self.list.node.updateOrder(names)
        self.list.node.checkConfigEntry(protocol)

        self.list.refreshCurrent()

    def OnDeleteTransport(self, event):
        selNames = self.list.getMultiSelection()
        nodes = self.getNodesForSelection(selNames)

        names = []
        for item in self.list.items:
            names.append(item.name)

        for item in nodes:
            names.remove(item.name)
            self.list.node.clearEmptyConfigEntry(item.name)

        self.list.node.updateOrder(names)

        self.list.refreshCurrent()


class TransportPluginsLoadOrderGroupNode(PreferenceGroupNode):
    """  """
    protocol = 'prefs.group.plug-in.transport.load-order'
    defName = 'TransportPluginsPrefsGroup'
    def __init__(self):
        name = _('Loading order')
        PreferenceGroupNode.__init__(self, name, None)

    def openList(self):
        conf = Utils.createAndReadConfig('Explorer')

        modules = eval(conf.get('explorer', 'installedtransports'), {})
        assert isinstance(modules, types.ListType)

        res = []
        for mod in modules:
            if mod in ExplorerNodes.installedModules:
                status = _('Installed')
                imgIdx = EditorHelper.imgSystemObjOrdered
            elif mod in ExplorerNodes.failedModules.keys():
                status = _('Broken: %s')%ExplorerNodes.failedModules[mod]
                imgIdx = EditorHelper.imgSystemObjBroken
            else:
                status = _('Pending restart')
                imgIdx = EditorHelper.imgSystemObjPending

            res.append(TransportPluginExplNode(mod, status, imgIdx))
        return res

    def updateOrder(self, newOrder):
        conf = Utils.createAndReadConfig('Explorer')
        conf.set('explorer', 'installedtransports', pprint.pformat(newOrder))
        Utils.writeConfig(conf)

    def checkValidModulePath(self, name):
        try:
            Utils.find_dotted_module(name)
        except ImportError, err:
            #print str(err)
            return False
        else:
            return True


class TransportPluginsTreeDisplayOrderGroupNode(PreferenceGroupNode):
    """  """
    protocol = 'prefs.group.plug-in.transport.tree-order'
    defName = 'TransportPluginsPrefsGroup'
    def __init__(self):
        name = _('Tree display order')
        PreferenceGroupNode.__init__(self, name, None)

    def openList(self):
        conf = Utils.createAndReadConfig('Explorer')

        treeOrder = eval(conf.get('explorer', 'transportstree'), {})
        assert isinstance(treeOrder, type([]))

        res = []
        for prot in treeOrder:
            if not ExplorerNodes.nodeRegByProt.has_key(prot):
                status = _('Protocol not installed')
                imgIdx = EditorHelper.imgSystemObjPending
            else:
                status = _('Installed')
                imgIdx = EditorHelper.imgSystemObjOrdered

            res.append(TransportPluginExplNode(prot, status, imgIdx))
        return res

    def updateOrder(self, newOrder):
        conf = Utils.createAndReadConfig('Explorer')
        conf.set('explorer', 'transportstree', pprint.pformat(newOrder))
        Utils.writeConfig(conf)

    def checkConfigEntry(self, protocol):
        conf = Utils.createAndReadConfig('Explorer')
        if not conf.has_option('explorer', protocol):
            conf.set('explorer', protocol, '{}')
        Utils.writeConfig(conf)

    def clearEmptyConfigEntry(self, protocol):
        conf = Utils.createAndReadConfig('Explorer')
        if conf.has_option('explorer', protocol) and \
              eval(conf.get('explorer', protocol).strip(), {}) == {}:
            conf.remove_option('explorer', protocol)
            Utils.writeConfig(conf)


class HelpConfigPGN(PreferenceGroupNode):
    """  """
    protocol = 'prefs.group.help.config'
    defName = 'HelpConfigPrefsGroup'
    def __init__(self):
        name = _('Help system')
        PreferenceGroupNode.__init__(self, name, None)

    def openList(self):
        return


class HelpConfigBooksPGN(PreferenceGroupNode):
    """  """
    protocol = 'prefs.group.help.config.books'
    defName = 'HelpConfigBooksPrefsGroup'
    def __init__(self):
        name = _('Help books')
        PreferenceGroupNode.__init__(self, name, None)

    def openList(self):
        bookPaths = self.readBooks()
        res = []
        for bookPath in bookPaths:
            try:
                res.append(HelpConfigBookNode(bookPath))
            except IOError, err:
                # too disruptive to display an error
                pass
        return res

#        return [HelpConfigBookNode(bookPath)
#                for bookPath in bookPaths]


    def readBooks(self):
        return eval(Utils.createAndReadConfig('Explorer').get('help', 'books'), {})

    def writeBooks(self, books):
        conf = Utils.createAndReadConfig('Explorer')
        conf.set('help', 'books', pprint.pformat(books))
        Utils.writeConfig(conf)


    def preparePath(self, path):
        helpPath = Preferences.pyPath+'/Docs/'

        if path.startswith('file://'):
            path = path[7:]

        # Add relative paths for files inside Docs directory
        if os.path.normcase(path).startswith(os.path.normcase(helpPath)):
            return path[len(helpPath):]
        else:
            return path

    def editBook(self, curPath, newPath):
        books = self.readBooks()
        books[books.index(curPath)] = self.preparePath(newPath)
        self.writeBooks(books)

    def addBook(self, path):
        path = self.preparePath(path)
        self.writeBooks(self.readBooks() + [path])

    def removeBook(self, path):
        books = self.readBooks()
        books.remove(path)
        self.writeBooks(books)

    def updateOrder(self, paths):
        self.writeBooks(paths)


class HelpConfigBookNode(ExplorerNodes.ExplorerNode):
    """  """
    protocol = 'help.book'
    def __init__(self, resourcepath):
        fullpath = self.getAbsPath(resourcepath)

        name = os.path.basename(resourcepath)
        if os.path.splitext(fullpath)[1] == '.hhp':
            # Peek at title inside hhp file
            for line in open(fullpath).readlines():
                if line.startswith('Title'):
                    name = line.split('=')[1].strip()

        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None,
              EditorHelper.imgHelpBook, None, {})

    def open(self, editor):
        return None, None

##    def getURI(self):
##        return '%s (%s)'%(ExplorerNodes.ExplorerNode.getURI(self),
##                          self.pluginStatus)

    def isFolderish(self):
        return False

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def getAbsPath(self, resourcepath):
        if not os.path.isabs(resourcepath):
            return os.path.join(Preferences.pyPath, 'Docs', resourcepath)
        else:
            return resourcepath



class HelpConfigBooksController(ExplorerNodes.Controller):
    addItemBmp = 'Images/Shared/NewItem.png'
    removeItemBmp = 'Images/Shared/DeleteItem.png'
    moveUpBmp = 'Images/Shared/up.png'
    moveDownBmp = 'Images/Shared/down.png'

    itemDescr = _('item')

    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.Menu()

        [wxID_HB_EDIT, wxID_HB_NEW, wxID_HB_DEL, wxID_HB_UP, wxID_HB_DOWN,
         wxID_HB_REST, wxID_HB_CLRI, wxID_HB_OPEN] = Utils.wxNewIds(8)

        self.helpBooksMenuDef = [ (wxID_HB_EDIT, _('Edit %s')%self.itemDescr,
                                   self.OnEditBookPath, '-'),
                                  (wxID_HB_NEW, _('Add new %s')%self.itemDescr,
                                   self.OnNewBook, self.addItemBmp),
                                  (wxID_HB_DEL, _('Remove %s')%self.itemDescr,
                                   self.OnRemoveBook, self.removeItemBmp),
                                  (-1, '-', None, ''),
                                  (wxID_HB_UP, _('Move up'),
                                   self.OnMoveBookUp, self.moveUpBmp),
                                  (wxID_HB_DOWN, _('Move down'),
                                   self.OnMoveBookDown, self.moveDownBmp),
                                  (-1, '-', None, '-'),
                                  (wxID_HB_OPEN, _('Open hhp file'),
                                   self.OnOpenHHP, '-'),
                                  (-1, '-', None, '-'),
                                  (wxID_HB_REST, _('Restart the help system'),
                                   self.OnRestartHelp, '-'),
                                  (wxID_HB_CLRI, _('Clear the help indexes'),
                                   self.OnClearHelpIndexes, '-'),
                                ]

        self.setupMenu(self.menu, self.list, self.helpBooksMenuDef)
        self.toolbarMenus = [self.helpBooksMenuDef]

    def destroy(self):
        self.helpBooksMenuDef = ()
        self.toolbarMenus = ()
        self.menu.Destroy()

    def editorUpdateNotify(self, info=''):
        self.OnReloadItems()

    def OnReloadItems(self, event=None):
        if self.list.node:
            self.list.refreshCurrent()

    def moveBook(self, node, idx, direc):
        paths = [item.resourcepath for item in self.list.items]

        path = paths[idx]
        del paths[idx]
        paths.insert(idx + direc, path)

        self.list.node.updateOrder(paths)

        self.list.refreshCurrent()
        self.list.selectItemByIdx(idx+direc+1)

    def OnMoveBookUp(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only move 1 at a time'))
            else:
                node = nodes[0]
                idx = self.list.items.index(node)
                if idx == 0:
                    wx.LogError(_('Already at the beginning'))
                else:
                    self.moveBook(node, idx, -1)

    def OnMoveBookDown(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            nodes = self.getNodesForSelection(ms)
            if len(nodes) != 1:
                wx.LogError(_('Can only move 1 at a time'))
            else:
                node = nodes[0]
                idx = self.list.items.index(node)
                if idx >= len(self.list.items) -1:
                    wx.LogError(_('Already at the end'))
                else:
                    self.moveBook(node, idx, 1)

    def OnEditBookPath(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            for node in self.getNodesForSelection(ms):
                if not os.path.isabs(node.resourcepath):
                    path = os.path.join(Preferences.pyPath,
                                        'Docs', node.resourcepath)
                else:
                    path = node.resourcepath

                curpath, curfile = os.path.split(path)
                newpath = self.editor.openFileDlg('AllFiles', curdir=curpath)
                if newpath:
                    self.list.node.editBook(node.resourcepath, path)
                    self.list.refreshCurrent()

    def OnNewBook(self, event):
        path = self.editor.openFileDlg('AllFiles', curdir=Preferences.pyPath+'/Docs')
        if path and self.list.node:
            self.list.node.addBook(path)
            self.list.refreshCurrent()

    def OnRemoveBook(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            for node in self.getNodesForSelection(ms):
                self.list.node.removeBook(node.resourcepath)
            self.list.refreshCurrent()

    def OnRestartHelp(self, event):
        import Help
        Help.delHelp()
        wx.Yield()
        Help.initHelp()

    def OnClearHelpIndexes(self, event):
        import Help

        cd = Help.getCacheDir()
        for name in os.listdir(cd):
            if os.path.splitext(name)[1] == '.cached':
                os.remove(os.path.join(cd, name))
                wx.LogMessage(_('Deleted %s')%name)

    def OnOpenHHP(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            for node in self.getNodesForSelection(ms):
                self.editor.openOrGotoModule(node.getAbsPath(node.resourcepath))

#-------------------------------------------------------------------------------


ExplorerNodes.register(BoaPrefGroupNode)
ExplorerNodes.register(PluginFilesGroupNode,
      controller=PluginFilesGroupNodeController)
ExplorerNodes.register(TransportPluginsLoadOrderGroupNode,
      controller=TransportPluginsLoadOrderController)
ExplorerNodes.register(TransportPluginsTreeDisplayOrderGroupNode,
      controller=TransportPluginsTreeDisplayOrderController)
ExplorerNodes.register(HelpConfigBooksPGN, controller=HelpConfigBooksController)
