#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# Name:        Boa.py
# Purpose:     The main file for Boa.
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:App:BoaApp

""" The __main__ file for Boa.

Handles creation/initialisation of main objects and commandline arguments """

import sys, os, string, time, warnings, datetime
import importlib

#sys.stdout = sys.__stdout__#open('stdout.txt', 'w')
#sys.stderr = sys.__stderr__#open('stderr.txt', 'w')

#try: import psyco; psyco.full()
#except ImportError: pass


t1 = time.time()

# This flag determines if Boa should try to send the filename via a socket to an
# already running instance of Boa. There is another flag under Preferences
# which determines if Boa should create and listen on the socket.
server_mode = 1

main_script = 'Boa.py'


trace_mode = 'functions' # 'lines'  'functions'
trace_save = 'all'#'lastline' # 'all'
def trace_func(frame, event, arg):
    """ Callback function when Boa runs in tracing mode"""
    if frame and tracefile :
        now = datetime.datetime.now()

        #fileDetail
        info = '%s|%s|%d|%d|%s|\n' % (now, frame.f_code.co_filename, frame.f_lineno,
              id(frame), event)

        if trace_save == 'lastline':
            tracefile.seek(0)
        tracefile.write(info)
        tracefile.flush()
    return trace_func

def get_current_frame():
    try: raise Exception('get_exc_info')
    except: return sys.exc_info()[2].tb_frame.f_back

def sendToRunningBoa(names, host='127.0.0.1', port=50007):
    import socket
    try:
        if names:
            print('Sent', end=' ')
        for name in names:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            # do not change files of form [prot]://[path]
            if name.find('://') == -1:
                name = os.path.abspath(name)
            s.send(name)
            print(name, end=' ')
            s.close()
        print()
    except socket.error: return 0
    else: return 1

startupErrors = []

import __version__

# Command line options
doDebug = constricted = emptyEditor = blockSocketServer = 0
startupfile = ''
startupModules = ()
startupEnv = os.environ.get('BOASTARTUP') or os.environ.get('PYTHONSTARTUP')
wxVersionSelect = None
unicodeEncoding = None

