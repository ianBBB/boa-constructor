#-----------------------------------------------------------------------------
# Name:        About.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys, time, re, string
from thread import start_new_thread

import wx
import wx.html
import wx.lib.wxpTag

import __version__
import Preferences, Utils
from Utils import _

from ExternalLib import langlistctrl

translations = [
  (wx.LANGUAGE_AFRIKAANS, 'Riaan Booysen (riaan@e.co.za)'),
  (wx.LANGUAGE_CHINESE, 'Dylan Yang (otherrrr@gmail.com)'),
  (wx.LANGUAGE_FRENCH, 'Olivier Thiery (olivier.th@gmail.com)'),
  (wx.LANGUAGE_GERMAN, 'Werner F. Bruhin (werner.bruhin@free.fr), Jens Klein (jens@bluedynamics.com)'),
  (wx.LANGUAGE_ITALIAN, 'Michele Petrazzo (michele.petrazzo@unipex.it)'),
  (wx.LANGUAGE_PORTUGUESE_BRAZILIAN, 'Sergio Brant (sergiobrant@yahoo.com.br)'),
  (wx.LANGUAGE_SPANISH, 'Felix Medrano Sanz (xukosky@yahoo.es)'),
]

prog_update = re.compile('<<(?P<cnt>[0-9]+)/(?P<tot>[0-9]+)>>')

about_html = '''
<html>
<body bgcolor="#4488FF">
<center>
<table cellpadding="5" bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><br>
    <img src="%s"><br>
    <font color="#006600" size="+4"><b>Constructor</b></font><br><strong>v%s</strong>%s</td>
  </tr>
</table>
%s
</body>
</html>
'''

#  <param name="style" value="ALIGN_CENTER | CLIP_CHILDREN | ST_NO_AUTORESIZE">

progress_text = '''<p>
<wxp module="wx" class="StaticText">
  <param name="label" value="  ">
  <param name="id"    value="%d">
  <param name="size"  value="(352, 20)">
  <param name="style" value="wx.ALIGN_CENTER | wx.CLIP_CHILDREN | wx.ST_NO_AUTORESIZE">
</wxp>
<wxp module="wx" class="Window">
  <param name="id"    value="%d">
  <param name="size"  value="(352, 16)">
</wxp>'''


credits_html = '''
<html>
<body bgcolor="#4488FF">
<center>
<table bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><h3>Credits</h3><br>
    <br>
<b>The Boa Team</b><br>
<br>
Riaan Booysen (riaan@e.co.za)<p>
Werner F. Bruhin (werner.bruhin@free.fr)<br>
Shane Hathaway (shane@zope.com)<br>
Kevin Gill (kevin@telcotek.com)<br>
Robert Boulanger (robert@boulanger.de)<br>
Tim Hochberg (tim.hochberg@ieee.org)<br>
Kevin Light (klight@walkertechnical.com)<br>
Marius van Wyk (marius@e.co.za)<br>

<p>
<b>Translators</b><br>
<br>
%s
<p>
<b>Many thanks to</b><br>
<br>
Guido van Rossum and PythonLabs for Python<br>
<br>
wxPython (Robin Dunn) & wxWidgets (Julian Smart, Robert Roebling, Vadim Zeitlin, et al.)<br>
Neil Hodgson for Scintilla<br>
<br>
moduleparse.py borrows from pyclbrs.py - standard python library<br>
PythonInterpreter.py by Fredrik Lundh<br>
Mozilla, Delphi, WinCVS for iconic inspirations<br>
Cyclops, ndiff, reindent by Tim Peters<br>
Client.py, WebDAV, DateTime package and the Zope Book from Zope Corporation for Zope integration<br>
PyChecker by Neal Norwitz & Eric C. Newton<br>
py2exe by Thomas Heller<br>
Jeff Sasmor for wxStyledTextCtrl docs<br>
Hernan M. Foffani for ZopeShelf from which the Zope Book was converted<br>
Phil Dawes et al for the Bicycle Repair Man project, a Python refactoring package<br>
<p>
Mike Fletcher for reports, ideas and patches (MakePy dialog and much improved UML layout)<br>
<p>
Cedric Delfosse for maintaining the Debian package of Boa
<p>
<b>Boa interfaces with the following external applications, thanks to their authors</b><br>
Zope, CVS, SVN, SSH, SCP<br>
<p>
Last but not least, a very big thank you to <a href="TBS">Tangible Business Software</a> for partially
sponsoring my time on this project.<br>
<p>
<b>Boa Constructor is built on:</b><br>
<a href="Python"><img src="%s"></a>&nbsp;
<a href="wxPython"><img src="%s"></a>&nbsp;
<a href="wxWidgets"><img src="%s"></a><br>
<p>
<b>Boa Constructor is packaged for:</b><br>
<a href="Debian"><img src="%s"></a>&nbsp;
<a href="Gentoo"><img src="%s"></a>&nbsp;
<a href="FreeBSD"><img src="%s"></a>&nbsp;
<p>
<a href="Back">Back</a><br>
    </td>
  </tr>
</table>
</body>
</html>
'''

