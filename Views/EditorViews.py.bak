#----------------------------------------------------------------------
# Name:        EditorViews.py
# Purpose:     Base view classes that are the visual plugins for models
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
print 'importing Views'

import os, sys

import wx
import wx.html

import Preferences, Utils
from Preferences import IS, staticInfoPrefs, keyDefs
from Utils import _

import Search
from Models import EditorHelper

# XXX Python specific views should probably move out to PythonViews

wxwHeaderTemplate ='''<html> <head>
   <title>%(Title)s</title>
</head>
<body bgcolor="#FFFFFF">'''

wxwModuleTemplate = '''
<h1>%(Module)s</h1>
%(ModuleSynopsis)s
<p><b><font color="#FF0000">Classes</font></b><br>
<p>%(ClassList)s
<p><b><font color="#FF0000">Functions</font></b><br>
<p>%(FunctionList)s
<hr>
'''

wxwAppModuleTemplate = '''
<h1>%(Module)s</h1>
%(ModuleSynopsis)s
<p><b><font color="#FF0000">Modules</font></b><br>
<p>%(ModuleList)s
<p><b><font color="#FF0000">Classes</font></b><br>
<p>%(ClassList)s
<p><b><font color="#FF0000">Functions</font></b><br>
<p>%(FunctionList)s
<hr>
'''

wxwClassTemplate = '''
<a NAME="%(Class)s"></a>
<h2>%(Class)s</h2>
%(ClassSynopsis)s
<p><b><font color="#FF0000">Derived from</font></b>
<p>%(ClassSuper)s
<p><b><font color="#FF0000">Methods</font></b>
<p>
%(MethodList)s
<p>
%(MethodDetails)s
<hr>
<center>
*</center>
'''

wxwMethodTemplate = '''
<hr><a NAME="%(Class)s%(Method)s"></a>
<h3>
%(Class)s.%(Method)s</h3>
<b>%(Method)s</b>(<i>%(Params)s</i>)
<p>&nbsp;%(MethodSynopsis)s
<p>
'''

wxwFunctionTemplate = '''
<hr><a NAME="%(Function)s"></a>
<h3>
%(Function)s</h3>
<b>%(Function)s</b>(<i>%(Params)s</i>)
<p>&nbsp;%(FunctionSynopsis)s
<p>
'''

wxwFooterTemplate = '</body></html>'

class EditorView:
    viewName = 'viewName undefined'
    viewTitle = 'viewTitle undefined'
    
    plugins = ()
    def __init__(self, model, actions=(), dclickActionIdx=-1,
          editorIsWindow=True, overrideDClick=False):
        self.active = False
        self.model = model
        try:self.editorDisconnect = self.model.editor.Disconnect
        except: pass
        self.modified = False
        if editorIsWindow:
            self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
            self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

            dt = Utils.BoaFileDropTarget(model.editor)
            self.SetDropTarget(dt)

        self.popx = self.popy = 0

        self.canExplore = False

        actions = list(actions)
        self.plugins = [Plugin(model, self, actions) for Plugin in self.plugins]
        self.actions = tuple(actions)

        self.defaultActionIdx = dclickActionIdx
        self.buildMethodIds()
        self.buildMenuDefn()
        # Connect default action of the view to doubleclick on view
        if not overrideDClick and dclickActionIdx < len(actions) and dclickActionIdx > -1:
            self.Bind(wx.EVT_LEFT_DCLICK, actions[dclickActionIdx][1])

    def destroy(self):
        self.disconnectEvts()

        self.model = None
        self.methodsIds = None
        del self.actions

#---Action management-----------------------------------------------------------
    def buildMethodIds(self):
        self.methodsIds = []
        for name, meth, bmp, accl in self.actions:
            if name != '-':
                self.methodsIds.append( (wx.NewId(), meth) )

    def buildMenuDefn(self):
        self.accelLst = []
        self.menuDefn = []

        mIds = self.methodsIds[:]
        mIds.reverse()

        # Build Edit/popup menu and accelerator list
        for name, meth, bmp, accl in self.actions:
            if name == '-':
                wId = -1
            else:
                wId, _m = mIds.pop()

            if name[0] == '+':
                canCheck = True
                name = name[1:]
            else:
                canCheck = False

            if accl:
                code = keyDefs[accl]
            else:
                code = ()

            #name = name + (keyDefs[accl][2] and ' \t'+keyDefs[accl][2] or '')

            self.menuDefn.append( (wId, name, code, bmp, canCheck) )

            if accl:
                self.accelLst.append( (code[0], code[1], wId) )

    def generateMenu(self):
        menu = wx.Menu()
        for wId, name, code, bmp, canCheck in self.menuDefn:
            if name != '-':
                Utils.appendMenuItem(menu, wId, name, code, bmp)
            else:
                menu.AppendSeparator()
        return menu

    def addViewMenus(self):
        self.buildMenuDefn()
        return self.generateMenu(), self.accelLst

    def connectEvts(self):
        for wId, meth in self.methodsIds:
            self.Bind(wx.EVT_MENU, meth, id=wId)
            self.model.editor.Bind(wx.EVT_MENU, meth, id=wId)

    def disconnectEvts(self):
        if self.model:
            for wId, meth in self.methodsIds:
                self.Disconnect(wId)
                self.editorDisconnect(wId)

    def addViewTools(self, toolbar):
        addedSep = False
        for name, meth, bmp, accls in self.actions:
            if name == '-' and not bmp:
                toolbar.AddSeparator()
                addedSep = True
            elif bmp != '-':
                if name[0] == '+':
                    # XXX Add toggle button
                    name = name [1:]
                if not addedSep:
                    # this is the separator between File and Edit
                    toolbar.AddSeparator()
                    addedSep = True
                Utils.AddToolButtonBmpObject(self.model.editor, toolbar,
                      IS.load(bmp), name, meth)

