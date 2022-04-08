#----------------------------------------------------------------------
# Name:        SizersView.py
# Purpose:     Designer for sizer objects
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
print 'importing Views.SizersView'

import os, copy

import wx

import Preferences, Utils
from Utils import _

import sourceconst
import PaletteMapping, PaletteStore, Help

from InspectableViews import DesignerError
from DataView import DataView
import ObjCollection

class SizersView(DataView):
    viewName = 'Sizers'
    viewTitle = _('Sizers')
    
    collectionMethod = sourceconst.init_sizers
    def __init__(self, parent, inspector, model, compPal, designer):
        DataView.__init__(self, parent, inspector, model, compPal)
        designer.initSizers(self)

        self.sizerConnectList = []

##    def layoutSizers(self):
##        objs = self.objectOrder[:]
##        objs.reverse()
##        for name in objs:
##            self.objects[name][1].Layout()

    def recreateSizers(self):
        # disconnect controls from sizers
        for prop in self.sizerConnectList:
            ctrl = self.controllerView.objects[prop.comp_name][1]
            ctrl.SetSizer(None)

        # build and delete list of sizers that are not owned by other sizers
        delLst = []
        for itemInfo in self.objects.values():
            sizer = itemInfo[1]
            if not hasattr(sizer, '_sub_sizer'):
                delLst.append(sizer)
        for sizer in delLst:
            if sizer:
                sizer.Destroy()

        # remove references
        for objInfo in self.controllerView.objects.values():
            ctrl = objInfo[1]
            if hasattr(ctrl, '_in_sizer'):
                del ctrl._in_sizer
            if hasattr(ctrl, '_has_sizer'):
                del ctrl._has_sizer

        # recreate
        for sizerName in self.objectOrder:
            self.objects[sizerName][0].recreateSizer()

        for sizerName in self.objectOrder:
            self.objects[sizerName][0].recreateSizerItems()

        for prop in self.sizerConnectList:
            compn, ctrl = self.controllerView.objects[prop.comp_name][:2]
            sizer = self.objects[Utils.ctrlNameFromSrcRef(prop.params[0])][1]
            compn.SetSizer(sizer)

    def saveCtrls(self, definedCtrls, module=None):
        collDeps = []
        self.writeSizerConnectProps(collDeps)
        DataView.saveCtrls(self, definedCtrls, module, collDeps=collDeps)

    def checkSizerConnectRename(self, oldName, newName):
        srOldName = Utils.srcRefFromCtrlName(oldName)
        srNewName = Utils.srcRefFromCtrlName(newName)
        for prop in self.sizerConnectList:
            if prop.params[0] == srOldName:
                prop.params[0] = srNewName

    def checkCollectionRename(self, oldName, newName, companion=None):
        for objInfo in self.objects.values():
            cmp = objInfo[0]
            if cmp != companion and cmp.collections.has_key('Items'):
                collEditView = cmp.collections['Items']
                objColl = self.model.objectCollections[
                      collEditView.collectionMethod]
                objColl.renameCtrl(oldName, newName)

    def designerRenameNotify(self, oldName, newName):
        for prop in self.sizerConnectList:
            if prop.comp_name == oldName:
                prop.comp_name = newName

        self.checkCollectionRename(oldName, newName)


    def writeSizerConnectProps(self, output, stripFrmId=''):
        from Companions import BaseCompanions
        writerDTC = BaseCompanions.DesignTimeCompanion('SizerWriter', self)
        for prop in self.sizerConnectList:
            writerDTC.addContinuedLine(sourceconst.bodyIndent+prop.asText(stripFrmId),
                  output, sourceconst.bodyIndent)

    def initObjectsAndCompanions(self, creators, objColl, dependents, depLinks):
        DataView.initObjectsAndCompanions(self, creators, objColl, dependents, depLinks)

        for ctrlName in objColl.propertiesByName.keys():
            for prop in objColl.propertiesByName[ctrlName]:
                if prop.prop_setter == 'SetSizer':
                    compn, ctrl = self.controllerView.objects[ctrlName][:2]
                    sizer = self.objects[Utils.ctrlNameFromSrcRef(prop.params[0])][1]
                    compn.SetSizer(sizer)
                    self.sizerConnectList.append(prop)


    def deleteCtrl(self, name, parentRef = None):
        DataView.deleteCtrl(self, name, parentRef)

        srName = Utils.srcRefFromCtrlName(name)
        for prop in self.sizerConnectList[:]:
            if prop.params[0] == srName:
                compn, ctrl = self.controllerView.objects[prop.comp_name][:2]
                ctrl.SetSizer(None)
                ctrl.Refresh()
                self.sizerConnectList.remove(prop)

        wx.CallAfter(self.recreateSizers)
        wx.CallAfter(self.controllerView.OnRelayoutDesigner, None)#Refresh()

