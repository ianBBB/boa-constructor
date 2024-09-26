#----------------------------------------------------------------------
# Name:        PropertyEditors.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
"""
    Property editors provide a design time interface for the inspector to
    examine and manipulate properties of controls.

    Some properties are live and also update the design time control,
    others only update the source and changes may only be seen when the
    frame is reloaded or the control is recreated.
"""

print('importing PropertyEditors')

# XXX Value getting setting of value between internal and sometime control value
# XXX Is still too fuzzy

from types import *
import os, string

import wx
from wx import adv

from .InspectorEditorControls import *

import methodparse

import Utils
from Utils import _

from . import Enumerations

# ########################
# str type is in UFT-8, so no need for this
# #######################
# StringTypes = [StringType]
# try: StringTypes.append(UnicodeType)
# except: pass

class EditorStyles:pass
class esExpandable(EditorStyles):pass
class esDialog(EditorStyles):pass
class esReadOnly(EditorStyles):pass
class esRecreateProp(EditorStyles):pass

class PropertyRegistry:
    """ Factory to return propery editors from recognisable types
        It does not return property editors for certain design-time types like
        sets, enumerations, booleans, etc.
    """

    def __init__(self):
        self.classRegistry = {}
        self.typeRegistry = {}#{type(None): None}

    def registerClasses(self, propClass, propEditors):
        for propEdit in propEditors:
            self.classRegistry[propClass.__name__] = propEdit

    def registerTypes(self, propType, propEditors):
        for propEdit in propEditors:
            self.typeRegistry[propType] = propEdit

    def factory(self, name, parent, companion, rootCompanion, propWrapper, idx, width):
        try:
            propWrapper.connect(companion.control, companion)
            value = propWrapper.getValue()
        except Exception as message:
            print(_('Error on accessing Getter for %s: %s')%(name, message))
            value = None

        #2.4
        # if isinstance(value, InstanceType):
        if isinstance(value,type):
            if value.__class__.__name__ in self.classRegistry:
                return self.classRegistry[value.__class__.__name__](name,
                  parent, companion, rootCompanion, propWrapper, idx, width)
            else:
                pass
##                print 'e:class', value, value.__class__.__name__, 'for', name, 'not supported'
        #2.5
        if type(value) in self.typeRegistry:
            return self.typeRegistry[type(value)](name, parent, companion,
              rootCompanion, propWrapper, idx, width)
        elif isinstance(value, object) and hasattr(value, '__class__') and \
              value.__class__.__name__ in self.classRegistry:
            return self.classRegistry[value.__class__.__name__](name,
                  parent, companion, rootCompanion, propWrapper, idx, width)
        else:
            if isinstance(value, type(None)):
                return None
            elif type(value) in self.typeRegistry:
                return self.typeRegistry[type(value)](name, parent, companion,
                  rootCompanion, propWrapper, idx, width)
            else:
                pass
##                print 'e:type', value, type(value), 'for', name, 'not supported'


# XXX Check IEC initialisation not from Display value but from 'valueFromIEC'
class PropertyEditor:
    """ Class associated with a design time identified type,
        it manages the behaviour of a NameValue in the Inspector
    """

    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, _1=None , _2=None):
        self.name = name
        self.parent = parent

        self.idx = idx
        self.width = width
        self.editorCtrl = None
        self.companion = companion
        self.obj = companion.control
        self.propWrapper = propWrapper
        self.propWrapper.connect(self.obj, self.companion)
        self.rootCompanion = rootCompanion
        self.root = rootCompanion.control
        self.style = []
        self.ownerPropEdit = None
        self.expanded = False
        self.initFromComponent()

    def initFromComponent(self):
        self.value = self.propWrapper.getValue()
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())

    def edit(self):
        pass

    def inspectorEdit(self):
        """ Start a property editing operation and opens the inplace editor """
        pass

    def refreshCompCtrl(self):
        if self.obj and hasattr(self.obj, 'Refresh'):
            self.obj.Refresh()

    def isValuesEqual(self, propVal, ctrlVal):
        if isinstance(propVal, wx.Font) and isinstance(ctrlVal, wx.Font):
            return fontAsExpr(propVal) == fontAsExpr(ctrlVal)
        # elif isinstance(propVal, (str, UnicodeType)) and \
        #      isinstance(ctrlVal, (str, UnicodeType)):
        elif isinstance(propVal, str) and \
             isinstance(ctrlVal, str):
            return propVal == ctrlVal
        else:
            return propVal == ctrlVal

    def validateProp(self, oldVal, newVal):
        pass

    def inspectorPost(self, closeEditor = True):
        """ Post inspector editor control, update ctrl and persist value """
        if self.editorCtrl:
            v = self.getValue()
            cv = self.getCtrlValue()
            # Only post changes
            if not self.isValuesEqual(v, cv):
                self.validateProp(v, cv)
                self.setCtrlValue(cv, v)
                self.refreshCompCtrl()
                self.persistValue(self.valueAsExpr())
                # When sub properties post, update their main properties
                if self.ownerPropEdit:
                    self.companion.updateOwnerFromObj()
                    self.ownerPropEdit.initFromComponent()

                    # XXX Font's want new objects assigned to them before
                    # XXX they update
                    if esRecreateProp in self.ownerPropEdit.getStyle():
                        v = self.companion.eval(self.ownerPropEdit.valueAsExpr())
                        self.ownerPropEdit.setCtrlValue(v, v)

                    self.ownerPropEdit.persistValue(self.ownerPropEdit.valueAsExpr())
                    self.ownerPropEdit.refreshCompCtrl()

                if self.name in self.companion.mutualDepProps:
                    for prop in self.companion.mutualDepProps:
                        if prop != self.name:
                            insp = self.companion.designer.inspector
                            insp.constructorUpdate(prop)
                            insp.propertyUpdate(prop)

            if closeEditor and self.editorCtrl:
                self.editorCtrl.destroyControl()
                self.editorCtrl = None


    def inspectorCancel(self):
        """ Cancel a property editor operation """
        if self.editorCtrl:
            self.editorCtrl.destroyControl()
            self.editorCtrl = None

    def getStyle(self):
        return self.style

    def getValue(self):
        """ Returns and initialises value for prop editor.

        If in edit mode, value should be read from the editor control

        Override if needed.
        """
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        return self.value

    def setValue(self, value):
        """ Initialise the prop editor and if needed the editor control """
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())

    def getCtrlValue(self):
        """ Read current prop value from designed object """
        return self.propWrapper.getValue()

    def setCtrlValue(self, oldValue, value):
        """ Update designed object with current prop """
        # If overridden, rem to call check triggers if not calling parent method
        self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value)

    def persistValue(self, value):
        funcName = self.propWrapper.getSetterName()
        self.companion.persistProp(self.name, funcName, value)

    def getDisplayValue(self):
        """ Value that should display when the prop editor is not in edit mode """
        return repr(self.value)

    def valueAsExpr(self):
        """ Return value as evaluatable source """
        return self.getDisplayValue()

    def getValues(self):
        """ Return list of options """
        return self.values

    def setValues(self, values):
        """ Sets list of options """
        self.values = values

    def valueToIECValue(self):
        """ Return prop value in the form that the editor control expects """
        return self.value

    def setValueFromIECValue(self, value):
        """ Set value from the format that the editor control produces """
        self.value = value

    def setWidth(self, width):
        self.width = width
        if self.editorCtrl:
            self.editorCtrl.setWidth(width)

    def setIdx(self, idx):
        self.idx = idx
        if self.editorCtrl:
            self.editorCtrl.setIdx(idx)

