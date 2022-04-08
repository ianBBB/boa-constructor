import os, sys, string

import Preferences, Utils, Plugins

if not Plugins.transportInstalled('ZopeLib.ZopeExplorer'):
    raise Plugins.SkipPlugin, 'Zope support is not enabled'

#---Model-----------------------------------------------------------------------

# Define new zope image and a Model for opening in the Editor
from ZopeLib.ZopeEditorModels import addZOAImage, ZOAIcons, ZopeBlankEditorModel, ZopeController

addZOAImage('Formulator Form', 'Images/ZOA/FormulatorForm.png')

field_meta_types = ['FileField', 'MultiCheckBoxField', 'LinesField',
      'ListField', 'TextAreaField', 'MultiListField', 'EmailField',
      'CheckBoxField', 'PasswordField', 'FloatField', 'PatternField',
      'LinkField', 'StringField', 'RawTextAreaField', 'IntegerField',
      'RadioField', 'DateTimeField']
for field in field_meta_types:
    addZOAImage(field, 'Images/ZOA/FormulatorField.png')

class FormulatorFormModel(ZopeBlankEditorModel):
    imgIdx = ZOAIcons['Formulator Form']

#---Controller------------------------------------------------------------------

# Connect controller to the model
from Models import Controllers

Controllers.modelControllerReg[FormulatorFormModel] = ZopeController

#---Views-----------------------------------------------------------------------

from Views.EditorViews import EditorView
import wx

