#----------------------------------------------------------------------
# Name:        OGLViews.py
# Purpose:     Diagrammatic views on the source using the OGL lib.
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
print 'importing Views.OGLViews'

import pickle, os

import wx
import wx.lib.ogl as ogl

import Preferences, Utils
from Utils import _

from Preferences import IS

import EditorViews

# XXX It would be better to not apply persistent positions after creating shapes,
# XXX but to use positions when shape is created

# XXX Bug on right click in background

# Wishlist
# * Is the topological layout applicable to import diagrams? (They can be cyclic)
# * Optional hiding of classes in UMLView

ogl.OGLInitialize()

class RoundedRectangleShape(ogl.RectangleShape):
    def __init__(self, w=0.0, h=0.0):
        ogl.RectangleShape.__init__(self, w, h)
        self.SetCornerRadius(-0.3)

class MyEvtHandler(ogl.ShapeEvtHandler):
    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Redraw(dc)
        else:
            redraw = False
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []
            for s in shapeList:
                try:
                    if s and s.Selected():
                        # If we unselect it now then some of the objects in
                        # shapeList will become invalid (the control points are
                        # shapes too!) and bad things will happen...
                        toUnselect.append(s)
                except Exception, message: pass#print Exception, message

            shape.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)
                canvas.Redraw(dc)

    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)

    def OnSize(self, x, y):
        self.base_OnSize(x, y)

    def OnRightClick(self, x, y, keys, attachment):
        shape = self.GetShape()
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)

        if hasattr(self, 'menu') and self.menu:
            shape.GetCanvas().PopupMenu(self.menu, wx.Point(x, y))

    def OnRightDown(self, event):
        print "OnRightDown", event

#----------------------------------------------------------------------

incy = 45

class PersistentShapeCanvas(ogl.ShapeCanvas):
    ext = '.lay'
    def __init__(self, parent, shapes):
        ogl.ShapeCanvas.__init__(self, parent, style = 0)
        self.SetBackgroundColour(Preferences.vpOGLCanvasBackgroundColour)
        self.shapes = shapes

    def saveSizes(self, filename):
        """ Build a picklable dictionary of sizes/positions and save. """
        persProps = {}

        for shape in self.shapes:
            try:
                if hasattr(shape, 'unqPclName'):
                    persProps[shape.unqPclName] = shape.getPos()
            except:
                print 'error:', shape
                raise

        from Explorers.Explorer import openEx
        t = openEx(filename)
        t.save(t.currentFilename(), pickle.dumps(persProps))

    def printSizes(self, filename):
        """ Export the Canvas to Postscript """
        prdata = wx.PrintData()
        from Explorers.Explorer import openEx
        t = openEx(filename)
        prdata.SetFilename(t.currentFilename())
        dc = wx.PostScriptDC(prdata)
        if dc.Ok():
            dc.StartDoc('Export')
            self.Redraw(dc)
            dc.EndDoc()
            
            wx.LogMessage('Exported %s'%filename)

    def loadSizes(self, filename):
        from Explorers.Explorer import openEx, TransportError
        t = openEx(filename)
        try:
            persProps = pickle.loads(t.load())
        except SyntaxError:
            if wx.MessageBox(_('%s is possibly corrupt (cannot be unpickled), delete it?'\
                  'Default layout will be used.')%filename, _('Corrupt file'), 
                  style = wx.YES_NO | wx.ICON_EXCLAMATION) == wx.YES:
                # XXX update to use transport !!
                if filename[:7] != 'file://':
                    wx.LogMessage(_('Sorry, only supported on the filesystem'))
                else:
                    os.remove(filename[7:])

            raise TransportError(_('Corrupt layout file'))

        unmatchedPcls = persProps.keys()
        matchedShapes = []

        for shape in self.shapes:
            if persProps.has_key(shape.unqPclName):
                unmatchedPcls.remove(shape.unqPclName)
            else:
                unmatchedPcls.append(shape.unqPclName)

        for shape in self.shapes:
            if persProps.has_key(shape.unqPclName):
                pos = persProps[shape.unqPclName]
                shape.setPos(pos)

        self.redraw()

    def redraw(self):
        diagram = self.GetDiagram()
        canvas = diagram.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.shapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
