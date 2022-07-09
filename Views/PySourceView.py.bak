#-----------------------------------------------------------------------------
# Name:        PySourceView.py
# Purpose:     Python Source code View
#
# Author:      Riaan Booysen
#
# Created:     2000/04/26
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Views.PySourceView'

import os, string, bdb, sys, types, keyword

import wx
import wx.stc

import ProfileView, Search, Help, Preferences, ShellEditor, Utils, SourceViews
from Utils import _

from SourceViews import EditorStyledTextCtrl
from StyledTextCtrls import PythonStyledTextCtrlMix, BrowseStyledTextCtrlMix,\
     FoldingStyledTextCtrlMix, AutoCompleteCodeHelpSTCMix, \
     CallTipCodeHelpSTCMix, DebuggingViewSTCMix, idWord, word_delim, object_delim
from Preferences import keyDefs
import methodparse, moduleparse, sourceconst
import wxNamespace

mrkCnt = SourceViews.markerCnt
brkPtMrk, tmpBrkPtMrk, disabledBrkPtMrk, stepPosMrk = range(mrkCnt+1, mrkCnt+5)
SourceViews.markerCnt = mrkCnt + 4

brwsIndc, synErrIndc = range(0, 2)
lineNoMrg, symbolMrg, foldMrg = range(0, 3)

class ShellNameNotFound(Exception): pass

class PythonSourceView(EditorStyledTextCtrl, PythonStyledTextCtrlMix,
                       BrowseStyledTextCtrlMix, FoldingStyledTextCtrlMix,
                       AutoCompleteCodeHelpSTCMix, CallTipCodeHelpSTCMix,
                       DebuggingViewSTCMix):
    viewName = 'Source'
    viewTitle = _('Source')
    
    breakBmp = 'Images/Debug/Breakpoints.png'
    runCrsBmp = 'Images/Editor/RunToCursor.png'
    modInfoBmp = 'Images/Modules/InfoBlock.png'
    def __init__(self, parent, model):
        a1 = (('-', None, '', ''),
              (_('Comment'), self.OnComment, '-', 'Comment'),
              (_('Uncomment'), self.OnUnComment, '-', 'Uncomment'),
              (_('Indent'), self.OnIndent, '-', 'Indent'),
              (_('Dedent'), self.OnDedent, '-', 'Dedent'),
              ('-', None, '-', ''),
              (_('Run to cursor'), self.OnRunToCursor, self.runCrsBmp, ''),
              # evts defined in DebuggingViewSTCMix
              (_('Toggle breakpoint'), self.OnSetBreakPoint, self.breakBmp, 'ToggleBrk'),
              (_('Load breakpoints'), self.OnLoadBreakPoints, '-', ''),
              (_('Save breakpoints'), self.OnSaveBreakPoints, '-', ''),
              ('-', None, '', ''),
              (_('Add module runner'), self.OnAddSimpleApp, '-', ''),
              ('-', None, '-', ''),
              (_('Add module info'), self.OnAddModuleInfo, self.modInfoBmp, ''),
              (_('Add comment line'), self.OnAddCommentLine, '-', 'DashLine'),
              (_('Code transformation'), self.OnCodeTransform, '-', 'CodeXform'),
              (_('Code completion'), self.OnCompleteCode, '-', 'CodeComplete'),
              (_('Call tips'), self.OnParamTips, '-', 'CallTips'),
              (_('Browse to'), self.OnBrowseTo, '-', 'BrowseTo'),
              ('-', None, '-', ''),
              (_('Context help'), self.OnContextHelp, '-', 'ContextHelp'))

        wxID_PYTHONSOURCEVIEW = wx.NewId()

        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONSOURCEVIEW,
          model, a1, -1)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEVIEW,
              (lineNoMrg, Preferences.STCLineNumMarginWidth))
        BrowseStyledTextCtrlMix.__init__(self, brwsIndc)
        FoldingStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEVIEW, foldMrg)
        AutoCompleteCodeHelpSTCMix.__init__(self)
        CallTipCodeHelpSTCMix.__init__(self)
        DebuggingViewSTCMix.__init__(self, (brkPtMrk, tmpBrkPtMrk,
              disabledBrkPtMrk, stepPosMrk))

        self.lsp = 0
        # XXX These could be persisted
        self.lastRunParams = ''
        self.lastDebugParams = ''

        # last line # that was edited
        self.damagedLine = -1

        self.setupDebuggingMargin(symbolMrg)

        # Error indicator
        self.IndicatorSetStyle(synErrIndc, wx.stc.STC_INDIC_SQUIGGLE)
        self.IndicatorSetForeground(synErrIndc, Preferences.STCSyntaxErrorColour)

        self.SetIndentationGuides(Preferences.STCIndentationGuides)

        self.Bind(wx.stc.EVT_STC_CHARADDED, self.OnAddChar, id=wxID_PYTHONSOURCEVIEW)

        # still too buggy
        self.Bind(wx.stc.EVT_STC_MODIFIED, self.OnModified, id=wxID_PYTHONSOURCEVIEW)
        #self.Bind(wx.EVT_FIX_PASTE, self.OnFixPaste)

        self.active = True

    def saveNotification(self):
        EditorStyledTextCtrl.saveNotification(self)
        # XXX update breakpoint filename

    def refreshCtrl(self):
        EditorStyledTextCtrl.refreshCtrl(self)
        self.setInitialBreakpoints()

    def processComment(self, textLst, idntBlock):
        return ['##%s'%l for l in textLst]

    def processUncomment(self, textLst, idntBlock):
        for idx in range(len(textLst)):
            if len(textLst[idx]) >= 2 and textLst[idx][:2] == '##':
                textLst[idx] = textLst[idx][2:]
        return textLst

    def processIndent(self, textLst, idntBlock):
        return ['%s%s'%(idntBlock, t) for t in textLst]

    def processDedent(self, textLst, idntBlock):
        indentLevel=len(idntBlock)
        for idx in range(len(textLst)):
            if len(textLst[idx]) >= indentLevel and \
              textLst[idx][:indentLevel] == idntBlock:
                textLst[idx] = textLst[idx][indentLevel:]
        return textLst

    def checkCallTipHighlight(self):
        if self.CallTipActive():
            pass

