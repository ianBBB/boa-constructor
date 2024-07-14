#-------------------------------------------------------------------------------
# Name:        BaseCompanions.py
# Purpose:     Classes that 'shadow' controls. They implement design time
#              behaviour and interfaces
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#-------------------------------------------------------------------------------

""" Classes that 'shadow' controls.

They implement design time behaviour and interfaces. Also used for inspectable
objects """

print('importing Companions')

import copy

import wx
# from wxCompat import wxNO_3D

import Preferences, Utils
from Utils import _

from PropEdit.PropertyEditors import *
from .Constructors import WindowConstr
import RTTI
from . import EventCollections

import methodparse, sourceconst

""" Design time classes
        These are companion classes to wxPython classes that capture
        design-time behaviour like
          * Constructor parameters
          * Events
          * Property editors

    XXX Todo XXX

    * write/wrap many more classes
    * streaming of properties
        * xml option
        * handling of default values
    * define event and name for popup menu on component
    * overrideable method or new multi inheritance class
      for palette creation in container companions,

"""

class Companion:
    """ Default companion, entity with a name and default documentation """
    def __init__(self, name):
        self.name = name
    def getPropertyHelp(self, propName):
        return propName

class CodeCompanion(Companion):
    pass

class DesignTimeCompanion(Companion):
    """ Base class for all companions participating in the design-time process.
    """
    handledConstrParams = ()
    suppressWindowId = False
    def __init__(self, name, designer):
        Companion.__init__(self, name)
        self.parentCompanion = None
        self.designer = designer
        # Design time window id
        self.dId = wx.NewIdRef(count=1)
        self.id = None

        # Property editors for properties whose types cannot be deduced
        self.editors = {'Class': ClassConstrPropEdit}
        # Enumerated values for the options of a property editor
        self.options = {}
        # Enumerated display values for the options of a property editor
        # XXX Change to something less generic
        self.names = {}

        # Companion methods that must be called when a property changes
        self.triggers = {'Name': self.SetName}
        # Companions for properties for which a companion can not be deduced
        self.subCompanions = {}
        # Parsers for special properties, given string value should
        # return valid wxPython object
        # The property evaluator should return a tuple of arguments
        # as customPropEvaluators are also used to initialise multi parameter
        # properties
        self.customPropEvaluators = {}
        # Properties that should be initialised thru the companion instead of
        # directly on the control. Usually this applies to 'write-only'
        # properties whose values cannot otherwise be determined
        # It's keyed on the property name and if the setter does not start
        # with Set*, it's keyed on the setter name
        self.initPropsThruCompanion = []
        # Run time dict of created collection companions
        self.collections = {}
        # Can't work, remove
        self.letClickThru = False
        # Mutualy depentent props
        # These props will all be refeshed in the inspector when any one of
        # them is updated
        self.mutualDepProps = []
        # Flag for controls which do not process mouse events correctly
        self.ctrlDisabled = False
        self.compositeCtrl = False
        #
        self.resourceImports = []

        # Parse objects for reading in and writing out source
        self.textConstr = None
        self.textPropList = []
        self.textEventList = []
        self.textCollInitList = []

    def destroy(self):
        del self.triggers

    def constructor(self):
        """ This method must be overriden by defining it in in another class
            and multiply inheriting from this new class and a
            DesignTimeCompanion derivative. This allows groups of components
            having the same constructor to be created."""

        return {}

    def extraConstrProps(self):
        return {}

#    def defaults(self):
#        return {}

    def getPropList(self):
        propList = RTTI.getPropList(self.control, self)
        pw = RTTI.PropertyWrapper('Class', 'CompnRoute', self.GetClass, self.SetClass)
        propList['constructor'].append(pw)
        return propList

    def GetClass(self, dummy=None):
        """ Used by the Inspector to display the type of the selected object """
        return self.textConstr.class_name

    def SetClass(self, value):
        """ Used by the Inspector to display the type of the selected object """
        self.textConstr.class_name = value

    def properties(self):
        """ Properties additional to those gleened thru reflection.
            Dictionary key=propname : type, val=getter, setter tuple.
            type = 'CtrlRoute' : Routed to get/setters on the control
                   'CompnRoute': Routed to get/setters on the companion
        """

        return {}

    def setConstr(self, constr):
        """ Define a new constructor for source code, called when a component is
            parsed from source
            See also: persistConstr """
        self.textConstr = constr

    def setProps(self, propList):
        # XXX Should companion initialise comp props instead of Designer?
        self.textPropList = propList

    def setCollInits(self, collInitList):
        self.textCollInitList = collInitList

    def setEvents(self, eventList):
        self.textEventList = eventList

    def getEvents(self):
        return self.textEventList

    def getWinId(self):
        return self.id

    def hideDesignTime(self):
        """ Property names of automatically picked up properties that should
            not be shown in the Inspector. """
        return []

    def dontPersistProps(self):
        """ Properties are live (i.e. read/write) at design time but whose
            changes won't be applied to source. This is for cascading type
            properties like Size vs ClientSize. Updating one will automatically
            update the other so only one of them has to be stored."""
        return ['Class']

    def onlyPersistProps(self):
        """ Properties that should not be applied at design-time and should
            only be applied to the source """
        return []

    def events(self):
        return []

    def editor(self):
        pass

    def vetoedMethods(self):
        return []

