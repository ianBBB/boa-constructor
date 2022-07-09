#-----------------------------------------------------------------------------
# Name:        CodeTemplates.plug-in.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2006
# RCS-ID:      $Id$
# Copyright:   (c) 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:CodeTemplateManagerDlg

import wx
import wx.stc

import os, glob, ConfigParser

import Preferences, Utils, Plugins
from Utils import _

[wxID_CODETEMPLATEMANAGERDLG] = [wx.NewId() for _init_ctrls in range(1)]

class CodeTemplateManagerDlg(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_CODETEMPLATEMANAGERDLG,
              name='CodeTemplateManagerDlg', parent=prnt, pos=wx.Point(639,
              363), size=wx.Size(349, 324), style=wx.DEFAULT_DIALOG_STYLE,
              title=_('Code Template Manager'))
        self.SetClientSize(wx.Size(341, 297))
        self.Center(wx.BOTH)

    def __init__(self, parent):
        self._init_ctrls(parent)

def showCodeTemplateManagerDlg(editor):
    dlg = CodeTemplateManagerDlg(editor)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()

#-------------------------------------------------------------------------------

Preferences.keyDefs['CodeTemplates'] = (wx.ACCEL_ALT, ord('T'), 'Alt-T')

codeTemplatesUserListType = 1

class CodeTemplateManager:
    """ Reads all Plug-ins/CodeTemplates/*.cfg files and publishes their templates """
    def __init__(self):
        self.readTemplates()
    
    def readTemplates(self):
        files = []
        for path in Preferences.pluginPaths:
            cp = os.path.join(path, 'CodeTemplates')
            if os.path.exists(cp):
                files.extend([os.path.join(cp, f) 
                              for f in glob.glob(os.path.join(cp, '*.cfg'))])

        self.conf = ConfigParser.SafeConfigParser()
        self.conf.read(files)
    
    def getNames(self, language):
        names = self.conf.sections()
        names = [name for name in names 
                 if self.conf.get(name, 'language') in (language, 'any')]
        names.sort()
        return names
    
    def getTemplate(self, name):
        if self.conf.has_section(name):
            return self.conf.get(name, 'template')
        raise Exception, _('Code Template: %s not found')%name

codeTemplateManager = CodeTemplateManager()


class CodeTemplatesViewPlugin:
    """ Provides access to Code Templates to insert in a Source View """
    def __init__(self, model, view, actions):
        self.model = model
        self.view = view
        actions.append( (_('Code Templates'), self.OnCodeTemplates, '-', 'CodeTemplates') )
        self.view.Bind(wx.stc.EVT_STC_USERLISTSELECTION, self.OnCodeTemplateSelected)

    def OnCodeTemplates(self, event):
        names = codeTemplateManager.getNames(self.view.language)
        self.view.UserListShow(codeTemplatesUserListType, ' '.join(names))

    def OnCodeTemplateSelected(self, event):
        if event.GetListType() == codeTemplatesUserListType:
            idnt = Utils.getIndentBlock()
            self.view.insertCodeBlock(codeTemplateManager.getTemplate(
                  event.GetText()).replace('\\t', idnt))
        event.Skip()
            

from Views import SourceViews
SourceViews.EditorStyledTextCtrl.plugins += (CodeTemplatesViewPlugin,)

# Tools dialog not useful yet
#Plugins.registerTool(_('Code Template Manager'), showCodeTemplateManagerDlg)