class FactoryPropEdit(PropertyEditor):
    pass

class LockedPropEdit(PropertyEditor):
    def getDisplayValue(self):
        return str(self.value)

#-------------------------------------------------------------------------------

class ConfPropEdit(PropertyEditor):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx,
          width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion,
          propWrapper, idx, width)
        self.setValues(names)

    def getDisplayValue(self):
        return str(self.value)

    def initFromComponent(self):
        self.value = self.getCtrlValue()

    def persistValue(self, value):
        pass

class ContainerConfPropEdit(ConfPropEdit):
    def getStyle(self):
        return [esExpandable]
    def inspectorEdit(self):
        self.editorCtrl = BevelIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)

class StrConfPropEdit(ConfPropEdit):
    def valueToIECValue(self):
        return self.value
#        return eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = self.editorCtrl.getValue()
            except Exception as message:
                self.value = self.getCtrlValue()
                print('invalid constr prop value', message)
        else:
            self.value = self.getCtrlValue()
        return self.value

class PasswdStrConfPropEdit(StrConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width, style=wx.TE_PASSWORD)
    def getDisplayValue(self):
        return '*'*len(self.value)

class EvalConfPropEdit(ConfPropEdit):
    def valueToIECValue(self):
        return repr(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, repr(self.value))
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = eval(self.editorCtrl.getValue(), {})
            except Exception as message:
                self.value = self.getCtrlValue()
                print('invalid constr prop value', message)
        else:
            self.value = self.getCtrlValue()
        return self.value

class EnumConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)
##
##    def getValues(self):
##        return self.names

class ColourConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        data = wx.ColourData()
        data.SetColour(self.companion.eval(self.value))
        data.SetChooseFull(True)
        dlg = wx.ColourDialog(self.parent, data)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                col = dlg.GetColourData().GetColour()
                self.editorCtrl.value = \
                      'wx.Colour(%d, %d, %d)'%(col.Red(),col.Green(),col.Blue())
                self.inspectorPost(False)
        finally:
            dlg.Destroy()

class FilepathConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        from FileDlg import wxFileDialog
        dlg = wxFileDialog(self.parent, _('Choose the file'), '.', '', 'AllFiles', wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.editorCtrl.setValue(repr(dlg.GetFilePath()))
                self.inspectorPost(False)
            else:
                if wx.MessageBox(_('Clear the current property value?'),
                      _('Clear filepath?'), style=wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                    self.editorCtrl.setValue("''")
                    self.inspectorPost(False)
        finally:
            dlg.Destroy()

class DirpathConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dlg = wx.DirDialog(self.parent)#, defaultPath=self.editorCtrl.value)
        try:
            dlg.SetPath(self.companion.eval(self.editorCtrl.value))
            if dlg.ShowModal() == wx.ID_OK:
                self.editorCtrl.setValue(repr(dlg.GetPath()))
                self.inspectorPost(False)
            else:
                if wx.MessageBox(_('Clear the current property value?'),
                      _('Clear dirpath?'), style=wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                    self.editorCtrl.setValue("''")
                    self.inspectorPost(False)
        finally:
            dlg.Destroy()

class BoolConfPropEdit(ConfPropEdit):
    truths = ['on', 'true', '1']
    def getDisplayValue(self):
        return self.valueToIECValue()

    def valueToIECValue(self):
        return self.value.lower() in self.truths and 'True' or 'False'

    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value in self.truths)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

#-------------------------------------------------------------------------------

class OptionedPropEdit(PropertyEditor):
    """ Property editors initialised with options """
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)
        self.options = options
        self.names = names
        if names:
            self.revNames = Enumerations.reverseDict(names)
        else:
            self.revNames = None

class ConstrPropEditFacade:
    def initFromComponent(self):
        self.value = ''
    def getCtrlValue(self):
        return ''
    def getValue(self):
        return ''
    def setValue(self, value):
        self.value = value

class ConstrPropEdit(ConstrPropEditFacade, PropertyEditor):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx,
      width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion,
          propWrapper, idx, width)
    def initFromComponent(self):
        self.value = self.getValue()
    def valueToIECValue(self):
        return self.value
    def getDisplayValue(self):
        return self.getValue()
    def getCtrlValue(self):
        # PRUNE
        # For a menu item, the menu text in the constructor call is referred to as "item" whereas in the
        # properties it is simply called "text". When collecting values for the Inspector, the values
        # are based on the constructor values but for menu items, the returned value has to take into account
        # this difference in parameter name.  test KIND and NAME


        paramName = self.companion.constructor()[self.name]
        return self.companion.textConstr.params[paramName]
    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)
        if hasattr(self.companion, 'index'):
            self.propWrapper.setValue(self.companion.eval(value), self.companion.index)
        else:
            self.propWrapper.setValue(value)

class ReadOnlyConstrPropEdit(ConstrPropEdit):
    def getValue(self):
        self.value = self.getCtrlValue()
        return self.value
    def inspectorEdit(self):
        val = self.getValue()
        self.editorCtrl = BeveledLabelIEC(self, val)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
##    def getDisplayValue(self):
##        return 'RO:`self.getValue()`

class ColourConstrPropEdit(ConstrPropEdit):
    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        data = wx.ColourData()
        data.SetColour(self.companion.eval(self.value))
        data.SetChooseFull(True)
        dlg = wx.ColourDialog(self.parent, data)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                col = dlg.GetColourData().GetColour()
                self.value = 'wx.Colour(%d, %d, %d)'%(col.Red(),col.Green(),col.Blue())
                self.editorCtrl.setValue(self.value)
                self.inspectorPost(False)
        finally:
            dlg.Destroy()


# Collection id name
class ItemIdConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        val = self.valueToIECValue()
        self.editorCtrl = TextCtrlIEC(self, val)
        self.editorCtrl.createControl(self.parent, val, self.idx, self.width)

    def valueToIECValue(self):
        return self.getDisplayValue()

    def getDisplayValue(self):
        base = self.companion.newWinId('')
        return self.getValue()[len(base):]

    def fixupName(self, name):
        newname = []
        for c in name:
            if c == ' ': c = '_'
            if c in string.digits + string.ascii_letters + '_':
                newname.append(c)

        return ''.join(newname).upper()

    def getValue(self):
        if self.editorCtrl and self.editorCtrl.getValue():
            base = self.companion.newWinId('')
            self.value = base + self.fixupName(self.editorCtrl.getValue())
        else:
            self.value = self.getCtrlValue()
        return self.value

    def valueAsExpr(self):
        return self.getValue()

    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value, self.companion.index)

class ButtonIdConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

    def getValues(self):
        return [Utils.windowIdentifier(self.companion.designer.GetName(), 
                self.companion.name)] + Enumerations.wxStockIds

    def getValue(self):
        if self.editorCtrl and self.editorCtrl.getValue():
            self.value = self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value


class IntConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = SpinCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
#             and self.editorCtrl.getValue():
            self.value = str(self.editorCtrl.getValue())
        else:
            self.value = self.getCtrlValue()
        return self.value

