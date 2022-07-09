#Boa:FramePanel:ImageEditorPanel

import os, math, tempfile
from cStringIO import StringIO

import wx
from wx.lib.anchors import LayoutAnchors

import Utils, Plugins, Models.ResourceSupport
from Utils import _

# draw destination consts
ddCanvas = 1
ddGrid = 2

[wxID_IMAGEEDITORPANEL, wxID_IMAGEEDITORPANELBGCOLBTN, 
 wxID_IMAGEEDITORPANELBRUSHCOLBTN, wxID_IMAGEEDITORPANELEDITWINDOW, 
 wxID_IMAGEEDITORPANELFGCOLBTN, wxID_IMAGEEDITORPANELMODECHOICE, 
 wxID_IMAGEEDITORPANELPENBRUSHWINDOW, wxID_IMAGEEDITORPANELSLIDER1, 
 wxID_IMAGEEDITORPANELSPINBUTTON1, wxID_IMAGEEDITORPANELSPINBUTTON2, 
 wxID_IMAGEEDITORPANELSPINBUTTON3, wxID_IMAGEEDITORPANELSTATICTEXT1, 
] = [wx.NewId() for _init_ctrls in range(12)]

class ImageEditorPanel(wx.Panel):
    def _init_utils(self):
        # generated method, don't edit
        self.cursorCross = wx.StockCursor(id=wx.CURSOR_CROSS)

        self.cursorMove = wx.StockCursor(id=wx.CURSOR_SIZING)

        self.cursorDraw = wx.StockCursor(id=wx.CURSOR_PENCIL)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_IMAGEEDITORPANEL,
              name='ImageEditorPanel', parent=prnt, pos=wx.Point(466, 318),
              size=wx.Size(586, 356),
              style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self._init_utils()
        self.SetAutoLayout(True)
        self.SetClientSize(wx.Size(578, 329))

        self.modeChoice = wx.Choice(choices=self.drawingModes,
              id=wxID_IMAGEEDITORPANELMODECHOICE, name='modeChoice',
              parent=self, pos=wx.Point(8, 7), size=wx.Size(64, 21), style=0)
        self.modeChoice.SetToolTipString(_('Current drawing mode'))
        self.modeChoice.Bind(wx.EVT_CHOICE, self.OnModeChoiceChoice,
              id=wxID_IMAGEEDITORPANELMODECHOICE)

        self.FGColBtn = wx.Button(id=wxID_IMAGEEDITORPANELFGCOLBTN, label='',
              name='FGColBtn', parent=self, pos=wx.Point(78, 5),
              size=wx.Size(24, 24), style=0)
        self.FGColBtn.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.FGColBtn.SetToolTipString(_('Pen colour'))
        self.FGColBtn.Bind(wx.EVT_BUTTON, self.OnFgcolbtnButton,
              id=wxID_IMAGEEDITORPANELFGCOLBTN)

        self.spinButton3 = wx.SpinButton(id=wxID_IMAGEEDITORPANELSPINBUTTON3,
              name='spinButton3', parent=self, pos=wx.Point(106, 5),
              size=wx.Size(16, 24), style=wx.SP_VERTICAL)
        self.spinButton3.SetRange(0, 32)
        self.spinButton3.SetToolTipString(_('Pen width'))
        self.spinButton3.Bind(wx.EVT_COMMAND_SCROLL,
              self.OnSpinbutton3CommandScroll,
              id=wxID_IMAGEEDITORPANELSPINBUTTON3)

        self.spinButton2 = wx.SpinButton(id=wxID_IMAGEEDITORPANELSPINBUTTON2,
              name='spinButton2', parent=self, pos=wx.Point(122, 5),
              size=wx.Size(16, 24), style=wx.SP_VERTICAL)
        self.spinButton2.SetRange(0, 11)
        self.spinButton2.SetToolTipString(_('Pen style'))
        self.spinButton2.Bind(wx.EVT_COMMAND_SCROLL,
              self.OnSpinbutton2CommandScroll,
              id=wxID_IMAGEEDITORPANELSPINBUTTON2)

        self.penBrushWindow = wx.Window(id=wxID_IMAGEEDITORPANELPENBRUSHWINDOW,
              name='penBrushWindow', parent=self, pos=wx.Point(137, 5),
              size=wx.Size(32, 24), style=wx.SUNKEN_BORDER)
        self.penBrushWindow.SetToolTipString(_('Pen / Brush preview'))
        self.penBrushWindow.Bind(wx.EVT_PAINT, self.OnPenBrushWindowPaint)

        self.spinButton1 = wx.SpinButton(id=wxID_IMAGEEDITORPANELSPINBUTTON1,
              name='spinButton1', parent=self, pos=wx.Point(168, 5),
              size=wx.Size(16, 24), style=wx.SP_VERTICAL)
        self.spinButton1.SetRange(0, 7)
        self.spinButton1.SetToolTipString(_('Brush style'))
        self.spinButton1.Bind(wx.EVT_COMMAND_SCROLL,
              self.OnSpinbutton1CommandScroll,
              id=wxID_IMAGEEDITORPANELSPINBUTTON1)

        self.brushColBtn = wx.Button(id=wxID_IMAGEEDITORPANELBRUSHCOLBTN,
              label='', name='brushColBtn', parent=self, pos=wx.Point(189, 5),
              size=wx.Size(24, 24), style=0)
        self.brushColBtn.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.brushColBtn.SetToolTipString(_('Brush colour'))
        self.brushColBtn.Bind(wx.EVT_BUTTON, self.OnBrushcolbtnButton,
              id=wxID_IMAGEEDITORPANELBRUSHCOLBTN)

        self.BGColBtn = wx.Button(id=wxID_IMAGEEDITORPANELBGCOLBTN, label='',
              name='BGColBtn', parent=self, pos=wx.Point(213, 5),
              size=wx.Size(24, 24), style=0)
        self.BGColBtn.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.BGColBtn.SetToolTipString(_('Background brush colour'))
        self.BGColBtn.Bind(wx.EVT_BUTTON, self.OnBgcolbtnButton,
              id=wxID_IMAGEEDITORPANELBGCOLBTN)

        self.slider1 = wx.Slider(id=wxID_IMAGEEDITORPANELSLIDER1, maxValue=25,
              minValue=1, name='slider1', parent=self, point=wx.Point(244, 5),
              size=wx.Size(108, 24), style=wx.SL_HORIZONTAL, value=16)
        self.slider1.SetToolTipString(_('Zoom factor'))
        self.slider1.Bind(wx.EVT_SCROLL, self.OnSlider1ScrollThumbtrack)

        self.editWindow = wx.ScrolledWindow(id=wxID_IMAGEEDITORPANELEDITWINDOW,
              name='editWindow', parent=self, pos=wx.Point(8, 34),
              size=wx.Size(561, 288), style=wx.SUNKEN_BORDER)
        self.editWindow.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.editWindow.SetConstraints(LayoutAnchors(self.editWindow, True,
              True, True, True))
        self.editWindow.Bind(wx.EVT_PAINT, self.OnEditWindowPaint)
        self.editWindow.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEditWindowEraseBackground)
        self.editWindow.Bind(wx.EVT_LEFT_DOWN, self.OnEditWindowLeftDown)
        self.editWindow.Bind(wx.EVT_LEFT_UP, self.OnEditWindowLeftUp)
        self.editWindow.Bind(wx.EVT_MOTION, self.OnEditWindowMotion)
        self.editWindow.Bind(wx.EVT_SCROLLWIN, self.OnEditWindowScroll)

        self.staticText1 = wx.StaticText(id=wxID_IMAGEEDITORPANELSTATICTEXT1,
              label=_('Image info'), name='staticText1', parent=self,
              pos=wx.Point(360, 2), size=wx.Size(208, 27),
              style=wx.ST_NO_AUTORESIZE)

    def __init__(self, parent):
        self.drawingModes = [_('Select'), _('Draw'), _('Line'), _('Circle'), _('Box'), _('Fill'), _('Colour')]
        self._init_ctrls(parent)

        self.currentCursor = None

        self.drawingMethMap = {_('Select'): (ddCanvas|ddGrid, self.drawSelection),
                               _('Draw')  : (ddCanvas,        self.drawPoint),
                               _('Line')  : (ddCanvas|ddGrid, self.drawLine),
                               _('Circle'): (ddCanvas|ddGrid, self.drawCircle),
                               _('Box')   : (ddCanvas|ddGrid, self.drawBox),
                               _('Fill')  : (ddCanvas,        self.drawFill),
                               _('Move')  : (ddCanvas|ddGrid, self.drawMove),
                               _('Colour'): (ddCanvas,        self.drawPickColour),
                              }

        self.mode = ''
        self.setMode(_('Draw'))

        self.mDC = self.bmp = None

        self.fgcol = wx.BLACK
        self.fgpen = wx.Pen(self.fgcol, 1, wx.SOLID)
        self.bgcol = wx.LIGHT_GREY
        self.bgbsh = wx.Brush(self.bgcol)
        self.brush = wx.Brush(wx.WHITE, wx.TRANSPARENT)
        self.invpen = wx.Pen(wx.BLUE, 0, wx.TRANSPARENT)
        self.selpen = wx.Pen(wx.WHITE, 2, wx.SOLID)

        self.x = self.y = 0

        self.modeChoice.SetSelection(1)

        self.offset = 0, 0

        self.prevSelRect = ()
        self.prevLineSeg = ()
        self.prevPointCol = ()


    brushStyles = [wx.TRANSPARENT, wx.SOLID, wx.BDIAGONAL_HATCH, wx.CROSSDIAG_HATCH,
                   wx.FDIAGONAL_HATCH, wx.CROSS_HATCH, wx.HORIZONTAL_HATCH,
                   wx.VERTICAL_HATCH]

    penStyles = [wx.SOLID, wx.TRANSPARENT, wx.DOT, wx.LONG_DASH, wx.SHORT_DASH, wx.DOT_DASH,
                 wx.BDIAGONAL_HATCH, wx.CROSSDIAG_HATCH, wx.FDIAGONAL_HATCH, wx.CROSS_HATCH,
                 wx.HORIZONTAL_HATCH, wx.VERTICAL_HATCH]

    extTypeMap = {'.bmp': wx.BITMAP_TYPE_BMP,
                  '.gif': wx.BITMAP_TYPE_GIF,
                  '.jpg': wx.BITMAP_TYPE_JPEG,
                  '.png': wx.BITMAP_TYPE_PNG,
                  '.ico': wx.BITMAP_TYPE_ICO,
                  }

