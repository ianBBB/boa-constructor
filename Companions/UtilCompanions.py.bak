#-----------------------------------------------------------------------------
# Name:        UtilCompanions.py
# Purpose:     Companion classes for non visible objects
#
# Author:      Riaan Booysen
#
# Created:     2000
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.UtilCompanions'
import os, copy

import wx

import Preferences, Utils
from Utils import _

from BaseCompanions import UtilityDTC, CollectionDTC, CollectionIddDTC, NYIDTC

import Constructors
from PropEdit.PropertyEditors import IntConstrPropEdit, StrConstrPropEdit, \
      CollectionPropEdit, BitmapConstrPropEdit, EnumConstrPropEdit, \
      LCCEdgeConstrPropEdit, WinEnumConstrPropEdit, BoolConstrPropEdit, \
      MenuEnumConstrPropEdit, BoolPropEdit, ColourConstrPropEdit, \
      ConstrPropEdit

from PropEdit import Enumerations, InspectorEditorControls
import EventCollections, RTTI

import methodparse, moduleparse, sourceconst

class ImageListDTC(UtilityDTC):
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Width': IntConstrPropEdit,
                             'Height': IntConstrPropEdit,
                             'Images': CollectionPropEdit,})
        self.subCompanions['Images'] = ImageListImagesCDTC

    def constructor(self):
        return {'Name': 'name', 'Width': 'width', 'Height': 'height'}

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Images': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self):
        return {'width': '16',
                'height': '16'}

    def defaultAction(self):
        nv = self.designer.inspector.props.getNameValue('Images')
        if nv:
            nv.propEditor.edit(None)

class ImageListImagesCDTC(CollectionDTC):
    propName = 'Images'
    displayProp = 'bitmap'
    indexProp = '(None)'
    insertionMethod = 'Add'
    deletionMethod = 'Remove'

    additionalMethods = { 'AddWithColourMask': ('Add with colour mask', 'bitmap', '(None)'),
#                          'AddIcon'     : ('Add icon', 'icon', '(None)')
                        }

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Bitmap': BitmapConstrPropEdit,
                        'Mask': BitmapConstrPropEdit,
#                        'Icon': BitmapConstrPropEdit,
                        'MaskColour': ColourConstrPropEdit}
        from Views.CollectionEdit import ImageListCollectionEditor
        self.CollEditorFrame = ImageListCollectionEditor

    def constructor(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method == 'Add':
            return {'Bitmap': 'bitmap', 'Mask': 'mask'}
        elif tcl.method == 'AddWithColourMask':
            return {'Bitmap': 'bitmap', 'MaskColour': 'maskColour'}
#        elif tcl.method == 'AddIcon':
#            return {'Icon': 'icon'}

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Bitmap':    ('CompnRoute', None, self.setBitmap),
                      'Mask':      ('NoneRoute', None, None),
#                      'Icon':      ('CompnRoute', None, self.setBitmap),
                    })
        return props

    def designTimeSource(self, wId, method=None):
        if method is None:
            method = self.insertionMethod

        if method == 'Add':
            return {'bitmap': 'wx.NullBitmap',
                    'mask':   'wx.NullBitmap'}
        elif method == 'AddWithColourMask':
            return {'bitmap': 'wx.NullBitmap',
                    'maskColour': 'wx.Colour(255, 0, 255)'}
