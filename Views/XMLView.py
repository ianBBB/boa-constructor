#-----------------------------------------------------------------------------
# Name:        XMLView.py
# Purpose:
#
# Author:      Riaan Booysen
#              Based on xml tree example in wxPython demo
#
# Created:     2001/01/06
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys

import wx

from Utils import _

from EditorViews import EditorView


class XMLTreeView(wx.TreeCtrl, EditorView):
    viewName = 'XMLTree'
    viewTitle = _('XMLTree')
    
    gotoLineBmp = 'Images/Editor/GotoLine.png'

    def __init__(self, parent, model):
        id = wx.NewIdRef(count=1)
        wx.TreeCtrl.__init__(self, parent, id)#, style=wx.TR_HAS_BUTTONS | wx.SUNKEN_BORDER)
        EditorView.__init__(self, model,
          ((_('Goto line'), self.OnGoto, self.gotoLineBmp, ''),), 0)

        self.nodeStack = []
        self.locations = {}
        self._parser = None

        self.Bind(wx.EVT_KEY_UP, self.OnKeyPressed)

        self.active = True

    def buildTree(self, parent, dict):
        for item in dict.keys():
            child = self.AppendItem(parent, item, 0)
            if len(dict[item].keys()):
                self.buildTree(child, dict[item])
            self.Expand(child)

    def refreshCtrl(self):
        self.nodeStack = [self.AddRoot('Root')]
        self.loadTree(self.model.filename)
        self.Expand(self.nodeStack[0])
        return

    # Define a handler for start element events
    def startElement(self, name, attrs ):
        name = name.encode()
        if attrs:
            for k in attrs:
                name += ', %s=%s' % (k, attrs[k])
            
##            if attrs.has_key('class'):
##                if attrs.has_key('name'):
##                    name = '%s (%s:%s)' % (name, attrs['name'], attrs['class'])
##                else:
##                    name = '%s (%s)' % (name, attrs['class'])
##            else:
##                if attrs.has_key('name'):
##                    name = '%s :%s' % (name, attrs['name'])

        id = self.AppendItem(self.nodeStack[-1], name)
        self.nodeStack.append(id)
        if self._parser:
            self.locations[id] = (self._parser.CurrentColumnNumber, self._parser.CurrentLineNumber)

    def endElement(self,  name ):
        self.nodeStack = self.nodeStack[:-1]

    def characterData(self, data ):
        if data.strip():
            data = data.encode()
            self.AppendItem(self.nodeStack[-1], data)


    def loadTree(self, filename):
        # Create a parser

        from xml.parsers import expat
        self._parser = parser = expat.ParserCreate()

        # Tell the parser what the start element handler is
        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characterData

        # Parse the XML File
        parserStatus = parser.Parse(self.model.data, 1)

    def OnGoto(self, event):
        idx  = self.GetSelection()
        if idx.IsOk():
            if idx in self.locations:
                col, line = self.locations[idx]
                xmlSrcView = self.model.views['XML']
                xmlSrcView.focus()
                xmlSrcView.gotoLine(line)

    def OnKeyPressed(self, event):
        key = event.GetKeyCode()
        if key == 13:
            if self.defaultActionIdx != -1:
                self.actions[self.defaultActionIdx][1](event)

##class XMLTree(wx.TreeCtrl):
##    def __init__(self, parent, ID):
##        wx.TreeCtrl.__init__(self, parent, ID)
##        self.nodeStack = [self.AddRoot(Root)]
##
##    # Define a handler for start element events
##    def StartElement(self, name, attrs ):
##        if py2:
##            name = name.encode()
##        id = self.AppendItem(self.nodeStack[-1], name)
##        self.nodeStack.append(id)
##
##    def EndElement(self,  name ):
##        self.nodeStack = self.nodeStack[:-1]
##
##    def CharacterData(self, data ):
##        if data.strip():
##            if py2:
##                data = data.encode()
##            self.AppendItem(self.nodeStack[-1], data)
##
##
##    def LoadTree(self, filename):
##        # Create a parser
##        Parser = parsermodule.ParserCreate()
##
##        # Tell the parser what the start element handler is
##        Parser.StartElementHandler = self.StartElement
##        Parser.EndElementHandler = self.EndElement
##        Parser.CharacterDataHandler = self.CharacterData
##
##        # Parse the XML File
##        ParserStatus = Parser.Parse(open(filename,'r').read(), 1)
