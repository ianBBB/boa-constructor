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


class PhoenixNoNameDTC(WindowDTC):
    """Companion for Phoenix windows whose constructor omits ``name``."""

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style'}

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {
            'pos': position,
            'size': size,
            'style': '0',
        }


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


class RibbonPageDTC(PhoenixLabeledDTC):
    def constructor(self):
        return {'Label': 'label', 'Icon': 'icon', 'Style': 'style'}

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {
            'label': repr(self.name),
            'icon': 'wx.NullBitmap',
            'style': '0',
        }


class RibbonPanelDTC(PhoenixLabeledDTC):
    def constructor(self):
        return {
            'Label': 'label',
            'MinimisedIcon': 'minimised_icon',
            'Position': 'pos',
            'Size': 'size',
            'Style': 'style',
        }

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {
            'label': repr(self.name),
            'minimised_icon': 'wx.NullBitmap',
            'pos': position,
            'size': size,
            'style': 'wx.ribbon.RIBBON_PANEL_DEFAULT_STYLE',
        }


class AuiToolBarDTC(PhoenixNoNameDTC):
    def constructor(self):
        return {
            'Position': 'position',
            'Size': 'size',
            'Style': 'style',
        }

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {
            'position': position,
            'size': size,
            'style': 'wx.aui.AUI_TB_DEFAULT_STYLE',
        }


class WinIdWindowDTC(PhoenixWindowDTC):
    windowIdName = 'winid'


class InfoBarDTC(WindowDTC):
    windowIdName = 'winid'

    def constructor(self):
        return {}

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {}


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


class PropertyGridManagerDTC(PhoenixWindowDTC):
    """Keep PropertyGridManager valid by giving it an initial page.

    wxWidgets 3.2.9 on MSW crashes in the propgrid DLL when a page-less
    manager is destroyed.  Persist the page as normal generated source, but
    only create it directly for a brand-new design-time control.  Reloaded
    controls receive it when Boa replays their persisted properties.
    """

    defaultPageLabel = _('Properties')

    def designTimeControl(self, position, size, args=None):
        control = PhoenixWindowDTC.designTimeControl(
            self, position, size, args)
        if args is None and control.GetPageCount() == 0:
            control.AddPage(self.defaultPageLabel)
        return control

    def persistConstr(self, className, params):
        PhoenixWindowDTC.persistConstr(self, className, params)
        self.persistProp('DefaultPage', 'AddPage',
                         repr(self.defaultPageLabel))


import Plugins

Plugins.registerPalettePage('Phoenix', _('Phoenix'))
# Phoenix registers a few non-visual helpers onto the Utilities page.
# Ensure the page exists regardless of import ordering.
Plugins.registerPalettePage('Utilities (Data)', _('Utilities (Data)'))

# Controls that are present in Phoenix but optional across builds.
try:
    import wx.dataview

    Plugins.registerComponents('Utilities (Data)',
          (wx.dataview.DataViewCtrl, 'wx.dataview.DataViewCtrl', PhoenixWindowDTC),
          (wx.dataview.DataViewListCtrl, 'wx.dataview.DataViewListCtrl', PhoenixNoNameDTC),
          (wx.dataview.TreeListCtrl, 'wx.dataview.TreeListCtrl', PhoenixWindowDTC),
        )
except ImportError:
    pass

try:
    import wx.adv

    Plugins.registerComponent('Buttons',
          wx.adv.CommandLinkButton,
          'wx.adv.CommandLinkButton', CommandLinkButtonDTC)
    Plugins.registerComponents('Phoenix',
          (wx.adv.HyperlinkCtrl, 'wx.adv.HyperlinkCtrl', PhoenixLabeledDTC),
          (wx.adv.TimePickerCtrl, 'wx.adv.TimePickerCtrl', PhoenixWindowDTC),
        )
    Plugins.registerComponent('ListControls',
          wx.adv.BitmapComboBox, 'wx.adv.BitmapComboBox', PhoenixWindowDTC)
    Plugins.registerComponent('ContainersLayout',
          wx.adv.BannerWindow, 'wx.adv.BannerWindow', WinIdWindowDTC)
except (ImportError, AttributeError):
    pass

try:
    import wx.ribbon

    Plugins.registerComponents('ContainersLayout',
          (wx.ribbon.RibbonBar, 'wx.ribbon.RibbonBar', PhoenixNoNameDTC),
          (wx.ribbon.RibbonPage, 'wx.ribbon.RibbonPage', RibbonPageDTC),
          (wx.ribbon.RibbonPanel, 'wx.ribbon.RibbonPanel', RibbonPanelDTC),
          (wx.ribbon.RibbonButtonBar, 'wx.ribbon.RibbonButtonBar', PhoenixNoNameDTC),
        )
except (ImportError, AttributeError):
    pass

try:
    import wx.aui

    Plugins.registerComponent('ContainersLayout',
          wx.aui.AuiNotebook, 'wx.aui.AuiNotebook', PhoenixNoNameDTC)
    Plugins.registerComponent('ContainersLayout',
          wx.aui.AuiToolBar, 'wx.aui.AuiToolBar', AuiToolBarDTC)
    Plugins.registerComponent('Utilities (Data)', wx.aui.AuiManager, 'wx.aui.AuiManager', AuiManagerDTC)
except (ImportError, AttributeError):
    pass

try:
    import wx.propgrid

    Plugins.registerComponents('Phoenix',
          (wx.propgrid.PropertyGrid, 'wx.propgrid.PropertyGrid', PhoenixWindowDTC),
          (wx.propgrid.PropertyGridManager, 'wx.propgrid.PropertyGridManager', PropertyGridManagerDTC),
        )
except (ImportError, AttributeError):
    pass

try:
    Plugins.registerComponents('Phoenix',
          (wx.ActivityIndicator, 'wx.ActivityIndicator', WinIdWindowDTC),
        )
    Plugins.registerComponents('ListControls',
          (wx.RearrangeList, 'wx.RearrangeList', RearrangeListDTC),
          (wx.RearrangeCtrl, 'wx.RearrangeCtrl', RearrangeCtrlDTC),
        )
    Plugins.registerComponent('ContainersLayout',
          wx.InfoBar, 'wx.InfoBar', InfoBarDTC)
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