class SBFWidthConstrPropEdit(IntConstrPropEdit):
    def getCtrlValue(self):
        return self.companion.GetWidth()

    def setCtrlValue(self, oldValue, value):
        self.companion.SetWidth(value)

    def persistValue(self, value):
        pass

class ClassLinkConstrPropEdit(IntConstrPropEdit): pass

def patchExplorerFileTypes(add=True):
    from Explorers import FileExplorer
    if add:
        FileExplorer.filterDescrOrd.append('ArtProvider')
        FileExplorer.filterDescr['ArtProvider'] = ('ArtProvider', -1)
    else:
        FileExplorer.filterDescrOrd.remove('ArtProvider')
        del FileExplorer.filterDescr['ArtProvider']
        
class BitmapPropEditMix:
    extTypeMap = {'.bmp': 'wx.BITMAP_TYPE_BMP',
                  '.gif': 'wx.BITMAP_TYPE_GIF',
                  '.jpg': 'wx.BITMAP_TYPE_JPEG',
                  '.png': 'wx.BITMAP_TYPE_PNG',
                  '.py':  'ResourceModule'}

    srcClass = 'wx.Bitmap'
    ctrlClass = wx.Bitmap
    nullClass = 'wx.NullBitmap'
    artProvClass = 'wx.ArtProvider'

    onlyIcons = False

    def showImgDlg(self, dir, name, tpe='Bitmap'):
        model = self.companion.designer.model
        selImg = ''
        apClientId = ''
        apSize = ''
        
        if tpe == 'Bitmap' and not os.path.isdir(dir):
            wx.MessageBox(_('The given directory is invalid, using current '
                         'directory.\n(%s)')%dir, _('Warning'),
                         wx.OK | wx.ICON_EXCLAMATION)
            dir = '.'
        elif tpe == 'ResourceModule':
            selImg = name
        elif tpe == 'ArtProvider':
            selImg = name
            apClientId = dir[0]
            apSize = dir[-1]
            dir = '.'

        from FileDlg import wxFileDialog

        filter = ''
        keepShowing = True
        while keepShowing:
            keepShowing = False
            if tpe == 'ResourceModule':
                mod = model.resources[dir]
                ext = '.py'
                pth = abspth = os.path.splitext(mod.__file__)[0]+ext
            elif tpe == 'ArtProvider':
                filter = 'ArtProvider'
            else:
                patchExplorerFileTypes(True)
                dlg = wxFileDialog(self.parent, _('Choose an image'), dir, name,
                      'ImageFiles', wx.FD_OPEN)
                try:
                    if dlg.ShowModal() != wx.ID_OK:
                        return '', '', ''
                    pth = abspth = dlg.GetFilePath().replace('\\', '/')
                    filter = dlg.chTypes.GetStringSelection()
                finally:
                    dlg.Destroy()
                    patchExplorerFileTypes(False)

                if filter != 'ArtProvider' and not Preferences.cgAbsoluteImagePaths:
                    pth = Utils.pathRelativeToModel(pth, model)

                ext = os.path.splitext(pth)[-1].lower()

            if filter == 'ArtProvider':
                from . import ArtProviderBrowser
                dlg = ArtProviderBrowser.ArtProviderBrowser(self.parent, name, apClientId, apSize)
                try:
                    result = dlg.ShowModal()
                    if result == wx.ID_OK:
                        return ( (dlg.clientId.GetStringSelection(), 
                                 dlg.imgSize.GetValue()), dlg.artId.GetValue(), 
                                 'ArtProvider')
                    elif result == wx.ID_YES:
                        keepShowing = True
                        tpe = 'Bitmap'
                        continue
                    else:
                        return '', '', ''

                finally:
                    dlg.Destroy()
                
            elif ext == '.py':
                if os.path.isabs(pth):
                    pth = Utils.pathRelativeToModel(pth, model)

                resInfo = self.handleResourceFiles(abspth, pth, selImg)
                if resInfo:
                    if resInfo == -1:
                        return '', '', ''
                    if resInfo == 'FileDlg':
                        dir, name = os.path.split(abspth)
                        keepShowing = True
                        tpe = 'Bitmap'
                        continue
                    return resInfo[0], resInfo[1], 'ResourceModule'
            try:
                ext = self.extTypeMap[ext]
            except KeyError as err:
                raise Exception(_('Files of type %s not allowed for this '
                                'property editor.\n The following types '
                                'are allowed %s')%(str(err),
                                ', '.join(list(self.extTypeMap.keys()))))
            else:
                return abspth, pth, ext

    def extractPathFromSrc(self, src):
        if src:
            if src.startswith(self.nullClass):
                return os.path.join('.', self.nullClass, 'Bitmap'), '.', 'wx.NullBitmap', 'Bitmap'
            elif src.startswith('wx.Bitmap(') or src.startswith('wx.Icon('):
                if src.startswith('wx.Bitmap('):
                    filename = src[len('wx.Bitmap(')+1:]
                else:
                    filename = src[len('wx.Icon(')+1:]

                pth = filename[:filename.rfind(',')-1]
                if not os.path.isabs(pth):
                    mbd = Utils.getModelBaseDir(self.companion.designer.model)
                    if mbd: mbd = mbd[7:]
                    pth = os.path.normpath(os.path.join(mbd, pth)).replace('\\',
                          '/')
                dir, name = os.path.split(pth)
                if not dir: dir = '.'
                return os.path.join(pth, 'Bitmap'), dir, name, 'Bitmap'
            elif src.startswith('wx.ArtProvider.'):
                bs = src.find('(')
                be = src.rfind(')')
                params = methodparse.safesplitfields(src[bs+1:be], ',')
                #params = src[bs+1:be].split(',')
                artId, clientId, size = params
                return src+'/ArtProvider', (clientId, size), artId, 'ArtProvider'
            else:
                import moduleparse
                m = moduleparse.is_resource_bitmap.search(src)
                if m:
                    importName, imageName = m.group('imppath'), m.group('imgname')
                    src = os.path.join(importName, imageName, 'ResourceModule')
                    return (src, importName, imageName, 'ResourceModule')

        return './Unknown/Unknown', '.', '', 'Unknown'

    def handleResourceFiles(self, resourceFilename, relResourceFilename, image=''):
        from Models import Controllers

        Model, main = Controllers.identifyFile(resourceFilename)
        for ResourceClass in Controllers.resourceClasses:
            if issubclass(Model, ResourceClass):
                break
        else:
            return # not a resource module

        idx, imageName = self.showResourceDlg(resourceFilename, image)
        if idx is None: return 'FileDlg'
        if idx == -1:   return -1

        importName = os.path.splitext(relResourceFilename)[0].replace('\\',
              '/').replace('/', '.')
        if os.path.isabs(relResourceFilename):
            importName = os.path.splitdrive(importName)[1][1:]
            impNameDlg = wx.TextEntryDialog(self.parent, _('Correct the module '
                  'name that must be imported'), _('Resource module'), importName)
            try:
                if impNameDlg.ShowModal() != wx.ID_OK:
                    return
                importName = impNameDlg.GetValue()
                # XXX test with imp?
            finally:
                impNameDlg.Destroy()
        else:
            if relResourceFilename.startswith('../'):
                while importName.startswith('../'):
                    importName = importName[3:]
            importName = importName.replace('/', '.')

        return importName, imageName

    def getSrcForResPath(self, importName, imageName):
        if self.onlyIcons: cls = 'Icon'
        else:              cls = 'Bitmap'
        return '%s.get%s%s()'%(importName, imageName, cls)

    def showResourceDlg(self, filename, image=''):
        from Models import ResourceSupport
        resDlg = ResourceSupport.ResourceSelectDlg(self.parent,
          self.companion.designer.model.editor, filename, image, self.onlyIcons)
        try:
            result = resDlg.ShowModal()
            if result == wx.ID_CANCEL:
                return -1, ''
            if result == wx.ID_YES:
                return None, None
            if result == wx.ID_OK:
                idx = resDlg.resources.selected
                return idx, resDlg.resources.imageSrcInfo[idx][0]
            return -1, ''
        finally:
            resDlg.Destroy()

    def assureArtProviderImageLoaded(self, infoSrc, artIdSrc):
        clientIdSrc, sizeSrc = infoSrc
        clientId = self.companion.eval(clientIdSrc)
        size = self.companion.eval(sizeSrc)
        artId = self.companion.eval(artIdSrc)
        
        src = 'wx.ArtProvider.GetBitmap(%s, %s, %s)'%(artIdSrc, clientIdSrc, sizeSrc)

        return src, wx.ArtProvider.GetBitmap(artId, clientId, size), src+'/ArtProvider'

    def assureResourceLoaded(self, importName, imageName):
        model = self.companion.designer.model
        if model.assureResourceLoaded(importName, model.resources,
              specialAttrs=model.specialAttrs):
            src = self.getSrcForResPath(importName, imageName)
            value = self.companion.eval(src)
            bmpPath = os.path.join(importName, imageName, 'ResourceModule')
            self.companion.registerResourceModule(importName)

            return src, value, bmpPath
        else:
            raise Exception(_('%s could not be loaded as a Resource Module')%importName)


