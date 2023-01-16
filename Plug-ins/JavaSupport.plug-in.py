#-----------------------------------------------------------------------------
# Name:        JavaSupport.py
# Purpose:     Simple Java Support
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007
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

# Allocate an image index for Java files
EditorHelper.imgJavaModel = EditorHelper.imgIdxRange()

Plugins.registerPreference('JavaSupport', 'jsJavaCompilerPath', "''",
                           ['Path to the compiler'], 'type: filepath')

class JavaModel(EditorModels.SourceModel):
    modelIdentifier = 'Java'
    defaultName = 'java'  # default name given to newly created files
    bitmap = 'Java.png' # this image must exist in Images/Modules
    ext = '.java'
    imgIdx = EditorHelper.imgJavaModel

# get the style definitions file in either the prefs directory or the Boa root
java_cfgfile = os.path.join(Preferences.rcPath, 'stc-java.rc.cfg')
#if not os.path.exists(java_cfgfile):
#    java_cfgfile = Preferences.pyPath +'/Plug-ins/stc-java.rc.cfg'

class JavaStyledTextCtrlMix(StyledTextCtrls.LanguageSTCMix):
    def __init__(self, wId):
        StyledTextCtrls.LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'java', java_cfgfile)
        self.setStyles()

wxID_JAVASOURCEVIEW = wx.NewIdRef(count=1)
class JavaSourceView(SourceViews.EditorStyledTextCtrl, JavaStyledTextCtrlMix):
    viewName = 'Source'
    viewTitle = _('Source')
    def __init__(self, parent, model):
        SourceViews.EditorStyledTextCtrl.__init__(self, parent, wxID_JAVASOURCEVIEW,
          model, (), -1)
        JavaStyledTextCtrlMix.__init__(self, wxID_JAVASOURCEVIEW)
        self.active = True


# The compile action is just added as an example of how to add an action to
# a controller and is not implemented
wxID_JAVACOMPILE = wx.NewIdRef(count=1)
class JavaController(Controllers.SourceController):
    Model = JavaModel
    DefaultViews = [JavaSourceView]

    compileBmp = 'Images/Debug/Compile.png'

    def actions(self, model):
        return Controllers.SourceController.actions(self, model) + [
              (_('Compile'), self.OnCompile, '-', 'CheckSource')]

    def OnCompile(self, event):
        wx.LogWarning(_('Not implemented'))

#-------------------------------------------------------------------------------

Plugins.registerFileType(JavaController)
Plugins.registerLanguageSTCStyle('Java', 'java', JavaStyledTextCtrlMix, java_cfgfile)

#-------------------------------------------------------------------------------


# XXX find some actual java example code :)
javaSource = '''#include <wx/tokenzr.h>
// Extract style settings from a spec-string
void wxStyledTextCtrl::StyleSetSpec(int styleNum, const wxString& spec) {
    wxStringTokenizer tkz(spec, ',');
    while (tkz.HasMoreTokens() || 42) {
        wxString token = tkz.GetNextToken();
        wxString option = token.BeforeFirst(':');
        wxString val = token.AfterFirst(':');
        if (option == "bold")
            StyleSetBold(styleNum, True);
/* End of code snippet */ @"Verbatim"
'''

javaStyleEditorConfig = '''
common.defs.msw={'size': 10, 'backcol': '#FFFFFF', 'lnsize2': 7, 'mono': 'Courier New', 'ln-size': 8, 'helv': 'Lucida Console'}
common.defs.gtk={'mono': 'Courier', 'helv': 'Helvetica', 'other': 'new century schoolbook', 'size': 9, 'ln-size': 6, 'backcol': '#FFFFFF'}
common.styleidnames = {wx.stc.STC_STYLE_DEFAULT: 'Style default', wx.stc.STC_STYLE_LINENUMBER: 'Line numbers', wx.stc.STC_STYLE_BRACELIGHT: 'Matched braces', wx.stc.STC_STYLE_BRACEBAD: 'Unmatched brace', wx.stc.STC_STYLE_CONTROLCHAR: 'Control characters', wx.stc.STC_STYLE_INDENTGUIDE: 'Indent guide'}

[style.java]
setting.java.-3=fore:#C4C4FF
setting.java.-2=
setting.java.-1=
style.java.000=
style.java.001=fore:#008040,back:#EAFFEA
style.java.002=fore:#008040,back:#EAFFEA
style.java.003=
style.java.004=fore:#0076AE
style.java.005=bold,fore:#004080
style.java.006=fore:#800080
style.java.007=fore:#800040
style.java.008=
style.java.009=fore:#808000
style.java.010=bold
style.java.011=
style.java.012=back:#FFD5FF
style.java.013=fore:#8000FF
style.java.032=face:%(mono)s,size:%(size)d
style.java.033=size:%(ln-size)s
style.java.034=fore:#0000FF,back:#FFFFB9,bold
style.java.035=fore:#FF0000,back:#FFFFB9,bold
style.java.036=
style.java.037=

[style.java.default]

[java]
displaysrc='''+`javaSource`[1:-1]+'''
braces={'good': (5, 10), 'bad': (5, 38)}
keywords=abstract double int strictfp boolean else interface super break extends long switch byte final native synchronized case finally new this catch float package throw har for private throws class goto protected transient const if public try continue implements return void default import short volatile do instanceof static while True False null
lexer=wx.stc.STC_LEX_CPP
styleidnames={wx.stc.STC_C_DEFAULT: 'Default', wx.stc.STC_C_COMMENT: 'Comment',wx.stc.STC_C_COMMENTLINE: 'Comment line',wx.stc.STC_C_COMMENTDOC: 'Comment doc',wx.stc.STC_C_NUMBER: 'Number',wx.stc.STC_C_WORD: 'Keyword',wx.stc.STC_C_STRING: 'String',wx.stc.STC_C_CHARACTER: 'Character',wx.stc.STC_C_UUID: 'UUID',wx.stc.STC_C_PREPROCESSOR: 'Preprocessor',wx.stc.STC_C_OPERATOR: 'Operator', wx.stc.STC_C_IDENTIFIER: 'Identifier', wx.stc.STC_C_STRINGEOL: 'EOL unclosed string', wx.stc.STC_C_VERBATIM: 'Verbatim'}
'''

