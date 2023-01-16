#-----------------------------------------------------------------------------
# Name:        ZopeViews.py
# Purpose:     Custom views for Zope models
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing ZopeLib.ZopeViews'

import os, time

import wx

from Views.EditorViews import HTMLView, ListCtrlView
from Views.SourceViews import EditorStyledTextCtrl
from Views.StyledTextCtrls import DebuggingViewSTCMix
from Models.HTMLSupport import BaseHTMLStyledTextCtrlMix

import Utils, ErrorStack

from ExternalLib import xmlrpclib

# Can be extended by plug-ins, used by syntax highlighted styles
zope_additional_attributes = ''

# XXX This is expensive and will really need to delay generatePage until View
# XXX is focused (like ExploreView)
# XXX The HTML control does not interact well with Zope.

class ZopeHTMLStyledTextCtrlMix(BaseHTMLStyledTextCtrlMix):
    def __init__(self, wId):
        BaseHTMLStyledTextCtrlMix.__init__(self, wId)

        zope_dtml_elements = 'dtml-var dtml-in dtml-if dtml-elif dtml-else dtml-unless '\
        'dtml-with dtml-let dtml-call dtml-comment dtml-tree dtml-try dtml-except '\
        'dtml-raise dtml-finally dtml-sqlvar '

        zope_zsql_tags = 'params '

        zope_attributes=\
        'sequence-key sequence-item sequence-start sequence-end sequence-odd '

        self.keywords = self.keywords + ' public !doctype '+ zope_dtml_elements +\
              zope_zsql_tags + zope_attributes + zope_additional_attributes

        self.setStyles()

class ZopeHTMLSourceView(EditorStyledTextCtrl, ZopeHTMLStyledTextCtrlMix):
    viewName = 'ZopeHTML'
    viewTitle = 'ZopeHTML'

    breakBmp = 'Images/Debug/Breakpoints.png'
    defaultEOL = '\n'
    def __init__(self, parent, model, actions=()):
        wxID_ZOPEHTMLSOURCEVIEW = wx.NewIdRef(count=1)
        EditorStyledTextCtrl.__init__(self, parent, wxID_ZOPEHTMLSOURCEVIEW,
          model, (('Refresh', self.OnRefresh, '-', 'Refresh'),) + actions, -1)
        ZopeHTMLStyledTextCtrlMix.__init__(self, wxID_ZOPEHTMLSOURCEVIEW)
        self.active = True

class ZopeDebugHTMLSourceView(ZopeHTMLSourceView, DebuggingViewSTCMix):
    breakBmp = 'Images/Debug/Breakpoints.png'
    defaultEOL = '\n'
    def __init__(self, parent, model, actions=()):
        ZopeHTMLSourceView.__init__(self, parent, model,
      (('Toggle breakpoint', self.OnSetBreakPoint, self.breakBmp, 'ToggleBrk'),)
        )

        from Views.PySourceView import brkPtMrk, tmpBrkPtMrk, disabledBrkPtMrk, \
                                       stepPosMrk, symbolMrg
        DebuggingViewSTCMix.__init__(self, (brkPtMrk, tmpBrkPtMrk,
              disabledBrkPtMrk, stepPosMrk))
        self.setupDebuggingMargin(symbolMrg)

        self.active = True

    def OnMarginClick(self, event):
        DebuggingViewSTCMix.OnMarginClick(self, event)

    def refreshCtrl(self):
        ZopeHTMLSourceView.refreshCtrl(self)
        self.setInitialBreakpoints()

class ZopeHTMLView(HTMLView):
    viewName = 'View'
    viewTitle = 'View'
    def generatePage(self):
        import urllib
        url = 'http://%s:%d/%s'%(self.model.transport.properties['host'],
              self.model.transport.properties['httpport'],
              self.model.transport.whole_name())
        f = urllib.urlopen(url)
        s = f.read()
        return s

class ZopeUndoView(ListCtrlView):
    viewName = 'Undo'
    viewTitle = 'Undo'
    undoBmp = 'Images/Shared/Undo.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          (('Undo', self.OnUndo, self.undoBmp, ''),), -1)
        self.addReportColumns( (('Action', 300), ('User', 75), ('Date', 130)) )

        self.active = True

        self.undoIds = []

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        try:
            undos = self.model.transport.getUndoableTransactions()
        except xmlrpclib.Fault, error:
            wx.LogError(Utils.html2txt(error.faultString))
        else:
            i = 0
            self.undoIds = []
            for undo in undos:
                self.addReportItems(i, (undo['description'], undo['user_name'], str(undo['time'])) )
                self.undoIds.append(undo['id'])
                i = i + 1

            self.pastelise()

    def OnUndo(self, event):
        if self.selected != -1:
            try:
                self.model.transport.undoTransaction([self.undoIds[self.selected]])
            except xmlrpclib.Fault, error:
                wx.LogError(Utils.html2txt(error.faultString))
            except xmlrpclib.ProtocolError, error:
                if error.errmsg == 'Moved Temporarily':
                    # This is actually a successful move
                    self.refreshCtrl()
                else:
                    wx.LogError(Utils.html2txt(error.errmsg))
            else:
                self.refreshCtrl()

