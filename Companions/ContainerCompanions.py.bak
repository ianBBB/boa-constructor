#-----------------------------------------------------------------------------
# Name:        ContainerCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.ContainerCompanions'

import copy

import wx

import Preferences, Utils
from Utils import _

from BaseCompanions import ContainerDTC, CollectionDTC, CollectionIddDTC
import PaletteStore

import Constructors
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

import methodparse, sourceconst

EventCategories['PanelEvent'] = ('wx.EVT_SYS_COLOUR_CHANGED',)

class PanelDTC(Constructors.WindowConstr, ContainerDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['DefaultItem'] = ButtonClassLinkPropEdit
        self.windowStyles.insert(0, 'wx.TAB_TRAVERSAL')

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.TAB_TRAVERSAL',
                'name':  `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['PanelEvent']

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + ['DefaultItem']

EventCategories['SashEvent'] = ('wx.EVT_SASH_DRAGGED', )
commandCategories.append('SashEvent')
class SashWindowDTC(Constructors.WindowConstr, ContainerDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'SashVisibleLeft' : SashVisiblePropEdit,
                             'SashVisibleTop' : SashVisiblePropEdit,
                             'SashVisibleRight' : SashVisiblePropEdit,
                             'SashVisibleBottom' : SashVisiblePropEdit})
        self.windowStyles = ['wx.SW_3D', 'wx.SW_3DSASH', 'wx.SW_3DBORDER',
                             'wx.SW_BORDER'] + self.windowStyles
        self.edgeNameMap = {'SashVisibleLeft'  : wx.SASH_LEFT,
                            'SashVisibleTop'   : wx.SASH_TOP,
                            'SashVisibleRight' : wx.SASH_RIGHT,
                            'SashVisibleBottom': wx.SASH_BOTTOM}
        for name in self.edgeNameMap.keys() + ['SashVisible']:
            self.customPropEvaluators[name] = self.EvalSashVisible
        #self.customPropEvaluators['SashVisible'] = self.EvalSashVisible

    def properties(self):
        props = ContainerDTC.properties(self)
        prop = ('NameRoute', self.GetSashVisible, self.SetSashVisible)
        for name in self.edgeNameMap.keys():
            props[name] = prop
        return props

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.CLIP_CHILDREN | wx.SW_3D',
                'name':  `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['SashEvent']

    def GetSashVisible(self, name):
        return self.edgeNameMap[name], self.control.GetSashVisible(self.edgeNameMap[name])

    def SetSashVisible(self, name, value):
        self.control.SetSashVisible(self.edgeNameMap[name], value[1])

    def EvalSashVisible(self, exprs, objects):
        res = []
        for expr in exprs:
            res.append(self.eval(expr))
        return tuple(res)

    def persistProp(self, name, setterName, value):
        if setterName == 'SetSashVisible':
            edge, visbl = value.split(',')
            for prop in self.textPropList:
                if prop.prop_setter == setterName and prop.params[0] == edge:
                    prop.params = [edge.strip(), visbl.strip()]
                    return
            self.textPropList.append(methodparse.PropertyParse( None, self.name,
                setterName, [edge.strip(), visbl.strip()], 'SetSashVisible'))
        else:
            ContainerDTC.persistProp(self, name, setterName, value)

class SashLayoutWindowDTC(SashWindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        SashWindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Alignment'   : EnumPropEdit,
                             'Orientation' : EnumPropEdit,
                            })
        self.options.update({'Alignment'   : sashLayoutAlignment,
                             'Orientation' : sashLayoutOrientation
                            })
        self.names.update({'Alignment'   : sashLayoutAlignmentNames,
                           'Orientation' : sashLayoutOrientationNames
                          })

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.CLIP_CHILDREN | wx.SW_3D',
                'name':  `self.name`}

    def properties(self):
        props = SashWindowDTC.properties(self)
        props.update({'DefaultSize': ('CompnRoute', self.GetDefaultSize,
          self.SetDefaultSize)})
        return props

    def getSizeDependentProps(self):
        return SashWindowDTC.getSizeDependentProps(self)+[('prop', 'DefaultSize')]

##    def events(self):
##        return ContainerDTC.events(self) + ['SashEvent']

    def GetDefaultSize(self, something):
        if self.control:
            return self.control.GetSize()
        else:
            return wx.Size(15, 15)

    def SetDefaultSize(self, size):
        if self.control:
            self.control.SetSize(size)

    def defaultAction(self):
        # should be called from 'Relayout' command
        self.control.SetDefaultSize(self.control.GetSize())
        wx.LayoutAlgorithm().LayoutWindow(self.control.GetParent())

class ScrolledWindowDTC(Constructors.WindowConstr, ContainerDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['TargetWindow'] = WindowClassLinkPropEdit

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':   position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.HSCROLL | wx.VSCROLL',
                'name':  `self.name`}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + ['TargetWindow']

    def events(self):
        return ContainerDTC.events(self) + ['ScrollWinEvent']
    
    def hideDesignTime(self):
        return ContainerDTC.hideDesignTime(self) + ['TargetRect']


    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
            if self.control.GetTargetWindow() == compn.control:
                self.propRevertToDefault('TargetWindow', 'SetTargetWindow')
                self.control.SetTargetWindow(self.control)

