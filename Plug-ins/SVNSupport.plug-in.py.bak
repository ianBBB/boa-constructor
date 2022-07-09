#-----------------------------------------------------------------------------
# Name:        SVNExplorer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2006
# RCS-ID:      $Id$
# Copyright:   (c) 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
""" Explorer classes for SVN browsing and operations """

import time, stat, os

import wx
from wx.lib.dialogs import ScrolledMessageDialog


from Explorers import ExplorerNodes, scrm
from Models import EditorModels, EditorHelper
from Preferences import IS

import ProcessProgressDlg, Utils

(wxID_SVNUPDATE, wxID_SVNCOMMIT, wxID_SVNADD, wxID_SVNREMOVE,
 wxID_SVNDIFF, wxID_SVNLOG, wxID_SVNSTATUS, wxID_FSSVNIMPORT, wxID_FSSVNCHECKOUT,
 wxID_FSSVNENV, wxID_SVNTAG, wxID_SVNBRANCH, wxID_SVNLOCK, wxID_SVNUNLOCK, 
 wxID_SVNTEST, wxID_SVNRESOLVED, wxID_SVNINFO) = Utils.wxNewIds(17)

svnFolderImgIdx = 6
maxHelpLines = 30

class SVNEntriesParser:
    def __init__(self, filename):
        self.entries = []
        self.initParser(filename)
    
    def entry(self, name):
        for entryName, entryAttrs in self.entries:
            if name == entryName:
                return entryAttrs
        raise KeyError, name+' not found'
        
    def StartElement(self, name, attrs ):
        name = name.encode()
        if name == 'entry' and 'name' in attrs and attrs['name']:
            self.entries.append( (name, attrs) )

    def initParser(self, filename):
        from xml.parsers import expat
        parser = expat.ParserCreate()
        parser.StartElementHandler = self.StartElement
        return parser.Parse(open(filename,'r').read(), 1)


def isSVN(filename):
    file = os.path.basename(filename)
    return file.lower() == '.svn' and \
                      os.path.exists(os.path.join(filename, 'entries')) and \
                      os.path.exists(os.path.join(filename, 'format')) 

def svnFileLocallyModified(filename, entry):
    """  svnFileLocallyModified -> modified, conflict """

    filets = time.asctime(time.gmtime(os.stat(filename)[stat.ST_MTIME]))
    
    try:
        texttime = entry['text-time'].rsplit('.', 1)[0]
    except KeyError: 
        return False, False
    
    texttime = time.asctime(time.strptime(texttime, '%Y-%m-%dT%H:%M:%S'))
    
    return (texttime != filets, False)
##    
##    
##    ismerge = timestamp.split('+')
##    conflict = ismerge[0] == 'Result of merge'
##    filets = time.asctime(time.gmtime(os.stat(filename)[stat.ST_MTIME]))
##    if conflict and len(ismerge) == 1 or ismerge[0][:15] == 'dummy timestamp':
##        filesegs, svnsegs = 1, 0
##    # convert day to int to avoid zero padded differences
##    else:
##        if conflict:
##            filesegs, svnsegs = filets.split(), ismerge[1].split()
##        else:
##            filesegs, svnsegs = filets.split(), timestamp.split()
##        if svnsegs and svnsegs[0] == 'Initial' or len(svnsegs) < 3:
##            svnsegs.append('0')
##        # use day field of dates for comparison
##        filesegs[2], svnsegs[2] = int(filesegs[2]), int(svnsegs[2])
##
##    return (filesegs != svnsegs, conflict)


