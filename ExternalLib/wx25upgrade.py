# -*- coding: iso-8859-1 -*-#
#-----------------------------------------------------------------------------
# Name:        wx25upgrade.py
# Purpose:     Upgrade code from 2.4 style to 2.5
#
# Author:      Paul Sorenson
# Contrib.:    Werner F. Bruhin
#              Riaan Booysen
#
# Special thanks to Paul McGuire for his help!
#
# Created:     Feb 2005
# RCS-ID:      $Id$
#-----------------------------------------------------------------------------
#
# WARNING - changes files, take care!
#
# requires: pyparsing
# usage: python wx25upgrade myFrame.py > myNewFrame.py
#
# There are three dictionaries which allow for easy conversion for addtional
# converstions, update the key section with the 2.4 name and the value with the
# 2.5 name.
#
# self.importNames, for import statements
# self.specialNames, for classes, e.g. 'GenButton': 'wx.lib.buttons.GenButton'
# self.specialNames2, for other names, e.g. 'wxGrid.wxGrid': 'wx.grid.Grid.wxGrid'
# 
# This file currently munges the 
# - EVT_xxx change from wxPython 2.4 style to 2.5/2.6 style
# - .Append for menu, changes 'helpString' to 'help', 'item' to 'text' and
#   wxITEM to wx.ITEM
# - changes the 'map(lambda _init_whatever: wxNewId()' to the new format
# - changes the classes from wxName to wx.Name
#   check "self.specialNames" to see which special cases are handled
# - changes the 'init' from wxName.__init to wx.Name.__init
#   check "self.importNames" to see which imports are handled
# - true and false to True and False
# - SetStatusText "(i=" keyword to "(number="
# - AddSpacer "n, n" to wx.Size(n, n)
# - flag= i.e. flag=wxALL
# - style= i.e. style=wxDEFAULT_DIALOG_STYLE
# - orient=wx to orient=wx.
# - kind=wx to kind=wx.
# - wxFont(8,wxSWISS,wxNORMAL,wxNORMAL to wx.Font(8,wx.SWISS,wx.NORMAL,wx.NORMAL
# - _custom_classes are changed
#
#
# A lot is converted however manual inspection and correction of code
# IS STILL REQUIRED!

from pyparsing import *
import string
import copy
import importlib


def lit(text):
    '''For when you want to return a literal value independent of the input'''
    def _lit(s, l, t):
        return text
    return _lit

# parse action to remove quotation marks from quoted strings
# used e.g. for customClasses
# Thanks to Paul McGuire
def stripQuotes(s,l,t):
    return t[0][1:-1]


