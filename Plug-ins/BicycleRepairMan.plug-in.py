#-----------------------------------------------------------------------------
# Name:        BicycleRepairMan.plug-in.py
# Purpose:     Integrating Boa Constructor and Bicycle Repair Man
#
# Author:      Riaan Booysen
#
# Created:     2003/04/26
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2007
# Licence:     BSD
#-----------------------------------------------------------------------------

""" A Boa Constructor Plug-in that integrates the Bicycle Repair Man into the IDE.

The refactoring actions are published under the Edit menu of Python Source Views,
this is also the source's context menu.

There is a global refactoring context shared between all open modules.
This is exposed as editor.brm_context.

Also clearing the current context can be called from the Explorer menu.

"""

import os, linecache, traceback
from thread import start_new_thread

import bike

import wx

import Preferences, Utils, Plugins
from Utils import _

from Views import PySourceView, SourceViews
from Models import PythonEditorModels, PythonControllers
from Explorers import ExplorerNodes, FileExplorer
import ErrorStack, Editor

Editor.EditorFrame.brm_context = None

# Issues
# * On Windows filenames aren't guaranteed to always match those in the Editor
# * When the Boa IDE framework supports it, the BRM support should have
#   it's own menu, e.g. Tools->BicycleRepairMan->[Actions]
#   or a submenu under Edit, e.g. Edit->BicycleRepairMan->[Actions]

# Notes
# * There is an off-by-one issue between BRM and Scintilla,
#       before passing a scintilla lineno to BRM, add 1
#       before passing a BRM lineno to Scintilla, minus 1
# Settings to control how the collection of files that BRM tracks is built up

Plugins.registerPreference('BicycleRepairMan', 'brmProgressLogger',
                           "'ProgressStatusLogger'",
                           ['Destination for progress messages from BRM.'],
                           "options: 'ProgressStatusLogger', 'ProgressErrOutLogger'")

#-Editor plugins----------------------------------------------------------------

class CancelOperation(Exception): pass

