#----------------------------------------------------------------------
# Name:        Enumerations.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
import wx
from wx import adv
from wx import Dialog
# from wxCompat import wxNO_3D

def reverseDict(dict):
    rev = {}
    for k in dict.keys():
        rev[dict[k]] = k
    return rev

# windowStyles =[wx.CAPTION, wx.MINIMIZE_BOX, wx.MAXIMIZE_BOX, THICK_FRAME,
windowStyles =[wx.CAPTION, wx.MINIMIZE_BOX, wx.MAXIMIZE_BOX,
wx.SIMPLE_BORDER, wx.DOUBLE_BORDER, wx.SUNKEN_BORDER, wx.RAISED_BORDER,
wx.STATIC_BORDER, wx.TRANSPARENT_WINDOW, wx.TAB_TRAVERSAL, wx.VSCROLL,
wx.HSCROLL, wx.CLIP_CHILDREN]

windowNameStyles = {'wx.CAPTION':wx.CAPTION, 'wx.MINIMIZE_BOX':wx.MINIMIZE_BOX,
# 'wx.MAXIMIZE_BOX':wx.MAXIMIZE_BOX, 'THICK_FRAME':THICK_FRAME,
'wx.MAXIMIZE_BOX':wx.MAXIMIZE_BOX,
'wx.SIMPLE_BORDER':wx.SIMPLE_BORDER, 'wx.DOUBLE_BORDER':wx.DOUBLE_BORDER,
'wx.SUNKEN_BORDER':wx.SUNKEN_BORDER, 'wx.RAISED_BORDER':wx.RAISED_BORDER,
'wx.STATIC_BORDER':wx.STATIC_BORDER, 'wx.TRANSPARENT_WINDOW':wx.TRANSPARENT_WINDOW,
'wx.TAB_TRAVERSAL':wx.TAB_TRAVERSAL, 'wx.VSCROLL':wx.VSCROLL,
'wx.HSCROLL':wx.HSCROLL, 'wx.CLIP_CHILDREN':wx.CLIP_CHILDREN}

# if hasattr(wx, 'NO_3D'):
    # windowNameStyles.update({'wx.NO_3D':wxNO_3D})
# elif hasattr(wx, 'wxNO_3D'):
    # windowNameStyles.update({'wx.wxNO_3D':wxNO_3D})

# Fonts
fontFamily = [wx.FONTFAMILY_DEFAULT, wx.FONTFAMILY_DECORATIVE, wx.FONTFAMILY_ROMAN,
              wx.FONTFAMILY_SCRIPT, wx.FONTFAMILY_SWISS, wx.FONTFAMILY_MODERN]
fontFamilyNames = {'wx.DEFAULT':wx.FONTFAMILY_DEFAULT, 'wx.DECORATIVE':wx.FONTFAMILY_DECORATIVE,
                   'wx.ROMAN':wx.FONTFAMILY_ROMAN, 'wx.SCRIPT':wx.FONTFAMILY_SCRIPT,
                   'wx.SWISS':wx.FONTFAMILY_SWISS, 'wx.MODERN':wx.FONTFAMILY_MODERN}
fontStyle = [wx.FONTSTYLE_NORMAL, wx.FONTSTYLE_SLANT, wx.FONTSTYLE_ITALIC]
fontStyleNames = {'wx.NORMAL':wx.FONTSTYLE_NORMAL, 'wx.SLANT':wx.FONTSTYLE_SLANT, 'wx.ITALIC':wx.FONTSTYLE_ITALIC}
fontWeight = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
fontWeightNames = {'wx.NORMAL':wx.FONTWEIGHT_NORMAL, 'wx.LIGHT':wx.FONTWEIGHT_LIGHT,
                   'wx.BOLD':wx.FONTWEIGHT_BOLD}

splitterWindowSplitMode = [1, 2]
splitterWindowSplitModeNames = {'wx.SPLIT_HORIZONTAL': 1,
                                'wx.SPLIT_VERTICAL': 2}

constraintEdges = ['wx.Left', 'wx.Right', 'wx.Top', 'wx.Bottom', 'wx.Height',
                   'wx.Width', 'wx.CentreX', 'wx.CentreY']
constraintRelationships = ['wx.Unconstrained', 'wx.AsIs', 'wx.Above', 'wx.Below',
                           'wx.LeftOf', 'wx.RightOf', 'wx.SameAs', 'wx.PercentOf',
                           'wx.Absolute']

