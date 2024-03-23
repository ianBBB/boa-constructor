#----------------------------------------------------------------------
# Name:        ClassBrowser.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:ClassBrowserFrame

import os, pyclbr, sys

import wx

import Preferences, Utils, Plugins
from Preferences import IS
from Utils import _

[wxID_CLASSBROWSERFRAME, wxID_CLASSBROWSERFRAMEHIERARCHY, 
 wxID_CLASSBROWSERFRAMEPAGES, wxID_CLASSBROWSERFRAMESTATUSBAR, 
 wxID_CLASSBROWSERFRAMETREE, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(5)]

class ClassBrowserFrame(wx.Frame, Utils.FrameRestorerMixin):
    def _init_coll_pages_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.hierarchy, select=True,
              text=_('Hierarchy'))
        parent.AddPage(imageId=-1, page=self.tree, select=False, text=_('Modules'))

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_CLASSBROWSERFRAME, name='', parent=prnt,
              pos=wx.Point(475, 238), size=wx.Size(299, 497),
              style=wx.DEFAULT_FRAME_STYLE | Preferences.childFrameStyle,
              title=_('wxPython Class Browser'))
        self.SetClientSize(wx.Size(291, 470))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.statusBar = wx.StatusBar(id=wxID_CLASSBROWSERFRAMESTATUSBAR,
              name='statusBar', parent=self, style=wx.STB_SIZEGRIP)
        self.SetStatusBar(self.statusBar)

        self.pages = wx.Notebook(id=wxID_CLASSBROWSERFRAMEPAGES, name='pages',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(291, 450), style=0)

        self.hierarchy = wx.TreeCtrl(id=wxID_CLASSBROWSERFRAMEHIERARCHY,
              name='hierarchy', parent=self.pages, pos=wx.Point(0, 0),
              size=wx.Size(283, 424), style=wx.TR_HAS_BUTTONS)

        self.tree = wx.TreeCtrl(id=wxID_CLASSBROWSERFRAMETREE, name='tree',
              parent=self.pages, pos=wx.Point(0, 0), size=wx.Size(283, 424),
              style=wx.TR_HAS_BUTTONS)

        self._init_coll_pages_Pages(self.pages)

    def __init__(self, parent):
        self._init_ctrls(parent)

        self.winConfOption = 'classbrowser'
        self.loadDims()

        self.SetIcon(IS.load('Images/Icons/ClassBrowser.ico'))

        self.classes = {}

        # for module in ('wx', 'wx.html', 'wx.lib.calendar', 'wx.grid', 'wx.stc',
        #                'wx.gizmos', 'wx.adv.Wizard'):
        #     self.classes.update(pyclbr.readmodule(module))
#DRAMA Have to remove 'wx.adv.Wizard' from this code because it generates this error;
# 'ImportError: No package named wx.adv'

        for module in ('wx', 'wx.html', 'wx.lib.calendar', 'wx.grid', 'wx.stc',
                       'wx.gizmos'):
            self.classes.update(pyclbr.readmodule(module))


        tID =wx.NewIdRef(count=1)
        root = self.hierarchy.AddRoot('wx.Object')

        clsDict = {}

        for i in self.classes.keys():
            travTilBase(i, self.classes, clsDict)

        buildTree(self.hierarchy, root, clsDict)
        self.hierarchy.Expand(root)

        tID =wx.NewIdRef(count=1)

        root = self.tree.AddRoot(_('Modules'))
        modules = {}
        moduleName = ''
        for className in self.classes.keys():
            moduleName = os.path.basename(self.classes[className].file)
            if not moduleName in modules:
                modules[moduleName] = {}
            modules[moduleName][className] = {}
            modules[moduleName][className]['Properties'] = {}
            modules[moduleName][className]['Methods'] = {}
            modules[moduleName][className]['Built-in'] = {}
            for method in self.classes[className].methods.keys():
                if (method[:2] == '__'):
                    modules[moduleName][className]['Built-in'][method] = self.classes[className].lineno
                elif (method[:3] == 'Get'):
                    if 'Set'+method[3:] in self.classes[className].methods:
                        modules[moduleName][className]['Properties'][method[3:]] = self.classes[className].lineno
                    else:
                        modules[moduleName][className]['Methods'][method] = self.classes[className].lineno
                elif (method[:3] == 'Set'):
                    if 'Get'+method[3:] in self.classes[className].methods:
                        modules[moduleName][className]['Properties'][method[3:]] = self.classes[className].lineno
                    else:
                        modules[moduleName][className]['Methods'][method] = self.classes[className].lineno
                else:
                    modules[moduleName][className]['Methods'][method] = self.classes[className].lineno
        moduleLst = sorted(list(modules.keys()))
        for module in moduleLst:
            roots = self.tree.AppendItem(root, module)
            classLst = sorted(list(modules[module].keys()))
            for classes in classLst:
                aClass = self.tree.AppendItem(roots, classes)
                methItem = self.tree.AppendItem(aClass, _('Methods'))
                for methods in modules[module][classes]['Methods'].keys():
                    methodsItem = self.tree.AppendItem(methItem, methods)
                propItem = self.tree.AppendItem(aClass, _('Properties'))
                for properties in modules[module][classes]['Properties'].keys():
                    propertyItem = self.tree.AppendItem(propItem, properties)
                bInItem = self.tree.AppendItem(aClass, _('Built-in'))
                for builtIns in modules[module][classes]['Built-in'].keys():
                    builtInItem = self.tree.AppendItem(bInItem, builtIns)
                suprItem = self.tree.AppendItem(aClass, _('Super'))
                for supers in self.classes[classes].super:
                    try:
                        superItem = self.tree.AppendItem(suprItem, supers.name)
                    except AttributeError:
                        superItem = self.tree.AppendItem(suprItem, supers)

        self.tree.Expand(root)

    def setDefaultDimensions(self):
        self.SetSize(0, Preferences.underPalette,
          Preferences.inspWidth,
          Preferences.bottomHeight)

    def OnCloseWindow(self, event):
        self.Show(True)
        self.Show(False)
        if __name__ == '__main__':
            self.Destroy()


def findInsertModules(name, tree):
    ri = tree.GetRootItem()
    item = ri
    found = False
    while item:
        item = tree.GetNextSibling(item)
        if tree.GetItemText(item) == name:
            found = True
            return item

    return tree.AddRoot(name)

def travTilBase(name, classes, root):
    if not name in classes:
        if not name in root:
            root[name] = {}
        return root[name]
    elif len(classes[name].super) == 0:
        if not name in root:
            root[name] = {}
        return root[name]
    else:
        super1 = classes[name].super[0]
        if type(super1) != type(''):
            super1 = super1.name
        c = travTilBase(super1, classes, root)
        if not name in c:
            c[name] = {}
        return c[name]

def buildTree(tree, parent, dict):
    items = sorted(list(dict.keys()))

    for item in items:
        child = tree.AppendItem(parent, item)
        if len(dict[item].keys()):
            buildTree(tree, child, dict[item])

#-------------------------------------------------------------------------------

def openClassBrowser(editor):
    palette = editor.palette
    if not palette.browser:

        wx.BeginBusyCursor()
        try:
            palette.browser = ClassBrowserFrame(palette)
        finally:
            wx.EndBusyCursor()
    palette.browser.restore()


# pyclbr doesn't work without source
if not hasattr(sys, 'frozen'):
    Plugins.registerTool(_('wxPython class browser'), openClassBrowser,
                         'Images/Shared/ClassBrowser.png')

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.App()
    frame = ClassBrowserFrame(None)
    frame.Show(True)
    app.MainLoop()