#            shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)

class PerstShape:
    def __init__(self, unqPclName):
        self.unqPclName = unqPclName

    def setPos(self, pos):
        """Must be implemented for any class deriving from it, called
         after reading positions from pickle."""

    def getPos(self, pos):
        """Must be implemented for any class deriving from it, called
         before reading sizes into pickle."""


class PerstDividedShape(ogl.DividedShape, PerstShape):
    def __init__(self, unqPclName, width, height):
        ogl.DividedShape.__init__(self, width, height)
        PerstShape.__init__(self, unqPclName)

    def setPos(self, pos):
        '''Pos for divide shape, format:
         (width, height)'''

        self.SetX(pos[0])
        self.SetY(pos[1])


    def getPos(self):
        """Pos for divide shape, format:
         (width, height)"""

        return (self.GetX(), self.GetY())

    def FlushText(self):
        """This method retrieves the text from the shape
        regions and draws it. There seems to be a problem that
        the text is not normally drawn. """
        canvas = self.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        count = 0
        for region in self.GetRegions():
            region.SetFormatMode(4)
            self.FormatText(dc, region.GetText(), count)
            count = count + 1

class ScrollingContainer(wx.ScrolledWindow):
    scrollStepX = 10
    scrollStepY = 10
    def __init__(self, parent, size):
        wx.ScrolledWindow.__init__(self, parent, -1, style = wx.SUNKEN_BORDER)
        self.SetScrollbars(self.scrollStepX, self.scrollStepY,
                           size.x / self.scrollStepX, size.y / self.scrollStepY)

class PersistentOGLView(ScrollingContainer, EditorViews.EditorView):
    viewName = 'OGL'
    viewTitle = _('OGL')
    loadBmp = 'Images/Editor/Open.png'
    saveBmp = 'Images/Editor/Save.png'
    defSize = 2000

    def __init__(self, parent, model, actions = ()):
        ScrollingContainer.__init__(self, parent, wx.Size(self.defSize, self.defSize))
        EditorViews.EditorView.__init__(self, model,
          ((_('(Re)load diagram'), self.OnLoad, self.loadBmp, ''),
           (_('Save diagram'), self.OnSave, self.saveBmp, ''),
           (_('Print diagram to PostScript'), self.OnPrintToPS, '-', ''), 
           ('-', None, '-', ''),
           (_('Change size'), self.OnSetSize, '-', ''),
           )+actions)

        self.shapes = []
        self.canvas = PersistentShapeCanvas(self, self.shapes)
        self.canvas.SetSize(self.GetVirtualSize())

        self.canvas.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

        self.diagram = ogl.Diagram()
        self.canvas.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self.canvas)

        self.shapeMenu = None

        self.size = self.defSize

        self._loaded = False

        self.active = True

    def destroy(self):
        self.destroyShapes()
##        self.diagram.Destroy()
        EditorViews.EditorView.destroy(self)

    def destroyShapes(self):
        self.shapes[:] = []
        self.diagram.DeleteAllShapes()

    def refreshCtrl(self):
        layoutFile = os.path.splitext(self.model.filename)[0]+self.ext
        from Explorers.Explorer import TransportError
        try:
            self.canvas.loadSizes(layoutFile)
            self._loaded = True
        except TransportError:
            self._loaded = False

    def newLine(self, dc, fromShape, toShape):
        line = ogl.LineShape()
        line.SetCanvas(self.canvas)
        line.SetPen(Preferences.vpOGLLinePen)
        line.SetBrush(Preferences.vpOGLLineBrush)

        line.AddArrow(ogl.ARROW_ARROW)
        #pmf = wxPseudoMetaFile()
        #pmf.LoadFromMetaFile('Images/Views/UML/inherit.wmf', 10.0, 10.0)
        #line.AddArrow(ARROW_METAFILE, mf=pmf)
        line.MakeLineControlPoints(2)
        fromShape.AddLine(line, toShape)
        self.diagram.AddShape(line)
        line.Show(True)

        # for some reason, the shapes have to be moved for the line to show up...
        fromShape.Move(dc, fromShape.GetX(), fromShape.GetY())

    def newRegion(self, font, name, textLst, maxWidth, totHeight = 10):
        region = ogl.ShapeRegion()
        dc = wx.ClientDC(self.canvas)
        dc.SetFont(font)

        for text in textLst:
            w, h = dc.GetTextExtent(text)
            if w > maxWidth: maxWidth = w
            totHeight = totHeight + h + 0 # interline padding

        region.SetFont(font)
        region.SetText('\n'.join(textLst))
        #region._text = string.join(textLst, '\n')
        region.SetName(name)

        return region, maxWidth, totHeight

    def addShape(self, shape, x, y, pen, brush, text):
