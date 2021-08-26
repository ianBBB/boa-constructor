#Boa:MiniFrame:ImageViewer

import wx
import os, tempfile

def create(parent):
    return ImageViewer(parent)

imgs = {'.bmp' : wx.BITMAP_TYPE_BMP,
        '.gif' : wx.BITMAP_TYPE_GIF,
        '.png' : wx.BITMAP_TYPE_PNG,
        '.jpg' : wx.BITMAP_TYPE_JPEG,
        '.ico' : wx.BITMAP_TYPE_ICO}

[wxID_IMAGEVIEWER, wxID_IMAGEVIEWERSASHWINDOW1, wxID_IMAGEVIEWERSTATICBITMAP1, 
] = [wx.NewId() for _init_ctrls in range(3)]

class ImageViewer(wx.MiniFrame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.MiniFrame.__init__(self, id=wxID_IMAGEVIEWER, name='ImageViewer',
              parent=prnt, pos=wx.Point(401, 286), size=wx.Size(127, 131),
              style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP,
              title='Image viewer')
        self.SetClientSize(wx.Size(119, 104))

        self.sashWindow1 = wx.SashWindow(id=wxID_IMAGEVIEWERSASHWINDOW1,
              name='sashWindow1', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(119, 104),
              style=wx.SW_BORDER | THICK_FRAME | wx.SW_3D)
        self.sashWindow1.SetExtraBorderSize(self.borderSize)
        self.sashWindow1.SetMinimumSizeX(24)
        self.sashWindow1.SetMinimumSizeY(24)
        self.sashWindow1.Bind(wx.EVT_SIZE, self.OnSashwindow1Size)

        self.staticBitmap1 = wx.StaticBitmap(bitmap=wx.NullBitmap,
              id=wxID_IMAGEVIEWERSTATICBITMAP1, name='staticBitmap1',
              parent=self.sashWindow1, pos=wx.Point(9, 9), size=wx.Size(101,
              86), style=0)

    def __init__(self, parent, doubleClickCallback=None):
        self.borderSize = 30
        self._init_ctrls(parent)
        self.Centre(wx.BOTH)

        if doubleClickCallback:
            self.staticBitmap1.Bind(wx.EVT_LEFT_DCLICK, doubleClickCallback)

    def showImage(self, filename, node = None):
        if node is not None:
            fn = tempfile.mktemp(os.path.splitext(node.name)[-1])
            open(fn, 'wb').write(node.load())
        else:
            fn = filename

        self.SetTitle('Image Viewer - %s' %(os.path.basename(fn)))
        try:
            ext = os.path.splitext(fn)[-1].lower()
            bmp = wx.Image(fn, imgs[ext]).ConvertToBitmap()
        except KeyError:
            wx.LogError('Unsupported extension: %s'%ext)
            return
        self.sashWindow1.SetClientSize(wx.Size(bmp.GetWidth()+self.borderSize*2,
                                              bmp.GetHeight()+self.borderSize*2))
        self.SetClientSize(self.sashWindow1.GetSize())
        self.staticBitmap1.SetBitmap(bmp)

        if node is not None:
            os.remove(fn)

        self.Centre(wx.BOTH)
        self.Show(True)

    def OnSashwindow1Size(self, event):
        self.sashWindow1.Refresh()
        #self.staticBitmap1.Refresh()
        event.Skip()


if __name__ == '__main__':
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = create(None)
    frame.Show(True)
    frame.showImage('../Images/Modules/wx.Frame.png')
    app.MainLoop()
