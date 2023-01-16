#-----------------------------------------------------------------------------
# Name:        ResourceSupport.py
# Purpose:     Management of modules that contain functions to create images
#
# Author:      Riaan Booysen
#
# Created:     2003/07/27
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ResourceSelectDlg

import string, sys

import wx
from wx.tools import img2py
# import wx.lib.art.myimagemodule
import wx.lib.art.img2pyartprov
from wx.lib.anchors import LayoutAnchors

from Utils import _

[wxID_RESOURCESELECTDLG, wxID_RESOURCESELECTDLGBTNCANCEL, 
 wxID_RESOURCESELECTDLGBTNFILEDLG, wxID_RESOURCESELECTDLGBTNOK, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(4)]

class ResourceSelectDlg(wx.Dialog):
    def _init_coll_boxSizerButtons_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.btnOK, 0, border=15,
              flag=wx.BOTTOM | wx.TOP | wx.LEFT | wx.ALIGN_RIGHT)
        parent.AddWindow(self.btnCancel, 0, border=15,
              flag=wx.BOTTOM | wx.TOP | wx.LEFT | wx.ALIGN_RIGHT)
        parent.AddWindow(self.btnFileDlg, 0, border=15,
              flag=wx.BOTTOM | wx.TOP | wx.LEFT | wx.ALIGN_RIGHT)

    def _init_coll_boxSizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.boxSizerButtons, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizerMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizerButtons = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_boxSizerMain_Items(self.boxSizerMain)
        self._init_coll_boxSizerButtons_Items(self.boxSizerButtons)

        self.SetSizer(self.boxSizerMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_RESOURCESELECTDLG,
              name='ResourceSelectDlg', parent=prnt, pos=wx.Point(384, 293),
              size=wx.Size(307, 359),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('Select Resource'))
        self.SetClientSize(wx.Size(299, 332))

        self.btnOK = wx.Button(id=wx.ID_OK, label=_('OK'), name='btnOK',
              parent=self, pos=wx.Point(15, 15), size=wx.Size(75, 23), style=0)

        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='btnCancel', parent=self, pos=wx.Point(105, 15),
              size=wx.Size(75, 23), style=0)

        self.btnFileDlg = wx.Button(id=wxID_RESOURCESELECTDLGBTNFILEDLG,
              label=_('File Dialog...'), name='btnFileDlg', parent=self,
              pos=wx.Point(195, 15), size=wx.Size(75, 23), style=0)
        self.btnFileDlg.Bind(wx.EVT_BUTTON, self.OnBtnfiledlgButton,
              id=wxID_RESOURCESELECTDLGBTNFILEDLG)

        self._init_sizers()

    def __init__(self, parent, editor, resourceFilename, imageName='',
          onlyIcons=False):
        self._init_ctrls(parent)

        from Explorers import Explorer

        model = PyResourceBitmapModel('', resourceFilename, editor, True)
        model.transport = Explorer.openEx(resourceFilename)
        model.load(notify=False)
        self.resources = PyResourceImagesSelectionView(self, model,
              listStyle=wx.LC_SMALL_ICON | wx.LC_ALIGN_TOP,
              imgLstStyle=wx.IMAGE_LIST_SMALL)
        self.resources.onlyIcons = onlyIcons

        self.boxSizerMain.Prepend(self.resources, 1,
                                  wx.LEFT|wx.RIGHT|wx.TOP|wx.GROW, 15)
        self.resources.refreshCtrl()

        if imageName:
            sel = -1
            for idx, r in zip(list(range(len(self.resources.imageSrcInfo))),
                              self.resources.imageSrcInfo):
                if r[0] == imageName:
                    sel = idx
                    break

            if sel != -1:
                self.resources.Select(sel)
                self.resources.EnsureVisible(sel)

        self.resources.SetFocus()

    def OnBtnfiledlgButton(self, event):
        self.EndModal(wx.ID_YES)


#-------------------------------------------------------------------------------

import os
from io import StringIO

import Preferences, Utils

from Views import EditorViews
from Models import EditorHelper, Controllers, PythonEditorModels, PythonControllers

class PyResourceModuleExec:
    def __init__(self, pyResImgSrc):
        self.imageFunctions = {}
        src = Utils.toUnixEOLMode(pyResImgSrc)+'\n\n'
        exec(src, self.imageFunctions)

