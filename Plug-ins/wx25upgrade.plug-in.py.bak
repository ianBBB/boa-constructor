#-----------------------------------------------------------------------------
# Name:        wx25upgradeDialog.py
# Purpose:     Dialog to select a folder to upgrade
#
#              Inspired by paul sorenson's upgrade.py, which is required
#
# Author:      Werner F. Bruhin
#
# Created:     2005/07/03
# RCS-ID:      $Id$
# Licence:     very simple, any one may use and/or change it.
#-----------------------------------------------------------------------------
#Boa:Dialog:Wx25CodeUpgradeDlg

import wx
import os
import sys
import string

from ExternalLib import wx25upgrade, reindent
import Utils

[wxID_WX25CODEUPGRADEDLG, wxID_WX25CODEUPGRADEDLGSETFILE, 
 wxID_WX25CODEUPGRADEDLGSETSOURCE, wxID_WX25CODEUPGRADEDLGSETTARGET, 
 wxID_WX25CODEUPGRADEDLGSOURCEFILE, wxID_WX25CODEUPGRADEDLGSOURCEFOLDER, 
 wxID_WX25CODEUPGRADEDLGSTARTFILE, wxID_WX25CODEUPGRADEDLGSTARTFOLDER, 
 wxID_WX25CODEUPGRADEDLGSTATICTEXT1, wxID_WX25CODEUPGRADEDLGSTATICTEXT2, 
 wxID_WX25CODEUPGRADEDLGSTFILE, wxID_WX25CODEUPGRADEDLGSTSOURCEFOLDER, 
 wxID_WX25CODEUPGRADEDLGSTTARGETFOLDER, wxID_WX25CODEUPGRADEDLGTARGETFOLDER, 
 wxID_WX25CODEUPGRADEDLGUPGRADEGUIDE, 
] = [wx.NewId() for _init_ctrls in range(15)]

