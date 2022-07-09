#-----------------------------------------------------------------------------
# Name:        ListCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.ListCompanions'

import wx
import wx.grid

from Utils import _

from BaseCompanions import WindowDTC, ChoicedDTC, CollectionDTC, CollectionIddDTC

import Constructors
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

import methodparse

class ListCtrlDTC(Constructors.MultiItemCtrlsConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Columns':         ListColumnsColPropEdit,
                             'ImageListSmall':  ListCtrlImageListClassLinkPropEdit,
                             'ImageListNormal': ListCtrlImageListClassLinkPropEdit})
        self.windowStyles = ['wx.LC_LIST', 'wx.LC_REPORT', 'wx.LC_VIRTUAL', 'wx.LC_ICON',
                             'wx.LC_SMALL_ICON', 'wx.LC_ALIGN_TOP',
                             'wx.LC_ALIGN_LEFT', 'wx.LC_AUTOARRANGE',
                             'wx.LC_USER_TEXT', 'wx.LC_EDIT_LABELS',
                             'wx.LC_NO_HEADER', 'wx.LC_SINGLE_SEL',
                             'wx.LC_SORT_ASCENDING', 'wx.LC_SORT_DESCENDING',
                             'wx.LC_HRULES', 'wx.LC_VRULES'] + self.windowStyles
        self.subCompanions['Columns'] = ListCtrlColumnsCDTC
        self.listTypeNameMap = {'ImageListSmall'  : wx.IMAGE_LIST_SMALL,
                                'ImageListNormal' : wx.IMAGE_LIST_NORMAL}
        for name in self.listTypeNameMap.keys():
            self.customPropEvaluators[name] = self.EvalImageList
        self.customPropEvaluators['ImageList'] = self.EvalImageList

    def properties(self):
        props = WindowDTC.properties(self)
        props['Columns'] =  ('NoneRoute', None, None)

        prop = ('NameRoute', self.GetImageList, self.SetImageList)
        for name in self.listTypeNameMap.keys():
            props[name] = prop

        return props

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.LC_ICON',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ListEvent']

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + ['ItemCount']


#---Image list management-------------------------------------------------------
    def GetImageList(self, name):
        return (self.control.GetImageList(self.listTypeNameMap[name]),
            self.listTypeNameMap[name])

    def SetImageList(self, name, value):
        self.control.SetImageList(value[0], self.listTypeNameMap[name])

    def EvalImageList(self, exprs, objects):
        imgLst, lstTpe = exprs
        return objects[imgLst], self.eval(lstTpe)

    def notification(self, compn, action):
        WindowDTC.notification(self, compn, action)
        if action == 'delete':
            for propName, typeName in (('ImageListSmall', 'wx.IMAGE_LIST_SMALL'),
                                       ('ImageListNormal', 'wx.IMAGE_LIST_NORMAL')):
                imgLst, imgLstType = self.GetImageList(propName)
                if imgLst and `imgLst` == `compn.control`:
                    self.SetImageList(propName, (None,))
                    idx = 0
                    while idx < len(self.textPropList):
                        prop = self.textPropList[idx]
                        if prop.prop_setter == 'SetImageList' and \
                              prop.params[1] == typeName:
                            del self.textPropList[idx]
                        else:
                            idx = idx + 1

    def persistProp(self, name, setterName, value):
        if setterName == 'SetImageList':
            imgList, listType = value.split(',')
            imgList, listType = imgList.strip(), listType.strip()
            for prop in self.textPropList:
                if prop.prop_setter == setterName and prop.params[1] == listType:
                    prop.params = [imgList, listType]
                    return
            self.textPropList.append(methodparse.PropertyParse( None, self.name,
                setterName, [imgList, listType], 'SetImageList'))
        else:
            WindowDTC.persistProp(self, name, setterName, value)


class ListCtrlColumnsCDTC(CollectionDTC):
    propName = 'Columns'
    displayProp = 'heading'
    indexProp = 'col'
    insertionMethod = 'InsertColumn'
    deletionMethod = 'DeleteColumn'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Width': IntConstrPropEdit,
                        'Heading': StrConstrPropEdit,
                        'Format': EnumConstrPropEdit}#StyleConstrPropEdit}
#        self.options = {'Format': formatStyle}
        self.names = {'Format': formatStyle}

    def constructor(self):
        return {'Column': 'col', 'Heading': 'heading', 'Format': 'format',
                'Width': 'width'}

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Column':  ('NoneRoute', None, None),
                      'Heading': ('NoneRoute', None, None),
