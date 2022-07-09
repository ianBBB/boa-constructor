#-----------------------------------------------------------------------------
# Name:        BasicCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.BasicCompanions'

import wx

import wx.html
import wx.stc
import wx.animate

from Utils import _

from BaseCompanions import WindowDTC, ChoicedDTC, CollectionDTC

import Constructors
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *
from PropEdit import InspectorEditorControls

class ScrollBarDTC(Constructors.MultiItemCtrlsConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.SB_HORIZONTAL', 'wx.SB_VERTICAL'] + self.windowStyles

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wx.SB_HORIZONTAL',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent', 'CmdScrollEvent']

EventCategories['ComboEvent'] = ('wx.EVT_COMBOBOX', 'wx.EVT_TEXT',
                                 'wx.EVT_TEXT_ENTER')
commandCategories.append('ComboEvent')
class ComboBoxDTC(ChoicedDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.CB_SIMPLE', 'wx.CB_DROPDOWN', 'wx.CB_READONLY',
                             'wx.CB_SORT', 'wx.TE_PROCESS_ENTER'] + self.windowStyles

    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Choices': 'choices', 'Style': 'style',
                'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'value': `self.name`,
                'pos': position,
                'size': size,
                'choices': '[]',
                'style': '0',
                'name': `self.name`}

##    def vetoedMethods(self):
##        return ['GetColumns', 'SetColumns', 'GetSelection', 'SetSelection',
##                'GetStringSelection', 'SetStringSelection']
##
##    def hideDesignTime(self):
##        return ['Label']

    def events(self):
        return ChoicedDTC.events(self) + ['ComboEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ComboEvent', 'wx.EVT_COMBOBOX')

EventCategories['ChoiceEvent'] = ('wx.EVT_CHOICE',)
commandCategories.append('ChoiceEvent')
class ChoiceDTC(Constructors.ListConstr, ChoicedDTC):
    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': size,
                'choices': `[]`,
                'style': '0',
                'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['ChoiceEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ChoiceEvent', 'wx.EVT_CHOICE')

class LabeledNonInputConstr:
    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Label': 'label',
                'Style': 'style', 'Name': 'name'}

class StaticTextDTC(LabeledNonInputConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.ALIGN_LEFT', 'wx.ALIGN_RIGHT', 'wx.ALIGN_CENTRE',
                             'wx.ST_NO_AUTORESIZE'] + self.windowStyles
    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

EventCategories['TextCtrlEvent'] = ('wx.EVT_TEXT', 'wx.EVT_TEXT_ENTER',
                                    'wx.EVT_TEXT_URL', 'wx.EVT_TEXT_MAXLEN')
commandCategories.append('TextCtrlEvent')
class TextCtrlDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.TE_PROCESS_ENTER', 'wx.TE_PROCESS_TAB',
                             'wx.TE_MULTILINE', 'wx.TE_PASSWORD',
                             'wx.TE_READONLY', 'wx.TE_RICH', 'wx.TE_RICH2',
                             'wx.TE_AUTO_URL', 'wx.TE_NOHIDESEL',
                             'wx.TE_LEFT', 'wx.TE_CENTER', 'wx.TE_RIGHT',
                             'wx.TE_DONTWRAP', 'wx.TE_LINEWRAP', 'wx.TE_WORDWRAP',
                             ] + self.windowStyles
        self.editors['Editable'] = BoolPropEdit
        self._maxLength = 0
        self.initPropsThruCompanion.append('MaxLength')

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'MaxLength': ('CompnRoute', self.GetMaxLength, self.SetMaxLength),
                      'Editable':  ('CtrlRoute', wx.TextCtrl.IsEditable, wx.TextCtrl.SetEditable)})
        return props

    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'value': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + \
              ['Selection', 'Title', 'Label', 'DefaultStyle']

    def events(self):
        return WindowDTC.events(self) + ['TextCtrlEvent']

    def GetMaxLength(self, x):
        return self._maxLength

    def SetMaxLength(self, value):
        self._maxLength = value
        self.control.SetMaxLength(value)