#---Page management-------------------------------------------------------------
    docked = True
    def addToNotebook(self, notebook, viewTitle='', panel=None):
        self.notebook = notebook
        if not viewTitle:
            viewTitle = Utils.getViewTitle(self)

        self.pageIdx = notebook.GetPageCount()
        if panel:
            notebook.AddPage(panel, viewTitle)
        else:
            notebook.AddPage(self, viewTitle)

        self.modified =  False
        self.readOnly = False

    def deleteFromNotebook(self, focusView, tabName):
        # set selection to source view
        # check that not already destroyed
        if hasattr(self, 'model'):
            if self.modified:
                #if wx.MessageBox('View modified, apply changes?',
                #  'Close View',
                #  wx.OK | wxCANCEL | wx.ICON_EXCLAMATION) == wx.YES:
                self.refreshModel()

            self.model.reorderFollowingViewIdxs(self.pageIdx)
            # XXX If the last view closes should the model close ??
            if self.model.views.has_key(focusView):
                self.model.views[focusView].focus()
            del self.model.views[tabName]
            self.destroy()
            self.notebook.DeletePage(self.pageIdx)

#---Editor status updating------------------------------------------------------
    def updatePageName(self):
        if hasattr(self, 'notebook'):
            currName = self.notebook.GetPageText(self.pageIdx)

            viewTitle = Utils.getViewTitle(self)

            if self.isModified(): newName = '~%s~' % viewTitle
            else: newName = viewTitle

            if currName != newName:
                if newName == viewTitle:
                    if self.model.viewsModified.count(self.viewName):
                        self.model.viewsModified.remove(self.viewName)
                else:
                    if not self.model.viewsModified.count(self.viewName):
                        self.model.viewsModified.append(self.viewName)
                self.notebook.SetPageText(self.pageIdx, newName)
                self.updateEditor()

    def updateEditor(self):
        self.model.editor.updateModuleState(self.model)

    def updateViewState(self):
        self.updatePageName()

#---Standard interface----------------------------------------------------------
    def activate(self):
        self.active = True
        if self.modified: self.refresh()

    def deactivate(self):
        self.active = False

    def update(self):
        self.modified = True
        if self.active:
            self.refresh()

    def refresh(self):
        self.refreshCtrl()
        self.modified = False

    def refreshModel(self):
        """ Override this to apply changes in your view to the model """
        self.model.update()
        self.model.notify()

    def focus(self, refresh=True):
        if hasattr(self, 'notebook'):
            self.notebook.SetSelection(self.pageIdx)
        if refresh:
##            self.notebook.Refresh()
            self.SetFocus()

    def saveNotification(self):
        pass

    def close(self):
        self.destroy()

    def isModified(self):
        return self.modified

    def explore(self):
        """ Return items for Explorer """
        return []

    def gotoBrowseMarker(self, marker):
        """ Called by the browse history stack, children should override to
        participate in the HistoryBrowser """
        self.focus()

    def OnRightDown(self, event):
        self.popx = event.GetX()
        self.popy = event.GetY()

    def OnRightClick(self, event):
        menu = self.generateMenu()
        event.GetEventObject().PopupMenuXY(menu, event.GetX(), event.GetY())
        menu.Destroy()

class TestView(wx.TextCtrl, EditorView):
    viewName = 'Test'
    viewTitle = _('Test')
    def __init__(self, parent, model):
        wx.TextCtrl.__init__(self, parent, -1, '',
              style=wx.TE_MULTILINE | wx.TE_RICH | wx.HSCROLL)
        EditorView.__init__(self, model, (), 5)
        self.active = True

    def refreshCtrl(self):
        self.SetValue('')

class HTMLView(wx.html.HtmlWindow, EditorView):
    prevBmp = 'Images/Shared/Previous.png'
    nextBmp = 'Images/Shared/Next.png'

    viewName = 'HTML'
    viewTitle = _('HTML')
    def __init__(self, parent, model, actions = ()):
        wx.html.HtmlWindow.__init__(self, parent, style=wx.SUNKEN_BORDER)
        EditorView.__init__(self, model, ((_('Back'), self.OnPrev, self.prevBmp, ''),
                      (_('Forward'), self.OnNext, self.nextBmp, '') )+ actions, -1)
        #self.SetRelatedFrame(model.editor, _('Editor %s)')
        #self.SetRelatedStatusBar(1)

        model.editor.statusBar.setHint('')

        self.title = 'HTML'
        self.data = ''
        self.active = True

    def generatePage(self):
        return ''

    def refreshCtrl(self):
        self.data = self.generatePage()
        self.SetPage(self.data)

    def OnPrev(self, event):
        self.HistoryBack()

    def OnNext(self, event):
        self.HistoryForward()

class HTMLFileView(HTMLView):
    viewName = 'View'
    viewTitle = _('View')
    def generatePage(self):
        return self.model.data

# XXX Add structured text/wiki option for doc strings
# XXX Option to only list documented methods
class HTMLDocView(HTMLView):
    viewName = 'Documentation'
    viewTitle = _('Documentation')

    printBmp = 'Images/Shared/Print.png'
    def __init__(self, parent, model, actions = ()):
        HTMLView.__init__(self, parent, model, (
              ('-', None, '', ''),
              (_('Save HTML'), self.OnSaveHTML, '-', ''),
              (_('Print'), self.OnPrintHTML, self.printBmp, ''), )+ actions)
        self.title = 'Boa docs'

        self.printer = wx.html.HtmlEasyPrinting()

    def generatePage(self):
        page = wxwHeaderTemplate % {'Title': self.title}
        page = self.genCustomPage(page) + wxwFooterTemplate
        return page

    def genCustomPage(self, page):
        """ Override to make the page a little more interesting """
        return page

    def OnSaveHTML(self, event):
        from FileDlg import wxFileDialog
        dlg = wx.FileDialog(self, _('Save as...'), '.', '', '*.html',
          wx.SAVE | wx.OVERWRITE_PROMPT)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                from Explorers.Explorer import openEx
                trpt = openEx(dlg.GetPath())
                trpt.save(trpt.currentFilename(), self.data)
        finally:
            dlg.Destroy()

    def OnPrintHTML(self, event):
        self.printer.PrintText(self.generatePage())