#                      'Format':  ('IndexRoute', None, None),
                      'Width':   ('IndexRoute', wx.ListCtrl.GetColumnWidth,
                                                wx.ListCtrl.SetColumnWidth)})
        return props

    def designTimeSource(self, wId, method=None):
        return {'col': `wId`,
                'heading': `'%s%d'%(self.propName, wId)`,
                'format': 'wx.LIST_FORMAT_LEFT',
                'width': `-1`}

    def appendItem(self, method=None):
        if not (self.control.GetWindowStyleFlag() & wx.LC_REPORT):
            wx.MessageBox(_('wx.ListCtrl must be created with the wx.LC_REPORT flag.'),
                  'Error', wx.ICON_ERROR | wx.OK, self.designer)
            return
        CollectionDTC.appendItem(self, method)

    def moveItem(self, idx, dir):
        newIdx = CollectionDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            li = self.control.GetColumn(idx)
            text = li.GetText()
            self.control.DeleteColumn(idx)
            self.control.InsertColumnInfo(newIdx, li)
            self.control.SetColumn(newIdx, li) # doesn't update without this
        return newIdx

    def deleteItem(self, idx):
        CollectionDTC.deleteItem(self, idx)
        del self.textConstrLst[idx]

class ListViewDTC(ListCtrlDTC): pass

class TreeCtrlDTC(Constructors.MultiItemCtrlsConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'ImageList': ImageListClassLinkPropEdit,
                             #'StateImageList': ImageListClassLinkPropEdit
                             })
        self.windowStyles = ['wx.TR_NO_BUTTONS', 'wx.TR_HAS_BUTTONS',
                             'wx.TR_EDIT_LABELS', 'wx.TR_NO_LINES',
                             'wx.TR_LINES_AT_ROOT',
                             #'wxTR_HIDE_ROOT',
                             'wx.TR_ROW_LINES',
                             #'wxTR_HAS_VARIABLE_ROW_HEIGHT',
                             'wx.TR_SINGLE', 'wx.TR_MULTIPLE', 'wx.TR_EXTENDED',
                             'wx.TR_DEFAULT_STYLE'] + self.windowStyles

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wx.TR_HAS_BUTTONS',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + ['StateImageList']

    def dependentProps(self):
        return WindowDTC.dependentProps(self) + ['ImageList', 'StateImageList']

    def notification(self, compn, action):
        WindowDTC.notification(self, compn, action)
        if action == 'delete':
            if `self.control.GetImageList()` == `compn.control`:
                self.propRevertToDefault('ImageList', 'SetImageList')
                self.control.SetImageList(None)

##            if `self.control.GetStateImageList()` == `compn.control`:
##                self.propRevertToDefault('StateImageList', 'SetStateImageList')
##                self.control.SetStateImageList(None)

    def events(self):
        return WindowDTC.events(self) + ['TreeEvent']