class SVNController(ExplorerNodes.Controller):
    updateBmp = 'Images/CvsPics/Update.png'
    commitBmp = 'Images/CvsPics/Commit.png'
    addBmp = 'Images/CvsPics/Add.png'
    removeBmp = 'Images/CvsPics/Remove.png'
    diffBmp = 'Images/CvsPics/Diff.png'
    logBmp = 'Images/CvsPics/Log.png'
    statusBmp = 'Images/CvsPics/Status.png'
    #infoBmp = 'Images/CvsPics/Info.png'
    #resolvedBmp = 'Images/CvsPics/ResolvedConflict.png'
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.Menu()
        self.svnOptions = '-z7'

        self.svnMenuDef = [
              (wxID_SVNUPDATE, 'Update', self.OnUpdateSVNItems, self.updateBmp),
              (wxID_SVNCOMMIT, 'Commit', self.OnCommitSVNItems, self.commitBmp),
              (wxID_SVNRESOLVED, 'Resolved', self.OnResolvedSVNItems, '-'),
              (-1, '-', None, ''),
              (wxID_SVNADD, 'Add', self.OnAddSVNItems, self.addBmp),
              (wxID_SVNREMOVE, 'Remove', self.OnRemoveSVNItems, self.removeBmp),
              (-1, '-', None, ''),
              (wxID_SVNDIFF, 'Diff', self.OnDiffSVNItems, self.diffBmp),
              (wxID_SVNLOG, 'Log', self.OnLogSVNItems, self.logBmp),
              (wxID_SVNSTATUS, 'Status', self.OnStatusSVNItems, self.statusBmp),
              (wxID_SVNINFO, 'Info', self.OnInfoSVNItems, '-'),
              #(-1, '-', None, ''),
              #(wxID_SVNLOCK, 'Lock', self.OnLockSVNItems, '-'),
              #(wxID_SVNUNLOCK, 'Unlock', self.OnUnlockSVNItems, '-'), 
        ]

        self.setupMenu(self.menu, self.list, self.svnMenuDef)

        self.fileSVNMenuDef = [
              #(wxID_FSSVNIMPORT, 'Import', self.OnImportSVNFSItems, '-'),
              (wxID_FSSVNCHECKOUT, 'Checkout', self.OnCheckoutSVNFSItems, '-'),
        ]

        self.fileSVNMenu = wx.Menu()
        self.setupMenu(self.fileSVNMenu, self.list, self.fileSVNMenuDef, False)


        self.images = wx.ImageList(16, 16)
        for svnImg in ( 'Images/CvsPics/File.png',
                        'Images/CvsPics/BinaryFile.png',
                        'Images/CvsPics/ModifiedFile.png',
                        'Images/CvsPics/ModifiedBinaryFile.png',
                        'Images/CvsPics/MissingFile.png',
                        'Images/CvsPics/ConflictingFile.png',
                        'Images/CvsPics/Dir.png',
                        'Images/Modules/FolderUp.png',
                        'Images/CvsPics/UnknownDir.png',
                        'Images/CvsPics/UnknownFile.png'):
            self.images.Add(IS.load(svnImg))

        self.toolbarMenus = [self.svnMenuDef]

        FSSVNFolderNode.images = self.images

    def destroy(self):
        self.svnMenuDef = ()
        self.fileSVNMenuDef = ()
        self.toolbarMenus = ()
        self.images = None
        FSSVNFolderNode.images = None
        self.menu.Destroy()

    def getName(self, item):
        name = ExplorerNodes.Controller.getName(self, item)
        if ' ' in name:
            return '"%s"' % name
        else:
            return name

    def setupListCtrl(self):
        self.list.SetWindowStyleFlag(wx.LC_REPORT)
        self.list.InsertColumn(0, 'Name', wx.LIST_FORMAT_LEFT, 150)
        self.list.InsertColumn(1, 'Rev.', wx.LIST_FORMAT_LEFT, 50)
        self.list.InsertColumn(2, 'Date', wx.LIST_FORMAT_LEFT, 150)
        self.list.InsertColumn(3, 'Status', wx.LIST_FORMAT_LEFT, 150)
        self.list.InsertColumn(4, 'Options', wx.LIST_FORMAT_LEFT, 50)

    def cleanupListCtrl(self):
        cols = range(5)
        cols.reverse()
        for col in cols:
            self.list.DeleteColumn(col)

    def showMessage(self, cmd, msg):
        dlg = ScrolledMessageDialog(self.list, msg, cmd)
        try: dlg.ShowModal()
        finally: dlg.Destroy()

    def svnCmd(self, command, options, files, extraOptions = ''):
        #svnOpts = self.svnOptions
        #if extraOptions:
        #    svnOpts = '%s %s'%(svnOpts, extraOptions)
        return 'svn %s %s %s' % (command, options, ' '.join(files))

    def svnCmdPrompt(self, wholeCommand, inDir, help = ''):
        #if isinstance(self.list.node, FSSVNFolderNode):
        #    svnroot = self.list.node.root
        #else:
        #    svnroot = os.environ.get('SVNROOT', '(not defined)')
        dlg = wx.TextEntryDialog(self.list, '(in dir %s)\n\n%s'%(inDir, help),
              'SVN command line', wholeCommand)
        if wx.Platform == '__WXMSW__':
            te = Utils.getCtrlsFromDialog(dlg, 'TextCtrl')[0]
            try:
                te.SetSelection(wholeCommand.index('['),
                                wholeCommand.index(']')+1)
            except ValueError:
                te.SetInsertionPoint(len(wholeCommand))
        try:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetValue()
            else:
                return ''
        finally:
            dlg.Destroy()

    def getSvnHelp(self, cmd, option = 'help'):
        SVNPD = ProcessProgressDlg.ProcessProgressDlg(self.list,
                  'svn %s %s'% (option, cmd), '', modally=False)
        try:
            return ' '.join(SVNPD.output[:maxHelpLines]).expandtabs(8)
        finally:
            SVNPD.Destroy()

    # svnOutput can be 'output window', 'dialogs' or 'tuple'
    def doSvnCmd(self, cmd, svnDir, stdinput='', svnOutput='output window'):
        # Repaint background
        wx.Yield()

        cwd = os.getcwd()
        try:
            os.chdir(svnDir)
            SVNPD = ProcessProgressDlg.ProcessProgressDlg(self.list, cmd, 'SVN progress...')
            try:
                if SVNPD.ShowModal() == wx.OK:
                    outls = SVNPD.output
                    errls = SVNPD.errors
                else:
                    return
            finally:
                SVNPD.Destroy()

            err = ''.join(errls).strip()

            if svnOutput == 'output window':
                errout = self.editor.erroutFrm
                tbs = errout.updateCtrls((), outls, 'SVN Result', '', err)
                errout.display(tbs)

            elif svnOutput == 'dialogs':
                if err.strip():
                    dlg = wx.MessageDialog(self.list, err,
                      'Server response or Error', wx.OK | wx.ICON_EXCLAMATION)
                    try: dlg.ShowModal()
                    finally: dlg.Destroy()

                if outls and not (len(outls) == 1 and not outls[0].strip()):
                    self.showMessage(cmd, ''.join(outls))
            elif svnOutput == 'tuple':
                return outls, errls

            #msgType = 'warning' if err else 'info' # i wish
            if err: msgType = 'Warning'
            else: msgType = 'Info'
            self.editor.setStatus('SVN command completed: %s'%cmd, msgType)

        finally:
            os.chdir(cwd)

    def doSvnCmdOnSelection(self, cmd, cmdOpts,
              preCmdFunc=None, postCmdFunc=None, svnOutput='output window'):
        if self.list.node:
            names = self.getNamesForSelection(self.list.getMultiSelection())
            svnDir = os.path.dirname(self.list.node.resourcepath)
            if not names: names = ['']