EventCategories['RadioButtonEvent'] = ('wx.EVT_RADIOBUTTON',)
commandCategories.append('RadioButtonEvent')
class RadioButtonDTC(Constructors.LabeledInputConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit
        self.windowStyles = ['wx.RB_GROUP'] + self.windowStyles

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['RadioButtonEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('RadioButtonEvent', 'wx.EVT_RADIOBUTTON')


EventCategories['CheckBoxEvent'] = ('wx.EVT_CHECKBOX',)
commandCategories.append('CheckBoxEvent')
class CheckBoxDTC(Constructors.LabeledInputConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit
        self.windowStyles = ['wx.ALIGN_RIGHT'] + self.windowStyles

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['CheckBoxEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('CheckBoxEvent', 'wx.EVT_CHECKBOX')


class SliderDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['MinValue'] = IntConstrPropEdit
        self.editors['MaxValue'] = IntConstrPropEdit
        self.windowStyles = ['wx.SL_HORIZONTAL', 'wx.SL_VERTICAL',
                             'wx.SL_AUTOTICKS', 'wx.SL_LABELS', 'wx.SL_LEFT',
                             'wx.SL_RIGHT', 'wx.SL_TOP',
                             'wx.SL_SELRANGE'] + self.windowStyles

    def constructor(self):
        return {'Value': 'value', 'MinValue': 'minValue', 'MaxValue': 'maxValue',
                'Position': 'pos', 'Size': 'size', 'Style': 'style',
                'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'value': '0',
                'minValue': '0',
                'maxValue': '100',
                'pos': position,
                'size': size,
                'style': 'wx.SL_HORIZONTAL',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + ['TickFreq']

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent', 'CmdScrollEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ScrollEvent', 'wx.EVT_SCROLL')

class GaugeDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.GA_HORIZONTAL', 'wx.GA_VERTICAL',
                        'wx.GA_PROGRESSBAR', 'wx.GA_SMOOTH'] + self.windowStyles

    def constructor(self):
        return {'Range': 'range', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'range': '100',
                'pos': position,
                'size': size,
                'style': 'wx.GA_HORIZONTAL',
                'name': `self.name`}

class StaticBoxDTC(LabeledNonInputConstr, WindowDTC):
    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': self.getDefCtrlSize(),
                'style': '0',
                'name': `self.name`}

    def properties(self):
        props = WindowDTC.properties(self)
        del props['Sizer']
        return props

class StaticLineDTC(Constructors.WindowConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.LI_HORIZONTAL', 'wx.LI_VERTICAL'] + self.windowStyles

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

class StaticBitmapDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Bitmap'] = BitmapPropEdit

    def constructor(self):
        return {'Bitmap': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'bitmap': 'wx.NullBitmap',
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

class HtmlWindowDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.html.HW_SCROLLBAR_NEVER', 'wx.html.HW_SCROLLBAR_AUTO'] + self.windowStyles
        self._borders = 10
        self.initPropsThruCompanion.append('Borders')

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Name': 'name', 'Style': 'style'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.html.HW_SCROLLBAR_AUTO',
                'name': `self.name`}

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'Borders':  ('CompnRoute', self.GetBorders, self.SetBorders)})
        return props

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent']

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'import wx.html') )

    def GetBorders(self, x):
        return self._borders

    def SetBorders(self, value):
        self._borders = value
        self.control.SetBorders(value)

stcEOLMode = [wx.stc.STC_EOL_CRLF, wx.stc.STC_EOL_CR, wx.stc.STC_EOL_LF]
stcEOLModeNames = {'wx.stc.STC_EOL_CRLF': wx.stc.STC_EOL_CRLF,
                   'wx.stc.STC_EOL_CR': wx.stc.STC_EOL_CR,
                   'wx.stc.STC_EOL_LF': wx.stc.STC_EOL_LF}

stcEdgeMode = [wx.stc.STC_EDGE_NONE, wx.stc.STC_EDGE_LINE, wx.stc.STC_EDGE_BACKGROUND]
stcEdgeModeNames = {'wx.stc.STC_EDGE_NONE': wx.stc.STC_EDGE_NONE,
                    'wx.stc.STC_EDGE_LINE': wx.stc.STC_EDGE_LINE,
                    'wx.stc.STC_EDGE_BACKGROUND': wx.stc.STC_EDGE_BACKGROUND}