class BookCtrlDTC(Constructors.WindowConstr, ContainerDTC):
    bookCtrlName = 'wx.BookCtrl'
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Pages':     CollectionPropEdit,
                             'ImageList': ImageListClassLinkPropEdit})
        self.subCompanions['Pages'] = BookCtrlPagesCDTC
        self.letClickThru = True

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Pages': ('NoneRoute', None, None)})
        del props['Sizer']
        return props

    def designTimeControl(self, position, size, args = None):
        ctrl = ContainerDTC.designTimeControl(self, position, size, args)
        ctrl.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged, id=ctrl.GetId())
        return ctrl

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':   position,
                'size':  self.getDefCtrlSize(),
                'style': '0',
                'name':  `self.name`}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + ['ImageList', 'Pages']

    def dontPersistProps(self):
        return ContainerDTC.dontPersistProps(self) + ['Selection']

    def defaultAction(self):
        self.designer.inspector.props.getNameValue('Pages').propEditor.edit(None)

    def OnPageChanged(self, event):
        try:
            if 'Pages' in self.collections:
                self.collections['Pages'].updateSelection(event.GetSelection())
                wx.PostEvent(self.control, wx.SizeEvent( self.control.GetSize() ))
        except Exception, err:
            print 'OnPageChanged exception', str(err)
        event.Skip()

    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
            if self.control.GetImageList() == compn.control:
                self.propRevertToDefault('ImageList', 'SetImageList')
                self.control.SetImageList(None)

class BookCtrlPagesCDTC(CollectionDTC):
    propName = 'Pages'
    displayProp = 'text'
    indexProp = '(None)'
    insertionMethod = 'AddPage'
    deletionMethod = 'RemovePage'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Page': ClassLinkConstrPropEdit,
                        'Text': StrConstrPropEdit,
                        'Selected' : BoolConstrPropEdit,
                        'ImageId': IntConstrPropEdit}

        self.tempPlaceHolders = []

    def constructor(self):
        return {'Page': 'page', 'Text': 'text',
                'Selected' : 'select', 'ImageId': 'imageId'}

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Page': ('NoneRoute', None, None),
                      'Text': ('IndexRoute', wx.Notebook.GetPageText.im_func, wx.Notebook.SetPageText.im_func),
                      'Selected' : ('CompnRoute', self.GetPageSelected, self.SetPageSelected),
                      'ImageId': ('IndexRoute', wx.Notebook.GetPageImage.im_func, wx.Notebook.SetPageImage.im_func)})
        return props

##    def appendItem(self):
##        tph = wx.Window(self.control, -1)
##        self.tempPlaceHolders.append(tph)
##        CollectionDTC.appendItem(self)

    def designTimeSource(self, wId, method=None):
        return {'page': 'None',
                'text': `'%s%d'%(self.propName, wId)`,
                'select': 'True',
                'imageId': `-1`}

    def initDesignTimeEvents(self, ctrl):
        ctrlEvtHandler = self.designer.ctrlEvtHandler
        ctrl.Bind(wx.EVT_MOTION, ctrlEvtHandler.OnMouseOver)
        ctrl.Bind(wx.EVT_LEFT_DOWN, ctrlEvtHandler.OnControlSelect)
        ctrl.Bind(wx.EVT_LEFT_UP, ctrlEvtHandler.OnControlRelease)
        ctrl.Bind(wx.EVT_LEFT_DCLICK, ctrlEvtHandler.OnControlDClick)
        ctrl.Bind(wx.EVT_SIZE, ctrlEvtHandler.OnControlResize)

    def applyDesignTimeDefaults(self, params, method=None):
        prms = copy.copy(params)

        page = BlankWindowPage(self.control, self.designer, params, 'page')
        self.tempPlaceHolders.append(page)
        if params['page'] != 'None':
            ctrl = self.designer.objects[prms['page'][5:]][1]
            ctrl.Reparent(page)
            page.ctrl = ctrl

        del prms['page']
        params = self.designTimeDefaults(prms, method)
        params['page'] = page

        getattr(self.control, self.insertionMethod)(**params)

    def moveItem(self, idx, dir):
        newIdx = CollectionDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            focus = self.control.GetSelection() == idx
            text = self.control.GetPageText(idx)
            img = self.control.GetPageImage(idx)
            page = self.control.GetPage(idx)
            if self.control.RemovePage(idx):
                self.control.InsertPage(newIdx, page, text, focus, img)
        return newIdx

    def deleteItem(self, idx):
        activePageDeleted = self.control.GetSelection() == idx

        CollectionDTC.deleteItem(self, idx)

        # Delete BlankWindow
        self.tempPlaceHolders[idx].Destroy()
        del self.tempPlaceHolders[idx]

        # Set new active page if necesary
        if activePageDeleted:
            newIdx = idx
            if idx == len(self.textConstrLst):
                newIdx = newIdx - 1
            elif len(self.textConstrLst) == 0:
                newIdx = None

            if newIdx is not None:
                if newIdx < self.control.GetPageCount():
                    self.updateSelection(newIdx)
                    self.control.SetSelection(newIdx)
                    self.control.Refresh()

        del self.textConstrLst[idx]

    def updateSelection(self, newSelection):
        idx = 0
        for constr in self.textConstrLst:
            constr.params['select'] = newSelection == idx and 'True' or 'False'
            idx = idx + 1

    def defaultAction(self):
        self.SetPageSelected(True)

    def GetPageSelected(self, compn):
        pass

    def SetPageSelected(self, value):
        if value:
            self.control.SetSelection(self.index)

    def notification(self, compn, action):
        if action == 'delete':
            if compn == self:
                # Notebook page being deleted
                # XXX Consider overwriting deleteItem for this
                constr = self.textConstrLst[compn.index]
                if constr.params['page'] != 'None':
                    self.designer.deleteCtrl(Utils.ctrlNameFromSrcRef(constr.params['page']))
            else:
                for constr in self.textConstrLst:
                    if Utils.srcRefFromCtrlName(compn.name) == constr.params['page']:
                        constr.params['page'] == 'None'

                for tph in self.tempPlaceHolders:
                    if tph.ctrl == compn.control:
                        tph.clearCtrl()

    def writeCollectionItems(self, output, stripFrmId=''):
        CollectionDTC.writeCollectionItems(self, output, stripFrmId)
        warn = 0
        for constr in self.textConstrLst:
            if constr.params['page'] == 'None':
                wx.LogWarning('No control for %s, page %s'%(
                      self.parentCompanion.name, constr.params['text']))
                warn = 1
        if warn:
            wx.LogWarning(_('The red-dashed area of a %s page must contain\n'\
            'a control or the generated source will be invalid outside the '\
            'Designer')% self.parentCompanion.bookCtrlName)