##                names = ['']
##                svnDir, names[0] = os.path.split(svnDir)
            cmdStr = self.svnCmdPrompt(self.svnCmd(cmd, cmdOpts, names), svnDir,
                  self.getSvnHelp(cmd))
            if cmdStr:
                if preCmdFunc: preCmdFunc(names)
                res = self.doSvnCmd(cmdStr, svnDir, svnOutput=svnOutput)
                if postCmdFunc: postCmdFunc(names)
                return res

    def doSvnCmdInDir(self, cmd, cmdOpts, svnDir, items, svnOpts = ''):
        cmdStr = self.svnCmdPrompt(self.svnCmd(cmd, cmdOpts, items, svnOpts),
              svnDir, self.getSvnHelp(cmd))
        if cmdStr:
            self.doSvnCmd(cmdStr, svnDir)
            return True
        else:
            return False

##    def importSVNItems(self):
##        # Imports are called from normal folders not SVN folders
##
##        # XXX Check if SVN folder exists ?
##        svnDir = self.list.node.resourcepath
##        if self.doCvsCmdInDir('import', '', svnDir, ['[MODULE]', 'VENDOR', 'RELEASE']):
##            self.list.refreshCurrent()


    def checkoutSVNItems(self):
        # Checkouts are called from normal folders not SVN folders
        svnDir = self.list.node.resourcepath
        if self.doSvnCmdInDir('checkout', '', svnDir, ['--username [USER]', 
            '--password [PASS]', '[URL]', '[PATH]'], ''):
            self.list.refreshCurrent()

    def updateSVNItems(self):
        self.doSvnCmdOnSelection('update', '')
        self.list.refreshCurrent()

    def OnUpdateSVNItems(self, event):
        self.updateSVNItems()

    def OnCommitSVNItems(self, event):
        self.doSvnCmdOnSelection('commit', '-m "[no message]"')
        self.list.refreshCurrent()

    def OnAddSVNItems(self, event):
        self.doSvnCmdOnSelection('add', '')
        self.list.refreshCurrent()


    quotes = ('"', "'")
    def selPreCmd_remove(self, list):
        dir = os.path.dirname(self.list.node.resourcepath)
        for name in list:
            try:

                if name[0] in self.quotes and name[-1] in self.quotes:
                    name = name[1:-1]
                os.remove(os.path.join(dir, name))
            except OSError, err:
                # Skip files already removed
                print err

    def OnRemoveSVNItems(self, event):
        self.doSvnCmdOnSelection('remove', '', self.selPreCmd_remove)
        self.list.refreshCurrent()

    def OnDiffSVNItems(self, event):
        # a syntax highlighted window is provided for unified diffs
        res = self.doSvnCmdOnSelection('diff', '-r HEAD', svnOutput='tuple')
        if res is not None and len(res)==2:
            outls, errls = res
            errout = self.editor.erroutFrm
            tbs = errout.updateCtrls((), outls, 'SVN Result', '', errls)
            errout.display(tbs)
            errout.displayDiff(''.join(outls))


    def OnLogSVNItems(self, event):
        self.doSvnCmdOnSelection('log', '')

    def OnStatusSVNItems(self, event):
        self.doSvnCmdOnSelection('status', '-u')

    def OnImportSVNFSItems(self, event):
        self.importSVNItems()

    def OnCheckoutSVNFSItems(self, event):
        self.checkoutSVNItems()

    def OnTagSVNItems(self, event):
        self.doSvnCmdOnSelection('tag', '[TAG]')

    def OnBranchSVNItems(self, event):
        self.doSvnCmdOnSelection('tag', '-b')