class ModuleDocView(HTMLDocView):

    def genCustomPage(self, page):
        return self.genModuleSect(page)

    def genModuleSect(self, page):
        classList, classNames = self.genClassListSect()
        funcList, funcNames = self.genFuncListSect()
        module = self.model.getModule()
        modBody = wxwModuleTemplate % { \
          'ModuleSynopsis': module.getModuleDoc(),
          'Module': self.model.moduleName,
          'ClassList': classList,
          'FunctionList': funcList,
        }

        return self.genFunctionsSect(\
            self.genClassesSect(page + modBody, classNames), funcNames)

    def genListSect(self, names):
        lst = []
        for name in names:
            lst.append('<a href="#%s">%s</a>' %(name, name))
        return '<BR>'.join(lst)

    def genClassListSect(self):
        classNames = self.model.getModule().class_order
        return self.genListSect(classNames), classNames

    def genFuncListSect(self):
        funcNames = self.model.getModule().function_order
        return self.genListSect(funcNames), funcNames

    def genClassesSect(self, page, classNames):
        clsBody = ''
        classes = []
        module = self.model.getModule()
        for aclass in classNames:
            supers = []
            for super in module.classes[aclass].super:
                try:
                    supers.append('<a href="#%s">%s</a>'%(super.name, super.name))
                except:
                    supers.append(super)
            if len(supers) > 0:
                supers = ', '.join(supers)
            else:
                supers = ''

            methlist, meths = self.genMethodSect(aclass)

            clsBody = wxwClassTemplate % { \
              'Class': aclass,
              'ClassSuper': supers,
              'ClassSynopsis': module.getClassDoc(aclass),
              'MethodList': methlist,
              'MethodDetails': meths,
            }
            classes.append(clsBody)

        return page + ' '.join(classes)

    def genMethodSect(self, aclass):
        methlist = []
        meths = []
        module = self.model.getModule()
        methods = module.classes[aclass].methods.keys()
        methods.sort()
        for ameth in methods:
            methlist.append('<a href="#%(Class)s%(Method)s">%(Method)s</a><br>' % {\
              'Class': aclass,
              'Method': ameth})
            methBody = wxwMethodTemplate % { \
              'Class': aclass,
              'Method': ameth,
              'MethodSynopsis': module.getClassMethDoc(aclass, ameth),
              'Params': module.classes[aclass].methods[ameth].signature,
            }
            meths.append(methBody)

        return ' '.join(methlist), ' '.join(meths)

    def genFunctionsSect(self, page, funcNames):
        funcBody = ''
        functions = []
        module = self.model.getModule()
        for func in funcNames:
            funcBody = wxwFunctionTemplate % { \
              'Function': func,
              'Params': module.functions[func].signature,
              'FunctionSynopsis': module.getFunctionDoc(func),
            }
            functions.append(funcBody)

        return page + ' '.join(functions)

# XXX For editing views there should be a prompt before closing.
class CloseableViewMix:
    """ Defines a closing action for views like results.
        Deletes page named tabName
    """
    closeViewBmp = 'Images/Editor/CloseView.png'

    def __init__(self, hint = _('results')):
        self.closingActionItems = ( (_('Close %s')%hint, self.OnClose,
                                     self.closeViewBmp, 'CloseView'), )

    def OnClose(self, event):
        del self.closingActionItems
        self.deleteFromNotebook('Source', self.tabName)

class CyclopsView(HTMLView, CloseableViewMix):
    viewName = 'Cyclops report'
    viewTitle = _('Cyclops report')
    def __init__(self, parent, model):
        CloseableViewMix.__init__(self)
        HTMLView.__init__(self, parent, model, ( ('-', -1, '', ''), ) +
          self.closingActionItems)

    def OnLinkClicked(self, linkinfo):
        """ classlink, attriblink """
        url = linkinfo.GetHref()

        if url[0] == '#':
            self.base_OnLinkClicked(linkinfo)
        else:
            jumpType, jumpPath = url.split('://')
            segs = jumpPath.split('.')
            if jumpType == 'classlink':
                mod, clss = segs[-2:]
                if len(segs) > 2:
                    pack = segs[:-2]
                else:
                    pack = []
            elif jumpType == 'attrlink':
                mod, clss, attr = segs[-3:]
                if len(segs) > 3:
                    pack = segs[:-3]
                else:
                    pack = []

            for dirname in sys.path:
                fullname = os.path.abspath(os.path.join(dirname, mod+'.py'))
                if os.path.exists(fullname):
                    found = fullname
                    break
                else:
                    pckPth = '/'.join(pack)
                    fullname = os.path.abspath(os.path.join(dirname, pckPth, mod+'.py'))
                    if os.path.exists(fullname):
                        found = fullname
                        break

            else: return

            model, controller = self.model.editor.openOrGotoModule(fullname)
            module = model.getModule()
            if jumpType == 'classlink':
                lineno = module.classes[clss].block.start
            elif jumpType == 'attrlink':
                if module.classes[clss].attributes.has_key(attr):
                    lineno = module.classes[clss].attributes[attr][0].start
                elif module.classes[clss].methods.has_key(attr):
                    lineno = module.classes[clss].methods[attr].start
                else:
                    lineno = module.classes[clss].block.start

                mod, clss, attr = segs[-3:]
                if len(segs) > 3:
                    pack = segs[:-3]
                else:
                    pack = []

            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].gotoLine(lineno - 1)

    def generatePage(self):
        return self.report

    def OnSaveReport(self, event):
        fn, ok = self.model.editor.saveAsDlg(\
          os.path.splitext(self.model.filename)[0]+'.cycles', '*.cycles')
        if ok:
            from Explorers.Explorer import openEx
            transport = openEx(fn)
            transport.save(transport.currentFilename(), self.report, 'w')


