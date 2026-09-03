#-----------------------------------------------------------------------------
# Name:        PhoenixCompanions.py
# Purpose:     Register newer wxPython Phoenix controls on the palette
#
# Author:      Boa contributors
# Licence:     GPL
#-----------------------------------------------------------------------------

import wx

from Utils import _

from . import Constructors
from .BaseCompanions import WindowDTC, UtilityDTC


class PhoenixWindowDTC(WindowDTC):
    """Generic companion for Phoenix controls with standard window constructor."""


class PhoenixLabeledDTC(Constructors.LabeledInputConstr, WindowDTC):
    """Generic companion for controls that expect a label-like argument."""

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {
            'label': repr(self.name),
            'pos': position,
            'size': size,
            'style': '0',
            'name': repr(self.name),
        }


class CommandLinkButtonDTC(WindowDTC):
    def constructor(self):
        return {
            'Position': 'pos',
            'Size': 'size',
            'MainLabel': 'mainLabel',
            'Note': 'note',
            'Style': 'style',
            'Name': 'name',
        }

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {
            'pos': position,
            'size': size,
            'mainLabel': repr(self.name),
            'note': repr(''),
            'style': '0',
            'name': repr(self.name),
        }


class RearrangeListDTC(WindowDTC):
    def constructor(self):
        return {
            'Position': 'pos',
            'Size': 'size',
            'Order': 'order',
            'Items': 'items',
            'Style': 'style',
            'Name': 'name',
        }

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {
            'pos': position,
            'size': size,
            'order': '[]',
            'items': '[]',
            'style': '0',
            'name': repr(self.name),
        }


class RearrangeCtrlDTC(WindowDTC):
    def constructor(self):
        return {
            'Position': 'pos',
            'Size': 'size',
            'Order': 'order',
            'Items': 'items',
            'Style': 'style',
            'Name': 'name',
        }

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {
            'pos': position,
            'size': size,
            'order': '[]',
            'items': '[]',
            'style': '0',
            'name': repr(self.name),
        }


class AuiManagerDTC(Constructors.EmptyConstr, UtilityDTC):
    """Non-visual AUI manager utility object."""

    def designTimeSource(self):
        return {}


class NotificationMessageDTC(Constructors.EmptyConstr, UtilityDTC):
    """Non-visual notification utility object."""

    def designTimeSource(self):
        return {}


import Plugins

Plugins.registerPalettePage('Phoenix', _('Phoenix'))
# Phoenix registers a few non-visual helpers onto the Utilities page.
# Ensure the page exists regardless of import ordering.
Plugins.registerPalettePage('Utilities (Data)', _('Utilities (Data)'))

# Controls that are present in Phoenix but optional across builds.
try:
    import wx.dataview

    Plugins.registerComponents('Phoenix',
          (wx.dataview.DataViewCtrl, 'wx.dataview.DataViewCtrl', PhoenixWindowDTC),
          (wx.dataview.DataViewListCtrl, 'wx.dataview.DataViewListCtrl', PhoenixWindowDTC),
          (wx.dataview.TreeListCtrl, 'wx.dataview.TreeListCtrl', PhoenixWindowDTC),
        )
except ImportError:
    pass

try:
    import wx.adv

    Plugins.registerComponents('Phoenix',
          (wx.adv.CommandLinkButton, 'wx.adv.CommandLinkButton', CommandLinkButtonDTC),
          (wx.adv.HyperlinkCtrl, 'wx.adv.HyperlinkCtrl', PhoenixLabeledDTC),
          (wx.adv.BitmapComboBox, 'wx.adv.BitmapComboBox', PhoenixWindowDTC),
          (wx.adv.TimePickerCtrl, 'wx.adv.TimePickerCtrl', PhoenixWindowDTC),
          (wx.adv.BannerWindow, 'wx.adv.BannerWindow', PhoenixWindowDTC),
        )
except (ImportError, AttributeError):
    pass

try:
    import wx.ribbon

    Plugins.registerComponents('Phoenix',
          (wx.ribbon.RibbonBar, 'wx.ribbon.RibbonBar', PhoenixWindowDTC),
          (wx.ribbon.RibbonPage, 'wx.ribbon.RibbonPage', PhoenixLabeledDTC),
          (wx.ribbon.RibbonPanel, 'wx.ribbon.RibbonPanel', PhoenixLabeledDTC),
          (wx.ribbon.RibbonButtonBar, 'wx.ribbon.RibbonButtonBar', PhoenixWindowDTC),
        )
except (ImportError, AttributeError):
    pass

try:
    import wx.aui

    Plugins.registerComponents('Phoenix',
          (wx.aui.AuiNotebook, 'wx.aui.AuiNotebook', PhoenixWindowDTC),
          (wx.aui.AuiToolBar, 'wx.aui.AuiToolBar', PhoenixWindowDTC),
        )
    Plugins.registerComponent('Utilities (Data)', wx.aui.AuiManager, 'wx.aui.AuiManager', AuiManagerDTC)
except (ImportError, AttributeError):
    pass

try:
    import wx.propgrid

    Plugins.registerComponents('Phoenix',
          (wx.propgrid.PropertyGrid, 'wx.propgrid.PropertyGrid', PhoenixWindowDTC),
          (wx.propgrid.PropertyGridManager, 'wx.propgrid.PropertyGridManager', PhoenixWindowDTC),
        )
except (ImportError, AttributeError):
    pass

try:
    Plugins.registerComponents('Phoenix',
          (wx.ActivityIndicator, 'wx.ActivityIndicator', PhoenixWindowDTC),
          (wx.RearrangeList, 'wx.RearrangeList', RearrangeListDTC),
          (wx.RearrangeCtrl, 'wx.RearrangeCtrl', RearrangeCtrlDTC),
          (wx.InfoBar, 'wx.InfoBar', PhoenixWindowDTC),
        )
except AttributeError:
    pass

try:
    import wx.html2

    # WebView is intentionally not registered: it is factory-based (WebView.New)
    # and cannot be created by the standard constructor path used by companions.
except ImportError:
    pass

try:
    import wx.adv

    Plugins.registerComponent('Utilities (Data)',
          wx.adv.NotificationMessage,
          'wx.adv.NotificationMessage', NotificationMessageDTC)
except (ImportError, AttributeError):
    pass
