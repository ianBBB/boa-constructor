#----------------------------------------------------------------------
# Name:        Editor.py
# Purpose:     The main IDE frame containing the Shell, Explorer and
#              opened objects
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:EditorFrame

""" The main IDE frame containing the Shell, Explorer and the ability to host
Models and their Views on ModulePages"""

print 'importing Editor'

import os, sys, pprint
import Queue

import wx

from Models import EditorHelper, Controllers

from EditorUtils import EditorToolBar, EditorStatusBar, ModulePage, socketFileOpenServerListen

import Preferences, Utils, Plugins
from Preferences import keyDefs, IS, flatTools
from Utils import BottomAligningSplitterWindow
from Utils import _

import About, Help, Browse

from Explorers import Explorer
from Explorers.ExplorerNodes import TransportError, TransportSaveError, TransportLoadError
import ShellEditor
#from ModRunner import EVT_EXEC_FINISH

# register language chooser
import LanguageSelectDlg

addTool = Utils.AddToolButtonBmpIS

class CancelClose(Exception): pass

(mmFile, mmEdit, mmViews, mmWindows, mmHelp) = range(5)

[wxID_EDITORFRAME, wxID_EDITORFRAMESTATUSBAR, wxID_EDITORFRAMETABS, 
 wxID_EDITORFRAMETABSSPLITTER, wxID_EDITORFRAMETOOLBAR, 
] = [wx.NewId() for _init_ctrls in range(5)]