def processArgs(argv):
    _doDebug = _doRemoteDebugSvr = _constricted = _emptyEditor = 0
    _blockSocketServer = 0
    _startupfile = ''
    _startupModules = ()
    _wxVersionSelect = _unicodeEncoding = None
    import getopt
    try:
        optlist, args = getopt.getopt(argv, 'CDTSBERNHVhvO:W:U:',
         ['Constricted', 'Debug', 'Trace', 'StartupFile', 'BlockHomePrefs',
          'EmptyEditor', 'RemoteDebugServer', 'NoCmdLineTransfer', 'Help', 
          'Version', 'help', 'version', 'OverridePrefsDirName=', 'WxVersionSelect=',
          'UnicodeEncoding='])
    except getopt.GetoptError as err:
        print('Error: %s'%str(err))
        print('For options: Boa.py --help')
        sys.exit()

    if len(args):
        # XXX Only the first file appears in the list when multiple files
        # XXX are drag/dropped on a Boa shortcut, why?
        _startupModules = args

    for opt, arg in optlist:
        if opt in ('-D', '--Debug') and len(args):
            # XXX should be able to 'debug in running Boa'
            _doDebug = 1
        elif opt in ('-R', '--RemoteDebugServer') and len(args):
            _doRemoteDebugSvr = 1
        elif opt in ('-T', '--Trace'):
            print('Running in trace mode.')
            global tracefile
            tracefile = open('Boa.trace', 'wt')
            tracefile.write(os.getcwd()+'\n')
            trace_func(get_current_frame().f_back, 'call', None)
            trace_func(get_current_frame(), 'call', None)
            if trace_mode == 'functions':
                sys.setprofile(trace_func)
            elif trace_mode == 'lines':
                sys.settrace(trace_func)
    
        if opt in ('-S', '--StartupFile'):
            _startupfile = startupEnv
    
        if opt in ('-C', '--Constricted'):
            _constricted = 1
    
        if opt in ('-E', '--EmptyEditor'):
            _emptyEditor = 1
    
        if opt in ('-N', '--NoCmdLineTransfer'):
            _blockSocketServer = 1
        
        if opt in ('-W', '--wxVersionSelect', ''):
            _wxVersionSelect = arg

        if opt in ('-U', '--UnicodeEncoding', ''):
            _unicodeEncoding = arg
    
        if opt in ('-h', '--help', '-H', '--Help'):
            print('Boa Constructor (%s)'%__version__.version)
            print('Command-line usage: %s [options] [file1] [file2] ...'%main_script)
            print('-C, --Constricted:')
            print('\tRuns in constricted mode, overrides the Preference')
            print('-D, --Debug:')
            print('\tRuns the first filename passed on the command-line in the Debugger ')
            print('\ton startup')
            print('-T, --Trace:')
            print('\tRuns in traceing mode. Used for tracking down core dumps. Every ')
            print('\tfunction call is logged to a file which can later be parsed for ')
            print('\ta traceback')
            print('-S, --StartupFile:')
            print('\tExecutes the script pointed to by $BOASTARTUP or '
                  '$PYTHONSTARTUP in')
            print('\tthe Shell namespace. The Editor object is available as sys.boa_ide.')
            print('\tOverrides the Preference')
            print('-B, --BlockHomePrefs:')
            print('\tPrevents the $HOME directory being used ')
            print('-O dirname, --OverridePrefsDirName dirname:')
            print('\tSpecify a different directory to load Preferences from.')
            print('\tDefault is .boa and is used if it exists')
            print('\tDirectory will be created (and populated) if it does not exist')
            print('-E, --EmptyEditor:')
            print("\tDon't open the files that were open last time Boa was closed.")
            print('-R, --RemoteDebugServer:')
            print('\tRuns the first filename passed on the command-line in a ')
            print('\tRemote Debugger Server that can be connected to over a socket.')
            print('-N, --NoCmdLineTransfer:')
            print("\tDon't transfer command line options to a running Boa, start a ")
            print('\tnew instance.')
            print('-U encoding, --UnicodeEncoding encoding:')
            print('\tSpecify a specific encoding to use.')
            print('-W version, --wxVersionSelect version:')
            print('\tSpecify a specific version of wxPython to use.')
            print('-H, --Help, -h, --help:')
            print('\tThis page.')
    
            sys.exit()
    
        if opt in ('-v', '--version', '-V', '--Version'):
            print('Version: %s'%__version__.version)
            sys.exit()

    return (_doDebug, _startupfile, _startupModules, _constricted, _emptyEditor,
            _doRemoteDebugSvr, _blockSocketServer, _wxVersionSelect, 
            _unicodeEncoding, optlist, args)

# This happens as early as possible (before wxPython loads) to make filename
# transfer to a running Boa as quick as possible and little NS pollution
if __name__ == '__main__' and len(sys.argv) > 1:
    (doDebug, startupfile, startupModules, constricted, emptyEditor, doDebugSvr,
     blockSocketServer, wxVersionSelect, unicodeEncoding, 
     opts, args) = processArgs(sys.argv[1:])
    if doDebugSvr and startupModules:
        print('Running as a Remote Debug Server')
        from Debugger.RemoteServer import start
        # XXX username, password optionally should be on the command-line
        start(username='', password='')

        # startupModules contain everything from the first filename and on
        sys.argv = startupModules
        sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])))
        exec(compile(open(sys.argv[0], "rb").read(), sys.argv[0], 'exec'), {'__name__': '__main__',
                               '__builtins__': __builtins__})

        sys.exit()

    # Try connect to running Boa using sockets, tnx to Tim Hochberg
    if not blockSocketServer and startupModules and server_mode:
        if sendToRunningBoa(startupModules):
            print('Transfered arguments to running Boa, exiting.')
            sys.exit()