EventCategories['ListBoxEvent'] = ('wx.EVT_LISTBOX', 'wx.EVT_LISTBOX_DCLICK')
commandCategories.append('ListBoxEvent')
class ListBoxDTC(Constructors.ListConstr, ChoicedDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Choices'] = ChoicesConstrPropEdit
        self.windowStyles = ['wx.LB_SINGLE', 'wx.LB_MULTIPLE', 'wx.LB_EXTENDED',
                             'wx.LB_HSCROLL', 'wx.LB_ALWAYS_SB', 'wx.LB_NEEDED_SB',
                             'wx.LB_SORT'] + self.windowStyles

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': size,
                'choices': '[]',
                'style': '0',
                'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['ListBoxEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ListBoxEvent', 'wx.EVT_LISTBOX')


EventCategories['CheckListBoxEvent'] = ('wx.EVT_CHECKLISTBOX',)
commandCategories.append('CheckListBoxEvent')
class CheckListBoxDTC(ListBoxDTC):
    def events(self):
        return ListBoxDTC.events(self) + ['CheckListBoxEvent']

EventCategories['RadioBoxEvent'] = ('wx.EVT_RADIOBOX',)
commandCategories.append('RadioBoxEvent')
class RadioBoxDTC(ChoicedDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['MajorDimension'] = MajorDimensionConstrPropEdit
        self.windowStyles = ['wx.RA_SPECIFY_ROWS', 'wx.RA_SPECIFY_COLS'] + self.windowStyles

    def constructor(self):
        return {'Label': 'label', 'Position': 'pos', 'Size': 'size',
                'Choices': 'choices', 'MajorDimension': 'majorDimension',
                'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'choices': `['asd']`,
                'majorDimension': '1',
                'style': 'wx.RA_SPECIFY_COLS',
                'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['RadioBoxEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('RadioBoxEvent', 'wx.EVT_RADIOBOX')

class GenericDirCtrlDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['DefaultFilter'] = IntConstrPropEdit
        self.windowStyles = ['wx.DIRCTRL_DIR_ONLY', 'wx.DIRCTRL_SELECT_FIRST',
              'wx.DIRCTRL_SHOW_FILTERS', 'wx.DIRCTRL_3D_INTERNAL',
              'wx.DIRCTRL_EDIT_LABELS'] + self.windowStyles
        self.compositeCtrl = True

    def constructor(self):
        return {'Name': 'name', 'Position': 'pos', 'Size': 'size',
                'DefaultPath': 'dir', 'Style': 'style', 'Filter': 'filter',
                'DefaultFilter': 'defaultFilter'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'dir': "'.'",
                'style': 'wx.DIRCTRL_3D_INTERNAL | wx.SUNKEN_BORDER',
                'filter': "''",
                'defaultFilter': '0',
                'name': `self.name`}


EventCategories['GridEvent'] = ('wx.grid.EVT_GRID_CELL_LEFT_CLICK',
      'wx.grid.EVT_GRID_CELL_RIGHT_CLICK', 'wx.grid.EVT_GRID_CELL_LEFT_DCLICK',
      'wx.grid.EVT_GRID_CELL_RIGHT_DCLICK', 'wx.grid.EVT_GRID_LABEL_LEFT_CLICK',
      'wx.grid.EVT_GRID_LABEL_RIGHT_CLICK',
      'wx.grid.EVT_GRID_LABEL_LEFT_DCLICK',
      'wx.grid.EVT_GRID_LABEL_RIGHT_DCLICK',
      'wx.grid.EVT_GRID_ROW_SIZE', 'wx.grid.EVT_GRID_COL_SIZE',
      'wx.grid.EVT_GRID_RANGE_SELECT', 'wx.grid.EVT_GRID_CELL_CHANGE',
      'wx.grid.EVT_GRID_SELECT_CELL', 'wx.grid.EVT_GRID_EDITOR_SHOWN',
      'wx.grid.EVT_GRID_EDITOR_HIDDEN', 'wx.grid.EVT_GRID_EDITOR_CREATED',
)

class GridDTC(Constructors.WindowConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Editable'] = self.editors['GridLinesEnabled'] = BoolPropEdit
        self.editors['SelectionMode'] = EnumPropEdit
        self.compositeCtrl = True

        self.options['SelectionMode'] = [wx.grid.Grid.wxGridSelectCells,
                                         wx.grid.Grid.wxGridSelectRows,
                                         wx.grid.Grid.wxGridSelectColumns]
        self.names['SelectionMode'] = \
              {'wx.grid.Grid.wxGridSelectCells': wx.grid.Grid.wxGridSelectCells,
               'wx.grid.Grid.wxGridSelectRows': wx.grid.Grid.wxGridSelectRows,
               'wx.grid.Grid.wxGridSelectColumns': wx.grid.Grid.wxGridSelectColumns}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': '0',
                'name': `self.name`}

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'Editable': ('CtrlRoute',
                      wx.grid.Grid.IsEditable, wx.grid.Grid.EnableEditing),
                      'GridLinesEnabled': ('CtrlRoute',
                      wx.grid.Grid.GridLinesEnabled, wx.grid.Grid.EnableGridLines)})
        return props

    def designTimeControl(self, position, size, args = None):
        dtc = WindowDTC.designTimeControl(self, position, size, args)
        dtc.CreateGrid(0, 0)
        return dtc

    def events(self):
        return WindowDTC.events(self) + ['GridEvent']

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'import wx.grid') )

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + \
              ['RowLabelAlignment', 'ColLabelAlignment', 'Table',
               'DefaultEditor', 'DefaultRenderer', 'TargetWindow', 'TargetRect',
               'DefaultCellAlignment']

#-------------------------------------------------------------------------------

import Plugins

Plugins.registerPalettePage('ListControls', _('List Controls'))

Plugins.registerComponents('ListControls',
      (wx.ListBox, 'wx.ListBox', ListBoxDTC),
      (wx.CheckListBox, 'wx.CheckListBox', CheckListBoxDTC),
      (wx.grid.Grid, 'wx.grid.Grid', GridDTC),
      (wx.ListCtrl, 'wx.ListCtrl', ListCtrlDTC),
      (wx.ListView, 'wx.ListView', ListViewDTC),
      (wx.TreeCtrl, 'wx.TreeCtrl', TreeCtrlDTC),
      (wx.RadioBox, 'wx.RadioBox', RadioBoxDTC),
      (wx.GenericDirCtrl, 'wx.GenericDirCtrl', GenericDirCtrlDTC),
    )
