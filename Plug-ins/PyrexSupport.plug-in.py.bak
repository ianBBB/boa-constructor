#-----------------------------------------------------------------------------
# Name:        PyrexSupport.py
# Purpose:     Support for editing pyrex files and compiling to C
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

import os, imp

import wx
import wx.stc

import Preferences, Utils, Plugins
from Utils import _

try:
    imp.find_module('Pyrex')
except ImportError:
    raise Plugins.SkipPlugin, _('Pyrex is not installed')

from Models import Controllers, EditorHelper, EditorModels, PythonEditorModels, PythonControllers
from Views import SourceViews, StyledTextCtrls

EditorHelper.imgPyrexModel = EditorHelper.imgIdxRange()

class PyrexModel(EditorModels.SourceModel):
    modelIdentifier = 'Pyrex'
    defaultName = 'pyrex'
    bitmap = 'Pyrex.png'
    ext = '.pyx'
    imgIdx = EditorHelper.imgPyrexModel

pyrex_cfgfile = os.path.join(Preferences.rcPath, 'stc-pyrex.rc.cfg')
#if not os.path.exists(pyrex_cfgfile):
#    pyrex_cfgfile = Preferences.pyPath +'/Plug-ins/stc-pyrex.rc.cfg'

class PyrexStyledTextCtrlMix(StyledTextCtrls.LanguageSTCMix):
    def __init__(self, wId):
        StyledTextCtrls.LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'pyrex', pyrex_cfgfile)
        self.setStyles()

wxID_PYREXSOURCEVIEW = wx.NewId()
class PyrexSourceView(SourceViews.EditorStyledTextCtrl, PyrexStyledTextCtrlMix):
    viewName = 'Source'
    viewTitle = _('Source')
    def __init__(self, parent, model):
        SourceViews.EditorStyledTextCtrl.__init__(self, parent,
              wxID_PYREXSOURCEVIEW, model, (), -1)
        PyrexStyledTextCtrlMix.__init__(self, wxID_PYREXSOURCEVIEW)
        self.active = True


#wxID_PYREXCOMPILE = wx.NewId()
class PyrexController(Controllers.SourceController):
    Model = PyrexModel
    DefaultViews = [PyrexSourceView]

    compileBmp = 'Images/Debug/Compile.png'

    def actions(self, model):
        return Controllers.SourceController.actions(self, model) + [
              ('Compile', self.OnCompile, '-', 'CheckSource')]

    def OnCompile(self, event):
        from Pyrex.Compiler import Main, Errors

        model = self.getModel()
        try:
            result = Main.compile(model.localFilename(), c_only=1)
        except Errors.PyrexError, err:
            wx.LogError(str(err))
            msg = 'Error'
        else:
            msg = 'Info'

        if msg == 'Error' or result.num_errors > 0:
            model.editor.setStatus('Pyrex compilation failed', 'Error')
        else:
            model.editor.setStatus('Pyrex compilation succeeded')


#-------------------------------------------------------------------------------

Plugins.registerFileType(PyrexController)
Plugins.registerLanguageSTCStyle('Pyrex', 'pyrex', PyrexStyledTextCtrlMix, pyrex_cfgfile)

#-------------------------------------------------------------------------------

pyrexSource = '''## Comment Blocks!
cdef extern from "Numeric/arrayobject.h":

  struct PyArray_Descr:
    int type_num, elsize
    char type
  ctypedef class PyArrayObject [type PyArray_Type]:
    cdef char *data
    cdef int nd
    cdef int *dimensions, *strides
    cdef object base
    cdef PyArray_Descr *descr
    cdef int flags
'''

