
import wx

class HelloFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)

        # create a panel in the frame
        pnl = wx.Panel(self)

        # put some text with a larger bold font on it
        st = wx.StaticText(pnl, label="Hello World!")
        # font = st.GetFont()
        # font.PointSize += 10
        # font = font.Bold()
        # st.SetFont(font)

# ######################################################
        import io

        def getZWData():
            return \
                '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x0b\x08\x02\
                \x00\x00\x00\xf9\x80\x9an\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\
                \x00\x01\x9aIDAT(\x91M\x91?h\x93q\x14E\xdf/\xfd\x9a\xf8\'\xd1I*\xd2R\x03u\
                \xa8\x82.N\x0e\x0eJ\x91\x12h\xc0\xa1B\x04\x11A\\\xd5\xb1\x82\x83\x93\xab:U7\
                \x87\x82"\x88]2hE\x85\xa0NE\x97L\x1d:\xb9X#1_\x93\xbc\xfb\xde\xbb\x0e5\x12\
                \xb8p\xcf|Njo\xb7\xe7\x97\xe7eI\xc4DB$Dl\xc4*b":\x06EI\xf9\x9f\xbc\xb4\xbf\
                \xb4\xda|0s\x1a\xce\x08z\xd0\x83\x164\x0f\xf3\x80\xd3<\xe0aF\xdc\xf9\xb8\x9e\
                \xf2<?0Y\xf2\x027\xde\xdeZX\xe83A\xc4I\x8cMI%\x91\xd2L\xb7\xdb\xccD\x84\x13\
                \x0f\xf3\x17\xe5\x8b\xcb\xabk\xf7n\\\x88A!)\xcd\x02\xa0)M\xc3@h\x18\xb2)\xb4\
                \x1fI\xd6}\xbcR\xa8\x1f\xaf\\\xf9\xf2\xfb\xe9\xaf\xc5\xe9\xe9\xd7_\xb7N\xf4s\
                \x07\x02 \xd4\xa1\xae\x08\xa8\x03\x07{X\x13I;\xad\x8dlk\xb3\xdc\xf8L\xda\xee\
                \xfb\xc6\xe4\xf9\xa5\xc5Z\r\xc3!\x00U\xd5\x7f\xa7\x00\xaa\xd5j\xab\xd5\xca\
                \xb2\x93g\xfd\xfb\x07\xd2v?\x1d.\x9c\xab\xbd\xbc^\x7frd\xe0@@\x03\x08(\r\x01\
                \r\xc3\xbe)\xbc\x13\xc9B\xe2\xd0\xcd\xfb\x11\xc13\x9d\xe7\xb7\x1b\x97&zYR\
                \x06B\xc0\xa4\x91\x10I\x99\xc0\x82\x15\x8b6\'\x92:\x9dN\xa5R\x19\x0ez\xebo\
                \xae^\xaew\x98)\xa9\x8c=9#K\x02\xa1\xa74\xb7\xf3\xf3[\xea\xf7\xfb\x03\x0c\
                \x9f5\xef\x1e=5RN\x8b\x80\x13\x16\x16\xfe\xbf\x89\x93\xbe\xf2j3m\xff\xd8\x9e\
                =6+\xd7Dz\xa3\xa8:\x8a=\xce{\xed\xcb\xf2\x17\xc6\xbc\\0\x92\xc2\xa7\xad\x00\
                \x00\x00\x00IEND\xaeB`\x82'
#
#         def getZWBitmap():
#             return wx.Bitmap(getZWImage())

        def getZWImage():
            stream = io.StringIO(getZWData())
            return wx.Image(stream,wx.BITMAP_TYPE_PNG)

# #############
#         my_image=


##############################################
        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        pnl.SetSizer(sizer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")


    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='Hello World 2')
    frm.Show()
    app.MainLoop()