##    def OnLockSVNItems(self, event):
##        self.doSvnCmdOnSelection('admin', '-l[REV]')
##
##    def OnUnlockSVNItems(self, event):
##        self.doSvnCmdOnSelection('admin', '-u[REV]')

    def OnResolvedSVNItems(self, event):
        self.doSvnCmdOnSelection('resolved', '')
        self.list.refreshCurrent()

    def OnInfoSVNItems(self, event):
        self.doSvnCmdOnSelection('info', '')

class SVNFolderNode(ExplorerNodes.ExplorerNode):
    protocol = 'svn'
    def __init__(self, entry, resourcepath, dirpos, parent):
        if entry:
            name = entry['name']
            try:
                self.revision = entry['committed-rev']
            except KeyError:
                self.revision = ''
            try:
                self.tagdate = entry['committed-date']
            except KeyError:
                self.tagdate = ''
            try:
                self.timestamp = entry['text-time']
            except KeyError:
                self.timestamp = self.tagdate
        else:
            name=self.revision=self.timestamp=self.tagdate = ''

        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None, svnFolderImgIdx, parent)

        self.dirpos = dirpos

    def text(self):
        return '/'.join(('D', self.name, self.revision, self.timestamp, self.options, self.tagdate))

    def isFolderish(self):
        return False

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def createParentNode(self):
        parent = os.path.abspath(os.path.join(self.resourcepath, '..'))
        return PyFileNode(os.path.basename(parent), parent, self.clipboard,
                  EditorModels.FolderModel.imgIdx, self)

    def open(self, editor):
        tree = editor.explorer.tree
        par = tree.GetItemParent(tree.GetSelection())
        chd = tree.getChildNamed(par, self.name)
        if not tree.IsExpanded(chd):
            tree.Expand(chd)
        svnChd = tree.getChildNamed(chd, '.svn')
        tree.SelectItem(svnChd)
        return None, None