about_text = '''
<p>A <b>Python</b> IDE and <b>wxPython</b> GUI builder
</p>

<p><a href="Boa">https://bitbucket.org/cwt/boa-constructor</a><br></u>
&copy;2012-2014 <b>Chaiwat Suttipongsakul</b>.<br>
<a href="MailMe">cwt@bashell.com</a></p>
<p><a href="BoaLegacy">http://boa-constructor.sourceforge.net</a><br></u>
&copy;1999-2007 <b>Riaan Booysen</b>.<br>
<a href="MailRiaan">riaan@e.co.za</a></p>
<p><a href="Credits">Credits</a></p>
<p><font size=-1 color="#000077">Python %s</font><br>
<font size=-1 color="#000077">wx.Python %s: %s, <img src="%s">&nbsp;%s, %s</font></p>
<hr>
<wxp module="wx" class="Button">
  <param name="label" value="OK">
  <param name="id"    value="ID_OK">
</wxp>
</center>
<br>
<p>
<center>
<font size=-1><i>for <font color="#AA0000"><b>Bonnie</b></font></i></font>
</center>
</p>
'''

wx.FileSystem.AddHandler(wx.MemoryFSHandler())

def addImagesToFS():
    PNG = wx.BITMAP_TYPE_PNG
    for name, path, type in [
        ('Boa.jpg', 'Images/Shared/Boa.jpg', wx.BITMAP_TYPE_JPEG),
        ('PythonPowered.png', 'Images/Shared/PythonPowered.png', PNG),
        ('wxPyButton.png', 'Images/Shared/wxPyButton.png', PNG),
        ('wxWidgetsButton.png', 'Images/Shared/wxWidgetsButton.png', PNG),
        ('Debian.png', 'Images/Shared/Debian.png', PNG),
        ('Gentoo.png', 'Images/Shared/Gentoo.png', PNG),
        ('FreeBSD.png', 'Images/Shared/FreeBSD.png', PNG),
        ]:
        if name not in addImagesToFS.addedImages:
            wx.MemoryFSHandler.AddFile(name, Preferences.IS.load(path), type)
            addImagesToFS.addedImages.append(name)

    for lid, _tr in translations:
        li = wx.Locale.GetLanguageInfo(lid)
        name = 'flag-%s' % li.CanonicalName
        if name not in addImagesToFS.addedImages:
            bmp = langlistctrl.GetLanguageFlag(lid)
            wx.MemoryFSHandler.AddFile(name, bmp, wx.BITMAP_TYPE_PNG)
            addImagesToFS.addedImages.append(name)


addImagesToFS.addedImages = []

def createSplash(parent, modTot, fileTot):
    return AboutBoxSplash(parent, modTot, fileTot, extraStyle=wx.html.HW_SCROLLBAR_NEVER)

def createNormal(parent):
    return AboutBox(parent)

wxID_ABOUTBOX = wx.NewId()