#        shape.SetDraggable(False)
        shape.SetCanvas(self.canvas)
        shape.SetX(x)
        shape.SetY(y)
        shape.SetPen(pen)
        shape.SetBrush(brush)
#        shape.SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.NORMAL, False))
        shape.AddText(text)
        shape.SetShadowMode(ogl.SHADOW_RIGHT)
        self.diagram.AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler()
        evthandler.menu = self.shapeMenu
        evthandler.view = self
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)

        return len(self.shapes) -1

    def setSize(self, size):
        nvsx, nvsy = size.x / self.scrollStepX, size.y / self.scrollStepY
        self.Scroll(0, 0)
        self.SetScrollbars(self.scrollStepX, self.scrollStepY, nvsx, nvsy)
        self.canvas.SetSize(self.GetVirtualSize())


    def OnLoad(self, event):
        self.canvas.loadSizes(os.path.splitext(self.model.filename)[0]+self.ext)

    def OnSave(self, event):
        self.canvas.saveSizes(os.path.splitext(self.model.filename)[0]+self.ext)

    def OnPrintToPS(self, event):
        self.canvas.printSizes(os.path.splitext(self.model.filename)[0]+'.ps')

    def OnSetSize(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter new canvas size (width==height)',
            'Size', `self.size`)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.size = int(dlg.GetValue())
                self.setSize(wx.Size(self.size, self.size))
        finally:
            dlg.Destroy()

    def OnRightClick1(self, event):
        print self.canvas.HitTest(event.GetX(), event.GetX())
        event.Skip()


