#-----------------------------------------------------------------------------
# Name:        ErrorStack.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/05/29
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
import string, re, os, sys, pprint
import Utils

# XXX Make this more generic for pluggable parsers

if sys.version[:2] == '2.':
    tb_id = 'Traceback (most recent call last):'
else:
    tb_id = 'Traceback (innermost last):'

fileLine = re.compile('  File "(?P<filename>.+)", line (?P<lineno>[0-9]+)')

class StackEntry:
    def __init__(self, file = '', lineNo = 0, line = '', error = ()):
        self.file = file
        self.line = line
        self.lineNo = lineNo
        self.error = error

    def __repr__(self):
        return 'File "%s", line %d\n%s' % (self.file, self.lineNo, self.line)


class RecFile(Utils.PseudoFile):
    def write(self, s):
        self.output.append(s)

    def readlines(self):
        return self.output


class StackErrorParser:
    def __init__(self, lines):
        self.lines = lines
        self.stack = []
        self.error = []
        self.parse()

    def printError(self):
        print self.error
        for se in self.stack:
            print se

    def __repr__(self):
        return `self.error`+'\n'+pprint.pformat(self.stack)


#    def write(self, s):
#        self.lines.append(s)

class StdErrErrorParser(StackErrorParser):
    def parse(self):
        if len(self.lines):
            line1 = self.lines.pop()
            self.error[:] = list(line1.split(': '))

            if len(self.error) == 1:
                self.error.insert(0, 'String exception')
            self.error[1] = self.error[1].strip()
            for idx in range(len(self.lines)-1):
                mo = fileLine.match(self.lines[idx].rstrip())
                if mo:
                    self.stack.append(StackEntry(mo.group('filename'),
                      int(mo.group('lineno')), self.lines[idx + 1], self.error))

class PyCheckerErrorParser(StackErrorParser):
    def parse(self):
        import linecache
        if self.lines:
            pyCheckWarn = self.lines.pop()
            try:
                filename, lineNo, warng = eval(pyCheckWarn.strip(), {})
            except:
                pass
            else:
                self.error[:] = [warng]
                self.stack.append(StackEntry(os.path.abspath(filename), lineNo,
                      linecache.getline(filename, lineNo), self.error))

class PyLintErrorParser(StackErrorParser):
    def parse(self):
        import linecache
        if self.lines:
            filename, lineNo, msg = self.lines.pop()
            self.error[:] = [msg]
            self.stack.append(StackEntry(os.path.abspath(filename), lineNo,
                  linecache.getline(filename, lineNo), self.error))

def buildLintWarningList(lines):
    res = []
    for line in lines:
        res.append(PyLintErrorParser([line]))
    return res

#    return [PyLintErrorParser([line]) for line in lines]

# Limit stack size / processing time
# Zero to ignore limit
max_stack_depth = 100
max_lines_to_process = 20000

# XXX Look into speeding this up a bit :) !
class CrashTraceLogParser(StackErrorParser):
    """ Build a stack from a trace file built with option -T """
    def parse(self):
        lines = self.lines
        stack = self.stack = []
        fileSize = len(lines)
        self.error[:] = ['Core dump stack', 'trace file size: '+`fileSize`]

        baseDir = lines[0].strip()
        del lines[0]

        lines.reverse()

        cnt = 0
        while len(lines):
            cnt = cnt + 1
            if max_lines_to_process and cnt >= max_lines_to_process:
                break
            line = lines[0]
            del lines[0]
            try:
                file, lineno, frameid, event, arg = line.split('|', 4)
            except:
                print 'Error on line', cnt, line
                break
            if event == 'call':
                if not os.path.isabs(file):
                    file = os.path.join(baseDir, file)
                try: code = open(file).readlines()[int(lineno)-1]
                except IOError: code = ''
                stack.append( StackEntry(file, int(lineno), code) )
                if max_stack_depth and len(stack) >= max_stack_depth:
                    break
            elif event == 'return':
                idx = 0
                while 1:
                    try:
                        _file, _lineno, _frameid, _event, _rest = lines[idx].split('|', 4)
                        #print _file, _lineno, _frameid, _event
                    except Exception, error:
                        print 'Error on find', cnt, idx, lines[idx], str(error)
                        break

                    if _file == file and _frameid == frameid and _event == 'call':
                        del lines[:idx+1]
                        cnt = cnt + idx
                        break

                    idx = idx + 1
                    if idx >= len(lines):
                        print 'Call not found', file, lineno, frameid, len(lines)
                        del lines[:]
                        break

        if len(stack):
            stack.reverse()
        else:
            self.error[:] = ['Empty (resolved) stack', 'trace file size: '+`fileSize`]