##    def links(self):
##        return []

    # Rename to links
    def dependentProps(self):
        """ These are properties that depend on other controls already
            being created. They will be initialised right at the end of
            the definition block
        """
        return []

    def applyRunTime(self):
        """ Properties whose value will be modifyable at design-time
            and whose changes will be applied to the source but will
            not be applied to the controls at design time e.g. Show/Enable.
        """
        pass

    def getPropEditor(self, prop):
        if prop in list(self.editors.keys()): return self.editors[prop]
        else: return None

    def getPropOptions(self, prop):
        if prop in list(self.options.keys()): return self.options[prop]
        else: return None

    def getPropNames(self, prop):

        if prop in self.names:
            return self.names[prop]
        else:
            return None

    def evtGetter(self, name):
        for evt in self.textEventList:
            if evt.event_name == name: return evt.trigger_meth
        return None

    def evtSetter(self, name, value):
        for evt in self.textEventList:
            if evt.event_name == name:
                evt.trigger_meth = value
                return

    def persistConstr(self, className, params):
        """ Define a new constructor for source code, called when creating a
            new component from the palette
            See also: setConstr """

        paramStrs = []
        for param in list(params.keys()):
            paramStrs.append('%s = %s'%(param, params[param]))

        # XXX Is frame name initialised ???
        self.textConstr = methodparse.ConstructorParse('self.%s = %s(%s)' %(
              self.name, className, ', '.join(paramStrs)))

        # if className == 'wx.StatusBar':  # PRUNE
        #     self.textConstr = methodparse.ConstructorParse('self.%s = %s(%s)' %(
        #           self.name, className, ', '.join(paramStrs)) + '\nself.SetStatusBar(self.%s)'%(self.name))
        #
        #     a=0
        # else:
        #     self.textConstr = methodparse.ConstructorParse('self.%s = %s(%s)' %(
        #           self.name, className, ', '.join(paramStrs)))
        # a=0


        self.designer.addCtrlToObjectCollection(self.textConstr)

    def persistCollInit(self, method, ctrlName, propName, params = {}):
        """ Define a new collection init method for source code, called when
            creating a new item in CollectionEditor
        """

        collInitParse = methodparse.CollectionInitParse(None, ctrlName, method,
          [], propName)

        self.parentCompanion.textCollInitList.append(collInitParse)

        self.designer.addCollToObjectCollection(collInitParse)

    def checkTriggers(self, name, oldValue, newValue):
        #trigger specially handled callbacks for property changes with consequences
        if name in self.triggers:
            self.triggers[name](oldValue, newValue)

    def getCompName(self):
        if id(self.control) == id(self.designer):
            return ''
        else:
            return self.name

    def persistProp(self, name, setterName, value):
        c = self.constructor()
        #constructor
        if name in c:
            self.textConstr.params[c[name]] = value
        #property
        elif name not in self.dontPersistProps():
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    prop.params = [value]
                    return

            self.textPropList.append(methodparse.PropertyParse( \
                None, self.getCompName(), setterName, [value], name))

    def persistedPropVal(self, name, setterName):
        c = self.constructor()
        #constructor
        if name in c:
            return self.textConstr.params[c[name]]
        #property
        elif name not in self.dontPersistProps():
            for prop in self.textPropList:
                try:
                    if prop.prop_setter == setterName:
                        return prop.params
                except:
                    #print 'except in persistprop'
                    raise
        return None

    def propRevertToDefault(self, name, setterName):
        """ Removes property methods from source and revert constructor
            parameters to default values """
        c = self.constructor()
        #constructor
        if name in c:
            defVal = self.designTimeSource()[c[name]]
            self.textConstr.params[c[name]] = defVal
        #property
        elif name not in self.dontPersistProps():
            idx = 0
            while idx < len(self.textPropList):
                prop = self.textPropList[idx]
                if prop.prop_setter == setterName:
                    del self.textPropList[idx]
                else:
                    idx = idx + 1

    def propIsDefault(self, name, setterName):
        """ Returns True if no modification has been made to the property
            or constructor parameter """
        c = self.constructor()
        #constructor
        if name in c:
            try:
                dts = self.designTimeSource()
            except TypeError:
                return True
            else:
                if c[name] in dts:
                    defVal = self.designTimeSource()[c[name]]
                    return self.textConstr.params[c[name]] == defVal
                else:
                    return True
        #property
        elif name not in self.dontPersistProps():
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    return False
        return True

    def persistEvt(self, name, value, wId = None):
        """ Add a source entry for an event or update the trigger method of
            am existing event. """
        for evt in self.textEventList:
            if evt.event_name == name:
                evt.trigger_meth = value
                return
        if self.control == self.designer or \
              not isinstance(self.control, wx.EvtHandler) or \
              isinstance(self.control, wx.Timer):
            comp_name = ''
        else:
            comp_name = self.name
        self.textEventList.append(methodparse.EventParse(None, comp_name, name,
                                                         value, wId))

    def evtName(self):
        return self.name

    def addIds(self, lst):
        if self.id is not None:
            # generate default win id for list when reserved one is used by control
            if self.id in EventCollections.reservedWxIds:
                wId = Utils.windowIdentifier(self.designer.GetName(), self.name)
            else:
                wId = self.id
            lst.append(wId)

    def renameEventListIds(self, wId):
        for evt in self.textEventList:
            if evt.windowid and evt.windowid not in EventCollections.reservedWxIds:
                evt.windowid = wId

    def setProp(self, name, value):
        """ Optional callback companions can override for extra functionality
            after updating a property e.g. refreshing """
        pass

    def SetName(self, oldValue, newValue):
        """ Triggered when the 'Name' property is changed """
        if newValue in self.designer.objects:
            wx.LogError(_('There is already an object named %s')%newValue)
        else:
            self.name = newValue
            self.designer.model.renameCtrl(oldValue, newValue)
            self.designer.renameCtrl(oldValue, newValue)

    def renameCtrl(self, oldName, newName):
        self.textConstr.comp_name = newName
        for prop in self.textPropList:
            prop.comp_name = newName
        for collInit in self.textCollInitList:
            collInit.renameCompName2(oldName, newName)
        for evt in self.textEventList:
            if evt.comp_name:
                evt.comp_name = newName

    def renameCtrlRefs(self, oldName, newName):
        """ Notification of a the rename of another control, used to fix up
            references
        """
        if self.textConstr:
            self.textConstr.renameCompName2(oldName, newName)
        for prop in self.textPropList:
            prop.renameCompName2(oldName, newName)

    def getPropNameFromSetter(self, setter):
        props = self.properties()
        for prop in list(props.keys()):
            if props[prop][1] and props[prop][1].__name__ == setter:
                return prop
        if setter[:3] == 'Set': return setter[3:]
        else: return setter

    def eval(self, expr):
        import PaletteMapping
        try:
            return PaletteMapping.evalCtrl(expr, self.designer.model.specialAttrs)
        except Exception as err:
            print((_('Illegal expression: %s')%expr))
            raise

    def defaultAction(self):
        """ Invoke the default property editor for this component,
            This can be anything from a custom editor to an event.
        """
        pass

    def notification(self, compn, action):
        """ Called after components are added and before they are removed.
            Used for initialisation or finalisation hooks in other
            components.
        """
        pass

    def registerResourceModule(self, name):
        """ Resource Module name that should be added to the import list """
        if name not in self.resourceImports:
            self.resourceImports.append(name)

    def writeResourceImports(self):
        """ Return import line that will be added to module
        """
        if not self.resourceImports:
            return ''
        else:
            return '\n'.join(['import %s'%mod for mod in self.resourceImports])

    def writeImports(self):
        """ Return import line that will be added to module
        """
        return ''

