#-----------------------------------------------------------------------------
# Name:        FileDlg.py
# Purpose:     Dialog that emulates the standard file dialog, but can browse
#              any explorer supported protocol.
#
# Author:      Riaan Booysen
#
# Created:     2000/09/17
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:wxBoaFileDialog

from os import path
import os

from wxPython.wx import *
from wxPython.html import *
from wxPython.lib.anchors import LayoutAnchors

import Preferences
import Utils
from Utils import wxUrlClickHtmlWindow, EVT_HTML_URL_CLICK

openStr = 'Open'
saveStr = 'Save'

htmlPath = '''<body bgcolor="#%x%x%x"><font size=-1><a href="ROOT">top</a> | <a href="UP">up</a> | <a href="NEWFOLDER">new
folder</a> ||&nbsp;<a href="PROTROOT">%s</a><b>://</b>%s</font></body>'''
htmlLnk = '''<a href="%s">%s</a>'''
htmlCurrItem = '''<b><font color="#0000BB">%s</font></b>'''

[wxID_WXBOAFILEDIALOG, wxID_WXBOAFILEDIALOGBTCANCEL, wxID_WXBOAFILEDIALOGBTOK, wxID_WXBOAFILEDIALOGCHTYPES, wxID_WXBOAFILEDIALOGHTMLWINDOW1, wxID_WXBOAFILEDIALOGPANEL1, wxID_WXBOAFILEDIALOGSTATICTEXT1, wxID_WXBOAFILEDIALOGSTATICTEXT2, wxID_WXBOAFILEDIALOGTCFILENAME] = map(lambda _init_ctrls: wxNewId(), range(9))

