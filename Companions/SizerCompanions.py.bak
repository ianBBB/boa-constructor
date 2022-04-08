#-----------------------------------------------------------------------------
# Name:        SizerCompanions.py
# Purpose:     Companion classes for Sizer objects
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing Companions.SizerCompanions'

# XXX _in_sizer is not necessary, use GetContainingSizer() instead

import os, sys, copy

import wx

#from wx.lib.rcsizer import RowColSizer

import Preferences, Utils
from Utils import _

from BaseCompanions import UtilityDTC, CollectionDTC, CollectionIddDTC, NYIDTC, HelperDTC
import Companions

from PropEdit.PropertyEditors import IntConstrPropEdit, StrConstrPropEdit, \
      CollectionPropEdit, ObjEnumConstrPropEdit, EnumConstrPropEdit, \
      FlagsConstrPropEdit, WinEnumConstrPropEdit, BoolConstrPropEdit, \
      BoolPropEdit, EnumPropEdit, ReadOnlyConstrPropEdit, \
      SizerEnumConstrPropEdit, SizeConstrPropEdit, ConstrPropEdit, \
      IntPropEdit, esExpandable

from PropEdit.InspectorEditorControls import TextCtrlIEC
from PropEdit.FlexGridGrowablesDlg import FlexGridGrowablesDlg

from PropEdit import Enumerations
import EventCollections, RTTI, methodparse


class SizerItemsColPropEdit(CollectionPropEdit): pass

class BlankSizer(wx.BoxSizer):
    """ Used as a placeholder for initial sizer items which has None for
        the window or sizer """
    def __init__(self):
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        self.AddSpacer((24, 24))

class SizerDTC(UtilityDTC):
    host = 'Sizers'
    def __init__(self, name, designer, objClass):
        UtilityDTC.__init__(self, name, designer, objClass)
        self.editors['Items'] = SizerItemsColPropEdit
        self.subCompanions['Items'] = SizerItemsCDTC

    def properties(self):
        props = UtilityDTC.properties(self)
        props.update({'Items': ('NoneRoute', None, None)})
        return props

    def dependentProps(self):
        return UtilityDTC.dependentProps(self) + ['Items']

    def designTimeSource(self):
        return {}

    def defaultAction(self):
        nv = self.designer.inspector.props.getNameValue('Items')
        if nv: nv.propEditor.edit(None)

    def renameCtrl(self, oldName, newName):
        UtilityDTC.renameCtrl(self, oldName, newName)

        self.designer.checkSizerConnectRename(oldName, newName)

    def renameCtrlRefs(self, oldName, newName):
        UtilityDTC.renameCtrlRefs(self, oldName, newName)

        self.designer.checkCollectionRename(oldName, newName, self)

    def recreateSizer(self):
        args = self.designer.setupArgs(self.name, self.textConstr.params,
          self.handledConstrParams, evalDct = self.designer.model.specialAttrs)
        self.control = self.designTimeObject(args)
        self.designer.objects[self.name][1] = self.control

    def recreateSizerItems(self):
        for collComp in self.collections.values():
            collComp.control = self.control
            for crt in collComp.textConstrLst:
                collComp.applyDesignTimeDefaults(crt.params, crt.method)


class SizerFlagsDTC(Companions.FlagsDTC):
    paramName = 'flag'
    propName = 'Flag'

class SizerFlagsConstrPropEdit(FlagsConstrPropEdit):
    def getSubCompanion(self):
        return SizerFlagsDTC

class SizerWinEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def getObjects(self):
        designer = self.companion.designer.controllerView
        windows = designer.getObjectsOfClass(wx.Window)
        for n, w in windows.items():
            if hasattr(w, '_in_sizer') or n == 'self':
                del windows[n]
        windowNames = windows.keys()
        windowNames.sort()
        res = ['None'] + windowNames
        if self.value != 'None':
            res.insert(1, self.value)
        return res

    def getCtrlValue(self):
        return self.companion.GetWindow()
    def setCtrlValue(self, oldValue, value):
        self.companion.SetWindow(value)

# XXX Remove 'Insert' special casing, no longer used