[wxID_CTRLPARENT, wxID_EDITPASTE, wxID_EDITDELETE] = Utils.wxNewIds(3)

class BlankWindowPage(wx.Window):
    """ Window representing uninitialised space, it grabs the first control
        dropped onto it and replaces None with new ctrl in code.

        Used by BookCtrls for a default page
    """

    # XXX A delete of this object should remove the page from the notebook

    # XXX Copy/Cutting a blank page does not make sense ???

    def __init__(self, parent, designer, params, nameKey):
        wx.Window.__init__(self, parent, -1)
        self.params = params
        self.designer = designer

        # XXX how/when can I delete this menu, it will leak !!
        self.menu = wx.Menu()
        self.menu.Append(wxID_CTRLPARENT, 'Up')
        self.menu.AppendSeparator()
        self.menu.Append(wxID_EDITPASTE, 'Paste')
        self.menu.Append(wxID_EDITDELETE, 'Delete')
        self.Bind(wx.EVT_MENU, self.OnCtrlParent, id=wxID_CTRLPARENT)
        self.Bind(wx.EVT_MENU, self.OnCtrlPaste, id=wxID_EDITPASTE)
        self.Bind(wx.EVT_MENU, self.OnCtrlDelete, id=wxID_EDITDELETE)

        ctrlEvtHandler = self.designer.ctrlEvtHandler
        self.Bind(wx.EVT_MOTION, ctrlEvtHandler.OnMouseOver)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnControlSelect)
        self.Bind(wx.EVT_LEFT_UP, ctrlEvtHandler.OnControlRelease)
        self.Bind(wx.EVT_LEFT_DCLICK, ctrlEvtHandler.OnControlDClick)
        self.Bind(wx.EVT_SIZE, self.OnControlResize)
        self.Bind(wx.EVT_MOVE, self.OnControlMove)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_RIGHT_UP, self.OnPopupMenu)

        self.SetName(parent.GetName())
        self.ctrl = None
        self.nameKey = nameKey

        self.proxyContainer = True

    def clearCtrl(self):
        self.ctrl = None
        self.params[self.nameKey] = 'None'

    def OnControlSelect(self, event):
        """ Select parent of proxy container or create new control, update
            page reference to it and resize new ctrl to fill proxy container
        """
        dsgn = self.designer
        new = dsgn.compPal.selection
        if self.ctrl:
            dsgn.selectControlByPos(self.ctrl, event.GetPosition(), event.ShiftDown())
        else:
            dsgn.ctrlEvtHandler.OnControlSelect(event)

        if new:
            self.linkToNewestControl()

    def OnControlResize(self, event):
        """ Child ctrl of the proxy container should be sized to fill the control
        """
        if self.ctrl:
            p = self.GetPosition()
            s = self.GetSize()
            self.ctrl.SetDimensions(0, 0, s.x, s.y)
        else:
            self.designer.ctrlEvtHandler.OnControlResize(event)

    dashSize = 8
    def OnPaint(self, event):
        """ Draw red dash pattern, hopefully implying danger are that must be
            filled
        """
        try:
            if self.ctrl is None:
                dc = wx.PaintDC(self)
                sze = self.GetClientSize()

                dc.SetPen(wx.RED_PEN)
                dc.BeginDrawing()
                try:
                    for i in range((sze.x + sze.y) / self.dashSize):
                        dc.DrawLine(0, i*self.dashSize, i*self.dashSize, 0)
                finally:
                    dc.EndDrawing()
        finally:
            event.Skip()

    def OnControlMove(self, event):
        """ When moved or sized, ignore and fill the proxy container
        """
        parent = self.GetParent()
        wx.PostEvent(parent, wx.SizeEvent( parent.GetSize() ))

    def OnCtrlParent(self, event):
        self.designer.OnSelectParent(event)

    def OnCtrlPaste(self, event):
        self.designer.OnPasteSelected(event)

    def OnCtrlDelete(self, event):
        self.designer.OnControlDelete(event)

    def OnPopupMenu(self, event):
        self.PopupMenu(self.menu, event.GetPosition())

    def linkToNewestControl(self):
        self.ctrl = self.designer.objects[self.designer.objectOrder[-1:][0]][1]
        self.params[self.nameKey] = Utils.srcRefFromCtrlName(self.ctrl.GetName())
        self.OnControlResize(None)


