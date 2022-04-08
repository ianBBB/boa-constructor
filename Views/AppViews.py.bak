#-----------------------------------------------------------------------------
# Name:        AppViews.py
# Purpose:     Views for application management
#
# Author:      Riaan Booysen
#
# Created:
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Views.AppViews'

""" View classes for the AppModel """

import os
import time

try:
    from cmp import cmp
except ImportError:
    from filecmp import cmp

import wx
import wx.stc

from EditorViews import ListCtrlView, ModuleDocView, wxwAppModuleTemplate, \
                        ToDoView, CloseableViewMix, FindResultsAdderMixin
import SourceViews
import Search, Utils
from Utils import _

class AppFindResults(ListCtrlView, CloseableViewMix):
    viewName = 'Application Find Results'
    viewTitle = _('Application Find Results')

    gotoLineBmp = 'Images/Editor/GotoLine.png'

    def __init__(self, parent, model):
        CloseableViewMix.__init__(self, _('find results'))
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          ( (_('Goto match'), self.OnGoto, self.gotoLineBmp, ''),
            (_('Rerun query'), self.OnRerun, '-', ''),
          ) +
            self.closingActionItems, 0)

        self.InsertColumn(0, _('Module'), width = 100)
        self.InsertColumn(1, _('Line no'), wx.LIST_FORMAT_CENTRE, 40)
        self.InsertColumn(2, _('Col'), wx.LIST_FORMAT_CENTRE, 40)
        self.InsertColumn(3, _('Text'), width = 550)

        self.results = {}
        self.listResultIdxs = []
        self.tabName = 'Results'
        self.findPattern = ''
        self.active = True
        self.model = model

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        i = 0
        self.listResultIdxs = []
        for mod in self.results.keys():
            for result in self.results[mod]:
                self.listResultIdxs.append((mod, result))
                i = self.addReportItems(i, (os.path.basename(mod), `result[0]`,
                  `result[1]`, result[2].strip()) )

        self.model.editor.statusBar.setHint(_('%d matches of "%s".')%(i, self.findPattern))

        self.pastelise()

    def OnGoto(self, event):
        if self.selected >= 0:
            modName = self.listResultIdxs[self.selected][0]
            model, cntrl = self.model.openModule(modName)
            srcView = model.views['Source']
            srcView.focus()
            foundInfo = self.listResultIdxs[self.selected][1]
            srcView.lastSearchPattern = self.findPattern
            srcView.lastSearchResults = self.results[modName]
            try:
                srcView.lastMatchPosition = self.results[modName].index(foundInfo)
            except:
                srcView.lastMatchPosition = 0
                #print 'foundInfo not found'

            srcView.selectSection(foundInfo[0], foundInfo[1], self.findPattern)

    def OnRerun(self, event):
        self.rerun(None)

# XXX Add 'Get description from module info' option
class AppView(ListCtrlView, FindResultsAdderMixin):
    viewName = 'Application'
    viewTitle = _('Application')

    openBmp = 'Images/Editor/OpenFromApp.png'
    addModBmp = 'Images/Editor/AddToApp.png'
    remModBmp = 'Images/Editor/RemoveFromApp.png'
    findBmp = 'Images/Shared/Find.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          ((_('Open'), self.OnOpen, self.openBmp, ''),
           ('-', None, '', ''),
           (_('Add'), self.OnAdd, self.addModBmp, 'Insert'),
           (_('Edit'), self.OnEdit, '-', ''),
           (_('Remove'), self.OnRemove, self.remModBmp, 'Delete'),
           ('-', None, '', ''),
           (_('Find'), self.OnFind, self.findBmp, 'Find'),
           ('-', None, '-', ''),
           (_('Make module main module'), self.OnMakeMain, '-', ''),
           ), 0)

        self.InsertColumn(0, _('Module'), width = 150)
        self.InsertColumn(1, _('Type'), width = 50)
        self.InsertColumn(2, _('Description'), width = 150)
        self.InsertColumn(3, _('Relative path'), width = 220)

        self.sortOnColumns = [0, 1, 3]

        self.SetImageList(model.editor.modelImageList, wx.IMAGE_LIST_SMALL)

        self.lastSearchPattern = ''
        self.active = True
        self.canExplore = True
        self.model = model

#        EVT_LIST_BEGIN_DRAG(self, self.GetId(), self.OnDrag)