class BitmapConstrPropEdit(IntConstrPropEdit, BitmapPropEditMix):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        model = self.companion.designer.model
        src, dir, name, tpe = self.extractPathFromSrc(self.value)
        abspth, pth, tpe = self.showImgDlg(dir, name, tpe)
        if not tpe:
            return
        elif tpe == 'ResourceModule':
            self.value, ctrlVal, bmpPath = self.assureResourceLoaded(abspth, pth)
        elif tpe == 'ArtProvider':
            self.value, ctrlVal, bmpPath = self.assureArtProviderImageLoaded(abspth, pth)
        elif abspth:
            self.value = 'wx.Bitmap(%s, %s)'%(repr(pth), tpe)
            ctrlVal = wx.Bitmap(abspth, self.companion.eval(tpe))

        self.persistValue(self.value)
        self.propWrapper.setValue(ctrlVal, self.companion.index)
        self.refreshCompCtrl()

    def getValue(self):
        if self.editorCtrl:
            return self.value
        else:
            return self.getCtrlValue()

class BitmapPropEdit(PropertyEditor, BitmapPropEditMix):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options = None, names = None):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

##    def getStyle(self):
##        return ClassPropEdit.getStyle(self) + [esDialog, esReadOnly]

    def getDisplayValue(self):
        return '(%s)'%self.srcClass

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)
        constrs = self.companion.constructor()
        if self.name in constrs:
            constr = self.companion.textConstr.params[constrs[self.name]]
        else:
            constr = self.companion.persistedPropVal(self.name,
                  self.propWrapper.getSetterName())
            if constr is not None:
                constr = constr[0]

        self.bmpPath = self.extractPathFromSrc(constr)[0]

    def edit(self, event):
        if self.bmpPath:
            path, tpe = os.path.split(self.bmpPath)
            if tpe == 'ArtProvider':
                src, dir, name, tpe = self.extractPathFromSrc(path)
            else:
                dir, name = os.path.split(path)
        else:
            dir, name, tpe = '.', '', 'Bitmap'

        abspth, pth, tpe = self.showImgDlg(dir, name, tpe)
        if not tpe or not abspth:
            return
        if tpe == 'ResourceModule':
            src, self.value, self.bmpPath = self.assureResourceLoaded(abspth, pth)
        elif tpe == 'ArtProvider':
            src, self.value, self.bmpPath = self.assureArtProviderImageLoaded(abspth, pth)
        else:
            self.value = self.ctrlClass(abspth, self.companion.eval(tpe))
            self.bmpPath = os.path.join(pth, 'Bitmap')
        self.inspectorPost(False)

    def getValue(self):
        return self.value

    def valueAsExpr(self):
        if self.bmpPath:
            path, tpe = os.path.split(self.bmpPath)
            dir, name = os.path.split(path)
            if tpe == 'Bitmap':
                # XXX path and name both?
                if path == self.nullClass:
                    return self.nullClass
                elif name == self.nullClass:
                    return self.nullClass
                else:
                    return '%s(%s, %s)'%(self.srcClass, repr(path),
                           self.extTypeMap[os.path.splitext(path)[-1].lower()])
            elif tpe == 'ResourceModule':
                return self.getSrcForResPath(dir, name)
            elif tpe == 'ArtProvider':
                return path
            elif tpe == 'Unknown':
                return self.nullClass
            else:
                raise Exception(_('Unhandled image handling type: %s')%tpe)
        else:
            return self.nullClass

class IconPropEdit(BitmapPropEdit):
    srcClass = 'wx.Icon'
    ctrlClass = wx.Icon
    nullClass = 'wx.NullIcon'
    onlyIcons = True

    extTypeMap = {'.ico': 'wx.BITMAP_TYPE_ICO',
                  '.py':  'ResourceModule'}


