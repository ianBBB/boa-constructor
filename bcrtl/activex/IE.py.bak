import wx
from wx.lib.activexwrapper import MakeActiveXClass
import win32com.client.gencache

try:
    IEModule = win32com.client.gencache.EnsureModule(
          '{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 0x0, 1, 1)
except Exception, error:
    raise ImportError, error

defaultNamedNotOptArg = IEModule.defaultNamedNotOptArg

[wxEVT_CWB_BEFORENAVIGATE, wxEVT_CWB_TITLECHANGE, wxEVT_CWB_DOWNLOADBEGIN,
 wxEVT_CWB_PROPERTYCHANGE, wxEVT_CWB_COMMANDSTATECHANGE,
 wxEVT_CWB_FRAMEBEFORENAVIGATE, wxEVT_CWB_WINDOWACTIVATE, wxEVT_CWB_NEWWINDOW,
 wxEVT_CWB_DOWNLOADCOMPLETE, wxEVT_CWB_WINDOWRESIZE, wxEVT_CWB_WINDOWMOVE,
 wxEVT_CWB_PROGRESSCHANGE, wxEVT_CWB_FRAMENEWWINDOW, wxEVT_CWB_STATUSTEXTCHANGE,
 wxEVT_CWB_FRAMENAVIGATECOMPLETE, wxEVT_CWB_QUIT, wxEVT_CWB_NAVIGATECOMPLETE,
] = [wx.NewId() for _init_events in range(17)]

EVT_CWB_BEFORENAVIGATE = wx.PyEventBinder(wxEVT_CWB_BEFORENAVIGATE)
EVT_CWB_TITLECHANGE = wx.PyEventBinder(wxEVT_CWB_TITLECHANGE)
EVT_CWB_DOWNLOADBEGIN = wx.PyEventBinder(wxEVT_CWB_DOWNLOADBEGIN)
EVT_CWB_PROPERTYCHANGE = wx.PyEventBinder(wxEVT_CWB_PROPERTYCHANGE)
EVT_CWB_COMMANDSTATECHANGE = wx.PyEventBinder(wxEVT_CWB_COMMANDSTATECHANGE)
EVT_CWB_FRAMEBEFORENAVIGATE = wx.PyEventBinder(wxEVT_CWB_FRAMEBEFORENAVIGATE)
EVT_CWB_WINDOWACTIVATE = wx.PyEventBinder(wxEVT_CWB_WINDOWACTIVATE)
EVT_CWB_NEWWINDOW = wx.PyEventBinder(wxEVT_CWB_NEWWINDOW)
EVT_CWB_DOWNLOADCOMPLETE = wx.PyEventBinder(wxEVT_CWB_DOWNLOADCOMPLETE)
EVT_CWB_WINDOWRESIZE = wx.PyEventBinder(wxEVT_CWB_WINDOWRESIZE)
EVT_CWB_WINDOWMOVE = wx.PyEventBinder(wxEVT_CWB_WINDOWMOVE)
EVT_CWB_PROGRESSCHANGE = wx.PyEventBinder(wxEVT_CWB_PROGRESSCHANGE)
EVT_CWB_FRAMENEWWINDOW = wx.PyEventBinder(wxEVT_CWB_FRAMENEWWINDOW)
EVT_CWB_STATUSTEXTCHANGE = wx.PyEventBinder(wxEVT_CWB_STATUSTEXTCHANGE)
EVT_CWB_FRAMENAVIGATECOMPLETE = wx.PyEventBinder(wxEVT_CWB_FRAMENAVIGATECOMPLETE)
EVT_CWB_QUIT = wx.PyEventBinder(wxEVT_CWB_QUIT)
EVT_CWB_NAVIGATECOMPLETE = wx.PyEventBinder(wxEVT_CWB_NAVIGATECOMPLETE)

class wxComWebBrowserEvent(wx.PyEvent):
    def __init__(self, eventType, evtArgs):
        wx.PyEvent.__init__(self)
        self.SetEventType(eventType)
        self.__dict__.update(evtArgs)

def varnames2dict(varnames, locals):
    res = {}
    for name in varnames:
        res['m_'+name] = locals[name]
    return res

class wxComWebBrowserEvents:
    def __init__(self, eventhandler):
        self.eventhandler = eventhandler
    def OnBeforeNavigate(self, URL=defaultNamedNotOptArg, Flags=defaultNamedNotOptArg, TargetFrameName=defaultNamedNotOptArg, PostData=defaultNamedNotOptArg, Headers=defaultNamedNotOptArg, Cancel=defaultNamedNotOptArg):
        "Fired when a new hyperlink is being navigated to."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_BEFORENAVIGATE, varnames2dict(self.OnBeforeNavigate.im_func.func_code.co_varnames[1:], locals())))
    def OnTitleChange(self, Text=defaultNamedNotOptArg):
        "Document title changed."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_TITLECHANGE, varnames2dict(self.OnTitleChange.im_func.func_code.co_varnames[1:], locals())))
    def OnDownloadBegin(self):
        "Download of a page started."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_DOWNLOADBEGIN, varnames2dict(self.OnDownloadBegin.im_func.func_code.co_varnames[1:], locals())))
    def OnPropertyChange(self, Property=defaultNamedNotOptArg):
        "Fired when the PutProperty method has been called."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_PROPERTYCHANGE, varnames2dict(self.OnPropertyChange.im_func.func_code.co_varnames[1:], locals())))
    def OnCommandStateChange(self, Command=defaultNamedNotOptArg, Enable=defaultNamedNotOptArg):
        "The enabled state of a command changed"
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_COMMANDSTATECHANGE, varnames2dict(self.OnCommandStateChange.im_func.func_code.co_varnames[1:], locals())))
    def OnFrameBeforeNavigate(self, URL=defaultNamedNotOptArg, Flags=defaultNamedNotOptArg, TargetFrameName=defaultNamedNotOptArg, PostData=defaultNamedNotOptArg, Headers=defaultNamedNotOptArg, Cancel=defaultNamedNotOptArg):
        "Fired when a new hyperlink is being navigated to in a frame."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_FRAMEBEFORENAVIGATE, varnames2dict(self.OnFrameBeforeNavigate.im_func.func_code.co_varnames[1:], locals())))
    def OnWindowActivate(self):
        "Fired when window has been activated."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_WINDOWACTIVATE, varnames2dict(self.OnWindowActivate.im_func.func_code.co_varnames[1:], locals())))
    def OnNewWindow(self, URL=defaultNamedNotOptArg, Flags=defaultNamedNotOptArg, TargetFrameName=defaultNamedNotOptArg, PostData=defaultNamedNotOptArg, Headers=defaultNamedNotOptArg, Processed=defaultNamedNotOptArg):
        "Fired when a new window should be created."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_NEWWINDOW, varnames2dict(self.OnNewWindow.im_func.func_code.co_varnames[1:], locals())))
    def OnDownloadComplete(self):
        "Download of page complete."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_DOWNLOADCOMPLETE, varnames2dict(self.OnDownloadComplete.im_func.func_code.co_varnames[1:], locals())))
    def OnWindowResize(self):
        "Fired when window has been sized."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_WINDOWRESIZE, varnames2dict(self.OnWindowResize.im_func.func_code.co_varnames[1:], locals())))
    def OnWindowMove(self):
        "Fired when window has been moved."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_WINDOWMOVE, varnames2dict(self.OnWindowMove.im_func.func_code.co_varnames[1:], locals())))
    def OnProgressChange(self, Progress=defaultNamedNotOptArg, ProgressMax=defaultNamedNotOptArg):
        "Fired when download progress is updated."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_PROGRESSCHANGE, varnames2dict(self.OnProgressChange.im_func.func_code.co_varnames[1:], locals())))
    def OnFrameNewWindow(self, URL=defaultNamedNotOptArg, Flags=defaultNamedNotOptArg, TargetFrameName=defaultNamedNotOptArg, PostData=defaultNamedNotOptArg, Headers=defaultNamedNotOptArg, Processed=defaultNamedNotOptArg):
        "Fired when a new window should be created."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_FRAMENEWWINDOW, varnames2dict(self.OnFrameNewWindow.im_func.func_code.co_varnames[1:], locals())))
    def OnStatusTextChange(self, Text=defaultNamedNotOptArg):
        "Statusbar text changed."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_STATUSTEXTCHANGE, varnames2dict(self.OnStatusTextChange.im_func.func_code.co_varnames[1:], locals())))
    def OnFrameNavigateComplete(self, URL=defaultNamedNotOptArg):
        "Fired when a new hyperlink is being navigated to in a frame."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_FRAMENAVIGATECOMPLETE, varnames2dict(self.OnFrameNavigateComplete.im_func.func_code.co_varnames[1:], locals())))
    def OnQuit(self, Cancel=defaultNamedNotOptArg):
        "Fired when application is quiting."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_QUIT, varnames2dict(self.OnQuit.im_func.func_code.co_varnames[1:], locals())))
    def OnNavigateComplete(self, URL=defaultNamedNotOptArg):
        "Fired when the document being navigated to becomes visible and enters the navigation stack."
        wx.PostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_NAVIGATECOMPLETE, varnames2dict(self.OnNavigateComplete.im_func.func_code.co_varnames[1:], locals())))

wxComWebBrowserPtr = MakeActiveXClass(IEModule.WebBrowser)
class wxComWebBrowser(wxComWebBrowserPtr):
    def __init__(self, parent = None, id = -1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=''):
        wxComWebBrowserPtr.__init__(self, parent, id, pos, size, style)
        self._eventObj = wxComWebBrowserEvents(self)
        self.SetName(name)