#        elif method == 'AddIcon':
#            return {'icon': 'wx.NullIcon'}

    def moveItem(self, idx, dir):
        newIdx = CollectionDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            self.control.RemoveAll()
            for crt in self.textConstrLst:
                self.applyDesignTimeDefaults(crt.params, crt.method)
        return newIdx

    def getDisplayProp(self):
        value = '-'
        tcl = self.textConstrLst[self.index]
        if self.displayProp in tcl.params:
            value = tcl.params[self.displayProp]
            if value != 'wx.NullBitmap':
                if value.startswith('wx.Bitmap'):
                    value = os.path.basename(value[10:-21])
                else:
                    m = moduleparse.is_resource_bitmap.search(value)
                    if m:
                        value = '%s.%s'%(m.group('imppath'), m.group('imgname'))
        return value

    def setBitmap(self, value):
        if value != wx.NullBitmap:
            self.control.Replace(self.index, value)
            self.designer.collEditors[(self.name, self.propName)].refreshCtrl(True)

    def defaultAction(self):
        nv = self.designer.inspector.constr.getNameValue('Bitmap')
        if nv:
            nv.propEditor.edit(None)

    def designTimeDefaults(self, vals, method=None):
        dtd = CollectionDTC.designTimeDefaults(self, vals)

        # resize wx.NullBitmap if different size than the imagelist
        ix, iy = self.parentCompanion.control.GetSize(0)
        for param in vals.keys():
            if vals[param] == 'wx.NullBitmap' and (\
                  dtd[param].GetWidth() != ix or\
                  dtd[param].GetHeight() != iy):
                newbmp = wx.EmptyBitmap(ix, iy)
                mdc = wx.MemoryDC()
                mdc.SelectObject(newbmp)
                mdc.DrawBitmap(dtd[param], 0, 0, False)
                mdc.SelectObject(wx.NullBitmap)
                dtd[param] = newbmp

        return dtd

    def applyDesignTimeDefaults(self, params, method=None):
        dtparams = {}; dtparams.update(params)
        if 'mask' in dtparams and dtparams['mask'] == 'wx.NullBitmap':
            del dtparams['mask']
        CollectionDTC.applyDesignTimeDefaults(self, dtparams, method)

# This class handles window id magic which should be done by a base class
# UtilityIddDTC or maybe an IddDTCMix for everyone
EventCollections.EventCategories['TimerEvent'] = ('wx.EVT_TIMER',)
EventCollections.commandCategories.append('TimerEvent')
class TimerDTC(UtilityDTC):
    handledConstrParams = ('id',)
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.id = self.getWinId()
    def constructor(self):
        return {'Owner': 'owner', 'Id': 'id'}
    def designTimeSource(self):
        return {'owner': 'self', 'id': self.id}
    def designTimeObject(self, args=None):
        return UtilityDTC.designTimeObject(self, self.designTimeDefaults())
    def designTimeDefaults(self):
        return {'owner': self.designer, 'id': wx.NewId()}
    def events(self):
        return ['TimerEvent']
    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('TimerEvent', 'wx.EVT_TIMER')
#-------------------------------------------------------------------------------
    def getWinId(self):
        return Utils.windowIdentifier(self.designer.model.main, self.name)
    def SetName(self, oldValue, newValue):
        UtilityDTC.SetName(self, oldValue, newValue)
        self.updateWindowIds()
    def updateWindowIds(self):
        self.id = self.getWinId()
        self.textConstr.params['id'] = self.id
        self.renameEventListIds(self.id)

#class AcceleratorTableDTC(NYIDTC):
class AcceleratorTableDTC(UtilityDTC):
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Entries': CollectionPropEdit})
        self.subCompanions['Entries'] = AcceleratorTableEntriesCDTC

    def constructor(self):
        return {'Entries': 'choices'}

    def designTimeSource(self):
        return {'choices':'[]'}


class AcceleratorEntryPropEdit(ConstrPropEdit):
#    def valueToIECValue(self):
#        return self.companion.eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dlg = wx.TextEntryDialog(self.parent, 'Question', 'Caption', 'Default answer')
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            self.value = dlg.GetValue()
            # Your code
        finally:
            self.inspectorPost(False)
            dlg.Destroy()


class AcceleratorTableEntriesCDTC(CollectionDTC):
    propName = 'Entries'
    displayProp = 0
    indexProp = '(None)'
    insertionMethod = 'append'
    deletionMethod = '(None)'
    #sourceObjName = ''

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)

        self.editors['Entry'] = AcceleratorEntryPropEdit

#        self.editors.update({'Flags':   IntConstrPropEdit,
#                             'KeyCode': IntConstrPropEdit,
#                             'Command': IntConstrPropEdit})

    def constructor(self):
        return {'Entry': 0}
