#-----------------------------------------------------------------------------
# Name:        PascalSupport.py
# Purpose:     Example plugin module showing how to add new filetypes to the ide
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

import os

import wx
import wx.stc

import Preferences, Utils, Plugins
from Utils import _

import PaletteStore

from Models import Controllers, EditorHelper, EditorModels
from Views import SourceViews, StyledTextCtrls
from Explorers import ExplorerNodes

# Allocate an image index for Pascal files
EditorHelper.imgPascalModel = EditorHelper.imgIdxRange()

# Register plug-in preference
Plugins.registerPreference('PascalSupport', 'psPascalCompilerPath', "''",
                           ['Path to the compiler'], 'type: filepath')

class PascalModel(EditorModels.SourceModel):
    modelIdentifier = 'Pascal'
    defaultName = 'pascal'  # default name given to newly created files
    bitmap = 'Pascal.png' # this image must exist in Images/Modules
    ext = '.pas'
    imgIdx = EditorHelper.imgPascalModel

# get the style definitions file in either the prefs directory or the Boa root
pascal_cfgfile = Preferences.rcPath +'/stc-pascal.rc.cfg'

class PascalStyledTextCtrlMix(StyledTextCtrls.LanguageSTCMix):
    def __init__(self, wId):
        StyledTextCtrls.LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'pascal', pascal_cfgfile)
        self.setStyles()

wxID_PASSOURCEVIEW = wx.NewIdRef(count=1)
class PascalSourceView(SourceViews.EditorStyledTextCtrl, PascalStyledTextCtrlMix):
    viewName = 'Source'
    viewTitle = _('Source')
    def __init__(self, parent, model):
        SourceViews.EditorStyledTextCtrl.__init__(self, parent, wxID_PASSOURCEVIEW,
          model, (), -1)
        PascalStyledTextCtrlMix.__init__(self, wxID_PASSOURCEVIEW)
        self.active = True

# Register a Pascal STC style editor under Preferences
Plugins.registerLanguageSTCStyle('Pascal', 'pascal', PascalStyledTextCtrlMix, pascal_cfgfile)

# The compile action is just added as an example of how to add an action to
# a controller and is not implemented
wxID_PASCALCOMPILE = wx.NewIdRef(count=1)
class PascalController(Controllers.SourceController):
    Model = PascalModel
    DefaultViews = [PascalSourceView]

    compileBmp = 'Images/Debug/Compile.png'

    def actions(self, model):
        return Controllers.SourceController.actions(self, model) + [
              (_('Compile'), self.OnCompile, '-', 'CheckSource')]

    def OnCompile(self, event):
        wx.LogWarning(_('Not implemented'))

#-------------------------------------------------------------------------------
# Registers the filetype in the IDE framework
Plugins.registerFileType(PascalController, aliasExts=('.dpr',))

#-------------------------------------------------------------------------------
# Config file embedded in plug-in

pascalSource = '''unit Unit1;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  StdCtrls;

type
  TForm1 = class(TForm)
    Button1: TButton;
    procedure Button1Click(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

implementation

{$R *.DFM}

procedure TForm1.Button1Click(Sender: TObject);
const
  a = 10;
var
  b : String;
begin
  b := 'String'
end;

end.
'''

pascalStyleEditorConfig = '''
common.defs.msw={'size': 10, 'backcol': '#FFFFFF', 'lnsize2': 7, 'mono': 'Courier New', 'lnsize': 8, 'helv': 'Lucida Console'}
common.defs.gtk={'mono': 'Courier', 'helv': 'Helvetica', 'other': 'new century schoolbook', 'size': 9, 'lnsize': 6, 'backcol': '#FFFFFF'}
common.styleidnames = {wx.stc.STC_STYLE_DEFAULT: 'Style default', wx.stc.STC_STYLE_LINENUMBER: 'Line numbers', wx.stc.STC_STYLE_BRACELIGHT: 'Matched braces', wx.stc.STC_STYLE_BRACEBAD: 'Unmatched brace', wx.stc.STC_STYLE_CONTROLCHAR: 'Control characters', wx.stc.STC_STYLE_INDENTGUIDE: 'Indent guide'}

[style.pascal]
setting.pascal.-3=fore:#8080FF
setting.pascal.-2=
setting.pascal.-1=
style.pascal.000=
style.pascal.001=fore:#008040,back:#EAFFEA
style.pascal.002=fore:#008040,back:#EAFFEA,size:%(size)d
style.pascal.003=
style.pascal.004=fore:#0076AE
style.pascal.005=bold,fore:#004080
style.pascal.006=fore:#800080
style.pascal.007=fore:#800040
style.pascal.008=
style.pascal.009=fore:#808000
style.pascal.010=bold
style.pascal.011=
style.pascal.012=back:#FFD5FF
style.pascal.013=fore:#8000FF
style.pascal.032=face:%(mono)s,size:%(size)d
style.pascal.033=size:%(lnsize)s
style.pascal.034=fore:#0000FF,back:#FFFFB9,bold
style.pascal.035=fore:#FF0000,back:#FFFFB9,bold
style.pascal.036=
style.pascal.037=

[style.pascal.default]

[pascal]
displaysrc='''+`pascalSource`[1:-1]+'''
braces={}
keywords=and array as asm begin case class const constructor destructor dispinterface div do downto else end except exports file finalization finally for function goto if implementation in inherited initialization inline interface is label library mod nil not object of or out packed procedure program property raise record repeat resourcestring set shl shr string then threadvar to try type unit until uses var while with xor private protected public published automated at on
lexer=wx.stc.STC_LEX_PASCAL
styleidnames={wx.stc.STC_C_DEFAULT: 'Default', wx.stc.STC_C_COMMENT: 'Comment',wx.stc.STC_C_COMMENTLINE: 'Comment line',wx.stc.STC_C_COMMENTDOC: 'Comment doc',wx.stc.STC_C_NUMBER: 'Number',wx.stc.STC_C_WORD: 'Keyword',wx.stc.STC_C_STRING: 'String',wx.stc.STC_C_CHARACTER: 'Character',wx.stc.STC_C_PREPROCESSOR: 'Preprocessor',wx.stc.STC_C_OPERATOR: 'Operator', wx.stc.STC_C_IDENTIFIER: 'Identifier', wx.stc.STC_C_STRINGEOL: 'EOL unclosed string'}
'''

