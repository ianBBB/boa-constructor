#-----------------------------------------------------------------------------
# Name:        BitmapListEditorDlg.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2006
# RCS-ID:      $Id$
# Copyright:   (c) 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:BitmapListEditorDlg

import wx

import methodparse

from Utils import _

from PropertyEditors import BitmapPropEditMix


class BitmapProp(BitmapPropEditMix):
    def __init__(self, parent, companion):
        self.parent = parent
        self.companion = companion


def create(parent):
    return BitmapListEditorDlg(parent)

[wxID_BITMAPLISTEDITORDLG, wxID_BITMAPLISTEDITORDLGBUTTON6, 
 wxID_BITMAPLISTEDITORDLGBUTTON7, wxID_BITMAPLISTEDITORDLGBUTTONADD, 
 wxID_BITMAPLISTEDITORDLGBUTTONEDIT, wxID_BITMAPLISTEDITORDLGBUTTONMOVEDOWN, 
 wxID_BITMAPLISTEDITORDLGBUTTONMOVEUP, wxID_BITMAPLISTEDITORDLGBUTTONREMOVE, 
 wxID_BITMAPLISTEDITORDLGLISTCTRL, 
] = [wx.NewId() for _init_ctrls in range(9)]

class BitmapListEditorDlg(wx.Dialog):
    def _init_coll_boxSizer3_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.button6, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.button7, 0, border=0, flag=0)

    def _init_coll_boxSizer4_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.buttonAdd, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.buttonRemove, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.buttonEdit, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.buttonMoveUp, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.buttonMoveDown, 0, border=0, flag=0)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.boxSizer2, 1, border=16, flag=wx.ALL | wx.GROW)
        parent.AddSizer(self.boxSizer3, 0, border=16,
              flag=wx.RIGHT | wx.LEFT | wx.BOTTOM | wx.ALIGN_RIGHT)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.listCtrl, 1, border=0, flag=wx.GROW)
        parent.AddSpacer(wx.Size(16, 16), border=0, flag=0)
        parent.AddSizer(self.boxSizer4, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_listCtrl_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT, heading='Source',
              width=320)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer3 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer4 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)
        self._init_coll_boxSizer3_Items(self.boxSizer3)
        self._init_coll_boxSizer4_Items(self.boxSizer4)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_BITMAPLISTEDITORDLG,
              name='BitmapListEditorDlg', parent=prnt, pos=wx.Point(581, 347),
              size=wx.Size(465, 371),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('Bitmap List Editor'))
        self.SetClientSize(wx.Size(457, 344))
        self.Center(wx.BOTH)

        self.listCtrl = wx.ListCtrl(id=wxID_BITMAPLISTEDITORDLGLISTCTRL,
              name='listCtrl', parent=self, pos=wx.Point(16, 16),
              size=wx.Size(334, 273),
              style=wx.LC_SINGLE_SEL | wx.LC_NO_HEADER | wx.LC_REPORT | wx.LC_ICON)
        self._init_coll_listCtrl_Columns(self.listCtrl)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnListCtrlListItemSelected,
              id=wxID_BITMAPLISTEDITORDLGLISTCTRL)

        self.buttonAdd = wx.Button(id=wxID_BITMAPLISTEDITORDLGBUTTONADD,
              label=_('Add'), name='buttonAdd', parent=self, pos=wx.Point(366, 79),
              size=wx.Size(75, 23), style=0)
        self.buttonAdd.Bind(wx.EVT_BUTTON, self.OnButtonAddButton,
              id=wxID_BITMAPLISTEDITORDLGBUTTONADD)

        self.buttonRemove = wx.Button(id=wxID_BITMAPLISTEDITORDLGBUTTONREMOVE,
              label=_('Remove'), name='buttonRemove', parent=self,
              pos=wx.Point(366, 110), size=wx.Size(75, 23), style=0)
        self.buttonRemove.Bind(wx.EVT_BUTTON, self.OnButtonRemoveButton,
              id=wxID_BITMAPLISTEDITORDLGBUTTONREMOVE)

        self.buttonEdit = wx.Button(id=wxID_BITMAPLISTEDITORDLGBUTTONEDIT,
              label=_('Edit'), name='buttonEdit', parent=self, pos=wx.Point(366,
              141), size=wx.Size(75, 23), style=0)
        self.buttonEdit.Bind(wx.EVT_BUTTON, self.OnButtonEditButton,
              id=wxID_BITMAPLISTEDITORDLGBUTTONEDIT)

        self.buttonMoveUp = wx.Button(id=wxID_BITMAPLISTEDITORDLGBUTTONMOVEUP,
              label=_('Move up'), name='buttonMoveUp', parent=self,
              pos=wx.Point(366, 172), size=wx.Size(75, 23), style=0)
        self.buttonMoveUp.Bind(wx.EVT_BUTTON, self.OnButtonMoveUpButton,
              id=wxID_BITMAPLISTEDITORDLGBUTTONMOVEUP)

        self.buttonMoveDown = wx.Button(id=wxID_BITMAPLISTEDITORDLGBUTTONMOVEDOWN,
              label=_('Move down'), name='buttonMoveDown', parent=self,
              pos=wx.Point(366, 203), size=wx.Size(75, 23), style=0)
        self.buttonMoveDown.Bind(wx.EVT_BUTTON, self.OnButtonMoveDownButton,
              id=wxID_BITMAPLISTEDITORDLGBUTTONMOVEDOWN)

        self.button6 = wx.Button(id=wx.ID_OK, label=_('OK'), name='button6',
              parent=self, pos=wx.Point(283, 305), size=wx.Size(75, 23),
              style=0)

        self.button7 = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='button7', parent=self, pos=wx.Point(366, 305),
              size=wx.Size(75, 23), style=0)

        self._init_sizers()

    def __init__(self, parent, bitmapsSrc, companion):
        self._init_ctrls(parent)
        
        self.selection = -1
        self.parent = parent
        self.companion = companion
        self.bitmapsSrc = bitmapsSrc
        self.imageList = None
        self.bitmapsSrcEntries = methodparse.safesplitfields(bitmapsSrc[1:-1], ',')
        self.bitmaps = self.companion.eval(bitmapsSrc)
        self.width, self.height = -1, -1
        self.initImageListCtrl()

    def initImageListCtrl(self):
        if self.bitmaps and self.bitmapsSrcEntries != ['wx.NullBitmap']:
            bmp = self.bitmaps[0]
            self.width, self.height = bmp.GetWidth(), bmp.GetHeight()
            self.imageList = wx.ImageList(self.width, self.height)
            self.listCtrl.SetImageList(self.imageList, wx.IMAGE_LIST_SMALL)
            self.listCtrl.DeleteAllItems()
            for idx in range(len(self.bitmaps)):
                src = self.bitmapsSrcEntries[idx]
                bmp = self.bitmaps[idx]
                
                self.addToListCtrl(idx, src, bmp)
                
    def addToListCtrl(self, idx, src, bmp, ii=None):
        if ii is None:
            ii = self.imageList.Add(bmp)
        self.listCtrl.InsertImageStringItem(idx, src, ii)

    def browseForImgSrc(self, src):
        bp = BitmapProp(self.parent, self.companion)
        dummy, dir, name, tpe = bp.extractPathFromSrc(src)
        abspth, pth, tpe = bp.showImgDlg(dir, name, tpe)
        if not tpe:
            return None, None
        elif tpe == 'ResourceModule':
            value, ctrlVal, bmpPath = bp.assureResourceLoaded(abspth, pth)
        elif tpe == 'ArtProvider':
            value, ctrlVal, bmpPath = bp.assureArtProviderImageLoaded(abspth, pth)
        elif abspth:
            value = 'wx.Bitmap(%s, %s)'%(`pth`, tpe)
            ctrlVal = wx.Bitmap(abspth, self.companion.eval(tpe))
        
        return value, ctrlVal

    def getBitmapsSource(self):
        return '['+', '.join(self.bitmapsSrcEntries)+']'

    def OnListCtrlListItemSelected(self, event):
        self.selection = event.GetIndex()

    def OnButtonAddButton(self, event):
        src, bmp = self.browseForImgSrc('wx.NullBitmap')
        
        if not (src and bmp):
            return

        if self.width == -1 and self.height == -1:
            if self.bitmapsSrcEntries == ['wx.NullBitmap']:
                self.bitmaps[0] = bmp
                self.bitmapsSrcEntries[0] = src
                
                self.initImageListCtrl()
            else:
                print ':('
            
            return

        elif self.width != bmp.GetWidth() or self.height != bmp.GetHeight():
            wx.LogError(_('Size mismatch, all images must have the same size (%s, %s), not (%s, %s)')%(
                  self.width, self.height, bmp.GetWidth(), bmp.GetHeight()))
            return
        
        self.addToListCtrl(len(self.bitmaps), src, bmp)
        self.bitmaps.append(bmp)
        self.bitmapsSrcEntries.append(src)
        
    def OnButtonRemoveButton(self, event):
        if self.selection != -1:
            del self.bitmaps[self.selection]
            del self.bitmapsSrcEntries[self.selection]

            self.listCtrl.DeleteItem(self.selection)

    def OnButtonEditButton(self, event):
        if self.selection != -1:
            src, bmp = self.browseForImgSrc(self.bitmapsSrcEntries[self.selection])

            if not (src and bmp):
                return

            if self.width != bmp.GetWidth() or self.height != bmp.GetHeight():
                wx.LogError(_('Size mismatch, all images must have the same size (%s, %s)')%(
                      self.width, self.height))
                return

            self.bitmaps[self.selection] = bmp
            self.bitmapsSrcEntries[self.selection] = src
    
            ii = self.imageList.Add(bmp)
            self.listCtrl.SetItemText(self.selection, src)
            self.listCtrl.SetItemImage(self.selection, ii)

    def moveBitmap(self, index, direction):
        bmp = self.bitmaps[index]
        bmpSrc = self.bitmapsSrcEntries[index]
        
        del self.bitmaps[index]
        del self.bitmapsSrcEntries[index]

        ii = self.listCtrl.GetItem(index).GetImage()
        self.listCtrl.DeleteItem(index)
        
        newIdx = index+direction
        
        self.bitmaps.insert(newIdx, bmp)
        self.bitmapsSrcEntries.insert(newIdx, bmpSrc)
        
        self.addToListCtrl(newIdx, bmpSrc, bmp, ii)
        
        state = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        self.listCtrl.SetItemState(newIdx, state, state)

    def OnButtonMoveUpButton(self, event):
        if self.selection > 0:
            self.moveBitmap(self.selection, -1)
            
    def OnButtonMoveDownButton(self, event):
        if self.selection != -1 and self.selection < len(self.bitmaps)-1:
            self.moveBitmap(self.selection, 1)

            
