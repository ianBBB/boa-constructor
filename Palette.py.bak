#----------------------------------------------------------------------
# Name:        Palette.py
# Purpose:     Main frame containing palette for visual frame design
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:BoaFrame

print 'importing Palette'

import os, sys

import wx

import PaletteStore
import Help, Preferences, Utils, Plugins
from Preferences import IS, flatTools
from Utils import _

import wx.lib.buttons

currentMouseOverTip = ''


[wxID_BOAFRAME, wxID_BOAFRAMEPALETTE, wxID_BOAFRAMETOOLBAR, 
] = [wx.NewId() for _init_ctrls in range(3)]

[wxID_BOAFRAMETOOLBARTOOLS0, wxID_BOAFRAMETOOLBARTOOLS1, 
] = [wx.NewId() for _init_coll_toolBar_Tools in range(2)]

class BoaFrame(wx.Frame, Utils.FrameRestorerMixin):

    paletteIcon = 'Images/Icons/Boa.ico'

    def _init_coll_toolBar_Tools(self, parent):
        # generated method, don't edit

        parent.AddTool(bitmap=IS.load('Images/Shared/Inspector.png'),
              id=wxID_BOAFRAMETOOLBARTOOLS0, isToggle=False, longHelpString='',
              pushedBitmap=wx.NullBitmap,
              shortHelpString=_('Brings the Inspector to the front'))
        parent.AddTool(bitmap=IS.load('Images/Shared/Editor.png'),
              id=wxID_BOAFRAMETOOLBARTOOLS1, isToggle=False, longHelpString='',
              pushedBitmap=wx.NullBitmap,
              shortHelpString=_('Brings the Editor to the front'))
        self.Bind(wx.EVT_TOOL, self.OnInspectorToolClick,
              id=wxID_BOAFRAMETOOLBARTOOLS0)
        self.Bind(wx.EVT_TOOL, self.OnEditorToolClick,
              id=wxID_BOAFRAMETOOLBARTOOLS1)

        parent.Realize()

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self,
              #style=wx.SYSTEM_MENU | wx.RESIZE_BORDER | wx.CAPTION | wx.MINIMIZE_BOX,
              id=wxID_BOAFRAME, name='', parent=prnt, pos=wx.Point(116, 275),
              size=wx.Size(645, 74),
              style=wx.DEFAULT_FRAME_STYLE& ~wx.MAXIMIZE_BOX,
              title=self.frameTitle)
        self.SetClientSize(wx.Size(637, 47))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_ICONIZE, self.OnBoaframeIconize)

        self.toolBar = wx.ToolBar(id=wxID_BOAFRAMETOOLBAR, name='toolBar',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(637, 24),
              style=wx.TB_HORIZONTAL | wx.NO_BORDER | Preferences.flatTools)
        self.SetToolBar(self.toolBar)

        self.palette = wx.Notebook(id=wxID_BOAFRAMEPALETTE, name='palette',
              parent=self, pos=wx.Point(0, 24), size=wx.Size(637, 23), style=0)

        self._init_coll_toolBar_Tools(self.toolBar)

    def __init__(self, parent, id, app):
        self.frameTitle = 'Boa Constructor - Python IDE & wxPython GUI Builder'
        self.frameTitle = Preferences.paletteTitle

        self._init_ctrls(parent)

        self.winConfOption = 'palette'
        self.loadDims()

        self.paletteStyle = Preferences.paletteStyle
        if self.paletteStyle == 'menu':
            self.menuBar = wx.MenuBar()
            self.SetMenuBar(self.menuBar)
            self.palette.Show(False)

        self.app = app
        self.destroying = False

        self.widgetSet = {}
        self.SetIcon(IS.load(self.paletteIcon))

        self.browser = None

        self.toolBar.AddSeparator()

        self.componentSB = ComponentSelection(self)

        if Preferences.showFrameTestButton:
            self.toolBar.AddSeparator()
            self.addTool('Images/Shared/CustomHelp', 'Test', 'Test', self.OnTest)

        # Add main helpbuttons defined in the config file
        conf = Utils.createAndReadConfig('Explorer')
        self.paletteHelpItems = eval(conf.get('help', 'palettehelp'), {})

        self.toolBar.AddSeparator()
        self.addTool('Images/Shared/Help', _('Boa or selected component help'),
              _('Show help'), self.OnHelpToolClick)
        self.addTool('Images/Shared/wxWinHelp', _('wxPython help'),
              _('Show help'), self.OnWxWinHelpToolClick)
        self.addTool('Images/Shared/PythonHelp', _('Python help'),
              _('Show help'), self.OnPythonHelpToolClick)

        # Add additional helpbuttons if defined in the config file
        customHelpItems = eval(conf.get('help', 'customhelp'), {})
        self.customHelpItems = {}
        for caption, helpFile in customHelpItems.items():
            mID = wx.NewId()
            self.toolBar.AddTool(mID, IS.load('Images/Shared/CustomHelp.png'),
              shortHelpString = caption)
            self.Bind(wx.EVT_TOOL, self.OnCustomHelpToolClick, id=mID)
            self.customHelpItems[mID] = (caption, helpFile)

        if wx.Platform == '__WXGTK__':
            self.toolBar.AddSeparator()
            self.addTool('Images/Shared/CloseWindow', 'Exit', '', self.OnCloseClick)
        self.toolBar.Realize()

        self.palettePages = []

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

    def initPalette(self, inspector, editor):
        self.inspector = inspector
        self.editor = editor

        if Preferences.paletteStyle == 'menu':
            mb = self.menuBar
        else:
            mb = None

        # XXX Set these from class
        if not hasattr(sys, 'cyclops'):
            # 'New' page
            palettePage = NewPalettePage(self.palette, PaletteStore.newPalette[0],
                  'Images/Palette/', self, self.widgetSet, self)

            for modelName in PaletteStore.paletteLists['New']:
                palettePage.addButton2(modelName,
                    PaletteStore.newControllers[modelName],
                    wx.lib.buttons.GenBitmapButton)
            if mb: mb.Append(menu=palettePage.menu, title=PaletteStore.newPalette[0])
            self.palettePages.append(palettePage)

            # Normal control pages
            for palette in PaletteStore.palette:
                palettePage = PalettePage(self.palette, palette[0],
                      'Images/Palette/', self, self.widgetSet,
                      self.componentSB, self)
                palettePage.addToggleBitmaps(palette[2], None, None)
                self.palettePages.append(palettePage)
                if mb: mb.Append(menu=palettePage.menu, title=palette[0])

            # Dialog page