class ZopeSecurityView(ListCtrlView):
    viewName = 'Security'
    viewTitle = 'Security'
    undoBmp = 'Images/Shared/Undo.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          (('Edit', self.OnEdit, self.undoBmp, ''),), -1)
        self.active = True

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        perms = self.model.transport.getPermissions()
        roles = self.model.transport.getRoles()

        colls = [('Acquired', 40), ('Permission', 275)]
        for role in roles:
            colls.append( (role, 75) )

        self.addReportColumns( colls )

        i = 0
        for perm in perms:
            self.addReportItems(*(i, ((perm['acquire'] == 'CHECKED' and '*' or '',
                  perm['name']) + tuple(map( lambda x: x['checked'] == 'CHECKED' and '*' or '',
                  perm['roles'])) )))
            i = i + 1

        self.pastelise()

    def OnEdit(self, event):
        if self.selected != -1:
            pass

class ZopeSiteErrorLogParser(ErrorStack.StackErrorParser):
    def __init__(self, lines, libPath, baseUrl):
        self.libPath = libPath
        self.baseUrl = baseUrl
        ErrorStack.StackErrorParser.__init__(self, lines)

    def parse(self):
        error = None
        lines = self.lines[:]
        while lines:
            line = lines.pop()
            if line.startswith('  Module '):
                modPath, lineNo, funcName = line[9:].split(', ')
                lineNo = int(lineNo[5:])
                modPath = modPath.strip()
                if modPath == 'Script (Python)':
                    path = lines.pop()
                    lines.pop()
                    if path.startswith('   - <PythonScript at '):
                        path = path[22:].strip()[:-1]
                        debugUrl = self.baseUrl+path+'/Script (Python)'
                        self.stack.append(
                              ErrorStack.StackEntry(debugUrl, lineNo+1, funcName))
                elif modPath.startswith('Python expression'):
                    continue
                else:
                    modPath = self.libPath+'/'+modPath.replace('.', '/')+'.py'
                    self.stack.append(ErrorStack.StackEntry(modPath, lineNo, funcName))
            elif line.startswith('   - <PythonScript at '):
                path = line[22:].strip()[:-1]
                debugUrl = self.baseUrl+path+'/Script (Python)'
                self.stack.append(
                      ErrorStack.StackEntry(debugUrl, 0, os.path.basename(path)))
            elif line.startswith('   - <ZopePageTemplate at '):
                path = line[26:].strip()[:-1]
                debugUrl = self.baseUrl+path+'/Page Template'
                self.stack.append(ErrorStack.StackEntry(debugUrl, 0,
                      os.path.basename(path)))
            elif line.startswith('   - URL: '):
                path = line[10:].strip()
                lineNo, colNo = lines.pop().split(', ')
                lineNo = int(lineNo.split()[-1])
                debugUrl = self.baseUrl+path+'/Page Template'
                self.stack.append(ErrorStack.StackEntry(debugUrl, lineNo,
                      os.path.basename(path)))
            elif line and line[0] != ' ':
                errType, errValue = line.split(': ', 1)
                lines.reverse()
                errValue = (errValue + ' '.join(lines)).strip()
                if errValue and errValue[0] == '<':
                    errValue = Utils.html2txt(errValue).replace('\n', ' ')

                error = [errType, errValue]
                break

        assert error
        self.error = error
        for entry in self.stack:
            entry.error = error


class ZopeSiteErrorLogView(ListCtrlView):
    viewName = 'Site Error Log'
    viewTitle = 'Site Error Log'
    gotoTracebackBmp = 'Images/Shared/Traceback.png'
    refreshBmp = 'Images/Editor/Refresh.png'

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wx.LC_REPORT,
          (('Open traceback', self.OnOpen, self.gotoTracebackBmp, ''),
           ('Refresh', self.OnRefresh, self.refreshBmp, 'Refresh')), 0)
        self.active = True

    logEntryIds = []
    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        errLogNode = self.model.transport

        try:
            entries = errLogNode.getResource().getLogEntries()
        except xmlrpclib.Fault, error:
            wx.LogError(Utils.html2txt(error.faultString))
        else:

            cols = [('Time', 150), ('User', 100), ('Type', 80),
                    ('Value', 200), ('Request URL', 350)]
            self.addReportColumns(cols)

            i = 0
            self.logEntryIds = []
            for entry in entries:
                value = entry['value']
                # pretty print html errors
                if value and value[0] == '<':
                    value = Utils.html2txt(value).replace('\n', ' ').strip()
                self.addReportItems(i, (time.ctime(entry['time']),
                      entry['username'], entry['type'], value, entry['url']) )
                self.logEntryIds.append(entry['id'])
                i = i + 1

            self.pastelise()

    def OnOpen(self, event):
        if self.selected != -1:
            logId = self.logEntryIds[self.selected]
            errLogNode = self.model.transport
            try:
                textEntry = errLogNode.getResource().getLogEntryAsText(logId)
            except xmlrpclib.Fault, error:
                wx.LogError(Utils.html2txt(error.faultString))
            else:
                lines = textEntry.split('\n')
                lines.reverse()
                top = lines.pop().strip()
                assert top == 'Traceback (innermost last):'

                props = errLogNode.properties
                libPath = props['localpath'] +'/lib/python'
                # zopedebug urls are transparently looked up in the zope
                # connections list when the transport is opened.
                baseUrl = 'zopedebug://%s:%s/'%(props['host'], props['httpport'])
                errStack = ZopeSiteErrorLogParser(lines, libPath, baseUrl)

                erroutFrm = self.model.editor.erroutFrm
                erroutFrm.updateCtrls([errStack], '', 'Error', libPath, textEntry)
                erroutFrm.display()

    def OnRefresh(self, event):
        self.refreshCtrl()
