#-----------------------------------------------------------------------------
# Name:        ConfigSupport.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002/12/03
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.ConfigSupport'

import wx

import Preferences, Utils, Plugins
from Utils import _

import EditorHelper
EditorHelper.imgConfigFileModel = EditorHelper.imgIdxRange()

from Models.EditorModels import SourceModel

class ConfigFileModel(SourceModel):
    modelIdentifier = 'Config'
    defaultName = 'config'
    bitmap = 'Config.png'
    imgIdx = EditorHelper.imgConfigFileModel
    ext = '.cfg'


from Views.StyledTextCtrls import LanguageSTCMix, stcConfigPath
class ConfigSTCMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, (), 'prop', stcConfigPath)
        self.setStyles()


wxID_CONFIGVIEW = wx.NewId()
from Views.SourceViews import EditorStyledTextCtrl
class ConfigView(EditorStyledTextCtrl, ConfigSTCMix):
    viewName = 'Config'
    viewTitle = _('Config')
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_CONFIGVIEW, model, (), -1)
        ConfigSTCMix.__init__(self, wxID_CONFIGVIEW)
        self.active = True


import Controllers
class ConfigFileController(Controllers.SourceController):
    Model           = ConfigFileModel
    DefaultViews    = [ConfigView]

#-------------------------------------------------------------------------------

Plugins.registerFileType(ConfigFileController, aliasExts=('.ini',))
Plugins.registerLanguageSTCStyle('Config', 'prop', ConfigSTCMix, 'stc-styles.rc.cfg')