pyrexStyleEditorConfig = '''
common.defs.msw={'size': 10, 'backcol': '#FFFFFF', 'lnsize2': 7, 'mono': 'Courier New', 'lnsize': 8, 'helv': 'Lucida Console', 'ln-font': 'Lucida Console', 'ln-size': 8}
common.defs.gtk={'mono': 'Courier', 'helv': 'Helvetica', 'other': 'new century schoolbook', 'size': 9, 'lnsize': 6, 'backcol': '#FFFFFF', 'ln-font': 'Lucida Console', 'ln-size': 8}
common.styleidnames = {wx.stc.STC_STYLE_DEFAULT: 'Style default', wx.stc.STC_STYLE_LINENUMBER: 'Line numbers', wx.stc.STC_STYLE_BRACELIGHT: 'Matched braces', wx.stc.STC_STYLE_BRACEBAD: 'Unmatched brace', wx.stc.STC_STYLE_CONTROLCHAR: 'Control characters', wx.stc.STC_STYLE_INDENTGUIDE: 'Indent guide'}

[style.pyrex]
setting.pyrex.-3=
setting.pyrex.-2=fore:#000000
setting.pyrex.-1=fore:#000000,back:#88C4FF
style.pyrex.000=fore:#808080
style.pyrex.001=fore:#007F00,back:#E8FFE8
style.pyrex.002=fore:#007F7F
style.pyrex.003=fore:#7F007F
style.pyrex.004=fore:#7F007F
style.pyrex.005=fore:#00007F,bold
style.pyrex.006=fore:#7F0000
style.pyrex.007=fore:#000033,back:#FFFFE8
style.pyrex.008=fore:#0000FF,bold
style.pyrex.009=fore:#007F7F,bold
style.pyrex.010=bold
style.pyrex.011=
style.pyrex.012=fore:#7F7F7F
style.pyrex.013=fore:#000000,back:#ECD7EC,eolfilled
style.pyrex.032=back:%(backcol)s,face:%(mono)s,size:%(size)d
style.pyrex.033=size:%(ln-size)d,face:%(ln-font)s,back:#A0A0A0
style.pyrex.034=fore:#0000FF,back:#FFFF88,bold
style.pyrex.035=fore:#FF0000,back:#FFFF88,bold
style.pyrex.036=
style.pyrex.037=

[style.pyrex.default]

[pyrex]
displaysrc='''+`pyrexSource`[1:-1]+'''
braces={}
styleidnames={wx.stc.STC_P_DEFAULT: 'Default', wx.stc.STC_P_COMMENTLINE: 'Comment', wx.stc.STC_P_NUMBER : 'Number', wx.stc.STC_P_STRING : 'String', wx.stc.STC_P_CHARACTER: 'Single quoted string', wx.stc.STC_P_WORD: 'Keyword', wx.stc.STC_P_TRIPLE:'Triple quotes', wx.stc.STC_P_TRIPLEDOUBLE: 'Triple double quotes', wx.stc.STC_P_CLASSNAME: 'Class definition', wx.stc.STC_P_DEFNAME: 'Function or method', wx.stc.STC_P_OPERATOR: 'Operators', wx.stc.STC_P_IDENTIFIER: 'Identifiers', wx.stc.STC_P_COMMENTBLOCK: 'Comment blocks', wx.stc.STC_P_STRINGEOL: 'EOL unclosed string'}
lexer=wx.stc.STC_LEX_PYTHON
keywords=and assert break class continue def del elif else except exec finally for from global if import in is lambda not or pass print raise return try while struct union enum ctypedef cdef void extern NULL
'''

Plugins.assureConfigFile(pyrex_cfgfile, pyrexStyleEditorConfig)

#-------------------------------------------------------------------------------