EventCategories['NotebookEvent'] = ('wx.EVT_NOTEBOOK_PAGE_CHANGED',
                                    'wx.EVT_NOTEBOOK_PAGE_CHANGING')
commandCategories.append('NotebookEvent')
class NotebookDTC(BookCtrlDTC):
    bookCtrlName = 'wx.Notebook'
    def __init__(self, name, designer, parent, ctrlClass):
        BookCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.NB_FIXEDWIDTH', 'wx.NB_LEFT', 'wx.NB_RIGHT',
                             'wx.NB_BOTTOM', 'wx.NB_MULTILINE'] + self.windowStyles
    def events(self):
        return BookCtrlDTC.events(self) + ['NotebookEvent']


EventCategories['ListbookEvent'] = ('wx.EVT_LISTBOOK_PAGE_CHANGED', 
                                    'wx.EVT_LISTBOOK_PAGE_CHANGING')
commandCategories.append('ListbookEvent')
class ListbookDTC(BookCtrlDTC):
    bookCtrlName = 'wx.Listbook'
    def __init__(self, name, designer, parent, ctrlClass):
        BookCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.LB_DEFAULT', 'wx.LB_TOP', 'wx.LB_LEFT', 
              'wx.LB_RIGHT', 'wx.LB_BOTTOM', 'wx.LB_ALIGN_MASK'] + self.windowStyles
    def events(self):
        return BookCtrlDTC.events(self) + ['ListbookEvent']


EventCategories['ChoicebookEvent'] = ('wx.EVT_CHOICEBOOK_PAGE_CHANGED', 
                                      'wx.EVT_CHOICEBOOK_PAGE_CHANGING')
commandCategories.append('ListbookEvent')
class ChoicebookDTC(BookCtrlDTC):
    bookCtrlName = 'wx.Choicebook'
    def __init__(self, name, designer, parent, ctrlClass):
        BookCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.CHB_DEFAULT', 'wx.CHB_TOP', 'wx.CHB_LEFT', 
              'wx.CHB_RIGHT', 'wx.CHB_BOTTOM', 'wx.CHB_ALIGN_MASK'] + self.windowStyles
    def events(self):
        return BookCtrlDTC.events(self) + ['ChoicebookEvent']

EventCategories['TreebookEvent'] = ('wx.EVT_TREEBOOK_PAGE_CHANGED', 
                                    'wx.EVT_TREEBOOK_PAGE_CHANGING',
                                    'wx.EVT_TREEBOOK_NODE_COLLAPSED',
                                    'wx.EVT_TREEBOOK_NODE_EXPANDED')
commandCategories.append('TreebookEvent')
class TreebookDTC(BookCtrlDTC):
    bookCtrlName = 'wx.Treebook'
    def __init__(self, name, designer, parent, ctrlClass):
        BookCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.BK_DEFAULT', 'wx.BK_TOP', 'wx.BK_LEFT', 
              'wx.BK_RIGHT', 'wx.BK_BOTTOM'] + self.windowStyles
    def events(self):
        return BookCtrlDTC.events(self) + ['TreebookEvent']

EventCategories['ToolbookEvent'] = ('wx.EVT_TOOLBOOK_PAGE_CHANGED', 
                                    'wx.EVT_TOOLBOOK_PAGE_CHANGING')
commandCategories.append('ToolbookEvent')
class ToolbookDTC(BookCtrlDTC):
    bookCtrlName = 'wx.Toolbook'
    def __init__(self, name, designer, parent, ctrlClass):
        BookCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.BK_DEFAULT'] + self.windowStyles
    def events(self):
        return BookCtrlDTC.events(self) + ['ToolbookEvent']


EventCategories['SplitterWindowEvent'] = ('wx.EVT_SPLITTER_SASH_POS_CHANGING',
                                          'wx.EVT_SPLITTER_SASH_POS_CHANGED',
                                          'wx.EVT_SPLITTER_UNSPLIT',
                                          'wx.EVT_SPLITTER_DOUBLECLICKED')
commandCategories.append('SplitterWindowEvent')