class FormulatorFormOrderView(wx.TreeCtrl, EditorView):
    viewName = 'Order'
    viewTitle = 'Order'
    
    refreshBmp = 'Images/Editor/Refresh.png'
    addGroupBmp = 'Images/Shared/NewItem.png'
    remGroupBmp = 'Images/Shared/DeleteItem.png'
    moveUpBmp = 'Images/Shared/up.png'
    moveDownBmp = 'Images/Shared/down.png'

    def __init__(self, parent, model):
        wid = wx.NewId()
        wx.TreeCtrl.__init__(self, parent, wid,
         style = wx.TR_HAS_BUTTONS | wx.SUNKEN_BORDER | wx.TR_EDIT_LABELS)
        EditorView.__init__(self, model,
          (('Refresh', self.OnRefresh, self.refreshBmp, 'Refresh'),
           ('-', None, '', ''),
           ('Add group', self.OnAddGroup, self.addGroupBmp, ''),
           ('Remove group', self.OnRemoveGroup, self.remGroupBmp, ''),
           ('Rename group', self.OnRenameGroup, '-', ''),
           ('-', None, '', ''),
           ('Move up', self.OnMoveUp, self.moveUpBmp, ''),
           ('Move down', self.OnMoveDown, self.moveDownBmp, ''),
           ('Move fields to other group', self.OnMoveFieldToGroup, '-', ''),
            ), -1)

        self.Bind(wx.EVT_KEY_UP, self.OnKeyPressed)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit, id=wid)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndLabelEdit, id=wid)

        self._groupedFields = []
        self.canExplore = True
        self.active = True

    def destroy(self):
        EditorView.destroy(self)
        self.tokenImgLst = None

    def getFormulatorForm(self):
        return self.model.zopeObj.getResource()

    sysmsg = '<div class="system-msg">'
    def getRespMesg(self, html):
        msgTagStart = string.find(html, self.sysmsg)
        if msgTagStart != -1:
            msgStart = msgTagStart+len(self.sysmsg)
            msgEnd = string.find(html, '</div>', msgStart)
            if msgEnd != -1:
                return html[msgStart:msgEnd]
        return ''

    def statusUpdate(self, html):
        self.model.editor.setStatus(self.getRespMesg(html))

    def refreshCtrl(self, selectGroupField=None):
        node = self.model.zopeObj
        groupedFields = node.getResource().zoa.props.Formulator.GroupedFields()
        # ZOA('Formulator_Form_GroupedFields')
        self._groupedFields = groupedFields

        self.DeleteAllItems()

        ri = self.AddRoot(node.name)

        if selectGroupField is not None:
            selGrp, selFld = selectGroupField
            if selGrp == selFld == None:
                si = ri
            else:
                si = None
        else:
            selGrp = selFld = None
            si = None

        for group, fields in groupedFields:
            gi = self.AppendItem(ri, group)
            if group == selGrp and selFld is None:
                si = gi
            for field, meta in fields:
                fi = self.AppendItem(gi, '%s [%s]' %(field, meta),
                      data=wx.TreeItemData( (field, meta, group) ))
                if group == selGrp and field == selFld:
                    si = fi
            self.Expand(gi)
        self.Expand(ri)

        if si is not None:
            self.SelectItem(si)
            self.EnsureVisible(si)

    def getItemLevel(self, itm):
        cnt = 0
        root = self.GetRootItem()
        while itm != root:
            itm = self.GetItemParent(itm)
            #print itm, itm.IsOk()
            cnt = cnt + 1
        return cnt

    def OnKeyPressed(self, event):
        key = event.KeyCode()
        if key == 13:
            self.EndEditLabel(self.GetSelection(), 0)

    def OnAddGroup(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter new group name', 'Add Group', '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                grpName = dlg.GetValue()
                self.getFormulatorForm().add_group(grpName)
                self.refreshCtrl( (grpName, None) )
        finally:
            dlg.Destroy()

    def OnRemoveGroup(self, event):
        ti = self.GetSelection()
        if self.getItemLevel(ti) != 1:
            wx.LogError('Selected item is not a group')
        else:
            grpName = self.GetItemText(ti)
            self.getFormulatorForm().remove_group(grpName)
            self.refreshCtrl( (grpName, None) )

    def OnRenameGroup(self, event):
        ti = self.GetSelection()
        if self.getItemLevel(ti) != 1:
            wx.LogError('Selected item is not a group')
        else:
            self.EditLabel(ti)

    def OnMoveUp(self, event):
        ti = self.GetSelection()
        lev = self.getItemLevel(ti)
        lbl = self.GetItemText(ti)
        if lev == 1:
            self.statusUpdate(self.getFormulatorForm().manage_move_group_up(lbl))
            self.refreshCtrl( (lbl, None) )
        elif lev == 2:
            fld, mta, grp = self.GetItemData(ti).GetData()
            self.statusUpdate(self.getFormulatorForm().zoa.props.Formulator.move_field('up', grp, fld))
            self.refreshCtrl( (grp, fld) )
        else:
            wx.LogError('Cannot move root')

    def OnMoveDown(self, event):
        ti = self.GetSelection()
        lev = self.getItemLevel(ti)
        lbl = self.GetItemText(ti)
        if lev == 1:
            self.statusUpdate(self.getFormulatorForm().manage_move_group_down(lbl))
            self.refreshCtrl( (lbl, None) )
        elif lev == 2:
            fld, mta, grp = self.GetItemData(ti).GetData()
            self.statusUpdate(self.getFormulatorForm().zoa.props.Formulator.move_field('down', grp, fld))
            self.refreshCtrl( (grp, fld) )
        else:
            wx.LogError('Cannot move root (%d)'%lev)

    def OnMoveFieldToGroup(self, event):
        ti = self.GetSelection()
        lev = self.getItemLevel(ti)
        lbl = self.GetItemText(ti)
        if lev != 2:
            wx.LogError('Not a field')
        else:
            groups = map(lambda d: d[0], self._groupedFields)
            fld, mta, fromGroup = self.GetItemData(ti).GetData()
            groups.remove(fromGroup)
            dlg = wx.SingleChoiceDialog(self, 'Choose group to move to',
                  'Move to other group', groups)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    toGroup = dlg.GetStringSelection()
                    self.statusUpdate(
                      self.getFormulatorForm().zoa.props.Formulator.move_field(
                      'group', fromGroup, fld, toGroup))
                    self.refreshCtrl( (toGroup, fld) )
            finally:
                dlg.Destroy()

    def OnBeginLabelEdit(self, event):
        ti = event.GetItem()
        if self.getItemLevel(ti) != 1:
            event.Veto()

    def OnEndLabelEdit(self, event):
        ti = event.GetItem()
        oldName = self.GetItemText(ti)
        newName = event.GetLabel()
        self.statusUpdate(self.getFormulatorForm().manage_rename_group(oldName,
              {'new_name':newName}))
        self.refreshCtrl( (newName, None) )

    def OnRefresh(self, event):
        ti = self.GetSelection()
        lev = self.getItemLevel(ti)
        lbl = self.GetItemText(ti)
        if lev == 2:
            fld, mta, grp = self.GetItemData(ti).GetData()
            self.refreshCtrl( (grp, fld) )
        elif lev == 1:
            self.refreshCtrl( (lbl, None) )
        elif lev == 0:
            self.refreshCtrl( (None, None) )
        else:
            self.refreshCtrl( None )

#---Explorer--------------------------------------------------------------------

# Node in the explorer
from Views import SourceViews
from ZopeLib import ZopeViews
from ZopeLib.ZopeExplorer import ZopeItemNode, ZopeNode, zopeClassMap

class FormulatorFormNode(ZopeItemNode):
    Model = FormulatorFormModel
    defaultViews = (FormulatorFormOrderView,)
    additionalViews = (ZopeViews.ZopeUndoView, ZopeViews.ZopeSecurityView)
    def isFolderish(self):
        return True
    def checkentry(self, name, metatype, path):
        return apply(FormulatorFieldNode, (name, path, self.clipboard,
            -1, self, self.server, self.root, self.properties, metatype))

class FormulatorFieldNode(ZopeNode):
    Model = FormulatorFormModel
    def open(self, editor):
        editor.explorer.controllers['zope'].doInspectZopeItem(self)
        return None, None

zopeClassMap['Formulator Form'] = FormulatorFormNode

#---PropertyEditors-------------------------------------------------------------
from PropEdit.PropertyEditors import EnumConfPropEdit

class EncTypeEnumConfPropEdit(EnumConfPropEdit):
    def getValues(self):
        return ['', 'application/x-www-form-urlencoded', 'multipart/form-data']

class MethodEnumConfPropEdit(EnumConfPropEdit):
    def getValues(self):
        return ['GET', 'POST']

#---Companion-------------------------------------------------------------------
def fieldify(props, prefix='field_'):
    res = {}
    for n, v in props.items():
        if type(v) == type([]):
            res[prefix+n] = string.join(v, '\n')
        else:
            res[prefix+n] = str(v)
    return res

# Companion used for creation from palette and inspection/posting of props
from ZopeLib.ZopeCompanions import CustomZopePropsMixIn, ZopeCompanion, BoolZopePropEdit, EvalZopePropEdit
from Companions.BaseCompanions import HelperDTC
from PropEdit.PropertyEditors import ContainerConfPropEdit
import RTTI

class FieldBoolZopePropEdit(BoolZopePropEdit):
    boolKeyMap = {'true': '1', 'false': ''}

class DateTimeFieldConfPropEdit(ContainerConfPropEdit):
    def getSubCompanion(self):
        return DateTimeFieldSubCompanion

ZopeCompanion.propMapping.update({'field_boolean': FieldBoolZopePropEdit,
                                  'form_enctype': EncTypeEnumConfPropEdit,
                                  'form_method': MethodEnumConfPropEdit,
                                  'field_date': DateTimeFieldConfPropEdit})

class FormulatorFormZC(CustomZopePropsMixIn, ZopeCompanion):
    def create(self):
        prodPath = '/manage_addProduct/Formulator/'
        mime, res = self.call(self.objPath, prodPath+'manage_add',
              id=self.name, title='', URL1='', submit='')

    def getProps(self):
        #path, name = os.path.split(self.objPath)
        mime, res = self.call(self.objPath, 'zoa/props/Formulator/Form')
        return eval(res)

    def SetProp(self, name, value):
        props = self.getProps()
        props[name] = value

        groups = props['Groups']; del props['Groups']

        if name == 'Groups':
            pass
        else:
            mime, res = self.callkw(self.objPath, 'manage_settings', fieldify(props))

    propOrder = ('title', 'row_length', 'action', 'method', 'enctype', 'Groups')
    propTypeMap = {'title':       ('string', 'title'),
                   'row_length':  ('int', 'row_length'),
                   'action':      ('string', 'action'),
                   'method':      ('form_method', 'method'),
                   'enctype':     ('form_enctype', 'enctype'),
                   'Groups':      ('list', 'Groups'),
                  }

class DateTimeFieldSubCompanion(HelperDTC):
    def __init__(self, name, designer, ownerCompanion, obj, ownerPropWrap):
        HelperDTC.__init__(self, name, designer, ownerCompanion, obj,
              ownerPropWrap)
        self.propItems = []

    def getPropEditor(self, prop):
        return EvalZopePropEdit

    def getPropList(self):
        if self.obj is None:
            raise 'First assign a DateTime to the property.'

        name, val = self.ownerCompn.propTypeMap[self.name]
        subProps = [('sub%s_year'%name, self.obj.year() ),
                    ('sub%s_month'%name, self.obj.month() ),
                    ('sub%s_day'%name, self.obj.day() ),
                    ('sub%s_hour'%name, self.obj.hour() ),
                    ('sub%s_minute'%name, self.obj.minute() ),]
        propLst = []
        for prop in subProps:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
                  self.GetProp, self.SetProp))
        self.propItems = subProps

        return {'constructor': [],
                'properties': propLst}

    def GetProp(self, name):
        for prop in self.propItems:
            if prop[0] == name: return prop[1]

    def SetProp(self, name, value):
        raise 'Property editing not supported yet'

