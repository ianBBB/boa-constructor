#-----------------------------------------------------------------------------
# Name:        StyledTextCtrls.py
# Purpose:     Mixin classes to extend wxStyledTextCtrl
#
# Author:      Riaan Booysen
#
# Created:     2000/04/26
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import os, re, keyword

from wxPython.wx import *
from wxPython.stc import *

eols = {  wxSTC_EOL_CRLF : '\r\n',
          wxSTC_EOL_CR : '\r',
          wxSTC_EOL_LF : '\n'}

import Preferences
import methodparse
import STCStyleEditor

# from PythonWin from IDLE :)
_is_block_opener = re.compile(r':\s*(#.*)?$').search
_is_block_closer = re.compile(r'''
    \s*
    ( return
    | break
    | continue
    | raise
    | pass
    )
    \b
''', re.VERBOSE).match


def ver_tot(ma, mi, re):
    return ma*10000+mi*100+re

word_delim  = string.letters + string.digits + '_'
object_delim = word_delim + '.'

#---Utility mixins--------------------------------------------------------------

class FoldingStyledTextCtrlMix:
    def __init__(self, wId, margin):
        self.__fold_margin = margin
        self.SetProperty('fold', '1')
        self.SetMarginType(margin, wxSTC_MARGIN_SYMBOL)
        self.SetMarginMask(margin, wxSTC_MASK_FOLDERS)
        self.SetMarginSensitive(margin, true)
        self.SetMarginWidth(margin, Preferences.STCFoldingMarginWidth)
        markIdnt, markBorder, markCenter = Preferences.STCFoldingOpen
        self.MarkerDefine(wxSTC_MARKNUM_FOLDER, markIdnt, markBorder, markCenter)
        markIdnt, markBorder, markCenter = Preferences.STCFoldingClose
        self.MarkerDefine(wxSTC_MARKNUM_FOLDEROPEN, markIdnt, markBorder, markCenter)


        EVT_STC_MARGINCLICK(self, wId, self.OnMarginClick)

    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == self.__fold_margin:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) & wxSTC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, true)
                        self.Expand(lineClicked, true, true, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, false)
                            self.Expand(lineClicked, false, true, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, true)
                            self.Expand(lineClicked, true, true, 100)
                    else:
                        self.ToggleFold(lineClicked)


    def FoldAll(self):
        lineCount = self.GetLineCount()
        expanding = true

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & wxSTC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break

        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & wxSTC_FOLDLEVELHEADERFLAG and \
               (level & wxSTC_FOLDLEVELNUMBERMASK) == wxSTC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, true)
                    lineNum = self.Expand(lineNum, true)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, false)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1

    def Expand(self, line, doExpand, force=false, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & wxSTC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, true)
                    else:
                        self.SetFoldExpanded(line, false)
                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, true, force, visLevels-1)
                    else:
                        line = self.Expand(line, false, force, visLevels-1)
            else:
                line = line + 1;

        return line

def idWord(line, piv, lineStart, leftDelim = word_delim, rightDelim = word_delim):
    if piv >= len(line):
        return 0, 0
    pivL = pivR = piv
    # Look left
    for pivL in range(piv, -1, -1):
        if not line[pivL] in leftDelim:
            pivL = pivL + 1
            break
    # Look right
    for pivR in range(piv + 1, len(line)):
        if not line[pivR] in rightDelim:
            break
    else:
        pivR = pivR+1

    return pivL + lineStart, pivR - pivL

class BrowseStyledTextCtrlMix:
    """ This class is to be mix-in with a wxStyledTextCtrl to add
        functionality for browsing the code.
    """
    def __init__(self, indicator=0):
