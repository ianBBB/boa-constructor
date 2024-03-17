#----------------------------------------------------------------------
# Name:        Companions.py
# Purpose:     Classes defining and implementing the design time
#              behaviour of controls
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

""" Classes defining and implementing the design time behaviour of controls """

import wx

from wx.lib.anchors import LayoutAnchors

from PropEdit import PropertyEditors
from PropEdit.Enumerations import *
from .BaseCompanions import HelperDTC

import PaletteStore, RTTI

#---Helpers---------------------------------------------------------------------

class FontDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'FaceName'  : PropertyEditors.EnumPropEdit,
                        'Family'    : PropertyEditors.EnumPropEdit,
                        'Style'     : PropertyEditors.EnumPropEdit,
                        'Weight'    : PropertyEditors.EnumPropEdit,
                        'Underlined': PropertyEditors.BoolPropEdit,}

        fontEnum = wx.FontEnumerator()
        fontEnum.EnumerateFacenames()
        fontNameList = fontEnum.GetFacenames()
        fontFaceName = []
        fontFaceNameNames = {}
        for fnt in fontNameList:
            fontFaceName.append(fnt)
            fontFaceNameNames[fnt] = fnt
        fontFaceName.sort()

        self.options = {'FaceName' : fontFaceName,
                        'Family'   : fontFamily,
                        'Style'    : fontStyle,
                        'Weight'   : fontWeight,}
        self.names = {'FaceName' : fontFaceNameNames,
                      'Family'   : fontFamilyNames,
                      'Style'    : fontStyleNames,
                      'Weight'   : fontWeightNames,}

    def hideDesignTime(self):
        return HelperDTC.hideDesignTime(self) + ['Encoding', 'NativeFontInfo',
               'NativeFontInfoUserDesc', 'NoAntiAliasing']

class ColourDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'Red'    : PropertyEditors.IntPropEdit,
                        'Green'  : PropertyEditors.IntPropEdit,
                        'Blue'   : PropertyEditors.IntPropEdit,}
    def properties(self):
        return {'Red'  : ('CompnRoute', self.GetRed, self.SetRed),
                'Green': ('CompnRoute', self.GetGreen, self.SetGreen),
                'Blue' : ('CompnRoute', self.GetBlue, self.SetBlue),}

    def GetRed(self, cmpn):
        return self.obj.Red()
    def SetRed(self, value):
        self.obj.Set(max(min(value, 255), 0), self.obj.Green(), self.obj.Blue())

    def GetGreen(self, cmpn):
        return self.obj.Green()
    def SetGreen(self, value):
        self.obj.Set(self.obj.Red(), max(min(value, 255), 0), self.obj.Blue())

    def GetBlue(self, cmpn):
        return self.obj.Blue()
    def SetBlue(self, value):
        self.obj.Set(self.obj.Red(), self.obj.Green(), max(min(value, 255), 0))

class PosDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'X' : PropertyEditors.IntPropEdit,
                        'Y' : PropertyEditors.IntPropEdit}

    def properties(self):
        return {'X': ('CompnRoute', self.GetX, self.SetX),
                'Y': ('CompnRoute', self.GetY, self.SetY)}

    def GetX(self, comp):
        return self.obj.x
    def SetX(self, value):
        self.obj.Set(value, self.obj.y)

    def GetY(self, comp):
        return self.obj.y
    def SetY(self, value):
        self.obj.Set(self.obj.x, value)

class SizeDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'Width' : PropertyEditors.IntPropEdit,
                        'Height' : PropertyEditors.IntPropEdit}

    def properties(self):
        return {'Width': ('CompnRoute', self.GetWidth, self.SetWidth),
                'Height': ('CompnRoute', self.GetHeight, self.SetHeight)}

    def GetWidth(self, comp):
        return self.obj.width
    def SetWidth(self, value):
        self.obj.width = value

    def GetHeight(self, comp):
        return self.obj.height
    def SetHeight(self, value):
        self.obj.height = value
        
        