#---Call Tips-------------------------------------------------------------------

    def OnParamTips(self, event):
        if Preferences.autoRefreshOnCodeComplete:
            self.refreshModel()
        self.callTipCheck()

    def getTipValue(self, word, lnNo):
        """ Overwritten Mixin method, returns string to display as tool tip """
        module = self.model.getModule()
        objPth = word.split('.')
        safesplit = methodparse.safesplitfields

        if (len(objPth) == 2 or len(objPth) == 3) and objPth[0] == 'wx':
            wxPyTip = self.getFirstContinousBlock(
                       self.checkWxPyTips(module, word))
            if wxPyTip: return wxPyTip

        if len(objPth) == 1:
            res = self.getNameSig(objPth[0], module)
            if res is not None: return res

        cls = module.getClassForLineNo(lnNo)
        # inside classes
        if cls:
            if len(objPth) == 2 and objPth[0] == 'self':
                if cls.methods.has_key(objPth[1]):
                    return self.prepareModSigTip(objPth[1],
                          cls.methods[objPth[1]].signature)
                elif cls.super and type(cls.super[0]) is type(''):
                    return self.getFirstContinousBlock(
                      self.checkWxPyMethodTips(module, cls.super[0], objPth[1]))

            if len(objPth) == 2:
                methName, codeBlock = cls.getMethodForLineNo(lnNo)
                res = self.getNameMethodSig(objPth[0], objPth[1], module, codeBlock)
                if res is not None: return res


            if len(objPth) == 3 and objPth[0] == 'self':
                return self.getFirstContinousBlock(
                    self.getAttribSig(module, cls, objPth[1], objPth[2]))
        # global and function scope
        else:
            if len(objPth) == 2:
                codeBlock = module.getFunctionForLineNo(lnNo)
                res = self.getNameMethodSig(objPth[0], objPth[1], module, codeBlock)
                if res is not None: return res

        return self.checkShellTips(word)

    def getNameSig(self, name, module):
        if module.classes.has_key(name) and \
              module.classes[name].methods.has_key('__init__'):
            return self.prepareModSigTip(name,
                module.classes[name].methods['__init__'].signature)
        elif module.functions.has_key(name):
            return self.prepareModSigTip(name, module.functions[name].signature)
        elif __builtins__.has_key(name):
            return self.getFirstContinousBlock(__builtins__[name].__doc__)
        return None

    def checkShellTips(self, objPth):
        if self.model.editor.shell:
            return self.model.editor.shell.getTipValue(objPth, -1)
        else:
            return ''

    def checkWxPyTips(self, module, name):
        if module.imports.has_key('wx'):
            obj = wxNamespace.getWxObjPath(name)
            if obj:
                return self.prepareWxModSigTip(obj.__init__.__doc__)
        return ''

    def checkWxPyMethodTips(self, module, cls, name):
        if module.imports.has_key('wx'):
            Cls = wxNamespace.getWxObjPath(cls)
            if Cls and hasattr(Cls, name):
                meth = getattr(Cls, name)
                return self.prepareWxModSigTip(meth.__doc__)
        return ''

    def getNameMethodSig(self, name, method, module, codeBlock=None):
        if codeBlock:
            if name in codeBlock.locals:
                objType = codeBlock.locals[name].objtype
                res = self.getTypeSig(objType, method, module)
                if res is not None: return res
        if name in module.globals:
            objType = module.globals[name].signature
            res = self.getTypeSig(objType, method, module)
            if res is not None: return res

        return None

    def getAttribSig(self, module, cls, attrib, meth):
        if cls.attributes.has_key(attrib):
            objtype = cls.attributes[attrib][0].signature
            if module.classes.has_key(objtype) and \
                  module.classes[objtype].methods.has_key(meth):
                return module.classes[objtype].methods[meth].signature
            klass = wxNamespace.getWxClass(objtype)
            if klass:
                if hasattr(klass, meth):
                    return self.prepareWxModSigTip(getattr(klass, meth).__doc__)
        return ''

    sigTypeMap = {'dict': dict, 'list': list, 'string': str, 'tuple': tuple,
                  'number': int}

    def getTypeSig(self, objType, method, module):
        if self.sigTypeMap.has_key(objType):
            tpe = self.sigTypeMap[objType]
            try:
                return getattr(getattr(tpe, method), '__doc__')
            except AttributeError:
                pass

        if objType in module.classes and \
              module.classes[objType].methods.has_key(method):
            return self.prepareModSigTip(method,
                        module.classes[objType].methods[method].signature)
        meth = wxNamespace.getWxObjPath(objType+'.'+method)
        if meth and meth.__doc__:
            return self.prepareWxModSigTip(meth.__doc__)

        return None

    def prepareWxModSigTip(self, tip):
        if not tip:
            return ''
        paramStart = tip.find('(')
        if paramStart != -1:
            paramEnd = tip.rfind(')')
            if paramEnd != -1:
                return self.prepareModSigTip(tip[:paramStart],
                                             tip[paramStart+1:paramEnd]).strip()
        return tip.strip()

    def prepareModSigTip(self, name, paramsStr):
        if paramsStr.startswith('self,'):
            paramsStr = paramsStr[5:].strip()
        elif paramsStr == 'self':
            paramsStr = ''
        return '%s(%s)'%(name, paramsStr)