class SplitterWindowDTC(ContainerDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'SplitMode': EnumPropEdit,
                             'Window1'  : SplitterWindow1LinkPropEdit,
                             'Window2'  : SplitterWindow2LinkPropEdit})
        self.options['SplitMode'] = splitterWindowSplitMode
        self.names['SplitMode'] = splitterWindowSplitModeNames
        self.windowStyles = ['wx.SP_3D', 'wx.SP_3DSASH', 'wx.SP_3DBORDER',
                             'wx.SP_BORDER', 'wx.SP_NOBORDER', 
                             'wx.SP_PERMIT_UNSPLIT', 'wx.SP_LIVE_UPDATE',
                             ] + self.windowStyles 
        self.win1 = None
        self.win2 = None

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style',
                'Name': 'name'}

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Window1'  : ('CompnRoute', self.GetWindow1, self.SetWindow1),
                      'Window2'  : ('CompnRoute', self.GetWindow2, self.SetWindow2),
                      'SplitMode': ('CompnRoute', self.GetSplitMode, self.SetSplitMode),})
        return props

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.SP_3D',
                'name':  `self.name`}

    def hideDesignTime(self):
        return ContainerDTC.hideDesignTime(self) + ['SplitMode']

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + \
          ['SplitVertically', 'SplitHorizontally']

    def events(self):
        return ContainerDTC.events(self) + ['SplitterWindowEvent']

    modeMethMap = {wx.SPLIT_VERTICAL:   'SplitVertically',
                   wx.SPLIT_HORIZONTAL: 'SplitHorizontally'}

    def renameCtrlRefs(self, oldName, newName):
        ContainerDTC.renameCtrlRefs(self, oldName, newName)
        # Check if subwindow references have changed
        # XXX should maybe be done with notification, action = 'rename'
        oldSrc = Utils.srcRefFromCtrlName(oldName)
        for prop in self.textPropList:
            if prop.prop_setter in ('SplitVertically', 'SplitHorizontally'):
                if oldSrc in prop.params:
                    prop.params[prop.params.index(oldSrc)] = \
                          Utils.srcRefFromCtrlName(newName)

    def persistProp(self, name, setterName, value):
        """ When attempting to persist the Window properties and the
            SplitMode property, add, or update a previously
            defined  SplitVertically or SplitHorizontally method."""

        if setterName in ('SetWindow1', 'SetWindow2'):
            propSN = setterName
            setterName = self.modeMethMap[self.control.GetSplitMode()]

            win1, win2 = self.GetWindow1(None), self.GetWindow2(None)
            sashPos = `self.control.GetSashPosition()`

            if win1: win1 = 'self.'+win1.GetName()
            else: win1 = 'None'
            if win2: win2 = 'self.'+win2.GetName()
            else: win2 = 'None'

            for prop in self.textPropList:
                if prop.prop_setter in ('SplitVertically', 'SplitHorizontally'):
                    prop.prop_setter = setterName
                    prop.params = [win1, win2, sashPos]
                    return
            self.textPropList.append(methodparse.PropertyParse( None, self.name,
                setterName, [win1, win2, sashPos], setterName))
        elif setterName == 'SetSplitMode':
            sm = self.control.GetSplitMode()
            setterName = self.modeMethMap[sm]
            for prop in self.textPropList:
                if prop.prop_setter == 'SplitVertically' and sm == wx.SPLIT_HORIZONTAL or \
                   prop.prop_setter == 'SplitHorizontally' and sm == wx.SPLIT_VERTICAL:
                    prop.prop_setter = setterName
                    return

        elif setterName == 'SetSashPosition':
            for prop in self.textPropList:
                if prop.prop_setter in ('SplitVertically', 'SplitHorizontally'):
                    prop.params[2] = value
                    return
        else:
            ContainerDTC.persistProp(self, name, setterName, value)

    def persistedPropVal(self, name, setterName):
        # Unlike usual properties, SashPosition is persisted as a Split* method
        # Therefore it needs to check the Split* method for the source value
        if setterName == 'SetSashPosition':
            for prop in self.textPropList:
                if prop.prop_setter in ('SplitVertically', 'SplitHorizontally'):
                    return prop.params[2]
        return ContainerDTC.persistedPropVal(self, name, setterName)

    def notification(self, compn, action):
        ContainerDTC.notification(self, compn, action)
        if action == 'delete':
            # If the splitter itself is deleted it should unsplit so that
            # deletion notifications from it's children won't cause
            # access to deleted controls
            if compn.control == self.control:
                self.win1 = self.win2 = None
                self.splitWindow(None, None)
                return
            # Win 1
            # If Window1 is None, splitter can only be unsplit
            if compn.control == self.win1:#self.GetWindow1(None):
                self.control.Unsplit(self.win1)
                if self.win2: self.win2.Show(True)
                self.win1 = self.win2 = None

                setterName = self.modeMethMap[self.control.GetSplitMode()]
                self.propRevertToDefault('Window1', setterName)
                self.designer.inspector.propertyUpdate('Window1')
                self.designer.inspector.propertyUpdate('Window2')
                return
            if compn.control == self.win2:#self.GetWindow2(None):
                self.SetWindow2(None)
                setterName = self.modeMethMap[self.control.GetSplitMode()]
                self.persistProp('Window2', setterName, None)
                self.designer.inspector.propertyUpdate('Window2')
                return

#---Split mode------------------------------------------------------------------
    def GetSplitMode(self, compn):
        return self.control.GetSplitMode()

    def SetSplitMode(self, value):
        ctrl = self.control
        ctrl.SetSplitMode(value)

        # Resplit to force splitter to update
        w1, w2 = ctrl.GetWindow1(), ctrl.GetWindow2()
        self.splitWindow(w1, w2)