#---Source writing methods------------------------------------------------------
    def addContinuedLine(self, line, output, indent):
        if Preferences.cgWrapLines:
            if len(line) > Preferences.cgLineWrapWidth:
                segs = methodparse.safesplitfields(line, ',', True, (), ())
                line = sourceconst.bodyIndent+segs[0].lstrip()
                for seg in segs[1:]:
                    newLine = line +', '+ seg
                    if len(newLine) >= Preferences.cgLineWrapWidth:
                        output.append(line+',')
                        line = indent+' '*Preferences.cgContinuedLineIndent+seg
                    else:
                        line = newLine

        output.append(line)

    def writeConstructor(self, output, collectionMethod, stripFrmId=''):
        """ Writes out constructor and parameters for control
        """
        # Add constructor
        if self.textConstr:
            self.addContinuedLine(
                sourceconst.bodyIndent+self.textConstr.asText(stripFrmId),
                output, sourceconst.bodyIndent)

    nullProps = ('None', 'wx.NullBitmap', 'wx.NullIcon')
    def writeProperties(self, output, ctrlName, definedCtrls, deps, depLinks, stripFrmId=''):
        """ Write out property setters but postpone dependent properties.
        """
        # Add properties
        for prop in self.textPropList:
            # Skip blanked out props
            if len(prop.params) == 1 and prop.params[0] in self.nullProps:
                continue
            # Postpone dependent props
            if self.designer.checkAndAddDepLink(ctrlName, prop,
                  self.dependentProps(), deps, depLinks, definedCtrls):
                continue
            self.addContinuedLine(sourceconst.bodyIndent+prop.asText(stripFrmId),
                  output, sourceconst.bodyIndent)

    def writeEvents(self, output, module=None, stripFrmId=''):
        """ Write out EVT_* calls for all events. Optionally For every event
            definition not defined in source add an empty method declaration to
            the bottom of the class """
        for evt in self.textEventList:
            if evt.trigger_meth != _('(delete)'):
                self.addContinuedLine(
                      sourceconst.bodyIndent + evt.asText(stripFrmId),
                      output, sourceconst.bodyIndent)
                model = self.designer.model
                # Either rename the event or add if a new one
                # The first streamed occurrence will do the rename or add
                if (evt.prev_trigger_meth and module
                        and (evt.prev_trigger_meth in
                            module.classes[model.main].methods)):
                    module.renameMethod(model.main, evt.prev_trigger_meth,
                          evt.trigger_meth)
                elif module and not evt.trigger_meth in module.classes[model.main].methods:
                    module.addMethod(model.main, evt.trigger_meth,
                       'self, event', [sourceconst.bodyIndent + 'event.Skip()'])
            else:
                # remove the event if the trigger meth is 'delete'
                model = self.designer.model
                if module and evt.prev_trigger_meth in module.classes[model.main].methods:
                    module.removeMethod (model.main, evt.prev_trigger_meth)
    def writeCollections(self, output, collDeps, stripFrmId=''):
        """ Write out collection initialiser methods. """
        for collInit in self.textCollInitList:
            if collInit.getPropName() in self.dependentProps():
                self.addContinuedLine(
                    sourceconst.bodyIndent + collInit.asText(stripFrmId),
                    collDeps, sourceconst.bodyIndent)
            else:
                self.addContinuedLine(
                    sourceconst.bodyIndent + collInit.asText(stripFrmId),
                    output, sourceconst.bodyIndent)

    def writeDependencies(self, output, ctrlName, depLinks, definedCtrls,
          stripFrmId=''):
        """ Write out dependent properties if all the ctrls they reference
            have been created.
        """
        if ctrlName in depLinks:
            for prop, otherRefs in depLinks[ctrlName]:
                for oRf in otherRefs:
                    if oRf not in definedCtrls:
                        # special attrs are not 'reference dependencies'
                        if not hasattr(
                              self.designer.model.specialAttrs['self'], oRf):
                            break
                else:
                    self.addContinuedLine(
                          sourceconst.bodyIndent + prop.asText(stripFrmId),
                          output, sourceconst.bodyIndent)


class NYIDTC(DesignTimeCompanion):
    """ Blank holder for companions which have not been implemented."""
    host = 'Not Implemented'
    def __init__(self, name, designer, parent, ctrlClass):
        raise Exception(_('Not Implemented'))


class ControlDTC(DesignTimeCompanion):
    """ Visible controls created on a Frame and defined from
        _init_ctrls.
    """
    handledConstrParams = ('id', 'parent')
    windowIdName = 'id'
    windowParentName = 'parent'
    host = 'Designer'
    def __init__(self, name, designer, parent, ctrlClass):
        DesignTimeCompanion.__init__(self, name, designer)
        self.parent = parent
        self.ctrlClass = ctrlClass
        self.generateWindowId()
        self.container = False


    def designTimeControl(self, position, size, args = None):
        """ Create and initialise a design-time control """
        if args:
            self.control = self.ctrlClass(**args)
        else:
            self.control = self.ctrlClass(**self.designTimeDefaults(position, size))

        self.initDesignTimeControl()
        return self.control

    def designTimeDefaults(self, position = wx.DefaultPosition,
                                 size = wx.DefaultSize):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'Frame1', etc) """
        if not position: position = wx.DefaultPosition
        if not size: size = wx.DefaultSize


        dts = self.designTimeSource('wx.Point(%s, %s)'%(position.x, position.y),
          'wx.Size(%s, %s)'%(size.x, size.y))

        for param in list(dts.keys()):
            dts[param] = self.eval(dts[param])

        # # change windowIDName for those controls that require a different name.
        if self.ctrlClass.__name__ == 'ListView':
            self.windowIdName = 'winid'

        dts[self.windowParentName] = self.parent

        if not self.suppressWindowId:
            dts[self.windowIdName] = self.dId

        return dts

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control's source. 'parent' and 'id' handled automatically
        """
        return {}

    def generateWindowId(self):
        if self.designer:
            self.id = Utils.windowIdentifier(self.designer.GetName(), self.name)
        else: self.id = repr(wx.NewIdRef(count=1))

    def SetName(self, oldValue, newValue):
        DesignTimeCompanion.SetName(self, oldValue, newValue)
        self.updateWindowIds()
        if self.compositeCtrl:
            for ctrl in self.control.GetChildren():
                ctrl.SetName(newValue)

    def extraConstrProps(self):
        return {'Class': 'class'}