#---Code Completion-------------------------------------------------------------

    def OnCompleteCode(self, event):
        if Preferences.autoRefreshOnCodeComplete:
            self.refreshModel()
        self.codeCompCheck()

    def getCodeCompOptions(self, word, rootWord, matchWord, lnNo):
        #print 'getCodeCompOptions', word, rootWord, matchWord, lnNo
        """ Overwritten Mixin method, returns list of code completion names """
        objPth = rootWord.split('.')

        if objPth and objPth[0] == 'wx':
            return wxNamespace.getWxNamespaceForObjPath(rootWord)

        module = self.model.getModule()
        cls = module.getClassForLineNo(lnNo)
        if cls:
            if len(objPth) == 1:
                # obj attrs
                if objPth[0] == 'self':
                    return self.getAttribs(cls)
                # globals/locals
                elif objPth[0] == '':
                    if cls.super:
                        wrds = self.GetLine(lnNo).strip().split()
                        # check for def *, add inherited methods
                        if wrds and wrds[0] == 'def':
                            if isinstance(cls.super[0], moduleparse.Class):
                                return self.getAttribs(cls.super[0], methsOnly=True)
                            elif type(cls.super[0]) in types.StringTypes:
                                super = wxNamespace.getWxClass(cls.super[0])
                                if super:
                                    return self.getWxAttribs(super)
                    methName, meth = cls.getMethodForLineNo(lnNo)
                    return self.getCodeNamespace(module, meth)
                else:
                    methName, codeBlock = cls.getMethodForLineNo(lnNo)
                    res = self.getNameAttribs(objPth[0], module, codeBlock)
                    if res is not None: return res

            elif len(objPth) == 2:
                # attributes of attrs with known type
                if objPth[0] == 'self':
                    attrib = objPth[1]
                    return self.getAttribAttribs(module, cls, attrib)

        else:
            # handles, base classes in class declaration statement
            cls = module.getClassForLineNo(lnNo+1)
            if cls:
                return self.getAllClasses(module)
            # handles function and global scope
            if len(objPth) == 1 and objPth[0] == '':
                func = module.getFunctionForLineNo(lnNo)
                return self.getCodeNamespace(module, func)
            if len(objPth) == 1:
                codeBlock = module.getFunctionForLineNo(lnNo)
                res = self.getNameAttribs(objPth[0], module, codeBlock)
                if res is not None: return res

        return self.getShellNames(objPth)

    def importInShell(self, name, fromlist=()):
        locs = self.model.editor.shell.getShellLocals()
        try:
            mod = __import__(name, {}, locs, fromlist) 
        except Exception:
            # just swallow all errors, no way to guess what code could execute 
            # in the global scope of arbitrary modules
            return None
        
        if fromlist and hasattr(mod, fromlist[0]):
            return getattr(mod, fromlist[0])

        components = name.split('.') 
        for comp in components[1:]: 
            if hasattr(mod, comp):
                mod = getattr(mod, comp) 
        return mod 

    def getImportedShellObj(self, words):
        module = self.model.getModule()
        imports = module.imports.keys() + module.from_imports.keys() +\
                module.from_imports_names.keys()
        if self.model.editor.shell:
            shellLocals = self.model.editor.shell.getShellLocals()
            name = words[0]
            if name in imports:
                if Preferences.importOnCodeComplete and name not in shellLocals:
                    fromlist = []
                    if name in module.from_imports_names:
                        fromlist = [name]
                        name = module.from_imports_names[name]
                    
                    m = self.importInShell(name, fromlist)
                    if m is None:
                        raise ShellNameNotFound
                    shellLocals[name] = m

                if name in shellLocals:
                    obj = shellLocals[name]
                    for word in words[1:]:
                        if hasattr(obj, word):
                            obj = getattr(obj, word)
                        else:
                            raise ShellNameNotFound
                    return obj
        raise ShellNameNotFound

    def getShellNames(self, words):
        try:
            return ShellEditor.recdir(self.getImportedShellObj(words))
        except ShellNameNotFound:
            return []

    def getWxAttribs(self, cls, mems = None, methsOnly=False):
        if mems is None: mems = []

        for base in getattr(cls, '__bases__', ()):
            self.getWxAttribs(base, mems, methsOnly)

        # wx attrs are always methods
        mems.extend(dir(cls))
        return mems

    def getNameAttribs(self, name, module, codeBlock=None):
        if codeBlock:
            if name in codeBlock.locals:
                objType = codeBlock.locals[name].objtype
                res = self.getTypeAttribs(objType, module)
                if res is not None: return res
        if name in module.globals:
            objType = module.globals[name].signature
            res = self.getTypeAttribs(objType, module)
            if res is not None: return res

        return None

    def getTypeAttribs(self, objType, module):
        if self.attrTypeMap.has_key(objType):
            return self.attrTypeMap[objType]
        if objType in module.classes:
            return self.getAttribs(module.classes[objType])
        WxClass = wxNamespace.getWxClass(objType)
        if WxClass:
            return self.getWxAttribs(WxClass)
        return None

    def getAttribs(self, cls, methsOnly=False):
        loopCls = cls
        lst = []
        while loopCls:
            lst.extend(loopCls.methods.keys())
            if not methsOnly:
                lst.extend(loopCls.attributes.keys())

            if len(loopCls.super):
                prnt = loopCls.super[0]
                # Modules
                if isinstance(prnt, moduleparse.Class):
                    loopCls = prnt
                # Possible wxPython ancestor
                else:
                    WxClass = wxNamespace.getWxClass(prnt)
                    if WxClass:
                        lst.extend(self.getWxAttribs(WxClass))
                    loopCls = None
            else:
                loopCls = None

        return lst

    attrTypeMap = {'dict': dir({}), 'list': dir([]), 'string': dir(''),
                   'tuple': dir(()), 'number': dir(0)}

    def getAttribAttribs(self, module, cls, attrib):
        if cls.attributes.has_key(attrib):
            objtype = cls.attributes[attrib][0].signature
            if self.attrTypeMap.has_key(objtype):
                return self.attrTypeMap[objtype]
            elif module.classes.has_key(objtype):
                return self.getAttribs(module.classes[objtype])
            else:
                klass = wxNamespace.getWxClass(objtype)
                if klass:
                    return self.getWxAttribs(klass)
        return []

    def getCodeNamespace(self, module, block=None):
        names = []

        names.extend(module.imports.keys())
        names.extend(module.from_imports.keys())
        names.extend(module.from_imports_names.keys())
        names.extend(module.class_order)
        names.extend(module.function_order)
        names.extend(module.global_order)
        names.extend(__builtins__.keys())
        names.extend(keyword.kwlist)

        if block:
            names.extend(block.localnames())

        return names

    def getAllClasses(self, module):
        names = []
        names.extend(module.from_imports_names.keys())
        names.extend(module.class_order)

        return names