# XXX Add addReportColumns( list of name, width tuples) !
class ListCtrlView(wx.ListView, EditorView, Utils.ListCtrlSelectionManagerMix):
    viewName = 'List (abstract)'
    viewTitle = 'List (abstract)'
    def __init__(self, parent, model, listStyle, actions, dclickActionIdx=-1):
        wx.ListView.__init__(self, parent, -1,
              style=listStyle | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        EditorView.__init__(self, model, actions, dclickActionIdx,
              overrideDClick=True)
        Utils.ListCtrlSelectionManagerMix.__init__(self)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselect)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivate)
        # To catch enter to emulate activated event (bug with notebook and key events on windows)
        if wx.Platform == '__WXMSW__':
            self.Bind(wx.EVT_KEY_UP, self.OnKeyPressed)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)

        self.selected = -1

        self.sortOnColumns = []
        self.sortCol = -1
        self.sortData = {}
        self.active = True
        self.flipDir = False
        self._columnCount = 0

    def pastelPicker(self, idx):
        return idx % 2

    def pastelise(self):
        if Preferences.pastels:
            for idx in range(self.GetItemCount()):
                item = self.GetItem(idx)
                if self.pastelPicker(idx):
                    item.SetBackgroundColour(Preferences.pastelMedium)
                else:
                    item.SetBackgroundColour(Preferences.pastelLight)
                self.SetItem(item)

    def refreshCtrl(self):
        self.DeleteAllItems()
        self.sortData = {}

    def addReportItems(self, index, list, imgIdx = None):
        if list:
            if imgIdx is not None:
                self.InsertImageStringItem(index, list[0], imgIdx)
            else:
                self.InsertStringItem(index, list[0])
            self.SetItemData(index, index)
            self.sortData[index] = list
            col = 1
            if len(list) > 1:
                for text in list[1:]:
                    self.SetStringItem(index, col, str(text))
                    col = col + 1
        return index + 1

    def addReportColumns(self, columns):
        self.DeleteAllColumns()

        self._columnCount = 0

        for name, width in columns:
            self.InsertColumn(self._columnCount, name)
            self.SetColumnWidth(self._columnCount, width)
            self._columnCount = self._columnCount + 1

    def getSelectedIndex(self):
        if self.selected == -1:
            return -1
        else:
            return self.GetItemData(self.selected)

    def sortColumn(self, itemIdx1, itemIdx2):
        item1 = self.sortData[itemIdx1][self.sortCol]
        item2 = self.sortData[itemIdx2][self.sortCol]

        # try to sort integer columns by int value
        try: 
            i1 = int(item1)
            i2 = int(item2)
        except (TypeError, ValueError):
            pass
        else:
            item1, item2 = i1, i2

        if self.flipDir:
            item1, item2 = item2, item1
        if item1 < item2: return -1
        if item1 > item2: return 1
        return 0

    def OnKeyPressed(self, event):
        key = event.GetKeyCode()
        if key == 13:
            if self.defaultActionIdx != -1:
                self.actions[self.defaultActionIdx][1](event)
                return
        event.Skip()

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1

    def OnColClick(self, event):
        if event.m_col in self.sortOnColumns:
            if self.sortCol == event.m_col:
                self.flipDir = not self.flipDir
            else:
                self.sortCol = event.m_col
                self.flipDir = False
            self.SortItems(self.sortColumn)
            self.pastelise()

    def OnItemActivate(self, event):
        if self.defaultActionIdx < len(self.actions) and self.defaultActionIdx > -1:
            self.actions[self.defaultActionIdx][1](event)
#            EVT_LEFT_DCLICK(self, self.actions[self.dclickActionIdx][1])

class VirtualListCtrlView(wx.ListCtrl, EditorView):
    """ Simple virtual list ctrl

    Derived classes must implement
    def OnGetItemText(self, item, col):

    and call self.SetItemCount(<size>)

    """
    def __init__(self, parent, model, listStyle, actions, dclickActionIdx=-1,
          overrideDClick=True):
        wx.ListCtrl.__init__(self, parent, -1,
           style=listStyle | wx.LC_VIRTUAL | wx.SUNKEN_BORDER)
        EditorView.__init__(self, model, actions, dclickActionIdx,
           overrideDClick=overrideDClick)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselect)

        self.attrPM = wx.ListItemAttr()
        self.attrPM.SetBackgroundColour(Preferences.pastelMedium)

        self.attrPL = wx.ListItemAttr()
        self.attrPL.SetBackgroundColour(Preferences.pastelLight)

    selected = -1
    def OnItemSelect(self, event):
        self.selected = event.GetIndex()

    def OnItemDeselect(self, event):
        self.selected = -1

    def GetSelections(self):
        sel = []
        selCnt = self.GetSelectedItemCount()
        if selCnt:
            idx = -1
            while len(sel) < selCnt:
                idx = self.GetNextItem(idx, state=wx.LIST_STATE_SELECTED)
                if idx != -1:
                    sel.append(idx)
                else:
                    break
        return sel

    def OnGetItemImage(self, item):
        return -1

    def OnGetItemAttr(self, item):
        if Preferences.pastels:
            return item % 2 and self.attrPM or self.attrPL
        else:
            return None


