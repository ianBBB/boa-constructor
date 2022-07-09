import string, os, sys

import wx
from wx.lib.anchors import LayoutAnchors

import Preferences, Utils, Plugins
from Utils import _

from Explorers import ExplorerNodes, FileExplorer
from Models import EditorModels, EditorHelper, Controllers
from Views import EditorViews

# Register plug-in preference
Plugins.registerPreference('wxPythonDemo', 'wpWxPythonDemoFolder', "''", 
                           ['Path to the wxPython demo folder.', 
                            'If empty, wxPython/demo is used.'], 'type: dirpath')
Plugins.registerPreference('wxPythonDemo', 'wpShowWxPythonDemoTemplate', 'False', 
                           ['Should a template for an empty wxPython demo file', 
                            'be available on the Palette.'])


if Preferences.wpWxPythonDemoFolder:
    demoDir = Preferences.wpWxPythonDemoFolder
else:
    demoDir = os.path.join(os.path.dirname(wx.__file__), 'demo')

if not os.path.exists(demoDir):
    raise Plugins.SkipPlugin(_('wxPython demo directory not found.\n'
          'Please define the path under Preferences->Plug-ins'))

true = 1
false = 0

def importFromWxPyDemo(name):
    cwd = os.getcwd()
    sys.path.insert(0, demoDir)
    try:
        os.chdir(demoDir)
        try:
            return __import__(name, globals())
        finally:
            os.chdir(cwd)
            del sys.path[0]
    except Exception, err:
        print str(err)
        return None
        

def getWxPyDemoTree():
    Main = importFromWxPyDemo('Main')
    if Main:
        return Main._treeList
    else:
        return []


EditorHelper.imgWxPythonDemo = EditorHelper.addPluginImgs('Images/wxPythonDemo.png')


class SkipViewSignal(Exception):
    """ Raised when the demo is not docked """

class wxPythonDemoView(wx.Panel, EditorViews.EditorView, EditorViews.CloseableViewMix):
    viewName = tabName = 'Demo'
    viewTitle = _('Demo')
    
    def __init__(self, parent, model):
        wx.Panel.__init__(self, parent, -1)
        EditorViews.CloseableViewMix.__init__(self)
        EditorViews.EditorView.__init__(self, model, actions=self.closingActionItems)
        
        self.demoCtrl = None
        self.updateDemoCtrl()
        
        if self.demoCtrl is None:
            raise SkipViewSignal
        
    def updateDemoCtrl(self):
        demoModule = self.model.demoModule
        if demoModule:
            if self.demoCtrl:
                self.demoCtrl.Destroy()
    
            cwd = os.getcwd()
            os.chdir(demoDir)
            try:
                self.demoCtrl = demoModule.runTest(self.model.editor, self, self)
            finally:
                os.chdir(cwd)
                
            if self.demoCtrl:
                self.demoCtrl.SetSize(self.GetClientSize())
                self.SetAutoLayout(True)
                self.demoCtrl.SetConstraints(LayoutAnchors(self.demoCtrl, 
                                             True, True, True, True))
    
    def refreshCtrl(self):
        pass
    
    def WriteText(self, text):
        """ When View used as demo log """
        if not self.model: return
        
        ef = self.model.editor.erroutFrm
        ef.appendToOutput(text)
        ef.display()

    def write(self, text):
        """ When View used as demo log """
        self.WriteText(text)

class wxPythonDemoOverView(EditorViews.HTMLView, EditorViews.CloseableViewMix):
    viewName = tabName = 'Overview'
    viewTitle = _('Overview')

    def __init__(self, parent, model):
        EditorViews.CloseableViewMix.__init__(self)
        EditorViews.HTMLView.__init__(self, parent, model, actions=self.closingActionItems)
        
        self.refreshCtrl()
    
    def generatePage(self):
        if self.model.demoModule:
            return self.model.demoModule.overview
        else:
            return _('No module imported')


class wxPythonDemoNode(FileExplorer.FileSysNode):
    def open(self, editor):
        model, cntrl = editor.openOrGotoModule(self.resourcepath)
 
        if not hasattr(model, 'demoModule'):
            name = os.path.splitext(os.path.basename(model.filename))[0]
            model.demoModule = importFromWxPyDemo(name)
       
        if model.demoModule and (model, cntrl) != (None, None): 
            for View, focus in ((wxPythonDemoOverView, False), 
                                (wxPythonDemoView, True)):
                if model.views.has_key(View.viewName):
                    view = model.views[View.viewName]
                    view.updateDemoCtrl()
                else:
                    modPge = editor.getActiveModulePage()
                    try:
                        view = modPge.addView(View)
                    except SkipViewSignal:
                        view = None
                        
                if focus and view:
                    view.focus()

        return model, cntrl
    
class wxPythonDemoSectionNode(ExplorerNodes.ExplorerNode):
    protocol = 'wxpydemo.section'
    def __init__(self, name, items, clipboard, bookmarks):
        ExplorerNodes.ExplorerNode.__init__(self, name, '', clipboard, 
              EditorHelper.imgFolder)
        self.bookmarks = bookmarks
        self.vetoSort = true
        self.items = items

    def isFolderish(self):
        return true

    def createChildNode(self, name):
        mod = importFromWxPyDemo(name)
        if mod is None:
            return None
        else:
            demoFile = os.path.splitext(mod.__file__)[0]+'.py'
            imgIdx = Controllers.identifyFile(demoFile)[0].imgIdx
            return wxPythonDemoNode(name, demoFile, self.clipboard, imgIdx, 
                                    self, self.bookmarks)

    def openList(self):
        return [n for n in [self.createChildNode(name) for name in self.items] if n]
    