#-------Browsing----------------------------------------------------------------

    def findNameInModule(self, module, word):
        """ Find either a classname, global function or attribute in module """
        if module.classes.has_key(word):
            return module.classes[word].block.start-1
        elif module.functions.has_key(word):
            return module.functions[word].start-1
        elif module.globals.has_key(word):
            return module.globals[word].start-1
        else:
            return None

    def gotoName(self, module, word, currLineNo):
        line = self.findNameInModule(module, word)
        if line is not None:
            self.doClearBrwsLn()
            self.model.editor.addBrowseMarker(currLineNo)
            self.GotoLine(line)
            return True
        else:
            return False

    def handleBrwsObjAttrs(self, module, word, lineNo):
        cls = module.getClassForLineNo(lineNo)
        if cls:
            self.doClearBrwsLn()
            gotoLine = -1
            if cls.attributes.has_key(word):
                gotoLine = cls.attributes[word][0].start-1
            elif cls.methods.has_key(word):
                gotoLine = cls.methods[word].start-1
            elif cls.class_attributes.has_key(word):
                gotoLine = cls.class_attributes[word][0].start-1
            else:
                found, cls, block = module.find_declarer(cls, word, None)
                if found:
                    if type(block) == type([]):
                        gotoLine = block[0].start-1
                    else:
                        gotoLine = block.start-1
            if gotoLine != -1:
                self.model.editor.addBrowseMarker(lineNo)
                self.GotoLine(gotoLine)
            return True
        return False

    def handleBrwsWxNames(self, module, word, words, currLineNo):
        wxObj = wxNamespace.getWxObjPath(word)
        if wxObj is not None:
            if hasattr(wxObj, '__module__'):
                try: path, impType = self.model.findModule(wxObj.__module__)
                except ImportError: return False, None
                else:
                    if impType == 'package':
                        self.model.editor.addBrowseMarker(currLineNo)
                        model, ctrlr = self.model.editor.openOrGotoModule(
                              os.path.join(path, '__init__.py'))
                        return True, model
                    elif impType in ('name', 'module'):
                        self.model.editor.addBrowseMarker(currLineNo)
                        model, ctrlr = self.model.editor.openOrGotoModule(path)
                        if impType == 'name':
                            model.views['Source'].gotoName(model.getModule(), 
                                  words[-1], currLineNo)
                        return True, model
        return False, None
                

    def handleBrwsImports(self, module, word, currLineNo):
        words = word.split('.')

        # Standard imports
        if module.imports.has_key(word):
            self.doClearBrwsLn()

            try: path, impType = self.model.findModule(word)
            except ImportError: return False, None
            else:
                if impType == 'package':
                    self.model.editor.addBrowseMarker(currLineNo)
                    model, ctrlr = self.model.editor.openOrGotoModule(
                          os.path.join(path, '__init__.py'))
                    return True, model
                elif impType in ('name', 'module'):
                    self.model.editor.addBrowseMarker(currLineNo)
                    model, ctrlr = self.model.editor.openOrGotoModule(path)
                    return True, model
            return False, None
        # Handle module part of from module import name
        elif module.from_imports.has_key(word):
            try: path, impType = self.model.findModule(word)
            except ImportError: return False, None
            else:
                self.doClearBrwsLn()
                self.model.editor.addBrowseMarker(currLineNo)
                if impType == 'package':
                    path = os.path.join(path, '__init__.py')
                model, ctrlr = self.model.editor.openOrGotoModule(path)
                return True, model
        # Handle name part of from module import name
        elif module.from_imports_names.has_key(word):
            modName = module.from_imports_names[word]
            try: path, impType = self.model.findModule(modName, word)
            except ImportError: return False, None
            else:
                self.doClearBrwsLn()
                self.model.editor.addBrowseMarker(currLineNo)
                model, ctrlr = self.model.editor.openOrGotoModule(path)
                if impType == 'name':
                    model.views['Source'].gotoName(model.getModule(), word,
                          currLineNo)
                return True, model
        else:
            # Handle [package.]module.name
            if len(words) > 1:
                testMod = '.'.join(words[:-1])
                handled, model = self.handleBrwsImports(module, testMod, currLineNo)
                if handled is None:
                    return None, None # unhandled
                elif handled:
                    if not model.views['Source'].gotoName(model.getModule(),
                          words[-1], currLineNo):
                        wx.LogWarning(_('"%s" not found.')%words[-1])
                    return True, model
                else:
                    return False, None
            else:
                return None, None # unhandled

    def handleBrwsLocals(self, module, word, lineNo):
        # Check local names and parameters in methods and functions
        codeBlock = None
        cls = module.getClassForLineNo(lineNo)
        if cls:
            methName, codeBlock = cls.getMethodForLineNo(lineNo)
        else:
            codeBlock = module.getFunctionForLineNo(lineNo)

        if codeBlock:
            locals = codeBlock.localnames()
            if word in locals:
                self.doClearBrwsLn()
                self.model.editor.addBrowseMarker(lineNo)
                if word in codeBlock.locals.keys():
                    self.GotoLine(codeBlock.locals[word].lineno-1)
                else:
                    self.GotoLine(codeBlock.start-1)
                return True
        return False

    def handleBrwsRuntimeGlobals(self, word, currLineNo):
        # The current runtime values of the shell is inspected
        # as well as the wxPython namespaces
        if self.model.editor.shell:
            shellLocals = self.model.editor.shell.getShellLocals()
        else:
            shellLocals = {}

        if shellLocals.has_key(word):
            obj = shellLocals[word]
        #elif hasattr(wxNamespace, word):
        #    obj = getattr(wxNamespace, word)
        else:
            return False

        self.doClearBrwsLn()
        if hasattr(obj, '__init__') and type(obj.__init__) == types.MethodType:
            self.model.editor.addBrowseMarker(currLineNo)
            path = os.path.abspath(obj.__init__.im_func.func_code.co_filename)
            mod, cntrl = self.model.editor.openOrGotoModule(path)
            mod.views['Source'].GotoLine(obj.__init__.im_func.func_code.co_firstlineno -1)
        elif hasattr(obj, 'func_code'):
            self.model.editor.addBrowseMarker(currLineNo)
            path = os.path.abspath(obj.func_code.co_filename)
            mod, cntrl = self.model.editor.openOrGotoModule(path)
            mod.views['Source'].GotoLine(obj.func_code.co_firstlineno -1)
        else:
            return False
        return True

    def handleBrwsCheckImportStars(self, module, word, currLineNo):
        # try to match names from * imports modules currently open

        # Cache first time
        if not module.from_imports_star_cache:
            for starMod in module.from_imports_star:
                try:
                    module.from_imports_star_cache[starMod] = \
                          self.model.findModule(starMod)
                except ImportError: pass
        # work thru open * imported modules and try to match name
        for starMod in module.from_imports_star:
            try:
                res = module.from_imports_star_cache[starMod]
            except KeyError:
                res = None
                continue
            if res and self.model.editor.modules.has_key('file://'+res[0]):
                starModPage = self.model.editor.modules['file://'+res[0]]
                starModule = starModPage.model.getModule()
                lineNo = self.findNameInModule(starModule, word)
                if lineNo is not None:
                    self.model.editor.addBrowseMarker(currLineNo)
                    starModPage.focus()
                    starModPage.model.views['Source'].focus()
                    starModPage.model.views['Source'].GotoLine(lineNo)
                    return True
        return False

    def StyleVeto(self, style):
        """ Overridden from BrowseStyledTextCtrlMix, hook to block browsing
            over certain text styles """
        return style != 11

    def BrowseClick(self, word, line, lineNo, start, style):
        """ Overridden from BrowseStyledTextCtrlMix, jumps to declaration or
            opens module.

            Explicitly imported names are also handled.
        """
        module = self.model.getModule()
        words = word.split('.')
        debugger = self.model.editor.debugger

        if debugger and debugger.isDebugBrowsing():
            debugger.add_watch(word, True)
            return True
        # Obj names
        if len(words) >= 2 and words[0] == 'self':
            return self.handleBrwsObjAttrs(module, words[1], lineNo)
        # wx names
        if len(words) >= 2 and words[0] == 'wx':
            return self.handleBrwsWxNames(module, word, words, lineNo)
        # Imports
        handled, model = self.handleBrwsImports(module, word, lineNo)
        if handled is not None:
            return handled
        # Only non dotted names allowed past this point
        if len(words) != 1:
            return False
        # Check for module global classes, funcs and attrs
        if self.gotoName(module, word, lineNo):
            return True
        if self.handleBrwsLocals(module, word, lineNo):
            return True
        if self.handleBrwsRuntimeGlobals(word, lineNo):
            return True

        # As the last check, see if word is defined in any import * module
        if self.handleBrwsCheckImportStars(module, word, lineNo):
            return True

        return False

    def underlineWord(self, start, length):
        start, length = BrowseStyledTextCtrlMix.underlineWord(self, start, length)
        debugger = self.model.editor.debugger
        start, length = BrowseStyledTextCtrlMix.underlineWord(
            self, start, length)
        debugger = self.model.editor.debugger
        if debugger and debugger.isDebugBrowsing():
            word, line, lnNo, wordStart = self.getStyledWordElems(
                start, length)
            self.IndicatorSetForeground(0, Preferences.STCDebugBrowseColour)
            debugger.requestVarValue(word)
        else:
            self.IndicatorSetForeground(0, Preferences.STCCodeBrowseColour)

        return start, length

    def getBrowsableText(self, line, piv, lnStPs):
        return idWord(line, piv, lnStPs, object_delim)