idGotoLine = wx.NewId()
class ToDoView(ListCtrlView):
    viewName = 'Todo'
    viewTitle = _('Todo')
    gotoLineBmp = 'Images/Editor/GotoLine.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          ((_('Goto line'), self.OnGoto, self.gotoLineBmp, ''),), 0)

        self.sortOnColumns = [0, 1]

        self.InsertColumn(0, _('Line#'))
        self.InsertColumn(1, _('Urgency'))
        self.InsertColumn(2, _('Entry'))
        self.SetColumnWidth(0, 40)
        self.SetColumnWidth(1, 75)
        self.SetColumnWidth(2, 350)

        self.active = True
        self.distinctTodos = []
        self.blockReentrant = False

    def pastelPicker(self, idx):
        return ListCtrlView.pastelPicker(self, self.distinctTodos[idx])

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        i = 0
        lastLine = -1
        todoCnt = 0
        self.distinctTodos = []
        module = self.model.getModule()
        for todo in module.todos:
            todoStr = todo[1].rstrip()
            idx = -1
            while todoStr and todoStr[idx] == '!':
                idx = idx -1
            urgency = `idx * -1 -1`

            if todo[0] - 1 != lastLine:
                todoCnt = todoCnt + 1
            lineNo = `todo[0]`
            lastLine = todo[0]

            self.distinctTodos.append(todoCnt)
            self.addReportItems(i, (lineNo, urgency, todoStr))
            i = i + 1

        self.pastelise()

##    def OnItemSelect(self, event):
##        ListCtrlView.OnItemSelect(self, event)
##        if not self.blockReentrant:
##            self.blockReentrant = True
##            try:
##                selectedIdx = self.distinctTodos[self.selected]
##                for idx in range(self.GetItemCount()):
##                    item = self.GetItem(idx)
##                    focusState = item.GetState() & wx.LIST_STATE_FOCUSED
##                    if self.distinctTodos[idx] == selectedIdx:
##                        selectState = wx.LIST_STATE_SELECTED
##                    else:
##                        selectState = 0
##                    item.SetState(selectState | focusState)
##                    self.SetItem(item)
##            finally:
##                self.blockReentrant = False
##
##    def OnItemDeselect(self, event):
##        return
###        ListCtrlView.OnItemDeselect(self, event)
##        if not self.blockReentrant:
##            self.blockReentrant = True
##            try:
##                selectedIdx = self.distinctTodos[self.selected]
##                for idx in range(self.GetItemCount()):
##                    item = self.GetItem(idx)
##                    focusState = item.GetState() & wx.LIST_STATE_FOCUSED
##                    if self.distinctTodos[idx] == selectedIdx:
##                        selectState = wx.LIST_STATE_SELECTED
##                    else:
##                        selectState = 0
##                    item.SetState(selectState | focusState)
##                    self.SetItem(item)
##            finally:
##                self.blockReentrant = False

    def OnGoto(self, event):
        if self.model.views.has_key('Source') and self.selected >= 0:
            srcView = self.model.views['Source']
            # XXX Implement an interface for views to talk
            srcView.focus()
            module = self.model.getModule()
            srcView.gotoLine(int(module.todos[self.selected][0]) -1)

class FindResultsAdderMixin:
    def addFindResults(self, pattern, mapResults):
        """ mapResult is map of tuples where
            Key - 'Module', file name
            Value - ('Line no', 'Col', 'Text')
        """
        from FindResults import FindResults
        name = _('Results: %s')%pattern
        if not self.model.views.has_key(name):
            resultView = self.model.editor.addNewView(name, FindResults)
        else:
            resultView = self.model.views[name]
        resultView.tabName = name
        resultView.results = mapResults
        resultView.findPattern = pattern
        resultView.refresh()
        resultView.focus()


class PackageView(ListCtrlView, FindResultsAdderMixin):
    viewName = 'Package'
    viewTitle = _('Package')
    findBmp = 'Images/Shared/Find.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_LIST,
          ((_('Open'), self.OnOpen, '-', ()),
           (_('Find'), self.OnFind, self.findBmp, 'Find'),), 0)
        self.SetImageList(model.editor.modelImageList, wx.IMAGE_LIST_SMALL)

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        self.filenames = {}
        self.packageFiles = self.model.generateFileList()
        for itm in self.packageFiles:
            name = os.path.splitext(itm.treename or itm.name)[0]
            self.InsertImageStringItem(self.GetItemCount(), name, itm.imgIdx)
            self.filenames[name] = itm

    def OnOpen(self, event):
        if self.selected >= 0:
            name = self.GetItemText(self.selected)
            item = self.filenames[name]
            from Models import PythonEditorModels
            if item.imgIdx == PythonEditorModels.PackageModel.imgIdx:
                self.model.openPackage(name)
            else:
                self.model.openFile(name)

    def OnFind(self, event):
        import FindReplaceDlg
        FindReplaceDlg.find(self, self.model.editor.finder, self)

class InfoView(wx.TextCtrl, EditorView):
    viewName = 'Info'
    viewTitle = _('Info')

    def __init__(self, parent, model):
        wx.TextCtrl.__init__(self, parent, -1, '', style=wx.TE_MULTILINE | wx.TE_RICH | wx.HSCROLL)
        EditorView.__init__(self, (_('Add comment block to code'), self.OnAddInfo, ''), 5)
        self.active = True
        self.model = model
        self.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.NORMAL, False))

    def refreshCtrl(self):
        self.SetValue('')
        module = self.model.getModule()
        info = module.getInfoBlock()
        self.WriteText(`info`)

    def OnAddInfo(self, event):
        self.model.addInfoBlock()