class SortedUMLViewMix:
    """ Currently uses topological sort to make the UML diagram
    more readily readable on load.  Also resizes the diagram
    to the space taken by the actual diagram elements so that
    very large diagrams can be accommodated.

    The resulting diagrams are far more white-space-intensive
    than the original jumbles.  A more appropriate algorithm
    may be found by someone else.
    """
    def getShapeSize( self, shape ):
        """Return the size of a shape's representation, an abstraction point"""
        return shape.GetBoundingBoxMax()
    def getCurrentShape( self, className ):
        """Attempt to retrieve an already-existing class model object, another abstraction point"""
        return self.AllClasses.get( className )

    def buildShapes( self, dc ):
        """Retrieve the current module and build the graph elements

        Where possible, re-use the already-built class shapes.
        Uses toposort to attempt to arrange the shapes after
        they have been built.
        """
        module = self.model.getModule()
        routes = []
        nodes = []
        todo = [ module.createHierarchy() ]
        while todo:
            hierarchy = todo[0]
            for className in hierarchy.keys():
                if self.getCurrentShape( className ):
                    if className not in nodes:
                        nodes.append( className )
                else:
                    # build a new node...
                    if module.classes.has_key(className):
                        # this is a local class (defined in this module)
                        classModel = module.classes[className]
                        classShape = self.newClass(
                            (20, 30), (0, 0),
                            className,
                            classModel.methods.keys(),
                            classModel.attributes.keys()
                        )
                    else:
                        # external class
                        classShape = self.newExternalClass(
                            (20, 30), (0,0),
                            className,
                        )
                    self.AllClasses[className] = classShape
                    nodes.append( className )
                    classShape.SetId(1000 + len(self.AllClasses))
                # hierarchy maps the children of the classes by name
                if hierarchy.get( className ):
                    todo.append( hierarchy.get(className) )
                    children = hierarchy.get(className).keys()
                    for child in children:
                        if (className, child) not in routes:
                            routes.append( (className, child) )
            del todo[0]
        for parent, child in routes:
            self.newLine(dc, self.getCurrentShape(child), self.getCurrentShape(parent), )
        # now make it look nice...
        self.arrangeShapes( dc, nodes, routes)

    def arrangeShapes( self, dc, nodes, routes, whiteSpaceFactor = 1.1 ):
        """Given the nodes and routes (values are names only), arrange the shapes

        This could be called as an action after the initial display if prefered.
        """
        # okay, we've now built all of the nodes and collected all routes...
        generations = sort( nodes, routes )
        # now display the generations...
        # calculate width + height of all elements
        sizes = []
        for generation in generations:
            sizes.append([])
            for child in generation:
                sizes[-1].append( self.getShapeSize(self.getCurrentShape(child)))
        # calculate total width and total height
        width = 0
        height = 0
        widths = []
        heights = []
        for generation in sizes:
            currentWidth = 0
            currentHeight = 0
            for x,y in generation:
                if y > currentHeight:
                    currentHeight = y
                currentWidth = currentWidth + x
            # update totals
            if currentWidth > width:
                width = currentWidth
            height = height + currentHeight
            # store generation info
            widths.append( currentWidth )
            heights.append( currentHeight )
        # add in some whitespace so we can see lines...
        width = width * whiteSpaceFactor
        rawHeight = height
        height = height * whiteSpaceFactor
        verticalWhiteSpace = (height-rawHeight)/(len(generations)-1.0 or 2.0)
        self.setSize(wx.Size(int(width+50), int(height+50))) # fudge factors to keep some extra space
        # distribute each generation across the width
        # and the generations across height
        y = 0
        for currentWidth, currentHeight, generation in map( None, widths, heights, generations ):
            x = 0
            # whiteSpace is the space between any two elements...
            whiteSpace = (width - currentWidth)/(len(generation)-1.0 or 2.0)
            for className in generation:
                classShape = self.getCurrentShape(className)
                shapeX, shapeY = self.getShapeSize(classShape)
                # snap to diagram grid coords
                csX, csY = self.diagram.Snap((shapeX/2.0)+x, (shapeY/2.0)+y)
                # don't display until finished
                classShape.Move(dc, csX, csY, False)
                x = x + shapeX + whiteSpace
            y = y + currentHeight + verticalWhiteSpace


class RecursionError( OverflowError, ValueError ):
    """ Unable to calculate result because of recursive structure """

def sort(nodes, routes, noRecursion=0):
    """ Passed a list of node IDs and a list of source,dest ID routes
    attempt to create a list of stages where each sub list
    is one stage in a process.
    """
    children, parents = _buildChildrenLists(routes)
    # first stage is those nodes
    # having no incoming routes...
    stage = []
    stages = [stage]
    taken = []
    for node in nodes:
        if (not parents.get(node)):
            stage.append (node)
    if nodes and not stage:
        # there is no element which does not depend on
        # some other element!!!
        stage.append( nodes[0])
    taken.extend( stage )
    nodes = filter ( lambda x, l=stage: x not in l, nodes )
    while nodes:
        previousStageChildren = []
        nodelen = len(nodes)
        # second stage are those nodes
        # which are direct children of the first stage
        for node in stage:
            for child in children.get (node, []):
                if child not in previousStageChildren and child not in taken:
                    previousStageChildren.append(child)
                elif child in taken and noRecursion:
                    raise RecursionError( (child, node) )
        # unless they are children of other direct children...
        # TODO, actually do that...
        stage = previousStageChildren
        removes = []
        for current in stage:
            currentParents = parents.get( current, [] )
            for parent in currentParents:
                if parent in stage and parent != current:
                    # might wind up removing current...
                    if not current in parents.get(parent, []):
                        # is not mutually dependent...
                        removes.append( current )
        for remove in removes:
            while remove in stage:
                stage.remove( remove )
        stages.append( stage)
        taken.extend( stage )
        nodes = filter ( lambda x, l=stage: x not in l, nodes )
        if nodelen == len(nodes):
            if noRecursion:
                raise RecursionError( nodes )
            else:
                stages.append( nodes[:] )
                nodes = []
    return stages

