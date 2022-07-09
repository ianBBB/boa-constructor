#-----------------------------------------------------------------------------
# Name:        HTMLSupport.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.HTMLSupport'

import wx

import Preferences, Utils, Plugins
from Utils import _

import EditorHelper
EditorHelper.imgHTMLFileModel = EditorHelper.imgIdxRange()

from Models.EditorModels import PersistentModel

class HTMLFileModel(PersistentModel):
    modelIdentifier = 'HTML'
    defaultName = 'html'
    bitmap = 'WebDocHTML.png'
    imgIdx = EditorHelper.imgHTMLFileModel
    ext = '.html'


from Views.StyledTextCtrls import LanguageSTCMix, stcConfigPath
class BaseHTMLStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'html', stcConfigPath)


class HTMLStyledTextCtrlMix(BaseHTMLStyledTextCtrlMix):
    def __init__(self, wId):
        BaseHTMLStyledTextCtrlMix.__init__(self, wId)
        self.setStyles()


wxID_HTMLSOURCEVIEW = wx.NewId()
from Views.SourceViews import EditorStyledTextCtrl
class HTMLSourceView(EditorStyledTextCtrl, HTMLStyledTextCtrlMix):
    viewName = 'HTML'
    viewTitle = _('HTML')
    
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_HTMLSOURCEVIEW,
          model, (), -1)
        HTMLStyledTextCtrlMix.__init__(self, wxID_HTMLSOURCEVIEW)
        self.active = True


import Controllers
from Views.EditorViews import HTMLFileView
class HTMLFileController(Controllers.PersistentController):
    Model           = HTMLFileModel
    DefaultViews    = [HTMLSourceView]
    AdditionalViews = [HTMLFileView]

#-------------------------------------------------------------------------------

Plugins.registerFileType(HTMLFileController, aliasExts=('.htm',))
Plugins.registerLanguageSTCStyle('HTML', 'html', BaseHTMLStyledTextCtrlMix, 'stc-styles.rc.cfg')