#    def OnDrag(self, event):
#        print 'drag', event.GetString()
#        print 'drag', dir(event.__class__.__bases__[0])

    def explore(self):
        modSort = self.model.modules.keys()
        modSort.sort()
        return modSort

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        i = 0
        modSort = self.model.modules.keys()
        modSort.sort()
        for mod in modSort:
            # XXX Show a broken icon as default
            imgIdx = -1
            modTpe = 'Unknown'
            if self.model.moduleModels.has_key(mod):
                imgIdx = self.model.moduleModels[mod].imgIdx
                modTpe = self.model.moduleModels[mod].modelIdentifier
            else:
                self.model.idModel(mod)
                if self.model.moduleModels.has_key(mod):
                    imgIdx = self.model.moduleModels[mod].imgIdx
                    modTpe = self.model.moduleModels[mod].modelIdentifier

            appMod = self.model.modules[mod]

            if appMod[0]:
                modTpe = '*%s*'%modTpe

            i = self.addReportItems(i, (mod, modTpe, appMod[1], appMod[2]), imgIdx)

        self.pastelise()

    def OnOpen(self, event):
        if self.selected >= 0:
            # XXX maybe this should be done in the browsing framework
            self.model.openModule(self.GetItemText(self.selected))
            self.model.prevSwitch = self


    def OnAdd(self, event):
        self.model.viewAddModule()

    def OnEdit(self, event):
        name = self.GetItemText(self.selected)
        dlg = wx.TextEntryDialog(self, _('Set the description of the module'),
            _('Edit item'), self.model.modules[name][1])
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                self.model.editModule(name, name, self.model.modules[name][0],
                      answer)
                self.model.update()
                self.model.notify()
        finally:
            dlg.Destroy()

    def OnRemove(self, event):
        if self.selected >= 0:
            if not self.model.modules[self.GetItemText(self.selected)][0]:
                self.model.removeModule(self.GetItemText(self.selected))
            else:
                wx.MessageBox(_('Cannot remove the main frame of an application'),
                    _('Module remove error'))

    def OnImports(self, events):
        wx.BeginBusyCursor()
        try:
            self.model.showImportsView()
        finally:
            wx.EndBusyCursor()

        if self.model.views.has_key('Imports'):
            self.model.views['Imports'].focus()
        self.model.update()
        self.model.notify()

    def OnOpenAll(self, event):
        modules = self.model.modules.keys()
        modules.sort()
        for mod in modules:
            try:
                self.model.editor.openOrGotoModule(\
                  self.model.modules[mod][2])
            except: pass

    def OnFind(self, event):
        import FindReplaceDlg
        FindReplaceDlg.find(self, self.model.editor.finder, self)

    def OnMakeMain(self, event):
        if self.selected >= 0:
            self.model.changeMainFrameModule(self.GetItemText(self.selected))


class AppModuleDocView(ModuleDocView):
    viewName = 'Application Documentation'
    viewTitle = _('Application Documentation')

    def OnLinkClicked(self, linkinfo):
        url = linkinfo.GetHref()

        if url[0] == '#':
            self.base_OnLinkClicked(linkinfo)
        else:
            mod = os.path.splitext(url)[0]
            newMod, cntrl = self.model.openModule(mod)
            view  = newMod.editor.addNewView(ModuleDocView.viewName, ModuleDocView)
            view.refreshCtrl()
            view.focus()

    def genModuleListSect(self):
        modLst = []
        modNames = self.model.modules.keys()
        modNames.sort()
        for amod in modNames:
            desc = self.model.modules[amod][1].strip()
            modLst.append('<tr><td width="25%%"><a href="%s.html">%s</a></td><td>%s</td></tr>' %(amod, amod, desc))

        return '<table BORDER=0 CELLSPACING=0 CELLPADDING=0>'+'<BR>'.join(modLst)+'</table>', modNames

    def genModuleSect(self, page):
        classList, classNames = self.genClassListSect()
        funcList, funcNames = self.genFuncListSect()
        module = self.model.getModule()
        modBody = wxwAppModuleTemplate % { \
          'ModuleSynopsis': module.getModuleDoc(),
          'Module': self.model.moduleName,
          'ModuleList': self.genModuleListSect()[0],
          'ClassList': classList,
          'FunctionList': funcList,
       }

        return self.genFunctionsSect(\
            self.genClassesSect(page + modBody, classNames), funcNames)

#        return self.genClassesSect(page + modBody, classNames)

class AppCompareView(ListCtrlView, CloseableViewMix):
    viewName = 'App. Compare'
    viewTitle = _('App. Compare')

    gotoLineBmp = 'Images/Editor/GotoLine.png'

    def __init__(self, parent, model):
        CloseableViewMix.__init__(self, _('compare results'))
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          ( ('Do diff', self.OnGoto, self.gotoLineBmp, ''), ) +\
           self.closingActionItems, 0)

        self.InsertColumn(0, _('Module'), width = 100)
        self.InsertColumn(1, _('Differs from'), width = 450)
        self.InsertColumn(2, _('Result'), width = 75)

        self.results = {}
        self.listResultIdxs = []
        self.tabName = 'App. Compare'
        self.active = True
        self.model = model
        self.compareTo = ''

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        from Models.PythonEditorModels import BaseAppModel
        otherApp = BaseAppModel('', self.compareTo, '', self.model.editor, True, {})

        from Explorers.Explorer import openEx
        otherApp.transport = openEx(self.compareTo)

        otherApp.load()
        otherApp.readModules()

        filename, otherFilename = self.model.assertLocalFile(), otherApp.assertLocalFile()

        i = 0
        # Compare apps
        if not cmp(filename, otherFilename):
            i = self.addReportItems(i,
                  (os.path.splitext(os.path.basename(filename))[0], otherFilename,
                   _('changed')))

        # Find changed modules and modules not occuring in other module
        for module in self.model.modules.keys():
            if otherApp.modules.has_key(module):
                otherFile = otherApp.assertLocalFile(otherApp.moduleFilename(module))
                filename = self.model.assertLocalFile(self.model.moduleFilename(module))
                try:
                    if not cmp(filename, otherFile):
                        i = self.addReportItems(i, (module, otherFile, _('changed')) )
                except OSError:
                    pass
            else:
                i = self.addReportItems(i, (module, '', _('deleted')) )

        # Find modules only occuring in other module
        for module in otherApp.modules.keys():
            if not self.model.modules.has_key(module):
                #otherFile = otherApp.moduleFilename(module)
                i = self.addReportItems(i, (module, '', _('added')) )

        self.pastelise()

    def OnGoto(self, event):
        if self.selected >= 0:
            module = self.GetItemText(self.selected)
            model, controller = self.model.openModule(module)
            otherModule = self.GetItem(self.selected, 1).GetText()
            if otherModule:
                controller.OnDiffModules(filename=otherModule)