class Upgrade:
    def __init__(self):
        # Set to True if you want to convert non Boa generated events
        # which contain "control.GetId()"
        specialEventCode = True
        self.specialNames = {"GenButton": "wx.lib.buttons.GenButton",
                             "StyledTextCtrl": "wx.stc.StyledTextCtrl",
                             "GenStaticText": "wx.lib.stattext.GenStaticText",
                             "MaskedComboBox": "wx.lib.masked.combobox.ComboBox",
                             "MaskedTextCtrl": "wx.lib.masked.textctrl.TextCtrl",
                             "IpAddrCtrl": "wx.lib.masked.ipaddrctrl.IpAddrCtrl",
                             "MaskedNumCtrl": "wx.lib.masked.numctrl.NumCtrl",
                             "TimeCtrl": "wx.lib.masked.timectrl.TimeCtrl",
                             "IntCtrl": "wx.lib.intctrl.IntCtrl",
                             "PyGridTableBase": "wx.grid.PyGridTableBase",
                             "PyGridCellRenderer": "wx.grid.PyGridCellRenderer",
                             "GridTableMessage": "wx.grid.GridTableMessage",
                             "Grid": "wx.grid.Grid",
                             "EditableListBox": "wx.adv.EditableListBox",
                             "TreeListCtrl": "wx.gizmos.TreeListCtrl",
                             "ListCtrlAutoWidthMixin": "listmix.ListCtrlAutoWidthMixin",
                             "ColumnSorterMixin": "listmix.ColumnSorterMixin",
                             }

        self.specialNames2 = {"wxInitAllImageHandlers" : "wx.InitAllImageHandlers",
                              "wxIcon" : "wx.Icon",
                              "wxBITMAP" : "wx.BITMAP",
                              "wxBitmap" : "wx.Bitmap",
                              "wxSize" : "wx.Size",
                              "wxNullBitmap": "wx.NullBitmap",
                              "wxPoint": "wx.Point",
                              "wxNewId": "wx.NewId",
                              "wxColour": "wx.Colour",
                              "wxOPEN": "wx.FD_OPEN",
                              "wxRED": "wx.RED",
                              "wxBLUE": "wx.BLUE",
                              "wxGREEN": "wx.GREEN",
                              "wxBLACK": "wx.BLACK",
                              "wxWHITE": "wx.WHITE",
                              "wxGridTable": "wx.grid.GridTable",
                              "wxGRIDTABLE": "wx.grid.GRIDTABLE",
                              "wxGrid.wxGrid": "wx.grid.Grid.wxGrid",
                              "wxGRID": "wx.grid.GRID",
                              "wxACCEL": "wx.ACCEL",
                              "wxAcceleratorTable": "wx.AcceleratorTable",
                              "wxTheClipboard": "wx.TheClipboard",
                              "wxOK": "wx.OK",
                              "wxICON_": "wx.ICON_",
                              "wxPySimpleApp": "wx.PySimpleApp",
                              "wxYES_NO": "wx.YES_NO",
                              "wxYES": "wx.YES",
                              "wxNO": "wx.NO",
                              "wxCANCEL": "wx.CANCEL",
                              "wxYES_DEFAULT": "wx.YES_DEFAULT",
                              "wxNO_DEFAULT": "wx.NO_DEFAULT",
                              "wxID_YES": "wx.ID_YES",
                              "wxID_NO": "wx.ID_NO",
                              "wxID_OK": "wx.ID_OK",
                              "wxID_CANCEL": "wx.ID_CANCEL",
                              "wxCallAfter": "wx.CallAfter",
                              "wxDefault": "wx.Default",
                              "wxNamedColor": "wx.NamedColor",
                              "wxIMAGE": "wx.IMAGE",
                              "wxLIST": "wx.LIST",
                              "WXK_": "wx.WXK_",
                              "wxTL_": "wx.gizmos.TL_",
                              "wxBeginBusyCursor": "wx.BeginBusyCursor",
                              "wxEndBusyCursor": "wx.EndBusyCursor",
                              "wxMessageBox": "wx.MessageBox",
                              "wxTreeList": "wx.gizmos.TreeList",
                              "wxPD_": "wx.PD_",
                              "wxEmptyBitmap": "wx.EmptyBitmap",
                              "wxCOPY": "wx.COPY",
                              "wxImage": "wx.Image",
                              "wxWave": "wx.Sound",
                              "wxUsleep": "wx.Usleep",
                              "wxSafeYield": "wx.SafeYield",
                              "wxYield": "wx.Yield",
                              "wxToolTip": "wx.ToolTip",
                              "wxCAP_": "wx.CAP_",
                              "wxJOIN_": "wx.JOIN_",
                              "wxSHORT_DASH": "wx.SHORT_DASH",
                              "wxDOT_DASH": "wx.DOT_DASH",
                              "wxDOT": "wx.DOT",
                              "wxSAVE": "wx.SAVE",
                              "wxOVERWRITE_PROMPT": "wx.OVERWRITE_PROMPT",
                              "wxCHANGE_DIR": "wx.CHANGE_DIR",
                              "wxMULTIPLE": "wx.MULTIPLE",
                              "wxSOLID": "wx.SOLID",
                              "wxLIGHT": "wx.LIGHT",
                              "wxNORMAL": "wx.NORMAL",
                              "wxBOLD": "wx.BOLD",
                              "wxTRANSPARENT": "wx.TRANSPARENT",
                              "wxITALIC": "wx.ITALIC",
                              "wxSLANT": "wx.SLANT",
                              "wxSWISS": "wx.SWISS",
                              "wxROMAN": "wx.ROMAN",
                              "wxSCRIPT": "wx.SCRIPT",
                              "wxDECORATIVE": "wx.DECORATIVE",
                              "wxMODERN": "wx.MODERN",
                              "wxCURSOR_": "wx.CURSOR_",
                              "wxPen": "wx.Pen",
                              "wxPlatformInfo": "wx.PlatformInfo",
                              "wxLeft": "wx.Left",
                              "wxRight": "wx.Right",
                              "wxBrush": "wx.Brush",
                              "wxLogError": "wx.LogError",
                              "wxLogMessage": "wx.LogMessage",
                              "wxLogInfo": "wx.LogInfo",
                              "wxLogWarning": "wx.LogWarning",
                              "wxPlatform": "wx.Platform",
                              "wxPostEvent": "wx.PostEvent",
                              "wxArtProvider_": "wx.ArtProvider.",
                              "wxART_": "wx.ART_",
                              "wxTreeItemIcon_": "wx.TreeItemIcon_",
                              "wxVERTICAL": "wx.VERTICAL",
                              "wxHORIZONTAL": "wx.HORIZONTAL",
                              "wxALL": "wx.ALL",
                              "wxTOP": "wx.TOP",
                              "wxBOTTOM": "wx.BOTTOM",
                              "wxRIGHT": "wx.RIGHT",
                              "wxLEFT": "wx.LEFT",
                              "wxEXPAND": "wx.EXPAND",
                              "wxSHAPED": "wx.SHAPED",
                              "wxGROW": "wx.GROW",
                              "wxFIXED_MINSIZE": "wx.FIXED_MINSIZE",
                              "wxALIGN_CENTER": "wx.ALIGN_CENTER",
                              "wxALIGN_LEFT": "wx.ALIGN_LEFT",
                              "wxALIGN_RIGHT": "wx.ALIGN_RIGHT",
                              "wxALIGN_TOP": "wx.ALIGN_TOP",
                              "wxALIGN_BOTTOM": "wx.ALIGN_BOTTOM",
                              "wxALIGN_CENTER_VERTICAL": "wx.ALIGN_CENTER_VERTICAL",
                              "wxALIGN_CENTER_HORIZONTAL": "wx.ALIGN_CENTER_HORIZONTAL",                             
                              }

        self.importNames = {"wx": "import wx",
                            "stc": "import wx.stc",
                            "gizmos": "import wx.gizmos",
                            "grid": "import wx.grid",
                            "lib.buttons": "import wx.lib.buttons",
                            "lib.stattext": "import wx.lib.stattext",
                            "lib.maskededit": "import wx.lib.masked.maskededit",
                            "lib.maskededit": "import wx.lib.masked.maskededit",
                            "lib.maskednumctrl": "import wx.lib.masked.numctrl",
                            "lib.timectrl": "import wx.lib.timectrl",
                            "lib.intctrl": "import wx.lib.intctrl",
                            "html": "import wx.html",
                            "intctrl": "import wx.lib.intctrl",
                            "lib.mixins.listctrl": "import wx.lib.mixins.listctrl as listmix"
                            }

        COMMA = Suppress(",")
        LPAREN = Suppress("(")
        RPAREN = Suppress(")")
        EQ = Suppress("=")

        LBRACE = Suppress("{")
        RBRACE = Suppress("}")
        LBRACK = Suppress("[")
        RBRACK = Suppress("]")
        COLON  = Suppress(":")

        ident = Word(alphas+"_",alphanums+"_")
        uident = Word(string.ascii_uppercase+"_")        
        qualIdent = Word(alphas+"_",alphanums+"_.")
        qualIdent2 = Word(alphas+"_",alphanums+"_.()")
        intOnly = Word(nums)
        uident2 = Word(string.ascii_uppercase+"_",string.ascii_uppercase+"_123456789")
        
        wxExp = Suppress("wx")
        flagExp = (wxExp+uident2)
        flags = delimitedList(flagExp, delim="|")
        
        # 2 Parameter evt macros.
        evt_P2 = Literal("EVT_") + uident + LPAREN +\
            qualIdent + COMMA +\
            qualIdent +\
            RPAREN
        evt_P2.setParseAction(self.evt_P2Action)

        # 3 Parameter evt macros.
        evt_P3 = Literal("EVT_") + uident + LPAREN +\
            qualIdent + COMMA +\
            qualIdent + COMMA +\
            qualIdent +\
            RPAREN
        evt_P3.setParseAction(self.evt_P3Action)

        # 3 Parameter evt macros.
        #   specialEventCode = True required
        #   event codes containing "control.GetId()" in code
        evt_P3a = Literal("EVT_") + uident + LPAREN +\
            qualIdent + COMMA +\
            qualIdent2 + COMMA +\
            qualIdent +\
            RPAREN
        evt_P3a.setParseAction(self.evt_P3aAction)

        # Append keyword args
        unicodeString = Literal("u") + quotedString
        karg = ident + EQ + ((quotedString | unicodeString) | ident)
        append = Suppress(".Append") \
            + LPAREN + karg + COMMA + karg + COMMA \
            + karg + COMMA + karg + RPAREN
        append.setParseAction(self.appendAction)

        # wxFont
        wxfont = Suppress("wxFont") + LPAREN + \
                        intOnly + COMMA + ident + COMMA + ident + COMMA + \
                        ident
        wxfont.setParseAction(self.wxfontAction)

        # SetStatusText keyword args
        setStatusText = Suppress(".SetStatusText") \
            + LPAREN + ident + EQ + intOnly
        setStatusText.setParseAction(self.setStatusTextAction)

        # AddSpacer keyword args
        addSpacer = Suppress(".AddSpacer") \
            + LPAREN + intOnly + COMMA + intOnly
        addSpacer.setParseAction(self.addSpacerAction)

        # Flags
        flags = OneOrMore( oneOf( "flag style orient kind" ) + "=" ) + flags
        flags.setParseAction(self.flagsAction)

        # map(lambda... to wx.NewIdRef(count=1) for etc
        RANGE = Suppress("range") + Suppress("(")
        COL = Suppress(":")
        repId1 = Suppress("map(lambda") + qualIdent2 + COL \
                + qualIdent2 + COMMA + RANGE + intOnly + RPAREN + RPAREN
        repId1.setParseAction(self.repId1Action)
        
        # import
        imp = Literal("from wxPython.") + delimitedList(ident,".",combine=True)\
                + Literal("import") + restOfLine
        importlib.setParseAction(self.impAction)

        # Specific name space changes
        repWXSpec = Or(map(Literal, self.specialNames2.keys()))
        repWXSpec.setParseAction(self.repNamespace)

        # wx to wx. e.g. wxFrame1(wxFrame)to wxFrame1(wx.Frame)
        repWX = Literal("(") + Literal("wx") + ident + ")"
        repWX.setParseAction(self.repWXAction)
        
        # wx to wx. e.g. self.panel1 = wxPanel to self.Panel1 = wx.Panel
        repWX2 = Literal("=") + Literal("wx") + ident + "(" 
        repWX2.setParseAction(self.repWX2Action)
        
        # init wx to wx.
        repWX3 = Literal("wx") + ident + ".__"
        repWX3.setParseAction(self.repWX3Action)

        # Multiple class inheritance, e.g. (wxListCtrl, wxListCtrlAutoWidthMixin)
        repWX4 = Literal("(wx") + ident + COMMA + ident + RPAREN
        repWX4.setParseAction(self.repWX4Action)

        # true to True
        repTrue = Literal("true")
        repTrue.setParseAction(lit("True"))

        # false to False
        repFalse = Literal("false")
        repFalse.setParseAction(lit("False"))
        
        # custom_classes
        # Special thanks to Paul McGuire
        removeQuotes = copy.copy(quotedString).setParseAction(stripQuotes)        
        # Define expressions for the keys and values in the input list data - may
        # need to expand the allowed contents
        # of the delimitedList in dictVal, depending on occurrence of real numbers,
        # booleans, nested lists, etc.
        dictKey = quotedString
        dictVal = Group( LBRACK + delimitedList( removeQuotes | intOnly ) + RBRACK )
        custClass = Literal("_custom_classes") + EQ + \
                    LBRACE+ dictOf( dictKey, COLON + dictVal + Optional(COMMA)
                        ).setResultsName("dictData") + RBRACE

        custClass.setParseAction(self.custClassAction)

        self.grammar = evt_P2 | evt_P3 | append | wxfont\
            | setStatusText | addSpacer | flags | repId1 | imp\
            | repWXSpec | repWX | repWX2 | repWX3 | repWX4\
            | repTrue | repFalse | custClass 
             
        if specialEventCode:
            self.grammar ^= evt_P3a 

    def evt_P2Action(self, s, l, t):
        ev, evname, win, fn = t
        module = "wx"
        if evname.find("GRID") != -1:
            module += ".grid"
        return "%s.Bind(%s.%s%s, %s)" % (win, module, ev, evname, fn)

    def evt_P3Action(self, s, l, t):
        ev, evname, win, id, fn = t
        return "%s.Bind(wx.%s%s, %s, id=%s)" % (win, ev, evname, fn, id)

    def evt_P3aAction(self, s, l, t):
        ev, evname, win, id, fn = t
        return "%s.Bind(wx.%s%s, %s, id=%s)" % (win, ev, evname, fn, id)