##        self.handCrs = wxStockCursor(wxCURSOR_HAND)
##        self.stndCrs = wxStockCursor(wxCURSOR_ARROW)
        self.IndicatorSetStyle(indicator, wxSTC_INDIC_PLAIN)
        self.IndicatorSetForeground(indicator, wxBLUE)
        self._indicator = indicator
        self.styleStart = 0
        self.styleLength = 0
        self.ctrlDown = false
        EVT_MOTION(self, self.OnBrowseMotion)
        EVT_LEFT_DOWN(self, self.OnBrowseClick)
        EVT_KEY_DOWN(self, self.OnKeyDown)
        EVT_KEY_UP(self, self.OnKeyUp)

    def doClearBrwsLn(self):
        self.styleStart, self.styleLength = \
            self.clearUnderline(self.styleStart, self.styleLength)

    def BrowseClick(self, word, line, lineNo, start, style):
        """Called when a link is clicked.
           Override to use, return true if click is swallowed """
        return false

    def StyleVeto(self, style):
        return false

    def underlineWord(self, start, length):
        #self.SetCursor(self.handCrs)
        self.SetLexer(wxSTC_LEX_NULL)

        self.StartStyling(start, wxSTC_INDICS_MASK)
        self.SetStyling(length, wxSTC_INDIC0_MASK)
#        self.Refresh(false)
        return start, length

    def clearUnderline(self, start, length):
        #self.SetCursor(self.stndCrs)

        self.StartStyling(start, wxSTC_INDICS_MASK)
        self.SetStyling(length, 0)
        self.SetLexer(wxSTC_LEX_PYTHON)
        self.Refresh(false)
        return 0, 0

    def getBrowsableText(self, line, piv, lnStPs):
        return idWord(line, piv, lnStPs)

    def OnBrowseMotion(self, event):
        try:
            #check if words should be underlined
            if event.ControlDown():
                mp = event.GetPosition()
                pos = self.PositionFromPoint(wxPoint(mp.x, mp.y))

                stl = self.GetStyleAt(pos) & 31

                if self.StyleVeto(stl):
                    if self.styleLength > 0:
                        self.styleStart, self.styleLength = \
                          self.clearUnderline(self.styleStart, self.styleLength)
                    return

                lnNo = self.LineFromPosition(pos)
                lnStPs = self.PositionFromLine(lnNo)
                line = self.GetLine(lnNo)
                piv = pos - lnStPs
                start, length = self.getBrowsableText(line, piv, lnStPs)
                #mark new
                if length > 0 and self.styleStart != start:
                    if self.styleLength > 0:
                        self.clearUnderline(self.styleStart, self.styleLength)
                    self.styleStart,self.styleLength = \
                      self.underlineWord(start, length)
                #keep current
                elif self.styleStart == start: pass
                #delete previous
                elif self.styleLength > 0:
                    self.styleStart, self.styleLength = \
                      self.clearUnderline(self.styleStart, self.styleLength)

            #clear any underlined words
            elif self.styleLength > 0:
                self.styleStart, self.styleLength = \
                  self.clearUnderline(self.styleStart, self.styleLength)
        finally:
            event.Skip()

    def getStyledWordElems(self, styleStart, styleLength):
        if styleLength > 0:
            lnNo = self.LineFromPosition(styleStart)
            lnStPs = self.PositionFromLine(lnNo)
            line = self.GetLine(lnNo)
            start = styleStart - lnStPs
            word = line[start:start+styleLength]
            return word, line, lnNo, start
        else:
            return '', 0, 0, 0

    def OnBrowseClick(self, event):
        word, line, lnNo, start = self.getStyledWordElems(self.styleStart, self.styleLength)
        if word:
            style = self.GetStyleAt(self.styleStart) & 31
            if self.BrowseClick(word, line, lnNo, start, style):
                return
        event.Skip()

    def OnKeyDown(self, event):
        if event.ControlDown(): self.ctrlDown = true
        event.Skip()

    def OnKeyUp(self, event):
        if self.ctrlDown and (not event.ControlDown()):
            self.ctrlDown = false
            if self.styleLength > 0:
                self.styleStart, self.styleLength = \
                  self.clearUnderline(self.styleStart, self.styleLength)
        event.Skip()