#---Window1&2 methods---------------------------------------------------------
    def splitWindow(self, window1, window2):
        ctrl = self.control
        sm = ctrl.GetSplitMode()
        sp = ctrl.GetSashPosition()

        if ctrl.IsSplit():
            ctrl.Unsplit()

        if sm == wx.SPLIT_VERTICAL:
            splitMeth = ctrl.SplitVertically
        elif sm == wx.SPLIT_HORIZONTAL:
            splitMeth = ctrl.SplitHorizontally
        else:
            return

        if window1 and window2:
            splitMeth(window1, window2, sp)
        elif window1 or window2:
            if window1:
                ctrl.Initialize(window1)
            else:
                ctrl.Initialize(window2)

        if window1: window1.Show(True)
        if window2: window2.Show(True)

        self.designer.inspector.propertyUpdate('SashPosition')

    def getWindow(self, win, winGetter):
        if not win:
            w = winGetter()
            if w:
                wId = w.GetId()
                for cmpn, ctrl, prnt in self.designer.objects.values():
                    if ctrl.GetId() == wId:
                        return ctrl
            return None
        else:
            return win

    def GetWindow1(self, compn):
        self.win1 = self.getWindow(self.win1, self.control.GetWindow1)
        return self.win1

    def SetWindow1(self, value):
        # XXX check win1!=win2
        self.win1 = value
        w2 = self.GetWindow2(None)
        if value:
            self.splitWindow(value, w2)
        elif w2:
            self.win1 = self.win2 = None
            self.control.Unsplit()
            self.propRevertToDefault('Window1', self.modeMethMap[self.control.GetSplitMode()])
            self.designer.inspector.propertyUpdate('Window2')

    def GetWindow2(self, compn):
        self.win2 = self.getWindow(self.win2, self.control.GetWindow2)
        return self.win2

    def SetWindow2(self, value):
        self.win2 = value
        self.splitWindow(self.control.GetWindow1(), value)

EventCategories['ToolEvent'] = ('wx.EVT_TOOL', 'wx.EVT_TOOL_RCLICKED')
commandCategories.append('ToolEvent')
class ToolBarDTC(Constructors.WindowConstr, ContainerDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Tools': CollectionPropEdit})
        self.subCompanions['Tools'] = ToolBarToolsCDTC
        self.windowStyles = ['wx.TB_FLAT', 'wx.TB_DOCKABLE', 'wx.TB_HORIZONTAL',
                             'wx.TB_VERTICAL', 'wx.TB_3DBUTTONS', 'wx.TB_TEXT',
                             'wx.TB_NOICONS', 'wx.TB_NODIVIDER', 'wx.TB_NOALIGN',
                            ] + self.windowStyles

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Tools': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wx.TB_HORIZONTAL | wx.NO_BORDER',
                'name': `self.name`}

    def dependentProps(self):
        return ContainerDTC.dependentProps(self) + ['Tools']

    def defaultAction(self):
        self.designer.inspector.props.getNameValue('Tools').propEditor.edit(None)


def BlankToolBitmap(width, height):
    bmp = wx.EmptyBitmap(width, height)
    dc = wx.MemoryDC()
    dc.SelectObject(bmp)
    dc.SetBrush(wx.Brush(wx.RED, wx.BDIAGONAL_HATCH))
    dc.SetBackground(wx.Brush(wx.WHITE))
    dc.SetPen(wx.Pen(wx.WHITE, 0, wx.TRANSPARENT))
    dc.BeginDrawing()
    dc.DrawRectangle(0, 0, width, height)

    return bmp

class BlankToolControl(wx.StaticBitmap):
    def __init__(self, toolbar):
        width, height = toolbar.GetToolSize().Get()
        bmp = BlankToolBitmap(width, height)
        wx.StaticBitmap.__init__(self, toolbar, -1, bmp, style=wx.SIMPLE_BORDER)