from bike.query.findReferences import CouldntFindDefinitionException
class BRMViewPlugin:
    """ Plugin class for View classes that exposes the refactoring API.

    Handles """
    def __init__(self, model, view, actions):
        self.model = model
        self.view = view
        actions.extend( (
              ('-', None, '-', ''),
              (_('BRM - Find references'), self.OnFindReferences, '-', ''),
              (_('BRM - Find definition'), self.OnFindDefinition, '-', ''),
              ('-', None, '-', ''),
              (_('BRM - Rename'), self.OnRename, '-', ''),
              (_('BRM - Extract method'), self.OnExtractMethod, '-', ''),
              ('-', None, '-', ''),
              (_('BRM - Extract local variable'), self.OnExtractLocalVar, '-', ''),
              (_('BRM - Inline local variable'), self.OnInlineLocalVar, '-', ''),
              ('-', None, '-', ''),
              #('BRM - Get type of expression', self., '-', ''), # not useful currently
              (_('BRM - Undo last'), self.OnUndoLast, '-', ''),
        ) )

    def prepareForSelectOperation(self):
        selection = self.view.GetSelectedText().strip()
        if not selection:
            raise Exception, _('No text selected.')

        ctx = self.model.editor.brm_context
        filename = self.model.checkLocalFile()
        pos = self.view.GetSelectionStart()
        lineno = self.view.LineFromPosition(pos)+1
        column = self.view.GetColumn(pos)

        return ctx, selection, filename, lineno, column

    def prepareOutputDisplay(self, txt):
        errout = self.model.editor.erroutFrm
        errout.runningDir = ''
        errout.tracebackType = 'Info'

        tree = errout.errorStackTC
        tree.DeleteAllItems()
        root = tree.AddRoot(txt)
        errout.display()

        return errout, tree, root

    def saveAndRefresh(self):
        editor = self.model.editor
        savedfiles = editor.brm_context.save()

        for filename in savedfiles:
            editor.explorerModifyNotify('file://'+os.path.abspath(filename))


    def checkUnsavedChanges(self):
        model = self.model
        ctx = model.editor.brm_context

        for path in ctx.brmctx.paths:
            uri = 'file://'+os.path.abspath(path)
            if uri in model.editor.modules:
                try:
                    model.editor.prepareForCloseModule(
                          model.editor.modules[uri], True,
                          _('Save changes before Refactoring operation'))
                except Editor.CancelClose:
                    wx.LogError(_('Operation aborted.'))
                    return False
        return True

    def getExtractionInfo(self, xtype, caption):
        selection = self.view.GetSelectedText().strip()
        if not selection:
            raise CancelOperation, \
                  _('No text selected. Highlight the region you want to extract.')

        filename = self.model.checkLocalFile()
        name = wx.GetTextFromUser(_('New %s name:')%xtype, caption)
        if not name:
            raise CancelOperation, _('Empty names are invalid.')

        startpos, endpos = self.view.GetSelection()
        startline = self.view.LineFromPosition(startpos)
        startcol = self.view.GetColumn(startpos)
        endline = self.view.LineFromPosition(endpos)
        endcol = self.view.GetColumn(endpos)

        return filename, startline+1, startcol, endline+1, endcol, name

    def OnFindReferences(self, event=None):
        ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

        start_new_thread(self.findReferencesThread,
           (ctx, filename, lineno, column, sel) )

        self.model.editor.setStatus(_('BRM - Finding references...'))

    def findReferencesThread(self, ctx, fname, lineno, column, sel):
        try:
            matches = [ReferencesMatcher([ref])
              for ref in ctx.findReferencesByCoordinates(fname, lineno, column)]
        except CouldntFindDefinitionException:
            wx.CallAfter(self.findReferencesFindDefinition)
        except Exception, err:
            wx.CallAfter(wx.LogError,
                           ''.join(traceback.format_exception(*sys.exc_info())))
            wx.CallAfter(self.model.editor.setStatus,
                           _('BRM - Error %s')%str(err), 'Error')
        else:
            wx.CallAfter(self.findReferencesFinished, matches, sel)


    def findReferencesFindDefinition(self):
        self.model.editor.setStatus(_('BRM - Could not find definition'))

        if wx.MessageBox(_('Perform Find Definition?'), _('Find References'),
              wx.YES_NO | wx.ICON_WARNING) == wx.YES:
            self.OnFindDefinition()

    def findReferencesFinished(self, matches, sel):
        errout, tree, root = self.prepareOutputDisplay(
                             _('BRM - References for %s')%sel)

        x = 0
        for entry in matches:
            x = errout.addTracebackNode(entry, x)

        tree.SetItemHasChildren(root, True)
        tree.Expand(root)

        if x:
            errout.notebook.SetSelection(0)
            self.model.editor.setStatus(_('BRM - %s reference(s) found')%x)


    def OnFindDefinition(self, event=None):
        ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

        start_new_thread(self.findDefinitionThread,
                         (ctx, filename, lineno, column, sel))

        self.model.editor.setStatus(_('BRM - Finding definition...'))

    def findDefinitionThread(self, ctx, filename, lineno, column, sel):
        try:
            defs = ctx.findDefinitionByCoordinates(filename, lineno, column)
            if defs:
                try:
                    match = defs.next()
                except StopIteration:
                    wx.CallAfter(wx.LogError, _("Couldn't find definition"))
                    wx.CallAfter(self.model.editor.setStatus,
                                   _('BRM - Could not find definition'), 'Error')
                else:
                    wx.CallAfter(self.findDefinitionFinished, match, sel, defs)
            else:
                wx.CallAfter(wx.LogError, _("Couldn't find definition"))
                wx.CallAfter(self.model.editor.setStatus,
                               _('BRM - Could not find definition'), 'Error')
                
        except Exception, err:
            wx.CallAfter(wx.LogError,
                           ''.join(traceback.format_exception(*sys.exc_info())))
            wx.CallAfter(self.model.editor.setStatus,
                           _('BRM - Error %s')%str(err), 'Error')

    def findDefinitionFinished(self, match, sel, defs):
        mod, ctr = self.model.editor.openOrGotoModule(match.filename)
        view = mod.getSourceView()
        view.GotoLine(match.lineno-1)
        view.setLinePtr(match.lineno-1)

        errout, tree, root = self.prepareOutputDisplay(
                             _('BRM - Definition for %s')%sel)
        x = 1
        x = errout.addTracebackNode(ReferencesMatcher([match]), x)
        for ref in defs:
            entry = ReferencesMatcher([ref])
            x = errout.addTracebackNode(entry, x)

        tree.SetItemHasChildren(root, True)
        tree.Expand(root)

        if x:
            errout.notebook.SetSelection(0)
            self.model.editor.setStatus(_('BRM - %s matches(s) found')%x)

    def OnRename(self, event):
        if not self.checkUnsavedChanges():
            return

        ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

        ctx.setRenameMethodPromptCallback(self.renameCallback)

        newname = wx.GetTextFromUser(_('Rename to:'), _('Rename'), sel)
        if not newname:
            return

        ctx.renameByCoordinates(filename, lineno, column, newname)
        self.saveAndRefresh()

    def renameCallback(self, filename, lineno, colbegin, colend):
        currfile = self.model.filename

        model, ctr = self.model.editor.openOrGotoModule(filename)
        view = model.getSourceView()
        edge = view.PositionFromLine(lineno-1)
        view.SetSelection(edge+colbegin, edge+colend)

        res = wx.MessageBox(_('Cannot deduce the type of highlighted object'
                 ' reference.\nRename this declaration?'), _('Rename?'),
                 wx.YES_NO | wx.ICON_QUESTION) == wx.YES
        self.model.editor.openOrGotoModule(currfile)
        return res

    def OnExtractMethod(self, event):
        if not self.checkUnsavedChanges():
            return

        ctx = self.model.editor.brm_context
        try:
            ctx.extractMethod(*self.getExtractionInfo('Method', _('Extract method')))
        except CancelOperation, err:
            wx.LogError(str(err))
        else:
            self.view.SetSelectionEnd(self.view.GetSelectionStart())
            self.saveAndRefresh()

    def OnUndoLast(self, event):
        try:
            self.model.editor.brm_context.undo()
        except bike.UndoStackEmptyException, msg:
            wx.LogWarning(_('Nothing to undo, the undo stack is empty.'))
        else:
            self.saveAndRefresh()

    def OnExtractLocalVar(self, event):
        if not self.checkUnsavedChanges():
            return

        ctx = self.model.editor.brm_context
        try:
            filename, startline, startcol, endline, endcol, variablename = \
                  self.getExtractionInfo('Variable', _('Extract variable'))
        except CancelOperation, err:
            wx.LogError(str(err))
        else:
            ctx.extractLocalVariable(filename, startline, startcol, endline,
                  endcol, variablename)
            self.view.SetSelectionEnd(self.view.GetSelectionStart())
            self.saveAndRefresh()

    def OnInlineLocalVar(self, event):
        if not self.checkUnsavedChanges():
            return

        ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

        ctx.inlineLocalVariable(filename, lineno, column)

        self.saveAndRefresh()

    def OnGetExprType(self, event):
        ctx, sel, filename, lineno, column = self.prepareForSelectOperation()

        wx.LogMessage(
           `ctx.getTypeOfExpression(filename, lineno, column, column+len(sel))`)