class AppToDoView(ListCtrlView):
    viewName = 'Application Todo'
    viewTitle = _('Application Todo')

    gotoLineBmp = 'Images/Editor/GotoLine.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          ((_('Goto file'), self.OnGoto, self.gotoLineBmp, ''),), 0)

        self.sortOnColumns = [0, 1]

        self.InsertColumn(0, _('Name'))
        self.InsertColumn(1, _('#Todos'))
        self.InsertColumn(2, _('Filepath'))
        self.SetColumnWidth(0, 75)
        self.SetColumnWidth(1, 25)
        self.SetColumnWidth(2, 350)

        self.todos = []
        self.active = True

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        todos = []
        prog = 0
        from Models.PythonEditorModels import ModuleModel
        absModPaths = self.model.absModulesPaths()
        progStep = 100.0/len(absModPaths)
        for module in absModPaths:
            #module = 'file://'+absModPath
            self.model.editor.statusBar.progress.SetValue(int(prog*progStep))
            prog += 1
            self.model.editor.setStatus(_('Parsing %s...')%module)
            #module = self.modules[moduleName]
            #filename = self.normaliseModuleRelativeToApp(module[2])
            if module[:7] != 'file://':
                print _('%s skipped, only local files supported for Imports View')
                continue
            else:
                fn = module[7:]
            try: f = open(fn)
            except IOError:
                print _("couldn't load %s") % module
                continue
            else:
                data = f.read()
                f.close()
                name = os.path.splitext(os.path.basename(module))[0]
                model = ModuleModel(data, name, self.model.editor, 1)
                
                m = model.getModule()
                if m.todos:
                    todos.append( (name, len(m.todos), module) )
        
        self.model.editor.statusBar.progress.SetValue(0)
        self.model.editor.setStatus(_('Finished parsing'))
            
        i = 0
        for name, numTodos, path in todos:
            self.addReportItems(i, (name, numTodos, path))
            i += 1

        self.pastelise()
        
        self.todos = todos


    def OnGoto(self, event):
        if self.selected >= 0:
            name, numTodos, path = self.todos[self.selected]
            mod, ctrlr = self.model.editor.openOrGotoModule(path)
            if mod.views.has_key('Todo'):
                view = mod.views['Todo']
            else:
                view  = mod.editor.addNewView(ToDoView.viewName, ToDoView)
            view.refreshCtrl()
            view.focus()
            
##            srcView = self.model.views['Source']
##            # XXX Implement an interface for views to talk
##            srcView.focus()
##            module = self.model.getModule()
##            srcView.gotoLine(int(module.todos[self.selected][0]) -1)


class TextInfoFileView(SourceViews.EditorStyledTextCtrl):
    viewName = 'TextInfo'
    viewTitle = 'TextInfo'

    def __init__(self, parent, model):
        SourceViews.EditorStyledTextCtrl.__init__(self, parent, -1,
          model, (), 0)
        self.active = True
        wx.stc.EVT_STC_UPDATEUI(self, self.GetId(), self.OnUpdateUI)
        self.model.loadTextInfo(self.viewName)

    def OnUpdateUI(self, event):
        # don't update if not fully initialised
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

    def getModelData(self):
        return self.model.textInfos[self.viewName]

    def setModelData(self, data):
        self.model.textInfos[self.viewName] = data
        if self.viewName not in self.model.unsavedTextInfos:
            self.model.unsavedTextInfos.append(self.viewName)

class AppREADME_TIFView(TextInfoFileView):
    viewName = 'Readme.txt'
    viewTitle = 'Readme.txt'
    
class AppTODO_TIFView(TextInfoFileView):
    viewName = 'Todo.txt'
    viewTitle = 'Todo.txt'
    
class AppBUGS_TIFView(TextInfoFileView):
    viewName = 'Bugs.txt'
    viewTitle = 'Bugs.txt'

class AppCHANGES_TIFView(TextInfoFileView):
    viewName = 'Changes.txt'
    viewTitle = 'Changes.txt'
