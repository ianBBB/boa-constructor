#Boa:FramePanel:PathsPanel

import wx
import wx.grid

from Utils import _

[wxID_PATHSPANEL, wxID_PATHSPANELADD_BTN, wxID_PATHSPANELGRID, 
 wxID_PATHSPANELREMOVE_BTN, wxID_PATHSPANELSTATICBOX1, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(5)]

class PathsPanel(wx.Panel):
    def _init_coll_staticBoxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.grid, 1, border=8, flag=wx.ALL | wx.GROW)
        parent.Add(self.boxSizer1, 0, border=0, flag=wx.ALIGN_RIGHT)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        # parent.Add(self.add_btn, 0, border=8,
        #       flag=wx.ALL | wx.ALIGN_RIGHT)
        parent.Add(self.add_btn, 0, border=8,
              flag=wx.ALL)
        parent.Add(self.remove_btn, 0, border=8,
              flag=wx.BOTTOM | wx.TOP | wx.RIGHT)

    def _init_sizers(self):
        # generated method, don't edit
        self.staticBoxSizer1 = wx.StaticBoxSizer(box=self.staticBox1,
              orient=wx.VERTICAL)

        self.boxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_staticBoxSizer1_Items(self.staticBoxSizer1)
        self._init_coll_boxSizer1_Items(self.boxSizer1)

        self.SetSizer(self.staticBoxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PATHSPANEL, name='PathsPanel',
              parent=prnt, pos=wx.Point(316, 277), size=wx.Size(523, 274),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(515, 247))

        self.staticBox1 = wx.StaticBox(id=wxID_PATHSPANELSTATICBOX1,
              label=_('Server to client filepath mappings'), name='staticBox1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(515, 247), style=0)

        self.grid = wx.grid.Grid(id=wxID_PATHSPANELGRID, name='grid',
              parent=self, pos=wx.Point(13, 25), size=wx.Size(489, 169),
              style=wx.SUNKEN_BORDER)
        self.grid.SetDefaultRowSize(20)
        self.grid.SetColLabelSize(20)
        self.grid.SetRowLabelSize(0)

        self.add_btn = wx.Button(id=wxID_PATHSPANELADD_BTN, label=_('Add'),
              name='add_btn', parent=self, pos=wx.Point(344, 210),
              size=wx.Size(75, 24), style=0)
        self.add_btn.Bind(wx.EVT_BUTTON, self.OnAdd_btnButton,
              id=wxID_PATHSPANELADD_BTN)

        self.remove_btn = wx.Button(id=wxID_PATHSPANELREMOVE_BTN,
              label=_('Remove'), name='remove_btn', parent=self, pos=wx.Point(427,
              210), size=wx.Size(75, 24), style=0)
        self.remove_btn.Bind(wx.EVT_BUTTON, self.OnRemove_btnButton,
              id=wxID_PATHSPANELREMOVE_BTN)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)

        self.SetSize(pos.x, pos.y, size.x, size.y)

    def init_paths(self, paths):
        self.paths = paths
        numRows = len(self.paths)
        self.grid.CreateGrid(numRows, 2)
        self.grid.SetColLabelValue(0, _('Map server filenames starting with'))
        self.grid.SetColLabelValue(1, _('To client filenames starting with'))
        colWidth = self.grid.GetClientSize().x/2
        self.grid.SetColSize(0, colWidth)
        self.grid.SetColSize(1, colWidth)

        for row, (svr, clnt) in zip(range(numRows), self.paths):
            self.grid.SetCellValue(row, 0, svr)
            self.grid.SetCellValue(row, 1, clnt)
        self.grid.ForceRefresh()

    def read_paths(self):
        self.grid.SaveEditControlValue()
        return  [(self.grid.GetCellValue(row, 0), self.grid.GetCellValue(row, 1))
                 for row in range(self.grid.GetNumberRows())]

    def OnAdd_btnButton(self, event):
        self.grid.AppendRows(1)

    def OnRemove_btnButton(self, event):
        row = self.grid.GetGridCursorRow()
        if row != -1:
            self.grid.DeleteRows(row, 1)