class EnumConstrPropEdit(IntConstrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names):
        IntConstrPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names)
        self.names = names
    def valueToIECValue(self):
        return self.getValue()
    def inspectorEdit(self):
        value = self.getValue()
        self.editorCtrl = ChoiceIEC(self, value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(value)

    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        return self.names

class ClassConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        val = self.getValue()
        if val in self.companion.designer.model.customClasses:
            self.editorCtrl = ChoiceIEC(self, val)
            self.editorCtrl.createControl(self.parent, self.idx, self.width)
            self.editorCtrl.setValue(val)
        else:
            self.editorCtrl = BeveledLabelIEC(self, val)
            self.editorCtrl.createControl(self.parent, self.idx, self.width)

    def setCtrlValue(self, oldValue, value):
        #self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value)
    def getCtrlValue(self):
        return self.propWrapper.getValue()

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def getValues(self):
        custClss = self.companion.designer.model.customClasses
        MyCls = custClss[self.value]
        vals = []
        for name, Cls in list(custClss.items()):
            if MyCls == Cls:
                vals.append(name)
        vals.remove(Utils.getWxPyNameForClass(MyCls))
        vals.insert(0, Utils.getWxPyNameForClass(MyCls))
        return vals

##    def getDisplayValue(self):
##        dv = EnumConstrPropEdit.getDisplayValue(self)
##        print dv
##        return dv

class BoolConstrPropEdit(EnumConstrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx,
                 width, options, names):
        EnumConstrPropEdit.__init__(self, name, parent, companion, rootCompanion,
                 propWrapper, idx, width, options, ['True', 'False'])

    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

class LCCEdgeConstrPropEdit(EnumConstrPropEdit):
    def getCtrlValue(self):
        return self.companion.GetEdge()

    def getValue(self):
        if self.editorCtrl:
            try:
                if self.editorCtrl.getValue():
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception as message:
                self.value = self.getCtrlValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def setCtrlValue(self, oldValue, value):
        self.companion.SetEdge(value)

    def persistValue(self, value):
        pass

    def getValues(self):
        objName = self.companion.__class__.sourceObjName
        return [self.getCtrlValue()] + \
          ['%s.%s'%(objName, ai) for ai in self.companion.availableItems()]

class ObjEnumConstrPropEdit(EnumConstrPropEdit):
    def getValue(self):
        if self.editorCtrl:
            try:
                if self.editorCtrl.getValue():
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception as message:
                self.value = self.getCtrlValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def persistValue(self, value):
        pass

    def getObjects(self):
        return list(self.companion.designer.getAllObjects().keys())

    def getValues(self):
        vals = self.getObjects()
        try:
            val = self.getValue()
            if val == 'self': vals.remove('self')
            else: vals.remove('self.'+val)
        except: pass
        return vals

class WinEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def getObjects(self):
        return ['None'] + list(self.companion.designer.getObjectsOfClassWithParent(
                                wx.Window, self.companion.name).keys())
    def getCtrlValue(self):
        return self.companion.GetOtherWin()
    def setCtrlValue(self, oldValue, value):
        self.companion.SetOtherWin(value)

class MenuEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def getValues(self):
        return ['wx.Menu()'] + ObjEnumConstrPropEdit.getValues(self)
    def getObjects(self):
        menus = list(self.companion.designer.getObjectsOfClass(wx.Menu).keys())
        if isinstance(self.companion.control, wx.Menu):
            menus.remove(Utils.srcRefFromCtrlName(self.companion.name))
        return menus
    def setCtrlValue(self, oldValue, value):
        self.companion.SetMenu(value)
    def getCtrlValue(self):
        return self.companion.GetMenu()

##class ControlEnumConstrPropEdit(ObjEnumConstrPropEdit):
####    def getValues(self):
####        return ['wxMenu()'] + ObjEnumConstrPropEdit.getValues(self)
##    def getObjects(self):
##        return self.companion.designer.getObjectsOfClass(wx.Control).keys()
##    def setCtrlValue(self, oldValue, value):
##        self.companion.SetControl(value)
##    def getCtrlValue(self):
##        return self.companion.GetControl()

##class SizerEnumConstrPropEdit(ObjEnumConstrPropEdit):
##    def getValues(self):
##        return ['wx.Menu()'] + ObjEnumConstrPropEdit.getValues(self)
##    def getObjects(self):
##        return self.companion.designer.getObjectsOfClass(wx.BoxSizer).keys()
##    def setCtrlValue(self, oldValue, value):
##        self.companion.SetMenu(value)
##    def getCtrlValue(self):
##        return self.companion.GetMenu()


class BaseFlagsConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getStyle(self):
        return [esExpandable]

    def getValue(self):
        """ For efficiency override the entire getValue"""
        if self.editorCtrl:
            try:
                anInt = self.companion.eval(self.editorCtrl.getValue())
                if isinstance(anInt, int):
                    self.value = ' | '.join(map(str.strip,
                        self.editorCtrl.getValue().split('|')))
                else:
                    self.value = self.getCtrlValue()
            except Exception as message:
                self.value = self.getCtrlValue()
                print('invalid constr prop value', message)
        else:
            self.value = self.getCtrlValue()
        return self.value

class StyleConstrPropEdit(BaseFlagsConstrPropEdit):
    def getSubCompanion(self):
        from Companions.Companions import WindowStyleDTC
        return WindowStyleDTC

class FlagsConstrPropEdit(BaseFlagsConstrPropEdit):
    def getSubCompanion(self):
        from Companions.Companions import FlagsDTC
        return FlagsDTC

class StrConstrPropEdit(ConstrPropEdit):
    def valueToIECValue(self):
        return self.companion.eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx,
          self.width, self.edit)

    def getValue(self):
        if self.editorCtrl:
            try:
                aStr = self.editorCtrl.getValue()
                # if type(aStr) in StringTypes:
                if isinstance(aStr, str):
                    if self.value.startswith('_('):
                        self.value = '_(%r)'%aStr
                    else:
                        self.value = repr(aStr)
                else:
                    self.value = self.getCtrlValue()
            except Exception as message:
                self.value = self.getCtrlValue()
                print('invalid constr prop value', message)
        else:
            self.value = self.getCtrlValue()
        return self.value

    def edit(self, event):
        from . import StringEditDlg
        dlg = StringEditDlg.StringEditDlg(self.parent, self.value, self.companion)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.value = dlg.getStrSrc()
                self.editorCtrl.setValue(dlg.stringTC.GetValue())
                self.inspectorPost(False)
        finally:
            dlg.Destroy()

class SizeConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = self.editorCtrl.getValue()
            except Exception as message:
                self.value = self.getCtrlValue()
                print('invalid constr prop value', message)
        else:
            self.value = self.getCtrlValue()
        return self.value

class NameConstrPropEdit(ConstrPropEdit):
    def valueToIECValue(self):
        return self.companion.eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            value = self.editorCtrl.getValue()
            # if type(value) in StringTypes:
            if isinstance(value, str):
                value = repr(self.editorCtrl.getValue())
            else:
                value = self.getCtrlValue()

            if value != self.value:
                strVal = self.companion.eval(value)
                if not strVal:
                    message = _('Invalid name for a Python object')
                    wx.LogError(message)
                    return self.value

                for c in strVal:
                    if c not in string.ascii_letters+string.digits+'_':
                        message = _('Invalid name for a Python object')
                        wx.LogError(message)
                        return self.value

                if value in self.companion.designer.objects:
                    message = _('Name already used by another control.')
                    wx.LogError(message)
                    return self.value
            self.value = value
        else:
            self.value = self.getCtrlValue()
        return self.value


    def getCtrlValue(self):
        return repr(self.companion.name)

    def setCtrlValue(self, oldValue, newValue):
        self.companion.checkTriggers(self.name,
              self.companion.eval(oldValue),
              self.companion.eval(newValue))

    def persistValue(self, value):
        pass

class ChoicesConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                aList = self.companion.eval(self.editorCtrl.getValue())
                if isinstance(aList, list):
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception as message:
                self.value = self.getCtrlValue()
                print('invalid constr prop value', message)
        else:
            self.value = self.getCtrlValue()
        return self.value

class MajorDimensionConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                anInt = self.companion.eval(self.editorCtrl.getValue())
                if isinstance(anInt, int):
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception as message:
                self.value = self.getCtrlValue()
                print('invalid constr prop value', message)
        else:
            self.value = self.getCtrlValue()
        return self.value

