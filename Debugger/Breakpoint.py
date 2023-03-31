"""
Provides a breakpoint registry that can be sent to another process (via
getBreakpointList()).
"""

import os
# import trace

# try: from cPickle import Pickler, Unpickler
# except: from pickle import Pickler, Unpickler

# Now at Python 3.11, just use pickle.
from pickle import Pickler, Unpickler


class FileBreakpointList:
    def __init__(self):
        self.lines = {}  # lineno -> [{'temporary', 'cond', 'enabled', 'ignore'}]

    def loadBreakpoints(self, fn):
        try:
            if os.path.exists(fn):
                f = open(fn, 'rb')
                u = Unpickler(f)
                newlines = u.load()
                # The following line isn't quite correct
                # when multiple breakpoints are set on a
                # single line.
                self.lines.update(newlines)
                return 1
            else:
                return 0
        except:
            self.lines = {}
            return 0

    def saveBreakpoints(self, fn):
        try:
            if len(self.lines):
                savelines = {}
                # Filter out the temporary lines when saving.
                for lineno, linebreaks in self.lines.items():
                    savelines[lineno] = saveline = []
                    for brk in linebreaks:
                        if not brk['temporary']:
                            saveline.append(brk)
                f = open(fn, 'wb')
                p = Pickler(f)
                p.dump(savelines)
            else:
                os.remove(fn)
        except:
            pass

    def addBreakpoint(self, lineno, temp=0, cond='', ignore=0):
        import trace

        newbrk = {'temporary':temp, 'cond':cond, 'enabled':1, 'ignore':ignore}



        if lineno in self.lines.keys():
            linebreaks = self.lines[lineno]
            for brk in linebreaks:
                if brk['temporary'] == temp and brk['cond'] == cond:
                    # Already added.
                    return
            linebreaks.append(newbrk)
        else:
            self.lines[lineno] = linebreaks = [newbrk]

        trace.trace_is_on=False


    def deleteBreakpoints(self, lineno):
        if lineno in self.lines.keys():
            del self.lines[lineno]

    def moveBreakpoint(self, lineno, newlineno):
        if lineno != newlineno and lineno in self.lines.keys():
            bp = self.lines[lineno]
            del self.lines[lineno]
            self.lines[lineno] = bp

    def adjustBreakpoints(self, lineno, delta):
        set_breaks = []
        # traverse list twice, first deleting then re-adding to avoid stepping
        # on our own toes
        for brklineno, breaks in self.lines.items():
            if lineno < brklineno-1:
                del self.lines[brklineno]
                set_breaks.append( (brklineno+delta, breaks) )
        for brklineno, breaks in set_breaks:
            self.lines[brklineno] = breaks

    def enableBreakpoints(self, lineno, enable=1):
        if lineno in self.lines.keys():
            linebreaks = self.lines[lineno]
            for brk in linebreaks:
                brk['enabled'] = enable

    def ignoreBreakpoints(self, lineno, ignore=0):
        if lineno in self.lines.keys():
            linebreaks = self.lines[lineno]
            for brk in linebreaks:
                brk['ignore'] = ignore

    def conditionalBreakpoints(self, lineno, cond=''):
        if lineno in self.lines.keys():
            linebreaks = self.lines[lineno]
            for brk in linebreaks:
                brk['cond'] = cond

    def listBreakpoints(self):
        rval = []
        for lineno, linebreaks in self.lines.items():
            for brk in linebreaks:
                brkinfo = {'lineno':lineno}
                brkinfo.update(brk)
                rval.append(brkinfo)
        return rval

    def hasBreakpoint(self, lineno, endlineno=-1):
        if endlineno < 0:
            return (lineno in self.lines.keys())
        else:
            for line in self.lines.keys():
                if line >= lineno and line <= endlineno:
                    return 1
            return 0

    def clearTemporaryBreakpoints(self, lineno):
        if self.lines.has_key(lineno):
            linebreaks = self.lines[lineno]
            idx = 0
            while idx < len(linebreaks):
                brk = linebreaks[idx]
                if brk['temporary']:
                    del linebreaks[idx]
                else:
                    idx = idx + 1

    def clearAllBreakpoints(self):
        self.lines = {}


class BreakpointList:
    def __init__(self):
        self.files = {}  # filename -> FileBreakpointList

    def normalize(self, filename):
        if filename.find('://') < 0:
            filename = 'file://' + filename
        return filename

    def addBreakpoint(self, filename, lineno, temp=0, cond='', ignore=0):
        filename = self.normalize(filename)
        filelist = self.getFileBreakpoints(filename)
        filelist.addBreakpoint(lineno, temp, cond, ignore)

    def deleteBreakpoints(self, filename, lineno):
        filename = self.normalize(filename)
        if filename in self.files.keys():
            filelist = self.files[filename]
            filelist.deleteBreakpoints(lineno)

    def moveBreakpoint(self, filename, lineno, newlineno):
        filename = self.normalize(filename)
        if filename in self.files.keys():
            filelist = self.files[filename]
            filelist.moveBreakpoint(lineno, newlineno)

    def adjustBreakpoints(self, filename, lineno, delta):
        if filename in self.files.keys():
            filelist = self.files[filename]
            return filelist.adjustBreakpoints(lineno, delta)
        return 0

    def enableBreakpoints(self, filename, lineno, enable=1):
        filename = self.normalize(filename)
        if filename in self.files.keys():
            filelist = self.files[filename]
            filelist.enableBreakpoints(lineno, enable)

    def ignoreBreakpoints(self, filename, lineno, ignore=0):
        filename = self.normalize(filename)
        if filename in self.files.keys():
            filelist = self.files[filename]
            filelist.ignoreBreakpoints(lineno, ignore)

    def conditionalBreakpoints(self, filename, lineno, cond=''):
        filename = self.normalize(filename)
        if filename in self.files.keys():
            filelist = self.files[filename]
            filelist.conditionalBreakpoints(lineno, cond)

    def clearTemporaryBreakpoints(self, filename, lineno):
        filename = self.normalize(filename)
        if filename in self.files.keys():
            filelist = self.files[filename]
            filelist.clearTemporaryBreakpoints(lineno)

    def renameFileBreakpoints(self, oldname, newname):
        oldname = self.normalize(oldname)
        newname = self.normalize(newname)
        if oldname in self.files.keys():
            filelist = self.files[oldname]
            filelist.clearAllBreakpoints()
            del self.files[oldname]
            self.files[newname] = filelist

    def getFileBreakpoints(self, filename):
        filename = self.normalize(filename)
        if filename in self.files.keys():
            return self.files[filename]
        else:
            self.files[filename] = filelist = FileBreakpointList()
            return filelist

    def hasBreakpoint(self, filename, lineno, endlineno=-1):
        filename = self.normalize(filename)
        if filename in self.files.keys():
            filelist = self.files[filename]
            return filelist.hasBreakpoint(lineno, endlineno)
        return 0

    def getBreakpointList(self, fn=None):
        """Returns a list designed to pass to the setAllBreakpoints()
        debugger method.

        The optional fn constrains the return value to breakpoints in
        a specified file."""
        rval = []
        if fn is not None:
            fn = self.normalize(fn)
        for filename, filelist in self.files.items():
            if fn is None or filename == fn:
                for lineno, linebreaks in filelist.lines.items():
                    for brk in linebreaks:
                        brkinfo = {'filename': filename,
                                   'lineno': lineno}
                        brkinfo.update(brk)
                        rval.append(brkinfo)
        return rval


# ??? Should this really be a global variable?
# ISB can't see any need for it myself.
bplist = BreakpointList()