class wxPythonDemoDirNode(ExplorerNodes.ExplorerNode):
    protocol = 'wxpydemo'
    def __init__(self, clipboard, parent, bookmarks):
        ExplorerNodes.ExplorerNode.__init__(self, _('wxPython demo'), '', 
              clipboard, EditorHelper.imgWxPythonDemo)
        self.bookmarks = bookmarks
        self.bold = true
        self.vetoSort = true
        self.treeList = getWxPyDemoTree()
        
    def isFolderish(self):
        return true

    def createChildNode(self, section, items):
        return wxPythonDemoSectionNode(section, items, self.clipboard,
              self.bookmarks)

    def openList(self):
        return [self.createChildNode(name, items) 
                for name, items in self.treeList]


#-------------------------------------------------------------------------------
ExplorerNodes.register(wxPythonDemoDirNode, root=True)

#-------------------------------------------------------------------------------

import PaletteStore
from Models import PythonEditorModels, PythonControllers

class wxPythonDemoModuleModel(PythonEditorModels.ModuleModel):
    modelIdentifier = 'wxPythonDemoModule'
    defaultName = 'wxpythondemomodule'
    
    def getDefaultData(self):
        return '''import wx
    
#-------------------------------------------------------------------------------

# Define your demo class here and save this module in the wxPython demo folder

#-------------------------------------------------------------------------------

def runTest(frame, nb, log):
    win = wx.Panel(nb, -1) # Replace with your demo class 
    return win

#-------------------------------------------------------------------------------

overview = """<html><body>
<h2>Demo Name</h2>
<p>
</body></html>
"""
  
if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])])
'''

class wxPythonDemoModuleController(PythonControllers.ModuleController):
    Model = wxPythonDemoModuleModel

#-------------------------------------------------------------------------------

if Preferences.wpShowWxPythonDemoTemplate:
    Plugins.registerFileType(wxPythonDemoModuleController)

#-------------------------------------------------------------------------------

def getwxPythonDemoData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00\x97IDATx\x9c\xc5\x93\xdd\r\xc20\x0c\x84\xbf\xa2\x0e\xc2\x08\x8cp\
\x9b0J\x9c\x8d\x18\xc1l\xc0\x08\xdd$<$\xa4\x91h\xf8i\x8b\xb8\x97\x9c\xad\xf3\
I\xce%\x83 \x89\x0c\x07d\xc6\xa7pwF\x01\xa1i\x86\x10:\xf2e\x1c\xbeR\xff\xc2`\
t\t$ \xefD\x8co\x87\xcc\x1c\x10\xe0`f\xe9\x81\x96\xbf\x02X\x82|n_a\xcd\x90\
\xe4H%\xc6u\x06\xaaq\xff?\xc6\xfd/1\xc6aQh\x17\xe0T\xf8\xd1\xfa\x06\xbd\xaf`\
\x13p.\xc5u\xee\xef\xf0\x94\xddk\xd1\xf2\'\xdcf\xea\x93W\xfd\x1d\xbf|\\\xe5\
\xbf>Ca\x00\x00\x00\x00IEND\xaeB`\x82' 

def getwxPythonDemoModuleData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\
\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\xcaIDATx\x9c\xed\x95\xcd\r\xc20\x0cF_\x11\x03\xf8\xc8\x00\xdc1\x13\xe0\
\x8e\xc4\x06\xdd\xa03t\x036\x08\xdc9d\x84\x1c9\xb2A\xb8\xf0\xd3\x96V\xa9h%\
\x04\xea\x93"EN\xec/\x92\xbf$\x99@T\x9ax@\xcd\x18\x8b\xf7\x1e\x0cbl\r\x838\
\x05f\x16\x17\xa3\x8f\x99`\x16H\x92\x89HTm\xfa\xc8{O;6\x84\x10\x02!\x08 \x8f\
J`f\x9d\xdd\xff\x84\xa2("\xb8\x9a!\xff\xc1E\xcb\xe9KV\xc0\xe9>\x0f\xd3\x0b\
\x94\xe5\xe6i\x90\xfd\xfe0\xbd\x80\xaab\xf7wLD\xfe\xe0\xa2\xcd\x02Iz]\x94\
\xe7Y2\xf9x\x06\xd6\xb5\xc0\x05\xdc\xce\r\x13p\xaeo\xe5E\xb6\x05\xcaZ\xa0z\
\xdf\xf3\xfb=\xf8\xe6\x87sM&w5YW\x8a\x88<\xeb\xdc\x00I\xef\xca-\xb2\x8f\xf3\
\xee\x00\x00\x00\x00IEND\xaeB`\x82' 

Preferences.IS.registerImage('Images/wxPythonDemo.png', getwxPythonDemoData())
Preferences.IS.registerImage('Images/Palette/wxPythonDemoModule.png', getwxPythonDemoModuleData())
