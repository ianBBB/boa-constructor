#-----------------------------------------------------------------------------
# Name:        FindReplaceEngine.py
# Purpose:
#
# Author:      Tim Hochberg
#
# Created:     2001/29/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Tim Hochberg
# Licence:     GPL
#-----------------------------------------------------------------------------
import os, re, sys

import wx

from FindResults import FindResults
import Utils
from Utils import _

class FindError(ValueError):
    pass

def _fix(match, offset, length, selectionStart):
    if match is None:
        return None
    r = []
    try:
        for i in match.span():
            r.append((i + offset) % length + selectionStart)
    except:pass
    return tuple(r)

class FindReplaceEngine:
    def __init__(self, case=0, word=0, regex=0, wrap=1, reverse=0):
        self.case = 0
        self.word = 0
        self.mode = 'text' # or wildcard or regex
        self.wrap = 1
        self.closeOnFound = 0
        self.reverse = 0
        self.selection = 0
        self.findHistory = ['']
        self.replaceHistory = ['']
        self.folderHistory = ['']
        self.suffixHistory = ['*.py']
        self.suffixes = [".py"]
        self.regions = {}
        self.loadOptions()

    def _addHistory(self, pattern, history):
        if pattern:
            if pattern in history:
                history.remove(pattern)
            history.append(pattern)

    def addFind(self, pattern):
        self._addHistory(pattern, self.findHistory)

    def addReplace(self, pattern):
        self._addHistory(pattern, self.replaceHistory)

    def addFolder(self, pattern):
        self._addHistory(pattern, self.folderHistory)

    def addSuffix(self, pattern):
        self._addHistory(pattern, self.suffixHistory)

    def setRegion(self, view, region):
        self.regions[view] = region

    def getRegion(self, view):
        region = self.regions.get(view, view.GetSelection())
        if region[0] == region[1]:
            region = (0, view.GetTextLength())
        return region

    def findInSource(self, view, pattern):
        region = self.getRegion(view)
        self.addFind(pattern)
        start = view.GetSelection()[not self.reverse]
        if self.selection:
            result = self._find(view.GetTextRange(*region), pattern, start, region[0])
        else:
            result = self._find(view.GetText(), pattern, start, 0)
        if result is None:
            raise FindError(_("'%s' not found") % pattern)
        view.model.editor.addBrowseMarker(view.GetCurrentLine())

        if (result[0] < view.GetCurrentPos() and not self.reverse and self.wrap) or \
           (result[0] > view.GetCurrentPos() and self.reverse and self.wrap):
            view.model.editor.setStatus(_('Search wrapped'), 'Warning', ringBell=1)

        view.SetSelection(result[0], result[1])

        view.EnsureVisible(view.LineFromPosition(result[0]))

    def findNextInSource(self, view):
        self.findInSource(view, self.findHistory[-1])

    def _findAllInSource(self, text, pattern, selectionStart):
        viewResults = []
        for s, e in self._findAll(text, pattern, selectionStart, selectionStart):
            t = text[:s]
            lineNo = t.count('\n')
            left = max(t.rfind('\n'), 0) + 1
            index = s - left
            line = text[left:].split('\n', 1)[0]
            viewResults.append((lineNo+1, index+1, line))
        return viewResults

    def findAllInSource(self, view, pattern):
        region = self.getRegion(view)
        self.addFind(pattern)
        if self.selection:
            results = self._findAllInSource(view.GetTextRange(*region), pattern, region[0])
        else:
            results = self._findAllInSource(view.GetText(), pattern, 0)
        name = _('Results:') + ' ' + pattern
        if not view.model.views.has_key(name):
            resultView = view.model.editor.addNewView(name, FindResults)
        else:
            resultView = view.model.views[name]
        resultView.tabName = name
        resultView.results = {view.model.filename : results} # XXX should this be viewName?
        resultView.findPattern = pattern
        resultView.refresh()
        resultView.focus()

        resultView.rerunCallback = self.findAllInSource
        resultView.rerunParams = (view, pattern)

    def replaceInSource(self, view, pattern, new):
        region = self.getRegion(view)
        self.addFind(pattern)
        self.addReplace(new)
        # GetSelectedText returns bugus string when nothing is selected
        selRange = view.GetSelection()
        selText = view.GetSelectedText()
        if selRange[0] == selRange[1]:
            selText = ''
        # If the text to be replaced is not yet selected, don't replace, just
        # look for the next occurence.
        if self._find(selText, pattern, 0, 0) is not None: # XXX make more specific
            start = selRange[self.reverse]
            if self.selection:
                result = self._find(view.GetTextRange(*region), pattern, start, region[0])
            else:
                result = self._find(view.GetText(), pattern, start, 0)
            if result is None:
                raise FindError(_("'%s' not found") % pattern)
            view.SetSelection(result[0], result[1])
            compiled = self._compile(pattern)
            if self.mode == 'regex':
                new = compiled.sub(new, view.GetSelectedText())
            view.ReplaceSelection(new)

        # Attempt to find the next replacement
        try:
            self.findInSource(view, pattern)
        except FindError:
            pass

    def replaceAllInSource(self, view, pattern, new):
        region = self.getRegion(view)
        self.addFind(pattern)
        self.addReplace(new)
        text = view.GetText()
        # Replace from the end so that we can do the replace in place without
        # the indices getting messed up.
        self.reverse, oldReverse = 1, self.reverse
        if self.selection:
            results = self._findAll(view.GetTextRange(*region), pattern, region[0], region[0])
        else:
            results = self._findAll(view.GetText(), pattern, 0, 0)
        self.reverse = oldReverse
        compiled = self._compile(pattern)
        if results == []:
            return
        view.model.editor.addBrowseMarker(view.GetCurrentLine())
        for item in results:
            view.SetSelection(item[0], item[1])
            n = new
            if self.mode == 'regex':
                n = compiled.sub(new, view.GetSelectedText())
            view.ReplaceSelection(n)
        view.model.editor.statusBar.setHint(_("%s items replaced") % len(results))

    def findNamesInPackage(self, view):
        names = []
        packages = [os.path.dirname(view.model.assertLocalFile())]
        for base in packages:
            for p in [os.path.join(base, n) for n in os.listdir(base)]: 
                if os.path.isfile(p) and os.path.splitext(p)[1] in self.suffixes:
                    names.append(p)
                elif os.path.isdir(p) and os.path.isfile(os.path.join(base, "__init__.py")):
                    packages.append(p)
        names.sort(lambda x, y : os.path.basename(x) > os.path.basename(y))
        return names

    def findAllInFiles(self, names, view, pattern):
        self.addFind(pattern)
        results = {}
        # Setup progress dialog
        dlg = wx.ProgressDialog(_("Finding '%s' in files") % pattern,
                           _('Searching...'),
                            len(names),
                            view,
                            wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
        try:

            for i in range(len(names)):
                filename = self._getValidFilename(names[i])
                if not filename: continue
                try:
                    results[names[i]] = self._findAllInSource(open(filename).read(), pattern, 0)
                except IOError:
                    continue

                if type(filename) is unicode:
                    filename = filename.encode(sys.getfilesystemencoding())

                if not dlg.Update(i, _("Searching in file '%s'")%filename):
                    try:
                        view.model.editor.statusBar.setHint(_("Search aborted"))
                    except:
                        pass

            view.rerunCallback = self.findAllInFiles
            view.rerunParams = (names, view, pattern)

            view.addFindResults(pattern, results)
        finally:
            dlg.Destroy()

    def findAllInPackage(self, view, pattern):
        self.findAllInFiles(self.findNamesInPackage(view), view, pattern)

    def findAllInApp(self, view, pattern):
        names = map(view.model.moduleFilename, view.model.modules.keys())
        names.sort()
        self.findAllInFiles(names, view, pattern)


    def _compile(self, pattern):
        flags = [re.IGNORECASE, 0][self.case]
        if not self.mode == 'regex':
            pattern = re.escape(pattern)
        if self.mode == 'wildcard':
            pattern = pattern.replace(r'\?', '.?')
            pattern = pattern.replace(r'\*', '.*')
        if self.word:
            pattern = r"\b%s\b" % pattern
        return re.compile(pattern, flags)

    def _processText(self, text, start):
        before, after = text[:start], text[start:]
        if self.wrap:
            offset = start
            domain = after + before
        elif not self.reverse:
            offset = start
            domain = after
        else:
            offset = 0
            domain = before
        return domain, offset

    def _findAll(self, text, pattern, start, selectionStart):
        start = start - selectionStart
        compiled = self._compile(pattern)
        domain, offset = self._processText(text, start)
        matches = []
        start = 0
        while 1:
            s = compiled.search(domain, start)
            if s is None or s.end() == 0:
                break
            start = s.end()
            matches.append(_fix(s, offset, len(text), selectionStart))
        if self.reverse:
            matches.reverse()
        return matches

    def _find(self, text, pattern, start, selectionStart):
        if self.reverse:
            return (self._findAll(text, pattern, start, selectionStart) + [None])[0]
        start = start - selectionStart
        compiled = self._compile(pattern)
        domain, offset = self._processText(text, start)
        return _fix(compiled.search(domain), offset, len(text), selectionStart)

    def loadOptions(self):
        try:
            conf = Utils.createAndReadConfig('Explorer')
            if conf.has_section('finder'):
                self.wrap = conf.getint('finder', 'wrap')
                self.closeOnFound = conf.getint('finder', 'closeonfound')
        except:
            print 'Problem loading finder options'

    def saveOptions(self):
        try:
            conf = Utils.createAndReadConfig('Explorer')
            if not conf.has_section('finder'): conf.add_section('finder')
            conf.set('finder', 'wrap', str(self.wrap))
            conf.set('finder', 'closeonfound', str(self.closeOnFound))
            Utils.writeConfig(conf)
        except Exception, err:
            print 'Problem saving finder options: %s' % err

    def _getValidFilename(self, filename):
        protsplit = filename.split('://')
        if len(protsplit) > 1:
            if protsplit[0] != 'file' or len(protsplit) > 2:
                wx.LogWarning(_('%s not searched, only local files allowed')%filename)
                return ''
            return protsplit[1]
        return filename
