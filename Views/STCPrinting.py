#-----------------------------------------------------------------------------
# Name:        STCPrinting.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2003/05/21
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007
# Licence:     wxWidgets
#-----------------------------------------------------------------------------
#Boa:Dialog:STCPrintDlg

"""
"""

# XXX Currently forces stc rendering not to wrap lines, currently the page
# XXX total calculations depend on exact number of lines

# XXX

import os

import wx
import wx.stc

from Utils import _

def create(parent):
    return STCPrintDlg(parent)

[wxID_STCPRINTDLG, wxID_STCPRINTDLGBTNCANCEL, wxID_STCPRINTDLGBTNPRINT, 
 wxID_STCPRINTDLGBTNPRINTPREVIEW, wxID_STCPRINTDLGBTNPRINTSETUP, 
 wxID_STCPRINTDLGCKBFILENAME, wxID_STCPRINTDLGCKBPAGENUMBERS, 
 wxID_STCPRINTDLGRDBCOLOURMODE, 
] = [wx.NewIdRef(count=1) for _init_ctrls in range(8)]

stcPrintColourModes = [0, wx.stc.STC_PRINT_BLACKONWHITE, 
                          wx.stc.STC_PRINT_COLOURONWHITE,
                          wx.stc.STC_PRINT_COLOURONWHITEDEFAULTBG]

class STCPrintDlg(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_STCPRINTDLG, name='STCPrintDlg',
              parent=prnt, pos=wx.Point(352, 204), size=wx.Size(402, 189),
              style=wx.DEFAULT_DIALOG_STYLE, title=_('Print Source'))
        self.SetClientSize(wx.Size(394, 162))

        # self.rdbColourMode = wx.RadioBox(choices=[_('Normal'), _('Black on white'),      #orig
        #       _('Colour on white'), _('Colour on white default background')],
        #       id=wxID_STCPRINTDLGRDBCOLOURMODE, label=_('Colour Mode'),
        #       majorDimension=1, name='rdbColourMode', parent=self,
        #       point=wx.Point(8, 8), size=wx.Size(216, 112),
        #       style=wx.RA_SPECIFY_COLS)

        self.rdbColourMode = wx.RadioBox(choices=[_('Normal'), _('Black on white'),
              _('Colour on white'), _('Colour on white default background')],
              id=wxID_STCPRINTDLGRDBCOLOURMODE, label=_('Colour Mode'),
              majorDimension=1, name='rdbColourMode', parent=self,
              pos=wx.Point(8, 8), size=wx.Size(216, 112),
              style=wx.RA_SPECIFY_COLS)


        self.ckbFilename = wx.CheckBox(id=wxID_STCPRINTDLGCKBFILENAME,
              label=_('Filename at top'), name='ckbFilename', parent=self,
              pos=wx.Point(240, 16), size=wx.Size(144, 13), style=0)
        self.ckbFilename.SetValue(True)

        self.ckbPageNumbers = wx.CheckBox(id=wxID_STCPRINTDLGCKBPAGENUMBERS,
              label=_('Page numbers'), name='ckbPageNumbers', parent=self,
              pos=wx.Point(240, 40), size=wx.Size(136, 13), style=0)
        self.ckbPageNumbers.SetValue(True)

        self.btnPrintSetup = wx.Button(id=wxID_STCPRINTDLGBTNPRINTSETUP,
              label=_('Print Setup'), name='btnPrintSetup', parent=self,
              pos=wx.Point(8, 128), size=wx.Size(88, 23), style=0)
        self.btnPrintSetup.Bind(wx.EVT_BUTTON, self.OnPrintSetup,
              id=wxID_STCPRINTDLGBTNPRINTSETUP)

        self.btnPrintPreview = wx.Button(id=wxID_STCPRINTDLGBTNPRINTPREVIEW,
              label=_('Print Preview'), name='btnPrintPreview', parent=self,
              pos=wx.Point(104, 128), size=wx.Size(88, 23), style=0)
        self.btnPrintPreview.Bind(wx.EVT_BUTTON, self.OnPrintPreview,
              id=wxID_STCPRINTDLGBTNPRINTPREVIEW)

        self.btnPrint = wx.Button(id=wxID_STCPRINTDLGBTNPRINT, label=_('Print'),
              name='btnPrint', parent=self, pos=wx.Point(200, 128),
              size=wx.Size(88, 23), style=0)
        self.btnPrint.Bind(wx.EVT_BUTTON, self.OnDoPrint,
              id=wxID_STCPRINTDLGBTNPRINT)

        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='btnCancel', parent=self, pos=wx.Point(296, 128),
              size=wx.Size(88, 23), style=0)

    def __init__(self, parent, stc, filename=''):
        self._init_ctrls(parent)

        self.stc = stc
        self.filename = filename
        self.parentFrame = parent
        self.preview = None

        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_LETTER)
        self.printData.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15,15), wx.Point(15,15))

        #self.printData.SetPaperId(wx.PAPER_LETTER)


    def OnPrintSetup(self, event):
        data = wx.PageSetupDialogData()
        data.SetPrintData(self.printData)

        data.SetDefaultMinMargins(True)
        data.SetMarginTopLeft(self.margins[0])
        data.SetMarginBottomRight(self.margins[1])

        dlg = wx.PageSetupDialog(self, data)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetPageSetupData()
                self.printData = wx.PrintData(data.GetPrintData()) 
                self.printData.SetPaperId(data.GetPaperId())
                self.margins = (data.GetMarginTopLeft(),
                                data.GetMarginBottomRight())
        finally:
            dlg.Destroy()

    def createSTCPrintout(self):
        colourMode = stcPrintColourModes[self.rdbColourMode.GetSelection()]
        doPageNums = self.ckbPageNumbers.GetValue()
        if self.ckbFilename.GetValue():
            filename = self.filename
        else:
            filename = ''

        return STCPrintout(self.stc, colourMode, filename, doPageNums)

    def OnPrintPreview(self, event):
        printout1 = self.createSTCPrintout()
        printout2 = self.createSTCPrintout()
        self.preview = wx.PrintPreview(printout1, printout2, self.printData)
        if not self.preview.IsOk():
            wx.LogError(_('An error occured while preparing preview.'))
            return

        frame = wx.PreviewFrame(self.preview, self.parentFrame, _('Print Preview'))
        frame.Initialize()
        frame.Show(True)


    def OnDoPrint(self, event):
        pdd = wx.PrintDialogData()
        pdd.SetPrintData(self.printData)
        printer = wx.Printer(pdd)
        printout = self.createSTCPrintout()

        if not printer.Print(self.parentFrame, printout):
            wx.LogError(_('An error occured while printing.'))
        else:
            self.printData = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
        printout.Destroy()

        self.EndModal(wx.OK)