class EditorFrame(wx.Frame, Utils.FrameRestorerMixin):
    """ Source code editor and host for the Model/View/Controller classes"""

    editorTitle = _('Editor')
    editorIcon = 'Images/Icons/Editor.ico'

    openBmp = 'Images/Editor/Open.png'
    backBmp = 'Images/Shared/Previous.png'
    forwBmp = 'Images/Shared/Next.png'
    recentBmp = 'Images/Editor/RecentFiles.png'
    helpBmp = 'Images/Shared/Help.png'
    helpIdxBmp = 'Images/Shared/CustomHelp.png'
    ctxHelpBmp = 'Images/Shared/ContextHelp.png'
    tipBmp = 'Images/Shared/Tip.png'
    aboutBmp = 'Images/Shared/About.png'
    shellBmp = 'Images/Editor/Shell.png'
    explBmp = 'Images/Editor/Explorer.png'
    inspBmp = 'Images/Shared/Inspector.png'
    paletteBmp = 'Images/Shared/Palette.png'
    prefsBmp = 'Images/Modules/PrefsFolder.png'

    _custom_classes = {'wx.SplitterWindow': ['BottomAligningSplitterWindow'],'wx.StatusBar': ['EditorStatusBar'],'wx.ToolBar': ['EditorToolBar'],}
    def _init_coll_mainMenu_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=wx.Menu(), title=_('File'))
        parent.Append(menu=wx.Menu(), title=_('Edit'))
        parent.Append(menu=wx.Menu(), title=_('Views'))
        parent.Append(menu=self.toolsMenu, title=_('Tools'))

    def _init_utils(self):
        # generated method, don't edit
        self.modelImageList = wx.ImageList(height=16, width=16)

        self.mainMenu = wx.MenuBar()

        self.blankEditMenu = wx.Menu(title='')

        self.blankViewMenu = wx.Menu(title='')

        self.helpMenu = wx.Menu(title='')

        self.toolsMenu = wx.Menu(title='')

        self._init_coll_mainMenu_Menus(self.mainMenu)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_EDITORFRAME, name='', parent=prnt,
              pos=wx.Point(68, 72), size=wx.Size(810, 515),
              style=wx.DEFAULT_FRAME_STYLE| Preferences.childFrameStyle,
              title=_('Editor'))
        self._init_utils()
        self.SetMenuBar(self.mainMenu)
        self.SetClientSize(wx.Size(802, 488))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.statusBar = EditorStatusBar(id=wxID_EDITORFRAMESTATUSBAR,
              name='statusBar', parent=self, style=0)
        self.SetStatusBar(self.statusBar)

        self.toolBar = EditorToolBar(id=wxID_EDITORFRAMETOOLBAR, name='toolBar',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(802, 28),
              style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.SetToolBar(self.toolBar)

        self.tabsSplitter = BottomAligningSplitterWindow(id=wxID_EDITORFRAMETABSSPLITTER,
              name='tabsSplitter', parent=self, size=wx.Size(802, 421), pos=wx.DefaultPosition,
              style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE | wx.SP_3DSASH)
        self.tabsSplitter.SetMinimumPaneSize(1)

        self.tabs = wx.Notebook(id=wxID_EDITORFRAMETABS, name='tabs',
              parent=self.tabsSplitter, pos=wx.Point(2, 2), size=wx.Size(798,
              417), style=wx.CLIP_CHILDREN)
        self.tabs.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,
              self.OnTabsNotebookPageChanged, id=wxID_EDITORFRAMETABS)

    def __init__(self, parent, id, inspector, newMenu, componentPalette, app, palette):
        self._created = False
        self._init_ctrls(parent)

        self.palette = palette
        self.winConfOption = 'editor'
        self.loadDims()

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        self.SetIcon(IS.load(self.editorIcon))

        self.app = app
        self.modules = {}
        self.inspector = inspector
        self.compPalette = componentPalette
        self.debugger = None
        self.browser = Browse.HistoryBrowser()
        self.controllers = {}
        self.shellPageIdx = self.explorerPageIdx = -1

        self.toolAccels = []
        self.tools = {}
        for toolInfo in EditorHelper.editorToolsReg:
            name, func = toolInfo[:2]
            bmp, key = '-', ''
            if len(toolInfo) == 3:
                bmp = toolInfo[2]
            elif len(toolInfo) == 4:
                bmp, key = toolInfo[2:]

            self.addToolMenu(self.toolAccels, name, func, bmp, key)

        # Hook for shell and scripts
        if not hasattr(sys, 'boa_ide'):
            sys.boa_ide = self

        self.numFixedPages = 0

        # Explorer store
        self.explorerStore = Explorer.ExplorerStore(self)
        # called after all models have been imported and plugins executed
        EditorHelper.initExtMap()
        self.initImages()

        # Shell
        shl = Preferences.psPythonShell
        self.shell, self.shellPageIdx = None, -1
        if ShellEditor.shellReg.has_key(shl):
            Shell, imgIdx = ShellEditor.shellReg[shl]

            self.shell, self.shellPageIdx = self.addShellPage(shl, Shell, imgIdx)

        # Explorer
        self.explorer, self.explorerPageIdx = self.addExplorerPage()

        if self.explorer:
            self.explorer.tree.openDefaultNodes()


        # Menus
        self.newMenu = newMenu
        self.Bind(wx.EVT_MENU, self.OnOpen, id=EditorHelper.wxID_EDITOROPEN)
        self.Bind(wx.EVT_MENU, self.OnOpenRecent, id=EditorHelper.wxID_EDITOROPENRECENT)
        self.Bind(wx.EVT_MENU, self.OnExitBoa, id=EditorHelper.wxID_EDITOREXITBOA)

        # Windows menu
        self.Bind(wx.EVT_MENU, self.OnSwitchShell, id=EditorHelper.wxID_EDITORSWITCHSHELL)
        self.Bind(wx.EVT_MENU, self.OnSwitchExplorer, id=EditorHelper.wxID_EDITORSWITCHEXPLORER)
        self.Bind(wx.EVT_MENU, self.OnSwitchPrefs, id=EditorHelper.wxID_EDITORSWITCHPREFS)
        self.Bind(wx.EVT_MENU, self.OnSwitchPalette, id=EditorHelper.wxID_EDITORSWITCHPALETTE)
        self.Bind(wx.EVT_MENU, self.OnSwitchInspector, id=EditorHelper.wxID_EDITORSWITCHINSPECTOR)
        self.Bind(wx.EVT_MENU, self.OnBrowseForward, id=EditorHelper.wxID_EDITORBROWSEFWD)
        self.Bind(wx.EVT_MENU, self.OnBrowseBack, id=EditorHelper.wxID_EDITORBROWSEBACK)
        self.Bind(wx.EVT_MENU, self.OnPrevPage, id=EditorHelper.wxID_EDITORPREVPAGE)
        self.Bind(wx.EVT_MENU, self.OnNextPage, id=EditorHelper.wxID_EDITORNEXTPAGE)
        self.Bind(wx.EVT_MENU, self.OnHidePalette, id=EditorHelper.wxID_EDITORHIDEPALETTE)
        self.Bind(wx.EVT_MENU, self.OnWinDimsLoad, id=EditorHelper.wxID_EDITORWINDIMSLOAD)
        self.Bind(wx.EVT_MENU, self.OnWinDimsSave, id=EditorHelper.wxID_EDITORWINDIMSSAVE)
        self.Bind(wx.EVT_MENU, self.OnWinDimsRestoreDefs, id=EditorHelper.wxID_EDITORWINDIMSRESDEFS)

        self.winDimsMenu = wx.Menu()
        self.winDimsMenu.Append(EditorHelper.wxID_EDITORWINDIMSLOAD, _('Load'),
              _('Load window dimensions from the config.'))
        self.winDimsMenu.Append(EditorHelper.wxID_EDITORWINDIMSSAVE, _('Save'),
              _('Save window dimensions to the config.'))
        self.winDimsMenu.Append(EditorHelper.wxID_EDITORWINDIMSRESDEFS,
              _('Restore defaults'), _('Restore dimensions to defaults'))

        self.winMenu =wx.Menu()
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHPALETTE,
              _('Palette'), '', self.paletteBmp, _('Switch to the Palette frame.'))
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHINSPECTOR,
              _('Inspector'), keyDefs['Inspector'], self.inspBmp,
              _('Switch to the Inspector frame.'))
        self.winMenu.AppendSeparator()
        if self.shell:
            Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHSHELL,
                  _('Shell'), keyDefs['GotoShell'], self.shellBmp,
                  _('Switch to the Shell page'))
        if self.explorer:
            Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHEXPLORER,
                  _('Explorer'), keyDefs['GotoExplorer'], self.explBmp,
                  _('Switch to the Explorer page'))
            Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHPREFS,
                  _('Preferences'), (), self.prefsBmp,
                  _('Switch to the Preferences in the Explorer'))
        if self.shell or self.explorer:
            self.winMenu.AppendSeparator()
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORBROWSEBACK,
              _('Browse back'), (), self.backBmp, #\t%s'%keyDefs['BrowseBack'][2],
              _('Go back in browsing history stack'))
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORBROWSEFWD,
              _('Browse forward'), (), self.forwBmp, #\t%s'%keyDefs['BrowseFwd'][2],
              _('Go forward in browsing history stack'))
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORPREVPAGE,
              _('Previous page'), keyDefs['PrevPage'], '-',
              _('Switch to the previous page of the main notebook'))
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORNEXTPAGE,
              _('Next page'), keyDefs['NextPage'], '-',
              _('Switch to the next page of the main notebook'))
        self.winMenu.AppendSeparator()
        self.winMenu.AppendMenu(EditorHelper.wxID_EDITORWINDIMS,
              _('All window dimensions'), self.winDimsMenu,
              _('Load, save or restore IDE windows dimensions'))
        self.winMenu.Append(EditorHelper.wxID_EDITORHIDEPALETTE,
              _('Hide Palette'), _('Hide the Palette frame'))
        self.winMenu.AppendSeparator()
        self.mainMenu.Append(self.winMenu, _('Windows'))

        # Help menu
        Utils.appendMenuItem(self.helpMenu, EditorHelper.wxID_EDITORHELP, _('Help'),
              (), self.helpBmp, _('Opens help for the Editor'))
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPGUIDE,
              _('Getting started guide'), _('Opens the Getting started guide'))
        self.helpMenu.AppendSeparator()
        Utils.appendMenuItem(self.helpMenu, EditorHelper.wxID_EDITORHELPFIND,
              _('Find in index...'), keyDefs['HelpFind'], self.helpIdxBmp,
              _('Pops up a text input for starting a search of the help indexes'))
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPOPENEX, _('Open an example...'),
              _('Opens file dialog in the Examples directory'))
        Utils.appendMenuItem(self.helpMenu, EditorHelper.wxID_EDITORHELPTIPS,
              _('Tips'), (), self.tipBmp, _('Opens the "Tip of the Day" window'))
        self.helpMenu.AppendSeparator()
        Utils.appendMenuItem(self.helpMenu, EditorHelper.wxID_EDITORHELPABOUT,
              _('About'), (), self.aboutBmp, _('Opens the About box'))

        self.Bind(wx.EVT_MENU, self.OnHelp, id=EditorHelper.wxID_EDITORHELP)
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, id=EditorHelper.wxID_EDITORHELPABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelpGuide, id=EditorHelper.wxID_EDITORHELPGUIDE)
        self.Bind(wx.EVT_MENU, self.OnHelpTips, id=EditorHelper.wxID_EDITORHELPTIPS)
        self.Bind(wx.EVT_MENU, self.OnHelpFindIndex, id=EditorHelper.wxID_EDITORHELPFIND)
        self.Bind(wx.EVT_MENU, self.OnOpenExample, id=EditorHelper.wxID_EDITORHELPOPENEX)

        if wx.Platform == '__WXMAC__':
            helpMenuTitleName = _('&Help')
            self.mainMenu.Append(self.helpMenu, helpMenuTitleName)
            wx.App.SetMacExitMenuItemId(EditorHelper.wxID_EDITOREXITBOA)
            wx.App.SetMacAboutMenuItemId(EditorHelper.wxID_EDITORHELPABOUT)
            wx.App.SetMacPreferencesMenuItemId(EditorHelper.wxID_EDITORSWITCHPREFS)
        else:
            helpMenuTitleName = _('Help')
            self.mainMenu.Append(self.helpMenu, helpMenuTitleName)

        if Preferences.suSocketFileOpenServer:
            # Start listening for requests to open files. Listener will run,
            # passing filenames to openOrGotoModule, until closed is set.
            self.closed, self.listener = socketFileOpenServerListen(self)
        else:
            self.closed = None

        # create initial toolbar buttons and menus
        self._prevMod = None
        self._prevView = None
        self._prevContrl = None
        self._created = True
        self._blockToolbar = False