print('Starting Boa Constructor v%s'%__version__.version)
print('importing wxPython')

# ##########################
# old Python 2 code, standard encoding is now utf-8 which is
# set in the following line
###########################
# importlib.reload(sys)
# set_default_encoding = getattr(sys, 'setdefaultencoding')
# if unicodeEncoding is not None:
#     print('using encoding %s'%unicodeEncoding)
#
#     if hasattr(sys, 'frozen'):
#         set_default_encoding(unicodeEncoding)
#     else:
#         set_default_encoding(unicodeEncoding)
# else:
#     set_default_encoding('utf-8')
_unicodeEncoding = 'uft8'

try:
    # See if there is a multi-version install of wxPython
    if not hasattr(sys, 'frozen'):
        import wxversion
        if wxVersionSelect is None:
            wxversion.ensureMinimal('4.1')
        else:
            wxversion.select(wxVersionSelect)
except ImportError:
    # Otherwise assume a normal 2.4 install, if it isn't 2.4 it will
    # be caught below
    pass

import wx
from wx import adv
wx.RegisterId(15999)

#warnings.filterwarnings('ignore', '', DeprecationWarning, 'wxPython.imageutils')

# Use package version string as it is the only one containing bugfix version number
# Remove non number/dot characters
wxVersion = wx.__version__
for c in wxVersion:
    if c not in string.digits+'.':
        wxVersion = wxVersion.replace(c, '')

wxVersion = tuple([int(v) for v in (wxVersion.split('.')+['0'])[:4]])

if wxVersion < __version__.wx_version:
    wx.PySimpleApp()
    wx.MessageBox('Sorry! This version of Boa requires at least '\
                 'wxPython %d.%d.%d.%d'%__version__.wx_version,
                 'Version error', wx.OK | wx.ICON_ERROR)
    raise Exception('wxPython >= %d.%d.%d.%d required'%__version__.wx_version)

if __version__.wx_version_max and wxVersion > __version__.wx_version_max:
    #wx.PySimpleApp()
    app = wx.App(0)

    frame = wx.Frame(None)
    app.SetTopWindow(frame)
    frame.Show()
    wx.MessageBox('Sorry! This version of Boa does not work under '\
                 'wxPython %d.%d.%d.%d, please downgrade to '\
                 'wxPython %d.%d.%d.%d'% tuple(wxVersion+__version__.wx_version_max),
                 'Version error', wx.OK | wx.ICON_ERROR)
    raise Exception('wxPython %d.%d.%d.%d not supported'%wxVersion)

import Preferences
import Utils
from Utils import _

import About

print('running main...')

# XXX auto created frames (main frame handled currently)
# XXX More property editors!
# XXX More companion classes! $

# XXX Find: Exceptions should not cancel the search

# XXX Refactor PropertyEditor/Companion/Inspector interfaces

# XXX Support IDLE extensions

# XXX Code completion
# XXX     self.qwerty = qwerty
# XXX     wipes '= qwerty' when qwerty is selected

# XXX Renaming Boa.jpg in root fails

# XXX Save as after app is closed

# XXX Add wx.ImageBitmap, delete (prints class link error)