class SVNFileNode(ExplorerNodes.ExplorerNode):
    protocol = 'svn'
    def __init__(self, entry, resourcepath, parent):
        if entry:
            name = entry['name']
            try:
                self.revision = entry['committed-rev']
            except KeyError:
                self.revision = ''
            try:
                self.tagdate = entry['committed-date']
            except KeyError:
                self.tagdate = ''
            try:
                self.timestamp = entry['text-time']
            except KeyError:
                self.timestamp = self.tagdate
        else:
            name=self.revision=self.timestamp=self.tagdate = ''

        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None, -1, parent)

        self.imgIdx = 0#self.missing and self.missing << 2 \
        
        filename = os.path.abspath(os.path.join(self.resourcepath, '..', name))
        if os.path.exists(filename):
            self.modified, self.conflict = svnFileLocallyModified(filename, entry)
            self.missing = False
        else:
            self.modified = self.conflict = False
            self.missing = True

##        self.modified = False
        self.conflict = False
##        self.imgIdx = 0
##        if self.timestamp:
##            filename = os.path.abspath(os.path.join(self.resourcepath, '..', name))
##            if os.path.exists(filename):
##                self.modified, self.conflict = svnFileLocallyModified(filename, self.timestamp)
##            else:
##                self.missing = True
##
        self.imgIdx = self.missing and self.missing << 2 \
                      or self.conflict *5 or self.modified << 1

    def isFolderish(self):
        return False

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def getDescription(self):
        return '%s, (%s, %s)'%(self.name, self.revision, self.timestamp)#, self.options, self.tagdate), '/')

    def open(self, editor):
        tree = editor.explorer.tree
        node = editor.explorer.list.getSelection()
        timestamp = node.timestamp
        tree.SelectItem(tree.GetItemParent(tree.GetSelection()))
        editor.explorer.list.selectItemNamed(self.name)
        if self.conflict:
            node = editor.explorer.list.getSelection()

            if timestamp.startswith('Result of merge+'):
                model, controller = editor.openOrGotoModule(node.resourcepath,
                      transport=node)

                # XXX inefficient
                conflicts = model.getSVNConflicts()
                if conflicts:
                    from Views.EditorViews import SVNConflictsView
                    if not model.views.has_key(SVNConflictsView.viewName):
                        resultView = editor.addNewView(SVNConflictsView.viewName,
                              SVNConflictsView)
                    else:
                        resultView = model.views[SVNConflictsView.viewName]
                    resultView.refresh()
                    resultView.focus()
                else:
                    editor.setStatus('No SVN conflicts in file', 'Warning', True)

                return model, controller
        return None, None

    def text(self):
        return '/'.join(('', self.name, self.revision, self.timestamp, self.options, self.tagdate))

class SVNUnAddedItem(ExplorerNodes.ExplorerNode):
    def __init__(self, name, resourcepath, parent, isFolder):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, None, isFolder and 8 or 9, parent)

    def open(self, editor):
        tree = editor.explorer.tree
        tree.SelectItem(tree.GetItemParent(tree.GetSelection()))
        editor.explorer.list.selectItemNamed(self.name)
        return None, None