def _buildChildrenLists (routes):
    childrenTable = {}
    parentTable = {}
    for sourceID,destinationID in routes:
        currentChildren = childrenTable.get( sourceID, [])
        currentParents = parentTable.get( destinationID, [])
        if not destinationID in currentChildren:
            currentChildren.append ( destinationID)
        if not sourceID in currentParents:
            currentParents.append ( sourceID)
        childrenTable[sourceID] = currentChildren
        parentTable[destinationID] = currentParents
    return childrenTable, parentTable

class UMLView(PersistentOGLView, SortedUMLViewMix):
    viewName = 'UML'
    viewTitle = _('UML')

    ext = '.umllay'
    showAttributes = 1
    showMethods = 1
    AllClasses = {}
    toggleAttrBmp = 'Images/Views/UML/attribute.png'
    toggleMethBmp = 'Images/Views/UML/method.png'

    def __init__(self, parent, model):
        PersistentOGLView.__init__(self, parent, model, (
            ('-', None, '-', ''),
            (_('Toggle Attributes'), self.OnToggleAttributes, self.toggleAttrBmp, ''),
            (_('Toggle Methods'), self.OnToggleMethods, self.toggleMethBmp, ''),
            ('-', None, '-', ''),
            (_('Force layout'), self.OnForceLayout, '-', ''),
        ))
        self.menuStdClass = wx.Menu()
        id = wx.NewId()
        self.menuStdClass.Append(id, _('Goto Source'))
        self.Bind(wx.EVT_MENU, self.OnGotoSource, id=id)
        id = wx.NewId()
        self.menuStdClass.Append(id, _('Goto Documentation'),)
        self.Bind(wx.EVT_MENU, self.OnGotoDoc, id=id)

        self.shapeMenu = self.menuStdClass

    def destroy(self):
        PersistentOGLView.destroy(self)
        self.menuStdClass.Destroy()

    def newClass(self, size, pos, className, classMeths, classAttrs):
        shape = PerstDividedShape(className, size[0], size[1])

        maxWidth = 10 #padding
        if not self.showAttributes: classAttrs = [' ']
        if not self.showMethods: classMeths = [' ']

        regionName, maxWidth, nameHeight = self.newRegion(
              Preferences.oglBoldFont, 'class_name', [className], maxWidth)
        regionAttribs, maxWidth, attribsHeight = self.newRegion(
              Preferences.oglStdFont, 'attributes', classAttrs, maxWidth)
        regionMeths, maxWidth, methsHeight = self.newRegion(
              Preferences.oglStdFont, 'methods', classMeths, maxWidth)

        totHeight = nameHeight + attribsHeight + methsHeight

        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        regionAttribs.SetProportions(0.0, 1.0*(attribsHeight/float(totHeight)))
        regionMeths.SetProportions(0.0, 1.0*(methsHeight/float(totHeight)))

        shape.AddRegion(regionName)
        shape.AddRegion(regionAttribs)
        shape.AddRegion(regionMeths)

        shape.SetSize(maxWidth + 10, totHeight + 10)

        shape.SetRegionSizes()

        idx = self.addShape(shape, pos[0], pos[1], Preferences.vpOGLClassShapePen,
          Preferences.vpOGLClassShapeBrush, '')

        shape.FlushText()

        return self.shapes[idx]

    def newExternalClass(self, size, pos, className):
        shape = PerstDividedShape(className, size[0], size[1])

        maxWidth = 10 #padding
        regionName, maxWidth, nameHeight = self.newRegion(
              Preferences.oglBoldFont, 'class_name', [className], maxWidth)
        totHeight = nameHeight
        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        shape.AddRegion(regionName)
        shape.SetSize(maxWidth + 10, totHeight + 10)
        shape.SetRegionSizes()

        idx = self.addShape(shape, pos[0], pos[1],
            Preferences.vpOGLExternalClassShapePen,
            Preferences.vpOGLExternalClassShapeBrush, '')

        shape.FlushText()

        return self.shapes[idx]

    def refreshCtrl(self):
        dc = wx.ClientDC(self.canvas)
        self.canvas.PrepareDC(dc)

        self.destroyShapes()
        self.AllClasses = {}

        # Do initial layout
        self.buildShapes(dc)
        # Try to load layout from a pickle
        PersistentOGLView.refreshCtrl(self)

    def OnToggleMethods(self, event):
        if self.showMethods == 1: self.showMethods = 0
        else: self.showMethods = 1
        return self.refreshCtrl()

    def OnToggleAttributes(self, event):
        if self.showAttributes == 1: self.showAttributes = 0
        else: self.showAttributes = 1
        return self.refreshCtrl()

    def OnGotoDoc(self, event):
        if self.menuClass:
            name = self.menuClass
            if self.model.views.has_key('Documentation') and \
              self.model.getModule().classes.has_key(name):
                srcView = self.model.views['Documentation']
                srcView.focus()
                module = self.model.getModule()
                #srcView.gotoLine(int(module.classes[name].block.start) -1)
            else:
                print _('Documentation View is not open')
        else:
            print _('No shape selected')

    def OnGotoSource(self, event):
        if self.menuClass:
            name = self.menuClass
            if self.model.views.has_key('Source') and \
              self.model.getModule().classes.has_key(name):
                srcView = self.model.views['Source']
                srcView.focus()
                module = self.model.getModule()
                srcView.gotoLine(int(module.classes[name].block.start) -1)
            else:
                print _('No source for selection')
        else:
            print _('No shape selected')

    ## This allows me to pop-up a menu for the shape. However it loses the
    ## main menu position (x, y) go to 0,0 after the skip
    def OnRightClick(self, event):
        """If the event occurs on one of our shapes, I want to pop-up a shape"""
        x, y = (event.m_x, event.m_y)
        hit = 0
        for (name, shape) in self.AllClasses.items():
            hit = shape.HitTest(x, y)
            if hit: break
        x, y = self.CalcScrolledPosition(x, y)
        if not hit:
            menu = self.generateMenu()
            self.PopupMenuXY(menu, x, y)
            menu.Destroy()
            return
        # If we reach this point, then we have a selected shape.
        # However, it may be a class or external
        if self.model.getModule().classes.has_key(name):
            (self.menuShape, self.menuClass) = (shape, name)
            self.PopupMenu(self.menuStdClass, wx.Point(x, y))
            (self.menuShape, self.menuClass) = (None, None)

    def OnForceLayout(self, event):
        dc = wx.ClientDC(self.canvas)
        self.canvas.PrepareDC(dc)

        self.destroyShapes()
        self.AllClasses = {}

        self.buildShapes(dc)

        self.canvas.redraw()