#---Public methods--------------------------------------------------------------

    def initImageData(self, ext, data):
        """ Initialise editor with data """
        if data:
            # WAR: On Windows7 x64 with Aero disabled, Python 2.7 x64 and 
            #      wx-2.8-msw-unicode x64, SetUserScale fails when used on a DC 
            #      with a Bitmap selected coming from a BitmapFromImage
            #
            #      This is likely wxWidgets issue 3494 "wxDC::Blit ignores SetUserScale
            #      on source DC" [when a DIB is selected on the HDC]
            #      http://trac.wxwidgets.org/ticket/3494
            #
            #      To WAR this, create a new empty bitmap and blit to it from the 
            #      incoming DIB instead of selecting the incoming DIB onto the DC
            #      (another tested WAR is to use a colordepth of 16 in the 
            #       BitmapFromImage call, this probably causes the original 32-bit
            #       DIB to be exchanged by a color-converted BMP)
            bmp = wx.BitmapFromImage(wx.ImageFromStream(StringIO(data)))
            self.mDC, self.bmp = self.getTempMemDC(bmp.GetWidth(), bmp.GetHeight())
            self.mDC.DrawBitmap(bmp, 0, 0)
        else:
            self.mDC, self.bmp = self.getTempMemDC(16, 16)
            brush = wx.Brush(self.bgcol)
            self.mDC.SetBackground(brush)
            self.mDC.Clear()

        # Default back to png when opening data from source
        if ext == '.py':
            ext = '.png'

        self.imgExt = ext

        self.editWindow.Refresh()

        self.mDCundo, self.bmpundo = self.getTempMemDC(self.bmp.GetWidth(),
                                     self.bmp.GetHeight())
        self.selundo = None
        self.snapshot()

        self.updateScrollbars()
        self.updateImageInfo()

    def getImageData(self, ext=''):
        """ Returns the current bitmap data """
        if not ext:
            ext = self.imgExt

        fn = tempfile.mktemp()
        #if ext == '?': ext = '.png'
        tpe = self.extTypeMap[ext.lower()]
        self.bmp.SaveFile(fn, tpe)
        try:
            return open(fn, 'rb').read()
        finally:
            os.remove(fn)

    def imageModified(self):
        """ Called whenever image is modified, override to catch """
        pass