modules ={'About': [0, 'About box and Splash screen', 'About.py'],
 'AppViews': [0, 'Views for the AppModel', 'Views/AppViews.py'],
 'ArtProviderBrowser': [0, '', 'PropEdit/ArtProviderBrowser.py'],
 'BaseCompanions': [0, '', 'Companions/BaseCompanions.py'],
 'BasicCompanions': [0, '', 'Companions/BasicCompanions.py'],
 'BicycleRepairMan.plug-in': [0, '', 'Plug-ins/BicycleRepairMan.plug-in.py'],
 'Breakpoint': [0, '', 'Debugger/Breakpoint.py'],
 'Browse': [0, 'History for navigation through the IDE', 'Browse.py'],
 'ButtonCompanions': [0, '', 'Companions/ButtonCompanions.py'],
 'CPPSupport': [0, '', 'Models/CPPSupport.py'],
 'CVSExplorer': [0, '', 'Explorers/CVSExplorer.py'],
 'ChildProcessClient': [0, '', 'Debugger/ChildProcessClient.py'],
 'ChildProcessServer': [0, '', 'Debugger/ChildProcessServer.py'],
 'ChildProcessServerStart': [0, '', 'Debugger/ChildProcessServerStart.py'],
 'ClassBrowser': [0,
                  'Frame that displays the wxPython object hierarchy by Class and Module',
                  'ClassBrowser.py'],
 'ClipboardPlus.plug-in': [0, '', 'Plug-ins/ClipboardPlus.plug-in.py'],
 'CollectionEdit': [0, '', 'Views/CollectionEdit.py'],
 'ComCompanions': [0,
                   'Companion classes for COM (win32 only)',
                   'Companions/ComCompanions.py'],
 'Companions': [0,
                'Most visual wxPython class companions ',
                'Companions/Companions.py'],
 'ConfigSupport': [0, '', 'Models/ConfigSupport.py'],
 'Constructors': [0,
                  'Constructor signature mixin classes',
                  'Companions/Constructors.py'],
 'ContainerCompanions': [0, '', 'Companions/ContainerCompanions.py'],
 'Controllers': [0, '', 'Models/Controllers.py'],
 'CreationOrdDlg': [0, '', 'Views/CreationOrdDlg.py'],
 'CtrlAlign': [0, '', 'Views/CtrlAlign.py'],
 'CtrlSize': [0, '', 'Views/CtrlSize.py'],
 'Cyclops': [0, '', 'ExternalLib/Cyclops.py'],
 'DAVExplorer': [0, '', 'Explorers/DAVExplorer.py'],
 'DataView': [0,
              'View to manage non visual frame objects',
              'Views/DataView.py'],
 'DateTimeCompanions': [0, '', 'Companions/DateTimeCompanions.py'],
 'DebugClient': [0, '', 'Debugger/DebugClient.py'],
 'Debugger': [0,
              'Module for out-of-process debugging of Python apps',
              'Debugger/Debugger.py'],
 'DebuggerControls': [0, '', 'Debugger/DebuggerControls.py'],
 'Designer': [0, 'View to visually design frames', 'Views/Designer.py'],
 'DialogCompanions': [0, '', 'Companions/DialogCompanions.py'],
 'DiffView': [0, '', 'Views/DiffView.py'],
 'Editor': [0, 'Source code editor hosting models and views', 'Editor.py'],
 'EditorExplorer': [0, '', 'Explorers/EditorExplorer.py'],
 'EditorHelper': [0, '', 'Models/EditorHelper.py'],
 'EditorModels': [0, '', 'Models/EditorModels.py'],
 'EditorUtils': [0,
                 'Specialised ToolBar and StatusBar controls for the Editor',
                 'EditorUtils.py'],
 'EditorViews': [0,
                 'Main module for View classes that work with Models',
                 'Views/EditorViews.py'],
 'Enumerations': [0, '', 'PropEdit/Enumerations.py'],
 'ErrorStack': [0, 'Various forms of error parsers', 'ErrorStack.py'],
 'ErrorStackFrm': [0, '', 'ErrorStackFrm.py'],
 'EventCollections': [0, '', 'Companions/EventCollections.py'],
 'Explorer': [0,
              'Specialised visual controls for the Explorer (Tree, list and splitter)',
              'Explorers/Explorer.py'],
 'ExplorerNodes': [0, '', 'Explorers/ExplorerNodes.py'],
 'ExtMethDlg': [0, 'Dialog for ExternalMethods', 'ZopeLib/ExtMethDlg.py'],
 'ExtraZopeCompanions.plug-in': [0,
                                 '',
                                 'Plug-ins/ExtraZopeCompanions.plug-in.py'],
 'FTPExplorer': [0, '', 'Explorers/FTPExplorer.py'],
 'FileDlg': [0, 'Replacement for the standard file dialog. ', 'FileDlg.py'],
 'FileExplorer': [0, '', 'Explorers/FileExplorer.py'],
 'FindReplaceDlg': [0, '', 'FindReplaceDlg.py'],
 'FindReplaceEngine': [0, '', 'FindReplaceEngine.py'],
 'FindResults': [0, '', 'FindResults.py'],
 'FlexGridGrowableDlg': [0, '', 'Companions/FlexGridGrowableDlg.py'],
 'FrameCompanions': [0, '', 'Companions/FrameCompanions.py'],
 'GizmoCompanions': [0, '', 'Companions/GizmoCompanions.py'],
 'HTMLCyclops': [0, '', 'HTMLCyclops.py'],
 'HTMLResponse': [0, '', 'HTMLResponse.py'],
 'HTMLSupport': [0, '', 'Models/HTMLSupport.py'],
 'Help': [0, 'Interactive help frame', 'Help.py'],
 'HelpBook.plug-in': [0, '', 'Plug-ins/HelpBook.plug-in.py'],
 'ImageEditor.plug-in': [0, '', 'Plug-ins/ImageEditor.plug-in.py'],
 'ImageStore': [0,
                'Centralised point to load images (cached/zipped/etc)',
                'ImageStore.py'],
 'ImageViewer': [0, '', 'ZopeLib/ImageViewer.py'],
 'InProcessClient': [0, '', 'Debugger/InProcessClient.py'],
 'Infofields': [0, '', 'Infofields.py'],
 'InspectableViews': [0, '', 'Views/InspectableViews.py'],
 'Inspector': [0,
               "Inspects object's constructor/properties/events/parents",
               'Inspector.py'],
 'InspectorEditorControls': [0, '', 'PropEdit/InspectorEditorControls.py'],
 'IsolatedDebugger': [0, '', 'Debugger/IsolatedDebugger.py'],
 'JavaSupport.plug-in': [0, '', 'Plug-ins/JavaSupport.plug-in.py'],
 'LanguageSelectDlg': [0, '', 'LanguageSelectDlg.py'],
 'LibCompanions': [0, '', 'Companions/LibCompanions.py'],
 'ListCompanions': [0, '', 'Companions/ListCompanions.py'],
 'LoginDialog': [0, '', 'ZopeLib/LoginDialog.py'],
 'MaskedEditFmtCodeDlg': [0, '', 'Companions/MaskedEditFmtCodeDlg.py'],
 'ModRunner': [0,
               'Module that runs processes in a variety of ways',
               'ModRunner.py'],
 'ModuleFinder.plug-in': [0, '', 'Plug-ins/ModuleFinder.plug-in.py'],
 'OGLViews': [0, '', 'Views/OGLViews.py'],
 'ObjCollection': [0, '', 'Views/ObjCollection.py'],
 'Palette': [1,
             'Top frame which hosts the component palette and help options',
             'Palette.py'],
 'PaletteMapping': [0, '', 'PaletteMapping.py'],
 'PaletteStore': [0,
                  'Storage for variables defining the palette organisation',
                  'PaletteStore.py'],
 'PascalSupport.plug-in': [0, '', 'Plug-ins/PascalSupport.plug-in.py'],
 'PathMappingDlg': [0, '', 'Debugger/PathMappingDlg.py'],
 'PathsPanel': [0, '', 'Debugger/PathsPanel.py'],
 'Plugins': [0, '', 'Plugins.py'],
 'Preferences': [0,
                 'Central store of customiseable properties',
                 'Preferences.py'],
 'PrefsExplorer': [0, '', 'Explorers/PrefsExplorer.py'],
 'ProcessProgressDlg': [0, '', 'ProcessProgressDlg.py'],
 'ProfileView': [0, '', 'Views/ProfileView.py'],
 'PropDlg': [0, '', 'ZopeLib/PropDlg.py'],
 'PropertyEditors': [0,
                     'Module defining property editors used in the Inspector',
                     'PropEdit/PropertyEditors.py'],
 'PySourceView': [0, '', 'Views/PySourceView.py'],
 'PyrexSupport.plug-in': [0, '', 'Plug-ins/PyrexSupport.plug-in.py'],
 'PythonControllers': [0, '', 'Models/PythonControllers.py'],
 'PythonEditorModels': [0, '', 'Models/PythonEditorModels.py'],
 'PythonInterpreter': [0, '', 'ExternalLib/PythonInterpreter.py'],
 'RTTI': [0, 'Introspection code. Run time type info', 'RTTI.py'],
 'RegexEditor.plug-in': [0, '', 'Plug-ins/RegexEditor.plug-in.py'],
 'RemoteClient': [0, '', 'Debugger/RemoteClient.py'],
 'RemoteDialog': [0, '', 'Debugger/RemoteDialog.py'],
 'RemoteServer': [0, '', 'Debugger/RemoteServer.py'],
 'ResourceSupport': [0, '', 'Models/ResourceSupport.py'],
 'RunCyclops': [0, '', 'RunCyclops.py'],
 'SSHExplorer': [0, '', 'Explorers/SSHExplorer.py'],
 'STCStyleEditor': [0, '', 'Views/STCStyleEditor.py'],
 'Search': [0, '', 'Search.py'],
 'SelectionTags': [0,
                   'Controls and objects that manage the visual selection in the Designer',
                   'Views/SelectionTags.py'],
 'ShellEditor': [0, 'Python Interpreter Shell window', 'ShellEditor.py'],
 'Signature': [0, '', 'ExternalLib/Signature.py'],
 'SizerCompanions': [0, '', 'Companions/SizerCompanions.py'],
 'SizersView': [0, '', 'Views/SizersView.py'],
 'SourceViews': [0, '', 'Views/SourceViews.py'],
 'StyledTextCtrls': [0,
                     'Mixin classes to use features of Scintilla',
                     'Views/StyledTextCtrls.py'],
 'Tasks': [0, '', 'Debugger/Tasks.py'],
 'Tests': [0, '', 'Tests.py'],
 'UserCompanions.plug-in': [0, '', 'Plug-ins/UserCompanions.plug-in.py'],
 'UtilCompanions': [0, '', 'Companions/UtilCompanions.py'],
 'Utils': [0, 'General utility routines and classes', 'Utils.py'],
 'WizardCompanions': [0, '', 'Companions/WizardCompanions.py'],
 'XMLSupport': [0, '', 'Models/XMLSupport.py'],
 'XMLView': [0, '', 'Views/XMLView.py'],
 'ZipExplorer': [0, '', 'Explorers/ZipExplorer.py'],
 'ZopeCompanions': [0, '', 'ZopeLib/ZopeCompanions.py'],
 'ZopeEditorModels': [0, '', 'ZopeLib/ZopeEditorModels.py'],
 'ZopeExplorer': [0, '', 'ZopeLib/ZopeExplorer.py'],
 'ZopeFTP': [0, '', 'ZopeLib/ZopeFTP.py'],
 'ZopeViews': [0, '', 'ZopeLib/ZopeViews.py'],
 'methodparse': [0,
                 'Module responsible for parsing code inside generated methods',
                 'methodparse.py'],
 'moduleparse': [0,
                 'For parsing a whole module into Module, classes and functions',
                 'moduleparse.py'],
 'ndiff': [0, '', 'ExternalLib/ndiff.py'],
 'popen2import': [0, '', 'popen2import.py'],
 'prefs.gtk.rc': [0, '', 'Config/prefs.gtk.rc.py'],
 'prefs.keys.rc': [0, '', 'Config/prefs.keys.rc.py'],
 'prefs.mac.rc': [0, '', 'Config/prefs.mac.rc.py'],
 'prefs.msw.rc': [0, '', 'Config/prefs.msw.rc.py'],
 'prefs.plug-ins.rc': [0, '', 'Config/prefs.plug-ins.rc.py'],
 'prefs.rc': [0, '', 'Config/prefs.rc.py'],
 'reindent': [0, '', 'ExternalLib/reindent.py'],
 'relpath': [0, '', 'relpath.py'],
 'sourceconst': [0, 'Source generation constants', 'sourceconst.py'],
 'wxNamespace': [0, '', 'wxNamespace.py'],
 'wxPopen': [0, '', 'wxPopen.py'],
 'wxPythonControllers': [0, '', 'Models/wxPythonControllers.py'],
 'wxPythonEditorModels': [0, '', 'Models/wxPythonEditorModels.py'],
 'xmlrpclib': [0, '', 'ExternalLib/xmlrpclib.py']}