PySourceView.PythonSourceView.plugins += (BRMViewPlugin,)


##class BRMControllerPlugin:
##    """ Plugin class for Controller classes that plublishes the Model interface """
##    def __init__(self, controller):
##        self.controller = controller
##
##    def actions(self, model):
##        return []
##        return [('-', None, '', ''),
##                ('BRM - Import module(s)', self.OnImportModules, '-', ''),
##               ]
##
##    def OnImportModules(self, event):
##        model = self.controller.getModel()
##        cnt = model.plugins['BRM'].importModules()
##        if cnt:
##            model.editor.setStatus('BRM - Parsed %s modules'%cnt)
##
##PythonControllers.ModuleController.plugins += (BRMControllerPlugin,)


class BRMModelPlugin:
    """ Plugin class for Model classes that creates the context and performs
        various ways importing into the refactoring context. """
    name = 'BRM'
    def __init__(self, model):
        self.model = model

        # the first one created starts the context
        if not hasattr(model.editor, 'brm_context') or model.editor.brm_context is None:
            model.editor.brm_context = context = bike.init()
            context.setProgressLogger(
                  globals()[Preferences.brmProgressLogger](model.editor))

    def update(self):
        pass

PythonEditorModels.ModuleModel.plugins += (BRMModelPlugin,)


#-------------------------------------------------------------------------------

class ProgressErrOutLogger:
    """ File like logger that uses the Output tab at the bottom of the Editor """
    def __init__(self, editor):
        self.errout = editor.erroutFrm

    def write(self, txt):
        wx.CallAfter(self.errout.appendToOutput, txt)

class ProgressStatusLogger:
    """ File like logger that uses the Editor statusbar as output """
    def __init__(self, editor):
        self.editor = editor
        self._buffer = ''

    def write(self, txt):
        self._buffer += txt
        if txt.endswith('\n'):
            wx.CallAfter(self.editor.setStatus, self._buffer.strip())
            self._buffer = ''

class ReferencesMatcher(ErrorStack.StackErrorParser):
    """ Needed to build "traceback objects" that appear on Find definition """
    def parse(self):
        for ref in self.lines:
            self.error = ['%s%% confidence for: %s:%s'% (
                          ref.confidence, ref.filename, ref.lineno)]
            self.stack.append(ErrorStack.StackEntry(ref.filename, ref.lineno,
                      linecache.getline(ref.filename, ref.lineno), self.error))

#-Explorer plugins--------------------------------------------------------------

##class BRMTranspController:
##    """ Transport Controller that extends the context menu of Filesystem objects """
##    def __init__(self, controller, editor):
##        self.controller = controller
##        self.editor = editor
##
##    def menuDefs(self):
##        return []
##        return [
##         (-1, '-', None, '-'),
##         (wx.NewIdRef(count=1), 'BRM - Import selection', self.OnImportItem, '-'),
##         (wx.NewIdRef(count=1), 'BRM - Clear refactoring context', self.OnClearContext, '-'),
##         (-1, '-', None, '-'),
##        ]
##
##    def OnImportItem(self, event):
##        list = self.controller.list
##        if list.node and self.editor.brm_context:
##            nodes = self.controller.getNodesForSelection(list.getMultiSelection())
##            for node in nodes:
##                filename = node.resourcepath
##                # only import dirs and modules
##                if os.path.splitext(filename)[1] in ('', '.py'):
##                    self.editor.brm_context.load(filename)
##
##    def OnClearContext(self, event):
##        self.editor.brm_context = context = bike.init()
##        context.setProgressLogger(
##              globals()[Preferences.brmProgressLogger](self.editor))
##
###-------------------------------------------------------------------------------
##FileExplorer.FileSysController.plugins += (BRMTranspController,)