#        return {'Flags': 'flags', 'KeyCode': 'keyCode', 'Command': 'cmd'}

    def persistCollInit(self, method, ctrlName, propName, params = {}):
        collInitParse = methodparse.CollectionInitParse(None, '[]', method,
          [], propName)

        self.parentCompanion.textConstr.params = {'choices': collInitParse.asText()}
        self.designer.addCollToObjectCollection(collInitParse)

#    def SetName(self, oldName, newName):
#        CollectionDTC.SetName(self, oldName, newName)

    def designTimeSource(self, idx, method=None):
        return {0: '(0, 0, -1)'}

    def getDisplayProp(self):
        return `self.textConstrLst[self.index].params.values()`

#    def initialiser(self):
#        return ['%s%s = []'%(sourceconst.bodyIndent, self.__class__.sourceObjName), '']

    def finaliser(self):
        return ['', '%sreturn parent' %sourceconst.bodyIndent]#, self.__class__.sourceObjName)]

    def applyDesignTimeDefaults(self, params, method):
        return

EventCollections.EventCategories['MenuEvent'] = ('wx.EVT_MENU',)
EventCollections.commandCategories.append('MenuEvent')

class MenuDTC(UtilityDTC):
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Title': StrConstrPropEdit,
                             'Items': CollectionPropEdit})
        self.subCompanions['Items'] = MenuItemsCIDTC
        #self.adtSubCompanions = {'Items': (MenuItemsSepCIDTC, MenuItemsMenuCIDTC)}

    def constructor(self):
        return {'Name': 'name', 'Title': 'title'}

    def dependentProps(self):
        return UtilityDTC.dependentProps(self) + ['Items']

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Items':  ('NoneRoute', None, None)})
        return props

    def designTimeSource(self):
        return {'title': `''`}

    def hideDesignTime(self):
        return ['NextHandler', 'PreviousHandler', 'EventHandler', 'Id',
                'Parent', 'InvokingWindow']

    def defaultAction(self):
        nv = self.designer.inspector.props.getNameValue('Items')
        if nv:
            nv.propEditor.edit(None)