class BoaApp(wx.App):
    """ Application object, responsible for the Splash screen, applying command
        line switches, optional logging and creation of the main frames. """

    def __init__(self):
        wx.App.__init__(self, False)

    def OnInit(self):
        Preferences.initScreenVars()

        # i18n support
        self.locale = wx.Locale(Preferences.i18nLanguage)
        wx.Locale.AddCatalogLookupPathPrefix(os.path.join(Preferences.pyPath, 'locale'))
        if hasattr(sys, 'frozen'):
            self.locale.AddCatalog('wxstd')   
        self.locale.AddCatalog('boa') 

        wx.ToolTip.Enable(True)
        if Preferences.debugMode == 'release':
            self.SetAssertMode(wx.APP_ASSERT_SUPPRESS)
        elif Preferences.debugMode == 'development':
            self.SetAssertMode(wx.APP_ASSERT_EXCEPTION)


        conf = Utils.createAndReadConfig('Explorer')
        if not conf.has_section('splash'):
            conf.add_section('splash')
            modTot = 1
        else:
            modTot = conf.getint('splash', 'modulecount')
        fileTot = len(eval(conf.get('editor', 'openfiles'), {}))

        abt = About.createSplash(None, modTot, fileTot)
        try:
            abt.Show()
            abt.Update()
            # Let the splash screen repaint
            wx.Yield()

            # Imported here to initialise core features and plug-ins
            import PaletteMapping

            print('creating Palette')
            import Palette
            self.main = Palette.BoaFrame(None, -1, self)

            print('creating Inspector')
            import Inspector
            inspector = Inspector.InspectorFrame(self.main)

            print('creating Editor')
            import Editor
            editor = Editor.EditorFrame(self.main, -1, inspector, wx.Menu(),
                self.main.componentSB, self, self.main)
            self.SetTopWindow(editor)

            inspector.editor = editor

            conf.set('splash', 'modulecount', str(len(sys.modules)))
            try:
                Utils.writeConfig(conf)
            except IOError as err:
                startupErrors.append(_('Error writing config file: %s\nPlease '
              'ensure that the Explorer.*.cfg file is not read only.')% str(err))

            if not emptyEditor:
                editor.restoreEditorState()

            self.main.initPalette(inspector, editor)

    ##            editor.setupToolBar()

            import Help
            if not Preferences.delayInitHelp:
                print('initialising help')
                Help.initHelp()

            global constricted
            constricted = constricted or Preferences.suBoaConstricted

            print('showing main frames <<100/100>>')
            if constricted:
                editor.CenterOnScreen()
                inspector.CenterOnScreen()
                inspector.initSashes()
            else:
                self.main.Show()
                inspector.Show()
                # For some reason the splitters have to be visible on GTK before they
                # can be sized.
                inspector.initSashes()

            editor.Show()
            editor.doAfterShownActions()

            # Call startup files after complete editor initialisation
            global startupfile
            if Preferences.suExecPythonStartup and startupEnv:
                startupfile = startupEnv

            if editor.shell:
                editor.shell.execStartupScript(startupfile)

        finally:
            abt.Destroy()

        # Apply command line switches
        if doDebug and startupModules:
            mod = editor.openOrGotoModule(startupModules[0])[0]
            mod.debug()
        elif startupModules:
            for mod in startupModules:
                editor.openOrGotoModule(mod)

        editor.setupToolBar()

        editor.setStatus('Startup time: %5.2f' % (time.time() - t1))

        Utils.showTip(self.main.editor)

        if Preferences.logStdStreams:
            sys.stdout = Utils.OutputLoggerPF()
            sys.excepthook = Utils.wxPyExceptHook

        if Preferences.exWorkingDirectory:
            try:
                os.chdir(Preferences.exWorkingDirectory)
            except OSError as err:
                startupErrors.append(_('Could not set working directory from '
                                       'Preferences.exWorkingDirectory :'))
                startupErrors.append(str(err))

        if startupErrors:
            for error in startupErrors:
                wx.LogError(error)
            wx.LogError(_('\nThere were errors during startup, please click "Details"'))

        if wx.Platform == '__WXMSW__':
            self.tbicon = adv.TaskBarIcon()
            self.tbicon.SetIcon(self.main.GetIcon(), 'Boa Constructor')
            self.tbicon.Bind(adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)
            self.tbicon.Bind(adv.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarMenu)
            self.tbicon.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=self.TBMENU_RESTORE)
            self.tbicon.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
            self.tbicon.Bind(wx.EVT_MENU, self.OnTaskBarAbout, id=self.TBMENU_ABOUT)

        editor.assureRefreshed()

        return True

    [TBMENU_RESTORE, TBMENU_CLOSE, TBMENU_ABOUT] = Utils.wxNewIds(3)

    def OnTaskBarMenu(self, event):
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, _('Restore Boa Constructor'))
        menu.Append(self.TBMENU_CLOSE,   _('Exit'))
        menu.AppendSeparator()
        menu.Append(self.TBMENU_ABOUT,   _('About'))
        self.tbicon.PopupMenu(menu)
        menu.Destroy()

    def OnTaskBarActivate(self, event):
        if not self.main.IsShown():
            self.main.editor.restore()
        else:
            self.main.restore()

    def OnTaskBarClose(self, event):
        self.main.Close()
        #self.ProcessIdle()

    def OnTaskBarAbout(self, event):
        self.main.editor.OnHelpAbout(event)