class FSSVNFolderNode(ExplorerNodes.ExplorerNode):
    protocol = 'svn'
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, bookmarks=None):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              EditorModels.CVSFolderModel.imgIdx, parent)
        self.vetoSort = True
        self.dirpos = 0
        self.upImgIdx = 7

    def destroy(self):
        self.entries = []

    def getDescription(self):
        try:
            return '%s'% (self.root)
        except AttributeError:
            return ExplorerNodes.ExplorerNode.getDescription(self)

    def getTitle(self):
        try:
            return '%s'% (self.repository)
        except AttributeError:
            return ExplorerNodes.ExplorerNode.getTitle(self)

    def isFolderish(self):
        return True

    def notifyBeginLabelEdit(self, event):
        event.Veto()

    def createParentNode(self):
        if self.parent:
            return self.parent
        else:
            parent = os.path.abspath(os.path.join(self.resourcepath, os.path.join('..', '.svn')))
            return FSSVNFolderNode(os.path.basename(parent), parent, self.clipboard,
                      EditorModels.SVNFolderModel.imgIdx, self)

    def createChildNode(self, entry):
        if entry['kind'] == 'dir':
            self.dirpos = self.dirpos + 1
            return SVNFolderNode(entry, self.resourcepath, self.dirpos, self)
        elif entry['kind'] == 'file':
            try:
                return SVNFileNode(entry, self.resourcepath, self)
            except IOError:
                return None

    def openList(self):
        def readFile(self, name):
            return open(os.path.join(self.resourcepath, name)).read().strip()

        #self.root = readFile(self, 'Root')
        #self.repository = readFile(self, 'Repository')
        names = {}
        files = []
        dirs = []
        p = SVNEntriesParser(os.path.join(self.resourcepath, 'entries'))
        for name, entry in p.entries:
            svnNode = self.createChildNode(entry)
            if entry['kind'] == 'file':
                files.append(svnNode)
                names[svnNode.name] = svnNode
            elif entry['kind'] == 'dir':
                dirs.append(svnNode)
                names[svnNode.name] = svnNode

        fileEntries = self.parent.openList()
        for entry in fileEntries:
            if entry.name not in names:
                unaddedNode = SVNUnAddedItem(entry.name, entry.resourcepath, 
                      self, entry.isFolderish())
                if entry.isFolderish():
                    dirs.append(unaddedNode)
                else:
                    files.append(unaddedNode)
        
        self.entries = dirs + files
##            if svnNode:
##                res[svnNode.name] = svnNode
##                if svnNode.name not in filenames:
##                    missingEntries.append(svnNode)



##        res = {}
##        self.dirpos = 0
##        fileEntries = self.parent.openList()
##        txtEntries = open(os.path.join(self.resourcepath, 'Entries')).readlines()
##        filenames = map(lambda x: x.name, fileEntries)
##        missingEntries = []
##
##        for txtEntry in txtEntries:
##            svnNode = self.createChildNode(txtEntry.strip())
##            if svnNode:
##                res[svnNode.name] = svnNode
##                if svnNode.name not in filenames:
##                    missingEntries.append(svnNode)
##
##        lst = []
##        for entry in fileEntries:
##            testSVNDir = os.path.join(entry.resourcepath, 'SVN')
##            if os.path.isdir(entry.resourcepath) and \
##                  os.path.exists(testSVNDir) and isSVN(testSVNDir):
##                node = SVNFolderNode('D/%s////'%entry.name, self.resourcepath,
##                  self.dirpos, self)
##            else:
##                node = res.get(entry.name, SVNUnAddedItem(entry.name, entry.resourcepath, self, entry.isFolderish()))
##            if node:
##                lst.append(node)
##
##        for missing in missingEntries:
##            lst.append(missing)
##
##        self.entries = lst
        return self.entries 

    def open(self, editor):
        return editor.openOrGotoModule(self.resourcepath)

    def openParent(self, editor):
        tree = editor.explorer.tree
        svnParentItemParent = tree.GetItemParent(tree.GetItemParent(tree.GetSelection()))

        svnChd = tree.getChildNamed(svnParentItemParent, '.svn')
        if svnChd.IsOk():
            tree.SelectItem(svnChd)
            return True
        else:
            return False

#---------------------------------------------------------------------------
# Register svn dirs as a subtype of file explorers
from Explorers import FileExplorer
FileExplorer.FileSysNode.subExplorerReg['folder'].append(
      (FSSVNFolderNode, isSVN, EditorHelper.imgCVSFolder)
)

ExplorerNodes.register(FSSVNFolderNode, clipboard=None, confdef=('', ''),
                       controller=SVNController)