formatStyle = ['wx.LIST_FORMAT_LEFT', 'wx.LIST_FORMAT_RIGHT','wx.LIST_FORMAT_CENTRE',
               'wx.LIST_FORMAT_CENTER']

sashLayoutOrientation = [wx.adv.LAYOUT_HORIZONTAL, wx.adv.LAYOUT_VERTICAL]
sashLayoutOrientationNames = {'wx.adv.LAYOUT_HORIZONTAL' : wx.adv.LAYOUT_HORIZONTAL,
                              'wx.adv.LAYOUT_VERTICAL' : wx.adv.LAYOUT_VERTICAL}

sashLayoutAlignment = [wx.adv.LAYOUT_NONE, wx.adv.LAYOUT_TOP, wx.adv.LAYOUT_LEFT, wx.adv.LAYOUT_RIGHT,
                       wx.adv.LAYOUT_BOTTOM]
sashLayoutAlignmentNames = {'wx.adv.LAYOUT_NONE' : wx.adv.LAYOUT_NONE,
                            'wx.adv.LAYOUT_TOP' : wx.adv.LAYOUT_TOP,
                            'wx.adv.LAYOUT_LEFT' : wx.adv.LAYOUT_LEFT,
                            'wx.adv.LAYOUT_RIGHT' : wx.adv.LAYOUT_RIGHT,
                            'wx.adv.LAYOUT_BOTTOM' : wx.adv.LAYOUT_BOTTOM}

wxStockIds = [
    'wx.ID_ADD', 'wx.ID_APPLY', 'wx.ID_BOLD', 'wx.ID_CANCEL', 'wx.ID_CLEAR', 
    'wx.ID_CLOSE', 'wx.ID_COPY', 'wx.ID_CUT', 'wx.ID_DELETE', 'wx.ID_FIND', 
    'wx.ID_REPLACE', 'wx.ID_BACKWARD', 'wx.ID_DOWN', 'wx.ID_FORWARD',
    'wx.ID_UP', 'wx.ID_HELP', 'wx.ID_HOME', 'wx.ID_INDENT', 'wx.ID_INDEX',
    'wx.ID_ITALIC', 'wx.ID_JUSTIFY_CENTER', 'wx.ID_JUSTIFY_FILL',
    'wx.ID_JUSTIFY_LEFT', 'wx.ID_JUSTIFY_RIGHT', 'wx.ID_NEW', 'wx.ID_NO',
    'wx.ID_OK', 'wx.ID_OPEN', 'wx.ID_PASTE', 'wx.ID_PREFERENCES','wx.ID_PRINT',
    'wx.ID_PREVIEW', 'wx.ID_PROPERTIES', 'wx.ID_EXIT', 'wx.ID_REDO',
    'wx.ID_REFRESH', 'wx.ID_REMOVE', 'wx.ID_REVERT_TO_SAVED', 'wx.ID_SAVE',
    'wx.ID_SAVEAS', 'wx.ID_STOP', 'wx.ID_UNDELETE', 'wx.ID_UNDERLINE', 
    'wx.ID_UNDO', 'wx.ID_UNINDENT', 'wx.ID_YES', 'wx.ID_ZOOM_100', 
    'wx.ID_ZOOM_FIT', 'wx.ID_ZOOM_IN', 'wx.ID_ZOOM_OUT',
]

class BinarySet:
    def __init__(self, elements, names, set):
        self.elements = elements
        self.names = names
        self.revNames = reverseDict(names)

        self.set = set

    def getBinaryValue(self):
        v = 0
        for i in self.set:
            v = v + i
        return v

    def setBinaryValue(self, value):
        self.set = []
        for i in self.elements:
            if i & value:
                self.set.append(i)

    def add(self, elementName):
        element = self.names[elementName]
        self.remove(element)
        self.set.append(element)

    def remove(self, elementName):
        element = self.names[elementName]
        try:
            self.set.remove(element)
        except:
            pass

    def has_element(self, elementName):
        element = self.names[elementName]
        for i in self.set:
            if i == element:
                return True
        return False

    def values(self):
        v = []
        for i in self.elements:
            v.append([self.names[i], self.has_element(self.revNames[i])])
        return v