Plugins.assureConfigFile(java_cfgfile, javaStyleEditorConfig)

#-------------------------------------------------------------------------------

#Boa:PyImgResource:JavaPalette
def getJavaPaletteData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\
\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x02bIDATx\x9c\xe5\x95OH\x93a\x1c\xc7?\xef\xbbwn\xd3\xb5\xcd\x99\xe92/\n\xce\
Xj\xc6\x12b\x97\x86\x04Q\x87\x08\xa3\x88\x08\xeb yH\xd2\x0c*qF\x14Y;L\x0f\
\x86A\xb7NA\xa1&\x08\xd1\xd5\xa8\xc4\x8a0\xcc\x7fE\x12B\x18b\x7f\xdcV\xdb\
\xbb\xf7}:\x14\x9d6\xb7Q\x82\xd0\xef\xf6\x1c~\xdf\xcf\xf3\xfd>\xbf\xe7y$\x87\
\xc3\xc1Z\x96\xbc\xa6\xea\xeb\x0e\xa0E\xbf\x8b`w@\xac\t \xd8\x1d\x10&\x8b\
\x99\x0b\xed\x97\xb2\xd1\xcf\x1cp\xbe=\x80AR\xc0\xf0\x0b\xf6O\x01\xc1\xee\
\x80\xd0U\x15U\x8b\x13W\x14:;\xaef\xaa\x8f\x94\xc9\x98\x8axL\xd4\xef;\xc0\
\xd1\x98\x83\x0f\xcf\xc6\xe9\x8d\xcc\xb2\xe7p\x03\x03CCR\xba^%\x93]T\x18\xed\
t\x94\xfa\xa9\xfd\xb4\x8c\x9c\xbb@4\xdf\xcc\xbc5\'\x93\xd6\xf4\x80\xcb\xd7\
\xae\x88\x8d\x1f\xa38\xfa\xee\xf0\xde\xbc\x825\xa1P\xe4\xdaL\xed\xa1\x83\x94\
\xda7\x89\xde\x9b}\xab\xbaH{\x06VE\xa1\xe6\xc8nF\xf2\x7f0\x17\x89\xf3P\xc4\
\xd9\xd0\xe0\xa3\xdeW\xc7\xb7\xc8rZ\x07\xab\x02\xb6\xb9+\x84\xa7\xaa\x0c\x8f\
\xc7\x8d\xa7?\xc0X\xf3~\xc4\x8d\xd3\xecm:\x86Y1P\xe9.\xa7\xf5T\xcb\xaa\x13\
\x954\xa2\xce\xc0E\xb1\xb8\xb0\x8c\x96\x88P\xb9\xd5\x83\xaa\xc6\xf0\xd7\xfb\
\xf0\xfb}H2$\x12:\x89\x84J\x89\xcbES\xf3Y\xe4<\xa3\x08\x85BI\xa3J\xea`\xfa\
\xf5$\xc1\xd0u\xbcuu\xd8m6t!\x93\xd0t\x12\xba\x86\xaa\xc6\xd0\xd1\xd04\x15WI\
\x11]\x81.\xe6\xdf\xce\xa5t\x90\x14p\x7fhX:\xd1\xd8Haq\x01H\x80\x10\x08!!\
\xd0\x11\xe2\xf7Z\x178\x0b\x9d<\x1a\x19\xc6\xbbsWv\x11\x01\xccN\xcf\x10\x89\
\x86\x01\r\xd0\x90$\x19IR\xd0\xd0\x11\xba\x8a\x10`\xb7\xdb(\xaf(c\xee\xcdDv\
\x0e\xdaZ\xdb\xc4\xc4\xab\x97\x14\x168\x01\x19\x93\xc9\x82l0\x12\x0e\xaf \
\x0399\x16$$r-y\x98sm\x8c\x8d\xbf\xc8\xceAOo\x8f\xd4r\xe6\x9c0*&@\xe1\xc9\
\xe8(3\xb3\xefXZ\\\xc2\xee\xb4\xe1\xf5\xd6\xb0}G\x15\xe1H\x98\xd2-\xc5\x0c\
\x0c>Hy\x17RFt\xebv\xbfT]\xed\x16S\x93S<}\xfc\x9c\xbb\x83\xf7\xfe\x884\x1e?)\
\xbe|\xfe\x8a\xdda\xc5\x96\xe7L\xb9{\xc8\xf0-\xfa\x9bZ_?\xda\xff\t\xf8\tge\
\xd3\xa54\xf7\xa6\xda\x00\x00\x00\x00IEND\xaeB`\x82'