def buildErrorList(lines, Parser = StdErrErrorParser):
    errs = []
    currerr = None

    for line in lines:
        if line.strip() == tb_id:
            currerr = []
            errs.append(currerr)
        elif line:
            if currerr is not None:
                currerr.append(line)
                if line[0] not in string.whitespace:
                    currerr = None
            else:
                # Try catch syntax errors
                if line.startswith('  File '):
                    currerr = [line]
                    errs.append(currerr)
                else:
                    currerr = None
                    errs.append([line])

    res = []
    for err in errs:
        res.append(Parser(err))
    return res

def errorList(stderr):
    return buildErrorList(stderr.readlines())


def crashError(file):
    try:
        lines = open(file).readlines()
        ctlp = CrashTraceLogParser(lines)
        open(file+'.stack', 'w').write(`ctlp`)
        return [ctlp]
    except IOError:
        return []

resp = {0 : 'failed', 1: 'succeeded'}

def test_buildErrorList(name, err_lines, answer):
    err_list = str(buildErrorList(err_lines))
    succ = err_list == answer
    print '--Testing.', name, resp[succ]
    if not succ:
        print 'RESULT:'
        print err_list
        print 'ANSWER:'
        print answer
        print '--'

def test():
    tb = [tb_id+'\n',
          '  File "Views\\AppViews.py", line 172, in OnRun\n',
          '    self.model.run()\n',
          '  File "EditorModels.py", line 548, in run\n',
          "    self.checkError(c, 'Ran')",
          '  File "EditorModels.py", line 513, in checkError\n',
          '    err.parse()\n',
          'AttributeError: parse\n',
          tb_id+'\n',
          '  File "Views\\AppViews.py", line 172, in OnRun\n',
          '    self.model.run()\n',
          '  File "EditorModels.py", line 548, in run\n',
          "    self.checkError(c, 'Ran')",
          '  File "EditorModels.py", line 513, in checkError\n',
          '    err.parse()\n',
          'AttributeError: parse\n']

    tb_answ = '''[['AttributeError', 'parse']
[File "Views\AppViews.py", line 172
    self.model.run()
,
 File "EditorModels.py", line 548
    self.checkError(c, 'Ran'),
 File "EditorModels.py", line 513
    err.parse()
], ['AttributeError', 'parse']
[File "Views\AppViews.py", line 172
    self.model.run()
,
 File "EditorModels.py", line 548
    self.checkError(c, 'Ran'),
 File "EditorModels.py", line 513
    err.parse()
]]'''

    # Normal trace backs
    test_buildErrorList('Long traceback', tb, tb_answ)


    tb2 = ['  File "Views\\SelectionTags.py", line 23\012',
            '    :\012',
            '    ^\012',
            'SyntaxError: invalid syntax\012']
    tb2_answ = '''[['SyntaxError', 'invalid syntax']
[File "Views\\SelectionTags.py", line 23
    :
]]'''

    # Syntax errors
    test_buildErrorList('Short traceback', tb2, tb2_answ)

    single_line_excp = "Exception exceptions.TypeError: 'call of non-function (type None)' in <method wxColourPtr.__del__ of wxColour instance at 03190B4C> ignored"
    single_line_excp_answ = '''[['Exception exceptions.TypeError', "'call of non-function (type None)' in <method wxColourPtr.__del__ of wxColour instance at 03190B4C> ignored"]\n[]]'''

    # One line 'warning' exceptions (e.g. wxPython objects deleted after
    # the libraries have already unloaded

    test_buildErrorList('Single line exception', [single_line_excp], single_line_excp_answ)

if __name__ == '__main__':
    test()