class wxBoaFileDialog(wxDialog):
    currentDir = '.'
    _custom_classes = {'wxHtmlWindow': ['wxUrlClickHtmlWindow']}
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_WXBOAFILEDIALOG, name = 'wxBoaFileDialog', parent = prnt, pos = wxPoint(369, 279), size = wxSize(408, 283), style = wxRESIZE_BORDER | wxDEFAULT_DIALOG_STYLE, title = 'File Dialog')
        self._init_utils()
        self.SetAutoLayout(true)

        self.panel1 = wxPanel(id = wxID_WXBOAFILEDIALOGPANEL1, name = 'panel1', parent = self, pos = wxPoint(0, 0), size = wxSize(400, 256), style = wxTAB_TRAVERSAL)
        self.panel1.SetConstraints(LayoutAnchors(self.panel1, true, true, true, true))
        self.panel1.SetAutoLayout(true)

        self.staticText1 = wxStaticText(id = wxID_WXBOAFILEDIALOGSTATICTEXT1, label = 'File name:', name = 'staticText1', parent = self.panel1, pos = wxPoint(8, 192), size = wxSize(70, 16), style = 0)
        self.staticText1.SetConstraints(LayoutAnchors(self.staticText1, true, false, false, true))

        self.staticText2 = wxStaticText(id = wxID_WXBOAFILEDIALOGSTATICTEXT2, label = 'Files of type:', name = 'staticText2', parent = self.panel1, pos = wxPoint(8, 224), size = wxSize(70, 16), style = 0)
        self.staticText2.SetConstraints(LayoutAnchors(self.staticText2, true, false, false, true))

        self.tcFilename = wxTextCtrl(id = wxID_WXBOAFILEDIALOGTCFILENAME, name = 'tcFilename', parent = self.panel1, pos = wxPoint(90, 184), size = wxSize(214, 24), style = 0, value = '')
        self.tcFilename.SetConstraints(LayoutAnchors(self.tcFilename, true, false, true, true))
        EVT_TEXT_ENTER(self.tcFilename, wxID_WXBOAFILEDIALOGTCFILENAME, self.OnTcfilenameTextEnter)

        self.chTypes = wxChoice(choices = self.filterOpts, id = wxID_WXBOAFILEDIALOGCHTYPES, name = 'chTypes', parent = self.panel1, pos = wxPoint(90, 216), size = wxSize(214, 21), style = 0, validator = wxDefaultValidator)
        self.chTypes.SetConstraints(LayoutAnchors(self.chTypes, true, false, true, true))
        EVT_CHOICE(self.chTypes, wxID_WXBOAFILEDIALOGCHTYPES, self.OnChtypesChoice)

        self.btOK = wxButton(id = wxID_WXBOAFILEDIALOGBTOK, label = 'OK', name = 'btOK', parent = self.panel1, pos = wxPoint(320, 184), size = wxSize(72, 24), style = 0)
        self.btOK.SetConstraints(LayoutAnchors(self.btOK, false, false, true, true))
        EVT_BUTTON(self.btOK, wxID_WXBOAFILEDIALOGBTOK, self.OnBtokButton)

        self.btCancel = wxButton(id = wxID_WXBOAFILEDIALOGBTCANCEL, label = 'Cancel', name = 'btCancel', parent = self.panel1, pos = wxPoint(320, 216), size = wxSize(72, 24), style = 0)
        self.btCancel.SetConstraints(LayoutAnchors(self.btCancel, false, false, true, true))
        EVT_BUTTON(self.btCancel, wxID_WXBOAFILEDIALOGBTCANCEL, self.OnBtcancelButton)

        self.htmlWindow1 = wxUrlClickHtmlWindow(id = wxID_WXBOAFILEDIALOGHTMLWINDOW1, name = 'htmlWindow1', parent = self.panel1, pos = wxPoint(8, 0), size = wxSize(450, 20))
        self.htmlWindow1.SetBackgroundColour(self.htmlBackCol)
        self.htmlWindow1.SetConstraints(LayoutAnchors(self.htmlWindow1, true, true, true, false))

    def __init__(self, parent, message = 'Choose a file', defaultDir = '.', defaultFile = '', wildcard = '', style = wxOPEN, pos = wxDefaultPosition):
        self.htmlBackCol = wxColour(192, 192, 192)
        self.htmlBackCol = wxSystemSettings_GetSystemColour(wxSYS_COLOUR_BTNFACE)
        self.filterOpts = ['Boa files', 'Internal files', 'All files']
        self._init_ctrls(parent)
        self.SetStyle(style)

        EVT_SIZE(self.panel1, self.OnSize)
        EVT_KILL_FOCUS(self.btCancel, self.OnBtcancelKillFocus)
        EVT_CLOSE(self, self.OnCloseWindow)

        if defaultDir == '.':
            if self.currentDir == '.':
                defaultDir = path.abspath(self.currentDir)
            else:
                defaultDir = self.currentDir

        self.htmlWindow1.SetBorders(2)
        EVT_HTML_URL_CLICK(self.htmlWindow1, self.OnHtmlPathClick)

        self.lcFiles = createFileDlgFolderListClass()(self.panel1, self,
              defaultDir, pos = wxPoint(8, 21), size = wxSize(384, 152))
        self.lcFiles.SetConstraints(LayoutAnchors(self.lcFiles, true, true, true, true))

        EVT_LEFT_DCLICK(self.lcFiles, self.OnOpen)

        self.btOK.SetDefault()

        self.SetDirectory(defaultDir)
        self.SetFilename(defaultFile)

        self.editorFilter = self.lcFiles.node.filter
        self.editorFilterNode = self.lcFiles.node

        if wildcard:
            self.SetWildcard(wildcard)
        else:
            if self.lcFiles.node.filter == 'BoaFiles':
                self.chTypes.SetStringSelection('Boa files')
            elif self.lcFiles.node.filter == 'BoaInternalFiles':
                self.chTypes.SetStringSelection('Internal files')
            if self.lcFiles.node.filter == 'AllFiles':
                self.chTypes.SetStringSelection('All files')
            
        self.tcFilename.SetFocus()

        wxID_CLOSEDLG = wxNewId()
        EVT_MENU(self, wxID_CLOSEDLG, self.OnClose)
        self.SetAcceleratorTable(
              wxAcceleratorTable([(0, WXK_ESCAPE, wxID_CLOSEDLG)]))
        
    def OnSize(self, event):
        self.panel1.Layout()

    def OnCloseWindow(self, event):
        self.lcFiles.destroy()
        event.Skip()

    def newFileNode(self, defaultDir):
        from Explorers import FileExplorer, Explorer
        return FileExplorer.PyFileNode(path.basename(defaultDir), defaultDir, None,
              Explorer.EditorHelper.imgFolder, None, None)

    def updatePathLabel(self):
        # XXX This is messier than it should be !!!
        dir = self.GetDirectory()
        file = self.GetFilename()
        xtrdir = ''
        
        mainSegs = string.split(dir, '://')
        if len(mainSegs) == 1:
            prot = 'file'
            dir = mainSegs[0]
        elif len(mainSegs) == 2:
            prot, dir = mainSegs
        elif len(mainSegs) == 3:
            prot, dir, xtrdir = mainSegs
            
        import relpath
        filepath = []
        segs = relpath.splitpath(dir)
        if prot == 'zip':
            url = 'file://'
            for seg in segs[:-1]:
                url=url+seg+os.sep
                filepath.append(htmlLnk%(url, seg))

            segs2 = relpath.splitpath(xtrdir)
            url = 'zip'+url[4:]
            if segs:
                url = url + segs[-1]
                if segs2:
                    filepath.append(htmlLnk%(url, segs[-1]))
                else:
                    filepath.append(htmlCurrItem % segs[-1])
    
            filepath2 = []
            url = url +'://'
            for seg in segs2[:-1]:
                url=url+seg+'/'
                filepath2.append(htmlLnk%(url, seg))
            if segs2:
                filepath2.append(htmlCurrItem % segs2[-1])
            filepath2.append(file)

            htmlfilepath = string.join(filepath, '<b>%s</b>'%os.sep)
            if segs2:
                htmlfilepath = htmlfilepath + '<b>://</b>'+string.join(filepath2, '<b>/</b>')
        else:            
            url = '%s://'%prot
            for seg in segs[:-1]:
                url=url+seg+self.lcFiles.node.pathSep
                filepath.append(htmlLnk%(url, seg))
            if segs:
                filepath.append(htmlCurrItem % segs[-1])
            filepath.append(file)
            
            htmlfilepath = string.join(filepath, '<b>%s</b>'%self.lcFiles.node.pathSep)

        self.htmlWindow1.SetPage(htmlPath % (self.htmlBackCol.Red(), 
              self.htmlBackCol.Green(), self.htmlBackCol.Blue(), prot, 
              htmlfilepath))

    def open(self, node):
        if node:
            if node.isFolderish():
                self.lcFiles.refreshItems(self.modImages, node)
                self.updatePathLabel()
                if self.style & wxSAVE: btn = saveStr
                else: btn = openStr
                self.btOK.SetLabel(btn)
                return
        if self.tcFilename.GetValue():
            self.editorFilterNode.setFilter(self.editorFilter)
            dir = self.GetDirectory()
            wxBoaFileDialog.currentDir = dir
            self.EndModal(wxID_OK)

    def OnOpen(self, event):
        self.ok()

    def ok(self):
        if self.lcFiles.selected == 0:
            node = self.lcFiles.node.createParentNode()
            if node: node.allowedProtocols = ['zip']
            if node.resourcepath == self.lcFiles.node.resourcepath:
                prot = node.protocol
                if prot in ('config', 'root'):
                    catnode = self.transports
                else:
                    catnode = self.transportsByProtocol[prot]
                    
                self.lcFiles.refreshItems(self.modImages, catnode)
                self.updatePathLabel()
                if self.style & wxSAVE: btn = saveStr
                else: btn = openStr
                self.btOK.SetLabel(btn)
                return
        else:
            node = self.lcFiles.getSelection()
            if node: node.allowedProtocols = ['zip']

        if (node and not node.isFolderish() or not node) and self.style & wxOVERWRITE_PROMPT:
            if self.lcFiles.hasItemNamed(self.GetFilename()):
                dlg = wxMessageDialog(self, 'This file already exists.\n'\
                      'Do you want to overwrite the file?', 'Overwrite file?',
                      wxYES_NO | wxICON_WARNING)
                try:
                    if dlg.ShowModal() == wxID_NO:
                        return
                finally:
                    dlg.Destroy()
        self.open(node)

    def OnBtokButton(self, event):
        self.ok()

    def OnBtcancelButton(self, event):
        self.editorFilterNode.setFilter(self.editorFilter)
        self.EndModal(wxID_CANCEL)

    def OnTcfilenameTextEnter(self, event):
        self.ok()

