#-----------------------------------------------------------------------------
# Name:        XMLSupport.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.XMLSupport'

import wx

import Preferences, Utils, Plugins
from Utils import _

import EditorHelper
EditorHelper.imgXMLFileModel = EditorHelper.imgIdxRange()

from Models.EditorModels import PersistentModel
class XMLFileModel(PersistentModel):
    modelIdentifier = 'XML'
    defaultName = 'xml'
    bitmap = 'WebDocXML.png'
    imgIdx = EditorHelper.imgXMLFileModel
    ext = '.xml'


from Views.StyledTextCtrls import LanguageSTCMix, stcConfigPath
class XMLStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'xml', stcConfigPath)
        self.setStyles()


wxID_XMLSOURCEVIEW = wx.NewId()
from Views.SourceViews import EditorStyledTextCtrl
class XMLSourceView(EditorStyledTextCtrl, XMLStyledTextCtrlMix):
    viewName = 'XML'
    viewTitle = _('XML')

    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_XMLSOURCEVIEW,
          model, (), -1)
        XMLStyledTextCtrlMix.__init__(self, wxID_XMLSOURCEVIEW)
        self.active = True


import Controllers
class XMLFileController(Controllers.PersistentController):
    Model           = XMLFileModel
    DefaultViews    = [XMLSourceView]
    try:
        from Views.XMLView import XMLTreeView
        AdditionalViews = [XMLTreeView]
    except ImportError:
        AdditionalViews = []

#-------------------------------------------------------------------------------

Plugins.registerFileType(XMLFileController, aliasExts=('.dtd', '.xrc'))
Plugins.registerLanguageSTCStyle('XML', 'xml', XMLStyledTextCtrlMix, 'stc-styles.rc.cfg')