##    def GetClass(self, dummy):
##        return self.control.__class__.__name__
##
##    def SetClass(self, value):
##        raise 'Cannot change'

    def updateWindowIds(self):
        self.generateWindowId()
        if not self.suppressWindowId:
            EventCollections.renameCmdIdInDict(self.textConstr.params, self.windowIdName, self.id)
            self.renameEventListIds(self.id)

    def initDesignTimeEvents(self, ctrl):
        # XXX Uncommenting this causes a crash after the first
        # XXX OnMouseOver event
        # By pushing the eventhandler, even ctrls
        # that hook to the Mouse events will still cause
        # mouse event to fire (theoretically)
        # ctrl.PushEventHandler(self.designer.ctrlEvtHandler)
        self.designer.ctrlEvtHandler.connectEvts(ctrl, self.compositeCtrl)

    def initDesignTimeControl(self):
        #try to set the name
        try:
            self.control.SetName(self.name)
            if self.compositeCtrl:
                for ctrl in self.control.GetChildren():
                    ctrl.SetName(self.name)
                    ctrl._composite_child = 1
            self.control.SetToolTip(self.name)
            # Disabled controls do not pass thru mouse clicks to their parents on GTK :(
            if wx.Platform != '__WXGTK__' and self.ctrlDisabled:
                self.control.Enable(False)
        except:
            pass

        self.initDesignTimeEvents(self.control)

        self.popx = self.popy = 0

        self.control.Bind(wx.EVT_RIGHT_DOWN, self.designer.OnRightDown)
        # for wxMSW
#        EVT_COMMAND_RIGHT_CLICK(self.control, -1, self.designer.OnRightClick)
        # for wxGTK
        self.control.Bind(wx.EVT_RIGHT_UP, self.designer.OnRightClick)

    def beforeResize(self):
        pass
        #print 'beforeResize'

    def afterResize(self):
        pass
        #print 'afterResize'

    def updatePosAndSize(self):
        if self.textConstr and 'pos' in self.textConstr.params \
              and 'size' in self.textConstr.params:
            pos = self.control.GetPosition()
            size = self.control.GetSize()
            self.textConstr.params['pos'] = 'wx.Point(%d, %d)' % (pos.x, pos.y)
            self.textConstr.params['size'] = 'wx.Size(%d, %d)' % (size.x, size.y)

    def getDefCtrlSize(self):
        return 'wx.Size(%d, %d)'%(Preferences.dsDefaultControlSize.x,
                                 Preferences.dsDefaultControlSize.y)


    def getPositionDependentProps(self):
        return [('constr', 'Position'), ('prop', 'Position')]

    def getSizeDependentProps(self):
        return [('constr', 'Size'), ('prop', 'Size'), ('prop', 'ClientSize')]

class MultipleSelectionDTC(DesignTimeCompanion):
    """ Semi mythical class at the moment that will represent a group of
        selected objects. It's properties should represent the common subset
        of properties of the selection.

        Currently only used so the inspector has something to hold on to during
        multiple selection
    """

# sub properties (Font etc)
class HelperDTC(DesignTimeCompanion):
    """ Helpers are subobjects or enumerations of properties. """
    def __init__(self, name, designer, ownerCompanion, obj, ownerPropWrap):
        DesignTimeCompanion.__init__(self, name, designer)
        self.control = obj
#        self.obj = obj
        self.ownerCompn = ownerCompanion
        self.owner = ownerCompanion.control
        self.ownerPW = ownerPropWrap

        self.updateObjFromOwner()

    def updateObjFromOwner(self):
        """ The object to which a sub object is connected may change
            this method reconnects the property to the current object.
        """
        self.obj = self.ownerPW.getValue(self)
        self.ctrl = self.obj
        self.control = self.obj

    def updateOwnerFromObj(self):
        """ Changes to subobjects do not reflect in their owners
            automatically they have to be reassigned to their
            property
        """
        self.ownerPW.setValue(self.obj)

    def persistProp(self, name, setterName, value):
        """ When a subobject's property is told to persist, it
            should persist it's owner

           This is currently managed by the property editor
        """
        pass