class Wx25CodeUpgradeDlg(wx.Dialog):
    def _init_coll_flexGridSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stSourceFolder, 1, border=2,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.sourceFolder, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.stTargetFolder, 1, border=2,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.targetFolder, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.stFile, 1, border=2,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddWindow(self.sourceFile, 1, border=2, flag=wx.ALL)

    def _init_coll_bsDialog_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.flexGridSizer1, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.staticText1, 0, border=10,
              flag=wx.ALIGN_LEFT | wx.ALL)
        parent.AddSizer(self.fgsButtons, 0, border=2, flag=wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.StaticText2, 0, border=2, flag=wx.ALL)

    def _init_coll_fgsButtons_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.setSource, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.setTarget, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.startFolder, 1, border=2, flag=wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.setFile, 1, border=2, flag=wx.ALL)
        parent.AddWindow(self.startFile, 1, border=2, flag=wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.upgradeGuide, 1, border=2, flag=wx.ALL)

    def _init_sizers(self):
        # generated method, don't edit
        self.flexGridSizer1 = wx.FlexGridSizer(cols=2, hgap=0, rows=0, vgap=0)

        self.fgsButtons = wx.FlexGridSizer(cols=4, hgap=0, rows=0, vgap=0)

        self.bsDialog = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_flexGridSizer1_Items(self.flexGridSizer1)
        self._init_coll_fgsButtons_Items(self.fgsButtons)
        self._init_coll_bsDialog_Items(self.bsDialog)

        self.SetSizer(self.bsDialog)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_WX25CODEUPGRADEDLG,
              name='Wx25CodeUpgradeDlg', parent=prnt, pos=wx.Point(527, 423),
              size=wx.Size(573, 220), style=wx.DEFAULT_DIALOG_STYLE,
              title='Upgrade Boa code to 0.4 style')
        self.SetClientSize(wx.Size(565, 193))
        self.Center(wx.BOTH)

        self.stSourceFolder = wx.StaticText(id=wxID_WX25CODEUPGRADEDLGSTSOURCEFOLDER,
              label='Source Folder:', name='stSourceFolder', parent=self,
              pos=wx.Point(4, 8), size=wx.Size(69, 13), style=0)

        self.sourceFolder = wx.TextCtrl(id=wxID_WX25CODEUPGRADEDLGSOURCEFOLDER,
              name='sourceFolder', parent=self, pos=wx.Point(108, 4),
              size=wx.Size(435, 21), style=0, value='')

        self.targetFolder = wx.TextCtrl(id=wxID_WX25CODEUPGRADEDLGTARGETFOLDER,
              name='targetFolder', parent=self, pos=wx.Point(108, 29),
              size=wx.Size(435, 21), style=0, value='')

        self.stTargetFolder = wx.StaticText(id=wxID_WX25CODEUPGRADEDLGSTTARGETFOLDER,
              label='Target Folder', name='stTargetFolder', parent=self,
              pos=wx.Point(4, 33), size=wx.Size(63, 13), style=0)

        self.stFile = wx.StaticText(id=wxID_WX25CODEUPGRADEDLGSTFILE,
              label='File (individual):', name='stFile', parent=self,
              pos=wx.Point(4, 57), size=wx.Size(100, 13), style=0)

        self.sourceFile = wx.TextCtrl(id=wxID_WX25CODEUPGRADEDLGSOURCEFILE,
              name='sourceFile', parent=self, pos=wx.Point(108, 54),
              size=wx.Size(435, 21), style=0, value='')

        self.staticText1 = wx.StaticText(id=wxID_WX25CODEUPGRADEDLGSTATICTEXT1,
              label='It is strongly recommended NOT to set the "Target Folder" to the same name as "Source Folder"!',
              name='staticText1', parent=self, pos=wx.Point(10, 87),
              size=wx.Size(457, 13), style=0)
        self.staticText1.SetForegroundColour(wx.Colour(255, 0, 0))

        self.setSource = wx.Button(id=wxID_WX25CODEUPGRADEDLGSETSOURCE,
              label='Set Source Folder', name='setSource', parent=self,
              pos=wx.Point(4, 114), size=wx.Size(100, 23), style=0)
        self.setSource.Bind(wx.EVT_BUTTON, self.OnSetSourceButton,
              id=wxID_WX25CODEUPGRADEDLGSETSOURCE)

        self.setTarget = wx.Button(id=wxID_WX25CODEUPGRADEDLGSETTARGET,
              label='Set Target Folder', name='setTarget', parent=self,
              pos=wx.Point(108, 114), size=wx.Size(97, 23), style=0)
        self.setTarget.Bind(wx.EVT_BUTTON, self.OnSetTargetButton,
              id=wxID_WX25CODEUPGRADEDLGSETTARGET)

        self.startFolder = wx.Button(id=wxID_WX25CODEUPGRADEDLGSTARTFOLDER,
              label='Convert Folder', name='start', parent=self,
              pos=wx.Point(209, 114), size=wx.Size(92, 23), style=0)
        self.startFolder.Bind(wx.EVT_BUTTON, self.OnStartFolderButton,
              id=wxID_WX25CODEUPGRADEDLGSTARTFOLDER)

        self.setFile = wx.Button(id=wxID_WX25CODEUPGRADEDLGSETFILE,
              label='Set File name', name='setFile', parent=self,
              pos=wx.Point(4, 141), size=wx.Size(97, 23), style=0)
        self.setFile.Bind(wx.EVT_BUTTON, self.OnSetFileButton,
              id=wxID_WX25CODEUPGRADEDLGSETFILE)

        self.startFile = wx.Button(id=wxID_WX25CODEUPGRADEDLGSTARTFILE,
              label='Convert File', name='startFile', parent=self,
              pos=wx.Point(108, 141), size=wx.Size(92, 23), style=0)
        self.startFile.Bind(wx.EVT_BUTTON, self.OnStartFileButton,
              id=wxID_WX25CODEUPGRADEDLGSTARTFILE)

        self.upgradeGuide = wx.Button(id=wxID_WX25CODEUPGRADEDLGUPGRADEGUIDE,
              label='Upgrade Guide', name='upgradeGuide', parent=self,
              pos=wx.Point(305, 141), size=wx.Size(103, 23), style=0)
        self.upgradeGuide.Bind(wx.EVT_BUTTON, self.OnUpgradeGuideButton,
              id=wxID_WX25CODEUPGRADEDLGUPGRADEGUIDE)

        self.StaticText2 = wx.StaticText(id=wxID_WX25CODEUPGRADEDLGSTATICTEXT2,
              label='The "Upgrade Guide" provides information you should read before using this tool.',
              name='StaticText2', parent=self, pos=wx.Point(2, 178),
              size=wx.Size(438, 13), style=0)

        self._init_sizers()

    def __init__(self, parent, defaultDir):
        self._init_ctrls(parent)
        if '://' in defaultDir:
            if defaultDir.startswith('file://'):
                defaultDir = defaultDir[7:]
            else:
                defaultDir = '.'
        self.defaultDir = self.sourceFolderName = os.path.abspath(defaultDir)
        self.targetFolderName = self.sourceFolderName + 'Upgraded'
        self.sourceFolder.SetValue(self.sourceFolderName)
        self.targetFolder.SetValue(self.targetFolderName)

        self.u = wx25upgrade.Upgrade()
        
    def OnSetSourceButton(self, event):
        dlg = wx.DirDialog(self, defaultPath=self.sourceFolderName,
              style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                self.sourceFolder.SetValue(dir)
                self.targetFolder.SetValue(self.sourceFolder.GetValue()+'Upgraded')
        finally:
            dlg.Destroy()

    def OnSetTargetButton(self, event):
        dlg = wx.DirDialog(self, defaultPath=self.targetFolderName, 
              style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON )
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                self.targetFolder.SetValue(dir)
        finally:
            dlg.Destroy()

    def OnSetFileButton(self, event):
        dlg = wx.FileDialog(self, "Choose a file to convert", self.defaultDir, "", "*.py", wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.sourceFile.SetValue(filename)
        finally:
            dlg.Destroy()

    def OnStartFolderButton(self, event):
        targetFolder = self.targetFolder.GetValue()
        if not os.path.isdir(targetFolder):
            if wx.MessageBox('Target folder does not exist, create it?', 
                  'Create folder', wx.YES_NO | wx.ICON_QUESTION) == wx.NO:
                return
            os.mkdir(targetFolder)
            
        try:
            files = os.listdir(self.sourceFolder.GetValue())
            max = len(files)
            dlg = wx.ProgressDialog("Converting source files",
                                   "Starting conversion of source files",
                                   maximum = max,
                                   parent=self)
    
            keepGoing = True
            count = 0
       
            for name in files:
                count = count +1
                root, ext = os.path.splitext(name)
                if ext == '.py':
                    temp = 'Converting: %s' % name
                    keepGoing = dlg.Update(count, temp)
                    
                    fInputName = os.path.join(self.sourceFolder.GetValue(), name)
                    fInputLines = file(fInputName, 'r').readlines()
                    fInputData = self.reindentSource(fInputLines, fInputName)
                    fOutput = file(os.path.join(self.targetFolder.GetValue(), name), 'w')
                    try:
                        fOutput.write(self.u.upgrade(fInputData))
                    finally:
                        fOutput.close()
                        temp = 'Done converting: %s' % name
                        keepGoing = dlg.Update(count, temp)

            keepGoing = dlg.Update(count, "We are all done")
        finally:
            dlg.Destroy()
        
    def OnStartFileButton(self, event):
        max = 2
        dlg = wx.ProgressDialog("Converting source file",
                               "Starting conversion of source file\n\n",
                               maximum = max,
                               parent=self)
        keepGoing = True
        count = 0

        root, fileName = os.path.split(self.sourceFile.GetValue())
        newName, ext = os.path.splitext(self.sourceFile.GetValue())
        outName = newName+'Upg'+ext
        root2, newFileName = os.path.split(outName)
                
        fInputName = self.sourceFile.GetValue()
        fInputLines = file(fInputName, 'r').readlines()
        fInputData = self.reindentSource(fInputLines, fInputName)

        fOutput = file(outName, 'w')

        temp = 'Converting: %s,\n\nto: %s' % (fileName, newFileName)
        keepGoing = dlg.Update(count, temp)
        
        try:
            fOutput.write(self.u.upgrade(fInputData))
        finally:
            fOutput.close()
            
            count = count +1
            temp = 'Done converting: %s,\n\nto: %s' % (fileName, newFileName)
            keepGoing = dlg.Update(count, temp)
            print 'Converted: %s,\n\nnew name: %s' % (fileName, newFileName)
            count = count +1
            keepGoing = dlg.Update(count, "We are done")
            dlg.Destroy()

    def OnUpgradeGuideButton(self, event):
        import webbrowser
        webbrowser.open('http://wiki.wxpython.org/index.cgi/Boa040Upgrade')

    def reindentSource(self, srcLines, filename):
        data = ''.join(srcLines)
        eol = Utils.getEOLMode(data)
        file = SourcePseudoFile(srcLines)
        ri = reindent.Reindenter(file, eol=eol)
        try:
            if ri.run():
                file.output = []
                ri.write(file)

                return ''.join(file.output)
        except Exception, error:
            print 'Error on reindenting %s : %s'%(filename, str(error))

        return data

class SourcePseudoFile(Utils.PseudoFileOutStore):
    def readlines(self):
        return self.output
    
#-------------------------------------------------------------------------------

def showWx25CodeUpgradeDlg(editor):
    dlg = Wx25CodeUpgradeDlg(editor, editor.getOpenFromHereDir())
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    
import Plugins
Plugins.registerTool('wxPython 2.4 to 2.5/2.6 code upgrader', showWx25CodeUpgradeDlg)