def main(argv=None):
    # XXX Custom installations, should distutil libs be used for this ?
    # XXX Binary test is no longer valid, maybe type of __import__ function
    # Only install if it's not a 'binary' distribution
    if Preferences.installBCRTL and hasattr(wx, '__file__'):
        join, dirname = os.path.join, os.path.dirname
        wxPythonPath = dirname(wx.__file__)
        wxPythonLibPath = join(dirname(wx.__file__), 'lib')
        ##pythonLibPath = dirname(wx.PythonPath)
        try:
            # Install/update run time libs if necessary
            Utils.updateDir(join(Preferences.pyPath, 'bcrtl'),
                  join(wxPythonLibPath, 'bcrtl'))
        except Exception as error:
            startupErrors.extend(['Error while installing Run Time Libs:',
            '    '+str(error),
            '\nMake sure you have sufficient rights to copy these files, and that ',
            'the files are not read only. You may turn off this attempted ',
            'installation in prefs.rc.py : installBCRTL'])

    if argv is not None:
        global doDebug, startupfile, startupModules, constricted, emptyEditor, \
              doDebugSvr, blockSocketServer, wxVersionSelect, unicodeEncoding
        doDebug, startupfile, startupModules, constricted, emptyEditor, \
              doDebugSvr, blockSocketServer, wxVersionSelect, \
              unicodeEncoding, opts, args = processArgs(argv)
    try:
        app = BoaApp()
    except Exception as error:
        wx.MessageBox(str(error), _('Error on startup'))
        raise

    app.MainLoop()

    # Clean up (less warnings)
    if hasattr(app, 'tbicon'):
        del app.tbicon
    if not hasattr(sys, 'boa_debugger'):
        if Preferences.logStdStreams:
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__
        Preferences.cleanup()
    del app

if __name__ == '__main__':
    main()