class EventPropEdit(OptionedPropEdit):
    """ Property editor to handle design time definition of events """
    def initFromComponent(self):
        # unlike other propedit getter setters these are methods not funcs
        self.value = self.propWrapper.getValue(self.name)
    def valueToIECValue(self):
        v = self.value
        return v

    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

    def setCtrlValue(self, oldValue, value):
        self.propWrapper.setValue(value, self.name)

    def getDisplayValue(self):
        return self.valueToIECValue()

    extraOpts = [_('(delete)'), _('(rename)')]
    scopeOpts = {_('(show all)'): 'all',
                 _('(show own)'): 'own'}
    def getValues(self):
        """ Build event list based on currently selected scope for the event """
        # XXX Should ideally do this one day:
        # XXX   Show event's of similar types, e.g. mouse events, cmd events.
        # XXX   Also show events from the code not bound to the frame
        vals = []
        showScope = 'own'
        if self.companion:
            for evt in self.companion.textEventList:
                if evt.event_name == self.name:
                    showScope = evt.show_scope

                if evt.trigger_meth not in self.extraOpts:
                    try: vals.index(evt.trigger_meth)
                    except ValueError: vals.append(evt.trigger_meth)

            if showScope != 'own':
                # Add evts from other scopes
                # XXX Collection items' events aren't handled correctly
                # XXX designer != CollEditorView
                for comp, ctrl, prnt in list(self.companion.designer.objects.values()):
                    if comp != self.companion and showScope == 'all':
                        #or  showScope == 'same' and comp.__class__ == self.companion.__class__):
                        for evt in comp.textEventList:
                            if evt.trigger_meth not in self.extraOpts:
                                try: vals.index(evt.trigger_meth)
                                except ValueError: vals.append(evt.trigger_meth)

        scopeChoices = list(self.scopeOpts.keys())
        del scopeChoices[list(self.scopeOpts.values()).index(showScope)]

        vals.extend(self.extraOpts + scopeChoices)
        return vals

    def _repopulateChoice(self, value):
        self.editorCtrl.repopulate()
        self.editorCtrl.setValue(value)

    def getValue(self):
        """ Return current value, or if a special (*) value is selected,
            process it, and return previous 'current value' """
        if self.editorCtrl:
            oldVal = defVal = self.value
            value = self.editorCtrl.getValue()
            # Event rename
            if value == _('(rename)'):
                if oldVal == _('(delete)'):
                    for evt in self.companion.textEventList:
                        if evt.trigger_meth == oldVal:
                            defVal = evt.prev_trigger_meth
                            break

                ted = wx.TextEntryDialog(self.parent, _('Enter a new method name:'),
                      _('Rename event method'), defVal)
                try:
                    if ted.ShowModal() == wx.ID_OK:
                        self.value = ted.GetValue()

                        # XXX All references should be renamed !!!!
                        # XXX Add as method on designer
                        for evt in self.companion.textEventList:
                            if evt.trigger_meth == oldVal:
                                if not evt.prev_trigger_meth:
                                    evt.prev_trigger_meth = oldVal
                                evt.trigger_meth = self.value
                                break
                        self._repopulateChoice(self.value)
                finally:
                    ted.Destroy()
            # Event deletion
            elif value == _('(delete)'):
                for evt in self.companion.textEventList:
                    if evt.trigger_meth == oldVal:
                        if not evt.prev_trigger_meth:
                            evt.prev_trigger_meth = oldVal
                        break
                self.value = self.editorCtrl.getValue()
            # Event scope change
            elif value in list(self.scopeOpts.keys()):
                self.value = oldVal
                for evt in self.companion.textEventList:
                    if evt.event_name == self.name:
                        evt.show_scope = self.scopeOpts[value]
                        self._repopulateChoice(oldVal)
                        break
            # Normal event selection
            else:
                self.value = self.editorCtrl.getValue()

        return self.value

    def persistValue(self, value):
        self.companion.persistEvt(self.name, value)

class BITPropEditor(FactoryPropEdit):
    """ Editors for Built-in Python Types """
    def valueToIECValue(self):
        return repr(self.value)
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                value = self.companion.eval(self.editorCtrl.getValue())
            except Exception as mess:
                wx.LogError(_('Invalid value: %s') % str(mess))
                raise
            self.value = value
        return self.value

class IntPropEdit(BITPropEditor):
    def inspectorEdit(self):
        self.editorCtrl = SpinCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        return self.value

class StrPropEdit(BITPropEditor):
    def valueToIECValue(self):
        return self.companion.eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlButtonIEC(self, self.valueToIECValue())
        self.editorCtrl.createControl(self.parent, self.idx,
          self.width, self.edit)

    def getValue(self):
        if self.editorCtrl:
            aStr = self.editorCtrl.getValue()
            if self.value.startswith('_('):
                self.value = '_(%r)'%aStr
            else:
                self.value = repr(aStr)
        else:
            cv = self.getCtrlValue()
            self.value = repr(cv)
            ps = self.findPropSrc()
            if ps is not None:
                src = ps[0]
                cv = self.getCtrlValue()
                if src.startswith('_('):
                    self.value = '_(%r)'%cv

        return self.value

    def getDisplayValue(self):
        return self.value

    def edit(self, event):
        from . import StringEditDlg
        dlg = StringEditDlg.StringEditDlg(self.parent, self.value, self.companion)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.value = dlg.getStrSrc()
                self.editorCtrl.setValue(dlg.stringTC.GetValue())
                self.inspectorPost(False)
        finally:
            dlg.Destroy()

    def initFromComponent(self):
        v = self.propWrapper.getValue()
        self.value = repr(v)
        ps = self.findPropSrc()
        if ps is not None:
            src = ps[0]
            if src.startswith('_('):
                self.value = '_(%r)'%v
        
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())
    
    def findPropSrc(self):
        constr = self.companion.constructor()
        if self.name in constr:
            paramName = constr[self.name]
            
            return [self.companion.textConstr.params[paramName]]
        else:
            setterName = self.propWrapper.getSetterName()
            for prop in self.companion.textPropList:
                if prop.prop_setter == setterName:
                    return prop.params
        return None

    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)

        self.propWrapper.setValue(self.companion.eval(value))
    

class NamePropEdit(BITPropEditor):
    def valueToIECValue(self):
        return self.value

    identifier = string.ascii_letters+string.digits+'_'
    def getValue(self):
        if self.editorCtrl:
            value = self.editorCtrl.getValue()
            if value != self.value:
                if value in self.companion.designer.objects:
                    wx.LogError(_('Name already used by another control.'))
                    return self.value

                if not value:
                    message = _('Invalid name for a Python object')
                    wx.LogError(message)
                    return self.value

                for c in value:
                    if c not in self.identifier:
                        message = _('Invalid name for a Python object')
                        wx.LogError(message)
                        return self.value
            self.value = value
        return self.value

class TuplePropEdit(BITPropEditor):
    pass

class BoolPropEdit(OptionedPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options=None, names=None):
        OptionedPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names)

    def valueToIECValue(self):
        v = self.value
        if isinstance(v, int):
            return self.getValues()[v]
        else: return repr(v)
    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValues()[self.value])
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        return ['False', 'True']
    def getValue(self):
        if self.editorCtrl:
            # trick to convert boolean string to integer
            v = self.editorCtrl.getValue()
            self.value = self.getValues().index(self.editorCtrl.getValue())
            #self.value = self.companion.eval(self.editorCtrl.getValue())
        return self.value