##        debugger = self.model.editor.debugger
##        if debugger and debugger.isDebugBrowsing():
##            return idWord(line, piv, lnStPs, object_delim)
##        else:
##            return BrowseStyledTextCtrlMix.getBrowsableText(self, line, piv, lnStPs)

    def disableSource(self, doDisable):
        self.SetReadOnly(doDisable)
        #self.grayout(doDisable)

    def OnBrowseTo(self, event):
        word, line, lnNo, start, startOffset = self.getWordAtCursor()
        self.BrowseClick(word, line, lnNo, start, None)

#---Syntax checking-------------------------------------------------------------

    def checkChangesAndSyntax(self, lineNo=None):
        """ Called before moving away from a line """
        if not Preferences.checkSyntax:
            return
        if lineNo is None:
            lineNo = self.GetCurrentLine()
        if not Preferences.onlyCheckIfLineModified or \
              lineNo == self.damagedLine:
            slb, sle = ( self.GetStyleAt(self.PositionFromLine(lineNo)),
                         self.GetStyleAt(self.GetLineEndPosition(lineNo)-1) )
            line = self.GetLine(lineNo)
            self.checkSyntax( (line,), lineNo +1, self.GetLine,
                lineStartStyle = slb, lineEndStyle = sle)

    def indicateError(self, lineNo, errOffset, errorHint):
        """ Underline the point of error at the given line """
        # Display red squigly indicator underneath error
        errPos = self.PositionFromLine(lineNo-1)
        lineLen = self.LineLength(lineNo-1)
        nextLineLen = self.LineLength(lineNo)
        lenAfterErr = lineLen-errOffset+1
        styleLen = min(3, lenAfterErr)

        self.StartStyling(errPos+errOffset-2, wx.stc.STC_INDICS_MASK)
        self.SetStyling(styleLen, wx.stc.STC_INDIC1_MASK)
        # XXX I have to set the styling past the cursor position, why????
        self.SetStyling(lenAfterErr+nextLineLen, 0)#wx.stc.STC_INDIC0_MASK)

        if errorHint:
            self.model.editor.statusBar.setHint(errorHint, 'Error')

    def stripComment(self, line):
        segs = methodparse.safesplitfields(line, '#')
        if len(segs) > 1:
            line = segs[0] + ' '*(len(line)-len(segs[0])-1)+'\n'

        return line

    if_keywords = {'else':    'if 1',
                   'elif':    'if  ',
                  }
    try_keywords = {'except':  'try:pass',
                    'finally': 'try:pass',
                   }

    line_conts = ('(', '[', '{', '\\', ',')
    line_conts_ends = (')', ']', '}', ':', ',', '%')

    # Multiline strings, ignored currently based on scintilla style info
    ignore_styles = {6 : "'''", 7 : '"""'}

    syntax_errors = ('invalid syntax', 'invalid token')

    def checkSyntax(self, prevlines, lineNo, getPrevLine, compprefix='',
          indent='', contLinesOffset=0, lineStartStyle=0, lineEndStyle=0):
        # XXX Should also check syntax before saving.
        # XXX Multiline without brackets not caught
        # XXX Should check indent errors (multilines make this tricky)

        # XXX Unhandled cases:
        # XXX     ZopeCompanions 278
        # XXX     print a, b,
        # XXX         c, d
        errstr = 'Line %d valid '%lineNo
        prevline = prevlines[-1]
        stripprevline = prevline.strip()

        # Special case for blank lines
        if not stripprevline:
            self.model.editor.statusBar.setHint(errstr)
            return

        # Ignore multiline strings
        if lineStartStyle in self.ignore_styles.keys() or \
              lineEndStyle in self.ignore_styles.keys():
            self.model.editor.statusBar.setHint(errstr)
            return

        # Special case for \ followed by whitespace (don't strip it!)
        compstr = ''
        if stripprevline[-1] == '\\' and not compprefix:
            strs = prevline.split('\\')
            if strs[-1] and not strs[-1].strip():
                compstr = prevline.lstrip()

        # note, removes (flattens) indent
        if not compstr:
            compstr = compprefix+'\n'.join(\
                  [indent+line.strip() for line in prevlines])+'\n'

        try: import __future__
        except ImportError: compflags = 0
        else:
            # XXX Should check future imports from parsed module object
            # XXX Too expensive for now
            # mod = self.model.getModule()
            compflags = 0
            try: compflags = compflags | __future__.generators.compiler_flag
            except AttributeError: pass

        try:
            try:
                compile(compstr, '<editor>', 'single', compflags, 1)
            except TypeError:
                compile(compstr, '<editor>', 'single')
        except SyntaxError, err:
            err.lineno = lineNo
            errstr = err.__class__.__name__+': '+str(err)
            indentpl = prevline.find(stripprevline)
            if err[0] == 'unexpected EOF while parsing':
                errstr = 'incomplete (%d)'%lineNo
            elif err[0] == "'return' outside function":
                self.checkSyntax(prevlines, lineNo, getPrevLine,
                      'def func():\n', ' ')
                return
            elif err[0] == "'yield' outside function":
                self.checkSyntax(prevlines, lineNo, getPrevLine,
                      'def func():\n', ' ')
                return
            elif err[0] == 'expected an indented block':
                errstr = errstr + ' ignored'
            elif err[0] in ("'break' outside loop",
                  "'continue' not properly in loop"):
                self.checkSyntax(prevlines, lineNo, getPrevLine,
                      'while 1:\n', ' ')
                return
            elif err[0] == 'invalid token':
                self.indicateError(lineNo,
                      err.offset + indentpl - len(indent) - contLinesOffset,
                      'SyntaxError: %s'%err[0])
            #"can't assign to function call"
            # Invalid syntax
            else:
                if len(prevlines) == 1 and err.offset is not None and not contLinesOffset:
                    # Check for dedenting keywords
                    possblkeyword = stripprevline[:err.offset-len(indent)]
                    if possblkeyword in self.if_keywords.keys():
                        self.checkSyntax( (prevline.replace(possblkeyword,
                              self.if_keywords[possblkeyword], 1),),
                            lineNo, getPrevLine)
                        return
                    elif possblkeyword in self.try_keywords.keys():
                        if stripprevline[-1] == ':':
                            prevline = prevline.rstrip()+'pass\n'

                        self.checkSyntax( (self.try_keywords[possblkeyword],
                                           prevline), lineNo, getPrevLine)
                        return

                    # Check for line continueations
                    # XXX Lines ending on line_conts should be ignored
                    errpos = err.offset-len(indent)-1
                    if errpos < len(stripprevline) and \
                          stripprevline[errpos] in self.line_conts_ends:
                        ln = lineNo - 2

                        if stripprevline[-1] == '\\':
                            lines = prevline.rstrip()[:-1]+' '
                        else:
                            lines = prevline.rstrip()

                        errOffsetOffset = 0
                        while ln >= 0:
                            line = self.stripComment(getPrevLine(ln)[:-1])

                            rstripline = line.rstrip()
                            if rstripline and rstripline[-1] in self.line_conts:
                                # replace else, elif's with ifs
                                lstripline = line.lstrip()
                                if len(lstripline) >= 4:
                                    possblifkeyword = lstripline[:4]
                                    if possblifkeyword in self.if_keywords.keys():
                                        ##print 'replace if kw'
                                        rstripline = rstripline.replace(
                                              possblifkeyword,
                                              self.if_keywords[possblifkeyword], 1)

                                if rstripline[-1] == '\\':
                                    lines = rstripline[:-1] +' '+ lines
                                else:
                                    lines = rstripline + lines
                                errOffsetOffset = errOffsetOffset + len(rstripline)
                                ln = ln -1
                            # ignore blank or entirely commented lines
                            elif not rstripline:
                                ln = ln -1
                            else:
                                break

                        if errOffsetOffset:
                            self.checkSyntax((lines,), lineNo, getPrevLine,
                                  contLinesOffset = errOffsetOffset)
                            return

                if not err.offset:
                    erroffset = 0
                else:
                    erroffset = err.offset

                self.indicateError(lineNo,
                    erroffset + indentpl - len(indent) - contLinesOffset,
                    errstr)
                self.damagedLine = -1
                return

        except Exception, err:
            errstr = err.__class__.__name__+': '+str(err)

        if errstr:
            self.model.editor.statusBar.setHint(errstr)

        self.damagedLine = -1