class AboutBoxMixin:
    border = 7
    def __init__(self, parent, modTot=0, fileTot=0, extraStyle=0):
        self._init_ctrls(parent)

        addImagesToFS()

        self.moduleTotal = modTot
        self.fileTotal = fileTot

        self.blackback = wx.Window(self, -1, pos=(0, 0),
              size=self.GetClientSize(), style=wx.CLIP_CHILDREN)
        self.blackback.SetBackgroundColour(wx.BLACK)

        self.html = Utils.wxUrlClickHtmlWindow(self.blackback, -1,
              style=wx.CLIP_CHILDREN | wx.html.HW_NO_SELECTION | extraStyle)
        Utils.EVT_HTML_URL_CLICK(self.html, self.OnLinkClick)
        self.setPage()
        self.blackback.SetAutoLayout(True)
        lc = wx.LayoutConstraints()
        lc.top.SameAs(self.blackback, wx.Top, self.border)
        lc.left.SameAs(self.blackback, wx.Left, self.border)
        lc.bottom.SameAs(self.blackback, wx.Bottom, self.border)
        lc.right.SameAs(self.blackback, wx.Right, self.border)
        self.html.SetConstraints(lc)
        self.blackback.Layout()
        self.Center(wx.BOTH)
        self.SetAcceleratorTable(wx.AcceleratorTable([(0, wx.WXK_ESCAPE, wx.ID_OK)]))

    def gotoInternetUrl(self, url):
        try:
            import webbrowser
        except ImportError:
            wx.MessageBox('Please point your browser at: %s' % url)
        else:
            webbrowser.open(url)

    def OnLinkClick(self, event):
        clicked = event.linkinfo[0]
        if clicked == 'Credits':
            translators = []
            for lid, name in translations:
                li = wx.Locale.GetLanguageInfo(lid)
                translators.append('<img src="memory:flag-%s">&nbsp;%s - %s<br>' % (
                      li.CanonicalName, li.Description, name))
            translators = ''.join(translators)

            self.html.SetPage(credits_html % (translators,
                                              'memory:PythonPowered.png',
                                              'memory:wxPyButton.png',
                                              'memory:wxWidgetsButton.png',
                                              'memory:Debian.png',
                                              'memory:Gentoo.png',
                                              'memory:FreeBSD.png',
                                             ))
        elif clicked == 'Back':
            self.setPage()
            # self.html.HistoryBack()
        elif clicked == 'Python':
            self.gotoInternetUrl('http://www.python.org')
        elif clicked == 'wxPython':
            self.gotoInternetUrl('http://wxpython.org')
        elif clicked == 'wxWidgets':
            self.gotoInternetUrl('http://www.wxwidgets.org')
        elif clicked == 'Debian':
            self.gotoInternetUrl(
               'http://packages.debian.org/unstable/devel/boa-constructor.html')
        elif clicked == 'Gentoo':
            self.gotoInternetUrl(
               'http://www.gentoo.org/dyn/pkgs/dev-util/boa-constructor.xml')
        elif clicked == 'FreeBSD':
            self.gotoInternetUrl(
               'http://www.freebsd.org/ports/python.html#boaconstructor-0.2.3')
        elif clicked == 'Boa':
            self.gotoInternetUrl('https://bitbucket.org/cwt/boa-constructor')
        elif clicked == 'BoaLegacy':
            self.gotoInternetUrl('http://boa-constructor.sourceforge.net')
        elif clicked == 'TBS':
            self.gotoInternetUrl('http://www.tbs.co.za')
        elif clicked == 'MailMe':
            self.gotoInternetUrl('mailto:cwt@bashell.com')
        elif clicked == 'MailRiaan':
            self.gotoInternetUrl('mailto:riaan@e.co.za')


class AboutBox(AboutBoxMixin, wx.Dialog):
    def _init_ctrls(self, prnt):
        if Preferences.thisPlatform == 'msw':
            boxSize=wx.Size(410, 645)
        else:
            boxSize=wx.Size(410, 600)
        wx.Dialog.__init__(self, size=boxSize, pos=(-1, -1),
              id=wxID_ABOUTBOX, title=_('About Boa Constructor'), parent=prnt,
              name='AboutBox', style=wx.DEFAULT_DIALOG_STYLE)

        try:
            if 'Language.png' not in addImagesToFS.addedImages:
                wx.MemoryFSHandler.AddFile('Language.png',
                 langlistctrl.GetLanguageFlag(wx.GetApp().locale.GetLanguage()),
                 wx.BITMAP_TYPE_PNG)
                addImagesToFS.addedImages.append('Language.png')
        except Exception, err:
            pass

    def setPage(self):
        sysLangName = wx.GetApp().locale.GetSysName()
        self.html.SetPage((about_html % (
              'memory:Boa.jpg', __version__.version,
              '', about_text % (sys.version, wx.VERSION_STRING,
                ', '.join(wx.PlatformInfo), 'memory:Language.png', sysLangName,
                sys.getdefaultencoding()))))

DefAboutBox = AboutBox