# XXX Add filter option to show only occurences of a method and it's overrides
# XXX Could also expand all containers with bold items
class ExploreView(wx.TreeCtrl, EditorView):
    viewName = 'Explore'
    viewTitle = _('Explore')
    gotoLineBmp = 'Images/Editor/GotoLine.png'

    def __init__(self, parent, model):
        wx.TreeCtrl.__init__(self, parent, -1, style=wx.TR_HAS_BUTTONS | wx.SUNKEN_BORDER)
        EditorView.__init__(self, model, ((_('Goto line'), self.OnGoto, self.gotoLineBmp, ''),), 0)

        self.tokenImgLst = wx.ImageList(16, 16)
        for exploreImg in ('Images/Views/Explore/class.png',
                           'Images/Views/Explore/method.png',
                           'Images/Views/Explore/event.png',
                           'Images/Views/Explore/function.png',
                           'Images/Views/Explore/attribute.png',
                           'Images/Modules/'+self.model.bitmap,
                           'Images/Views/Explore/global.png',
                           'Images/Views/Explore/dottedline.png',
                           'Images/Views/Explore/import.png',
                           ):
            self.tokenImgLst.Add(IS.load(exploreImg))
        self.SetImageList(self.tokenImgLst)

        self.active = True
        self.canExplore = True

        self._populated_tree = 0

        self.Bind(wx.EVT_KEY_UP, self.OnKeyPressed)

    def destroy(self):
        EditorView.destroy(self)
        self.tokenImgLst = None

    def OnPageActivated(self, event):
        if not self._populated_tree:
            self._populated_tree = 1
            self.refreshCtrl(1)

    def refreshCtrl(self, load_now=0):
        self.DeleteAllItems()
        if not load_now and not self.IsShown():
            self._populated_tree = 0
            return
        self.AddRoot(_('Loading...'))

        from moduleparse import CodeBlock

        module = self.model.getModule()

        breaks = module.break_lines
        breakLnNos = breaks.keys()
        breakLnNos.sort()

        self.DeleteAllItems()
        rootItem = self.AddRoot(self.model.moduleName, 5, -1,
              wx.TreeItemData(CodeBlock('', 0, 0)))
        if module.imports or module.from_imports_names:
            importsItem = self.AppendItem(rootItem, 'Imports', 8, data=wx.TreeItemData(CodeBlock('', 0, 0)))
            for i in module.imports:
                self.AppendItem(importsItem, i, 6, data=wx.TreeItemData(CodeBlock('', module.imports[i][0], 0)))
            for i in module.from_imports_names:
                self.AppendItem(importsItem, i, 6, data=wx.TreeItemData(CodeBlock('', module.from_imports[module.from_imports_names[i]][0], 0)))
                
        for className in module.class_order:
            classItem = self.AppendItem(rootItem, className, 0, -1,
                  wx.TreeItemData(module.classes[className].block))
            for attrib in module.classes[className].attributes.keys():
                attribItem = self.AppendItem(classItem, attrib, 4, -1,
                  wx.TreeItemData(module.classes[className].attributes[attrib]))
            brkStrt = module.classes[className].block.start
            for method in module.classes[className].method_order:
                methBlock = module.classes[className].methods[method]
                for brkLnNo in breaks.keys():
                    if brkLnNo > brkStrt and brkLnNo < methBlock.start:
                        brkItm = self.AppendItem(classItem, breaks[brkLnNo] , 7,
                            -1, wx.TreeItemData(CodeBlock('', brkLnNo, brkLnNo)))
                        self.SetItemBold(brkItm)
                        self.SetItemTextColour(brkItm, Preferences.propValueColour)
                        del breaks[brkLnNo]

                if Utils.methodLooksLikeEvent(method):
                    methodsItem = self.AppendItem(classItem, method, 2, -1, wx.TreeItemData(methBlock))
                    if methBlock.locals:
                        for l in methBlock.locals:
                            methodLocalsItem = self.AppendItem(methodsItem, l, 6, -1,
                                  wx.TreeItemData(CodeBlock('', methBlock.locals[l].lineno, 0)))
                else:
                    methodsItem = self.AppendItem(classItem, method, 1, -1, wx.TreeItemData(methBlock))
                    if methBlock.locals:
                        for l in methBlock.locals:
                            methodLocalsItem = self.AppendItem(methodsItem, l, 6, -1,
                                  wx.TreeItemData(CodeBlock('', methBlock.locals[l].lineno, 0)))

        functionList = module.functions.keys()
        functionList.sort()
        for func in functionList:
            funcBlock = module.functions[func]
            funcItem = self.AppendItem(rootItem, func, 3, -1,
              wx.TreeItemData(funcBlock))
            if funcBlock.locals:
                for l in funcBlock.locals:
                    funcLocalsItem = self.AppendItem(funcItem, l, 6, -1,
                          wx.TreeItemData(CodeBlock('', funcBlock.locals[l].lineno, 0)))

        for globalName in module.global_order:
            globalItem = self.AppendItem(rootItem, globalName, 6, -1,
              wx.TreeItemData(module.globals[globalName]))

        self.Expand(rootItem)

    def OnGoto(self, event):
        if self.model.views.has_key('Source'):
            srcView = self.model.views['Source']
            idx = self.GetSelection()
            if idx.IsOk():
                srcView.focus()
                self.model.editor.addBrowseMarker(srcView.GetCurrentLine())
                dat = self.GetPyData(idx)
                if type(dat) == type([]):
                    srcView.gotoLine(dat[0].start -1)
                else:
                    srcView.gotoLine(dat.start -1)

    def OnKeyPressed(self, event):
        key = event.GetKeyCode()
        if key == 13:
            if self.defaultActionIdx != -1:
                self.actions[self.defaultActionIdx][1](event)
        event.Skip()

