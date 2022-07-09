#-----------------------------------------------------------------------------
# Name:        sourceconst.py
# Purpose:     Central place for constants, templates and snippets used by the
#              code generation process
#
# Author:      Riaan Booysen
#
# Created:     2001/19/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import os

import Preferences, Utils

idnt = Utils.getIndentBlock()

methodIndent = idnt
bodyIndent = idnt * 2

def wsfix(s):
    return s.replace('\t', idnt).replace('\n', os.linesep)


boaIdent = '#Boa'
boaClass = 'BoaApp'

init_ctrls = '_init_ctrls'
init_coll = '_init_coll_'
init_utils = '_init_utils'
init_props = '_init_props'
init_events = '_init_events'
init_sizers = '_init_sizers'
code_gen_warning = "generated method, don't edit"

defEnvPython = wsfix('#!/usr/bin/env python\n')
defCodingUtf8 = wsfix('# -*- coding: utf-8 -*-\n')

# XXX Frame Companion could return this source in writeImports?
defImport = wsfix('import wx\n\n')
defSig = defCodingUtf8 + boaIdent + wsfix(':%(modelIdent)s:%(main)s\n\n')

defCreateClass = wsfix('''def create(parent):
\treturn %(main)s(parent)

''')

srchWindowIdsLC = '\[wx.NewIdRef\(\) for %s in range\((?P<count>\d+)\)\]'
srchWindowIds = '\[(?P<winids>[A-Za-z0-9_, ]*)\] = ' + srchWindowIdsLC
srchWindowIdsCont = '(?P<any>.*)\] = ' + srchWindowIdsLC
defWindowIdsCont = wsfix('] = [wx.NewIdRef() for %(idIdent)s in range(%(idCount)d)]\n')
defWindowIds = wsfix('[%(idNames)s') + defWindowIdsCont

defClass = wsfix('''
class %(main)s(%(defaultName)s):
\tdef ''' + init_ctrls + '''(self, prnt):
\t\t%(defaultName)s.__init__(%(params)s)

\tdef __init__(self, parent):
\t\tself.''' + init_ctrls + '''(parent)
''')

defApp = wsfix('''import %(mainModule)s

modules = {'%(mainModule)s' : [1, 'Main frame of Application', 'none://%(mainModule)s.py']}

class BoaApp(wx.App):
\tdef OnInit(self):
\t\tself.main = %(mainModule)s.create(None)
\t\tself.main.Show()
\t\tself.SetTopWindow(self.main)
\t\treturn True

def main():
\tapplication = BoaApp(0)
\tapplication.MainLoop()

if __name__ == '__main__':
\tmain()
''')

defInfoBlock = wsfix('''#-----------------------------------------------------------------------------
# Name:        %(Name)s
# Purpose:     %(Purpose)s
#
# Author:      %(Author)s
#
# Created:     %(Created)s
# RCS-ID:      %(RCS-ID)s
# Copyright:   %(Copyright)s
# Licence:     %(Licence)s
#-----------------------------------------------------------------------------
''')

defSetup_py = wsfix('''
from distutils.core import setup

setup(name = '%(name)s',
      version = '%(version)s',
      scripts = [%(scripts)s],
)
''')

defPackageSrc = wsfix('''# Package initialisation
''')

defPyApp = wsfix('''modules = {}

def main():
\tpass

if __name__ == '__main__':
\tmain()
''')

simpleModuleRunSrc = wsfix('''

if __name__ == '__main__':
\tpass # add a call to run your script here
''')

simpleAppFrameRunSrc = wsfix('''

if __name__ == '__main__':
\tapp = wx.PySimpleApp()
\tframe = create(None)
\tframe.Show()

\tapp.MainLoop()
''')

simpleAppDialogRunSrc = wsfix('''

if __name__ == '__main__':
\tapp = wx.PySimpleApp()
\tdlg = create(None)
\ttry:
\t\tdlg.ShowModal()
\tfinally:
\t\tdlg.Destroy()
\tapp.MainLoop()
''')

simpleAppPopupRunSrc = wsfix('''

if __name__ == '__main__':
\tapp = wx.PySimpleApp()
\tframe = wx.Frame(None, -1, 'Parent')
\tframe.SetAutoLayout(True)
\tframe.Show()
\tpopup = create(frame)
\tpopup.Show(True)
\tapp.MainLoop()
''')