#-------------------------------------------------------------------------------

class ImportsView(PersistentOGLView):
    viewName = 'Imports'
    viewTitle = _('Imports')

    ext = '.implay'
    refreshBmp = 'Images/Editor/Refresh.png'

    def __init__(self, parent, model):
        PersistentOGLView.__init__(self, parent, model,
          (('-', None, '', ''),
           (_('Refresh'), self.OnRefresh, self.refreshBmp, ''))
        )
        self.relationships = None
        self.showImports = 1

    def newModule(self, size, pos, moduleName, importList):
        idx = self.addShape(PerstDividedShape(moduleName, size[0], size[1]),
          pos[0], pos[1],
          Preferences.vpOGLModuleShapePen,
          Preferences.vpOGLModuleShapeBrush, '')

        if not self.showImports: importList = [' ']

        maxWidth = 10 #padding

        regionName, maxWidth, nameHeight = self.newRegion(
              Preferences.oglBoldFont, 'module_name', [moduleName], maxWidth)
        regionClss, maxWidth, clssHeight = self.newRegion(
              Preferences.oglStdFont, 'methods', importList, maxWidth)

        totHeight = nameHeight + clssHeight

        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        regionClss.SetProportions(0.0, 1.0*(clssHeight/float(totHeight)))

        shape = self.shapes[idx]
        shape.AddRegion(regionName)
        shape.AddRegion(regionClss)

        shape.SetSize(maxWidth + 10, totHeight + 10)

        shape.SetRegionSizes()
        shape.FlushText()

        return shape, maxWidth + 10

    def refreshCtrl(self):
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)

        # Because of slow building process, cache after first time
        if not self.relationships:
            relations = self.model.buildImportRelationshipDict()
            self.relationships = relations
            self.destroyShapes()
        else:
            return
            #relations = self.relationships

        shapes = {}
        p = 10
        y = 20
        if hasattr(self.model, 'packageName'):
            packageName = self.model.packageName
        else:
            packageName = ''
        # Add shapes
        for rel in relations.keys():
            impLst = []
            for i in relations[rel].imports.keys():
                if i.startswith(packageName+'.'):
                    i = i[len(packageName)+1:]
                if relations.has_key(i):
                    impLst.append(i)
            for i in relations[rel].from_imports.keys():
                if i.startswith(packageName+'.'):
                    i = i[len(packageName)+1:]
                if relations.has_key(i):
                    impLst.append(i)

            shape, width = self.newModule((20, 30), (p, y), rel, relations[rel].classes.keys())
            shapes[rel] = (shape, impLst)
            p = p + width + 10
            if p > self.GetSize().x:
                p = 10
                y = y + 120

        # Add lines
        for module in shapes.keys():
            for line in shapes[module][1]:
                self.newLine(dc, shapes[module][0], shapes[line][0])

        PersistentOGLView.refreshCtrl(self)

    def OnRefresh(self, event):
        self.relationships = None
        self.refreshCtrl()


