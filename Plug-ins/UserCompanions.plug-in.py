#-----------------------------------------------------------------------------
# Name:        UserCompanions.py
# Purpose:     Add your own companion classes to this module
#              If you wish to define companion in separate modules, import
#              their contents into this module. Use from module import *
#
# Created:     2001/02/04
# RCS-ID:      $Id$
#-----------------------------------------------------------------------------

import wx

from Companions import BasicCompanions
from PropEdit import PropertyEditors

try:
    import bcrtl
except ImportError:
    raise ImportError('The "bcrtl" package is not installed, turn on "installBCRTL" under Preferences')

#-------------------------------------------------------------------------------

# Objects which Boa will need at design-time needs to be imported into the
# Companion module's namespace
import bcrtl.user.ExampleST

# Silly barebones example of a companion for a new component that is not
# available in the wxPython distribution
class ExampleSTDTC(BasicCompanions.StaticTextDTC):
    def writeImports(self):
        return 'import bcrtl.user.ExampleST'

#-------------------------------------------------------------------------------
# Example of a composite control, control itself, implemented in
# wxPython.lib.bcrtl.user.StaticTextCtrl

import bcrtl.user.StaticTextCtrl

class StaticTextCtrlDTC(BasicCompanions.TextCtrlDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        BasicCompanions.TextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['CaptionAlignment'] = PropertyEditors.EnumPropEdit
        self.options['CaptionAlignment'] = [wx.TOP, wx.LEFT]
        self.names['CaptionAlignment'] = {'wx.TOP': wx.TOP, 'wx.LEFT': wx.LEFT}

    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name',
                'Caption': 'caption'}

    def writeImports(self):
        return 'import bcrtl.user.StaticTextCtrl'

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        dts = BasicCompanions.TextCtrlDTC.designTimeSource(self, position, size)
        dts['caption'] = repr(self.name)
        return dts


#-------------------------------------------------------------------------------

import Plugins

# Register the components
Plugins.registerComponents('User',
    (bcrtl.user.ExampleST.ExampleStaticText,
       'ExampleStaticText', ExampleSTDTC),
    (bcrtl.user.StaticTextCtrl.StaticTextCtrl,
       'StaticTextCtrl', StaticTextCtrlDTC),
    )
