#----------------------------------------------------------------------
# Name:        DataView.py
# Purpose:     Designer for Utility (non visual) objects
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
print 'importing Views.DataView'

import os, copy

import wx

import Preferences, Utils
from Utils import _

import sourceconst
import PaletteMapping, PaletteStore, Help

from InspectableViews import InspectableObjectView, DesignerError
import ObjCollection

class DataView(wx.ListView, InspectableObjectView):
    viewName = 'Data'
    viewTitle = _('Data')
    
    collectionMethod = sourceconst.init_utils
    postBmp = 'Images/Inspector/Post.png'
    cancelBmp = 'Images/Inspector/Cancel.png'
    def __init__(self, parent, inspector, model, compPal):
        [self.wxID_DATAVIEW] = [wx.NewId() for _init_ctrls in range(1)]
        wx.ListView.__init__(self, parent, self.wxID_DATAVIEW, size=(0,0),
              style=Preferences.dataViewListStyle | wx.SUNKEN_BORDER)

        InspectableObjectView.__init__(self, inspector, model, compPal,
          ((_('Default editor'), self.OnDefaultEditor, '-', ''),
           (_('Post'), self.OnPost, self.postBmp, ''),
           (_('Cancel'), self.OnCancel, self.cancelBmp, ''),
           ('-', None, '-', ''),
           (_('Cut'), self.OnCutSelected, '-', ''),
           (_('Copy'), self.OnCopySelected, '-', 'Copy'),
           (_('Paste'), self.OnPasteSelected, '-', 'Paste'),
           (_('Delete'), self.OnControlDelete, '-', 'Delete'),
           ('-', None, '-', ''),
           (_('Creation/Tab order...'), self.OnCreationOrder, '-', ''),
           ('-', None, '-', ''),
           (_('Context help'), self.OnContextHelp, '-', 'ContextHelp'),
           ), 0)

        self.il = wx.ImageList(24, 24)
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnSelectOrAdd)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnObjectSelect, id=self.wxID_DATAVIEW)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnObjectDeselect, id=self.wxID_DATAVIEW)

        self.selection = []
        self.vetoSelect = False

        self.active = True

    def initialize(self):
        if self.model.objectCollections.has_key(self.collectionMethod):
            objCol = self.model.objectCollections[self.collectionMethod]
            objCol.indexOnCtrlName()
        else:
            objCol = ObjCollection.ObjectCollection()

        deps, depLinks = {}, {}
        self.initObjectsAndCompanions(objCol.creators, objCol, deps, depLinks)

    def initObjectsAndCompanions(self, creators, objColl, dependents, depLinks):
        InspectableObjectView.initObjectsAndCompanions(self, creators, objColl, dependents, depLinks)
        self.initIdOnlyObjEvts(objColl.events, creators)

    def refreshCtrl(self):
        self.DeleteAllItems()

        if self.model.objectCollections.has_key(self.collectionMethod):
            objCol = self.model.objectCollections[self.collectionMethod]
            objCol.indexOnCtrlName()
        else:
            objCol = ObjCollection.ObjectCollection()

        creators = {}
        for ctrl in objCol.creators:
            if ctrl.comp_name:
                creators[ctrl.comp_name] = ctrl

        for name in self.objectOrder:
            idx = -1
            ctrl = creators[name]
            className = ctrl.class_name
            try:
                ClassObj = PaletteMapping.evalCtrl(className)
            except NameError:
                if className in self.model.customClasses:
                    ClassObj = self.model.customClasses[className]
                else:
                    idx = self.il.Add(PaletteStore.bitmapForComponent(className,
                          'Component'))
            else:
                className = ClassObj.__name__

            if idx == -1:
                idx = self.il.Add(PaletteStore.bitmapForComponent(ClassObj))

            self.InsertImageStringItem(self.GetItemCount(), '%s : %s' % (
                  ctrl.comp_name, className), idx)
        self.opened = True

    def saveCtrls(self, definedCtrls, module=None, collDeps=None):
        InspectableObjectView.saveCtrls(self, definedCtrls, module, collDeps)

        compns = []
        for objInf in self.objects.values():
            compns.append(objInf[0])
        self.model.removeWindowIds(self.collectionMethod)
        self.model.writeWindowIds(self.collectionMethod, compns)

    def loadControl(self, CtrlClass, CtrlCompanion, ctrlName, params):
        """ Create and register given control and companion.
            See also: newControl """
        args = self.setupArgs(ctrlName, params,
          CtrlCompanion.handledConstrParams, evalDct = self.model.specialAttrs)

        # Create control and companion
        companion = CtrlCompanion(ctrlName, self, CtrlClass)
        self.objects[ctrlName] = [companion, companion.designTimeObject(args), None]
        self.objectOrder.append(ctrlName)

        return ctrlName

    def restore(self):
        # This is needed for when the inspector switches to it's designer
        self.model.editor.restore()
        # XXX Should probably switch to the DataView page in the notebook.

    def selectNone(self):
        for itemIdx in range(self.GetItemCount()):
            a = wx.LIST_STATE_SELECTED
            state = self.GetItemState(itemIdx, a)
            self.SetItemState(itemIdx, 0, a)

    def selectCtrls(self, ctrls):
        for itemIdx in range(self.GetItemCount()):
            name = self.GetItemText(itemIdx).split(' : ')[0]
            a = wx.LIST_STATE_SELECTED
            if name in ctrls: f = a
            else: f = 0
            state = self.GetItemState(itemIdx, a)
            self.SetItemState(itemIdx, f, a)

    def deleteCtrl(self, name, parentRef = None):
        self.selectNone()

        # notify other components of deletion
        if self.objects.has_key(name):
            self.controllerView.notifyAction(self.objects[name][0], 'delete')

            InspectableObjectView.deleteCtrl(self, name, parentRef)
            self.refreshCtrl()

    def renameCtrl(self, oldName, newName):
        self.controllerView.renameCtrlAndParentRefs(oldName, newName)

        InspectableObjectView.renameCtrl(self, oldName, newName)
        self.refreshCtrl()
        self.selectCtrls( (newName,) )

    def destroy(self):
        InspectableObjectView.destroy(self)
        self.il = None

    def close(self):
        self.cleanup()
        InspectableObjectView.close(self)

    def getSelectedName(self):
        return self.GetItemText(self.selection[0]).split(' : ')[0]

    def getSelectedNames(self):
        selected = []
        for itemIdx in range(self.GetItemCount()):
            name = self.GetItemText(itemIdx).split(' : ')[0]
            state = self.GetItemState(itemIdx, wx.LIST_STATE_SELECTED)
            if state:
                selected.append( (name, itemIdx) )
        return selected

    def OnSelectOrAdd(self, event=None):
        """ Control is clicked. Either select it or add control from palette """
        if self.compPal.selection:
            CtrlClass, CtrlCompanion = self.compPal.selection[1:3]
            # XXX this must be generic
            if CtrlCompanion.host == 'Data' and self.viewName == 'Sizers' or \
               CtrlCompanion.host == 'Sizers' and self.viewName == 'Data':
                view = self.model.views[CtrlCompanion.host]
                view.focus()
                view.OnSelectOrAdd()
                return

            try:
                objName = self.newObject(CtrlClass, CtrlCompanion)
            except DesignerError, err:
                if str(err) == _('Wrong Designer'):
                    return
                raise
            self.compPal.selectNone()
            self.refreshCtrl()
            self.selectCtrls([objName])
            
            return objName
        else:
            # Skip so that OnObjectSelect may be fired
            if event:
                event.Skip()
            

    def updateSelection(self):
        if len(self.selection) == 1:
            self.inspector.selectObject(self.objects[self.selection[0][0]][0],
                  False, sessionHandler=self.controllerView)
        else:
            self.inspector.cleanup()

    def OnObjectSelect(self, event):
        self.inspector.containment.cleanup()
        self.selection = self.getSelectedNames()
        self.updateSelection()

    def OnObjectDeselect(self, event):
        event.Skip()
        if self.vetoSelect: return
        idx = 0
        while idx < len(self.selection):
            name, ctrlIdx = self.selection[idx]
            if ctrlIdx == event.m_itemIndex:
                del self.selection[idx]
            else:
                idx = idx + 1

        self.updateSelection()

    def OnPost(self, event):
        """ Close all designers and save all changes """
        self.controllerView.saveOnClose = True
        self.close()

    def OnCancel(self, event):
        """ Close all designers and discard all changes """
        self.controllerView.saveOnClose = False
        self.controllerView.confirmCancel = True
        self.close()

    def OnCutSelected(self, event):
        """ Cut current selection to the clipboard """
        ctrls = [ni[0] for ni in self.selection]

        output = []
        self.cutCtrls(ctrls, [], output)

        Utils.writeTextToClipboard(os.linesep.join(output))

        self.refreshCtrl()

    def OnCopySelected(self, event):
        """ Copy current selection to the clipboard """
        ctrls = [ni[0] for ni in self.selection]

        output = []
        self.copyCtrls(ctrls, [], output)

        Utils.writeTextToClipboard(os.linesep.join(output))

    def OnPasteSelected(self, event):
        """ Paste current clipboard contents into the current selection """
        pasted = self.pasteCtrls('', Utils.readTextFromClipboard().split(os.linesep))
        if len(pasted):
            self.refreshCtrl()
            self.selectCtrls(pasted)

    def OnControlDelete(self, event):
        self.vetoSelect = True
        try:
            for name, idx in self.selection:
                self.deleteCtrl(name)
        finally:
            self.vetoSelect = False

        self.selection = self.getSelectedNames()
        self.updateSelection()

    def OnDefaultEditor(self, event):
        if len(self.selection) == 1:
            self.objects[self.selection[0][0]][0].defaultAction()

    def OnContextHelp(self, event):
        Help.showCtrlHelp(self.objects[self.selection[0][0]][0].GetClass())

    def OnRecreateSelected(self, event):
        wx.LogError(_('Recreating not supported in the %s view')%self.viewName)

    def OnCreationOrder(self, event):
        names = [name for name, idx in self.getSelectedNames()]
        self.showCreationOrderDlg(None)
        self.refreshCtrl()
        self.selectCtrls(names)
