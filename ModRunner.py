#-----------------------------------------------------------------------------
# Name:        ModRunner.py
# Purpose:     Different process executers.
#
# Author:      Riaan Booysen
#
# Created:     2001/12/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import string, traceback
import os, sys
from io import StringIO

import wx

import Preferences, Utils
from Utils import _

import ErrorStack

class ModuleRunner:
    def __init__(self, esf, runningDir=''):
        self.init(esf)
        self.runningDir = runningDir
        self.results = {}
        self.pid = 0

    def run(self, cmd):
        pass

    def init(self, esf):
        self.esf = esf

    def recheck(self):
        if self.results:
            return self.checkError(**self.results)

    def checkError(self, err, caption, out=None, root='Error', errRaw=()):
        if self.esf:
            if err or out:
                tbs = self.esf.updateCtrls(err, out, root, self.runningDir, errRaw)
                self.esf.display(len(err))
                return tbs
            else:
                self.esf.updateCtrls([])
                return None
        else:
            self.results = {'err': err,
                            'caption': caption,
                            'out': out,
                            'root': root,
                            'errRaw': errRaw}


class CompileModuleRunner(ModuleRunner):
    """ Uses compiles a module to show syntax errors

    If the model is not saved, the source in the model is compiled directly.
    Saved models (on the filesystem) are compiled from their files. This is
    useful for generating the .pyc files """
    def run(self, filename, source, modified):
        # If "filename" is passed as unicode,
        # we need to convert it back to the filesystem's encoding
        # because the "compile" function needs it so.

        # if type(filename) is unicode:   # In python 3, all strings are in unicode

        # filename = filename.encode(sys.getfilesystemencoding())
            
        # protsplit = string.find(filename, '://')
        protsplit = filename.find('://')
        if protsplit != -1:
            prot, _filename = filename[:protsplit], filename[protsplit+3:]
            if prot != 'none':
                filename = _filename
        else:
            prot = 'file'

        source = Utils.toUnixEOLMode(source)+'\n\n'
        try:
            code = compile(source, filename, 'exec')
        except SyntaxError:
            etype, value, tb = sys.exc_info()
            try:
                traceback.print_exception(etype, value, tb, 0, sys.stderr)
            finally:
                etype = value = tb = None
        except:
            # Add filename to traceback object
            etype, value, tb = sys.exc_info()
            try:
                if len(value.args) == 2 and len(value.args[1]) == 4:
                    msg, (_filename, lineno, offset, line) = value.args
                    if not _filename:
                        # XXX this is broken on too long lines
                        value.args = msg, (filename, lineno, offset, line)
                        value.filename = filename
                    traceback.print_exc()
                else:
                    traceback.print_exc()
                    
            finally:
                etype = value = tb = None

        # auto generating pycs is sometimes a pain
        ##        if modified or prot != 'file':
        ##        else:
        ##            import py_compile
        ##            py_compile.compile(filename)

class ExecuteModuleRunner(ModuleRunner):
    """ Uses wxPython's wx.Execute, no redirection """
    def run(self, cmd):
        wx.Execute(cmd, True)

class ProcessModuleRunner(ModuleRunner):
    """ Uses wxPython's wx.Process, output and errors are redirected and displayed
        in a frame. A cancelable dialog displays while the process executes
        This currently only works for non GUI processes """
    def run(self, cmd, Parser=ErrorStack.StdErrErrorParser,
            caption=_('Execute module'), root='Error', autoClose=False):
        import ProcessProgressDlg
        dlg = ProcessProgressDlg.ProcessProgressDlg(None, cmd, caption,
              autoClose=autoClose)
        try:
            dlg.ShowModal()
            serr = ErrorStack.buildErrorList(dlg.errors, Parser)
            return self.checkError(serr, _('Ran'), dlg.output, root, dlg.errors)

        finally:
            dlg.Destroy()

class wxPopenModuleRunner(ModuleRunner):
    def run(self, cmd, inpLines=[], execFinish=None):

        out=[]
        def outputFunc(val):
            out.append(val)

        err = []
        def errorsFunc(val):
            err.append(val)

        def finFunc():
            output = errors = ""
            if err:
                errors = StringIO(''.join(str(err[0], 'UTF-8'))).readlines()
            if out:
                output = StringIO(''.join(str(out[0], 'UTF-8'))).readlines()

            serr = ErrorStack.buildErrorList(errors)

            if serr or output:
                self.checkError(serr, _('Ran'), output, errRaw=errors)

            if execFinish:
                execFinish(self)

        import wxPopen
        self.proc = wxPopen.wxPopen3(cmd, inpLines, outputFunc, errorsFunc, finFunc, self.esf)

        self.pid = self.proc.pid


class PopenModuleRunner(ModuleRunner):
    """ Uses Python's popen2, output and errors are redirected and displayed
        in a frame. """
    def run(self, cmd, inpLines=[], execStart=None):
        inpLines.reverse()
        inp, outp, errp = os.popen3(cmd)  # should this be a subprocess?
        pid = 0 # XXX only available on unix :(
        if execStart:
            wx.CallAfter(execStart, pid)
        out = []
        while 1:
            if inpLines:
                inp.write(inpLines.pop())
            l = outp.readline()
            if not l: break
            out.append(l)

        errLines = errp.readlines()
        serr = ErrorStack.buildErrorList(errLines)
        self.pid = pid

        if serr or out:
            return self.checkError(serr, _('Ran'), out, errRaw=errLines)
        else:
            return None

PreferredRunner = PopenModuleRunner

wxEVT_EXEC_FINISH = wx.NewIdRef(count=1)

EVT_EXEC_FINISH = wx.PyEventBinder(wxEVT_EXEC_FINISH)

class ExecFinishEvent(wx.PyEvent):
    def __init__(self, runner):
        wx.PyEvent.__init__(self)
        self.SetEventType(wxEVT_EXEC_FINISH)
        self.runner = runner