##    def appendAction(self, s, l, t):
##        # tokens assumed to be in keyword, arg pairs in sequence
##        subs = {"helpString": "help", "item": "text"}
##        skipOne = False
##        arglist = []
##        for i in range(0, len(t), 1):
##            if skipOne == True:
##                skipOne = False
##            else:
##                kw, arg = t[i:i+2]
##                if arg == 'u':
##                    arg = 'u' + t[i+2:i+3][0]
##                    skipOne = True
##                try:
##                    kw = subs[kw]
##                except:
##                    pass
##                if kw == "kind":
##                    arg = arg.replace("wx", "wx.")
##                arglist.append("%s=%s" % (kw, arg))
##        return ".Append(" + string.join(arglist, ", ") + ")"
    def appendAction(self, s, l, t):
        # tokens assumed to be in keyword, arg pairs in sequence
        subs = {"helpString": "help", "item": "text"}
        arglist = []
        i = 0
        while i < len(t):
            kw, arg = t[i:i+2]
            if arg == 'u':
                arg = 'u' + t[i+2:i+3][0]
                i = i+3
            else:
                i = i+2
            try:
                kw = subs[kw]
            except:
                pass
            if kw == "kind":
                arg = arg.replace("wx", "wx.")
            arglist.append("%s=%s" % (kw, arg))
        return ".Append(" + string.join(arglist, ", ") + ")"

    def wxfontAction(self, s, l, t):
        a, b, c, d = t
        b = b.replace("wx", "wx.")
        c = c.replace("wx", "wx.")
        d = d.replace("wx", "wx.")
        return "wx.Font("+a+","+b+","+c+","+d

    def setStatusTextAction(self, s, l, t):
        a, b = t
        return ".SetStatusText(" + "number" + "=" + b

    def addSpacerAction(self, s, l, t):
        a, b = t
        return ".AddSpacer(wx.Size("+a+","+b+")"
    
    def flagsAction(self, s, l, t):
        return t[0] + t[1] + "wx." + string.join(t[2:], " | wx.")

    def repId1Action(self, s, l, t):
        a, b, c = t
        return "[wx.NewIdRef(count=1) for "+a+" in range("+c+")]"

    def impAction(self, s, l, t):
        a, b, c, d = t
        try:
            newImport = self.importNames[b]
            return newImport
        except KeyError:
            return a+b+" "+c +d

    def repNamespace(self, s, l, t):
        return self.specialNames2[t[0]]

    def repWXAction(self, s, l, t):
        if len(t) == 1:
            return
        else:
            a, b, c, d = t
            try:
                newWX = self.specialNames[c]
                return "("+newWX+d
            except KeyError:
                return "(wx."+c+d

    def repWX2Action(self, s, l, t):
        a, b, c, d = t
        try:
            newWX = self.specialNames[c]
            return a +newWX +d
        except KeyError:
            return a +" wx." +c +d

    def repWX3Action(self, s, l, t):
        a, b, c = t
        try:
            newWX = self.specialNames[b]
            return newWX +c
        except KeyError:
            return "wx." +b +c

    def repWX4Action(self, s, l, t):
        a, b, c = t
        try:
            b = self.specialNames[b]
        except KeyError:
            b = "wx."+b
        try:
            c = c.replace("wx", "")
            c = self.specialNames[c]
        except KeyError:
            c = "wx."+c
        return "("+b +", " +c +")"

    def custClassAction(self, s, l, t):
        res = "_custom_classes" + " = {"
        dictTokens = t.dictData
        for k in dictTokens.keys():
            res = res + k.replace("wx", "wx.")  + ": "
            res = res + str(dictTokens[k])
            res = res + ","
        res = res + "}"
        return res

    def upgrade(self, intext):
        '''Upgrade the text from wx2.4 style to wx2.5/2.6'''
        return self.grammar.transformString(intext)

if __name__ == "__main__":
    import sys
    u = Upgrade()
    if len(sys.argv) < 2:
        print ("usage: python wx25update.py <boafile>")
        sys.exit(1)
    filename = sys.argv[1]
    # fin = file(filename, "r")
    fin = open(filename, "r")
    try:
        print (u.upgrade(fin.read()))
    finally:
        fin.close()