# non-visual classes (Imagelists, etc)
class UtilityDTC(DesignTimeCompanion):
    """ Utility companions are 'invisible' components that
        are not owned by the Frame.

        Utilities are created before the frame and controls
        and defined in the _init_utils method.
    """

    host = 'Data'
    def __init__(self, name, designer, objClass):
        DesignTimeCompanion.__init__(self, name, designer)
        self.objClass = objClass
        self.editors['Name'] = NameConstrPropEdit

    def properties(self):
        props = DesignTimeCompanion.properties(self)
        props['Name'] = ('NoneRoute', None, None)
        return props

    def designTimeObject(self, args = None):
        if args:
            self.control = self.objClass(**args)
        else:
            self.control = self.objClass(**self.designTimeDefaults())

        return self.control

    def designTimeDefaults(self):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'Frame1', etc) """

        dts = self.designTimeSource()

        for param in list(dts.keys()):
            dts[param] = self.eval(dts[param])
        return dts

    def extraConstrProps(self):
        return {'Class': 'class'}

    def updateWindowIds(self):
        pass

    def updatePosAndSize(self):
        pass

# XXX Parents, from constructor or current selected container in designer
class WindowDTC(WindowConstr, ControlDTC):
    """ Defines the wxWindow interface overloading/defining specialised
        property editors. """
    def __init__(self, name, designer, parent, ctrlClass):
        ControlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'AutoLayout': BoolPropEdit,
                        'Shown': BoolPropEdit,
                        'Enabled': BoolPropEdit,
                        #'EvtHandlerEnabled': BoolPropEdit,
                        'Style': StyleConstrPropEdit,
                        #'Constraints': CollectionPropEdit,
                        'Name': NamePropEdit,
                        'Anchors': AnchorPropEdit,
                        'Sizer': SizerClassLinkPropEdit,
                        'SizeHints': TuplePropEdit,
                        'Cursor': CursorClassLinkPropEdit,
                        'Centered': EnumPropEdit,
                        'ThemeEnabled': BoolPropEdit,
                        'WindowVariant': EnumPropEdit,
                        'BackgroundStyle': EnumPropEdit,
                        })
        self.options['Centered'] = [None, wx.HORIZONTAL, wx.VERTICAL, wx.BOTH]
        self.names['Centered'] = {'None': None, 'wx.HORIZONTAL': wx.HORIZONTAL,
                                  'wx.VERTICAL': wx.VERTICAL, 'wx.BOTH': wx.BOTH}
        self.options['WindowVariant'] = [wx.WINDOW_VARIANT_NORMAL, 
              wx.WINDOW_VARIANT_SMALL, wx.WINDOW_VARIANT_MINI, 
              wx.WINDOW_VARIANT_LARGE]
        self.names['WindowVariant'] = {
            'wx.WINDOW_VARIANT_NORMAL': wx.WINDOW_VARIANT_NORMAL, 
            'wx.WINDOW_VARIANT_SMALL':  wx.WINDOW_VARIANT_SMALL, 
            'wx.WINDOW_VARIANT_MINI': wx.WINDOW_VARIANT_MINI, 
            'wx.WINDOW_VARIANT_LARGE': wx.WINDOW_VARIANT_LARGE}
        self.options['BackgroundStyle'] = [wx.BG_STYLE_SYSTEM, 
              wx.BG_STYLE_COLOUR, wx.BG_STYLE_CUSTOM]
        self.names['BackgroundStyle'] = {
            'wx.BG_STYLE_SYSTEM': wx.BG_STYLE_SYSTEM, 
            'wx.BG_STYLE_COLOUR': wx.BG_STYLE_COLOUR, 
            'wx.BG_STYLE_CUSTOM': wx.BG_STYLE_CUSTOM}
        self.triggers.update({'Size'     : self.SizeUpdate,
                              'Position' : self.PositionUpdate})
        self.customPropEvaluators.update({'Constraints': self.EvalConstraints,
                                          'SizeHints': self.EvalSizeHints,})

        self.windowStyles = ['wx.CAPTION', 'wx.MINIMIZE_BOX', 'wx.MAXIMIZE_BOX',
            'wx.SIMPLE_BORDER', 'wx.DOUBLE_BORDER',
            'wx.SUNKEN_BORDER', 'wx.RAISED_BORDER', 'wx.STATIC_BORDER', 
            'wx.TRANSPARENT_WINDOW', 'wx.TAB_TRAVERSAL',
            'wx.WANTS_CHARS', 'wx.NO_FULL_REPAINT_ON_RESIZE', 'wx.VSCROLL', 
            'wx.HSCROLL', 'wx.CLIP_CHILDREN', 'wx.NO_BORDER', 'wx.ALWAYS_SHOW_SB']
        
        self.mutualDepProps = ['Value', 'Title', 'Label']

        #import UtilCompanions
        #self.subCompanions['Constraints'] = UtilCompanions.IndividualLayoutConstraintOCDTC
        #self.subCompanions['SizeHints'] = UtilCompanions.SizeHintsDTC
        self.anchorSettings = []
        self._applyConstraints = False
        self.initPropsThruCompanion = ['SizeHints', 'Cursor', 'Center', 'Sizer']
        self._sizeHints = (-1, -1, -1, -1)
        self._cursor = wx.NullCursor
        self._centered = None

    def properties(self):
        return {'Shown': ('CompnRoute', self.GetShown, self.Show),
                'Enabled': ('CompnRoute', self.GetEnabled, self.Enable),
                'ToolTipString': ('CompnRoute', self.GetToolTipString, self.SetToolTip),
                'Anchors': ('CompnRoute', self.GetAnchors, self.SetConstraints),
                'SizeHints': ('CompnRoute', self.GetSizeHints, self.SetSizeHints),
                'Cursor': ('CompnRoute', self.GetCursor, self.SetCursor),
                'Centered': ('CompnRoute', self.GetCentered, self.Center),
                'Sizer': ('CompnRoute', self.GetSizer, self.SetSizer),
                }

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':  position,
                'size': self.getDefCtrlSize(),
                'name': repr(self.name),
                'style': '0'}

    def dependentProps(self):
        return ['Cursor']

    def onlyPersistProps(self):
        return ['Show', 'Enable']

    def hideDesignTime(self):
        return ['NextHandler', 'PreviousHandler', 'EventHandler', 'EvtHandlerEnabled',
                'Id', 'Caret', 'WindowStyleFlag', 'ToolTip', 'Title', 'Rect',
                'DragTarget', 'DropTarget', 'Cursor', 'VirtualSize', 'Sizer',
                'ContainingSizer', 'Constraints', 'DefaultItem', 'Validator',
                'WindowStyle', 'AcceleratorTable', 'ClientRect', 'ExtraStyle',
                'LayoutDirection']

    def dontPersistProps(self):
        return ControlDTC.dontPersistProps(self) + ['ClientSize']
    def applyRunTime(self):
        return ['Shown', 'Enabled', 'EvtHandlerEnabled']
    def events(self):
        return ['MiscEvent', 'MouseEvent', 'FocusEvent', 'KeyEvent', 'HelpEvent']

    def notification(self, compn, action):
        if action == 'delete':
            if self._cursor and repr(self._cursor) == repr(compn.control):
                self.propRevertToDefault('Cursor', 'SetCursor')
                self.SetCursor(wx.NullCursor)
        # XXX sizer

    def persistProp(self, name, setterName, value):
        if setterName == 'SetSizeHints':
            minW, minH, maxW, maxH = self.eval(value)
            newParams = [repr(minW), repr(minH), repr(maxW), repr(maxH)]
            # edit if exists
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    prop.params = newParams
                    return
            # add if not defined
            self.textPropList.append(methodparse.PropertyParse( None,
                self.getCompName(), setterName, newParams, 'SetSizeHints'))
        elif setterName == 'SetSizer':
            sizerList = self.designer.getSizerConnectList()
            if sizerList is not None:
                for prop in sizerList:
                    if prop.prop_setter == setterName and \
                          prop.comp_name == self.getCompName():
                        if value == 'None':
                            sizerList.remove(prop)
                        else:
                            prop.params = [value]
                        return

                if value != 'None':
                    sizerList.append(methodparse.PropertyParse(
                          None, self.getCompName(), setterName, [value], name))
        else:
            ControlDTC.persistProp(self, name, setterName, value)

    def propIsDefault(self, propName, setterName):
        if setterName == 'SetSizer':
            scl = self.designer.getSizerConnectList()
            if scl:
                for connProp in self.designer.getSizerConnectList():
                    if connProp.comp_name == self.getCompName():
                        return False
            return True
        else:
            return ControlDTC.propIsDefault(self, propName, setterName)

#---ToolTips--------------------------------------------------------------------
    def GetToolTipString(self, blah):
        return self.control.GetToolTip().GetTip()

    def SetToolTip(self, value):
        self.control.SetToolTip(value)

#---Anchors---------------------------------------------------------------------
    from wx.lib.anchors import LayoutAnchors

    def writeImports(self):
        imports = ControlDTC.writeImports(self)
        if self.anchorSettings:
            return '\n'.join( (imports,
                   'from wx.lib.anchors import LayoutAnchors') )
        else:
            return imports

    def GetAnchors(self, compn):
        if self.anchorSettings:
            return self.LayoutAnchors(*([self.control] + self.anchorSettings))
        else:
            return None

    # Named like the wxWindow method to override it when generating code
    def SetConstraints(self, value):
        curVal = self.control.GetConstraints()
        if curVal != value:
            self.control.SetConstraints(value)
        if self.designer.selection:
            self.designer.selection.updateAnchors()
        elif self.designer.multiSelection:
            for selection in self.designer.multiSelection:
                selection.updateAnchors()
        self.designer.inspector.propertyUpdate('Anchors')

    def EvalConstraints(self, exprs, objects):
        if exprs[0].startswith('LayoutAnchors'):
            ctrl, left, top, right, bottom = \
             methodparse.safesplitfields(exprs[0][len('LayoutAnchors')+1:-1], ',')
            ctrl, left, top, right, bottom = (objects[ctrl], self.eval(left),
                  self.eval(top), self.eval(right), self.eval(bottom))
            self.anchorSettings = [left, top, right, bottom]
            return (self.LayoutAnchors(ctrl, left, top, right, bottom), )
        return (None,)

    def updateAnchors(self, flagset, value):
        if not self.anchorSettings:
            self.defaultAnchors()

        for idx in range(4):
            if flagset[idx]:
                self.anchorSettings[idx] = value

    def removeAnchors(self):
        self.anchorSettings = []
        idx = 0
        while idx < len(self.textPropList):
            prop = self.textPropList[idx]
            if prop.prop_setter == 'SetConstraints' and \
                  prop.params[0].startswith('LayoutAnchors'):
                del self.textPropList[idx]
                break
            else:
                idx = idx + 1

    def defaultAnchors(self):
        self.anchorSettings = [True, True, False, False]

    def applyConstraints(self):
        left, top, right, bottom = self.anchorSettings
        self.control.SetConstraints(
            self.LayoutAnchors(self.control, left, top, right, bottom))

    def beforeResize(self):
        lc = self.control.GetConstraints()
        self._applyConstraints = lc != None and self.anchorSettings
        if self._applyConstraints:
            self.SetConstraints(None)

    def afterResize(self):
        if self._applyConstraints and self.anchorSettings:
            self.applyConstraints()
        elif self.designer.sizersView and hasattr(self.control, '_in_sizer'):
            szr = self.control._in_sizer
            if szr:
                for si in szr.GetChildren():
                    if si.IsWindow():
                        if si.GetWindow() == self.control:
                            p = self.control.GetPosition()
                            s = self.control.GetSize()
                            #si.SetDimension(p, s)
                            si.SetInitSize(s.width, s.height)
                            #szr.Layout()
                            #self.designer.sizersView.layoutSizers()
                            parent = self.control.GetParent()
                            if parent:
                                wx.PostEvent(parent, wx.SizeEvent(
                                    parent.GetSize(), parent.GetId()))
                                wx.CallAfter(parent.Refresh)#relayoutCtrl(self.designer)
                            #self.designer.model.editor.setStatus('Sizer item update %s, %s'%(p, s))
                            break


#---Designer updaters-----------------------------------------------------------
    def SizeUpdate(self, oldValue, newValue):
        if self.designer.selection:
            self.designer.selection.selectCtrl(self.control, self)
            self.designer.selection.moveCapture(self.control, self, wx.Point(0, 0))

    def PositionUpdate(self, oldValue, newValue):
        if self.designer.selection:
            self.designer.selection.selectCtrl(self.control, self)
            self.designer.selection.moveCapture(self.control, self, wx.Point(0, 0))

#---Size hints------------------------------------------------------------------
    def GetSizeHints(self, dummy):
        return self._sizeHints

    def SetSizeHints(self, value):
        self._sizeHints = value
        self.control.SetSizeHints(value[0], value[1], value[2], value[3])

    def EvalSizeHints(self, exprs, objects):
        res = []
        for expr in exprs:
            res.append(self.eval(expr))
        return tuple(res)

#---Cursors---------------------------------------------------------------------
    def GetCursor(self, x):
        return self._cursor
    def SetCursor(self, value):
        self._cursor = value
        self.control.SetCursor(value)

#---Sizers----------------------------------------------------------------------
    def GetSizer(self, x):
        return self.control.GetSizer()
    def SetSizer(self, value):
        if value is not None:
            self.control._has_sizer = value
            value._has_control = self.control
        else:
            if hasattr(self.control, '_has_sizer'):
                szr = self.control._has_sizer
                if szr:
                    if hasattr(szr, '_has_control'):
                        del szr._has_control
                del self.control._has_sizer

        self.control.SetSizer(value)

        if value is not None:
            value.Layout()
            self.designer.relayoutCtrl(self.control)

#-------------------------------------------------------------------------------

    def GetCentered(self, dummy):
        return self._centered
    def Center(self, value):
        self._centered = value
        if value:
            self.control.Center(value)

    def GetShown(self, x):
        for prop in self.textPropList:
            if prop.prop_setter == 'Show':
                return int(prop.params[0].lower() == 'true')
        return 1

    def Show(self, value):
        pass

    def GetEnabled(self, x):
        for prop in self.textPropList:
            if prop.prop_setter == 'Enable':
                return int(prop.params[0].lower() == 'true')
        return 1

    def Enable(self, value):
        pass


class ChoicedDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Choices'] = ChoicesConstrPropEdit

class ContainerDTC(WindowDTC):
    """ Parent for controls that contain/own other controls """
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.container = True

class CollectionDTC(DesignTimeCompanion):
    """ Companions encapsulating list maintaining behaviour into a single
        property
        Maintains an index which points to the currently active item in the
        collection
    """

    propName = 'undefined'
    insertionMethod = 'undefined'
    deletionMethod = 'undefined'
    displayProp = 'undefined'
    indexProp = 'undefined'
    sourceObjName = 'parent'

    additionalMethods = {}

    def __init__(self, name, designer, parentCompanion, ctrl):
        DesignTimeCompanion.__init__(self, name, designer)
        from Views.CollectionEdit import CollectionEditor
        self.CollEditorFrame = CollectionEditor
        self.control = ctrl
        self.setCollectionMethod()
        self.index = 0
        self.parentCompanion = parentCompanion

    def setCollectionMethod(self):
        self.collectionMethod = '_init_coll_%s_%s' %(self.name, self.propName)

    def setIndex(self, index):
        self.index = index
        self.setConstr(self.textConstrLst[index])

    def setConstrs(self, constrLst, inits, fins):
        self.initialisers = inits
        self.finalisers = fins

        self.textConstrLst = constrLst

    def renameCtrl(self, oldName, newName):
        DesignTimeCompanion.renameCtrl(self, oldName, newName)
        self.setCollectionMethod()

    def renameCtrlRefs(self, oldName, newName):
        # textConstr and textPropList not used in collections
        # DesignTimeCompanion.renameCtrlRefs(self, oldName, newName)
        for constr in self.textConstrLst:
            constr.renameCompName2(oldName, newName)

    def getCount(self):
        return len(self.textConstrLst)

    def getDisplayProp(self):
        tcl = self.textConstrLst[self.index]
        if tcl.method != self.insertionMethod:
            if tcl.method in self.additionalMethods:
                displayProp = self.additionalMethods[tcl.method][1]
            else:
                return '-'
        else:
            #INFO Code to take care of different parameter names in a menu item for item text. When Appending to a menu,
            # it's called an 'item' but in the menu item properties, its called 'text'.
            displayProp = None
            if 'kind' in tcl.params.keys():
                if tcl.params['kind'] == 'wx.ITEM_NORMAL':
                    displayProp = 'item'
                else:
                    displayProp = self.displayProp
            else:
                displayProp = self.displayProp

        if displayProp in tcl.params:
            propSrc = tcl.params[displayProp]
            if propSrc and (propSrc[0] in ("'", '"') or propSrc[:2] in ('u"', "u'")):
                return self.eval(propSrc)
            else:
                return propSrc
        else:
            return '-'

    def initialiser(self):
        """ When overriding, append this after derived initialiser """
        return ['']

    def finaliser(self):
        """ When overriding, append this before derived finaliser """
        return []

    def appendItem(self, method=None, srcParams={}):
        self.index = self.getCount()
        if method is None:
            method = self.insertionMethod
        src = self.designTimeSource(self.index, method)        
        src.update(srcParams)
        collItemInit = methodparse.CollectionItemInitParse(None,
          self.sourceObjName, method, src)

### change txt to item.

        self.textConstrLst.append(collItemInit)
        self.setConstr(collItemInit)

#PRUNE
# currently working in this area. The fields/properties collected by the code cause an error.
# A field called "text" causes the problem. The initial solution was to just remove the field from
# the dic to stop the error but this causes other problems downstream when the item is added to the menu.
#  I need to revert this code back to original and look at it more closely. These fields are found by
#  introspection so they should be correct. Maybe its the adding process. More work here to understand
#  it and resolve.
        self.applyDesignTimeDefaults(collItemInit.params, method)

        return collItemInit
#prune
        #Removing text field from dic to match wx append call.
        # intermediate_dic = collItemInit.params.copy()  # temp work around.
        # intermediate_dic.pop('text')
        # self.applyDesignTimeDefaults(intermediate_dic, method)
        #
        # return intermediate_dic

    def deleteItem(self, idx):
        # remove from ctrl
        if self.deletionMethod != '(None)':
            getattr(self.control, self.deletionMethod)(idx)

        # renumber items following deleted one
        if self.indexProp != '(None)':
            for constr in self.textConstrLst[idx:]:
                constr.params[self.indexProp] = repr(int(constr.params[self.indexProp]) -1)

    def moveItem(self, idx, dir):
        tc = self.textConstrLst[idx]
        newIdx = min(max(idx + dir, 0), len(self.textConstrLst)-1)

        if newIdx != idx:
            del self.textConstrLst[idx]
            self.textConstrLst.insert(newIdx, tc)

            if self.indexProp != '(None)':
                # swap index property values
                (self.textConstrLst[idx].params[self.indexProp],
                 self.textConstrLst[newIdx].params[self.indexProp]) = \
                (self.textConstrLst[newIdx].params[self.indexProp],
                 self.textConstrLst[idx].params[self.indexProp])

        return newIdx

    def applyDesignTimeDefaults(self, params, method=None):
        if method is None:
            method = self.insertionMethod
        args = []
        kwargs = {}
        paramItems_list= list(self.designTimeDefaults(params, method).items())

        int_list=[]
        str_list=[]
        for item in paramItems_list:
            if isinstance(item[0], str):
                str_list.append(item)
            else:
                int_list.append(item)
        str_list.sort()
        int_list.sort()
        paramItems = int_list + str_list
        for k, v in paramItems:
            if isinstance(k, type(0)):
                args.append(v)
            else:
                kwargs[k] = v
# PRUNE
#         if 'kind' in kwargs.keys() and 'text' in kwargs.keys():
#             if kwargs['kind'] == 0:
#                 kwargs['item'] = kwargs['text']
#                 kwargs.pop('text')

        getattr(self.control, method)(*args, **kwargs)

    def SetName(self, oldValue, newValue):
        self.name = newValue
        self.setCollectionMethod()

    def GetClass(self, dummy=None):
        return self.propName

    def SetClass(self, value):
        pass

    def updateWindowIds(self):
        pass

##    def addIds(self, lst):
##        """ Iterate over items and extend lst for collections with ids """
##        pass

    def designTimeDefaults(self, vals, method=None):
        """ Return a dictionary of parameters for adding an item to the collection """
        dtd = {}
        for param in list(vals.keys()):
            dtd[param] = self.eval(vals[param])
        return dtd

    def initCollection(self):
        pass

    def writeCollectionInitialiser(self, output, stripFrmId=''):
        output.extend(self.initialiser())

    def writeCollectionItems(self, output, stripFrmId=''):
        for creator in self.textConstrLst:
            self.addContinuedLine(
                  sourceconst.bodyIndent + creator.asText(stripFrmId),
                  output, sourceconst.bodyIndent)

    def writeCollectionFinaliser(self, output, stripFrmId=''):
        output.extend(self.finaliser())

    def getPropList(self):
        """ Returns a dictionary of methods suported by the control

            The dict has 'properties' and 'methods' keys which contain the
            getters/setters and undefined methods.
         """
        # XXX should use sub objects if available, but properties on collection
        # XXX items aren't supported yet
        return RTTI.getPropList(None, self)

    def defaultAction(self):
        """ Called when a component is double clicked in a designer
        """
        pass
##        print 'CDTC', self.textConstrLst[self.index]

    def notification(self, compn, action):
        """ Called when other components are deleted.

            Use it to clear references to components which are being deleted.
        """
        # XXX Should use this mechanism to trap renames as well
        pass
##        print 'CollectionDTC.notification', compn, action

class CollectionIddDTC(CollectionDTC):
    """ Collections which have window ids and events """
    windowIdName = 'id'
    idProp = '(undefined)'
    idPropNameFrom = '(undefined)'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'ItemId': ItemIdConstrPropEdit}

    def properties(self):
        props = CollectionDTC.properties(self)
        props['ItemId'] = ('CompnRoute', self.GetItemId, self.SetItemId)
        return props

    def evtName(self):
#        return '%s%s%d' % (self.name, self.propName, self.index)
        base = self.newWinId('')
        itemId = self.GetItemId(None)[len(base):].capitalize()
        return '%s%s' % (self.name, itemId)

##    def setIndex(self, idx):
##        CollectionDCT.setIndex(idx)
##        self.setEvents(

    def getEvents(self):
        evts = []
        idxWId = self.getWinId()
        for evt in self.textEventList:
            if evt.windowid == idxWId:
                evts.append(evt)
        return evts

    def getWinId(self):
        tcl = self.textConstrLst[self.index]
        if self.idProp in tcl.params:
            return tcl.params[self.idProp]
        else:
            return -1

    def getDesignTimeWinId(self):
        return self.control.GetMenuItems()[self.index].GetId()

    def addIds(self, lst):
        for constr in self.textConstrLst:
            if self.idProp in constr.params:
                wId = constr.params[self.idProp]
                if wId in EventCollections.reservedWxIds:
                    name, wId = self.newUnusedItemNames(0)
                lst.append(wId)

    def appendItem(self, method=None):
        CollectionDTC.appendItem(self, method)

#1        self.generateWindowId(self.index)
        self.updateWindowIds()

    def deleteItemEvents(self, idx):
        constr = self.textConstrLst[idx]
        if self.idProp in constr.params:
            wIdStr = constr.params[self.idProp]
            for evt in self.textEventList[:]:
                if evt.windowid == wIdStr:
                    self.textEventList.remove(evt)

    def deleteItem(self, idx):
        self.deleteItemEvents(idx)
        CollectionDTC.deleteItem(self, idx)

        self.updateWindowIds()

    def newUnusedItemNames(self, wId):
        while True:
            newItemName = '%s%d'%(self.propName, wId)
            winId = self.newWinId(newItemName)
            if self.isIdUsed(winId): wId = wId + 1
            else: break
        return newItemName, winId

    def isIdUsed(self, wId):
        for tc in self.textConstrLst:
            if self.idProp in tc.params and tc.params[self.idProp] == wId:
                return True
        return False


    def newWinId(self, itemName):
        return Utils.windowIdentifier(self.designer.controllerView.GetName(),
              self.name + itemName)

    def generateWindowId(self, idx):
        return

    def SetName(self, oldValue, newValue):
        CollectionDTC.SetName(self, oldValue, newValue)
        self.updateWindowIds()

    def evtGetter(self, name):
        wId = self.getWinId()
        for evt in self.textEventList:
            if evt.event_name == name and evt.windowid == wId:
                return evt.trigger_meth
        return None

    def evtSetter(self, name, value):
        wId = self.getWinId()
        for evt in self.textEventList:
            if evt.event_name == name and evt.windowid == wId:
                evt.trigger_meth = value
                return

    def persistEvt(self, name, value, wId = None):
        """ Add a source entry for an event or update the trigger method of
            am existing event. """
        if wId is None:
            wId = self.getWinId()

        for evt in self.textEventList:
            if evt.event_name == name and evt.windowid == wId:
                evt.trigger_meth = value
                return
        if self.control == self.designer or wId is not None:
            comp_name = ''
        else:
            comp_name = self.name
        self.textEventList.append(methodparse.EventParse(None, comp_name, name,
                                                         value, wId))

    def updateWindowIds(self):
        for idx in range(len(self.textConstrLst)):
            # XXX no op?
            self.generateWindowId(idx)

    def designTimeDefaults(self, vals, method=None):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'button1', etc)

            Derived classes should only call this base method if method
            requires an id parameter. This is usually the case."""
        values = copy.copy(vals)
        values[self.idProp] = repr(wx.NewIdRef(count=1))
        dts = CollectionDTC.designTimeDefaults(self, values)
        dts[self.idProp] = wx.NewIdRef(count=1)
        return dts

    def GetItemId(self, x):
        return self.textConstrLst[self.index].params[self.idProp]

    def SetItemId(self, value):
        oldValue = self.textConstrLst[self.index].params[self.idProp]
        self.textConstrLst[self.index].params[self.idProp] = value
        for evt in self.textEventList:
            if evt.windowid == oldValue:
                evt.windowid = value