class SizerItemsCDTC(CollectionDTC):
    propName = 'Items'
    displayProp = 0
    indexProp = '(None)'
    insertionMethod = 'AddWindow'
    deletionMethod = 'Remove'

    additionalMethods = { 'AddSizer': (_('Add sizer'), 0, '(None)'),
                          'AddSpacer': (_('Add spacer'), '', '(None)'),
                          #'AddStretchSpacer': ('Add stretch spacer', '', '(None)')
                        }

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Window': SizerWinEnumConstrPropEdit,
                        'Sizer': SizerEnumConstrPropEdit,
                        'Proportion': IntConstrPropEdit,
                        'Flag': SizerFlagsConstrPropEdit,
                        'Border': IntConstrPropEdit,
                        'Size': SizeConstrPropEdit,
                       }
        self.windowStyles = ['wx.LEFT', 'wx.RIGHT', 'wx.TOP', 'wx.BOTTOM', 'wx.ALL',
                             'wx.SHRINK', 'wx.GROW', 'wx.EXPAND', 'wx.SHAPED',
                             'wx.ALIGN_LEFT', 'wx.ALIGN_CENTER_HORIZONTAL',
                             'wx.ALIGN_RIGHT', 'wx.ALIGN_BOTTOM',
                             'wx.ALIGN_CENTER_VERTICAL', 'wx.ALIGN_TOP',
                             'wx.ALIGN_CENTER', 'wx.ADJUST_MINSIZE']

    def constructor(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method == 'AddWindow':
            return {'Window': 0, 'Proportion': 1, 'Flag': 'flag',
                    'Border': 'border'}
        elif tcl.method == 'AddSizer':
            return {'Sizer': 0, 'Proportion': 1, 'Flag': 'flag',
                    'Border': 'border'}
        elif tcl.method == 'AddSpacer':
            return {'Size': 0, 'Flag': 'flag',
                    'Border': 'border'}
        #elif tcl.method == 'AddStretchSpacer':
        #    return {'Proportion': 0}

    def designTimeSource(self, wId, method=None):
        if method is None:
            method = self.insertionMethod

        if method == 'AddWindow':
            return {0: 'None', 1: '0', 'flag': '0', 'border': '0'}
        elif method == 'AddSizer':
            return {0: 'None', 1: '0', 'flag': '0', 'border': '0'}
        elif method == 'AddSpacer':
            return {0: 'wx.Size(8, 8)', 'flag': '0', 'border': '0'}
        #elif method == 'AddStretchSpacer':
        #    return {0: '1'}

    def notification(self, compn, action):
        if action == 'delete':
            if not isinstance(compn, CollectionDTC):
                compnSrcRef = Utils.srcRefFromCtrlName(compn.name)
                for constr in self.textConstrLst:
                    if compnSrcRef == constr.params[0]:
                        constr.params[0] = 'None'
                        self.recreateSizers()
                        return

    def appendItem(self, method=None, srcParams={}):
        CollectionDTC.appendItem(self, method, srcParams)
        
        self.recreateSizers()
        #self.updateGUI()

    def deleteItem(self, idx):
        CollectionDTC.deleteItem(self, idx)
        del self.textConstrLst[idx]
        self.recreateSizers()
        #self.updateGUI()

    def moveItem(self, idx, dir):
        newIdx = CollectionDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            self.recreateSizers()
        return newIdx

    def defaultAction(self):
        constr = self.textConstrLst[self.index]
        if constr.method == 'AddWindow':
            if constr.params[0] != 'None':
                name = Utils.ctrlNameFromSrcRef(constr.params[0])
                designer = self.designer.controllerView
                compn, ctrl = designer.objects[name][:2]
                designer.inspector.selectObject(compn, True)
                designer.Raise()
                designer.selection.selectCtrl(ctrl, compn)

                wx.CallAfter(designer.SetFocus)
                return True

        elif constr.method == 'AddSizer':
            if constr.params[0] != 'None':
                name = Utils.ctrlNameFromSrcRef(constr.params[0])
                compn = self.designer.objects[name][0]
                self.designer.inspector.selectObject(compn, True)
                self.designer.selectCtrls([name])

                wx.CallAfter(self.designer.SetFocus)
                return True

    def designTimeDefaults(self, vals, method=None):
        if method is None:
            method = self.insertionMethod

        if method in ('AddWindow', 'AddSizer', 'Insert'):
            if method in ('AddWindow', 'AddSizer'): ctrlIdx = 0
            elif method == 'Insert':                ctrlIdx = 1

            if vals[ctrlIdx] != 'None':
                srcRef = vals[ctrlIdx]
                try:
                    # XXX improve
                    int(srcRef)
                except:
                    params = copy.copy(vals)
                    del params[ctrlIdx]
                    dtd = CollectionDTC.designTimeDefaults(self, params, method)
                    dtd[ctrlIdx] = self.designer.controllerView.getAllObjects()[srcRef]
                    if method == 'AddSizer':
                        dtd[ctrlIdx]._sub_sizer = self.control
                    elif method == 'AddWindow':
                        dtd[ctrlIdx]._in_sizer = self.control
                    return dtd

        return CollectionDTC.designTimeDefaults(self, vals, method)

    def applyDesignTimeDefaults(self, params, method=None):
        if method is None:
            method = self.insertionMethod

        if (method in ('AddWindow', 'AddSizer') and params[0] == 'None') or \
           (method == 'Insert' and params[1] == 'None'):
            defaults = self.designTimeDefaults(params, method)
            if method == 'Insert':
                proportion = defaults[2]
                import warnings; warnings.warn('Insert called with BlankSizer')
            else:
                proportion = defaults[1]
            self.control.AddSizer(BlankSizer(), proportion, defaults['flag'],
                                  defaults['border'])
        else:
            CollectionDTC.applyDesignTimeDefaults(self, params, method)

    def setParamAndUpdate(self, key, value):
        constr = self.textConstrLst[self.index]
        constr.params[key] = value
        self.recreateSizers()

    def GetWindow(self):
        return self.textConstrLst[self.index].params[0]
    def SetWindow(self, value):
        self.setParamAndUpdate(0, value)
        colEdKey = (self.parentCompanion.name, 'Items')
        if colEdKey in self.designer.collEditors:
            collEditView = self.designer.collEditors[colEdKey]
            wx.CallAfter(self.setWindowRefresh, collEditView)

    def setWindowRefresh(self, collEditView):
        collEditView.refreshCtrl(1)
        collEditView.selectObject(self.index)
        if collEditView.frame:
            collEditView.frame.selectObject(self.index)


    GetSizer = GetWindow
    SetSizer = SetWindow

    def persistProp(self, name, setterName, value):
        CollectionDTC.persistProp(self, name, setterName, value)
        if name in ('Size',):
            self.recreateSizers()
        elif name in ('Flag', 'Border', 'Proportion'):
            si = self.control.GetChildren()[self.index]
            getattr(si, 'Set'+name)(self.eval(value))
            self.updateGUI()

    def writeCollectionItems(self, output, stripFrmId=''):
        CollectionDTC.writeCollectionItems(self, output, stripFrmId)
        warn = 0
        for constr in self.textConstrLst:
            if constr.params[0] == 'None':
                wx.LogWarning(_('No control/sizer for sizer item of %s')%(
                      self.parentCompanion.name))
                warn = 1
        if warn:
            wx.LogWarning(_('None values are only valid in the Designer.\n'
                            'The generated source will be invalid outside the '
                            'Designer and should be fixed before executing.'))
  
    def recreateSizers(self):
        self.designer.recreateSizers()
        self.updateGUI()

    def updateGUI(self):
        self.control.Layout()
        wx.CallAfter(self.designer.controllerView.Refresh)

class BoxSizerDTC(SizerDTC):
    def __init__(self, name, designer, objClass):
        SizerDTC.__init__(self, name, designer, objClass)
        self.editors['Orientation'] = EnumPropEdit
        self.names['Orientation'] = {'wx.VERTICAL': wx.VERTICAL,
                                     'wx.HORIZONTAL': wx.HORIZONTAL}
        self.options['Orientation'] = [wx.VERTICAL, wx.HORIZONTAL]

    def constructor(self):
        return {'Name': 'name', 'Orientation': 'orient'}

    def designTimeSource(self):
        return {'orient': 'wx.VERTICAL'}

class GridSizerDTC(SizerDTC):
    def constructor(self):
        return {'Name': 'name', 'Rows': 'rows', 'Cols': 'cols',
                'VGap': 'vgap', 'HGap': 'hgap'}

    def designTimeSource(self):
        return {'rows': '1', 'cols': '0', 'vgap': '0', 'hgap': '0'}


class GrowablesColPropEdit(CollectionPropEdit):
    def edit(self, event):
        ce = self.companion.designer.showCollectionEditor(self.companion.name,
              self.name, False)

        growableRows, growableCols = ce.companion.getGrowables()

        fgsCompn = ce.companion.parentCompanion
        numRows, numCols = fgsCompn.getNumRowsCols(ce.companion)

        if not numRows and not numCols:
            wx.LogError(_('Rows and Cols may not both be 0'))
            return

        if not numRows or not numCols:
            numItems = len(self.companion.designer.showCollectionEditor(
                self.companion.name, 'Items', False).companion.textConstrLst)
        else:
            numItems = -1

        rows, cols = [], []
        if not numRows:
            numRows = numItems/float(numCols)
            numRows = int(numRows)+(numRows > int(numRows))
        for row in range(numRows):
            rows.append(row in growableRows)

        if not numCols:
            numCols = numItems/float(numRows)
            numCols = int(numCols)+(numCols > int(numCols))
        for col in range(numCols):
            cols.append(col in growableCols)

        dlg = FlexGridGrowablesDlg(self.parent, rows, cols)
        try:
            res = dlg.ShowModal()
            if res == wx.ID_CANCEL:
                return
            if res == wx.ID_YES:
                ce.show()
                return

            rows = dlg.rows
            cols = dlg.cols
        finally:
            dlg.Destroy()

        ce.companion.setGrowables(rows, cols)
        ce.companion.recreateSizers()


class GrowablesCDTC(CollectionDTC):
    propName = 'Growables'
    displayProp = 0
    indexProp = '(None)'
    insertionMethod = '(None)'
    deletionMethod = '(None)'

    additionalMethods = { 'AddGrowableRow': ('Add growable row', 0, '(None)'),
                          'AddGrowableCol': ('Add growable column', 0, '(None)')
                        }

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors['Index'] = IntConstrPropEdit

    def constructor(self):
        return {'Index': 0}

    def designTimeSource(self, wId, method=None):
        return {0: '0'}

    def getGrowables(self):
        rows, cols = [], []
        for constr in self.textConstrLst:
            if constr.method == 'AddGrowableRow':
                rows.append(self.eval(constr.params[0]))
            elif constr.method == 'AddGrowableCol':
                cols.append(self.eval(constr.params[0]))
        return rows, cols

    def _appendItem(self, method, idx):
        self.index = self.getCount()
        if method is None:
            method = self.insertionMethod
        collItemInit = methodparse.CollectionItemInitParse(None,
          self.sourceObjName, method, {0: str(idx)})

        self.textConstrLst.append(collItemInit)
        self.setConstr(collItemInit)

    def setGrowables(self, rows, cols):
        self.textConstrLst = []
        for idx, row in zip(range(len(rows)), rows):
            if row:
                self._appendItem('AddGrowableRow', idx)
        for idx, col in zip(range(len(cols)), cols):
            if col:
                self._appendItem('AddGrowableCol', idx)

    def recreateSizers(self):
        self.designer.recreateSizers()
        self.updateGUI()

    def updateGUI(self):
        self.control.Layout()
        wx.CallAfter(self.designer.controllerView.Refresh)


class FlexGridSizerDTC(GridSizerDTC):
    def __init__(self, name, designer, objClass):
        GridSizerDTC.__init__(self, name, designer, objClass)
        self.editors['Growables'] = GrowablesColPropEdit
        self.subCompanions['Growables'] = GrowablesCDTC

        self.editors['FlexibleDirection'] = EnumPropEdit
        self.names['FlexibleDirection'] = {'wx.VERTICAL': wx.VERTICAL,
                                     'wx.HORIZONTAL': wx.HORIZONTAL,
                                     'wx.BOTH': wx.BOTH}
        self.options['FlexibleDirection'] = [wx.VERTICAL, wx.HORIZONTAL, wx.BOTH]

        self.editors['NonFlexibleGrowMode'] = EnumPropEdit
        self.names['NonFlexibleGrowMode'] = {'wx.FLEX_GROWMODE_NONE': wx.FLEX_GROWMODE_NONE,
              'wx.FLEX_GROWMODE_SPECIFIED': wx.FLEX_GROWMODE_SPECIFIED,
              'wx.FLEX_GROWMODE_ALL': wx.FLEX_GROWMODE_ALL}
        self.options['NonFlexibleGrowMode'] = [wx.FLEX_GROWMODE_NONE, 
                                               wx.FLEX_GROWMODE_SPECIFIED,
                                               wx.FLEX_GROWMODE_ALL]

    def properties(self):
        props = GridSizerDTC.properties(self)
        props.update({'Growables': ('NoneRoute', None, None)})
        return props

    def dependentProps(self):
        return GridSizerDTC.dependentProps(self) + ['Growables']

    def getNumRowsCols(self, childCompanion):
        numRows = self.eval(self.textConstr.params['rows'])
        numCols = self.eval(self.textConstr.params['cols'])
        
        return numRows, numCols

#class RowColSizerDTC(FlexGridSizerDTC):
#    def writeImports(self):
#        return '\n'.join( (GridSizerDTC.writeImports(self),
#                           'from wx.lib.rcsizer import RowColSizer') )

class ControlLinkedSizerDTC(SizerDTC):
    LinkClass = None
    ctrlParam = ''
    _linkName = ''
    def designTimeObject(self, args = None):
        if args is not None:
            self.control = self.objClass(**args)
        else:
            linkClassName = self.LinkClass.__name__[:-3]
            dtd = self.designTimeDefaults()
            linkObjs = self.designer.controllerView.getObjectsOfClass(self.LinkClass).items()
            if not linkObjs:
                raise Exception, _('No %s controls available')%linkClassName

            linkObjs.sort()
            names, objs = [], []
            for name, obj in linkObjs:
                names.append(name); objs.append(obj)

            dlg = wx.SingleChoiceDialog(self.designer, _('Choose control'),
                  _('Create sizer'), names)
            try:
                if dlg.ShowModal() != wx.ID_OK:
                    raise Exception, _('Must choose a control to link with sizer')
                idx = dlg.GetSelection()
            finally:
                dlg.Destroy()

            self._linkName = names[idx]
            dtd[self.ctrlParam] = objs[idx]

            self.control = self.objClass(**dtd)

        return self.control

    def setConstr(self, constr):
        if self._linkName:
            constr.params[self.ctrlParam] = self._linkName
        SizerDTC.setConstr(self, constr)

    def persistConstr(self, className, params):
        if self._linkName:
            params[self.ctrlParam] = self._linkName
        SizerDTC.persistConstr(self, className, params)

    def notification(self, compn, action):
        if action == 'delete' and compn != self:
            compnSrcRef = Utils.srcRefFromCtrlName(compn.name)
            if self.ctrlParam in self.textConstr.params and \
                  compnSrcRef == self.textConstr.params[self.ctrlParam]:
                self.designer.deleteCtrl(self.name)


class StaticBoxSizerDTC(ControlLinkedSizerDTC):
    LinkClass = wx.StaticBox
    ctrlParam = 'box'
    def __init__(self, name, designer, objClass):
        ControlLinkedSizerDTC.__init__(self, name, designer, objClass)
        self.editors['Orientation'] = EnumPropEdit
        self.names['Orientation'] = {'wx.VERTICAL': wx.VERTICAL,
                                     'wx.HORIZONTAL': wx.HORIZONTAL}
        self.options['Orientation'] = [wx.VERTICAL, wx.HORIZONTAL]
        self.editors['StaticBox'] = ReadOnlyConstrPropEdit
        
        self._staticBoxParent = None
        self._staticBoxLabel = ''
        self._staticBoxName = wx.StaticBoxNameStr

    def constructor(self):
        return {'Name': 'name', 'StaticBox': 'box', 'Orientation': 'orient'}

    def designTimeSource(self):
        return {'box': 'None', 'orient': 'wx.VERTICAL'}

    def designTimeObject(self, args = None):
        if args and 'box' in args:
            b = args['box']
            if b is not None:
                if not b: # deleted static box
                    args['box'] = wx.StaticBox(self._staticBoxParent, -1, 
                          self._staticBoxLabel, name=self._staticBoxName)
                else:
                    self._staticBoxParent = b.GetParent()
                    self._staticBoxLabel = b.GetLabel()
                    self._staticBoxName = b.GetName()
                
        return ControlLinkedSizerDTC.designTimeObject(self, args)


##class NotebookSizerDTC(ControlLinkedSizerDTC):
##    LinkClass = wx.Notebook
##    ctrlParam = 'nb'
##    def __init__(self, name, designer, objClass):
##        ControlLinkedSizerDTC.__init__(self, name, designer, objClass)
##        self.editors['Notebook'] = ReadOnlyConstrPropEdit
##
##    def constructor(self):
##        return {'Name': 'name', 'Notebook': 'nb'}
##
##    def designTimeSource(self):
##        wx.LogWarning('wx.NotebookSizer no longer needed, please remove from source. Support will be removed.')
##        return {'nb': 'None'}
##
##    def properties(self):
##        props = ControlLinkedSizerDTC.properties(self)
##        del props['Items']
##        return props
##
##    def defaultAction(self):
##        pass

class GridBagSizerDTC(FlexGridSizerDTC):
    def __init__(self, name, designer, objClass):
        FlexGridSizerDTC.__init__(self, name, designer, objClass)
        self.subCompanions['Items'] = GBSizerItemsCDTC

    def constructor(self):
        return {'Name': 'name', 'VGap': 'vgap', 'HGap': 'hgap'}

    def designTimeSource(self):
        return {'vgap': '0', 'hgap': '0'}

    def getNumRowsCols(self, childCompanion):
        maxRows = 0
        maxCols = 0
        for si in self.control.GetChildren():
            (sipr, sipc), (sisr, sisc) = si.GetPos(), si.GetSpan()
            if sipr + sisr > maxRows:
                maxRows = sipr + sisr
            if sipc + sisc > maxCols:
                maxCols = sipc + sisc
            
        return maxRows, maxCols

class GBSizerItemsCDTC(SizerItemsCDTC):
    def __init__(self, name, designer, parentCompanion, ctrl):
        SizerItemsCDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Position': PositionTuplePropEdit,
                             'Span': SpanTuplePropEdit })
    def constructor(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method == 'AddWindow':
            return {'Window': 0, 'Position': 1, 
                    'Span': 'span', 'Flag': 'flag', 'Border': 'border'}
        elif tcl.method == 'AddSizer':
            return {'Sizer': 0, 'Position': 1, 
                    'Span': 'span', 'Flag': 'flag', 'Border': 'border'}
        elif tcl.method == 'AddSpacer':
            return {'Size': 0, 'Position': 1, 
                    'Span': 'span', 'Flag': 'flag', 'Border': 'border'}

    def designTimeSource(self, wId, method=None):
        if method is None:
            method = self.insertionMethod

        pos = self.findOpenPosition()

        if method == 'AddWindow':
            return {0: 'None', 1: repr(pos),  'span': '(1, 1)', 
                    'flag': '0', 'border': '0'}
        elif method == 'AddSizer':
            return {0: 'None', 1: repr(pos), 'span': '(1, 1)', 
                    'flag': '0', 'border': '0'}
        elif method == 'AddSpacer':
            return {0: 'wx.Size(8, 8)', 1: repr(pos), 'span': '(1, 1)', 
                    'flag': '0', 'border': '0'}

    def findOpenPosition(self):
        pos = [0, 0]
        while self.control.FindItemAtPosition(tuple(pos)):
            pos[1] += 1
        return tuple(pos)

    def applyDesignTimeDefaults(self, params, method=None):
        if method is None:
            method = self.insertionMethod

        pos = self.eval(params[1])
        if self.control.FindItemAtPosition(pos):
            raise Exception, _('Cannot use Position %s, an item is already at that position')%params[1]
        if pos[0] < 0 or pos[1] < 0:
            raise Exception, _('Position %s invalid, cannot contain negative values')%params[1]
        
        span = self.eval(params['span'])
        if span[0] < 0 or span[1] < 0:
            raise Exception, _('Span %s invalid, cannot contain negative values')%params[1]
        

        if (method in ('AddWindow', 'AddSizer') and params[0] == 'None') or \
           (method == 'Insert' and params[1] == 'None'):
            defaults = self.designTimeDefaults(params, method)
            self.control.AddSizer(BlankSizer(), defaults[1], 
                  defaults['span'], defaults['flag'], defaults['border'])
        else:
            SizerItemsCDTC.applyDesignTimeDefaults(self, params, method)

    def getSizerGUIObject(self):
        """ Returns a control, sizer, integer or None """
        constr = self.textConstrLst[self.index]
        
        srcRef = constr.params[0]
        if srcRef != 'None':
            if srcRef.startswith('wx.Size'):
                return self.index
            else:
                return self.designer.controllerView.getAllObjects()[srcRef]
        else:
            return None

    def persistProp(self, name, setterName, value):
        SizerItemsCDTC.persistProp(self, name, setterName, value)
        if name in ('Position', 'Span'):
            obj = self.getSizerGUIObject()
            if obj is not None:
                getattr(self.control, 'SetItem'+name)(obj, self.eval(value))
                self.updateGUI()

class TupleConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

class PositionTuplePropEdit(TupleConstrPropEdit):
    def getStyle(self):
        return [esExpandable]
    def getSubCompanion(self):
        return PositionRowColDTC

class SpanTuplePropEdit(TupleConstrPropEdit):
    def getStyle(self):
        return [esExpandable]
    def getSubCompanion(self):
        return SpanRowColDTC

class PositiveIntPropEdit(IntPropEdit):
    def inspectorEdit(self):
        IntPropEdit.inspectorEdit(self)
        self.editorCtrl.editorCtrl.SetRange(0, 2L**31-1)
    
class RowColDTC(HelperDTC):
    propName = 'Prop'
    paramName = 'param'
    setterMethod = 'Setter'
    
    def __init__(self, name, designer, cmpn, obj, ownerPW):
        HelperDTC.__init__(self, name, designer, cmpn, obj, ownerPW)
        self.editors = {'Row' : PositiveIntPropEdit,
                        'Column' : PositiveIntPropEdit}

    def properties(self):
        return {'Row': ('NameRoute', self.GetRowCol, self.SetRowCol),
                'Column': ('NameRoute', self.GetRowCol, self.SetRowCol)}

    def GetRowCol(self, name):
        t = self.eval(self.ownerCompn.textConstr.params[self.paramName])
        if name == 'Row': 
            return t[0]
        elif name == 'Column': 
            return t[1]
        
    def SetRowCol(self, name, value):
        t = self.eval(self.ownerCompn.textConstr.params[self.paramName])
        obj = self.ownerCompn.getSizerGUIObject()
        if name == 'Row': 
            newVal = (value, t[1])
        elif name == 'Column': 
            newVal = (t[0], value)
        self.ownerCompn.textConstr.params[self.paramName] = `newVal`
        self.designer.inspector.constructorUpdate(self.propName)
        # XXX Setting to an existing position causes asserts and is wrong
        # XXX Not sure how to handle this everywhere in the GridBagSizer support
        getattr(self.ownerCompn.control, self.setterMethod)( obj, newVal )


class PositionRowColDTC(RowColDTC):
    propName = 'Position'
    paramName = 1
    setterMethod = 'SetItemPosition'

class SpanRowColDTC(RowColDTC):
    propName = 'Span'
    paramName = 'span'
    setterMethod = 'SetItemSpan'

#-------------------------------------------------------------------------------

import Plugins

Plugins.registerComponents('ContainersLayout',
      (wx.BoxSizer, 'wx.BoxSizer', BoxSizerDTC),
      (wx.GridSizer, 'wx.GridSizer', GridSizerDTC),
      (wx.FlexGridSizer, 'wx.FlexGridSizer', FlexGridSizerDTC),
      (wx.StaticBoxSizer, 'wx.StaticBoxSizer', StaticBoxSizerDTC),
#      (wx.NotebookSizer, 'wx.NotebookSizer', NotebookSizerDTC),
      (wx.GridBagSizer, 'wx.GridBagSizer', GridBagSizerDTC),
    )