##            if PaletteStore.dialogPalette[2]:
##                self.dialogPalettePage = PanelPalettePage(self.palette,
##                      PaletteStore.dialogPalette[0],
##                      'Images/Palette/', self, self.widgetSet,
##                      self.componentSB, self)
##                for dialog in PaletteStore.dialogPalette[2]:
##                    self.dialogPalettePage.addButton(
##                          PaletteStore.compInfo[dialog][0],
##                          dialog, PaletteStore.compInfo[dialog][1],
##                          self.OnDialogPaletteClick, None, None,
##                          wx.lib.buttons.GenBitmapButton)
##                self.palettePages.append(self.dialogPalettePage)
##                if mb: mb.Append(menu=self.dialogPalettePage.menu, 
##                                 title=PaletteStore.dialogPalette[0])

            # Zope page
            if Plugins.transportInstalled('ZopeLib.ZopeExplorer'):
                self.zopePalettePage = ZopePalettePage(self.palette,
                      PaletteStore.zopePalette[0], 'Images/Palette/',
                      self, self.widgetSet, self.componentSB, self)
                self.zopePalettePage.addToggleBitmaps(
                      PaletteStore.zopePalette[2], None, None)
                self.palettePages.append(self.zopePalettePage)
                if mb: mb.Append(menu=self.zopePalettePage.menu, 
                                 title=PaletteStore.zopePalette[0])
        else:
            palettePage = None

    def setDefaultDimensions(self):
        self.SetDimensions(Preferences.screenX, Preferences.screenY + Preferences.topMenuHeight,
            Preferences.screenWidth - Preferences.windowManagerSide * 2,
            Preferences.paletteHeight)

    def addTool(self, filename, text, help, func, toggle = False):
        mID = wx.NewId()
        self.toolBar.AddTool(mID, IS.load(filename+'.png'),
          shortHelpString = text, isToggle = toggle)
        self.Bind(wx.EVT_TOOL, func, id=mID)
        return mID

    def OnInspectorToolClick(self, event):
        self.inspector.restore()

    def OnEditorToolClick(self, event):
        self.editor.restore()

    def OnHelpToolClick(self, event):
        if self.componentSB.selection:
            Help.showCtrlHelp(self.componentSB.selection[1].__name__)
        else:
            Help.showMainHelp(self.paletteHelpItems['boa'])

    def OnWxWinHelpToolClick(self, event):
        Help.showMainHelp(self.paletteHelpItems['wx'])

    def OnPythonHelpToolClick(self, event):
        Help.showMainHelp(self.paletteHelpItems['python'])

    def OnCustomHelpToolClick(self, event):
        caption, helpFile = self.customHelpItems[event.GetId()]
        Help.showHelp(helpFile)

    def OnFileExit(self, event):
        self.Close()

    def OnDialogPaletteClick(self, event):
        cls, cmp = self.dialogPalettePage.widgets[event.GetId()][1:]
        self.editor.addNewDialog(cls, cmp)

    def OnZopePaletteClick(self, event):
        cls, cmp = self.zopePalettePage.widgets[event.GetId()][1:]

    def OnComposeClick(self, event):
        pass
    def OnInheritClick(self, event):
        pass

    def OnCloseClick(self, event):
        self.Close()

    def OnCloseWindow(self, event):
        self.destroying = True
        try:
            if hasattr(self, 'editor') and self.editor:
                self.editor.destroying = True
                self.editor.Close()
                if not self.destroying:
                    return

            if hasattr(self, 'inspector'):
                self.inspector.destroying = True
                self.inspector.Close()

                if hasattr(self, 'app'):
                    self.app = None

            Help.delHelp()

            self.palette.Hide()
            for page in self.palettePages:
                page.destroy()

        finally:
            if not self.destroying:
                self.editor.destroying = False
                self.inspector.destroying = False
            else:
                self.Destroy()
                event.Skip()

                app =wx.GetApp()
                if hasattr(app, 'tbicon'):
                    app.tbicon.Destroy()


    def OnUncheckComponent(self, event):
        self.componentSB.selectNone()

    def OnTest(self, event):
        import Tests
        Tests.test_wxFrame(self)

    def OnCreateNew(self, name, controller):
        self.editor.addNewPage(name, controller)

    def Iconize(self, iconize):
        if Help._hc:
            frm = Help._hc.GetFrame()
            if frm: frm.Iconize(iconize)
        wx.Frame.Iconize(self, iconize)

    def OnBoaframeIconize(self, event):
        self.SetFocus()
        if Help._hc:
            frm = Help._hc.GetFrame()
            if frm: frm.Iconize(True)
        event.Skip()