#-------Events------------------------------------------------------------------
    def OnMarginClick(self, event):
        if event.GetMargin() == symbolMrg:
            DebuggingViewSTCMix.OnMarginClick(self, event)
        else:
            FoldingStyledTextCtrlMix.OnMarginClick(self, event)

    def OnRunToCursor(self, event):
        line = self.LineFromPosition(self.GetCurrentPos()) + 1
        self.addBreakPoint(line, temp=1, notify_debugger=0)
        # Avoid a race condition by sending the breakpoint
        # along with the "continue" instruction.
        temp_breakpoint = (self.model.filename, line)
        if self.model.app:
            model = self.model.app
        else:
            model = self.model
        model.debug(cont_if_running=1, cont_always=1,
                         temp_breakpoint=temp_breakpoint)

    def getWordAtCursor(self, delim=word_delim):
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.PositionFromLine(lnNo)
        line = self.GetCurLine()[0]
        piv = pos - lnStPs
        start, length = idWord(line, piv, lnStPs, delim)
        startOffset = start-lnStPs
        word = line[startOffset:startOffset+length]
        return word, line, lnNo, start, startOffset

    def OnContextHelp(self, event):
        Help.showContextHelp(self.getWordAtCursor()[0])

    def OnComment(self, event):
        selStartPos, selEndPos = self.GetSelection()
        if selStartPos != selEndPos:
            self.processSelectionBlock(self.processComment)
        else:
            self.GotoPos(self.PositionFromLine(self.LineFromPosition(selStartPos)))
            self.AddText('##')
            self.SetSelection(selStartPos, selStartPos)

    def OnUnComment(self, event):
        selStartPos, selEndPos = self.GetSelection()
        if selStartPos != selEndPos:
            self.processSelectionBlock(self.processUncomment)
        else:
            linePos = self.PositionFromLine(self.LineFromPosition(selStartPos))
            if self.GetTextRange(linePos, linePos+2) == '##':
                self.SetSelection(linePos, linePos+2)
                self.ReplaceSelection('')
                self.SetSelection(selStartPos, selStartPos)

    def OnIndent(self, event):
        selStartPos, selEndPos = self.GetSelection()
        if selStartPos != selEndPos:
            self.processSelectionBlock(self.processIndent)
        else:
            self.GotoPos(self.PositionFromLine(self.LineFromPosition(selStartPos)))
            self.AddText(Utils.getIndentBlock())
            self.SetSelection(selStartPos, selStartPos)

    def OnDedent(self, event):
        selStartPos, selEndPos = self.GetSelection()
        indentBlock = Utils.getIndentBlock()
        indentLevel = len(indentBlock)
        if selStartPos != selEndPos:
            self.processSelectionBlock(self.processDedent)
        else:
            linePos = self.PositionFromLine(self.LineFromPosition(selStartPos))
            if self.GetTextRange(linePos, linePos + indentLevel) == indentBlock:
                self.SetSelection(linePos, linePos + indentLevel)
                self.ReplaceSelection('')
                self.SetSelection(selStartPos, selStartPos)

    def OnAddSimpleApp(self, event):
        self.BeginUndoAction()
        try:
            self.InsertText(self.GetTextLength(), self.model.getSimpleRunnerSrc())
        finally:
            self.EndUndoAction()

    def OnStyle(self, event):
        pass

    def OnAddModuleInfo(self, event):
        self.refreshModel()
        prefs = Preferences.staticInfoPrefs.copy()
        self.model.addModuleInfo(prefs)
        self.updateEditor()

    def OnUpdateUI(self, event):
        EditorStyledTextCtrl.OnUpdateUI(self, event)

        if Preferences.braceHighLight:
            PythonStyledTextCtrlMix.OnUpdateUI(self, event)

    def OnAddChar(self, event):
        char = event.GetKey()
        # On enter indent to same indentation as line above
        # If ends in : indent xtra block
        lineNo = self.GetCurrentLine()
        self.damagedLine = lineNo
        if char == 10:
            pos = self.GetCurrentPos()
            prevline = self.GetLine(lineNo -1)

            self.doAutoIndent(prevline, pos)

            self.damagedLine = lineNo-1
            self.checkChangesAndSyntax(lineNo-1)
        elif char == 40 and Preferences.callTipsOnOpenParen:
            self.callTipCheck()

    def OnKeyDown(self, event):
        if self.CallTipActive():
            self.callTipCheck()

        key = event.GetKeyCode()

        # thx to Robert Boulanger
        if Preferences.handleSpecialEuropeanKeys:
            self.handleSpecialEuropeanKeys(event, Preferences.euroKeysCountry)

        if key in (wx.WXK_UP, wx.WXK_DOWN):
            self.checkChangesAndSyntax()
        # Tabbed indent