class AnchorsDTC(HelperDTC):
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'Left'   : PropertyEditors.BoolPropEdit,
                        'Top'    : PropertyEditors.BoolPropEdit,
                        'Right'  : PropertyEditors.BoolPropEdit,
                        'Bottom' : PropertyEditors.BoolPropEdit}
        self.anchCtrl = cmpn.control
        self.assureAnchors()
        self.GetLeftAnchor('')
        self.GetTopAnchor('')
        self.GetRightAnchor('')
        self.GetBottomAnchor('')

    def properties(self):
        return {'Left'    : ('CompnRoute', self.GetLeftAnchor, self.SetLeftAnchor),
                'Top'     : ('CompnRoute', self.GetTopAnchor, self.SetTopAnchor),
                'Right'   : ('CompnRoute', self.GetRightAnchor, self.SetRightAnchor),
                'Bottom'  : ('CompnRoute', self.GetBottomAnchor, self.SetBottomAnchor),}

    def assureAnchors(self):
        if not self.ownerCompn.anchorSettings:
            self.ownerCompn.defaultAnchors()

    def updateAnchors(self):
        self.ownerCompn.anchorSettings = [self.left, self.top, self.right, self.bottom]
        self.obj = LayoutAnchors(self.anchCtrl, self.left, self.top, self.right, self.bottom)

    def GetLeftAnchor(self, name):
        self.assureAnchors()
        self.left = self.ownerCompn.anchorSettings[0]
        return self.left
    def SetLeftAnchor(self, value):
        self.assureAnchors()
        self.left = value
        self.updateAnchors()

    def GetTopAnchor(self, name):
        self.assureAnchors()
        self.top = self.ownerCompn.anchorSettings[1]
        return self.top
    def SetTopAnchor(self, value):
        self.assureAnchors()
        self.top = value
        self.updateAnchors()

    def GetRightAnchor(self, name):
        self.assureAnchors()
        self.right = self.ownerCompn.anchorSettings[2]
        return self.right
    def SetRightAnchor(self, value):
        self.assureAnchors()
        self.right = value
        self.updateAnchors()

    def GetBottomAnchor(self, name):
        self.assureAnchors()
        self.bottom = self.ownerCompn.anchorSettings[3]
        return self.bottom
    def SetBottomAnchor(self, value):
        self.assureAnchors()
        self.bottom = value
        self.updateAnchors()


class BaseConstrFlagsDTC(HelperDTC):
    paramName = 'param'
    propName = 'Prop'
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {}
        for flag in self.ownerCompn.windowStyles:
            self.editors[flag] = PropertyEditors.BoolPropEdit

    def properties(self):
        props = {}
        prop = ('NameRoute', self.GetStyle, self.SetStyle)
        for flag in self.ownerCompn.windowStyles:
            props[flag] = prop
        return props

    def GetStyle(self, name):
        return name in self.ownerCompn.textConstr.params[self.paramName].split(' | ')

    def SetStyle(self, name, value):
        flags = self.ownerCompn.textConstr.params[self.paramName].split(' | ')
        if value:
            if name not in flags:
                if '0' in flags:
                    flags.remove('0')
                flags.insert(0, name)
        else:
            if name in flags:
                flags.remove(name)
                if not flags:
                    flags.append('0')
        flagsSrc = ' | '.join(flags)
        self.ownerCompn.textConstr.params[self.paramName] = flagsSrc
        self.designer.inspector.constructorUpdate(self.propName)
        flagsVal = self.eval(flagsSrc)
        ctrl = self.ownerCompn.control
        if hasattr(ctrl, 'SetWindowStyleFlag'):
            if ctrl.ClassName == 'wxListCtrl':
                try:
                    ctrl.SetWindowStyleFlag(flagsVal)
                except:
                    # This does not work. The first parameter has to be the graphics container that the dialogue will be
                    # displayed in (like a panel or frame) but "self" here is a list control and I do not know how to
                    # get a reference to next level up graphic component.
                    #
                    # dlg = wx.MessageDialog(self,
                    #                        'wxPython detected a problem with your style flags.\n' +
                    #                        'Your flags are set to;\n\n' +
                    #                        flagsSrc + '\n\n' +
                    #                        'There can only be exactly one mode setting style. These are\n' +
                    #                        'wx.LC_LIST, wx.LC_REPORT, wx.LC_VIRTUAL, wx.LC_ICON and wx.LC_SMALL_ICON.\n\n' +
                    #                        'Another restriction is that you cannot set contradictory flags such as;\n\n' +
                    #                        'wx.NO_BORDER | wx.RAISED_BORDER\n\n' +
                    #                        'Please review your flags and try again.',
                    #                        'Incorrect style flags', wx.OK | wx.ICON_INFORMATION)
                    # try:
                    #     result = dlg.ShowModal()
                    # finally:
                    #     dlg.Destroy()
                    print('wxPython detected a problem with your style flags.\n' +
                                           'Your flags are set to;\n\n' +
                                           flagsSrc + '\n\n' +
                                           'There can only be EXACTLY ONE mode setting style. These are;\n\n' +
                                           'wx.LC_LIST, wx.LC_REPORT, wx.LC_VIRTUAL, wx.LC_ICON and wx.LC_SMALL_ICON.\n\n' +
                                           'Another restriction is that you cannot set contradictory flags such as;\n\n' +
                                           'wx.NO_BORDER | wx.RAISED_BORDER\n\n' +
                                           'Please review your flags and try again.\n\n' +
                                            'P.S.  It is possible you may get this error message and\n\n' +
                                            ' you DO HAVE EXACTLY ONE STYLE. This appears to be a problem with\n\n' +
                                            ' wxPython and at this stage, I cannot fix it. In that case, just \n\n' +
                                            ' ignore this message and continue.'
                          )
            else:
                ctrl.SetWindowStyleFlag(flagsVal)

class WindowStyleDTC(BaseConstrFlagsDTC):
    paramName = 'style'
    propName = 'Style'

class FlagsDTC(BaseConstrFlagsDTC):
    paramName = 'flags'
    propName = 'Flags'


PaletteStore.helperClasses.update({
    'wx.Font': FontDTC,
    'wx.Colour': ColourDTC,
    'Anchors': AnchorsDTC
})