#-------------------------------------------------------------------------------

class STCPrintout(wx.Printout):
    margin = 0.1
    linesPerPage = 69

    def __init__(self, stc, colourMode=0, filename='', doPageNums=1):
        wx.Printout.__init__(self)
        self.stc = stc
        self.colourMode = colourMode
        self.filename = filename
        self.doPageNums = doPageNums

        self.pageTotal, m = divmod(stc.GetLineCount(), self.linesPerPage)
        if m: self.pageTotal += 1

##    def OnBeginDocument(self, start, end):
##        return self.base_OnBeginDocument(start, end)
##
##    def OnEndDocument(self):
##        self.base_OnEndDocument()
##
##    def OnBeginPrinting(self):
##        self.base_OnBeginPrinting()
##
##    def OnEndPrinting(self):
##        self.base_OnEndPrinting()
##
##    def OnPreparePrinting(self):
##        self.base_OnPreparePrinting()

    def HasPage(self, page):
        if page <= self.pageTotal:
            return True
        else:
            return False

    def GetPageInfo(self):
        return (1, self.pageTotal, 1, 32000)

    def OnPrintPage(self, page):
        stc = self.stc
        self.stcLineHeight = stc.TextHeight(0)

        # calculate sizes including margin and scale
        dc = self.GetDC()
        # dw, dh = dc.GetSizeTuple()   # orig
        dw, dh = dc.GetSize()

        mw = self.margin*dw
        mh = self.margin*dh
        textAreaHeight = dh - mh*2
        textAreaWidth = dw - mw*2

        scale = float(textAreaHeight)/(self.stcLineHeight*self.linesPerPage)
        dc.SetUserScale(scale, scale)

        # render page titles and numbers
        f = dc.GetFont()
        f.SetFamily(wx.ROMAN)
        f.SetFaceName('Times New Roman')
        f.SetPointSize(f.GetPointSize()+3)
        dc.SetFont(f)

        if self.filename:
            tlw, tlh = dc.GetTextExtent(self.filename)
            dc.DrawText(self.filename,
                  int(dw/scale/2-tlw/2), int(mh/scale-tlh*3))

        if self.doPageNums:
            pageLabel = _('Page: %d') % page
            plw, plh = dc.GetTextExtent(pageLabel)
            dc.DrawText(pageLabel,
                  int(dw/scale/2-plw/2), int((textAreaHeight+mh)/scale+plh*2))

        # render stc into dc
        stcStartPos = stc.PositionFromLine((page-1)*self.linesPerPage)
        stcEndPos = stc.GetLineEndPosition(page*self.linesPerPage-1)

        maxWidth = 32000
        stc.SetPrintColourMode(self.colourMode)
        ep = stc.FormatRange(1, stcStartPos, stcEndPos, dc, dc,
                        wx.Rect(int(mw/scale), int(mh/scale),
                               maxWidth, int(textAreaHeight/scale)),
                        wx.Rect(0, (page-1)*self.linesPerPage*self.stcLineHeight,
                            maxWidth, self.stcLineHeight*self.linesPerPage))

        # warn when less characters than expected is rendered by the stc when
        # printing
        if not self.IsPreview():
            if ep < stcEndPos:
                print ('warning: on page %s: not enough chars rendered, diff:'%(page, stcEndPos-ep))

        return True


#----------------------------------------------------------------------

if __name__ == '__main__':
    testFile = 'STCPrinting.py'
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1, '')
    # prepare an stc
    frame.stc = wx.stc.StyledTextCtrl(frame, -1)
    frame.stc.SetText(open(testFile).read())
    config = os.path.abspath('../Config/stc-styles.rc.cfg')
    from STCStyleEditor import initSTC
    initSTC(frame.stc, config, 'python')
    # print dlg for prepared stc
    dlg = STCPrintDlg(frame, frame.stc, testFile)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    wx.CallAfter(frame.Destroy)
    app.MainLoop()