#---wxFileDialog lookalike meths------------------------------------------------

    def SelectItem(self, name):
        node = self.lcFiles.getSelection()
        # deselect
        if not name:
            if self.style & wxSAVE: btn = saveStr
            else: btn = openStr
        # file
        elif name != '..' and not node.isFolderish():
            self.SetFilename(name)
            if self.style & wxSAVE: btn = saveStr
            else: btn = openStr
        # dir
        else:
            btn = openStr

        self.btOK.SetLabel(btn)

    def GetDirectory(self):
        return self.lcFiles.node.getURI()
    def GetFilename(self):
        return self.tcFilename.GetValue()
    def GetFilterIndex(self, *_args, **_kwargs):
        pass
    def GetMessage(self):
        return self.GetTitle()
    def GetPath(self):
        dir = self.GetDirectory()
        if dir[-1] != self.lcFiles.node.pathSep:
            return dir + self.lcFiles.node.pathSep + self.GetFilename()
        else:
            return dir + self.GetFilename()
    def GetFilePath(self):
        from Explorers import Explorer
        prot, cat, res, uri = Explorer.splitURI(self.GetPath())
        assert prot == 'file', 'Only filesystem paths allowed'
        return res
    def GetStyle(self):
        return self.style
    def GetWildcard(self):
        return self.wildcard
    def SetDirectory(self, newDir):
        from Explorers import Explorer
        prot, cat, res, uri = Explorer.splitURI(newDir+'/dummy.tmp')
        res = os.path.dirname(res)
        node = Explorer.getTransport(prot, cat, res, self.transports)
        node.allowedProtocols = ['zip']
        self.lcFiles.refreshItems(self.modImages, node)
        self.updatePathLabel()
    def SetFilename(self, filename):
        self.tcFilename.SetValue(filename)
        self.updatePathLabel()
    def SetFilterIndex(self, *_args, **_kwargs):
        pass
    def SetMessage(self, mess):
        self.SetTitle(mess)
    def SetPath(self, newPath):
        pass
    def SetStyle(self, style):
        title = 'File Dialog'
        btn = 'OK'
        if style & wxOPEN:
            title = 'Open'
            btn = openStr
        if style & wxSAVE:
            title = 'Save As'
            btn = saveStr

        self.SetTitle(title)
        self.btOK.SetLabel(btn)
        self.style = style
    def SetWildcard(self, wildcard):
        self.wildcard = wildcard
        if wildcard in self.filterOpts:
            self.chTypes.SetStringSelection(wildcard)
            self.OnChtypesChoice(None)