class PyResourceArtProvider(wx.ArtProvider):
    def __init__(self, pyResModExec):
        wx.ArtProvider.__init__(self)
        self.imageFunctions = pyResModExec.imageFunctions

    def CreateBitmap(self, artid, client, size):
        return self.imageFunctions[artid]()

extTypeMap = {'.bmp': wx.BITMAP_TYPE_BMP,
              '.gif': wx.BITMAP_TYPE_GIF,
              '.jpg': wx.BITMAP_TYPE_JPEG,
              '.png': wx.BITMAP_TYPE_PNG}

class PyResourceImagesView(EditorViews.ListCtrlView):
    viewName = 'Images'
    viewTitle = _('Images')

    gotoLineBmp = 'Images/Editor/GotoLine.png'
    moveUpBmp = 'Images/Shared/up.png'
    moveDownBmp = 'Images/Shared/down.png'
    deleteBmp = 'Images/Shared/Delete.png'

    imageSize = (32, 32)

    onlyIcons = False

    def __init__(self, parent, model, listStyle=wx.LC_ICON | wx.LC_ALIGN_TOP,
                                      imgLstStyle=wx.IMAGE_LIST_NORMAL):
        EditorViews.ListCtrlView.__init__(self, parent, model, listStyle,
          ((_('Goto line'), self.OnGoto, self.gotoLineBmp, ''), 
#           ('Move up', self.OnMoveUp, self.moveUpBmp, ''), 
#           ('Move down', self.OnMoveDown, self.moveDownBmp, ''), 
#           ('Delete image', self.OnDeleteImage, self.deleteBmp, ''), 
##           ('Add image', self.OnAddImage, '-', ''),
#           ('Export image', self.OnExportImage, '-', ''), 
           ), 0)

        self.images = wx.ImageList(*self.imageSize)
        self.AssignImageList(self.images, imgLstStyle)

        self.imageSrcInfo = []
        self.functions = None
        self.cataloged = False
        self.eol = os.linesep

        self.active = True

    def refreshCtrl(self):
        EditorViews.ListCtrlView.refreshCtrl(self)

        self.functions = PyResourceModuleExec(self.model.data)
        self.imageSrcInfo = []
        self.images.RemoveAll()
        artProv = PyResourceArtProvider(self.functions)
        # wx.ArtProvider.PushProvider(artProv)
        wx.ArtProvider.Push(artProv)
        try:
            m = self.model.getModule()
            self.cataloged = ('catalog' in m.globals) and ('index' in m.globals)
            self.eol = m.eol
            for f in m.function_order:
                if f.startswith('get') and f.endswith('Data'):
                    name = f[3:-4]
                    iconFunction = 'get%sIcon'%name in m.functions
                    if self.onlyIcons and not iconFunction:
                        continue
                    bmpFunctionStart = m.functions['get%sBitmap'%name].start
                    firstDataLine = m.source[m.functions['get%sData'%name].start]
                    compressed = firstDataLine.strip().startswith('return zlib.decompress')
                    bmp = wx.ArtProvider.GetBitmap('get%sBitmap'%name, size=self.imageSize)
                    idx = self.images.Add(bmp)
                    self.InsertImageStringItem(idx, name, idx)
                    self.imageSrcInfo.append(
                        (name, (m.functions[f].start, bmpFunctionStart),
                         compressed, iconFunction) )
        finally:
            wx.ArtProvider.Pop()

    def OnGoto(self, event):
        if self.selected != -1:
            srcView = self.model.getSourceView()
            srcView.focus()
            lineNo = self.imageSrcInfo[self.selected][1][0]
            srcView.gotoLine(lineNo-1)

##    def OnAddImage(self, event):
##        from Explorers.Explorer import openEx
##        fn = self.model.editor.openFileDlg(filter='*.*', curdir='.')
##        if fn.find('://') != -1:
##            fn = fn.split('://', 1)[1]
##        ConvertImgToPy
        
##        dlg =wx.DirDialog(self.model.editor)
##        try:
##            if dlg.ShowModal() != wx.ID_OK:
##                return
##            dir = dlg.GetPath()
##            res = []
##            os.path.walk(dir, visitor, res)
##        finally:
##            dlg.Destroy()
##
##def visitor(files, dirname, names):
##    for name in names:
##        filename = os.path.join(dirname, name)
##        if os.path.isfile(filename):
##            files.append(filename)

    def OnExportImage(self, event):
        if self.selected != -1:
            name = self.imageSrcInfo[self.selected][0]
            dlg = wx.FileDialog(self, 'Save image', '.', name+'.png', 
                  ';'.join(['*%s'%e for e in extTypeMap]), wx.SAVE)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    ext = os.path.splitext(path)[-1].lower()
                    if ext in extTypeMap:
                        func = self.functions.imageFunctions['get%sBitmap'%name]()
                        func.SaveFile(path, extTypeMap[ext])
                    else:
                        wx.LogError(_('Unsupported image type: %s')%ext)
            finally:
                dlg.Destroy()

    def OnMoveUp(self, event):
        pass

    def OnMoveDown(self, event):
        pass

    def OnDeleteImage(self, event):
        pass
            