class EnumPropEdit(OptionedPropEdit):
    def valueToIECValue(self):
        if self.revNames:
            try:
                return self.revNames[self.value]
            except KeyError:
                return repr(self.value)

        else: OptionedPropEdit.getDisplayValue(self)
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.setValue(self.value)
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        vals = list(self.names.keys())
        try:
            name = self.revNames[self.value]
        except KeyError:
            name = repr(self.value)
        if name not in vals:
            vals.append(name)
        # XXX !
        vals.sort()
        return vals
    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            try:
                self.editorCtrl.setValue(self.revNames[value])
            except KeyError:
                self.editorCtrl.setValue(repr(value))
    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            try:
                self.value = self.names[strVal]
            except KeyError:
                self.value = self.companion.eval(strVal)

        return self.value

class StringEnumPropEdit(EnumPropEdit):
    def getDisplayValue(self):
        return repr(self.value)

# Property editors for classes
class ClassPropEdit(FactoryPropEdit):
    def getDisplayValue(self):
        return '(%s)'%Utils.getWxPyNameForClass(self.value.__class__)
    def getStyle(self):
        return [esExpandable]

class ClassLinkPropEdit(OptionedPropEdit):
    defaults = {'None': None}
    linkClass = None
    def getStyle(self):
        return []
    def valueToIECValue(self):
        return self.getNameForValue(self.value, self.linkClass)

    def getNameForValue(self, value, LinkClass):
        for k, v in list(self.defaults.items()):
            if value == v:
                return k
        objs = self.companion.designer.getObjectsOfClass(LinkClass)
        for objName in list(objs.keys()):
            if objs[objName] and value and objs[objName] == value:
                return objName
        return repr(None)

    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.setValue(self.value)
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        defs = list(self.defaults.keys())
        defs.sort()
        return defs + list(self.companion.designer.getObjectsOfClass(self.linkClass).keys())
    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())
    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            if strVal in self.defaults:
                self.value = self.defaults[strVal]
            else:
                objs = self.companion.designer.getObjectsOfClass(self.linkClass)
                self.value = objs[strVal]

        return self.value

class WindowClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.Window

class WindowClassLinkWithParentPropEdit(WindowClassLinkPropEdit):
    def getValues(self):
        return ['None'] + list(self.companion.designer.getObjectsOfClassWithParent(
               self.linkClass, self.companion.name).keys())

class StatusBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.StatusBar

class ToolBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.ToolBar

class MenuBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.MenuBar

class ImageListClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.ImageList

class ButtonClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.Button

class CursorClassLinkPropEdit(ClassLinkPropEdit):
    defaults = {'None': wx.NullCursor, 'wx.STANDARD_CURSOR': wx.STANDARD_CURSOR,
                'wx.HOURGLASS_CURSOR': wx.HOURGLASS_CURSOR,
                'wx.CROSS_CURSOR': wx.CROSS_CURSOR}
    linkClass = wx.Cursor

class ListCtrlImageListClassLinkPropEdit(ImageListClassLinkPropEdit):
    listTypeMap = {wx.IMAGE_LIST_SMALL : 'wx.IMAGE_LIST_SMALL',
                   wx.IMAGE_LIST_NORMAL: 'wx.IMAGE_LIST_NORMAL'}
    def valueToIECValue(self):
        if self.value[0] is None: return repr(None)
        objs = self.companion.designer.getObjectsOfClass(self.linkClass)
        for objName in list(objs.keys()):
            if objs[objName] and self.value[0] and objs[objName] == self.value[0]:
                return objName
        return repr(None)

    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.valueToIECValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.valueToIECValue())

    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            if strVal == repr(None):
                self.value = (None, self.value[1])
            else:
                objs = self.companion.designer.getObjectsOfClass(self.linkClass)
                self.value = (objs[strVal], self.value[1])
        return self.value

    def valueAsExpr(self):
        return '%s, %s'%(self.valueToIECValue(), self.listTypeMap[self.value[1]])

class SplitterWindowLinkPropEdit(WindowClassLinkPropEdit):
    def getValues(self):
        children = list(self.companion.designer.getObjectsOfClassWithParent(
               self.linkClass, self.companion.name).keys())
        otherWin = self.getOtherWindow()
        if otherWin:
            otherWinName = 'self.%s'%otherWin.GetName()
            if otherWinName in children:
                children.remove(otherWinName)

        return ['None'] + children

    def getOtherWindow(self): return None

class SplitterWindow1LinkPropEdit(SplitterWindowLinkPropEdit):
    def getOtherWindow(self):
        return self.companion.GetWindow2(None)

class SplitterWindow2LinkPropEdit(SplitterWindowLinkPropEdit):
    def getOtherWindow(self):
        return self.companion.GetWindow1(None)

def getValidSizers(parent, designer, value):
    # build a list of nested parent sizers
    sizerParents = [parent]
    while hasattr(parent, '_sub_sizer'):
        parent = parent._sub_sizer
        sizerParents.append(parent)

    sizers = designer.getObjectsOfClass(wx.Sizer)
    # remove invalid sizers from the list
    for n, s in list(sizers.items()):
        if s in sizerParents or \
              hasattr(s, '_sub_sizer') or hasattr(s, '_has_control'):
            del sizers[n]

    sizerNames = list(sizers.keys())
    sizerNames.sort()

    res = ['None'] + sizerNames
    if value != 'None':
        res.insert(1, value)
    return res



class SizerEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def getObjects(self):
        return getValidSizers(self.companion.parentCompanion.control,
                              self.companion.designer, self.value)

    def getCtrlValue(self):
        return self.companion.GetSizer()
    def setCtrlValue(self, oldValue, value):
        self.companion.SetSizer(value)

class SizerClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.Sizer
    def getValues(self):
        if self.value is None:
            value = 'None'
        else:
            value = self.getNameForValue(self.value, self.linkClass)

        return getValidSizers(self.companion.control,
                              self.companion.designer, value)


class ColPropEdit(ClassPropEdit):
    def getStyle(self):
        return [esExpandable]

    def getSubCompanion(self):
        from Companions.Companions import ColourDTC
        return ColourDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        data = wx.ColourData()
        data.SetColour(self.value)
        data.SetChooseFull(True)
        dlg = wx.ColourDialog(self.parent, data)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.value = dlg.GetColourData().GetColour()
                self.inspectorPost(False)
                self.editorCtrl.setValue(self.value)
                self.propWrapper.setValue(self.value)
                self.obj.Refresh()
                #self.propWrapper.setValue(self.value)
                #self.obj.Refresh()
        finally:
            dlg.Destroy()

    def getValue(self):
        return self.value#wx.Colour(self.value.Red(), self.value.Green(), self.value.Blue())

    def valueAsExpr(self):
        return 'wx.Colour(%d, %d, %d)'%(self.value.Red(), self.value.Green(), self.value.Blue())