def getPyrexModuleData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00\xfaIDATx\x9c\x85SQ\xae\xc4 \x08\x1c6=\x00\x07v\x9b\r\x8fw_n0\xefCT\
\xda\xb5y4\x06*\x82\x0c#\xa2\xaa\x18\x12\x11t\xebv;\x01U\x95\xeaC\x91\xe9SUd\
\x12\x92\xe4\xd0n \x00.\xdfuM\x9f\xaa\xc2\xcds\x937\r\xee\x82k\x92c\x94$\x02\
\x90\xc0\xef\xcf\xd2w\x11Y6\x13\x90\x00\x98\xb8w\xd2\xcerX\x16\xf6\x88\xa0\
\xaa\xca\xf1\x14\xdc\xdei\x9c\xcf\xc9\x01\xe0\xd56\x81m\xd4\xb6\x91\x88`D\
\x90\\\xcc\xf0\xf2e\xe3\x06\x0b\xf8\xa7\x89\x8b\xc2<\x0c\xbb&\xc2g\x9f\x04I\
\xe3\x0byR,\x8dZ\xbe\x01\xf8\x00n\xbd\x81u\x8dfJ\xde|\x81\xec\xd6{\xe1\x85\
\xca\xfb\xcb\x1c\xfd\x98\x10\x86\xf6\x02\xc1m\xf5\xc2\xcd9\x1e\xdd\x84\x07P\
\xc6,D\x04a\x00\xde\xbd\x9c\x1d\xbd\xed\xfc\xde?\xea\x8f\xa3S\xf8\xf46\xea~\
\xcb\x8b\xe60\xb99a\xdf\x10\xc6\x9e\xdb\x9df_\xc3T\'\x12\x19Tq\xde\x83\xea\
\xfa\x03.(\xfa\xcc\xbb\xaeS\xb9\x00\x00\x00\x00IEND\xaeB`\x82'

def getPyrexPaletteData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\
\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x01QIDATx\x9c\xdd\x95AN\xc40\x0cE\x9f\x11\x070WE\xb3#D(\x98\xdd\x88\xab\x92\
\x1b\x98E\x125\xd3\xb8\x15\x0bf\x01\x96\xaaVu\xf2\x7f\xfc\xbf\xdd\x8a\xaar\
\xcfx\xb8+\xfa\xbf x<K\xd6Z\xddJ{N\x19TU\xe6\xdc\xbcv\xce\xfd\x88\xa0\xd6\
\xea\xee\x8e\x88\xe0\xee\x80\x90ruU\x95\x96\xbb]/\xd2r{\x9cP\xa2\xcb\xf3\xc5\
\xddA\x04\xc6\xfd\xe5u&^\xf7\xb8\xafU\x9dV0\xc0?\xde\xb7{\xb4f&\x08q\xf6s0\
\xeb\x1eE\xca\x1b\x98\xc8\xa6}\xad\xb1D7\x15\x9c\x81\xa7.\x11\xf9\x98<\x8a\
\xc5\x83\x14\x00\'\x80\xb0G\xda\xa1\x86/\x91\x07\xa1D\xcc\xcb:\xb0\x95&\x0f\
\x9c\xe8-k\xbb.\x15\xa8\xaa \xe0\xd2\xc1\x0b\xe0\x1b8o\xb7\xe6\x9e\x81\x87\
\x044<\xa4\x03\xcfUP\x1a\x81\x95\x068_G\x83\xb6\x10|\r\x1ds\x07\xce\r\x10\
\x07\xa3?O\xd5\x8e\x0bb\x0f\x16\x82\'U\x11\xb6\x13Y\xe9\x1d4\x9d/e\xb0b@\x1b\
\xcaatT\xc1b\xf2\x88Z\xabS\x80\x0e\x1e\xb5o\xca\xeb\xfb\xfd7\xeb\xf4cg\xb4\
\x16=\x9a\x8d\xf9\xfd\xa8r\xef\xc5!\x81\x15#\x91\xb0\xf7m\xb3\x95N\xb8\x03m\
\x871\xaez]\x8c>\x94\x08&\x99 \x9c`+\xc6\xf5s\x05\xfd1\xc1o\xc4\xdf\xffe\xde\
\x9d\xe0\x1b_\xc7\xa9{G\x16\x95\x05\x00\x00\x00\x00IEND\xaeB`\x82'

Preferences.IS.registerImage('Images/Modules/Pyrex.png', getPyrexModuleData())
Preferences.IS.registerImage('Images/Palette/Pyrex.png', getPyrexPaletteData())