##    def ShowModal(self, *_args, **_kwargs):
##        pass
##    def GetFilenames(self, *_args, **_kwargs):
##        val = apply(cmndlgsc.wxFileDialog_GetFilenames,(self,) + _args, _kwargs)
##        return val
##    def GetPaths(self, *_args, **_kwargs):
##        val = apply(cmndlgsc.wxFileDialog_GetPaths,(self,) + _args, _kwargs)
##        return val
    def __repr__(self):
        return '<C wxBoaFileDialog instance at %s>' % (self.this,)

    def OnChtypesChoice(self, event):
        fType = self.chTypes.GetStringSelection()
        if fType == 'Boa files':
            self.lcFiles.node.setFilter('BoaFiles')
        elif fType == 'Internal files':
            self.lcFiles.node.setFilter('BoaInternalFiles')
        elif fType == 'All files':
            self.lcFiles.node.setFilter('AllFiles')
        self.lcFiles.refreshCurrent()

    def OnBtcancelKillFocus(self, event):
        self.btOK.SetDefault()
        if self.lcFiles.selected == -1:
            self.lcFiles.selectItemNamed('..')

    def OnHtmlPathClick(self, event):
        url = event.linkinfo[0]
        
        if url == 'UP':
            self.lcFiles.selected = 0
            self.ok()
        elif url == 'NEWFOLDER':
            self.lcFiles.OnNewFolder(None)
        elif url == 'ROOT':
            self.open(self.transports)
        elif url == 'PROTROOT':
            if self.transportsByProtocol.has_key(self.lcFiles.node.protocol):
                self.open(self.transportsByProtocol[self.lcFiles.node.protocol])
            else:
                self.open(self.transports)
        else:
            self.SetDirectory(url)

    def OnClose(self, event):
        self.OnBtcancelButton(event)