def keyListFromDictList(key, dctLst):
    res = []
    for dct in dctLst:
        res.append(dct[key])
    return res

def dictListFind(name, value, dctLst):
    for dct in dctLst:
        if dct.has_key(name) and dct[name] == value:
            return dct
    return None

def select_d(entries_list, from_clause, where_clause):
    """ SQL wannabe """
    pass

FieldPropMap =  {'FileField': 'string',
                 #'MultiCheckBoxField': 'list',
                 #'LinesField': 'list',
                 #'ListField': 'list',
                 #'TextAreaField': 'stringlist',
                 #'MultiCheckboxField': 'stringlist',
                 #'MultiListField': 'stringlist',
                 'EmailField': 'string',
                 'CheckBoxField': 'field_boolean',
                 'PasswordField': 'string',
                 #'FloatField': 'float',
                 'PatternField': 'string',
                 'LinkField': 'string',
                 'StringField': 'string',
                 #'RawTextAreaField': 'stringlist',
                 #'IntegerField': 'string',
                 #'RadioField': 'stringlist',
                 'DateTimeField': 'field_date',
                 }
NotSupportedPropTypes = ['date']

class FormulatorFieldZC(CustomZopePropsMixIn, ZopeCompanion):

    def create(self):
        # XXX move to one zoa call assertfilteredmetatypesfor(container_metatype)
        # assert that called only in Formulator
        mime, res = self.call(self.objPath, 'zoa/metatype')
        assert res=='Formulator Form', \
              'Formulator fields can only be created inside a Formulator Form'

        # fetch valid field types
        mime, res = self.call(self.objPath, 'zoa/filteredmetatypes')
        availableFields = eval(res)

        fieldNames = keyListFromDictList('name', availableFields)
        dlg = wx.SingleChoiceDialog(None, 'Choose the formulator field to add',
            'Add field', fieldNames)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                fieldName = dlg.GetStringSelection()
            else:
                return
        finally:
            dlg.Destroy()

        mime, res = self.call(self.objPath,
              'manage_addProduct/Formulator/manage_addField',
              id=self.name, title='', fieldname=fieldName, URL1='', submit='')

    def getPropertyMap(self):
        propMap = []
        for (propName, propVal) in self.propItems:
            propMap.append( {'id': propName,
                             'type': self.getPropertyType(propName)} )
        return propMap

    def getPropertyType(self, name):
        if self.propTypeMap.has_key(name):
            return self.propTypeMap[name][0]
        else:
            return 'default'

    def getProps(self):
        mime, res = self.call(self.objPath, 'zoa/props/Formulator/Field')
        from ZopeLib.DateTime import DateTime
        lst = eval(res)

        self.propTypeMap = {}
        dct = {}
        for name, val, tpe, opts in lst:
            propEditType = FieldPropMap.get(tpe, 'default')
            if propEditType in NotSupportedPropTypes:
                continue
            self.propTypeMap[name] = (propEditType, name)
            dct[name] = val
        return dct

    def SetProp(self, name, value):
        props = self.getProps()
        props[name] = value

        messages = props['Messages']; del props['Messages']
##        overrides = props['Overrides']; del props['Overrides']

        if name == 'Messages':
            mime, res = self.callkw(self.objPath, 'manage_messages', fieldify(messages, ''))
##        elif name == 'Overrides':
##            mime, res = self.callkw(self.objPath, 'manage_override', fieldify(overrides))
        else:
            ##print fieldify(props)
            mime, res = self.callkw(self.objPath, 'manage_edit', fieldify(props))

    propOrder = None


# Add to the Zope palette
import PaletteStore
# form
PaletteStore.paletteLists['Zope'].append('Formulator Form')
PaletteStore.compInfo['Formulator Form'] = ['FormulatorForm', FormulatorFormZC]
# fields
PaletteStore.paletteLists['Zope'].append('FormulatorField')
fieldCompInfo = ['FormulatorField', FormulatorFieldZC]
PaletteStore.compInfo['FormulatorField'] = fieldCompInfo
for field in field_meta_types:
    PaletteStore.compInfo[field] = fieldCompInfo