class CodeHelpStyledTextCtrlMix:
    def getCurrLineInfo(self):
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.PositionFromLine(lnNo)
        return (pos, lnNo, lnStPs, 
                self.GetCurLine()[0], pos - lnStPs - 1)

    def getFirstContinousBlock(self, docs):
        res = []
        for line in string.split(docs, '\n'):
            if string.strip(line):
                res.append(line)
            else:
                break
        return string.join(res, '\n')
        

class AutoCompleteCodeHelpSTCMix(CodeHelpStyledTextCtrlMix):

##    def getCodeCompOptions(self, word, rootWord, matchWord, lnNo):
##        return []

    def codeCompCheck(self):
        pos, lnNo, lnStPs, line, piv = self.getCurrLineInfo()

        start, length = idWord(line, piv, lnStPs, object_delim, object_delim)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        pivword = piv - startLine
        
        dot = string.rfind(word, '.', 0, pivword+1)
        matchWord = word
        if dot != -1:
            rdot = string.find(word, '.', pivword)
            if rdot != -1:
                matchWord = word[dot+1:rdot]
            else:
                matchWord = word[dot+1:]
                
            offset = pivword - dot
            rootWord = word[:dot]
        else:
            offset = pivword + 1
            rootWord = ''

        if not matchWord:
            offset = 0

        names = self.getCodeCompOptions(word, rootWord, matchWord, lnNo)
        
        # remove duplicates
        unqNms = {}
        for name in names: unqNms[name] = None
        names = unqNms.keys()

        self.AutoCompShow(offset, string.join(names, ' '))
        self.AutoCompSelect(matchWord)
        
class CallTipCodeHelpSTCMix(CodeHelpStyledTextCtrlMix):
    def __init__(self):
        self.lastCallTip = ''
        self.lastTipHilite = (0, 0)

    def getTipValue(self, word, lnNo):
        return ''
        
    def callTipCheck(self):
        pos, lnNo, lnStPs, line, piv = self.getCurrLineInfo()

        bracket = methodparse.matchbracket(line[:piv+1], '(')
        if bracket == -1 and self.CallTipActive():
            self.CallTipCancel()
            return
        
        cursBrktOffset = piv - bracket
        
        start, length = idWord(line, bracket-1, lnStPs, object_delim, object_delim)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        if word:
            tip = self.getTipValue(word, lnNo)
            if tip:
                # Minus offset of 1st bracket in the tip
                tipBrkt = string.find(tip, '(')
                if tipBrkt != -1:
                    pos = pos - tipBrkt - 1
                else:
                    tipBrkt = 0
                    
                # get the current parameter from source
                paramNo = len(methodparse.safesplitfields(\
                      line[bracket+1:piv+1]+'X', ','))
                if paramNo:
                    paramNo = paramNo - 1
                
                # get hilight & corresponding parameter from tip
                tipBrktEnd = string.rfind(tip, ')')
                tip_param_str = tip[tipBrkt+1:tipBrktEnd]
                tip_params = methodparse.safesplitfields(\
                    tip_param_str, ',', ('(', '{'), (')', '}') )
                try: 
                    hiliteStart = tipBrkt+1 + string.find(tip_param_str, tip_params[paramNo])
                except IndexError: 
                    hilite = (0, 0)
                else:
                    hilite = (hiliteStart, 
                              hiliteStart+len(tip_params[paramNo]))

                # don't update if active and unchanged
                if self.CallTipActive() and tip == self.lastCallTip and \
                      hilite == self.lastTipHilite:
                    return

                # close if active and changed
                if self.CallTipActive() and (tip != self.lastCallTip or \
                      hilite != self.lastTipHilite):
                    self.CallTipCancel()

                self.CallTipShow(pos - cursBrktOffset, tip)

                self.CallTipSetHighlight(hilite[0], hilite[1])
                self.lastCallTip = tip
                self.lastTipHilite = hilite