class AppPackageView(PersistentOGLView):
    viewName = 'Application packages'
    viewTitle = _('Application packages')

    ext = '.apklay'
    refreshBmp = 'Images/Editor/Refresh.png'

    def __init__(self, parent, model):
        PersistentOGLView.__init__(self, parent, model,
          (('-', None, '', ''),
           (_('Refresh'), self.OnRefresh, self.refreshBmp, ''))
        )
        self.relationships = None

    def newModule(self, size, pos, moduleName, importList):
        idx = self.addShape(PerstDividedShape(moduleName, size[0], size[1]),
          pos[0], pos[1], wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, '')

        maxWidth = 10 #padding

        regionName, maxWidth, nameHeight = self.newRegion(
              Preferences.oglBoldFont, 'module_name', [moduleName], maxWidth)
        regionClss, maxWidth, clssHeight = self.newRegion(
              Preferences.oglStdFont, 'methods', importList, maxWidth)

        totHeight = nameHeight + clssHeight

        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        regionClss.SetProportions(0.0, 1.0*(clssHeight/float(totHeight)))

        shape = self.shapes[idx]
        shape.AddRegion(regionName)
        shape.AddRegion(regionClss)

        shape.SetSize(maxWidth + 10, totHeight + 10)

        shape.SetRegionSizes()
        shape.FlushText()

        return shape, maxWidth + 10

    def refreshCtrl(self):
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)

        # Because of slow building process, cache after first time
        if not self.relationships:
            relations = self.model.buildImportRelationshipDict()
            self.relationships = relations
            self.destroyShapes()
        else:
            return
            #relations = self.relationships

        shapes = {}
        p = 10
        y = 20
        # Add shapes
        for rel in relations.keys():
            impLst = []
            for i in relations[rel].imports.keys():
                if relations.has_key(i): impLst.append(i)

            shape, width = self.newModule((20, 30), (p, y), rel, relations[rel].classes.keys())
            shapes[rel] = (shape, impLst)
            p = p + width + 10
            if p > self.GetSize().x:
                p = 10
                y = y + 120

        # Add lines
        for module in shapes.keys():
            for line in shapes[module][1]:
                self.newLine(dc, shapes[module][0], shapes[line][0])

        PersistentOGLView.refreshCtrl(self)

    def OnRefresh(self, event):
        self.relationships = None
        self.refreshCtrl()

##class __Cleanup:
##    cleanup = ogl.OGLCleanUp
####    def __del__(self):
##    def __del__():
##        self.cleanup()
##
### when this module gets cleaned up then wx.OGLCleanUp() will get called
##__cu = __Cleanup()