class ComponentSelection:
    """ Controls the selection of the palette and access to associated
        palette mapping structures. Accessed by the Designer """
    def __init__(self, palette):
        wID = wx.NewId()
        self.selComp = wx.CheckBox(palette.toolBar, wID, '  '+_('(Nothing selected)'),
              size =wx.Size(180, 20))
        self.selComp.Enable(False)
        self.selComp.Bind(wx.EVT_CHECKBOX, palette.OnUncheckComponent, id=wID)
        palette.toolBar.AddControl(self.selComp)

##        cId = palette.addTool('Images/Shared/Compose', 'Compose', ' ',
##              palette.OnComposeClick, toggle = True)
##        iId = palette.addTool('Images/Shared/Inherit', 'Inherit', ' ',
##              palette.OnInheritClick, toggle = True)
##        palette.toolBar.ToggleTool(cId, True)
##        palette.toolBar.EnableTool(cId, False)
##        palette.toolBar.EnableTool(iId, False)

        self.selection = None
        self.prevPage = None

    def selectComponent(self, page, detail):
        if self.prevPage: self.prevPage.selectNone()
        self.selection = detail
        self.prevPage = page
        self.selComp.Enable(True)
        self.selComp.SetLabel('  '+detail[0])
        self.selComp.SetValue(True)

    def selectNone(self):
        if self.prevPage: self.prevPage.selectNone()
        self.selection = None
        self.selComp.Enable(False)
        self.selComp.SetLabel('  '+_('(Nothing selected)'))
        self.selComp.SetValue(False)

class BasePalettePage:
    pass
class ListCtrlPalettePage(wx.ListCtrl, BasePalettePage):
    pass
class CompositeListCtrlPalPage(ListCtrlPalettePage):
    pass
class TemplateListCtrlPalPage(ListCtrlPalettePage):
    pass