#---Language mixins-------------------------------------------------------------
class LanguageSTCMix:
    def __init__(self, wId, marginNumWidth, language, config):
        self.language = language
        (cfg, self.commonDefs, self.styleIdNames, self.styles, psgn, psg, olsgn,
              olsg, ds, self.lexer, self.keywords, bi) = \
              STCStyleEditor.initFromConfig(config, language)

        self.SetEOLMode(wxSTC_EOL_LF)
        self.eol = '\n'
        self.SetBufferedDraw(Preferences.STCBufferedDraw)
        self.SetCaretPeriod(Preferences.STCCaretPeriod)

        self.SetViewWhiteSpace(Preferences.STCViewWhiteSpace)
        self.SetViewEOL(Preferences.STCViewEOL)
        
        self.SetIndent(Preferences.STCIndent)
        self.SetUseTabs(Preferences.STCUseTabs)
        self.SetTabWidth(Preferences.STCTabWidth)
        self.SetCaretPeriod(Preferences.STCCaretPeriod)
        if Preferences.STCCaretPolicy:
            self.SetCaretPolicy(Preferences.STCCaretPolicy, 
                                Preferences.STCCaretPolicySlop)

        self.SetEdgeMode(Preferences.STCEdgeMode)
        self.SetEdgeColumn(Preferences.STCEdgeColumnWidth)
        
        if marginNumWidth:
            self.SetMargins(1, 1)
            self.SetMarginType(marginNumWidth[0], wxSTC_MARGIN_NUMBER)
            self.SetMarginWidth(marginNumWidth[0], marginNumWidth[1])

        EVT_STC_UPDATEUI(self, wId, self.OnUpdateUI)

    def setStyles(self, commonOverride=None):
        commonDefs = {}
        commonDefs.update(self.commonDefs)
        if commonOverride is not None:
            commonDefs.update(commonOverride)
            
        STCStyleEditor.setSTCStyles(self, self.styles, self.styleIdNames, 
              commonDefs, self.language, self.lexer, self.keywords)

    def OnUpdateUI(self, event):
        pass

    keymap={'euro': {219: '\\', 57: ']', 56: '[', 55: '{', 337: '~', 226: '|', 
                     81: '@', 48: '}',69: '�',77: '�',50: '�',51: '�'}, 
            'france': {51: '#', 219: ']', 56: '\\', 55: '`', 54: '|', 53: '[', 
                       52: '{', 226: '6', 50: '~', 337: '}', 48: '@'}, 
            'swiss-german': {223: '}', 221: '~', 220: '{', 219: '`', 186: '[', 
                             55: '|', 226: '\\', 51: '#', 50: '@', 192: ']'},
            'italian': {192: '@', 222: '#', 186: '[', 337: ']', 219: '{', 221: '}' },
           }

    def handleSpecialEuropeanKeys(self, event, countryKeymap='euro'):
        key = event.KeyCode()
        keymap = self.keymap[countryKeymap]
        if event.AltDown() and event.ControlDown() and keymap.has_key(key):
            currPos = self.GetCurrentPos()
            self.InsertText(currPos, keymap[key])
            self.SetCurrentPos(self.GetCurrentPos()+1)
            self.SetSelectionStart(self.GetCurrentPos())

stcConfigPath = os.path.join(Preferences.rcPath, 'stc-styles.rc.cfg')

class PythonStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId, margin):
        LanguageSTCMix.__init__(self, wId, margin, 'python', stcConfigPath)

        self.keywords = self.keywords + ' yield true false None'    
        
        self.setStyles()

    def grayout(self, do):
        if not Preferences.grayoutSource: return
        if do: f = {'backcol': '#EEF2FF'}
        else: f = None
        self.setStyles(f)

    def OnUpdateUI(self, event):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            try:
                charBefore = chr(self.GetCharAt(caretPos - 1))
            except ValueError:
                charBefore = ''
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and charBefore in "[]{}()" and styleBefore == 10:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            try:
                charAfter = chr(self.GetCharAt(caretPos))
            except ValueError:
                charAfter = ''
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and charAfter in "[]{}()" and styleAfter == 10:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1 and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            # self.Refresh(false)
    
    def doAutoIndent(self, prevline, pos):
        stripprevline = string.strip(prevline)
        if stripprevline:
            indent = prevline[:string.find(prevline, stripprevline)]
        else:
            indent = prevline[:-1]

        if self.GetUseTabs():
            indtBlock = '\t'
        else:
            indtBlock = self.GetTabWidth()*' '

        if _is_block_opener(prevline):
            indent = indent + indtBlock
        elif _is_block_closer(prevline):
            indent = indent[:-1*len(indtBlock)]
            
        self.BeginUndoAction()
        try:
            self.InsertText(pos, indent)
            self.GotoPos(pos + len(indent))
        finally:
            self.EndUndoAction()    

class BaseHTMLStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, 
              (0, Preferences.STCLineNumMarginWidth), 'html', stcConfigPath)

class HTMLStyledTextCtrlMix(BaseHTMLStyledTextCtrlMix):
    def __init__(self, wId):
        BaseHTMLStyledTextCtrlMix.__init__(self, wId)
        self.setStyles()

class XMLStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, 
              (0, Preferences.STCLineNumMarginWidth), 'xml', stcConfigPath)
        self.setStyles()

class CPPStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, 
              (0, Preferences.STCLineNumMarginWidth), 'cpp', stcConfigPath)
        self.setStyles()

class TextSTCMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, (), 'text', stcConfigPath)
        self.setStyles()
        
class ConfigSTCMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, (), 'prop', stcConfigPath)
        self.setStyles()

from types import IntType, SliceType, StringType
class STCLinesList:
    def __init__(self, STC):
        self.__STC = STC
    
    def _rememberPos(self):
        self.__pos = self.GetCurrentPos()

    def __getitem__(self, key):
        if type(key) is IntType:
            # XXX last char is garbage
            if key < len(self):
                return self.__STC.GetLine(key)[:-1]
            else:
                raise IndexError
        elif type(key) is SliceType:
            res = []
            for idx in range(key.start, key.stop):
                res.append(self[idx])
            return res
        else:
            raise TypeError, '%s not supported' % `type(key)`

    def __setitem__(self, key, value):
        stc = self.__STC
        if type(key) is IntType:
            assert type(value) is StringType
            if key < len(self):
                stc.SetSelection(stc.PositionFromLine(key), stc.GetLineEndPosition(key))
                stc.ReplaceSelection(value)
            else:
                raise IndexError
        elif type(key) is SliceType:
            lines = string.join(value, eols[stc.GetEOLMode()])
            stc.SetSelection(stc.PositionFromLine(key.start),
                  stc.GetLineEndPosition(key.stop))
            stc.ReplaceSelection(lines)
        else:
            raise TypeError, '%s not supported' % `type(key)`

    def __delitem__(self, key):
        stc = self.__STC
        if type(key) is IntType:
            stc.SetSelection(stc.PositionFromLine(key), stc.GetLineEndPosition(key)+1)
            stc.ReplaceSelection('')
        elif type(key) is SliceType:
            stc.SetSelection(stc.PositionFromLine(key.start),
                  stc.GetLineEndPosition(key.stop)+1)
            stc.ReplaceSelection('')
        else:
            raise TypeError, '%s not supported' % `type(key)`
    
    def __getattr__(self, name):
        if name == 'current':
            return self.__STC.GetCurrentLine()
        if name == 'count':
            return self.__STC.GetLineCount()
        if name == 'size':
            return self.__STC.GetTextLength()
        # dubious
        if name == 'line':
            return self.__STC.GetCurLine()[0]
        # dubious
        if name == 'pos':
            return self.__STC.GetCurrentPos()
        
        raise AttributeError, name

    def __len__(self):
        return self.__STC.GetLineCount()

  