class MenuItemsCIDTC(CollectionIddDTC):
    propName = 'Items'
    displayProp = 'text'
    indexProp = '(None)'
    insertionMethod = 'Append'
    insertionDesc = 'Append item'
    deletionMethod = 'Remove'
    idProp = 'id'
    idPropNameFrom = 'text'

    additionalMethods = { 'AppendSeparator': ('Append separator', '', '(None)'),
                          'AppendMenu'     : ('Append sub menu', 'text', '(None)') }

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionIddDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Text': StrConstrPropEdit,
                             'Help': StrConstrPropEdit,
                             'Kind': EnumConstrPropEdit,
                             'Menu': MenuEnumConstrPropEdit,
                            })

        self.names['Kind'] = ['wx.ITEM_NORMAL', 'wx.ITEM_CHECK', 'wx.ITEM_RADIO']

    def constructor(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method == 'Append':
            return {'Text': 'text', 'Help': 'help',
                    'Kind': 'kind', 'ItemId': 'id'}
        elif tcl.method == 'AppendSeparator':
            return {}
        elif tcl.method == 'AppendMenu':
            return {'Text': 'text', 'Help': 'help',
                    'Menu': 'submenu', 'ItemId': 'id'}

    def properties(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method in ('Append', 'AppendMenu'):
            props = CollectionIddDTC.properties(self)
            props.update(
                {'Text': ('IdRoute', wx.Menu.GetLabel, wx.Menu.SetLabel),
                 'Help': ('IdRoute', wx.Menu.GetHelpString, wx.Menu.SetHelpString)})
        elif tcl.method == 'AppendSeparator':
            props = {}

        return props

    def designTimeSource(self, wId, method=None):
        if method is None:
            method = self.insertionMethod

        newItemName, winId = self.newUnusedItemNames(wId)

        if method == 'Append':
            return {'id': winId,
                    'text': `newItemName`,
                    'help': `''`,
                    'kind': 'wx.ITEM_NORMAL'}
        elif method == 'AppendSeparator':
            return {}
        elif method == 'AppendMenu':
            return {'id': winId,
                    'text': `newItemName`,
                    'submenu': 'wx.Menu()',
                    'help': `''`}

    def designTimeDefaults(self, vals, method=None):
        if method is None:
            method = self.insertionMethod

        dtd = {}
        for param in vals.keys():
            if param == 'submenu':
                name = vals[param]
                if name[:4] == 'self':
                    dtd[param] = self.designer.objects[name[5:]][1]
                elif name == 'wx.Menu()':
                    dtd[param] = wx.Menu()
                else:
                    raise Exception, _('Invalid menu reference: %s')%name
            elif param == self.idProp:
                dtd[param] = wx.NewId()
            else:
                dtd[param] = self.eval(vals[param])

        return dtd

    def events(self):
        return ['MenuEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('MenuEvent', 'wx.EVT_MENU')

    def moveItem(self, idx, dir):
        newIdx = CollectionIddDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            menus = self.control.GetMenuItems()
            menu = self.control.RemoveItem(menus[idx])
            self.control.InsertItem(newIdx, menu)
        return newIdx

    def deleteItem(self, idx):
        menuItm = self.control.GetMenuItems()[idx]
        self.control.RemoveItem(menuItm)
        self.deleteItemEvents(idx)
        del self.textConstrLst[idx]

        self.updateWindowIds()

    def notification(self, compn, action):
        if action == 'delete':
            if compn != self:
                compnSrcRef = Utils.srcRefFromCtrlName(compn.name)
                for constr in self.textConstrLst:
                    if 'submenu' in constr.params:
                        if compnSrcRef == constr.params['submenu']:
                            constr.params['submenu'] = 'wx.Menu()'

    def GetMenu(self):
        return self.textConstrLst[self.index].params['submenu']

    def SetMenu(self, value):
        self.textConstrLst[self.index].params['submenu'] = value


class MenuBarDTC(UtilityDTC):
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'Menus': CollectionPropEdit})
        self.subCompanions['Menus'] = MenuBarMenusCDTC

    def constructor(self):
        return {'Style': 'style', 'Name': 'name'}

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Menus':  ('NoneRoute', None, None)})
        return props

    def dependentProps(self):
        return UtilityDTC.dependentProps(self) + ['Menus']

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {}

    def initDesignTimeControl(self):
        pass

    def vetoedMethods(self):
        return UtilityDTC.vetoedMethods(self)+['GetPosition', 'SetPosition',
               'GetSize', 'SetSize', 'GetRect', 'SetRect']

    def hideDesignTime(self):
        return []

    def defaultAction(self):
        nv  = self.designer.inspector.props.getNameValue('Menus')
        if nv:
            nv.propEditor.edit(None)

class MenuBarMenusCDTC(CollectionDTC):
    propName = 'Menus'
    displayProp = 'title'
    indexProp = '(None)'
    insertionMethod = 'Append'
    deletionMethod = 'Remove'


    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Menu': MenuEnumConstrPropEdit,
                             'Title': StrConstrPropEdit})

    def constructor(self):
        return {'Menu': 'menu', 'Title': 'title'}

    def designTimeSource(self, wId, method=None):
        return {'menu': 'wx.Menu()',
                'title': `'%s%d'%(self.propName, wId)`}

    def designTimeDefaults(self, vals, method=None):
        dtd = {}
        for param in vals.keys():
            if param == 'menu':
                name = vals[param]
                if name[:4] == 'self':
                    dtd[param] = self.designer.objects[name[5:]][1]
                elif name == 'wx.Menu()':
                    dtd[param] = wx.Menu()
                else:
                    raise Exception, _('Invalid menu reference: %s')%name
            else:
                dtd[param] = self.eval(vals[param])

        return dtd

    def moveItem(self, idx, dir):
        newIdx = CollectionDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            title = self.control.GetLabelTop(idx)
            menu = self.control.Remove(idx)
            self.control.Insert(newIdx, menu, title)
        return newIdx

    def vetoedMethods(self):
        return CollectionDTC.vetoedMethods(self)+['GetPosition', 'SetPosition',
              'GetSize', 'SetSize']

    def GetMenu(self):
        return self.textConstrLst[self.index].params['menu']

    def SetMenu(self, value):
        self.textConstrLst[self.index].params['menu'] = value