class PyResourceImagesSelectionView(PyResourceImagesView):
    docked = False
    imageSize = (16, 16)
    def OnGoto(self, event):
        if self.selected != -1:
            self.GetParent().EndModal(wx.ID_OK)

class PyResourceBitmapModel(PythonEditorModels.ModuleModel):
    modelIdentifier = 'PyImgResource'
    bitmap = 'PyResBitmap.png'
    imgIdx = EditorHelper.imgPyResBitmap = EditorHelper.imgIdxRange()

    def updateData(self, data, subImage):
        from wxCompat import crunch_data
        crunched = StringIO(crunch_data(data, subImage['zip'])).readlines()
        if subImage['zip']:
            crunched[-1].rstrip()
            crunched[-1] += ' )'+subImage['eol']
        srcLines = self.getDataAsLines()
        srcLines[subImage['start']:subImage['end']] = crunched + [subImage['eol']]

        self.setDataFromLines(srcLines)
        self.modified = True

        subImage['data'] = data

class PyResourceBitmapController(PythonControllers.ModuleController):
    Model = PyResourceBitmapModel
    DefaultViews    = PythonControllers.ModuleController.DefaultViews + \
                      [PyResourceImagesView]


validFuncChars = string.ascii_letters+string.digits+'_'
funcCharMap = {'-': '_', '.': '_'}
def fileNameToFunctionName(fn):
    res = []
    if fn and fn[0] in string.ascii_letters+'_':
        res.append(fn[0])
    for c in fn[1:]:
        if c not in validFuncChars:
            if c in funcCharMap:
                res.append(funcCharMap[c])
        else:
            res.append(c)
    return ''.join(res)

zopt = '-u '
def ConvertImgToPy(imgPath, editor):
    funcName = fileNameToFunctionName(os.path.basename(os.path.splitext(imgPath)[0]))
    pyResPath, ok = editor.saveAsDlg(funcName+'_img.py')
    if ok:
        if pyResPath.find('://') != -1:
            pyResPath = pyResPath.split('://', 1)[1]

        # snip script usage, leave only options
        docs = img2py.__doc__[img2py.__doc__.find('Options:')+11:]

        cmdLine = zopt+'-n %s'%(funcName)
        if os.path.exists(pyResPath):
            cmdLine = '-a ' + cmdLine

        dlg = wx.TextEntryDialog(editor,
              _('Options:\n\n%s\n\nEdit options string:')%docs, 'img2py', cmdLine)
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            cmdLine = dlg.GetValue().strip()
        finally:
            dlg.Destroy()

        opts = cmdLine.split()
        opts.extend([imgPath, pyResPath])

        tmp = sys.argv[0]
        sys.argv[0] = 'Boa Constructor'
        try:
            img2py.main(opts)
        finally:
            sys.argv[0] = tmp

        import sourceconst
        header = (sourceconst.defSig%{'modelIdent':'PyImgResource', 'main':''}).strip()
        if os.path.exists(pyResPath):
            src = open(pyResPath, 'r').readlines()
            if not (src and src[0].startswith(header)):
                src.insert(0, header+'\n')
                src.insert(1, '\n')
                open(pyResPath, 'w').writelines(src)
    
            m, c = editor.openOrGotoModule(pyResPath)
            c.OnReload(None)
        else:
            wx.LogWarning(_('Resource module not found. img2py failed to create the module'))

#-------------------------------------------------------------------------------

import Plugins

Plugins.registerFileType(PyResourceBitmapController, addToNew=False)

Controllers.resourceClasses.append(PyResourceBitmapModel)

EditorHelper.imageExtReg.append('.py')
if not '.py' in EditorHelper.imageSubTypeExtReg:
    EditorHelper.imageSubTypeExtReg['.py'] = []
EditorHelper.imageSubTypeExtReg['.py'].append(PyResourceBitmapModel)