class SizePropEdit(ClassPropEdit):
    def getDisplayValue(self):
        return self.valueToIECValue()
    def valueToIECValue(self):
        return repr(self.value)
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.valueToIECValue())
        self.editorCtrl.createControl(self.parent, self.valueToIECValue(), self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                tuplePos = self.companion.eval(self.editorCtrl.getValue())
            except Exception as mess:
                Utils.ShowErrorMessage(self.parent, _('Invalid value'), mess)
                raise
            self.value = wx.Size(tuplePos[0], tuplePos[1])
        return self.value
    def valueAsExpr(self):
        return 'wx.Size(%d, %d)'%(self.value.x, self.value.y)
    def getSubCompanion(self):
        from Companions.Companions import SizeDTC
        return SizeDTC

class PosPropEdit(ClassPropEdit):
    def getDisplayValue(self):
        return self.valueToIECValue()
    def valueToIECValue(self):
        return repr(self.value)
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                tuplePos = self.companion.eval(self.editorCtrl.getValue())
            except Exception as mess:
                Utils.ShowErrorMessage(self.parent, _('Invalid value'), mess)
                raise
            self.value = wx.Point(tuplePos[0], tuplePos[1])
        return self.value
    def valueAsExpr(self):
        return 'wx.Point(%d, %d)'%(self.value.x, self.value.y)
    def getSubCompanion(self):
        from Companions.Companions import PosDTC
        return PosDTC

class FontPropEdit(ClassPropEdit):
#    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, _1=None , _2=None):
#        ClassPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

    def getStyle(self):
        return ClassPropEdit.getStyle(self) + [esDialog, esReadOnly, esRecreateProp]

    def getSubCompanion(self):
        from Companions.Companions import FontDTC
        return FontDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def getValue(self):
        return self.value

    def edit(self, event):
        data = wx.FontData()
        dlg = wx.FontDialog(self.parent, data)
        dlg.GetFontData().SetInitialFont(self.value)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.value = dlg.GetFontData().GetChosenFont()
                self.inspectorPost(False)
        finally:
            dlg.Destroy()

    def valueAsExpr(self):
        fnt = self.value
        return fontAsExpr(fnt)

def fontAsExpr(fnt):
    fontFamily = Enumerations.reverseDict(Enumerations.fontFamilyNames)
    fontStyle = Enumerations.reverseDict(Enumerations.fontStyleNames)
    fontWeight = Enumerations.reverseDict(Enumerations.fontWeightNames)

    family = fontFamily.get(fnt.GetFamily(), fnt.GetFamily())
    style = fontStyle.get(fnt.GetStyle(), fnt.GetStyle())
    weight = fontWeight.get(fnt.GetWeight(), fnt.GetWeight())

    return 'wx.Font(%d, %s, %s, %s, %s, %s)'%(
        fnt.GetPointSize(), family, style, weight,
        fnt.GetUnderlined() and 'True' or 'False',
        repr(fnt.GetFaceName()))


class AnchorPropEdit(OptionedPropEdit):
    def getStyle(self):
        return [esExpandable]

    def getSubCompanion(self):
        from Companions.Companions import AnchorsDTC
        return AnchorsDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        if self.expanded:
            wx.MessageBox(_('Anchors can not be reset while the property is expanded'),
                  _('Anchors'))
        else:
            if self.companion.anchorSettings:
                message = _('Remove anchors?')
            else:
                message = _('Define default Anchors?')

            dlg = wx.MessageDialog(self.parent, message,
                              _('Anchors'), wx.YES_NO | wx.ICON_QUESTION)
            try:
                if dlg.ShowModal() == wx.ID_YES:
                    if self.companion.anchorSettings:
                        self.companion.removeAnchors()
                        self.propWrapper.setValue(self.getValue())
                    else:
                        self.companion.defaultAnchors()
                        self.inspectorPost(False)
            finally:
                dlg.Destroy()

    def getValue(self):
        return self.companion.GetAnchors(self.companion)

    def getDisplayValue(self):
        if self.companion.anchorSettings:
            l, t, r, b = self.companion.anchorSettings
            set = []
            if l: set.append('left')
            if t: set.append('top')
            if r: set.append('right')
            if b: set.append('bottom')
            return '('+', '.join(set)+')'
        else:
            return 'None'

    def valueAsExpr(self):
        if self.companion.anchorSettings:
            l, t, r, b = self.companion.anchorSettings
            return 'LayoutAnchors(self.%s, %s, %s, %s, %s)'%(self.companion.name,
                l and 'True' or 'False', t and 'True' or 'False',
                r and 'True' or 'False', b and 'True' or 'False')
        else:
            return 'None'


class SashVisiblePropEdit(BoolPropEdit):
    sashEdgeMap = {wx.adv.SASH_LEFT: 'wx.SASH_LEFT', wx.adv.SASH_TOP: 'wx.SASH_TOP',
                   wx.adv.SASH_RIGHT: 'wx.SASH_RIGHT', wx.adv.SASH_BOTTOM: 'wx.SASH_BOTTOM'}
    def valueToIECValue(self):
        v = self.value[1]
        if isinstance(v, int):
            return self.getValues()[v]
        else: return repr(v)
    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value[1])
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValues()[self.value[1]])
##    def getDisplayValue(self):
##        return self.valueToIECValue()
##    def getValues(self):
##        return ['False', 'True']
    def getValue(self):
        if self.editorCtrl:
            # trick to convert boolean string to integer
            v = self.editorCtrl.getValue()
            self.value = (self.value[0], self.getValues().index(self.editorCtrl.getValue()))
        return self.value
    def valueAsExpr(self):
        return '%s, %s'%(self.sashEdgeMap[self.value[0]],
                         self.value[1] and 'True' or 'False')

class CollectionPropEdit(PropertyEditor):
    """ Class associated with a design time identified type,
        it manages the behaviour of a NameValue in the Inspector
    """

    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, names, options):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def inspectorPost(self, closeEditor = True):
        """ Code persistance taken over by companion because collection
            transactions live longer than properties
        """
        if self.editorCtrl and closeEditor:
            self.editorCtrl.destroyControl()
            self.editorCtrl = None
            self.refreshCompCtrl()

    def getDisplayValue(self):
        return '(%s)'%self.name

    def valueAsExpr(self):
        return self.getDisplayValue()

    def edit(self, event):
        self.companion.designer.showCollectionEditor(\
          self.companion.name, self.name)

class ListColumnsColPropEdit(CollectionPropEdit): pass
class AcceleratorEntriesColPropEdit(CollectionPropEdit): pass
class MenuBarColPropEdit(CollectionPropEdit): pass
class MenuColPropEdit(CollectionPropEdit): pass
class ImagesColPropEdit(CollectionPropEdit): pass
class NotebookPagesColPropEdit(CollectionPropEdit): pass

# Property editor registration

def registerEditors(reg):
    for theType, theClass, editors in registeredTypes:
        if theType == 'Type':
            reg.registerTypes(theClass, editors)
        elif theType == 'Class':
            reg.registerClasses(theClass, editors)

registeredTypes = [
    ('Type', int, [IntPropEdit]),
    ('Type', str, [StrPropEdit]),
    # ('Type', UnicodeType, [StrPropEdit]),
    ('Type', tuple, [TuplePropEdit]),
    ('Class', wx.Size, [SizePropEdit]),
    ('Class', wx.Point, [PosPropEdit]),
    ('Class', wx.Font, [FontPropEdit]),
    ('Class', wx.Colour, [ColPropEdit]),
    ('Class', wx.Bitmap, [BitmapPropEdit]),
    ('Class', wx.Icon, [IconPropEdit]),
]

try:
    registeredTypes.append( ('Type', bool, [BoolPropEdit]) )
except NameError: # 2.2
    pass