stcLexer = [wx.stc.STC_LEX_NULL, wx.stc.STC_LEX_PYTHON, wx.stc.STC_LEX_CONTAINER,
            wx.stc.STC_LEX_CPP , wx.stc.STC_LEX_HTML , wx.stc.STC_LEX_XML, wx.stc.STC_LEX_PERL,
            wx.stc.STC_LEX_SQL, wx.stc.STC_LEX_VB, wx.stc.STC_LEX_PROPERTIES,
            wx.stc.STC_LEX_ERRORLIST, wx.stc.STC_LEX_MAKEFILE, wx.stc.STC_LEX_BATCH,
            wx.stc.STC_LEX_XCODE, wx.stc.STC_LEX_LATEX, wx.stc.STC_LEX_LUA, wx.stc.STC_LEX_DIFF,
            wx.stc.STC_LEX_CONF, wx.stc.STC_LEX_PASCAL, wx.stc.STC_LEX_AVE, wx.stc.STC_LEX_ADA,
            wx.stc.STC_LEX_LISP, wx.stc.STC_LEX_RUBY, wx.stc.STC_LEX_EIFFEL, wx.stc.STC_LEX_EIFFELKW,
            wx.stc.STC_LEX_TCL, wx.stc.STC_LEX_NNCRONTAB, wx.stc.STC_LEX_BULLANT,
            wx.stc.STC_LEX_VBSCRIPT, wx.stc.STC_LEX_BAAN,
            wx.stc.STC_LEX_MATLAB, wx.stc.STC_LEX_SCRIPTOL, wx.stc.STC_LEX_AUTOMATIC]
stcLexerNames = {'wx.stc.STC_LEX_NULL': wx.stc.STC_LEX_NULL,
      'wx.stc.STC_LEX_PYTHON': wx.stc.STC_LEX_PYTHON,
      'wx.stc.STC_LEX_CONTAINER': wx.stc.STC_LEX_CONTAINER,
      'wx.stc.STC_LEX_CPP': wx.stc.STC_LEX_CPP, 'wx.stc.STC_LEX_HTML': wx.stc.STC_LEX_HTML,
      'wx.stc.STC_LEX_XML': wx.stc.STC_LEX_XML, 'wx.stc.STC_LEX_PERL': wx.stc.STC_LEX_PERL,
      'wx.stc.STC_LEX_SQL': wx.stc.STC_LEX_SQL, 'wx.stc.STC_LEX_VB': wx.stc.STC_LEX_VB,
      'wx.stc.STC_LEX_PROPERTIES': wx.stc.STC_LEX_PROPERTIES,
      'wx.stc.STC_LEX_ERRORLIST': wx.stc.STC_LEX_ERRORLIST,
      'wx.stc.STC_LEX_MAKEFILE': wx.stc.STC_LEX_MAKEFILE,
      'wx.stc.STC_LEX_BATCH': wx.stc.STC_LEX_BATCH,
      'wx.stc.STC_LEX_XCODE': wx.stc.STC_LEX_XCODE, 'wx.stc.STC_LEX_LATEX': wx.stc.STC_LEX_LATEX,
      'wx.stc.STC_LEX_LUA': wx.stc.STC_LEX_LUA, 'wx.stc.STC_LEX_DIFF': wx.stc.STC_LEX_DIFF,
      'wx.stc.STC_LEX_CONF': wx.stc.STC_LEX_CONF, 'wx.stc.STC_LEX_PASCAL': wx.stc.STC_LEX_PASCAL,
      'wx.stc.STC_LEX_AVE': wx.stc.STC_LEX_AVE, 'wx.stc.STC_LEX_ADA': wx.stc.STC_LEX_ADA,
      'wx.stc.STC_LEX_LISP': wx.stc.STC_LEX_LISP, 'wx.stc.STC_LEX_RUBY': wx.stc.STC_LEX_RUBY,
      'wx.stc.STC_LEX_EIFFEL': wx.stc.STC_LEX_EIFFEL,
      'wx.stc.STC_LEX_EIFFELKW': wx.stc.STC_LEX_EIFFELKW,
      'wx.stc.STC_LEX_TCL': wx.stc.STC_LEX_TCL, 'wx.stc.STC_LEX_NNCRONTAB': wx.stc.STC_LEX_NNCRONTAB,
      'wx.stc.STC_LEX_BULLANT': wx.stc.STC_LEX_BULLANT,
      'wx.stc.STC_LEX_VBSCRIPT': wx.stc.STC_LEX_VBSCRIPT,
      'wx.stc.STC_LEX_BAAN': wx.stc.STC_LEX_BAAN,
      'wx.stc.STC_LEX_MATLAB': wx.stc.STC_LEX_MATLAB,
      'wx.stc.STC_LEX_SCRIPTOL': wx.stc.STC_LEX_SCRIPTOL,
      'wx.stc.STC_LEX_AUTOMATIC': wx.stc.STC_LEX_AUTOMATIC}