##        self.defaultAdtViews = {}
        self.setupToolBar(viewIdx = 0)

        dt = Utils.BoaFileDropTarget(self)
        self.SetDropTarget(dt)

        # init (docked) error output frame
        import ErrorStackFrm
        self.erroutFrm = ErrorStackFrm.ErrorStackMF(self, self)

        self.tabs.SetMinSize(wx.DefaultSize)
        self.erroutFrm.notebook.SetMinSize(wx.DefaultSize)
        if Preferences.eoErrOutDockWindow == 'editor':
            self.erroutFrm.notebook.Reparent(self.tabsSplitter)
            self.tabsSplitter.SplitHorizontally(self.tabs, self.erroutFrm.notebook,
              self.tabsSplitter.GetClientSize().y - self.tabsSplitter.GetSashSize())
        else:
            if Preferences.eoErrOutDockWindow == 'inspector':
                panel, notebook = \
                  Utils.wxProxyPanel(self.inspector.pages, self.erroutFrm.notebook)
                self.inspector.pages.AddPage(panel, 'ErrOut')
            self.tabsSplitter.Initialize(self.tabs)
        wx.PostEvent(self.tabsSplitter, wx.SizeEvent(self.tabsSplitter.GetSize()))

        # Hack to feed BoaFileDialog images
        import FileDlg
        FileDlg.wxBoaFileDialog.modImages = self.modelImageList

        #self.Bind(wx.EVT_EXEC_FINISH, self.OnExecFinish)
        self.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.OnMenuHighlight)

        from FindReplaceEngine import FindReplaceEngine
        self.finder = FindReplaceEngine()

        # quit server mode flag not guaranteed to be set (yet) even if there is
        # already a server running, but don't connect idle if not necessary
        if self.closed:
            if self.closed.isSet():
                print 'Not running in server mode'

    def __repr__(self):
        return '<EditorFrame (Boa IDE) instance at %d>'%id(self)

    def setDefaultDimensions(self):
        self.SetDimensions(Preferences.inspWidth + Preferences.windowManagerSide*2 +\
              Preferences.screenX, Preferences.underPalette + Preferences.screenY, 
              Preferences.edWidth, Preferences.bottomHeight)
        #if not self.palette.IsShown():
        #    self.Center()

    def expandOnInspectorClose(self):
        iPos = self.inspector.GetPosition()
        ePos = self.GetPosition()
        size = self.GetSize()
        width = size.x +self.inspector.GetSize().x
        self.SetDimensions(min(iPos.x, ePos.x), ePos.y, width, size.y)

    def restoreOnInspectorRestore(self):
        Utils.FrameRestorerMixin.loadDims(self)

    def releasePrevResources(self):
        self.toolBar.DisconnectToolIds()
        self.toolBar.ClearTools()

        if self._prevView:
            self._prevView.disconnectEvts()
            self._prevView = None
        if self._prevMod:
            self._prevMod.disconnectEvts()
            self._prevMod = None
        if self._prevContrl:
            self._prevContrl.disconnectEvts()
            self._prevContrl = None

    def initImages(self):
        # Build imageidx: filename list of all Editor images
        allImages = {}
        for img in EditorHelper.builtinImgs:
            allImages[len(allImages)] = img
        for mod in EditorHelper.modelReg.values():
            allImages[mod.imgIdx] = 'Images/Modules/'+mod.bitmap
        # XXX move ZOAImages/Icons into EditorHelper.extraImages updated from ZopeEditorModels
        if Plugins.transportInstalled('ZopeLib.ZopeExplorer'):
            from ZopeLib import ZopeEditorModels
            for metatype, filename in ZopeEditorModels.ZOAImages:
                idx = ZopeEditorModels.ZOAIcons[metatype]
                if allImages.has_key(idx) and filename != allImages[idx]:
                    print 'ImgIdx clash:', idx, filename, 'clashes with', allImages[idx]
                allImages[idx] = filename
        for imgIdx, name in EditorHelper.pluginImgs:
            allImages[imgIdx] = name

        # Populate imagelist
        imgIdxs = allImages.keys()
        imgIdxs.sort()
        for idx in imgIdxs:
            try:
                midx = self.modelImageList.Add(IS.load(allImages[idx]))
            except IS.Error: 
                midx = -1
            if idx != midx:
                print 'Image index mismatch', idx, midx, allImages[idx]

        self.tabs.SetImageList(self.modelImageList)

    def setupToolBar(self, modelIdx=None, viewIdx=None, force=False):
        """ Build toolbar and menus based on currently active IDE selection """
        if not self._created or self._blockToolbar:
            return

        if self.palette.destroying and not force:
            return

        self.releasePrevResources()

        accLst = self.toolAccels[:]
        for (ctrlKey, key, code), wId in (
              (keyDefs['Inspector'], EditorHelper.wxID_EDITORSWITCHINSPECTOR),
              (keyDefs['Open'], EditorHelper.wxID_EDITOROPEN),
              (keyDefs['HelpFind'], EditorHelper.wxID_EDITORHELPFIND),
              (keyDefs['GotoShell'], EditorHelper.wxID_EDITORSWITCHSHELL),
              (keyDefs['GotoExplorer'], EditorHelper.wxID_EDITORSWITCHEXPLORER),
              (keyDefs['BrowseBack'], EditorHelper.wxID_EDITORBROWSEBACK),
              (keyDefs['BrowseFwd'], EditorHelper.wxID_EDITORBROWSEFWD),
              (keyDefs['PrevPage'], EditorHelper.wxID_EDITORPREVPAGE),
              (keyDefs['NextPage'], EditorHelper.wxID_EDITORNEXTPAGE) ):
            accLst.append( (ctrlKey, key, wId) )

        # primary option: open a module
        fileMenu = wx.Menu()
        if self.palette.palettePages and Preferences.edShowFileNewMenu:
            fileMenu.AppendMenu(wx.NewId(), _('New'),
                  Utils.duplicateMenu(self.palette.palettePages[0].menu))
        Utils.appendMenuItem(fileMenu, EditorHelper.wxID_EDITOROPEN, _('Open'),
              keyDefs['Open'], self.openBmp, _('Open a module'))
        Utils.appendMenuItem(fileMenu, EditorHelper.wxID_EDITOROPENRECENT,
              _('Open recent files'), (), self.recentBmp)

        addTool(self, self.toolBar, self.openBmp, _('Open a module'), self.OnOpen)

        self.bbId = addTool(self, self.toolBar, self.backBmp, _('Browse back'), self.OnBrowseBack)
        self.bfId = addTool(self, self.toolBar, self.forwBmp, _('Browse forward'), self.OnBrowseForward)

        activeView = None
        actMod = self.getActiveModulePage(modelIdx)
        if actMod:
            actMod.connectEvts()
            self._prevMod = actMod

            ModClass = actMod.model.__class__
            ctrlr = self.getControllerFromModel(actMod.model)
            if ctrlr:
                self.toolBar.AddSeparator()
                accls = ctrlr.addActions(self.toolBar, fileMenu, actMod.model)
                self._prevContrl = ctrlr
                accLst.extend(accls)

            fileMenu.AppendSeparator()
            fileMenu.Append(EditorHelper.wxID_EDITOREXITBOA,
                  _('Exit Boa Constructor'), _('Exit Boa Constructor'))
            self.mainMenu.Replace(mmFile, fileMenu, _('File')).Destroy()

            # Edit menu
            activeView = actMod.getActiveView(viewIdx)
            if activeView:
                activeView.connectEvts()
                self._prevView = activeView

                activeView.addViewTools(self.toolBar)
                menu, accls = activeView.addViewMenus()
                self.mainMenu.Replace(mmEdit, menu, _('Edit')).Destroy()
                accLst.extend(accls)

                # Views menu
                # XXX Should only recalculate when module switches
                actMod.setActiveViewsMenu()

                menu = Utils.duplicateMenu(actMod.viewMenu)
                self.mainMenu.Replace(mmViews, menu, _('Views')).Destroy()
        else:
            if modelIdx == self.explorerPageIdx and self.explorer:
                self.explorer.addTools(self.toolBar)
                menu = self.explorer.getMenu()
                if menu:
                    self.mainMenu.Replace(mmEdit, Utils.duplicateMenu(menu),
                          _('Edit')).Destroy()
                else:
                    self.mainMenu.Replace(mmEdit,
                      Utils.duplicateMenu(self.blankEditMenu), _('Edit')).Destroy()
            else:
                self.mainMenu.Replace(mmEdit,
                  Utils.duplicateMenu(self.blankEditMenu), _('Edit')).Destroy()

            fileMenu.AppendSeparator()
            fileMenu.Append(EditorHelper.wxID_EDITOREXITBOA,
                  _('Exit Boa Constructor'), _('Exit Boa Constructor'))
            self.mainMenu.Replace(mmFile, fileMenu, _('File')).Destroy()

            self.mainMenu.Replace(mmViews,
                  Utils.duplicateMenu(self.blankViewMenu), _('Views')).Destroy()

        # Help button
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.helpBmp),
              _('Help'), self.OnHelp)

        self.toolBar.Realize()

        self.updateBrowserBtns()

        if accLst:
            self.SetAcceleratorTable(wx.AcceleratorTable(accLst))

    def addToolMenu(self, accelLst, name, eventFunc, bmp='-', key=''):
        wId =wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnActivateTool, id=wId)
        if key:
            code = keyDefs[key]
            accelLst.append( (code[0], code[1], wId) )
        else:
            code = ()
        self.tools[wId] = (name, eventFunc)
        Utils.appendMenuItem(self.toolsMenu, wId, name, code, bmp)

    def OnActivateTool(self, event):
        wId = event.GetId()
        name, toolFunc = self.tools[wId]
        toolFunc(self)

    def updateStaticMenuShortcuts(self):
        wm, hm = self.winMenu, self.helpMenu
        for menu, mId, label in ( (wm, EditorHelper.wxID_EDITORSWITCHINSPECTOR,
               _('Inspector')+'\t%s'%keyDefs['Inspector'][2]),
              (wm, EditorHelper.wxID_EDITORSWITCHSHELL,
               _('Shell')+'\t%s'%keyDefs['GotoShell'][2]),
              (wm, EditorHelper.wxID_EDITORSWITCHEXPLORER,
               _('Explorer')+'\t%s'%keyDefs['GotoExplorer'][2]),
              (wm, EditorHelper.wxID_EDITORPREVPAGE,
               _('Previous window')+'\t%s'%keyDefs['PrevPage'][2]),
              (wm, EditorHelper.wxID_EDITORNEXTPAGE,
               _('Next window')+'\t%s'%keyDefs['NextPage'][2]),
              (hm, EditorHelper.wxID_EDITORHELPFIND,
               _('Find in index...')+'\t%s'%keyDefs['HelpFind'][2]) ):
            menu.SetLabel(mId, label)

    def updateBrowserBtns(self):
        self.toolBar.EnableTool(self.bbId, self.browser.canBack())
        self.toolBar.EnableTool(self.bfId, self.browser.canForward())

    def doAfterShownActions(self):
        self.statusBar.linkProgressToStatusBar()
        self.statusBar.erroutFrm = self.erroutFrm
        if self.explorer:
            tree = self.explorer.tree
            if tree.defaultBookmarkItem:
                tree.SelectItem(tree.defaultBookmarkItem)
                self.explorer.list.SetFocus()

    def addShellPage(self, name, Shell, imgIdx):
        """ Adds the interactive interpreter to the editor """
        if wx.Platform == '__WXGTK__':
            # A panel between the STC and notebook reduces flicker
            tabPage, shellEdit = \
                  Utils.wxProxyPanel(self.tabs, Shell, -1)
        else:
            shellEdit = tabPage = Shell(self.tabs, -1)

        self.tabs.AddPage(tabPage, name, imageId=imgIdx)
        self.numFixedPages += 1

        return shellEdit, self.tabs.GetPageCount()-1


    def addExplorerPage(self):
        if Preferences.exUseExplorer:
            explorer = Explorer.ExplorerSplitter(self.tabs, self.modelImageList,
                                                 self, self.explorerStore)

            self.tabs.AddPage(explorer, _('Explorer'), imageId=EditorHelper.imgExplorer)
            self.numFixedPages += 1
            return explorer, self.tabs.GetPageCount()-1
        else:
            return None, -1

    def getValidName(self, modelClass, moreUsedNames = None):
        className = modelClass.defaultName.split('.')[-1]
        if moreUsedNames is None:
            moreUsedNames = []
        def tryName(className, fileExt, n):
            return 'none://%s%d%s' %(className, n, fileExt)
        n = 1
        #Obfuscated one-liner to check if such a name exists as a basename
        #in a the dict keys of self.module
        while filter(lambda key, name=tryName(className, modelClass.ext, n): \
              os.path.basename(key) == os.path.basename(name),
              self.modules.keys() + moreUsedNames):
            n = n + 1

        return tryName(className, modelClass.ext, n)

    def addModulePage(self, model, moduleName, defViews, views, imgIdx, notebook=None):
        if notebook is None:
            notebook = self.tabs

        if Preferences.editorNotebookOpenPos == 'current':
            spIdx = max(notebook.GetSelection() + 1, self.numFixedPages)

            modulePage = ModulePage(notebook, model, defViews, views, spIdx, self)

            # notify pages for idx adjustments
            for modPge in self.modules.values():
                modPge.addedPage(spIdx)

            if self.modules.has_key(moduleName):
                # XXX raise here
                print 'module %s exists'%moduleName
            self.modules[moduleName] = modulePage
            notebook.InsertPage(spIdx, modulePage.notebook, modulePage.pageName, True, imgIdx)

        elif Preferences.editorNotebookOpenPos == 'append':
            spIdx = notebook.GetPageCount()

            modulePage = ModulePage(notebook, model, defViews, views, spIdx, self)
            self.modules[moduleName] = modulePage
            notebook.AddPage(modulePage.notebook, modulePage.pageName, True, imgIdx)


        # XXX wxGTK does not trigger an AfterPageChangeEvent
        if wx.Platform == '__WXGTK__':
            self.OnTabsNotebookPageChanged(None, spIdx)

        notebook.SetSelection(spIdx)
        modulePage.refresh()
        self.editorUpdateNotify()

    def closeModulePage(self, modulePage, shutdown=False):
        actPge = self.tabs.GetSelection()
        numPgs = self.tabs.GetPageCount()
        if modulePage:
            try:
                self.closeModule(modulePage)
            except CancelClose:
                if shutdown: raise
                else:
                    self.updateTitle()
                    self.setupToolBar()
                    return
            except TransportSaveError, error:
                if shutdown: raise
                else:
                    wx.LogError(str(error))
                    return

            self.mainMenu.Replace(mmEdit, wx.Menu(), 'Edit').Destroy()
            if actPge == numPgs - 1:
                self.tabs.SetSelection(numPgs - self.numFixedPages)
            else:
                self.tabs.SetSelection(actPge)

            self.editorUpdateNotify()

            # XXX Work around bug where notebook change event differs between
            # XXX 2.3.2 and 2.3.3
            # XXX This overrides the wrong title and toolbar/menus set by the
            # XXX notebook change event
            sel = self.tabs.GetSelection()
            if sel > -1:
                self.updateTitle(sel)
                self.setupToolBar(sel)

    def getActiveModulePage(self, page=None):
        if page is None:
            page = self.tabs.GetSelection()
        # this excludes shell
        if page >= self.numFixedPages:
            for mod in self.modules.values():
                if mod.tIdx == page:
                    return mod
        # XXX raise on not found ?
        return None

    def focusActiveView(self):
        mp = self.getActiveModulePage()
        if mp:
            v = mp.getActiveView()
            if v:
                v.SetFocus()

    def activeApp(self):
        actMod = self.getActiveModulePage()
        if actMod and actMod.model.modelIdentifier in Controllers.appModelIdReg \
              and actMod.model.data <> '':
            return actMod
        else:
            return None

    def getController(self, Controller, *args):
        if not self.controllers.has_key(Controller):
            self.controllers[Controller] = Controller(*((self,) + args))

        return self.controllers[Controller]

    def addNewPage(self, metatype, Controller, modelParent=None):
        controller = self.getController(Controller)

        if modelParent is None:
            modelParent = self.activeApp()
            if modelParent:
                modelParent = modelParent.model

        model, name = controller.createNewModel(modelParent)
        if controller.docked:
            if model:
                self.addModulePage(model, name, controller.DefaultViews,
                                   controller.AdditionalViews, model.imgIdx)

                controller.afterAddModulePage(model)
                model.notify()
                self.updateTitle()
        else:
            controller.display(model)

        return model

    def getAppModules(self):
        """ Return a list of all open Application modules """
        apps = []
        for modPage in self.modules.values():
            if modPage.model.modelIdentifier in Controllers.appModelIdReg:
                apps.append(modPage.model)
        return apps

    def getControllerFromModel(self, model):
        ModClass = model.__class__
        if Controllers.modelControllerReg.has_key(ModClass):
            Controller = Controllers.modelControllerReg[ModClass]
            if self.controllers.has_key(Controller):
                return self.controllers[Controller]
            elif self.controllers.has_key(ModClass):
                return self.controllers[ModClass]
        return None