class AboutBoxSplash(AboutBoxMixin, wx.Frame):
    progressBorder = 1
    fileOpeningFactor = 10
    def _init_ctrls(self, prnt):
        wx.Frame.__init__(self, size=wx.Size(418, 320), pos=(-1, -1),
              id=wxID_ABOUTBOX, title='Boa Constructor', parent=prnt,
              name='AboutBoxSplash', style=wx.SIMPLE_BORDER)
        self.progressId = wx.NewId()
        self.gaugePId = wx.NewId()
        self.SetBackgroundColour(wx.Colour(0x44, 0x88, 0xFF))  # wxColour(0x99, 0xcc, 0xff))

    def setPage(self):
        self.html.SetPage(about_html % ('memory:Boa.jpg',
          __version__.version, progress_text % (self.progressId, self.gaugePId), ''))

        self.initCtrlNames()

    def initCtrlNames(self):
        self.label = self.FindWindowById(self.progressId)
        self.label.SetBackgroundColour(wx.WHITE)
        parentWidth = self.label.GetParent().GetClientSize().x
        self.label.SetSize((parentWidth - 40, self.label.GetSize().y))

        gaugePrnt = self.FindWindowById(self.gaugePId)
        gaugePrnt.SetBackgroundColour(wx.BLACK)  # wx.Colour(0x99, 0xcc, 0xff))
        gaugeSze = gaugePrnt.GetClientSize()
        self.gauge = wx.Gauge(gaugePrnt, -1,
              range=self.moduleTotal + self.fileTotal * self.fileOpeningFactor,
              style=wx.GA_HORIZONTAL | wx.GA_SMOOTH,
              pos=(self.progressBorder, self.progressBorder),
              size=(gaugeSze.x - 2 * self.progressBorder,
                    gaugeSze.y - 2 * self.progressBorder))
        self.gauge.SetBackgroundColour(wx.Colour(0xff, 0x33, 0x00))
        # secret early quit option
        self.gauge.Bind(wx.EVT_LEFT_DOWN, self.OnGaugeDClick)
        self._gaugeClicks = 0

        # route all printing thru the text on the splash screen
        sys.stdout = StaticTextPF(self.label)
        start_new_thread(self.monitorModuleCount, ())

        EVT_MOD_CNT_UPD(self, self.OnUpdateProgress)

    def monitorModuleCount(self):
        self._live = True
        lastCnt = 0
        if self and sys and len(sys.modules) >= self.moduleTotal:
            wx.PostEvent(self, ModCntUpdateEvent(self.moduleTotal, 'importing'))
        else:
            while self and self._live and sys and len(sys.modules) < self.moduleTotal:
                mc = len(sys.modules)
                if mc > lastCnt:
                    lastCnt = mc
                    wx.PostEvent(self, ModCntUpdateEvent(mc, 'importing'))
                time.sleep(0.125)

    def Destroy(self):
        self._live = False
        self.gauge = None

        if sys:
            sys.stdout = sys.__stdout__
        wx.Frame.Destroy(self)

    def OnUpdateProgress(self, event):
        self._live = event.tpe == 'importing' and self._live
        if self.gauge:
            cnt = event.cnt
            if event.tpe == 'opening':
                cnt = cnt * self.fileOpeningFactor + self.moduleTotal
            self.gauge.SetValue(min(self.gauge.GetRange(), cnt))
        self.Update()

    def OnGaugeDClick(self, event):
        if event.GetPosition().x < 10:
            self._gaugeClicks += 1
            if self._gaugeClicks >= 5:
                print
                print 'Received early abort...'
                sys.exit()

class StaticTextPF(Utils.PseudoFile):
    def write(self, s):
        if not wx.Thread_IsMain():
            locker = wx.MutexGuiLocker()

        res = prog_update.search(s)
        if res:
            cnt = int(res.group('cnt'))
            wx.PostEvent(self.output.GetGrandParent().GetParent(),
                  ModCntUpdateEvent(cnt, 'opening'))
            s = s[:res.start()]

        ss = string.strip(s)
        if ss:
            self.output.SetLabel(ss)

        if sys:
            try:
                sys.__stdout__.write(s)
            except UnicodeEncodeError:
                s = s.encode(sys.getdefaultencoding(), 'replace')
                sys.__stdout__.write(s)

        wx.Yield()

wxEVT_MOD_CNT_UPD = wx.NewId()
EVT_MOD_CNT_UPD = wx.PyEventBinder(wxEVT_MOD_CNT_UPD)

class ModCntUpdateEvent(wx.PyEvent):
    def __init__(self, cnt, tpe):
        wx.PyEvent.__init__(self)
        self.SetEventType(wxEVT_MOD_CNT_UPD)
        self.cnt = cnt
        self.tpe = tpe

if __name__ == '__main__':

    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()

    # frame
    def updlbl(frame):
        frame.label.SetLabel('Testing')
        frame.label.SetLabel('Testing 1')
        frame.label.SetLabel('Testing 2')
        frame.label.SetLabel('Testing 3')

    frame = createSplash(None, 0, 0)
    frame.Show()
    wx.CallAfter(updlbl, frame)

    app.MainLoop()