#class LayoutConstraintsDTC(Constructors.EmptyConstr, UtilityDTC):
#    def __init__(self, name, designer, objClass):
#        UtilityDTC.__init__(self, name, designer, objClass)
#        self.editors.update({'Constraints': CollPropEdit})
#        self.subCompanions['Constraints'] = IndividualLayoutConstraintCDTC
#
#    def properties(self):
#        props = UtilityDTC.properties(self)
#        props.update({'Constraints': ('NoneRoute', None, None)})
#        return props

cursorIconTypes = ['wx.BITMAP_TYPE_XBM', 'wx.BITMAP_TYPE_CUR',
                   'wx.BITMAP_TYPE_CUR_RESOURCE', 'wx.BITMAP_TYPE_ICO']

class CursorDTC(UtilityDTC):
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'CursorName': StrConstrPropEdit,
                             'Flags': EnumConstrPropEdit,
                             'HotSpotX': IntConstrPropEdit,
                             'HotSpotY': IntConstrPropEdit,
                             'Visible': BoolPropEdit})
        self.names['Flags'] = cursorIconTypes

    def constructor(self):
        return {'CursorName': 'cursorName', 'Flags': 'flags',
                'HotSpotX': 'hotSpotX', 'HotSpotY': 'hotSpotY'}
    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {'cursorName': "''",
                'flags': 'wx.BITMAP_TYPE_CUR',
                'hotSpotX': '0',
                'hotSpotY': '0'}

stockCursorIds = ['wx.CURSOR_ARROW', 'wx.CURSOR_BULLSEYE', 'wx.CURSOR_CHAR',
      'wx.CURSOR_CROSS', 'wx.CURSOR_HAND', 'wx.CURSOR_IBEAM', 'wx.CURSOR_LEFT_BUTTON',
      'wx.CURSOR_MAGNIFIER', 'wx.CURSOR_MIDDLE_BUTTON', 'wx.CURSOR_NO_ENTRY',
      'wx.CURSOR_PAINT_BRUSH', 'wx.CURSOR_PENCIL', 'wx.CURSOR_POINT_LEFT',
      'wx.CURSOR_POINT_RIGHT', 'wx.CURSOR_QUESTION_ARROW', 'wx.CURSOR_RIGHT_BUTTON',
      'wx.CURSOR_SIZENESW', 'wx.CURSOR_SIZENS', 'wx.CURSOR_SIZENWSE', 'wx.CURSOR_SIZEWE',
      'wx.CURSOR_SIZING', 'wx.CURSOR_SPRAYCAN', 'wx.CURSOR_WAIT', 'wx.CURSOR_WATCH',
      'wx.CURSOR_ARROWWAIT']

class StockCursorDTC(UtilityDTC):
    handledConstrParams = ()
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors.update({'CursorId': EnumConstrPropEdit,
                             'Visible': BoolPropEdit})
        self.names['CursorId'] = stockCursorIds

    def hideDesignTime(self):
        return ['Handle']
    def constructor(self):
        return {'CursorId': 'id'}
    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {'id': 'wx.CURSOR_ARROW'}


#-------------------------------------------------------------------------------
import Plugins

Plugins.registerPalettePage('Utilities (Data)', _('Utilities (Data)'))

Plugins.registerComponents('Utilities (Data)',
      (wx.MenuBar, 'wx.MenuBar', MenuBarDTC),
      (wx.Menu, 'wx.Menu', MenuDTC),
      (wx.ImageList, 'wx.ImageList', ImageListDTC),
      (wx.Timer, 'wx.Timer', TimerDTC),
      (wx.StockCursor, 'wx.StockCursor', StockCursorDTC),

      #(wx.AcceleratorTable, 'wx.AcceleratorTable', AcceleratorTableDTC),
      #(wxCursor: ['wx.Cursor', CursorDTC],

      # these objects need design time inheritance
      #(wxTextDropTarget, 'wx.TextDropTarget', NYIDTC),
      #(wxFileDropTarget, 'wx.FileDropTarget', NYIDTC),
    )