stcPrintColourMode = [wx.stc.STC_PRINT_NORMAL, wx.stc.STC_PRINT_INVERTLIGHT,
      wx.stc.STC_PRINT_BLACKONWHITE, wx.stc.STC_PRINT_COLOURONWHITE,
      wx.stc.STC_PRINT_COLOURONWHITEDEFAULTBG]
stcPrintColourModeNames = {'wx.stc.STC_PRINT_NORMAL': wx.stc.STC_PRINT_NORMAL,
      'wx.stc.STC_PRINT_INVERTLIGHT': wx.stc.STC_PRINT_INVERTLIGHT,
      'wx.stc.STC_PRINT_BLACKONWHITE': wx.stc.STC_PRINT_BLACKONWHITE,
      'wx.stc.STC_PRINT_COLOURONWHITE': wx.stc.STC_PRINT_COLOURONWHITE,
      'wx.stc.STC_PRINT_COLOURONWHITEDEFAULTBG': wx.stc.STC_PRINT_COLOURONWHITEDEFAULTBG}

stcWrapMode = [wx.stc.STC_WRAP_NONE, wx.stc.STC_WRAP_WORD]
stcWrapModeNames = {'wx.stc.STC_WRAP_NONE': wx.stc.STC_WRAP_NONE,
                    'wx.stc.STC_WRAP_WORD': wx.stc.STC_WRAP_WORD}

class StyledTextCtrlDTC(Constructors.WindowConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update(
            {'BackSpaceUnIndents': BoolPropEdit,
             'BufferedDraw': BoolPropEdit,
             'CaretLineVisible': BoolPropEdit,
             'EndAtLastLine': BoolPropEdit,
             'IndentationGuides': BoolPropEdit,
             'MouseDownCaptures': BoolPropEdit,
             'Overtype': BoolPropEdit,
             'ReadOnly': BoolPropEdit,
             'UndoCollection': BoolPropEdit,
             'UseHorizontalScrollBar': BoolPropEdit,
             'UseTabs': BoolPropEdit,
             'ViewEOL': BoolPropEdit,
             'ViewWhiteSpace': BoolPropEdit,
             'EOLMode': EnumPropEdit,
             'EdgeMode': EnumPropEdit,
             'Lexer': EnumPropEdit,
             'PrintColourMode': EnumPropEdit,
             'WrapMode': EnumPropEdit,
            })

        self.options.update({'EOLMode'   : stcEOLMode,
                             'EdgeMode' : stcEdgeMode,
                             'Lexer': stcLexer,
                             'PrintColourMode': stcPrintColourMode,
                             'WrapMode': stcWrapMode,
                            })
        self.names.update({'EOLMode'   : stcEOLModeNames,
                           'EdgeMode' : stcEdgeModeNames,
                           'Lexer': stcLexerNames,
                           'PrintColourMode': stcPrintColourModeNames,
                           'WrapMode': stcWrapModeNames,
                          })

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': '0',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + ['Anchor', 'CodePage',
               'DocPointer', 'LastKeydownProcessed', 'ModEventMask',
               'Status', 'STCFocus']

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'import wx.stc') )

class FilenameConstrPropEdit(ConstrPropEdit):
    dlgCaption = _('Choose a file')
    fileTypeFilter = '*.*'
    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dlg = wx.FileDialog(self.parent, self.dlgCaption, '.', self.value,
              self.fileTypeFilter, wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                value = dlg.GetPath()
                if os.path.isfile(value):
                    self.value = `value`
                    self.editorCtrl.setValue(self.value)
                    self.inspectorPost(False)
        finally:
            dlg.Destroy()


class GIFFilenameConstrPropEdit(FilenameConstrPropEdit):
    dlgCaption = _('Choose a gif file')
    fileTypeFilter = '*.gif'

class GIFAnimationCtrlDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.animate.AN_FIT_ANIMATION'] + self.windowStyles
        self.editors['Filename'] = GIFFilenameConstrPropEdit

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Name': 'name', 'Style': 'style',
                'Filename': 'filename'}

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {'pos': position,
                'size': size,#self.getDefCtrlSize(),
                'style': 'wx.animate.AN_FIT_ANIMATION|wx.NO_BORDER',
                'name': `self.name`,
                'filename': `''`}

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'import wx.animate') )

class MediaCtrlDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Filename'] = FilenameConstrPropEdit
        self.editors['Backend'] = EnumConstrPropEdit
        self.editors['Volume'] = BITPropEditor
        self.editors['PlaybackRate'] = BITPropEditor

        self.names['Backend'] = ['wx.media.MEDIABACKEND_DIRECTSHOW',
                                 'wx.media.MEDIABACKEND_MCI',
                                 'wx.media.MEDIABACKEND_QUICKTIME',
                                 'wx.media.MEDIABACKEND_GSTREAMER', "''"]

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Name': 'name', 'Style': 'style',
                'Filename': 'fileName', 'Backend': 'szBackend'}

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': '0',
                'name': `self.name`,
                'fileName': `''`,
                'szBackend': `''`}

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'import wx.media') )


EventCategories['RichTextEvent'] = (
    'wx.richtext.EVT_RICHTEXT_CHARACTER',
    'wx.richtext.EVT_RICHTEXT_DELETE',
    'wx.richtext.EVT_RICHTEXT_RETURN',
    'wx.richtext.EVT_RICHTEXT_STYLE_CHANGED',
    'wx.richtext.EVT_RICHTEXT_STYLESHEET_CHANGING',
    'wx.richtext.EVT_RICHTEXT_STYLESHEET_CHANGED',
    'wx.richtext.EVT_RICHTEXT_STYLESHEET_REPLACING',
    'wx.richtext.EVT_RICHTEXT_STYLESHEET_REPLACED',
    'wx.richtext.EVT_RICHTEXT_CONTENT_INSERTED',
    'wx.richtext.EVT_RICHTEXT_CONTENT_DELETED')
commandCategories.append('RichTextEvent')

class RichTextCtrlDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.richtext.RE_MULTILINE', 'wx.richtext.RE_READONLY',
                            ] + self.windowStyles
        self.editors['Editable'] = BoolPropEdit
    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Style': 'style'}
    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'value': `self.name`,
                'pos': position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.richtext.RE_MULTILINE'}
    def vetoedMethods(self):
        return ['GetTargetWindow', 'SetTargetWindow', 'ViewStart', 'TargetWindow']
    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'import wx.richtext') )
    def properties(self):
        import wx.richtext
        props = WindowDTC.properties(self)
        props.update({'Editable':  ('CtrlRoute', wx.richtext.RichTextCtrl.IsEditable, wx.richtext.RichTextCtrl.SetEditable)})
        return props
    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + ['TargetRect',
              'InternalSelectionRange', 'SelectionRange', 'HandlerFlags',
              'StyleSheet']
    def events(self):
        return WindowDTC.events(self) + ['RichTextEvent']

# Designer support needed to use ComboCtrl directly
# SetPopupControl(wx.SomeComboPopup) must be generated and set
EventCategories['ComboCtrlEvent'] = ('wx.EVT_TEXT', 'wx.EVT_TEXT_ENTER')
commandCategories.append('ComboCtrlEvent')
class ComboCtrlDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.CB_READONLY', 'wx.CB_SORT', 'wx.TE_PROCESS_ENTER',
          'wx.combo.CC_SPECIAL_DCLICK', 'wx.combo.CC_STD_BUTTON'] + self.windowStyles
        self.ctrlDisabled = True

    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'value': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

##    def vetoedMethods(self):
##        return ['GetColumns', 'SetColumns', 'GetSelection', 'SetSelection',
##                'GetStringSelection', 'SetStringSelection']
##
##    def hideDesignTime(self):
##        return ['Label']

    def events(self):
        return WindowDTC.events(self) + ['ComboCtrlEvent']

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'import wx.combo') )