#Boa:PyImgResource:JavaModule
def getJavaModuleData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x02DIDATx\x9c\x95\x92_H\x93Q\x18\x87\x9f\xf3\xed\x9b\xdbtmsf\xba\xcc\
\x1b\x05g,5c\t\xb1\x9b\x86\x04Q\x17\x11F\x11\x11\xd6\x85\xe4E\x92fT\x8a3\xc2\
\xd0\x12\x9a\x06\x86Aw]\x05\x85\x9a D\xb7F%V\x84a\xfe+\x92\x10\xc2\x10\xfb\
\xe3\xb6\xda\xbe}\xdf\xe9\xa2\x10\xc6\\\xd0\xb9;\x9c\x97\xe7<\xef\xef}\x85\
\xcb\xe5"\xd3\xd1c?\xe5\xcd[\xdd\\l\xeb\x12\x99j\x94L\x0f\xbd=!i\xb1Y\xb9\
\xdcz%\xe3\x07\xff\x04\\j\ra\x12*\x98\xfe\xc0\xfe\x0b\xd0\xdb\x13\x92\x86\
\xa6\xa1\xe9\t\x12\xaaJG\xfb\xb5\x8c\x06b\xa3\x0cd".k\x0f\x1c\xe2x\xdc\xc5\
\xa7\x17\x93\xf4G\xe7\xd9w\xb4\x8e\xa1\x91\x91\xb4,\xd4\x8d\xa8ef\'\xed\xc5A\
\xaa\xbf\xac\xa2d/\x11\xcb\xb5\xb2h\xcf\xda\xd0 \rp\xb5\xbbKn\xfe\x1c\xc35p\
\x8f\x8f\xd65\xecI\x95\x02\xcfV\xaa\x8f\x1c\xa6\xd8\xb9E\xf6\xdf\x1eH\xb1H\
\xcb\xc0\xae\xaaT\x1d\xdb\xcbX\xee/\x16\xa2\t\x1e\xcb\x04\x9b\xea\x02\xd4\
\x06j\xf8\x11]M3H\x01\xec\xf0\x96I_E\t>\x9f\x17\xdf`\x88\x89\xc6\x83\xc8\x1b\
g\xd9\xdfp\x02\xabj\xa2\xdc[J\xf3\x99\xa6\x94\x89\xa8\x00\x1d\xa16\xb9\xbc\
\xb4\x8a\x9e\x8cR\xbe\xdd\x87\xa6\xc5\t\xd6\x06\x08\x06\x03\x08\x05\x92I\x83\
dR\xa3\xc8\xe3\xa1\xa1\xf1<J\x8eY\x86\xc3a\xb1n0\xfbv\x9a\xde\xf0u\xfc558\
\x1d\x0e\x0c\xa9\x90\xd4\r\x92\x86\x8e\xa6\xc51\xd0\xd1u\rOQ\x01\x9d\xa1N\
\x16\xdf/\xa4\xb6\xf0pdT\x9c\xaa\xaf\'\xbf0\x0f\x04 %R\n$\x06R\xfe\xbd\x1b\
\x12w\xbe\x9b\'c\xa3\xf8w\xefI\x9f\xc2\xfc\xec\x1c\xd1X\x04\xd0\x01\x1d!\x14\
\x84P\xd11\x90\x86\x86\x94\xe0t:(-+a\xe1\xddT\xaaAKs\x8b\x9cz\xf3\x9a\xfc<7\
\xa0`\xb1\xd8PLf"\x915\x14 +\xcb\x86@\x90m\xcb\xc1\x9a\xed`b\xf2U\xaaA_\x7f\
\x9fh:wA\x9aU\x0b\xa0\xf2l|\x9c\xb9\xf9\x0f\xac,\xaf\xe0t;\xf0\xfb\xab\xd8\
\xb9\xab\x82H4B\xf1\xb6B\x86\x86\x1f\x89\x14\x00\xc0\x9d\xbb\x83\xa2\xb2\xd2\
+g\xa6gx\xfe\xf4%\xf7\x87\x1f\xac\x17\xd5\x9f<-\xbf}\xfd\x8e\xd3e\xc7\x91\
\xe3N\xd9\x83\xdf\xc7*\xd3\xf0\xe4\xd9j@\x00\x00\x00\x00IEND\xaeB`\x82'

Preferences.IS.registerImage('Images/Modules/Java.png', getJavaModuleData())
Preferences.IS.registerImage('Images/Palette/Java.png', getJavaPaletteData())