#---Utils-----------------------------------------------------------------------

    def setMode(self, mode, updateGUI=False):
        if self.mode != mode:
            if mode in (_('Draw'), _('Line'), _('Circle'), _('Box'), _('Fill')):
                self.currentCursor = self.cursorDraw
            else:
                self.currentCursor = self.cursorCross
            self.editWindow.SetCursor(self.currentCursor)

            self.clearState()

            self.mode = mode
            self.drawDest, self.drawMeth = self.drawingMethMap[self.mode]

            if updateGUI:
                self.modeChoice.SetStringSelection(mode)

    def clearState(self):
        self.dragoffset = self.dragpos = self.dragbmp = self.dragsrcrect = None
        self.sel = self.line = self.circle = self.box = None
        self.editWindow.SetCursor(self.currentCursor)

    def snapshot(self):
        self.mDC.SetUserScale(1.0, 1.0)
        self.mDCundo.Blit(0, 0, self.bmp.GetWidth(), self.bmp.GetHeight(),
              self.mDC, 0, 0)
        if self.sel: self.selundo = self.sel[:]
        else: self.selundo = None

    def getImgPos(self, event):
        x, y = event.GetPositionTuple()
        x, y = self.editWindow.CalcUnscrolledPosition(x, y)
        scale = self.slider1.GetValue()
        return ((x-self.offset[0]) / scale, (y-self.offset[1]) / scale)

    def getTempMemDC(self, width, height):
        bmp = wx.EmptyBitmap(width, height)
        memDC = wx.MemoryDC()
        memDC.SelectObject(bmp)
        return memDC, bmp

    def getSelBmp(self):
        if self.sel:
            x1, y1, x2, y2 = self.sel
            mDC, bmp = self.getTempMemDC(x2-x1+1, y2-y1+1)
            self.mDC.SetUserScale(1.0, 1.0)
            mDC.Blit(0, 0, x2-x1+1, y2-y1+1, self.mDC, x1, y1)
            mDC.SelectObject(wx.NullBitmap)
            return bmp
        return None

    def setMemDCBmp(self, bmp):
        if not bmp or not bmp.Ok():
            raise Exception, _('Invalid bitmap')
        self.mDC.SelectObject(wx.NullBitmap)
        self.bmp = bmp
        self.mDC.SelectObject(self.bmp)

    def updateScrollbars(self):
        scale = self.slider1.GetValue()
        xPos, yPos = self.editWindow.GetViewStart()
        self.editWindow.SetScrollbars(scale, scale,
              self.bmp.GetWidth(), self.bmp.GetHeight(), xPos, yPos)

    def updateImageInfo(self):
        if self.imgExt: ext = self.imgExt[1:].upper()
        else:           ext = 'UNKNOWN'

        w, h, d = self.bmp.GetWidth(), self.bmp.GetHeight(), self.bmp.GetDepth()

        msk = self.bmp.GetMask()
        if msk: m = 'Image is masked'
        else:   m = 'Image is not masked'

        if self.bmp.Ok(): x = ''
        else:             x = 'The bitmap is not valid!'

        text = '%s: (%s, %s), depth: %s\n%s. %s'%(ext, w, h, d, m, x)
        self.staticText1.SetLabel(text)