class ExplorePythonExtensionView(ExploreView):
    viewName = 'Explore'
    viewTitle = _('Explore')
    def refreshCtrl(self, load_now=0):
        self.DeleteAllItems()

        rootItem = self.AddRoot(self.model.module.__name__, 5, -1)
        self.populateItemFromModuleData(rootItem, self.model.moduleData)
        self.Expand(rootItem)

    def populateItemFromModuleData(self, item, moduleData):
        classes = moduleData.classes.items()
        classes.sort()
        for className, classData in classes:
            classItem = self.AppendItem(item, className, 0, -1)
            for meth in classData.methods:
                methItem = self.AppendItem(classItem, meth, 2, -1)
            attrs = classData.attrs.items()
            attrs.sort()
            for name, attr in attrs:
                attrItem = self.AppendItem(classItem, '%s: %s'%(name, attr), 6, -1)

        functions = moduleData.functions.items()
        functions.sort()
        for funcName, func in functions:
            funcItem = self.AppendItem(item, funcName, 3, -1)

        attrs = moduleData.attrs.items()
        attrs.sort()
        for name, attr in attrs:
            attrItem = self.AppendItem(item, '%s: %s'%(name, attr), 6, -1)

        modules = moduleData.modules.items()
        modules.sort()
        for name, module in modules:
            modItem = self.AppendItem(item, name, 5, -1)
            self.populateItemFromModuleData(modItem, module)

class ExploreEventsView(ExploreView):
    viewName = 'Events'
    viewTitle = _('Events')
    def __init__(self, parent, model):
        ExploreView.__init__(self, parent, model)
        self.objectColls = {}

    stdCollMeths = {'_init_ctrls': 'Controls',
                    '_init_utils': 'Utilities'}
    def refreshCtrl(self, load_now=0):
        model = self.model
        self.DeleteAllItems()
        if not load_now and not self.IsShown():
            self._populated_tree = 0
            return
        self.AddRoot(_('Loading...'))

        from moduleparse import CodeBlock

        module = model.getModule()
        self.DeleteAllItems()
        rootItem = self.AddRoot(model.main, 5, -1,
              wx.TreeItemData(CodeBlock('', 0, 0)))
        self.Expand(rootItem)

        evtMeths = []
        for method in module.classes[model.main].method_order:
            if Utils.methodLooksLikeEvent(method):
                evtMeths.append(method)

        self.objectColls = {}
        main = module.classes[self.model.main]
        collMeths = model.identifyCollectionMethods()

##        stdMeths = []
##        for sm in self.stdCollMeths.keys():
##            if sm in collMeths:
##                stdMeths.append(sm)
##                collMeths.remove(sm)

        objs = {}
        for oc in collMeths:
            codeSpan = main.methods[oc]
            codeBody = module.source[codeSpan.start : codeSpan.end]
            #self.objectColls[oc]
            objColl = model.readDesignerMethod(oc, codeBody)
            objColl.indexOnCtrlName()
            if self.stdCollMeths.has_key(oc):
                name = self.stdCollMeths[oc]
            else:
                collName = oc[11:]
                pv = collName.rfind('_')
                obj, prop = collName[:pv], collName[pv+1:]
                name = self.stdCollMeths.get(oc, 'Collection: %s.%s'%(obj, prop))
            collMethItem = self.AppendItem(rootItem, name, 1, -1,
                  wx.TreeItemData(main.methods[oc]))
            #self.Expand(collMethItem)

            idEvtMeths = {}
            ctrlEvtMeths = {}

            for evt in objColl.events:
                if evt.windowid:
                    if not idEvtMeths.has_key(evt.windowid):
                        idEvtMeths[evt.windowid] = []
                    idEvtMeths[evt.windowid].append(evt.trigger_meth)
                else:
                    if not ctrlEvtMeths.has_key(evt.comp_name):
                        ctrlEvtMeths[evt.comp_name] = []
                    ctrlEvtMeths[evt.comp_name].append(evt.trigger_meth)

            for crt in objColl.creators:
                cb = main.methods[oc]
                evts = []
                if oc in self.stdCollMeths.keys():
                    name = crt.comp_name
                    if ctrlEvtMeths.has_key(name):
                        evts.extend(ctrlEvtMeths[name])
##                        if not name:
##                            cb = main.block
                        if name:
                            cb = main.attributes[name]
                    if crt.params.has_key('id') and idEvtMeths.has_key(crt.params['id']):
                        evts.extend(idEvtMeths[crt.params['id']])

                    if evts:
                        attrItem = self.AppendItem(collMethItem, name, 4, -1,
                              wx.TreeItemData(cb))
                        #self.Expand(attrItem)
                        for evtMeth in evts:
                            evtItem = self.AppendItem(attrItem, evtMeth, 2, -1,
                                  wx.TreeItemData(main.methods[evtMeth]))

                elif crt.params.has_key('id'):
                    name = crt.params['id']
                    if idEvtMeths.has_key(name):
                        evts = idEvtMeths[name]
                        for evtMeth in evts:
                            evtItem = self.AppendItem(collMethItem, evtMeth, 2, -1,
                                  wx.TreeItemData(main.methods[evtMeth]))

        Utils.traverseTreeCtrl(self, rootItem, self.expandNode)

    def expandNode(self, tree, item):
        tree.Expand(item)


