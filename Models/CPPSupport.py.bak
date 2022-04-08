#-----------------------------------------------------------------------------
# Name:        CPPSupport.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.CPPSupport'

import os

import wx

import Preferences, Utils, Plugins
from Utils import _

import EditorHelper
EditorHelper.imgCPPModel = EditorHelper.imgIdxRange()

from Models.EditorModels import SourceModel
class CPPModel(SourceModel):
    modelIdentifier = 'CPP'
    defaultName = 'cpp'
    bitmap = 'Cpp.png'
    imgIdx = EditorHelper.imgCPPModel
    ext = '.cxx'

    def __init__(self, data, name, editor, saved):
        SourceModel.__init__(self, data, name, editor, saved)
        self.loadHeader()
        if data: self.update()

    def loadHeader(self):
        header = os.path.splitext(self.filename)[0]+'.h'
        if os.path.exists(header):
            # This should open a BasicFileModel instead of a file directly
            self.headerData = open(header).read()
        else:
            self.headerData = ''

    def load(self, notify=True):
        SourceModel.load(self, False)
        self.loadHeader()
        self.update()
        if notify: self.notify()


from Views.StyledTextCtrls import LanguageSTCMix, FoldingStyledTextCtrlMix, stcConfigPath
class CPPStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'cpp', stcConfigPath)
        self.setStyles()


wxID_CPPSOURCEVIEW = wx.NewId()
symbolFolding = 1
from Views.SourceViews import EditorStyledTextCtrl
class CPPSourceView(EditorStyledTextCtrl, CPPStyledTextCtrlMix, FoldingStyledTextCtrlMix):
    viewName = 'Source'
    viewTitle = _('Title')
    
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_CPPSOURCEVIEW,
          model, (), -1)
        CPPStyledTextCtrlMix.__init__(self, wxID_CPPSOURCEVIEW)
        FoldingStyledTextCtrlMix.__init__(self, wxID_CPPSOURCEVIEW, symbolFolding)
        self.active = True

    def OnMarginClick(self, event):
        FoldingStyledTextCtrlMix.OnMarginClick(self, event)


class HPPSourceView(CPPSourceView):
    viewName = 'Header'
    viewTitle = _('Header')

    def __init__(self, parent, model):
        CPPSourceView.__init__(self, parent, model)

    def refreshCtrl(self):
        self.pos = self.GetCurrentPos()
        prevVsblLn = self.GetFirstVisibleLine()

        self.SetText(self.model.headerData)
        self.EmptyUndoBuffer()
        self.GotoPos(self.pos)
        curVsblLn = self.GetFirstVisibleLine()
        self.LineScroll(0, prevVsblLn - curVsblLn)

        self.nonUserModification = False
        self.updatePageName()

import Controllers
class CPPController(Controllers.SourceController):
    Model           = CPPModel
    DefaultViews    = [CPPSourceView, HPPSourceView]


#-------------------------------------------------------------------------------

Plugins.registerFileType(CPPController, newName='Cpp',
                         aliasExts=('.cpp','.c','.h'))
Plugins.registerLanguageSTCStyle('CPP', 'cpp', CPPStyledTextCtrlMix, 'stc-styles.rc.cfg')