class BitmapComboBoxDTC(ComboCtrlDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ComboCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Items'] = CollectionPropEdit
        self.subCompanions['Items'] = BitmapComboBoxItemsCDTC

class BitmapComboBoxItemsCDTC(CollectionDTC):
    propName = 'Items'
    displayProp = 'item'
    indexProp = 'pos'
    insertionMethod = 'Insert'
    deletionMethod = 'Delete'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Position' : IntConstrPropEdit,
                        'Item': StrConstrPropEdit,
                        'Bitmap': BitmapConstrPropEdit}

    def constructor(self):
        return {'Position': 'pos', 'Item': 'item', 'Bitmap': 'bitmap'}

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Position': ('NoneRoute', None, None),
                      'Item':     ('NoneRoute', None, None),
                      'Bitmap':   ('CompnRoute', self.GetItemBitmap, self.SetItemBitmap)})
        return props

    def designTimeSource(self, wId, method=None):
        return {'pos': `wId`,
                'item': `'%s%d'%(self.propName, wId)`,
                'bitmap': 'wx.NullBitmap'}

    def GetItemBitmap(self):
        return self.control.GetItemBitmap(self.index)

    def SetItemBitmap(self, bitmap):
        self.control.SetItemBitmap(self.index, bitmap)


class SearchCtrlDTC(TextCtrlDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        TextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['SearchButtonVisible'] = BoolPropEdit
        self.editors['CancelButtonVisible'] = BoolPropEdit
        self.ctrlDisabled = True


    def properties(self):
        props = TextCtrlDTC.properties(self)
        props.update({'SearchButtonVisible': ('CtrlRoute',
            wx.SearchCtrl.IsSearchButtonVisible, wx.SearchCtrl.ShowSearchButton),
                      'CancelButtonVisible': ('CtrlRoute',
            wx.SearchCtrl.IsCancelButtonVisible, wx.SearchCtrl.ShowCancelButton)})
        return props


#-------------------------------------------------------------------------------
import Plugins

Plugins.registerPalettePage('BasicControls', _('Basic Controls'))

Plugins.registerComponents('BasicControls',
      (wx.StaticText, 'wx.StaticText', StaticTextDTC),
      (wx.TextCtrl, 'wx.TextCtrl', TextCtrlDTC),
      (wx.Choice, 'wx.Choice', ChoiceDTC),
      (wx.ComboBox, 'wx.ComboBox', ComboBoxDTC),
      (wx.CheckBox, 'wx.CheckBox', CheckBoxDTC),
      (wx.RadioButton, 'wx.RadioButton', RadioButtonDTC),
      (wx.Slider, 'wx.Slider', SliderDTC),
      (wx.Gauge, 'wx.Gauge', GaugeDTC),
      (wx.StaticBitmap, 'wx.StaticBitmap', StaticBitmapDTC),
      (wx.ScrollBar, 'wx.ScrollBar', ScrollBarDTC),
      (wx.StaticBox, 'wx.StaticBox', StaticBoxDTC),
      (wx.StaticLine, 'wx.StaticLine', StaticLineDTC),
      (wx.html.HtmlWindow, 'wx.html.HtmlWindow', HtmlWindowDTC),
      (wx.stc.StyledTextCtrl, 'wx.stc.StyledTextCtrl', StyledTextCtrlDTC),
      (wx.animate.GIFAnimationCtrl, 'wx.animate.GIFAnimationCtrl', GIFAnimationCtrlDTC),
    )

try:
    import wx.richtext
    Plugins.registerComponent('BasicControls', wx.richtext.RichTextCtrl, 'wx.richtext.RichTextCtrl', RichTextCtrlDTC)
except ImportError:
    pass

try:
    import wx.combo
#    Plugins.registerComponent('BasicControls', wx.combo.ComboCtrl, 'wx.combo.ComboCtrl', ComboCtrlDTC)
    Plugins.registerComponent('BasicControls', wx.combo.BitmapComboBox, 'wx.combo.BitmapComboBox', BitmapComboBoxDTC)
except ImportError:
    pass

try:
    import wx.media
    Plugins.registerComponent('BasicControls', wx.media.MediaCtrl, 'wx.media.MediaCtrl', MediaCtrlDTC)
except ImportError:
    pass

try:
    Plugins.registerComponent('BasicControls', wx.SearchCtrl, 'wx.SearchCtrl', SearchCtrlDTC)
except AttributeError:
    pass