class HierarchyView(wx.TreeCtrl, EditorView):
    viewName = 'Hierarchy'
    viewTitle = _('Hierarchy')
    gotoLineBmp = 'Images/Editor/GotoLine.png'

    def __init__(self, parent, model):
        id = wx.NewId()
        wx.TreeCtrl.__init__(self, parent, id, style=wx.TR_HAS_BUTTONS | wx.SUNKEN_BORDER)
        EditorView.__init__(self, model,
          ((_('Goto line'), self.OnGoto, self.gotoLineBmp, ''),), 0)

        self.tokenImgLst = wx.ImageList(16, 16)
        for hierImg in ('Images/Views/Hierarchy/inherit.png',
                        'Images/Views/Hierarchy/inherit_base.png',
                        'Images/Views/Hierarchy/inherit_outside.png',
                        'Images/Modules/'+self.model.bitmap):
            self.tokenImgLst.Add(IS.load(hierImg))

        self.SetImageList(self.tokenImgLst)

        self.Bind(wx.EVT_KEY_UP, self.OnKeyPressed)

        self.canExplore = True
        self.active = True

    def destroy(self):
        EditorView.destroy(self)
        self.tokenImgLst = None

    def buildTree(self, parent, dict):
        for item in dict.keys():
            child = self.AppendItem(parent, item, 0)
            if len(dict[item].keys()):
                self.buildTree(child, dict[item])
            self.Expand(child)

    def refreshCtrl(self):
        self.DeleteAllItems()
        self.AddRoot(_('Loading...'))
        module = self.model.getModule()
        self.DeleteAllItems()
        hierc = module.createHierarchy()

        root = self.AddRoot(self.model.moduleName, 3)
        for top in hierc.keys():
            if module.classes.has_key(top): imgIdx = 1
            else: imgIdx = 2

            item = self.AppendItem(root, top, imgIdx)
            self.buildTree(item, hierc[top])
            self.Expand(item)

        self.Expand(root)


    def OnGoto(self, event):
        idx  = self.GetSelection()
        if idx.IsOk():
            name = self.GetItemText(idx)
            if self.model.views.has_key('Source') and \
              self.model.getModule().classes.has_key(name):
                srcView = self.model.views['Source']
                srcView.focus()
                module = self.model.getModule()
                srcView.gotoLine(int(module.classes[name].block.start) -1)

    def OnKeyPressed(self, event):
        key = event.GetKeyCode()
        if key == 13:
            if self.defaultActionIdx != -1:
                self.actions[self.defaultActionIdx][1](event)

class DistUtilView(wx.Panel, EditorView):
    viewName = 'DistUtils'
    viewTitle = _('DistUtils')

    def __init__(self, parent, model):
        wx.Panel.__init__(self, parent, -1)
        EditorView.__init__(self, ())#('Add comment block to code', self.OnAddInfo, ()), 5)
        self.active = True
        self.model = model


    def refreshCtrl(self):
        pass

class DistUtilManifestView(ListCtrlView):
    viewName = 'Manifest'
    viewTitle = _('Manifest')

    refreshBmp = 'Images/Editor/Refresh.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          ((_('Open'), self.OnOpen, '-', ()),
           (_('Refresh'), self.OnRefresh, self.refreshBmp, 'Refresh')), 0)
        self.InsertColumn(0, _('Name'))
        self.InsertColumn(1, _('Filepath'))
        self.SetColumnWidth(0, 150)
        self.SetColumnWidth(1, 450)

        self.manifest = []

    def getSetupDir(self):
        return os.path.dirname(self.model.filename)

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        from Explorers.Explorer import openEx, TransportError
        manifestPath = self.getSetupDir() +'/Manifest'
        try:
            manifest = openEx(manifestPath).load()
        except TransportError, err:
            self.InsertStringItem(0, _('Error'))
            self.SetStringItem(0, 1, str(err))
            self.manifest = None
        else:
            self.manifest = []
            idx = -1
            for path in manifest.split('\n'):
                idx = idx + 1
                path = path.strip()
                if not path:
                    continue
                self.manifest.append(path)
                name = os.path.basename(path)
                self.InsertStringItem(idx, name)
                self.SetStringItem(idx, 1, path)

        self.pastelise()

    def OnOpen(self, event):
        if self.selected != -1 and self.manifest is not None:
            model, controller = self.model.editor.openOrGotoModule(
                  self.getSetupDir()+'/'+self.manifest[self.selected])

    def OnRefresh(self, event):
        self.refreshCtrl()


class CVSConflictsView(ListCtrlView):
    viewName = 'CVS conflicts'
    viewTitle = _('CVS conflicts')

    gotoLineBmp = 'Images/Editor/GotoLine.png'
    acceptBmp = 'Images/Inspector/Post.png'
    rejectBmp = 'Images/Inspector/Cancel.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          ((_('Goto line'), self.OnGoto, self.gotoLineBmp, ()),
           (_('Accept changes'), self.OnAcceptChanges, self.acceptBmp, ()),
           (_('Reject changes'), self.OnRejectChanges, self.rejectBmp, ()) ), 0)
        self.InsertColumn(0, _('Rev'))
        self.InsertColumn(1, _('Line#'))
        self.InsertColumn(2, _('Size'))
        self.SetColumnWidth(0, 40)
        self.SetColumnWidth(1, 40)
        self.SetColumnWidth(2, 40)

        self.conflicts = []

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        self.conflicts = self.model.getCVSConflicts()

        confCnt = 0
        for rev, lineNo, size in self.conflicts:
            self.InsertStringItem(confCnt, rev)
            self.SetStringItem(confCnt, 1, `lineNo`)
            self.SetStringItem(confCnt, 2, `size`)
            confCnt = confCnt + 1


        self.pastelise()

    def OnGoto(self, event):
        if self.model.views.has_key('Source'):
            srcView = self.model.views['Source']
            srcView.focus()
            lineNo = int(self.conflicts[self.selected][1]) -1
            srcView.gotoLine(lineNo)

    # XXX I've still to decide on this, operations should usually be applied
    # XXX thru the model, but by applying thru the STC you get it in the
    # XXX undo history
    def OnAcceptChanges(self, event):
        if self.selected != -1:
            self.model.acceptConflictChange(self.conflicts[self.selected])

    def OnRejectChanges(self, event):
        if self.selected != -1:
            self.model.rejectConflictChange(self.conflicts[self.selected])

class FolderEditorView(wx.Notebook, EditorView):
    viewName = 'Folder'
    viewTitle = _('Folder')

    def __init__(self, parent, model):
        wx.Notebook.__init__(self, parent, -1)
        EditorView.__init__(self, model,
          (), -1)#('Goto line', self.OnGoto, self.gotoLineBmp, ''),), 0)
        self.SetImageList(self.model.editor.tabs.GetImageList())
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChange, id=self.GetId())

    def refreshCtrl(self):
        pass

    def OnPageChange(self, event):
        pass

#-------------------------------------------------------------------------------

class EditorViewPlugin:
    pass