##        elif key == 9:
##            self.AddText(indentLevel*' ')
##            self.damagedLine = self.GetCurrentLine()
##            if not self.AutoCompActive(): return
        # Smart delete
        elif key == 8:
            selStartPos, selEndPos = self.GetSelection()
            if selStartPos == selEndPos:
                if self.GetUseTabs():
                    indtSze = 1
                else:
                    indtSze = self.GetTabWidth()
                line = self.GetCurLine()
                if len(line): line = line[0]
                else: line = ''
                pos = self.GetCurrentPos()
                self.damagedLine = self.LineFromPosition(pos)
                #ignore indenting when at start of line
                if self.PositionFromLine(self.LineFromPosition(pos)) != pos:
                    pos = pos -1
                    ln = self.LineFromPosition(pos)
                    ls = self.PositionFromLine(ln)
                    st = pos - ls
                    if not line[:st].strip():
                        self.SetSelection(ls + st/indtSze*indtSze, pos+1)
                        self.ReplaceSelection('')
                        return
        #event.Skip()
        BrowseStyledTextCtrlMix.OnKeyDown(self, event)

#---Meta comment----------------------------------------------------------------
    def OnAddCommentLine(self, event):
        pos = self.GetCurrentPos()
        ln = self.LineFromPosition(pos)
        ls = self.PositionFromLine(ln)
        self.InsertText(ls, '#-------------------------------------------'
                            '------------------------------------'+self.eol)
        self.SetCurrentPos(ls+4)
        self.SetAnchor(ls+4)

    def OnViewWhitespace(self, event):
        miid = self.menu.FindItem(_('View whitespace'))
        if self.menu.IsChecked(miid):
            mode = wx.stc.STC_WS_INVISIBLE
            self.menu.Check(miid, False)
        else:
            mode = wx.stc.STC_WS_VISIBLEALWAYS
            self.menu.Check(miid, True)

        self.SetViewWhiteSpace(mode)