#---Opening and closing items in the IDE----------------------------------------
    def openOrGotoModule(self, name, app=None, transport=None, notebook=None):
        """ Main entrypoint to open a file in the editor.

        Defaults to 'file' if no protocol given.
        Optionally handles <filename>::<lineno> format to start on a given line
        Case insensitively find model if already open.
        """

        app = None

        if name.find('://') == -1:
            name = 'file://'+name

        lineno = name.rfind('::')
        if lineno != -1:
            try: name, lineno = name[:lineno], int(name[lineno+2:]) -1
            except: lineno = -1

        controller = None
        name = Explorer.splitURI(name)[-1]
        if self.modules.has_key(name):
            self.modules[name].focus()
            model = self.modules[name].model
            controller = self.getControllerFromModel(model)
        else:
            # Check non case sensitive (fix for breakpoints)
            lst = self.modules.keys()
            assos = {}
            for keyIdx in range(len(lst)):
                assos[os.path.normcase(os.path.abspath(lst[keyIdx]))] = lst[keyIdx]

            a_name = os.path.normcase(os.path.abspath(name))
            if assos.has_key(a_name):
                self.modules[assos[a_name]].focus()
                model = self.modules[assos[a_name]].model
                controller = self.getControllerFromModel(model)
            else:
                model, controller = self.openModule(name, app, transport, notebook)

        if lineno != -1 and model.views.has_key('Source'):
            model.views['Source'].GotoLine(lineno)

        if controller is None:
            # XXX Use default controller class
            # XXX This path broken for Zope because of Model keys
            controller = self.getController(Controllers.modelControllerReg.get(
                  model.__class__, Controllers.DefaultController))

        if self.palette.IsShown():
            if self.palette.IsIconized() and self.IsIconized():
                self.palette.restore()
        elif self.IsIconized():
            self.restore()

        return model, controller

    def openModule(self, filename, app=None, transport=None, notebook=None):
        """ Open a Model in the IDE.

        Filename must be a valid URI.
        """
        # Get transport based on filename
        prot, category, respath, filename = Explorer.splitURI(filename)

        assert not self.modules.has_key(filename), _('File already open.')

        if prot == 'zope':
            if transport is None:
                transport = Explorer.getTransport(prot, category, respath,
                      self.explorerStore.transports)
            return self.openZopeDocument(transport, filename)
        else:
        # XXX commented for testing
        #elif not transport:
            if prot == 'file':
                if not os.path.isabs(respath):
                    respath = os.path.abspath(respath)
                    filename = prot+'://'+respath

            transport = Explorer.getTransport(prot, category, respath,
                self.explorerStore.transports)
            # connect if not a stateless connection
            if transport.connection:
                wx.BeginBusyCursor()
                try: transport.openList()
                finally: wx.EndBusyCursor()

        assert transport, _('Cannot open, no transport defined.')

        mode = 'rb'

        wx.BeginBusyCursor()
        try: source = transport.load(mode)
        finally: wx.EndBusyCursor()

        # Get Model based on the file type
        modCls, main = Controllers.identifyFile(filename, source)

        # See if file is entry in an open app
        if modCls.modelIdentifier not in Controllers.appModelIdReg and app is None:
            for openApp in self.getAppModules():
                normedMods = []
                for pth in openApp.absModulesPaths():
                    normedMods.append(os.path.normcase(pth))
                if os.path.normcase(filename) in normedMods:
                    app = openApp
                    break

        # Get MVC objects
        controller = self.getController(Controllers.modelControllerReg.get(
              modCls, Controllers.DefaultController))
        model = controller.createModel(source, filename, main, True, app)
        defViews = controller.DefaultViews
        views = controller.AdditionalViews

        model.transport = transport

        # Add in IDE or display
        if controller.docked:
            self.addModulePage(model, filename, defViews, views, model.imgIdx, notebook)
        else:
            controller.display(model)

        model.notify()

        return model, controller

    def getZopeController(self, Model):
        if not self.controllers.has_key(Model):
            self.controllers[Model] = \
                  Controllers.modelControllerReg[Model](self, Model)
        return self.controllers[Model]

    # XXX Unify with the rest of the explorers
    def openOrGotoZopeDocument(self, zopeObj):
        wholename=zopeObj.getURI()
        if self.modules.has_key(wholename):
            self.modules[wholename].focus()
            controller = self.getZopeController(zopeObj.Model)
            return self.modules[wholename].model, controller
        else:
            return self.openZopeDocument(zopeObj, wholename)

    # XXX Unify with the rest of the explorers
    def openZopeDocument(self, zopeObj, wholename):
        if zopeObj and zopeObj.Model:
            controller = self.getZopeController(zopeObj.Model)

            model = controller.createModel('', wholename, '', False, zopeObj)

            model.transport = zopeObj
            model.load()

            self.addModulePage(
                model, wholename, zopeObj.defaultViews,
                zopeObj.additionalViews, zopeObj.Model.imgIdx)
            model.notify()

            self.updateTitle()
            return model, controller
        else:
            wx.LogWarning(_('Zope Object %s not supported') % `zopeObj`)
            return None, None

    def addNewView(self, name, viewClass):
        module = self.getActiveModulePage()
        if module:
            if not module.model.views.has_key(name):
                return module.addView(viewClass, name)
            else:
                return module.model.views[name]

    def addNewDialog(self, dlgClass, dlgCompanion):
        module = self.getActiveModulePage()
        if module:
            view = module.getActiveView()
            if view and view.viewName == 'Source':
                compn = dlgCompanion('dlg', None)
                view.insertCodeBlock(compn.body())

    def getOpenFromHereDir(self):
        # XXX Should open dlg open from the Explorer position if it's the active page?
        curdir = '.'
        actMod = self.getActiveModulePage()
        if actMod:
            filename = actMod.model.filename
            if filename:
                curdir = os.path.dirname(filename)
                if not curdir or curdir == 'none:':
                    curdir = '.'
        return curdir

    def openFileDlg(self, filter='*.py', curdir='.', curfile=''):
        if filter == '*.py': filter = Preferences.exDefaultFilter

        if curdir=='.' and getattr(Preferences, 'exOpenFromHere', 1):
            # Open relative to the file in the active module page.
            curdir = self.getOpenFromHereDir()

        from FileDlg import wxFileDialog
        dlg = wxFileDialog(self, _('Choose a file'), curdir, curfile, filter, wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath()
        finally:
            dlg.Destroy()
        return ''

    def saveAsDlg(self, filename, filter = '*.py'):#, dont_pop=0):
        if filter == '*.py': filter = Preferences.exDefaultFilter

        segs = Explorer.splitURI(filename)
        dir, name = os.path.split(segs[2])
        if not dir:
            dir = '.'
        if dir[-1] == ':':
            dir = dir[:-1]

        from FileDlg import wxFileDialog
        dlg = wxFileDialog(self, _('Save as...'), dir, name, filter,
              wx.SAVE | wx.OVERWRITE_PROMPT)
        #dlg.dont_pop = dont_pop
        try:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath(), True
            else:
                return '', False
        finally:
            dlg.Destroy()

    def activeModSaveOrSaveAs(self, forceSaveAs=False):
        modulePage = self.getActiveModulePage()
        if modulePage:
            modulePage.model.refreshFromViews()
            modulePage.saveOrSaveAs(forceSaveAs)

    def prepareForCloseModule(self, modulePage, focusPromptingPages=False,
                              caption=_('Close module')):
        # XXX most of this should move to ModulePage
        idx = modulePage.tIdx
        model = modulePage.model
        name = model.filename
        if self.modules.has_key(name):
            if model.views.has_key('Designer'):
                model.views['Designer'].close()

            insp = self.inspector
            try:
                if insp.selCmp and insp.sessionHandler and \
                  hasattr(insp.selCmp, 'model') and model is insp.selCmp.model:
                    insp.sessionHandler.promptPostOrCancel(insp)
            except:
                if focusPromptingPages:
                    self.tabs.SetSelection(idx)
                    self.setupToolBar(idx, force=True)

                raise CancelClose

            model.refreshFromViews()
            if model.modified:
                if focusPromptingPages:
                    self.tabs.SetSelection(idx)
                    self.setupToolBar(idx, force=True)

                dlg = wx.MessageDialog(self, _('There are changes, do you want to save?'),
                        caption, wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                try: res = dlg.ShowModal()
                finally: dlg.Destroy()
                if res == wx.ID_YES:
                    self.activeModSaveOrSaveAs()
                    name = model.filename
                elif res == wx.ID_CANCEL:
                    raise CancelClose
            return idx, name
        else:
            return -1, None


    def closeModule(self, modulePage):
        idx, name = self.prepareForCloseModule(modulePage)

        if idx != -1:
            self.browser.checkRemoval(modulePage)
            self.tabs.RemovePage(idx)
            del self.modules[name]
            modulePage.destroy()

            # notify pages for idx adjustments
            for modPge in self.modules.values():
                modPge.removedPage(idx)


#---Visual updating methods-----------------------------------------------------
    def updateModuleState(self, model, filename='', pageIdx=None):
        self.updateModulePage(model, filename)
        self.updateTitle(pageIdx)

    def updateTitle(self, pageIdx = None):
        """ Updates the title of the Editor to reflect changes in selection,
            filename or model state.
        """

        # XXX Do decorations here
        modulePage = self.getActiveModulePage(pageIdx)
        if modulePage:
            self.SetTitle('%s - %s - %s' %(self.editorTitle,
                  modulePage.pageName, modulePage.model.filename))
        else:
            if pageIdx is None:
                pageIdx = self.tabs.GetSelection()
            self.SetTitle('%s - %s' % (self.editorTitle,
                  self.tabs.GetPageText(pageIdx)))

    def updateModulePage(self, model, filename=''):
        if filename:
            modPge = self.modules[filename]
        else:
            modPge = self.modules[model.filename]
        self.tabs.SetPageText(modPge.tIdx, modPge.updatePageName())

    def assureRefreshed(self):
        sel = self.tabs.GetSelection()
        if sel != -1:
            page = self.tabs.GetPage(sel)
            if page:
                page.SetFocus()

            self.updateTitle(sel)
            self.setupToolBar(sel)

    # XXX this looks like overkill
    def clearAllStepPoints(self):
        for mod in self.modules.values():
            if mod.model.views.has_key('Source'):
                mod.model.views['Source'].setStepPos(0)

    def setStatus(self, hint, msgType='Info', ringBell=False):
        self.statusBar.setHint(hint, msgType, ringBell)

    def getMainFrame(self):
        if self.palette.IsShown():
            return self.palette
        else:
            return self

    def minimizeBoa(self):
        if self.palette.IsShown() and not self.palette.IsIconized():
            self.palette.Iconize(True)
        elif not self.IsIconized():
            self.Iconize(True)

    def editorUpdateNotify(self):
        if self.explorer: self.explorer.editorUpdateNotify()

    def explorerRenameNotify(self, oldURI, newNode):
        if self.modules.has_key(oldURI):
            modulePage = self.modules[oldURI]
            modulePage.model.transport = newNode
            modulePage.model.updateNameFromTransport()
            newURI = newNode.getURI()
            modulePage.rename(oldURI, newURI)

            self.updateModulePage(modulePage.model, newURI)

    def explorerDeleteNotify(self, uri):
        if self.modules.has_key(uri):
            self.closeModulePage(self.modules[uri])

    def explorerModifyNotify(self, uri):
        if self.modules.has_key(uri):
            model = self.modules[uri].model

            model.load()

            mp = self.getActiveModulePage()
            if mp.model.filename == uri:
                self.updateModuleState(model)

    def OnOpen(self, event, curdir='.'):
        fn = self.openFileDlg(curdir=curdir)
        if fn:
            self.openOrGotoModule(fn)
            self.explorerStore.recentFiles.add(fn)

            if self.explorer:
                tree = self.explorer.tree
                node = tree.GetPyData(tree.GetSelection())
                if node and node.protocol == 'recent.files':
                    self.explorer.list.refreshCurrent()

    def OnOpenRecent(self, event, curdir='.'):
        self.OnOpen(event, 'recent.files://')

    def OnTabsNotebookPageChanged(self, event, sel=None):
        if sel is None:
            sel = event.GetSelection()
        if sel > -1:
            self.updateTitle(sel)
            if self._created:
                self.setupToolBar(sel)
                if sel == 1:
                    self.editorUpdateNotify()

            if event: event.Skip()
            # focus the active page
            if self._created:
                if sel > max(self.shellPageIdx, self.explorerPageIdx, -1):
                    wx.CallAfter(self.focusView, sel)
                else:
                    wx.CallAfter(self.focusPage, sel)

    def focusPage(self, sel):
        page = self.tabs.GetPage(sel)
        page.SetFocus()

    def focusView(self, sel):
        page = self.tabs.GetPage(sel)
        if page.__class__.__name__ != 'Notebook':
            page = page.GetChildren()[0]

        sel = page.GetSelection()
        if sel >= 0:
            view = page.GetPage(sel)
            view.SetFocus()

#---Help events-----------------------------------------------------------------
    def OnHelp(self, event):
        Help.showHelp('Editor.html')

    def OnHelpGuide(self, event):
        Help.showMainHelp('Boa Constructor Getting Started Guide')

    def OnHelpTips(self, event):
        Utils.showTip(self, True)

    def OnHelpAbout(self, event):
        abt = About.DefAboutBox(None)
        try:     abt.ShowModal()
        finally: abt.Destroy()

    def OnHelpFindIndex(self, event):
        dlg = wx.TextEntryDialog(self, _('Enter term to search for in the index'),
              _('Help - Find in index'), '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                Help.showContextHelp(dlg.GetValue())
        finally:
            dlg.Destroy()

    def OnContextHelp(self, event):
        wx.ContextHelp(self)

    def OnOpenExample(self, event):
        exampleDir = os.path.join(Preferences.pyPath, 'Examples')
        self.OnOpen(event, exampleDir)

    def OnToggleView(self, event, evtId=None):
        if evtId is None:
            evtId = event.GetId()
        mod = self.getActiveModulePage()
        if mod:
            modVwClss = [v.__class__ for v in mod.model.views.values()]
            #Find view class associated with this id
            for viewCls, wId in mod.adtViews:
                if wId == evtId:
                    if self.mainMenu.IsChecked(evtId):
                        #Should be added, but check that it doesn't exist
                        if viewCls not in modVwClss:
                            view = mod.addView(viewCls)
                            try:
                                view.refreshCtrl()
                            except:
                                notebook = view.notebook
                                view.deleteFromNotebook(mod.default, view.viewName)
                                self.mainMenu.Check(evtId, False)

                                # repaint over glitch on windows
                                # Update(), Refresh() does not work
                                if wx.Platform == '__WXMSW__':
                                    notebook.Show(False)
                                    notebook.Show(True)

                                raise
                            else:
                                view.focus()
                        else:
                            print 'Add: View already exists'
                    else:
                        #Should be removed, but check that it does exist
                        if viewCls in modVwClss:
                            viewName = viewCls.viewName
                            view = mod.model.views[viewName]
                            if view.modified:
                                view.refreshModel()
                            view.deleteFromNotebook(mod.default, viewName)

                            self.mainMenu.Check(evtId, False)
                            return
                        else:
                            print 'Remove: View already exists'
                    break

    def OnSwitchedToView(self, event):
        # This is triggered twice, I'd love to know why
        pass

#---Switching to different windows----------------------------------------------
    def OnGotoModulePage(self, event):
        wId = event.GetId()
        for mod in self.modules.values():
            if mod.windowId == wId:
                self.tabs.SetSelection(mod.tIdx)

    def OnSwitchShell(self, event=None):
        if self.shellPageIdx != -1:
            self.tabs.SetSelection(self.shellPageIdx)

    def OnSwitchExplorer(self, event):
        if self.tabs.GetSelection() == self.explorerPageIdx:
            tree = self.explorer.tree
            child, cookie = tree.GetFirstChild(tree.GetRootItem())
            tree.SelectItem(child)
            self.explorer.list.SetFocus()
            STATE = wx.LIST_STATE_FOCUSED|wx.LIST_STATE_SELECTED
            self.explorer.list.SetItemState(0, STATE, STATE)
        elif self.explorerPageIdx != -1:
            self.tabs.SetSelection(self.explorerPageIdx)

    def OnSwitchPrefs(self, event):
        if self.explorerPageIdx != -1:
            self.tabs.SetSelection(self.explorerPageIdx)
            tree = self.explorer.tree
            cookie = 0
            child = tree.GetLastChild(tree.GetRootItem())
            tree.SelectItem(child)
            tree.EnsureVisible(child)
            self.explorer.list.SetFocus()
            STATE = wx.LIST_STATE_FOCUSED|wx.LIST_STATE_SELECTED
            self.explorer.list.SetItemState(1, STATE, STATE)

    def OnSwitchPalette(self, event):
        self.palette.restore()

    def OnSwitchInspector(self, event):
        self.inspector.restore()

    def OnNextPage(self, event):
        pc = self.tabs.GetPageCount()
        idx = self.tabs.GetSelection() + 1
        if idx >= pc: idx = 0
        self.tabs.SetSelection(idx)
        self.focusActiveView()

    def OnPrevPage(self, event):
        pc = self.tabs.GetPageCount()
        idx = self.tabs.GetSelection() - 1
        if idx < 0: idx = pc - 1
        self.tabs.SetSelection(idx)
        self.focusActiveView()

#---Code Browsing---------------------------------------------------------------
    def addBrowseMarker(self, marker):
        """ Add marker to browse stack associated with the currently open module
            and view
        """
        modulePage = self.getActiveModulePage()
        if modulePage:
            activeView = modulePage.getActiveView()
            self.browser.add(modulePage, activeView.viewName, marker)
            self.updateBrowserBtns()

    def OnBrowseBack(self, event):
        self.browser.back()
        self.updateBrowserBtns()

    def OnBrowseForward(self, event):
        self.browser.forward()
        self.updateBrowserBtns()

#---State methods---------------------------------------------------------------
    def restoreEditorState(self):
        # Open previously opened files
        if Preferences.rememberOpenFiles:
            conf = Utils.createAndReadConfig('Explorer')
            if conf.has_section('editor'):
                try:
                    if conf.has_option('editor', 'openingfiles'):
                        conf.remove_option('editor', 'openingfiles')
                        wx.LogWarning(_('Skipped opening files because Boa '
                                     'possibly crashed last time while opening'))
                        return
                    files = eval(conf.get('editor', 'openfiles'), {})
                    self._blockToolbar = True
                    conf.set('editor', 'openingfiles', '1')
                finally:
                    try:
                        Utils.writeConfig(conf)
                    except Exception, error:
                        wx.LogError(_('Could not update config.'))
                try:
                    cnt = 0
                    for file in files:
                        try:
                            print 'opening in Editor: %s <<%d/%d>>' % (
                                  os.path.basename(file).split('::')[0], cnt,
                                  len(files))

                            self.openOrGotoModule(file)
                            cnt = cnt + 1
                        except (IOError, TransportError), error:
                            wx.LogWarning(str(error))
                        except Exception, error:
                            wx.LogError(str(error))
                            if Preferences.debugMode == 'development':
                                raise
                    try:
                        actPage = conf.getint('editor', 'activepage')
                        if actPage < self.tabs.GetPageCount():
                            self.tabs.SetSelection(actPage)
                    except:
                        pass

                finally:
                    self._blockToolbar = False
                    # during a crash this line wont be reached
                    conf.remove_option('editor', 'openingfiles')
                    try:
                        Utils.writeConfig(conf)
                    except Exception, error:
                        wx.LogError(_('Could not update config.'))

    def persistEditorState(self):
        # Save list of open files to config
        if Preferences.rememberOpenFiles:
            modOrder = []
            for mod, modPage in self.modules.items():
                if modPage.model.savedAs:
                    if modPage.model.views.has_key('Source'):
                        mod = '%s::%d' %(mod,
                              modPage.model.views['Source'].GetCurrentLine()+1)
                    modOrder.append( (modPage.tIdx, mod) )
            modOrder.sort()

            mods = []
            for idx, mod in modOrder:
                mods.append(mod)

            conf = Utils.createAndReadConfig('Explorer')
            if not conf.has_section('editor'): conf.add_section('editor')
            conf.set('editor', 'openfiles', pprint.pformat(mods))
            conf.set('editor', 'activepage', str(self.tabs.GetSelection()))
            try:
                Utils.writeConfig(conf)
            except Exception, error:
                wx.LogError(_('Could not save open file list: ')+str(error))

#---Misc events-----------------------------------------------------------------

    def OnExitBoa(self, event):
        self.palette.Close()

    def OnMenuHighlight(self, event):
        item = self.mainMenu.FindItemById(event.GetMenuId())
        if item:
            self.statusBar.setHint(item.GetHelp())

    def OnHidePalette(self, event):
        self.palette.Show(False)

    def OnCloseWindow(self, event):
        if not self.palette.destroying and not self.palette.IsShown():
            self.palette.Close()
            return

        if self.palette.destroying:
            if not Help.canClosePydocServer():
                if Help.pydocWarning():
                    self.palette.destroying = False
                    return

            if self.debugger:
                if self.debugger.running:
                    wx.LogError(_('Please close the application running in the '
                               'debugger before continuing.'))
                    self.palette.destroying = False
                    return
                else:
                    self.debugger.Close(True)

            if self.erroutFrm and not self.erroutFrm.checkProcessesAtExit():
                self.palette.destroying = False
                return

            self.persistEditorState()
            self.finder.saveOptions()

            modPageList = []
            modPageAppList = []
            for name, modPage in self.modules.items():
                if modPage.model.modelIdentifier in Controllers.appModelIdReg:
                    # move application files to the end of the list because
                    # other files could modify them on being saved
                    modPageAppList.append( (modPage.tIdx, name, modPage) )
                else:
                    modPageList.append( (modPage.tIdx, name, modPage) )
            modPageList.sort()
            modPageAppList.sort()

            for idx, name, modPage in modPageList + modPageAppList:
                try:
                    self.prepareForCloseModule(modPage, True)
                except CancelClose:
                    self.palette.destroying = False
                    return
                except TransportSaveError, error:
                    self.palette.destroying = False
                    wx.LogError(str(error))
                    return

            # stop accepting files over socket
            if self.closed:
                self.closed.set()
                # This caused problems when Boa closes 'too quickly', by sleeping
                # for half the select time-out, seems to work although sleeping for
                # the exactly the time-out would be safest (but starts to be noticeable)
                import time
                time.sleep(0.125)

            self.palette.editor = None
            self.inspector = None
            self.controllers = None
            if self.explorer:
                self.explorer.Hide()
                self.explorer.tree.DeleteAllItems()
                self.explorer.destroy()

            if self.newMenu:
                self.newMenu.Destroy()
            self.blankEditMenu.Destroy()
            self.blankViewMenu.Destroy()

            self.erroutFrm.Destroy()
            self.erroutFrm = None

            if self.shell:
                self.shell.destroy()

            if getattr(sys, 'boa_ide', None) == self:
                del sys.boa_ide

            self._prevMod = None
            self._prevView = None
            self._prevContrl = None

            self.modelImageList = None
            import FileDlg
            FileDlg.wxBoaFileDialog.modImages = None

            self.statusBar.destroy()

            self.Destroy()
            event.Skip()
        else:
            self.Show(False)

#---Window dimensions maintenance-----------------------------------------------
    def OnWinDimsLoad(self, event):
        Utils.callOnFrameRestorers(Utils.FrameRestorerMixin.loadDims)
        self.setStatus(_('Window dimensions loaded'))

    def OnWinDimsSave(self, event):
        Utils.callOnFrameRestorers(Utils.FrameRestorerMixin.saveDims)
        self.setStatus(_('Window dimensions saved'))

    def OnWinDimsRestoreDefs(self, event):
        Utils.callOnFrameRestorers(Utils.FrameRestorerMixin.restoreDefDims)
        self.setStatus(_('Window dimensions restored to defaults'))


if __name__ == '__main__':
    app = wx.PySimpleApp()

    import Palette
    palette = Palette.BoaFrame(None, -1, app)

    editor = palette.editor = EditorFrame(palette, -1, None, None, None, app, palette)
    editor.Show()
    app.MainLoop()