class ToolBarToolsCDTC(CollectionIddDTC):
    propName = 'Tools'
    displayProp = 'shortHelp'
    indexProp = '(None)'
    insertionMethod = 'DoAddTool'
    deletionMethod = 'DeleteToolByPos'
    idProp = 'id'
    idPropNameFrom = 'tools'

    additionalMethods = {'AddSeparator': (_('Add separator'), '', '(None)'),
                         'AddControl': (_('Add control'), 'control', '(None)'),
                         'AddTool': (_('Old add tool'), 'shortHelpString', '(None)')
                        }

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionIddDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors.update({'Bitmap': BitmapConstrPropEdit,
                             'PushedBitmap': BitmapConstrPropEdit,
                             'BitmapDisabled': BitmapConstrPropEdit,
                             'IsToggle': BoolConstrPropEdit,
                             'Label': StrConstrPropEdit,
                             'ShortHelpString': StrConstrPropEdit,
                             'LongHelpString': StrConstrPropEdit,
                             'ShortHelp': StrConstrPropEdit,
                             'LongHelp': StrConstrPropEdit,
                             'Kind': EnumConstrPropEdit,
                             'Control': WinEnumConstrPropEdit})
        self.names['Kind'] = ['wx.ITEM_NORMAL', 'wx.ITEM_CHECK', 'wx.ITEM_RADIO']

    def constructor(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method == 'DoAddTool':
            return {'ItemId': 'id',
                    'Label': 'label',
                    'Bitmap': 'bitmap',
                    'BitmapDisabled': 'bmpDisabled',
                    'Kind': 'kind',
                    'ShortHelp': 'shortHelp',
                    'LongHelp': 'longHelp'}
        elif tcl.method == 'AddTool':
            return {'ItemId': 'id', 'Bitmap': 'bitmap',
                    'PushedBitmap': 'pushedBitmap',
                    'IsToggle': 'isToggle',
                    'ShortHelpString': 'shortHelpString',
                    'LongHelpString': 'longHelpString'}
        elif tcl.method == 'AddSeparator':
            return {}
        elif tcl.method == 'AddControl':
            return {'Control': 'control'}

    def properties(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method in ('DoAddTool', 'AddTool'):
            return CollectionIddDTC.properties(self)
        elif tcl.method == 'AddSeparator':
            return {}
        elif tcl.method == 'AddControl':
            return {}

    def designTimeSource(self, wId, method=None):
        if method is None:
            method = self.insertionMethod

        newItemName, winId = self.newUnusedItemNames(wId)

        if method == 'DoAddTool':
            return {'id': winId,
                    'label': `''`,
                    'bitmap': 'wx.NullBitmap',
                    'bmpDisabled': 'wx.NullBitmap',
                    'kind': 'wx.ITEM_NORMAL',
                    'shortHelp': `newItemName`,
                    'longHelp': `''`}
        elif method == 'AddTool':
            return {'id': winId,
                    'bitmap': 'wx.NullBitmap',
                    'pushedBitmap': 'wx.NullBitmap',
                    'isToggle': 'False',
                    'shortHelpString': `newItemName`,
                    'longHelpString': `''`}
        elif method == 'AddSeparator':
            return {}
        elif method == 'AddControl':
            return {'control': 'None'}

    def finaliser(self):
        return ['', sourceconst.bodyIndent+'parent.Realize()']

    def appendItem(self, method=None):
        CollectionIddDTC.appendItem(self, method)
        self.control.Realize()

    def deleteItem(self, idx):
        CollectionIddDTC.deleteItem(self, idx)
        del self.textConstrLst[idx]

    def moveItem(self, idx, dir):
        newIdx = CollectionIddDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            self.control.ClearTools()
            for crt in self.textConstrLst:
                self.applyDesignTimeDefaults(crt.params, crt.method)
        return newIdx

    def applyDesignTimeDefaults(self, params, method=None):
        if method is None:
            method = self.insertionMethod

        prms = copy.copy(params)
        control = None
        if 'control' in params:
            if params['control'] == 'None':
                control = BlankToolControl(self.control)
            else:
                control = self.designer.objects[Utils.ctrlNameFromSrcRef(params['control'])][1]
            del prms['control']

        bitmaps = {}
        for bmp in ('bitmap', 'bmpDisabled', 'pushedBitmap'):
            if bmp in params and params[bmp] == 'wx.NullBitmap':
                bitmaps[bmp] = BlankToolBitmap(*self.control.GetToolBitmapSize().Get())
                del prms[bmp]

        params = self.designTimeDefaults(prms)

        if method in ('AddSeparator', 'AddControl'):
            del params['id']

        if control:
            params['control'] = control

        for bmp in bitmaps:
            params[bmp] = bitmaps[bmp]

        getattr(self.control, method)(**params)

        self.control.Realize()

    def events(self):
        return ['ToolEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ToolEvent', 'wx.EVT_TOOL')

    def notification(self, compn, action):
        if action == 'delete':
            if compn != self:
                compnSrcRef = Utils.srcRefFromCtrlName(compn.name)
                for constr in self.textConstrLst:
                    if 'control' in constr.params:
                        if compnSrcRef == constr.params['control']:
                            constr.params['control'] = 'None'
                            idx = self.textConstrLst.index(constr)
                            self.control.DeleteToolByPos(idx)
                            del self.textConstrLst[idx]
                            return

    def writeCollectionItems(self, output, stripFrmId=''):
        CollectionIddDTC.writeCollectionItems(self, output, stripFrmId)
        warn = 0
        for constr in self.textConstrLst:
            if 'control' in constr.params and constr.params['control'] == 'None':
                wx.LogWarning(_("Invalid None control for toolbar %s's AddControl")%(
                      self.parentCompanion.name))
                warn = 1
        if warn:
            wx.LogWarning(_('Control may not be None or the generated source will '
                            'be invalid outside the Designer.'))

    def GetOtherWin(self):
        return self.textConstrLst[self.index].params['control']

    def SetOtherWin(self, value):
        self.textConstrLst[self.index].params['control'] = value

class ToolBarSimpleDTC(ToolBarDTC):
    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': 'wx.TB_HORIZONTAL | wx.NO_BORDER',
                'name': `self.name`}

class StatusBarDTC(ContainerDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Fields'] = CollectionPropEdit
        self.subCompanions['Fields'] = StatusBarFieldsCDTC
        self.windowStyles = ['wx.ST_SIZEGRIP'] + self.windowStyles

    def constructor(self):
        return {'Style': 'style', 'Name': 'name'}

    def properties(self):
        props = ContainerDTC.properties(self)
        props.update({'Fields': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, position='wx.DefaultPosition', size='wx.DefaultSize'):
        return {'style': '0',
                'name': `self.name`}

    def hideDesignTime(self):
        return ContainerDTC.hideDesignTime(self) + ['Position', 'Size', 'ClientSize']

class StatusBarFieldsCDTC(CollectionDTC):
    propName = 'Fields'
    displayProp = 'text'
    indexProp = 'number'
    insertionMethod = 'SetStatusText'
    deletionMethod = '(None)'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'Number' : IntConstrPropEdit,
                        'Text': StrConstrPropEdit,
                        'Width': SBFWidthConstrPropEdit}
        self.widths = []

    def constructor(self):
        return {'Number': 'number', 'Text': 'text', 'Width': 'width'}

    def properties(self):
        props = CollectionDTC.properties(self)
        props.update({'Number':  ('NoneRoute', None, None),
                      'Text':  ('CompnRoute', self.GetText, self.SetText),
                      'Width': ('NoneRoute', None, None)})
        return props

    def designTimeSource(self, wId, method=None):
        return {'number': `wId`,
                'text': `'%s%d'%(self.propName, wId)`}

    def initialiser(self):
        return [sourceconst.bodyIndent+'parent.SetFieldsCount(%d)'%(
                self.getCount())]+CollectionDTC.initialiser(self)

    def finaliser(self):
        return ['', sourceconst.bodyIndent+'parent.SetStatusWidths(%s)'%`self.widths`]

    def initCollection(self):
        if self.widths:
            self.control.SetStatusWidths(self.widths)

    def appendItem(self, method=None):
        self.widths.append(-1)
        self.control.SetFieldsCount(len(self.widths))
        CollectionDTC.appendItem(self, method)

    def deleteItem(self, index):
        CollectionDTC.deleteItem(self, index)
        for idx in range(index, len(self.widths)):
            self.control.SetStatusText(self.control.GetStatusText(idx+1), idx)
        del self.widths[index]
        self.control.SetStatusWidths(self.widths)
        self.control.SetFieldsCount(len(self.widths))

    def moveItem(self, idx, dir):
        newIdx = CollectionDTC.moveItem(self, idx, dir)
        if newIdx != idx:
            w = self.widths[idx]
            del self.widths[idx]
            self.widths.insert(newIdx, w)
            self.control.SetStatusWidths(self.widths)
            oldText = self.control.GetStatusText(idx)
            newText = self.control.GetStatusText(newIdx)
            self.control.SetStatusText(newText, idx)
            self.control.SetStatusText(oldText, newIdx)
        return newIdx

    def setConstrs(self, constrLst, inits, fins):
        CollectionDTC.setConstrs(self, constrLst, inits, fins)
        if len(fins):
            self.widths = self.eval(fins[0]\
              [fins[0].find('(')+1 : fins[0].rfind(')')])
            self.control.SetFieldsCount(len(self.widths))

    def GetWidth(self):
        return `self.widths[self.index]`

    def SetWidth(self, value):
        self.widths[self.index] = int(value)
        self.control.SetStatusWidths(self.widths)

    def GetText(self):
        return `self.control.GetStatusText(self.index)`

    def SetText(self, value):
        self.control.SetStatusText(value, self.index)

# Designer support incomplete for this control
# Children created in this control need to reference their parent parameter
# as e.g. parent=self.collapsiblePane1.GetPane()
EventCategories['CollapsiblePaneEvent'] = ('wx.EVT_COLLAPSIBLEPANE_CHANGED', )
commandCategories.append('CollapsiblePaneEvent')
class CollapsiblePaneDTC(Constructors.LabeledInputConstr, ContainerDTC):
    suppressWindowId = True
    def __init__(self, name, designer, parent, ctrlClass):
        ContainerDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.CP_DEFAULT_STYLE', 'wx.CP_NO_TLW_RESIZE'] +self.windowStyles

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':   position,
                'size':  self.getDefCtrlSize(),
                'style': 'wx.CP_DEFAULT_STYLE',
                'name':  `self.name`,
                'label': `self.name`}

    def events(self):
        return ContainerDTC.events(self) + ['CollapsiblePaneEvent']

#-------------------------------------------------------------------------------

import Plugins

Plugins.registerPalettePage('ContainersLayout', _('Containers/Layout'))

Plugins.registerComponents('ContainersLayout',
      (wx.Panel, 'wx.Panel', PanelDTC),
      (wx.ScrolledWindow, 'wx.ScrolledWindow', ScrolledWindowDTC),
      (wx.SplitterWindow, 'wx.SplitterWindow', SplitterWindowDTC),
      (wx.SashWindow, 'wx.SashWindow', SashWindowDTC),
      (wx.SashLayoutWindow, 'wx.SashLayoutWindow', SashLayoutWindowDTC),
      (wx.ToolBar, 'wx.ToolBar', ToolBarDTC),
      (wx.StatusBar, 'wx.StatusBar', StatusBarDTC),
      (wx.Window, 'wx.Window', ContainerDTC),
      (wx.Notebook, 'wx.Notebook', NotebookDTC),
      (wx.Listbook, 'wx.Listbook', ListbookDTC),
      (wx.Choicebook, 'wx.Choicebook', ChoicebookDTC),
    )

try:
    Plugins.registerComponents('ContainersLayout',
      (wx.Treebook, 'wx.Treebook', TreebookDTC),
      (wx.Toolbook, 'wx.Toolbook', ToolbookDTC),
#      (wx.CollapsiblePane, 'wx.CollapsiblePane', CollapsiblePaneDTC),
    )  
except AttributeError:
    pass
    
    