Plugins.assureConfigFile(pascal_cfgfile, pascalStyleEditorConfig)

#-------------------------------------------------------------------------------

def getPascalPaletteData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\
\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x01!IDATx\x9c\xe5\x95\xbfJ\x03A\x10\x87\xbf\x13\x0b\xaf\x9b\xbc\x81W\x08ny\
\x01!\xed\x1d\xf8\x08\xbe\x88\xa49\x02V\x82p\xc4GH%\xd8%>\x80\x10\xbbX\xda\n\
)\xd62\xddM\x17\xbb\xb5\xc8\xa9hq\xb7\xcby\xa08\xcd\xb23\xcb\xef\x9b?\xecn$"\
\xf4i{\xbd\xaa\xffO\x80Qu\xbd\x01\x8c\xaa[\x85\xe5\xe3\x0f\x98\xab\xbaU\x01\
\x8c\xc2\xaa\xf0\x02\xcc\x8f\xd5\xe5\xef\x9b\x0c.G\xbe\xf2\x1e\x00\xa3\xea\
\xf2\x0c(>}y\xb6\xab\xe8G\x00\x1f\x99?\x00\xa7\xc0\xd57\x7f\x8bE>7\xb9Ru\x14\
5$\xabW`\xf0,Q\'\xc0@\x06.M\x85\x84\x84\xa7\xbb\xc5\x97X\x9e\xe5\xcc\xec\x92\
J\x9b!\xfbM\xc1\xc9\xc5\x04\xb0\xc4\x071\xc3\xb3!\xf6\xc5\x02`\xd7 \'\x02\
\xa5\x05\xaa\xc6\n\x1ag0>\x1fG\x9bM\xcc\xf6u[{\x12\xec\x1a\x92#\xcbu\xb9\xa0\
\xd2\xaa\xb5E\xadC\x9e\x96\xd3\xe8\xf6\xe6\x11c\x0c\xc9\xe1N|y\x8f\x97\xb8\
\x17\x00@D\x10I\x01\xebs<\x1c\xa0\xaa\xc1\xc2A\x80\xaa\xc3\xa7\xf4\xfb\x9e\
\xebP\xf3\xba\xc9]\xec\xef\xb7\xa8w\xc0\x1b@\xbfT\xe9_od\x9f\x00\x00\x00\x00\
IEND\xaeB`\x82'

def getPascalModuleData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\x0eIDATx\x9c\xa5\x93\xbfJ\xc4@\x10\x87\xbf\x88\x85\xe9&o`\n\xc1\x94\
9\x10\xae\xdd\x80\x8f\xe0\x8b\xc85\xe1\xc0J\x10\xc2\xf9\x08V\x82\xdd\x9d\x0f\
 \x9c\xddYZ*\\\xb1\x96\xd7\xedtg\xb7\x16\x89\x7fr\x89\x89\xc1i\x96\xf9\r\xbf\
ogg\xd8@D\xe8\x8aD\xd5\xbf\x88\x04\xbf\xd5\xf7\xfa\xcc\xabN|\x07`\xae\xeaW90\
.A\x83\x00\xf3c\xf5\xd9gb\xe0r<\xa0\x83D\xd5g\x06\xc8\xbf\xb5\xcc\x94\x1d\
\xfd\t\xf0u\xf3#p\n\\\xed\xe8;\x11\xb4m\xc1\xa9z\xf2\nb\xaa\x13\x88^\x9b\xdb\
\xa8\x01"\x89|\x9a\n11\xcf\xf7\x8bzg&\xe3\xc6.qZ\x87\xec\xffL\xa6\x17S\xc0\
\x12\x1e\x84\x8c\xceF\xd87\x0b\x80]\x83\x9c\x08\x14\x16p5pm\x06\x93\xf3I\xb0\
\xd9\x84l\xdf\xb7\x95\x12c\xd7\x10\x1fY\xae\x8b\x05N]\xe3\t\x8d!\xce\x8aYpw\
\xfbD\x92$\xc4\x87\xa5y\xf9@\xab\xb9\x15\x00 "\x88\xa4\x80m+\xf7\x03T\xb5\
\xd7\xd8\tp=\x1f\xac\x170$\xfe\r\xf8\x00P\xd5U\xa2\xb4=\x18n\x00\x00\x00\x00\
IEND\xaeB`\x82'

Preferences.IS.registerImage('Images/Modules/Pascal.png', getPascalModuleData())
Preferences.IS.registerImage('Images/Palette/Pascal.png', getPascalPaletteData())