class PanelPalettePage(wx.Panel, BasePalettePage):
    buttonSep = 11
    buttonBorder = 7
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, components, palette):
        # default size provided for better sizing on GTK where notebook page
        # size isn't available at button creation time
        wx.Panel.__init__(self, parent, -1, size=(44, 44))

        self.palette = palette
        self.components = components
        self.name = name
        self.bitmapPath = bitmapPath
        self.widgets = widgets
        self.buttons = {}
        parent.AddPage(self, name)
        self.posX = int(round(self.buttonSep/2.0))
        self.posY = int(round((self.GetSize().y -(24+self.buttonBorder))/2.0))
        self.eventOwner = eventOwner
        self.menu =wx.Menu()
        self.menusCheckable = False

    def destroy(self):
        if hasattr(self, 'widgets'):
            del self.widgets
            self.DestroyChildren()
            for btn in self.buttons.values():
                btn.faceDnClr = None
                btn.shadowPen = None
                btn.highlightPen = None
                btn.focusIndPen = None
                btn.bmpLabel = None
            if self.palette.paletteStyle == 'tabs':
                self.menu.Destroy()

    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, 
                  hintLeaveFunc, btnType):
        mID = wx.NewId()

        self.menu.Append(mID, widgetName, '', self.menusCheckable)
        self.palette.Bind(wx.EVT_MENU, clickEvt, id=mID)

        self.widgets[mID] = (widgetName, wxClass, constrClass)

        if self.palette.paletteStyle == 'menu':
            return mID

        bmp = self.getButtonBmp(widgetName, wxClass)
        width = bmp.GetWidth() + self.buttonBorder
        height = bmp.GetHeight() + self.buttonBorder

        newButton = btnType(self, mID, None, wx.Point(self.posX, self.posY),
                           wx.Size(width, height))

        newButton.SetBezelWidth(1)
        newButton.SetUseFocusIndicator(0)
        newButton.SetToolTipString(widgetName)
        try:
            newButton.SetBitmapLabel(bmp, False)
        except TypeError:
            newButton.SetBitmapLabel(bmp)

        self.Bind(wx.EVT_BUTTON, clickEvt, id=mID)

        self.buttons[widgetName] = newButton
        self.posX = self.posX + bmp.GetWidth() + 11

        return mID

    def getButtonBmp(self, name, wxClass):
        return PaletteStore.bitmapForComponent(wxClass)

class NewPalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, palette):
        PanelPalettePage.__init__(self, parent, name, bitmapPath, eventOwner, 
                                  widgets, palette, palette)
        self.selection = None

    def destroy(self):
        PanelPalettePage.destroy(self)

    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, 
                  hintLeaveFunc, btnType):
        mID = PanelPalettePage.addButton(self, widgetName, wxClass, constrClass, 
              clickEvt, hintFunc, hintLeaveFunc, btnType)
        return mID

    def addButton2(self, name, Controller, btnType):
        mID = PanelPalettePage.addButton(self, name, Controller, None, 
              self.OnClickTrap, None, None, btnType)
        self.palette.editor.Bind(wx.EVT_MENU, self.OnClickTrap, id=mID)

        return mID

    def getButtonBmp(self, name, wxClass):
        try:
            return IS.load('%s%s.png' %(self.bitmapPath, name))
        except IS.Error:
            return IS.load('Images/Palette/Component.png')

    def OnClickTrap(self, event):
        modPageInfo = self.widgets[event.GetId()]
        wx.CallAfter(self.palette.OnCreateNew, name=modPageInfo[0], 
              controller=modPageInfo[1])

class PalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, 
                 components, palette):
        PanelPalettePage.__init__(self, parent, name, bitmapPath, eventOwner, 
              widgets, components, palette)
        self.clickEvt = None
        self.selection = None
        self.menusCheckable = True

    def addToggleBitmaps(self, classes, hintFunc, hintLeaveFunc):
        for wxClass in classes:
            ci = PaletteStore.compInfo[wxClass]
            self.addButton(ci[0], wxClass, ci[1], self.OnClickTrap, hintFunc, 
                  hintLeaveFunc, wx.lib.buttons.GenBitmapToggleButton)

    def OnClickTrap(self, event):
        wId = event.GetId()
        if self.palette.paletteStyle == 'tabs':
            obj = event.GetButtonObj()
            if obj.up:
                self.selectNone()
                self.components.selectNone()
            else:
                self.components.selectComponent(self, self.widgets[wId])
                self.selection = obj
        elif self.palette.paletteStyle == 'menu':
            sel = self.menu.FindItemById(wId)
            if not sel.IsChecked():
                self.selectNone()
                self.components.selectNone()
            else:
                self.components.selectComponent(self, self.widgets[wId])
                sel.Check(True)
                self.selection = sel
            event.Skip()

    def selectNone(self):
        if self.selection:
            if self.palette.paletteStyle == 'tabs':
                self.selection.SetToggle(False)
                self.selection.Refresh()
                self.selection = None
            elif self.palette.paletteStyle == 'menu':
                self.selection.Check(False)
                self.selection = None


class ZopePalettePage(PalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets,
          components, palette):
        PalettePage.__init__(self, parent, name, bitmapPath, eventOwner,
              widgets, components, palette)

    def getButtonBmp(self, name, wxClass):
        return IS.load('%s%s.png' %(self.bitmapPath, name))


if __name__ == '__main__':
    app = wx.PySimpleApp()
    palette = BoaFrame(None, -1, app)
    palette.Show()
    palette.palette.AddPage(wx.Panel(palette.palette, -1), 'test')
    

    app.MainLoop()