#        self.menu.Check(miid, not self.menu.IsChecked(miid))

    def OnViewEOL(self, event):
        miid = self.menu.FindItem(_('View EOL characters'))
        check = not self.menu.IsChecked(miid)
        self.menu.Check(miid, check)
        self.SetViewEOL(check)

    # XXX 1st Xform, should maybe add beneath current method
    def OnCodeTransform(self, event):
        word, line, lnNo, start, startOffset = self.getWordAtCursor(object_delim)
        self.model.editor.addBrowseMarker(lnNo)
        # 1st Xform; Add method at cursor to the class
        if word.startswith('self.'):
            methName = word[5:]
            # Apply if there are changes to views
            self.model.refreshFromViews()
            module = self.model.getModule()
            cls = module.getClassForLineNo(lnNo)
            if cls and not cls.methods.has_key(methName):
                # Check if it looks like an event
                if len(methName) > 2 and methName[:2] == 'On' and (methName[2]
                                                       in string.uppercase+'_'):
                    parms = 'self, event'
                else:
                    parms = 'self, '

                module.addMethod(cls.name, methName, parms, [sourceconst.bodyIndent+'pass'], True)
                if cls.methods.has_key(methName):
                    lnNo = cls.methods[methName].start+1
                    self.model.refreshFromModule()
                    self.model.modified = True
                    self.model.editor.updateModulePage(self.model)
                    line2pos = self.PositionFromLine(lnNo)
                    self.SetCurrentPos(line2pos+8)
                    self.SetSelection(line2pos+8, line2pos+12)
                else:
                    print 'Method was not added'
        else:
            # 2nd Xform; Add inherited method call underneath method declation
            #            at cursor
            if line[:startOffset].strip() == 'def':
                self.model.refreshFromViews()
                module = self.model.getModule()
                cls = module.getClassForLineNo(lnNo)
                if cls and cls.super:
                    base1 = cls.super[0]
                    if type(base1) is type(''):
                        baseName = base1
                    else:
                        baseName = base1.name
                    methName, meth = cls.getMethodForLineNo(lnNo+1)
                    if meth:
                        # XXX Not tab aware
                        module.addLine('%s%s.%s(%s)'%(' '*startOffset, baseName,
                              word, meth.signature), lnNo+1)
                        self.model.refreshFromModule()
                        self.model.modified = True
                        self.model.editor.updateModulePage(self.model)

    def OnRefresh(self, event):
        if Preferences.autoReindent:
            self.model.reindent(False)
        EditorStyledTextCtrl.OnRefresh(self, event)

    def OnModified(self, event):
        modType = event.GetModificationType()
        linesAdded = event.GetLinesAdded()

        if self._blockUpdate: return

        # repair breakpoints
        if linesAdded:
            self.adjustBreakpoints(linesAdded, modType, event.GetPosition())

        # XXX The rest is too buggy
        event.Skip()
        return

        # Update module line numbers
        # module has to have been parsed at least once
        if linesAdded and self.model._module:
            lineNo = self.LineFromPosition(event.GetPosition())
            module = self.model.getModule()
            module.renumber(linesAdded, lineNo)

            #if linesAdded == 1:
            #    module.parseLineIsolated(self.GetLine(lineNo), lineNo)

            #self.model.editor.statusBar.setHint('update ren %d %d'%(linesAdded, lineNo))


class PythonDisView(EditorStyledTextCtrl, PythonStyledTextCtrlMix):
    viewName = 'Disassemble'
    viewTitle = _('Disassemble')
    
    breakBmp = 'Images/Debug/Breakpoints.png'
    def __init__(self, parent, model):
        wxID_PYTHONDISVIEW = wx.NewId()

        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONDISVIEW,
          model, (), -1)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONDISVIEW, ())

        self.active = True

    def refreshModel(self):
        # Do not update model
        pass

    def getModelData(self):
        return self.model.disassembleSource()

    def setModelData(self, data):
        pass

    def updateFromAttrs(self):
        self.SetReadOnly(True)

#-------------------------------------------------------------------------------

from Explorers import ExplorerNodes
ExplorerNodes.langStyleInfoReg.insert(0, ('Python', 'python',
      PythonStyledTextCtrlMix, 'stc-styles.rc.cfg') )