def createFileDlgFolderListClass():
    # XXX This is a bit convoluted ;)
    # XXX The late importing is the only way to avoid import problems because
    # XXX the dialog swapping code is initialised so early on

    from Explorers import Explorer
    class FileDlgFolderList(Explorer.PackageFolderList):
        def __init__(self, parent, dlg, filepath, pos = wxDefaultPosition, size = wxDefaultSize):
            from Explorers import Explorer
            Explorer.PackageFolderList.__init__(self, parent, '', pos, size, style = wxSUNKEN_BORDER)
            self.dlg = dlg
            EVT_LIST_ITEM_SELECTED(self, self.GetId(), self.OnItemSelect)
            EVT_LIST_ITEM_DESELECTED(self, self.GetId(), self.OnItemDeselect)
            EVT_RIGHT_UP(self, self.OnListRightUp)
            self.menu = wxMenu()
            menuId = wxNewId()
            self.menu.Append(menuId, 'New Folder')
            EVT_MENU(self, menuId, self.OnNewFolder)
            EVT_LIST_BEGIN_LABEL_EDIT(self, self.GetId(), self.OnBeginLabelEdit)
            EVT_LIST_END_LABEL_EDIT(self, self.GetId(), self.OnEndLabelEdit)

            dlg.transports, dlg.transportsByProtocol = self.buildExplorerNodes()

        def buildExplorerNodes(self):
            import Preferences, Utils, EditorHelper
            from Explorers import ExplorerNodes, FileExplorer
            
            transports = ExplorerNodes.RootNode('Transport', EditorHelper.imgFolder)
            transports.parent = transports
            transports.protocol = 'root'
            
            conf = Utils.createAndReadConfig('Explorer')
            catnode = FileExplorer.FileSysCatNode(None, conf, transports, None)
            transports.entries.append(catnode)
            transportsByProtocol = {'file': catnode}

            catnode = ExplorerNodes.BookmarksCatNode(None, conf, transports, transports)
            transports.entries.insert(0, catnode)
            transportsByProtocol['config.bookmark'] = catnode
            
            if conf.has_option('explorer', 'ssh'):
                from Explorers import SSHExplorer
                catnode = SSHExplorer.SSHCatNode(None, conf, transports, None)
                transports.entries.append(catnode)
                transportsByProtocol['ssh'] = catnode
            
            if conf.has_option('explorer', 'ftp'):
                from Explorers import FTPExplorer
                catnode = FTPExplorer.FTPCatNode(None, conf, transports, None)
                transports.entries.append(catnode)
                transportsByProtocol['ftp'] = catnode
            
            if conf.has_option('explorer', 'dav'):
                try:
                    from Explorers import DAVExplorer
                except ImportError:
                    pass
                else:
                    catnode = DAVExplorer.DAVCatNode(None, conf, transports, None)
                    transports.entries.append(catnode)
                    transportsByProtocol['dav'] = catnode
            
            return transports, transportsByProtocol
                
        def destroy(self):
            self.menu.Destroy()
            from Explorers import Explorer
            Explorer.PackageFolderList.destroy(self)
        
        def OnItemSelect(self, event):
            from Explorers import Explorer
            Explorer.PackageFolderList.OnItemSelect(self, event)
            item = self.getSelection()
            if item:
                self.dlg.SelectItem(item.name)
            elif self.selected == 0:
                self.dlg.SelectItem('..')
            event.Skip()
    
        def OnItemDeselect(self, event):
            from Explorers import Explorer
            Explorer.PackageFolderList.OnItemDeselect(self, event)
            self.dlg.SelectItem(None)
            event.Skip()
    
        def OnListRightUp(self, event):
            self.PopupMenu(self.menu, wxPoint(event.GetX(), event.GetY()))
            event.Skip()
    
        def OnNewFolder(self, event):
            name = Utils.getValidName(self.getAllNames(), 'Folder')
            self.node.newFolder(name)
            self.refreshCurrent()
            self.selectItemNamed(name)
            self.EnsureVisible(self.selected)
            self.EditLabel(self.selected)
    
        def OnBeginLabelEdit(self, event):
            self.oldLabelVal = event.GetText()
    
        def OnEndLabelEdit(self, event):
            newText = event.GetText()
            if newText != self.oldLabelVal:# and isinstance(self.list.node, ZopeItemNode):
                event.Skip()
                self.node.renameItem(self.oldLabelVal, newText)
                self.refreshCurrent()

    return FileDlgFolderList

if __name__ == '__main__':
    app = wxPySimpleApp()
    import PaletteMapping
    wxBoaFileDialog.modImages = wxImageList(16, 16)
    dlg = wxBoaFileDialog(None, defaultDir='.')
    try:
        if dlg.ShowModal() == wxID_OK:
            wxMessageBox(dlg.GetPath())
    finally:
        dlg.Destroy()
    