#-----------------------------------------------------------------------------
# Name:        FlexGridGrowableDlg.py
# Purpose:     Managing growable rows and columns for the wxFlexGridSizer
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:FlexGridGrowablesDlg

import wx
import wx.lib.buttons

from Utils import _

[wxID_FLEXGRIDGROWABLESDLG, wxID_FLEXGRIDGROWABLESDLGBUTTON1, 
 wxID_FLEXGRIDGROWABLESDLGBUTTON2, wxID_FLEXGRIDGROWABLESDLGBUTTON3, 
 wxID_FLEXGRIDGROWABLESDLGGRIDWIN, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(5)]

if wx.Platform == '__WXMAC__':
    ToggleButton = wx.lib.buttons.GenToggleButton
    EVT_TOGGLE = wx.EVT_BUTTON
else:
    ToggleButton = wx.ToggleButton
    EVT_TOGGLE = wx.EVT_TOGGLEBUTTON

class FlexGridGrowablesDlg(wx.Dialog):
    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        # parent.AddSizer(self.flex, 1, border=0, flag=wx.GROW | wx.ALL)        # orig
        # parent.AddSizer(self.boxSizer2, 0, border=0, flag=wx.ALIGN_RIGHT)     # orig

        parent.Add(self.flex, 1, border=0, flag=wx.GROW | wx.ALL)
        parent.Add(self.boxSizer2, 0, border=0, flag=wx.ALIGN_RIGHT)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        # parent.AddWindow(self.button3, 0, border=20,      # orig
        #       flag=wx.ALL | wx.ALIGN_RIGHT)
        # parent.AddWindow(self.button1, 0, border=20,
        #       flag=wx.RIGHT | wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT)
        # parent.AddWindow(self.button2, 0, border=20,
        #       flag=wx.RIGHT | wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT)

        parent.Add(self.button3, 0, border=20,
              flag=wx.ALL )
        parent.Add(self.button1, 0, border=20,
              flag=wx.RIGHT | wx.TOP | wx.BOTTOM)
        parent.Add(self.button2, 0, border=20,
              flag=wx.RIGHT | wx.TOP | wx.BOTTOM )
    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.flex = wx.FlexGridSizer(cols=self.numCols, hgap=0,
              rows=self.numRows, vgap=0)

        self.boxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_FLEXGRIDGROWABLESDLG,
              name='FlexGridGrowablesDlg', parent=prnt, pos=wx.Point(139, 88),
              size=wx.Size(435, 279),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title=_('Define Growable Rows and Columns (resize to test)'))
        self.SetClientSize(wx.Size(427, 252))
        self.Bind(wx.EVT_SIZE, self.OnFlexgridgrowablesdlgSize)

        self.button1 = wx.Button(id=wx.ID_OK, label=_('OK'), name='button1',
              parent=self, pos=wx.Point(237, 209), size=wx.Size(75, 23),
              style=0)

        self.button2 = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='button2', parent=self, pos=wx.Point(332, 209),
              size=wx.Size(75, 23), style=0)

        self.gridWin = wx.Window(id=wxID_FLEXGRIDGROWABLESDLGGRIDWIN,
              name='gridWin', parent=self, pos=wx.Point(32, 32),
              size=wx.Size(200, 100), style=0)
        self.gridWin.Bind(wx.EVT_PAINT, self.OnGridwinPaint)

        self.button3 = wx.Button(id=wxID_FLEXGRIDGROWABLESDLGBUTTON3,
              label=_('Editor'), name='button3', parent=self, pos=wx.Point(142,
              209), size=wx.Size(75, 23), style=0)
        self.button3.Enable(False)

        self._init_sizers()

    def __init__(self, parent, rows, cols):
        self.numRows = 4
        self.numRows = len(rows)+1
        self.numCols = 4
        self.numCols = len(cols)+1

        self._init_ctrls(parent)

        self.rows = rows
        self.cols = cols

        self.colIds = {}
        self.colBtns = []
        for idx, col in zip(range(len(cols)), cols):
            wid = wx.NewIdRef(count=1)
            tb = ToggleButton(self, wid, str(idx))
            if col: tb.SetValue(1)
            self.colIds[wid] = (idx, col)
            self.colBtns.append(tb)
            tb.Bind(EVT_TOGGLE, self.OnToggleCol, id=wid)

        self.rowIds = {}
        self.rowBtns = []
        for idx, row in zip(range(len(rows)), rows):
            wid =wx.NewIdRef(count=1)
            tb = ToggleButton(self, wid, str(idx))
            if row: tb.SetValue(1)
            self.rowIds[wid] = (idx, row)
            self.rowBtns.append(tb)
            tb.Bind(EVT_TOGGLE, self.OnToggleRow, id=wid)

        self.setupFlexSizer()

        if not rows or not cols:
            self.gridWin.Show(False)

        self.boxSizer1.Fit(self)

        # set current size as minimum size
        s = self.GetSize()
        self.SetSizeHints(s.width, s.height, -1, -1)
        wx.CallAfter(self.gridWin.Refresh)

    def OnToggleCol(self, event):
        idx, col = self.colIds[event.GetId()]
        self.cols[idx] = not col
        self.colIds[event.GetId()] = idx, not col

        self.setupFlexSizer()

    def OnToggleRow(self, event):
        idx, row = self.rowIds[event.GetId()]
        self.rows[idx] = not row
        self.rowIds[event.GetId()] = idx, not row

        self.setupFlexSizer()

    def OnFlexgridgrowablesdlgSize(self, event):
        if self.rows and self.cols:
            tlPos = self.colBtns[0].GetPosition()
            tlSize = self.colBtns[0].GetSize()
            trPos = self.colBtns[-1].GetPosition()
            trSize = self.colBtns[-1].GetSize()
            blPos = self.rowBtns[-1].GetPosition()
            blSize = self.rowBtns[-1].GetSize()
            self.gridWin.SetSize(tlPos.x, tlPos.y + tlSize.height,
                  trPos.x + trSize.width - tlPos.x,
                  blPos.y + blSize.height - tlSize.height)

        # let sizers update
        event.Skip()

    def OnGridwinPaint(self, event):
        dc = wx.PaintDC(self.gridWin)
        brush = wx.Brush(wx.WHITE)
        dc.SetBackground(brush)
        dc.Clear()
        dc.SetPen(wx.BLACK_PEN)

        w, h = self.gridWin.GetSize().Get()
        x = 0
        for vl in range(len(self.colBtns)):
            dc.DrawLine(x-1, 0, x-1, h)
            x += self.colBtns[vl].GetSize().width

        y = 0
        for hl in range(len(self.rowBtns)):
            dc.DrawLine(0, y-1, w, y-1)
            y += self.rowBtns[hl].GetSize().height

    def setupFlexSizer(self):
        self.boxSizer1.Remove(0)
        self.flex =wx.FlexGridSizer(cols=self.numCols, hgap=0,
              rows=self.numRows, vgap=0)
        self.boxSizer1.Insert(0, self.flex, 1, border=0, flag=wx.GROW | wx.ALL)

        rows, cols = self.rows, self.cols
        self.flex.Add(wx.Size(10, 10))
        for idx, col in zip(range(len(cols)), cols):
            self.flex.Add(self.colBtns[idx], 0, wx.GROW)
            if col:
                self.flex.AddGrowableCol(idx+1)

        for idx, row in zip(range(len(rows)), rows):
            self.flex.Add(self.rowBtns[idx], 0, wx.GROW)
            for s in range(len(cols)):
                self.flex.Add(wx.Size(10, 10))
            if row:
                self.flex.AddGrowableRow(idx+1)

        self.boxSizer1.Layout()
        # needed to repaint the custom drawn window
        wx.PostEvent(self, wx.SizeEvent(self.GetSize(), self.GetId()))

if __name__ == '__main__':
    app = wx.PySimpleApp()

    dlg = FlexGridGrowablesDlg(None, [1, 0], [1, 0, 0])
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