#---Drawing methods-------------------------------------------------------------

    def undo(self):
        self.mDC.SetUserScale(1.0, 1.0)
        self.mDC.Blit(0, 0, self.bmp.GetWidth(), self.bmp.GetHeight(),
              self.mDCundo, 0, 0)

    def drawSelection(self, event, state, dc=None):
        if not dc:
            if state == 'start':
                self.sel = self.getImgPos(event) * 2
            elif state in ('drag', 'end'):
                self.sel = self.sel[:2] + self.getImgPos(event)
                if state == 'end':
                    x1, y1, x2, y2 = self.sel
                    self.sel = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

            if self.sel != self.prevSelRect:
                if state == 'end':
                    self.prevSelRect = ()
                else:
                    self.prevSelRect = self.sel
                self.editWindow.Refresh()

        if dc and self.sel:
            x1, y1, x2, y2 = self.sel
            x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
            xoffset, yoffset = self.offset
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wx.XOR)
            dc.SetPen(self.selpen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(xoffset + x1 * scale - 1, yoffset + y1 * scale - 1,
                   (x2 - x1 + 1) * scale + 4, (y2 - y1 + 1) * scale + 4)

    def drawPoint(self, event, state):
        if state == 'start':
            self.snapshot()

        imgx, imgy = self.getImgPos(event)
        self.mDC.SetPen(self.fgpen)
        self.mDC.SetUserScale(1.0, 1.0)
        self.mDC.DrawPoint(imgx, imgy)
        self.editWindow.Refresh()

        if imgx >=0 and imgx < self.bmp.GetWidth() and \
           imgy >=0 and imgy < self.bmp.GetHeight():
            self.imageModified()

    def drawLine(self, event, state, dc=None):
        if not dc:
            if state == 'start':
                self.line = self.getImgPos(event) * 2
            elif self.line:
                self.line = self.line[:2] + self.getImgPos(event)
                if state == 'end':
                    self.snapshot()
                    self.mDC.SetLogicalFunction(wx.COPY)
                    self.mDC.SetPen(self.fgpen)
                    self.mDC.SetUserScale(1.0, 1.0)
                    self.mDC.DrawLine(*self.line)
                    self.mDC.DrawPoint(self.line[2], self.line[3])

                    x1, y1, x2, y2 = self.line
                    w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
                    if not ((x1 < 0 and x2 < 0) or (x1 >= w and x2 >= w) or \
                            (y1 < 0 and y2 < 0) or (y1 >= h and y2 >= h)):
                        self.imageModified()

                    self.line = None

            if self.prevLineSeg != self.line:
                if state == 'end':
                    self.prevLineSeg = ()
                else:
                    self.prevLineSeg = self.line

                self.editWindow.Refresh()

        if dc and self.line:
            x1, y1, x2, y2 = self.line
            xoffset, yoffset = self.offset
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wx.XOR)
            dc.SetPen(self.selpen)
            dc.DrawLine(xoffset + x1 * scale + scale/2, yoffset + y1 * scale + scale/2,
                        xoffset + x2 * scale + scale/2, yoffset + y2 * scale + scale/2)

    def drawBox(self, event, state, dc=None):
        if not dc:
            if state == 'start':
                self.box = self.getImgPos(event) * 2
            else:
                self.box = self.box[:2] + self.getImgPos(event)
                if state == 'end':
                    self.snapshot()
                    self.mDC.SetLogicalFunction(wx.COPY)
                    self.mDC.SetPen(self.fgpen)
                    self.mDC.SetUserScale(1.0, 1.0)
                    self.mDC.SetBrush(self.brush)
                    x1, y1, x2, y2 = self.box
                    self.mDC.DrawRectangle(x1, y1, x2-x1+1, y2-y1+1)
                    self.editWindow.Refresh()

                    x1, y1, x2, y2 = self.box
                    w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
                    if not ((x1 < 0 and x2 < 0) or (x1 >= w and x2 >= w) or \
                            (y1 < 0 and y2 < 0) or (y1 >= h and y2 >= h)):
                        self.imageModified()

                    self.box = None

            self.editWindow.Refresh()

        if dc and self.box:
            x1, y1, x2, y2 = self.box
            xoffset, yoffset = self.offset
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wx.XOR)
            dc.SetPen(self.selpen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(xoffset + x1 * scale - 1, yoffset + y1 * scale - 1,
                       (x2 - x1 + 1) * scale + 4, (y2 - y1 + 1) * scale + 4)

    def drawCircle(self, event, state, dc=None):
        if not dc:
            if state == 'start':
                self.circle = self.getImgPos(event) + (0,)
            elif state in ('drag', 'end') and self.circle:
                x1, y1, x2, y2 = self.circle[:2] + self.getImgPos(event)
                rad = math.sqrt(pow(x2-x1, 2) + pow(y2-y1, 2)) + 0.5
                self.circle = (x1, y1, rad)
                if state == 'end':
                    self.snapshot()
                    self.mDC.SetLogicalFunction(wx.COPY)
                    self.mDC.SetPen(self.fgpen)
                    self.mDC.SetUserScale(1.0, 1.0)
                    self.mDC.SetBrush(self.brush)
                    self.mDC.DrawEllipse(int(x1-rad+0.5), int(y1-rad+0.5),
                                         int(rad*2), int(rad*2))

                    x, y, rad = self.circle
                    x1, y1 = x-rad+0.5, y-rad+0.5
                    x2, y2 = x1 +rad*2, y1 +rad*2
                    w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
                    if not ((x1 < 0 and x2 < 0) or (x1 >= w and x2 >= w) or \
                            (y1 < 0 and y2 < 0) or (y1 >= h and y2 >= h)):
                        self.imageModified()

                    self.circle = None

            self.editWindow.Refresh()

        if dc and self.circle:
            x, y, rad = self.circle
            xoffset, yoffset = self.offset
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wx.XOR)
            dc.SetPen(self.selpen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawEllipse(int(xoffset + (x-rad+0.5) * scale),
                           int(yoffset + (y-rad+0.5) * scale),
                           int(rad*scale*2), int(rad*scale*2))

    def drawFill(self, event, state):
        self.snapshot()
        x, y = self.getImgPos(event)
        brush = wx.Brush(self.fgcol)
        self.mDC.SetBrush(brush)
        self.mDC.SetUserScale(1.0, 1.0)
        self.mDC.FloodFill(x, y, self.mDC.GetPixel(x, y))
        self.editWindow.Refresh()

        if x >=0 and x < self.bmp.GetWidth() and \
           y >=0 and y < self.bmp.GetHeight():
            self.imageModified()

    def drawMove(self, event, state, dc=None):
        x1, y1, x2, y2 = self.sel
        if not dc:
            x, y = self.getImgPos(event)
            if state == 'start':
                self.dragoffset = (x1 - x, y1 - y)
                if not self.dragbmp:
                    self.snapshot()
                    self.dragbmp = self.getSelBmp()
                    self.dragsrcrect = x1, y1, x2-x1+1, y2-y1+1
            elif state in ('drag', 'end'):
                # better to only do this once
                self.undo()

                dox, doy = self.dragoffset
                dx, dy = self.dragpos = dox + x, doy + y

                self.mDC.SetUserScale(1.0, 1.0)
                self.mDC.SetLogicalFunction(wx.COPY)
                self.mDC.SetPen(self.invpen)
                self.mDC.SetBrush(self.bgbsh)
                self.mDC.DrawRectangle(*self.dragsrcrect)

                self.mDC.DrawBitmap(self.dragbmp, dx, dy)

                if state == 'end':
                    self.sel = dx, dy, dx + x2-x1, dy + y2-y1

                self.editWindow.Refresh()

                self.imageModified()

        if dc and self.sel and self.dragpos:
            xoffset, yoffset = self.offset
            dx, dy = self.dragpos
            scale = self.slider1.GetValue()
            dc.SetLogicalFunction(wx.XOR)
            dc.SetPen(self.selpen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(xoffset + dx * scale - 1, yoffset + dy * scale - 1,
                       (x2 - x1 + 1) * scale + 4, (y2 - y1 + 1) * scale + 4)

    def drawPickColour(self, event, state):
        if state == 'end':
            x, y = self.getImgPos(event)
            newcol = self.mDC.GetPixel(x, y)

            self.fgcol = newcol
            self.fgpen.SetColour(newcol)
            self.FGColBtn.SetBackgroundColour(self.fgcol)

            self.setMode('Draw', updateGUI=True)

    def drawGrid(self, dc):
        pen = wx.Pen(wx.WHITE)
        dc.SetPen(pen)
        dc.SetLogicalFunction(wx.XOR)
        scale = self.slider1.GetValue()
        lines = []
        height = self.bmp.GetHeight()
        width = self.bmp.GetWidth()
        xoffset, yoffset = self.offset
        for y in range(height):
            lines.append( (xoffset, y * scale + yoffset,
                           width * scale + xoffset, y * scale + yoffset) )
        for x in range(width):
            lines.append( (x * scale + xoffset, yoffset,
                           x * scale + xoffset, height * scale + yoffset) )

        dc.DrawLineList(lines)

#---View control events---------------------------------------------------------

    def OnEditWindowEraseBackground(self, event):

        # Prevent erasing the background to avoid flicker, the background will
        # be cleared in OnEditWindowPaint
        pass

    def OnEditWindowPaint(self, event):

        # Double buffer the DC in OSs that require it to avoid flicker
        # Another option would be to only clear to background the parts of the
        # window that won't be covered by the bitmap (drawing the grid on top
        # will still flicker, though)
        dc = wx.AutoBufferedPaintDC(self.editWindow)

        self.editWindow.PrepareDC(dc)

        if not self.mDC or not self.bmp:
            return

        dc.BeginDrawing()
        try:
            scale = self.slider1.GetValue()
            self.mDC.SetUserScale(1.0/scale, 1.0/scale)
            width = self.bmp.GetWidth()*scale
            height = self.bmp.GetHeight()*scale
            xoffset = max((self.editWindow.GetSize().x - width) / 2, 0)
            yoffset = max((self.editWindow.GetSize().y - height) / 2, 0)
            dc.Clear()
            dc.Blit(xoffset, yoffset, width, height, self.mDC, 0, 0)
            self.mDC.SetUserScale(1.0, 1.0)
            self.offset = xoffset, yoffset
            if scale > 5:
                self.drawGrid(dc)
                framesize = 3
            else:
                framesize = 1

            dc.SetLogicalFunction(wx.COPY)
            pen = wx.Pen(wx.BLACK, framesize, wx.SOLID)
            dc.SetPen(pen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(xoffset-1 , yoffset-1, width+2, height+2)

            if (self.drawDest & ddGrid) and self.drawMeth:
                self.drawMeth(None, '', dc)
        finally:
            dc.EndDrawing()

    def OnPenBrushWindowPaint(self, event):
        dc = wx.PaintDC(self.penBrushWindow)
        dc.SetBrush(self.brush)
        dc.SetBackground(self.bgbsh)
        dc.SetPen(self.invpen)
        dc.BeginDrawing()
        try:
            cs = self.penBrushWindow.GetClientSize()
            dc.DrawRectangle(0, 0, cs.x, cs.y)
            dc.SetPen(self.fgpen)
            dc.DrawRectangle(cs.x/3-3, cs.y/3-3, cs.x/3+8, cs.y/3+6)
        finally:
            dc.EndDrawing()

    def OnEditWindowLeftDown(self, event):
        self.editWindow.CaptureMouse()

        if self.mode == _('Select') and self.sel:
            x1, y1, x2, y2 = self.sel
            x, y = self.getImgPos(event)
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                self.setMode(_('Move'))
                self.sel = x1, y1, x2, y2
        elif self.mode == _('Move') and self.sel:
            x1, y1, x2, y2 = self.sel
            x, y = self.getImgPos(event)
            if not (x >= x1 and x <= x2 and y >= y1 and y <= y2):
                self.setMode(_('Select'))
                self.sel = x1, y1, x2, y2

        if (self.drawDest & ddCanvas) and self.drawMeth:
            self.drawMeth(event, 'start')

    def OnEditWindowLeftUp(self, event):
        if self.editWindow.HasCapture():
            self.editWindow.ReleaseMouse()
            if (self.drawDest & ddCanvas) and self.drawMeth:
                self.drawMeth(event, 'end')

    def OnEditWindowMotion(self, event):
        if event.Dragging() and event.LeftIsDown():
            if (self.drawDest & ddCanvas) and self.drawMeth:
                self.drawMeth(event, 'drag')

        if self.sel and not event.Dragging() and not event.LeftIsDown():
            x1, y1, x2, y2 = self.sel
            x, y = self.getImgPos(event)
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                self.editWindow.SetCursor(self.cursorMove)
            else:
                self.editWindow.SetCursor(self.currentCursor)

    def OnSlider1ScrollThumbtrack(self, event):
        self.updateScrollbars()
        self.editWindow.Refresh()

    def showColDlg(self, col):
        data = wxStdColourData(col)
        dlg = wx.ColourDialog(self, data)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetColourData().GetColour()
            return None
        finally:
            dlg.Destroy()

    def OnFgcolbtnButton(self, event):
        newcol = self.showColDlg(self.fgcol)

        if newcol:
            self.fgcol = newcol
            self.fgpen.SetColour(newcol)
            self.FGColBtn.SetBackgroundColour(self.fgcol)
            self.penBrushWindow.Refresh()

    def OnBgcolbtnButton(self, event):
        newcol = self.showColDlg(self.bgcol)

        if newcol:
            self.bgcol = newcol
            self.bgbsh.SetColour(newcol)
            self.BGColBtn.SetBackgroundColour(self.bgcol)
            self.penBrushWindow.Refresh()

    def OnBrushcolbtnButton(self, event):
        newcol = self.showColDlg(self.brush.GetColour())

        if newcol:
            self.brush.SetColour(newcol)
            self.brushColBtn.SetBackgroundColour(newcol)
            self.penBrushWindow.Refresh()

    def OnModeChoiceChoice(self, event):
        self.setMode(self.modeChoice.GetStringSelection())
        self.editWindow.Refresh()

    def OnEditWindowScroll(self, event):
        event.Skip()
        self.editWindow.Refresh()

    def OnSpinbutton1CommandScroll(self, event):
        self.brush.SetStyle(self.brushStyles[self.spinButton1.GetValue()])
        self.penBrushWindow.Refresh()

    def OnSpinbutton2CommandScroll(self, event):
        self.fgpen.SetStyle(self.penStyles[self.spinButton2.GetValue()])
        self.penBrushWindow.Refresh()

    def OnSpinbutton3CommandScroll(self, event):
        self.fgpen.SetWidth(self.spinButton3.GetValue())
        self.penBrushWindow.Refresh()

#---View action events----------------------------------------------------------

    def OnCopy(self, event):
        clip = wx.TheClipboard
        clip.Open()
        try:
            bmp = self.getSelBmp()
            clip.SetData(wx.BitmapDataObject(bmp))
        finally:
            clip.Close()

    def OnPaste(self, event):
        clip = wx.TheClipboard
        clip.Open()
        try:
            data = wx.BitmapDataObject()
            try:
                clip.GetData(data)
            except:
                wx.LogError(_('Not a picture'))
            else:
                self.modeChoice.SetSelection(0)
                self.setMode('Move')
                self.snapshot()
                self.dragbmp = data.GetBitmap()
                self.dragsrcrect = -1, -1, 0, 0
                self.dragpos = 0, 0
                self.sel = 0, 0, self.dragbmp.GetWidth()-1, self.dragbmp.GetHeight()-1
                self.mDC.DrawBitmap(self.dragbmp, 0, 0)
                self.editWindow.Refresh()

                self.imageModified()
        finally:
            clip.Close()

    def OnUndo(self, event):
        self.undo()

        self.editWindow.Refresh()
        self.updateImageInfo()

    def OnClear(self, event):
        self.snapshot()
        if self.sel:
            x1, y1, x2, y2 = self.sel
            self.mDC.SetClippingRegion(x1, y1, x2-x1, y2-y1)
            self.mDC.Clear()
            self.mDC.DestroyClippingRegion()
        else:
            self.mDC.Clear()

        self.editWindow.Refresh()
        self.imageModified()

    def OnSetTransparentMask(self, event):
        self.mDC.SelectObject(wx.NullBitmap)
        self.bmp.SetMask(wx.Mask(self.bmp, self.fgcol))
        self.mDC.SelectObject(self.bmp)

        self.updateImageInfo()
        self.imageModified()

    def OnClearTransparentMask(self, event):
        self.mDC.SelectObject(wx.NullBitmap)
        self.bmp.SetMask(None)
        self.mDC.SelectObject(self.bmp)

        self.updateImageInfo()
        self.imageModified()

    def OnResize(self, event):
        dlg = wx.TextEntryDialog(self, _('Enter a tuple for the new size'),
              _('Resize'), '%s, %s'%(self.bmp.GetWidth(), self.bmp.GetHeight()))
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            width, height = eval(dlg.GetValue())
        finally:
            dlg.Destroy()

        # Create new bitmap of required size and copy current one to it
        mDC, bmp = self.getTempMemDC(width, height)
        mDC.Blit(0, 0, self.bmp.GetWidth(), self.bmp.GetHeight(),
                 self.mDC, 0, 0)
        mDC.SelectObject(wx.NullBitmap)

        self.setMemDCBmp(bmp)

        self.editWindow.Refresh()
        self.updateImageInfo()
        self.imageModified()

    def OnScale(self, event):
        dlg = wx.TextEntryDialog(self, _('Enter a tuple for the new size'),
              _('Scale'), '%s, %s'%(self.bmp.GetWidth(), self.bmp.GetHeight()))
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            width1, height1 = self.bmp.GetWidth(), self.bmp.GetHeight()
            width2, height2 = eval(dlg.GetValue())
        finally:
            dlg.Destroy()

        # draw a new version of the current bmp scaled to the user requested size
        xScale, yScale = float(width2)/width1, float(height2)/height1
        self.mDC.SetUserScale(1/xScale, 1/yScale)
        width, height = self.bmp.GetWidth()*xScale, self.bmp.GetHeight()*yScale
        mDC, bmp = self.getTempMemDC(width, height)
        mDC.Blit(0, 0, width, height, self.mDC, 0, 0)
        mDC.SelectObject(wx.NullBitmap)

        self.mDC.SetUserScale(1.0, 1.0)
        self.setMemDCBmp(bmp)

        self.editWindow.Refresh()
        self.updateImageInfo()
        self.imageModified()

    def OnCrop(self, event):
        self.setMemDCBmp(self.getSelBmp())

        self.clearState()

        self.editWindow.Refresh()
        self.updateImageInfo()
        self.imageModified()


class wxStdColourData(wx.ColourData):
    stdcolours = [(0, 0, 0), (128, 128, 128), (128, 0, 0), (128, 128, 0),
                  (0, 128, 0), (0, 128, 128), (0, 0, 128), (128, 0, 128),
                  (255, 255, 255), (192, 192, 192), (255, 0, 0), (255, 255, 0),
                  (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]

    def __init__(self, col=None):
        wx.ColourData.__init__(self)
        if col: self.SetColour(col)

        i = 0
        for r, g, b in self.stdcolours:
            self.SetCustomColour(i, wx.Colour(r, g, b))
            i = i + 1

#-Tester------------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1, 'Image Edit Test')
    panel = ImageEditorPanel(frame)
    frame.Show(True)
    panel.initImageData('.png', open('Images/Modules/Pyrex.png', 'rb').read())
    app.MainLoop()
    import sys
    sys.exit()

#-------------------------------------------------------------------------------

import Preferences

from Models import EditorModels, Controllers, EditorHelper
from Views import EditorViews

class ImageView(wx.Panel, EditorViews.EditorView):
    viewName = 'View'
    viewTitle = 'View'
    def __init__(self, parent, model):
        wx.Panel.__init__(self, parent, -1, style= wx.SUNKEN_BORDER)
        self.staticBitmapSmall = wx.StaticBitmap(self, -1, wx.NullBitmap)
        #self.staticBitmapBig = wx.StaticBitmap(self, -1, wx.NullBitmap)
        EditorViews.EditorView.__init__(self, model, (), -1)
        self.active = True

    imgsep = 16
    def refreshCtrl(self):
        if self.model.data:
            sio = StringIO(self.model.data)
            bmp = wx.BitmapFromImage(wx.ImageFromStream(sio))
            self.staticBitmapSmall.SetBitmap(bmp)
            self.staticBitmapSmall.SetDimensions(self.imgsep, self.imgsep,
                                                 bmp.GetWidth(), bmp.GetHeight())
            self.staticBitmapSmall.Refresh()                                     
            #self.staticBitmapBig.SetBitmap(bmp)
            #self.staticBitmapBig.SetDimensions(bmp.GetWidth()+self.imgsep*2,
            #      self.imgsep, bmp.GetWidth()*2, bmp.GetHeight()*2)

class ImageEditorView(ImageEditorPanel, EditorViews.EditorView):
    viewName = 'Edit'
    viewTitle = _('Edit')

    refreshBmp = 'Images/Editor/Refresh.png'
    copyBmp = 'Images/Shared/Copy.png'
    pasteBmp = 'Images/Shared/Paste.png'
    undoBmp = 'Images/Shared/Undo.png'
    def __init__(self, parent, model, actions=()):
        ImageEditorPanel.__init__(self, parent)
        EditorViews.EditorView.__init__(self, model, (
          (_('Refresh'), self.OnRefresh, self.refreshBmp, ''),
          ('-', None, '-', ''),
          (_('Copy'), self.OnCopy, self.copyBmp, ''),
          (_('Paste'), self.OnPaste, self.pasteBmp, ''),
          (_('Undo last change'), self.OnUndo, self.undoBmp, ''),
          (_('Undo view changes'), self.OnUndoViewChanges, '-', ''),
          (_('Clear'), self.OnClear, '-', ''),
          ('-', None, '-', ''),
          (_('Crop'), self.OnCrop, '-', ''),
          (_('Resize...'), self.OnResize, '-', ''),
          (_('Scale...'), self.OnScale, '-', ''),
          ('-', None, '-', ''),
          (_('Use current colour to set transparent mask'), self.OnSetTransparentMask, '-', ''),
          (_('Clear current transparent mask'), self.OnClearTransparentMask, '-', ''),
          ('-', None, '-', ''),
        ) + actions, -1)

        self.editWindow.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.editWindow.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

        self.active = True
        self.subImage = None

    def refreshCtrl(self, subImage=None):
        if subImage is None and self.subImage is None:
            data = self.model.data
        else:
            if not self.subImage:
                self.subImage = subImage
            data = self.subImage['data']

        ext = os.path.splitext(self.model.filename)[-1]

        self.initImageData(ext, data)
        self.editWindow.Refresh()

        self.modified = False
        self.updateViewState()

    def refreshModel(self):
        ext = os.path.splitext(self.model.filename)[-1]
        if ext == '.py':
            ext = '.png'

        data = self.getImageData(ext)

        if self.subImage:
            modelData = self.subImage['data']
        else:
            modelData = self.model.data

        if modelData != data:
            if self.subImage:
                self.model.updateData(data, self.subImage)
            else:
                self.model.data = data
                self.model.modified = True

        if self.model.viewsModified.count(self.viewName):
            self.model.viewsModified.remove(self.viewName)
        self.modified = False
        EditorViews.EditorView.refreshModel(self)

        self.updateEditor()
        self.updateViewState()

    def imageModified(self):
        self.modified = True
        self.updateViewState()

    def OnRefresh(self, event):
        self.refreshModel()

    def OnUndoViewChanges(self, event):
        self.refreshCtrl()


class BitmapEditorFileController(Controllers.PersistentController):
    Model = EditorModels.BitmapFileModel
    DefaultViews    = [ImageView]
    AdditionalViews = [ImageEditorView]

    editBmpBmp = 'Images/EditBitmap.png'
    conv2ModBmp = 'Images/Modules/PyResBitmap.png'

    def actions(self, model):
        return Controllers.PersistentController.actions(self, model) + [
              ('-', None, '-', ''),
              (_('Edit image'), self.OnGotoEditView, self.editBmpBmp, ''),
              (_('Convert to module'), self.OnConvertToModule, self.conv2ModBmp, ''),]

    def OnGotoEditView(self, event):
        model = self.getModel()
        if not model.views.has_key('Edit'):
            modPge = self.editor.getActiveModulePage()
            for View, wid in modPge.adtViews:
                if View == ImageEditorView:
                    self.editor.mainMenu.Check(wid, True)
                    break
            view = modPge.addView(ImageEditorView)
            view.refreshCtrl()
        else:
            view = model.views['Edit']
        view.focus()

    def OnConvertToModule(self, event):
        model = self.getModel()
        imgPath = model.localFilename()
        Models.ResourceSupport.ConvertImgToPy(imgPath, self.editor)


class CloseableImageEditorView(ImageEditorView, EditorViews.CloseableViewMix):
    def __init__(self, parent, model):
        EditorViews.CloseableViewMix.__init__(self, 'image editor')
        ImageEditorView.__init__(self, parent, model, self.closingActionItems)


from Models import ResourceSupport

class PyResourceImagesViewPlugin:
    editImgBmp = 'Images/EditBitmap.png'

    def __init__(self, model, view, actions):
        self.model = model
        self.view = view
        actions.extend( (
              (_('Edit image'), self.OnEditImage, self.editImgBmp, ''),
        ) )

    def OnEditImage(self, event):
        if self.view.selected != -1:
            name, (dataStartLn, bmpStartLine), zipped, icon = \
                  self.view.imageSrcInfo[self.view.selected]
            viewName = ResourceSupport.PyResourceImagesView.viewName
            if name:
                viewName += ':'+name

            if not self.model.views.has_key(viewName):
                modPge = self.model.editor.getActiveModulePage()
                view = modPge.addView(CloseableImageEditorView, viewName)
                view.tabName = view.viewName = viewName
                data = self.view.functions.imageFunctions['get%sData'%name]()
                subImage = {'data': data, 'name': name, 'start': dataStartLn+1,
                            'end': bmpStartLine-2, 'zip': zipped,
                            'icon': icon, 'cat': self.view.cataloged,
                            'eol': self.view.eol}
                view.refreshCtrl(subImage)
            else:
                view = self.model.views[viewName]
            view.focus()

ResourceSupport.PyResourceImagesView.plugins += (PyResourceImagesViewPlugin,)

#-------------------------------------------------------------------------------

Plugins.registerFileType(BitmapEditorFileController)

#-------------------------------------------------------------------------------
#Boa:PyImgResource:EditBitmap
def getEditBitmapData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00\x91IDATx\x9c\xa5\x92\xbb\x11\xc30\x0c\xc5\xc0\xa4Q\xa9Q=\x02\xbd\
\x81F\xcaHo\x03\xa6\x89e\xe9\xf2\xa3\xce\xecX\x00\x07\x9dh\xb5V\xae\xccm\x15\
\xd8\xb6-\xc6\xddV\n$E\x00\x06\xd4Zm\xa9\xe0\x80\x01|(I\x15H\x8a\x88\xc0\xcc\
\xf0\x97\xe0(\xb8\x97RR0\x18f\xe0\x8f\x13\xfe\xfb\x84\x11\xdewp\x9f\xe1\x9f\
\x82\x0c\xfcU\x90\x85?\nV\xe07\xc1*<\t\xfa\xbfZ\x1e\x86\xe1\x0e$M\'\x9a\x81{\
\xc1x\xdf\xee\x9e\x86{\x81\xa4pwZkip\x12\\\x99\'\xc3{a\x05\x01 \x1c\xda\x00\
\x00\x00\x00IEND\xaeB`\x82'

def getBitmapData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\
\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x01\x18IDATH\x89\xdd\x95MR\xc4 \x10\x85_3s))g!\xd7"\xc1Q\xe4dI\x85K\xe9\xb4\
\x8b\xc4a(~u\xccB\xbb*\x8b\x00\xf5\xbe\xee\xe6\x01D\xe2\x80=C\xec\xaa\xfe/\
\x00\xc7\xdc\xa0=\xbfp\xaf\xc0x~\xa6o\x03\x00@\x8f\xba)\xeeg\x0f\x00\\\x83\
\xdc\xdd"=\xeaj\xc5\xc5\nr\xe1(Nt\x88\xa7\x99\xc4!\xa9\xa4\x1b\xe0\xac\x03^\
\xdf\xc2\x80\x19\xc0\xbc&\xeeg\x0fy\x92\xe0\xcb;\x938F\x90n\x806q\xbe.Y\x91\
\xefR\x13@6$Tj\xb4<=\x14\xb1U\x00Y\x02\x8f\xc0\x17\x82L\n\t\xdb\xe2@"uS\xd3E\
%\xff\xa9i\x89\xc4\x93-\xef\x05$\xc1\x0c0C>\x86\xb6,\x93*.\xaf\x02x\xe4\xb5\
\x04\x02`pu\x8d\xb3n\xeb\x8d\x03s\xfd@6+`\xe6\xf5\x03\x00"8\xeb\xa0\x9e\xd46\
\xd7>\xedm\x9bn\x8d\xbe\xfa\xc3\x0c\x90\x08\xd5\xdc\x05\xb8=\xb9\xfaF\xb0\
\x9dw\x07\xc0\xcf\x1ejZ\xa2\xff\x9f\x04\xe5\x9eL\xbe|t_\xd7\x91X\xe6.\xca\
\x02~3\xfe\xfe\x93\xb9;\xe0\x13]\x82[\x14\xe0\xb9\xd5\x88\x00\x00\x00\x00IEN\
D\xaeB`\x82' 

Preferences.IS.registerImage('Images/EditBitmap.png', getEditBitmapData())
Preferences.IS.registerImage('Images/Palette/Bitmap.png', getBitmapData())
