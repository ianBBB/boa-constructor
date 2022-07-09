#-----------------------------------------------------------------------------
# Name:        InspectableViews.py
# Purpose:     View base class for GUI builder designer classes than can be
#              inspected and edited in the object inspector.
#              Currently: frame designer, data view and collection editors
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Views.InspectableViews'

import copy, os, pprint

import wx

import Preferences, Utils
from Utils import _

import PaletteMapping, EditorViews
from ObjCollection import ObjectCollection, getCollName

import methodparse, sourceconst

class DesignerError(Exception): pass

class InspectableObjectView(EditorViews.EditorView, Utils.InspectorSessionMix):
    """ Base class for Designers

    A designer visually maintains one _init_* method in the source.
    """
    viewName = 'InspectableObject'
    viewTitle = _('InspectableObject')
    
    collectionMethod = 'init_'
    collectionParams = 'self'
##    handledProps = []
    supportsParentView = False

    def setupArgs(self, ctrlName, params, dontEval, evalDct):
        """ Create a dictionary of parameters for the constructor of the
            control from a dictionary of string/source parameters.
            Catches design time parameter overrides.
        """

        args = {}
        # Build dictionary of params
        for paramKey in params.keys():
            value = params[paramKey]
            ## function references in the constructor
            #if len(value) >= 11 and value[:11] == 'self._init_':
            #    continue
            #    collItem = methodparse.CollectionInitParse(value)
            #    self.addCollView(paramKey, collItem.method, False)
            if paramKey in dontEval:
                args[paramKey] = params[paramKey]
            else:
                try:
                    args[paramKey] = PaletteMapping.evalCtrl(params[paramKey], 
                          evalDct)
                except AttributeError:
                    args[paramKey] = PaletteMapping.evalCtrl(params[paramKey], 
                          {'self': self.controllerView.objectNamespace})

        return args

    def __init__(self, inspector, model, compPal, actions=(), dclickActionIdx=-1, 
          editorIsWindow=True):
        self.compPal = compPal
        EditorViews.EditorView.__init__(self, model, actions, dclickActionIdx, editorIsWindow)
        self.selection = None
        self.inspector = inspector
        self.controllerView = None
        self.objects = {}
        self.objectOrder = []
        self.collEditors = {}
        self.opened = False

    def destroy(self):
        del self.controllerView
        del self.inspector
        for objval in self.objects.values():
            objval[0].destroy()
        for coll in self.collEditors.values():
            coll.destroy()
        del self.collEditors
        del self.objects
        EditorViews.EditorView.destroy(self)

    def doUp(self, inspector):
        self.controllerView.OnSelectParent()

# XXX Consider building subsets of the tree where possible
# XXX may become an issue on frames with many controls
##  decl buildParentRelationship(self) -> (dict, dict)
    def buildParentRelationship(self):
        """ Build a nested dictionary of key = name, value = dict pairs
            describing parental relationship.
            Assuming parents are created before children

            parRel : Nested relationship dictionary
            parRef : Flat reference dictionary
        """

        parRel = {}
        parRef = {}
        for ctrl in self.objectOrder:
            ce = self.objects[ctrl]
            if ce[2] is None:
                parRel[ctrl] = {}
                parRef[ctrl] = parRel[ctrl]
            else:
                parRef[ce[2]][ctrl] = {}
                parRef[ctrl] = parRef[ce[2]][ctrl]

        return  parRel, parRef

    def loadControl(self, ctrlClass, ctrlCompanion, ctrlName, params):
        pass

    def initObjectsAndCompanions(self, creators, objColl, dependents, depLinks):
        collDeps = {}
        for constr in creators:
            self.initObjCreator(constr)
            self.initObjProps(objColl.propertiesByName, constr.comp_name, constr, 
                  dependents, depLinks)
            self.initObjColls(objColl.collectionsByName, constr.comp_name, constr, 
                  collDeps)
            self.initObjEvts(objColl.eventsByName, constr.comp_name, constr)

            self.applyDepsForCtrl(constr.comp_name, depLinks)

        for ctrlName in collDeps.keys():
            for collInit in collDeps[ctrlName]:
                self.addCollView(ctrlName, collInit.method, False)

    def initObjCreator(self, constrPrs):
        # Assumes all design time ctrls are imported in global scope
        try:
            ctrlClass = PaletteMapping.evalCtrl(constrPrs.class_name, 
                  self.model.customClasses)
        except NameError:
            raise DesignerError, \
                  _('%s is not defined on the Palette.')%constrPrs.class_name
        try:
            ctrlCompnClass = PaletteMapping.compInfo[ctrlClass][1]
        except KeyError:
            raise DesignerError, \
                  _('%s is not defined on the Palette.')%ctrlClass.__name__
        else:
            ctrlName = self.loadControl(ctrlClass, ctrlCompnClass,
              constrPrs.comp_name, constrPrs.params)
            ctrlCompn = self.objects[ctrlName][0]
            ctrlCompn.setConstr(constrPrs)
    
    def initObjProps(self, props, name, creator, dependents, depLinks):
        """ Initialise property list by evaluating 1st parameter and calling
            prop's setter with it.
            Also associate companion name with prop parse objs               """
        # XXX creator not used
        if props.has_key(name):
            comp, ctrl = self.objects[name][0:2]
            # initialise live component's properies
            for prop in props[name]:
                prop.prop_name = comp.getPropNameFromSetter(prop.prop_setter)
                # Dependent properties
                if prop.prop_name in comp.dependentProps():
                    self.addDepLink(prop, name, dependents, depLinks)
                # Collection initialisers
                elif len(prop.params) and prop.params[0][:11] == 'self._init_':
                    collItem = methodparse.CollectionInitParse(prop.params[0])
                    self.addCollView(name, collItem.method, False)
                # Check for custom evaluator
                elif comp.customPropEvaluators.has_key(prop.prop_name):
                    args = comp.customPropEvaluators[prop.prop_name](prop.params, 
                          self.getAllObjects())
                    # XXX This is a hack !!!
                    # XXX argument list with more than one prop value are
                    # XXX initialised thru the companion instead of the control
                    if prop.prop_name in comp.initPropsThruCompanion:
                        getattr(comp, prop.prop_setter)(*(args,))
                    else:
                        getattr(ctrl, prop.prop_setter)(*args)
                # Check for pops which don't update the control
                elif prop.prop_name in comp.onlyPersistProps():
                    continue
                # Normal property, eval value and apply it
                else:
                    try:
                        value = PaletteMapping.evalCtrl(prop.params[0], 
                                                        self.model.specialAttrs)
                    except AttributeError, name:
                        value = PaletteMapping.evalCtrl(prop.params[0], 
                          {'self': self.controllerView.objectNamespace})
                    except:
                        print _('Problem with: %s') % prop.asText()
                        raise

                    if prop.prop_name in comp.initPropsThruCompanion:
                        getattr(comp, prop.prop_setter)(value)
                    else:
                        getattr(ctrl, prop.prop_setter)(value)

            # store default prop vals
            comp.setProps(props[name])

    def initObjColls(self, collInits, name, creator, dependents = None):
        """ Initialise collection properties by creating a collection view
            for it and applying it.
            Also associate companion name with prop parse objs               """

        if collInits.has_key(name):
            if dependents is None: dependents = {}
            comp = self.objects[name][0]
            for collInit in collInits[name]:
                if collInit.getPropName() in comp.dependentProps():
                    if not dependents.has_key(name):
                        dependents[name] = []
                    dependents[name].append(collInit)
                else:
                    self.addCollView(name, collInit.method, False)

            # store default collection initialisers
            comp.setCollInits(collInits[name])

    def initObjEvts(self, events, name, creator):
        if events.has_key(name):
            self.objects[name][0].setEvents(events[name])

    def initIdOnlyObjEvts(self, events, creators):
        for crt in creators:
            name = crt.comp_name
            if crt.params.has_key('id'):
                wId = crt.params['id']
                for evt in events:
                    if evt.windowid and evt.windowid == wId:
                        self.objects[name][0].setEvents([evt])

    def addCollView(self, name, collInitMethod, create):
        comp, ctrl = self.objects[name][:2]
        collName = getCollName(collInitMethod, name)
        try:
            collCompClass = comp.subCompanions[collName]
        except KeyError:
            raise Exception, _('Sub-Companion not found for %s in %s')%(name, collInitMethod)
        collComp = collCompClass(name, self, comp, ctrl)
        if create:
            collComp.persistCollInit(collInitMethod, name, collName)

        collInit = self.model.objectCollections[collInitMethod]
        collComp.setConstrs(collInit.creators, collInit.initialisers,
          collInit.finalisers)

        # init DTCtrl
        for crt in collComp.textConstrLst:
            collComp.applyDesignTimeDefaults(crt.params, crt.method)
        collComp.initCollection()

        comp.collections[collName] = collComp

        collEditView = CollectionEdit.CollectionEditorView(self, self.inspector,
            self.model, collComp)
        collEditView.initialise()

        self.collEditors[(comp.name, collName)] = collEditView

    def getRefsFromProp(self, prop):
        refs = []
        # Build lst of ctrl references from property
        for param in prop.params:
            if len(param) >= 4 and param[:4] == 'self':
                refs.append(Utils.ctrlNameFromSrcRef(param))
        return refs

    def checkAndAddDepLink(self, ctrlName, prop, dependentProps, deps, depLinks, definedCtrls):
        if prop.prop_name in dependentProps:
            refs = self.getRefsFromProp(prop)
            # Postpone if target ctrls not yet defined
            allCtrlsDefined = True#len(refs) > 0
            for ref in refs:
                if ref not in definedCtrls:
                    allCtrlsDefined = False

            if not allCtrlsDefined:
                self.addDepLink(prop, ctrlName, deps, depLinks)
                return True

        return False

    def applyDepsForCtrl(self, ctrlName, depLinks):
        if depLinks.has_key(ctrlName):
            for prop, otherRefs in depLinks[ctrlName]:
                for oRf in otherRefs:
                    if not oRf in self.objectOrder:
                        break
                else:
                    # Dependent properties are usually one parameter name
                    # references
                    comp, ctrl = self.objects[prop.comp_name][:2]
                    if len(prop.params) == 1:
                        if ctrlName is None:
                            value = self.companion.eval(prop.params[0])
                        elif ctrlName == '':
                            value = self
                        else:
                            ord, objs = self.model.allObjects()

                            if objs.has_key(ctrlName):
                                value = objs[ctrlName][1]
                            else:
                                continue
                        if prop.prop_name in comp.initPropsThruCompanion:
                            getattr(comp, prop.prop_setter)(value)
                        else:
                            getattr(ctrl, prop.prop_setter)(value)
                    else:
                        refs = []
                        # Build lst of ctrl references from property
                        for param in prop.params:
                            ctrlSrcName = Utils.ctrlNameFromSrcRef(param)
                            if len(param) >= 4 and param[:4] == 'self' and \
                                  self.objects.has_key(ctrlSrcName):
                                refs.append(self.objects[ctrlSrcName][1])
                            else:
                                refs.append(self.companion.eval(param))

                        getattr(ctrl, prop.prop_setter)(*refs)

            del depLinks[ctrlName]

    def addDepLink(self, prop, name, dependents, depLinks):
        refs = self.getRefsFromProp(prop)
        # Handle the case where ref is not a designer obj but a constant
        # all such constansts will be grouped under 'None'
        if not refs:
            if not depLinks.has_key(None):
                depLinks[None] = []
            depLinks[None].append( (prop, ()) )
        else:
            for link in refs:
                if not depLinks.has_key(link):
                    depLinks[link] = []
                otherRefs = refs[:]
                otherRefs.remove(link)
                depLinks[link].append( (prop, otherRefs) )

    def finaliseDepLinks(self, depLinks):
        for ctrlName in depLinks.keys():
            self.applyDepsForCtrl(ctrlName, depLinks)

    def renameEventMeth(self, oldName, newName):
        pass

    def renameCtrl(self, oldName, newName):
        """ Rename a control and update all its properties and events."""

        ctrl = self.objects[oldName]
        del self.objects[oldName]
        self.objects[newName] = ctrl

        idx = self.objectOrder.index(oldName)
        del self.objectOrder[idx]
        self.objectOrder.insert(idx, newName)
        # self.objectOrder[self.objectOrder.index(oldName)] = newName

        companion = self.objects[newName][0]
        companion.renameCtrl(oldName, newName)
        companion.renameCtrlRefs(oldName, newName)

        for name, prop in self.collEditors.keys():
            if name == oldName:
                collEditor = self.collEditors[(name, prop)]
                collEditor.renameCtrl(oldName, newName)
                del self.collEditors[(name, prop)]
                self.collEditors[(newName, prop)] = collEditor


    def renameFrame(self, oldName, newName):
        # update windowids & ctrls
        for comp, ctrl, dummy in self.objects.values():
            if not comp.suppressWindowId:
                comp.updateWindowIds()

    def saveCtrls(self, definedCtrls, module=None, collDeps=None):
        """ Replace current source of method in collectionMethod with values from
            constructors, properties and events.
        """

        newBody = []
        deps = {}
        depLinks = {}
        imports = []
        resourceImports = []

        if collDeps is None:
            extraLines = []
        else:
            extraLines = collDeps
        collDeps = []

        if not module:
            module = self.model.getModule()

        for collView in self.collEditors.values():
            collView.saveCtrls(module)

        # XXX Move toolbar up to the 1st position after the frame

        for ctrlName in self.objectOrder:
            definedCtrls.append(ctrlName)
            compn = self.objects[ctrlName][0]

            compn.writeConstructor(newBody, self.collectionMethod)
            compn.writeProperties(newBody, ctrlName, definedCtrls, deps, depLinks)
            compn.writeCollections(newBody, collDeps)
            compn.writeEvents(newBody, module=module)

            compn.writeDependencies(newBody, ctrlName, depLinks, definedCtrls)

            imp = compn.writeImports()
            if imp and imp not in imports:
                imports.append(imp)

            imp = compn.writeResourceImports()
            if imp and imp not in resourceImports:
                resourceImports.append(imp)

            if Preferences.cgEmptyLineBetweenObjects:
                newBody.append('')

        if not newBody or newBody[-1]:
            newBody.append('')

        if collDeps:
            newBody.extend(collDeps + [''])
            
        if extraLines:
            newBody.extend(extraLines + [''])

        for imp in imports:
            imps = imp.split('\n')
            for imp in imps:
                imp = imp.strip()
                if imp:
                    module.addImportStatement(imp)

        for imp in resourceImports:
            imps = imp.split('\n')
            for imp in imps:
                imp = imp.strip()
                if imp:
                    module.addImportStatement(imp, resourceImport=True)

        emptyCodeBlock = newBody == ['']

        if Preferences.cgAddInitMethodWarning:
            newBody.insert(0, '%s# %s'%(sourceconst.bodyIndent,
                                        sourceconst.code_gen_warning))

        if module.classes[self.model.main].methods.has_key(\
          self.collectionMethod):
            # Add doc string
            docs = module.getClassMethDoc(self.model.main,
              self.collectionMethod)
            if (len(docs) > 0) and docs[0]:
                newBody.insert(0, '%s""" %s """'%(sourceconst.bodyIndent, docs))
                emptyCodeBlock = False

            if emptyCodeBlock:
                module.removeMethod(self.model.main, self.collectionMethod)
                #newBody[-1:-1] = [sourceconst.bodyIndent+'pass']
            else:
                module.replaceMethodBody(self.model.main, self.collectionMethod, 
                      newBody)
        else:
            if not emptyCodeBlock:
                module.addMethod(self.model.main,
                  self.collectionMethod, self.collectionParams, newBody, 0)

    def copyCtrls(self, selCtrls, definedCtrls, output):
        """ Write out current source of selection to a text line list.
        """

        ctrlsAndContainedCtrls = self.expandNamesToContainers(selCtrls)
        deps = {}
        depLinks = {}
        collDeps = []

        collMeths = []
        for compName, collProp in self.collEditors.keys():
            if compName in ctrlsAndContainedCtrls:
                collView = self.collEditors[(compName, collProp)]
                collMeth = []
                collView.copyCtrls(collMeth)
                collMeths.append(collMeth)

        output.insert(0, '%sdef %s(%s):'% (sourceconst.methodIndent,
              self.collectionMethod, self.collectionParams))
        for ctrlName in ctrlsAndContainedCtrls:
            definedCtrls.append(ctrlName)
            compn = self.objects[ctrlName][0]

            compn.updatePosAndSize()

            frmName = self.model.main
            compn.writeConstructor(output, self.collectionMethod, stripFrmId=frmName)
            compn.writeProperties(output, ctrlName, definedCtrls, deps, depLinks, stripFrmId=frmName)
            compn.writeCollections(output, collDeps, stripFrmId=frmName)
            compn.writeEvents(output, stripFrmId=frmName)

            compn.writeDependencies(output, ctrlName, depLinks, definedCtrls, stripFrmId=frmName)

            output.append('')

        if collDeps:
            output.extend(collDeps + [''])

        collMeths.reverse()
        for methBody in collMeths:
            output[0:0] = methBody + ['']

    def cutCtrls(self, selCtrls, definedCtrls, output):
        # Copy to output
        self.copyCtrls(selCtrls, definedCtrls, output)
        self.selectNone()

        # Delete ctrls
        for ctrl in selCtrls:
            self.deleteCtrl(ctrl)

    def pasteCtrls(self, destCtrlName, input):
        # Split up into methods
        methList = []
        for line in input:
            splitLine = line.split()
            if len(splitLine) >= 2 and splitLine[0] == 'def':
                meth = splitLine[1][:splitLine[1].find('(')]
                currMeth = [meth]
                methList.append(currMeth)
            else:
                try:
                    currMeth.append(line)
                except NameError:
                    print 'PASTE ERROR', input
        if not methList:
            raise Exception, _('Nothing to paste')

        collObjColls = []
        pastedCtrls = []
        collMethod = ''
        # find main method
        idx = -1
        for meth in methList[:]:
            idx = idx + 1
            if meth[0] == self.collectionMethod:
                collMethod = meth[0]
                methBody = meth[1:]
            else:
                # XXX not good :(
                ctrlName = methodparse.ctrlNameFromMeth(meth[0])
                newObjColl = self.model.readDesignerMethod(meth[0], meth[1:])
                methodparse.decorateParseItems(
                      newObjColl.creators + newObjColl.events,
                      ctrlName, self.model.main)

                for plp in newObjColl.creators + newObjColl.events + \
                      newObjColl.properties + newObjColl.collections:
                    plp.prependFrameWinId(self.model.main)

                collObjColls.append( (meth[0], ctrlName, newObjColl) )

        if not collMethod:
            raise DesignerError, _('Method %s not found') % self.collectionMethod

        # Parse input source
        objCol = self.model.readDesignerMethod(collMethod, methBody)

        if not len(objCol.creators):
            return []

        # Fixup window ids
        for plp in objCol.creators + objCol.events + objCol.properties + \
              objCol.collections:
            plp.prependFrameWinId(self.model.main)

        # Rename possible name clashes
        objCol.indexOnCtrlName()
        pasteNameClasses = objCol.getCtrlNames()
        
        for name, cls in pasteNameClasses:
            if objCol.eventsByName.has_key(name):
                methodparse.decorateParseItems(objCol.eventsByName[name], name, 
                      self.model.main)
        
        newNames = []
        oldNames = []
        # Preserve order, but determine all new names before creating objs
        for name, clss in pasteNameClasses:
            if name in self.objectOrder:
                newName = self.newObjName(clss, newNames)
                newNames.append(newName)
                oldNames.append(name)
            else:
                newNames.append(name)
                oldNames.append(name)

        for oldName, newName in map(None, oldNames, newNames):
            if newName != oldName:
                objCol.renameCtrl(oldName, newName)
                pastedCtrls.append(newName)
                for idx in range(len(collObjColls)):
                    meth, collCtrlName, collObjColl = collObjColls[idx]
                    collObjColl.renameCtrl(oldName, newName)
                    if collCtrlName == oldName:
                        itms = meth.split('_')
                        itms[3:-1] = [newName]
                        collObjColls[idx] = ('_'.join(itms), newName, collObjColl)
            else:
                pastedCtrls.append(oldName)

        # Update model's object collections' collections
        for meth, collCtrlName, collObjColl in collObjColls:
            self.model.objectCollections[meth] = collObjColl

        # Get previous parent, 1st item in the group's parent will always be
        # the root parent
        # Only reparent visual controls
        if objCol.creators[0].params.has_key('parent'):
            copySource = objCol.creators[0].params['parent']
            objCol.reparent(copySource, Utils.srcRefFromCtrlName(destCtrlName))

        # create controls
        deps = {}
        depLnks = {}
        self.inspector.vetoSelect = True
        try:
            self.initObjectsAndCompanions(objCol.creators, objCol, deps, depLnks)
        finally:
            self.inspector.vetoSelect = False

        # merge pasted controls with current controls
        self.model.objectCollections[collMethod].merge(objCol)

        return pastedCtrls

    def addObject(self, ctrlName, companion, designTimeCtrl, parentName = None):
        self.objects[ctrlName] = [companion, designTimeCtrl]
        if parentName is not None: self.objects[ctrlName].append(parentName)
        self.objectOrder.append(ctrlName)

    def newObjName(self, className, additionalNames = None):
        """ Return a name for a control unique in the scope of the model. """

        if additionalNames is None: additionalNames = []
        # XXX Now that there is multiple maintained methods is may fail because
        # XXX it's only unique in the method.
        num = 1
        
        dotted = className.rfind('.')
        if dotted != -1:
            if className[:3] == 'wx.':
                newName = '%s%s'%(className[dotted+1:dotted+2].lower(), className[dotted+2:])
            else:
                newName = '%s%s'%(className[0].lower(), className[1:])                
        else:
            newName = '%s%s'%(className[0].lower(), className[1:])

        return Utils.getValidName(self.objects.keys() + additionalNames, newName)

    def newObject(self, ObjClass, ObjCompanionClass):
        """ At design time, when adding a new ctrl from the palette, create and
            register given control and companion.
        """
        self.checkHost(ObjCompanionClass)

        # XXX Only DataView uses this, refc
        objName = self.newObjName(ObjClass.__name__)

        companion = ObjCompanionClass(objName, self, ObjClass)
        params = companion.designTimeSource()
        self.addObject(objName, companion, companion.designTimeObject(), '')
        companion.persistConstr(Utils.getWxPyNameForClass(ObjClass), params)
        return objName


    def addCtrlToObjectCollection(self, textConstr):
        colMeth = self.collectionMethod
        if not self.model.objectCollections.has_key(colMeth):
            self.model.objectCollections[colMeth] = ObjectCollection()

        self.model.objectCollections[colMeth].creators.append(textConstr)

    def addCollToObjectCollection(self, collInitParse):
        colMeth = self.collectionMethod
        self.model.objectCollections[colMeth].collections.append(collInitParse)
        # Add a new method to maintained methods
        newObjColl = ObjectCollection()
        self.model.objectCollections[collInitParse.method] = newObjColl
        return newObjColl

    def selectObject(self):
        pass

    def selectNone(self):
        pass

    def deleteCtrl(self, name, parentRef = None):
        self.model.objectCollections[self.collectionMethod].deleteCtrl(name)
        del self.objectOrder[self.objectOrder.index(name)]
        del self.objects[name]

        for ctrlName, propName in self.collEditors.keys()[:]:
            if ctrlName == name:
#                self.collEditors[(ctrlName, propName)].close()
                if self.collEditors[(ctrlName, propName)].frame:
                    self.collEditors[(ctrlName, propName)].frame.Close()
                del self.collEditors[(ctrlName, propName)]

    def cleanup(self):
        if self == self.inspector.prevDesigner[0]:
            self.inspector.prevDesigner = (None, None)

    def close(self):
        if self.controllerView and self.controllerView != self:
            self.controllerView.close()

    def refreshContainment(self, selectName = None):
        """ Rebuild parent tree and optionally select given control """
        parRelations, parReference = self.buildParentRelationship()
        self.inspector.containment.refreshCtrl(self.model.main, parRelations, self)
        if selectName is not None:
            self.inspector.containment.selectName(selectName)
        return parRelations, parReference

##  decl getObjectsOfClass(self, theClass: class) -> dict
    def getObjectsOfClass(self, theClass):
        results = {}
        for objName in self.objects.keys():
            if issubclass(self.objects[objName][1].__class__, theClass):
                if objName:
                    results['self.'+objName] = self.objects[objName][1]
                else:
                    results['self'] = self.objects[objName][1]
        return results

    def getObjectsOfClassWithParent(self, theClass, theParentName):
        results = {}
        for objName in self.objects.keys():
            if self.objects[objName][2] == theParentName and \
                  isinstance(self.objects[objName][1], theClass):
                if objName:
                    results['self.'+objName] = self.objects[objName][1]
                else:
                    results['self'] = self.objects[objName][1]
        return results

    def getAllObjects(self):
        results = {}
        for objName in self.objects.keys():
            if objName:
                results['self.'+objName] = self.objects[objName][1]
            else:
                results['self'] = self.objects[objName][1]
        return results

    def getObjectsOfClassOwnedBy(self, theClass, theOwner):#XXX
        results = {}
        for objName in self.objects.keys():
            if self.objects[objName][1].__class__ is theClass:
                results['self.'+objName] = self.objects[objName][1]
        return results

    def showCollectionEditor(self, ctrlName, propName, show=True):
        """ Show the Collection Editor frame for given name and prop """
        # XXX param ctrlName is actually wrong!
        if ctrlName == self.GetName():
            ctrlName = ''

        if not self.collEditors.has_key((ctrlName, propName)):
            self.addCollView(ctrlName, '_init_coll_%s_%s'%(ctrlName, propName), True)

        collEditor = self.collEditors[(ctrlName, propName)]
        
        if show:
            collEditor.show()
        else:
            return collEditor

    def checkHost(self, CtrlCompanion):
        """ Checks that the companion may be hosted in this designer """
        if CtrlCompanion.host == 'Not Implemented':
            dlg = wx.MessageDialog(self, _('This component is not yet implemented'),
                              _('Not Implemented'), wx.OK | wx.ICON_ERROR)
            try: dlg.ShowModal()
            finally: dlg.Destroy()
            raise DesignerError, _('Not Implemented')
        if CtrlCompanion.host != self.viewName:
            dlg = wx.MessageDialog(self,
              _('This component must be created in the %s view')%CtrlCompanion.host,
              _('Wrong Designer'), wx.OK | wx.ICON_ERROR)
            try: dlg.ShowModal()
            finally: dlg.Destroy()
            raise DesignerError, _('Wrong Designer')

    def expandNamesToContainers(self, ctrlNames):
        """ Expand set of names to include the names of all their children """
        return ctrlNames

    def collapseNamesToContainers(self, ctrlNames):
        """ Collapse set of names to exclude the names of all their children """
        return ctrlNames

    def notifyAction(self, compn, action):
        # notify components
        for otherCompn, otherCtrl, otherPrnt in self.objects.values():
            otherCompn.notification(compn, action)

        # notify collections
        for collView in self.collEditors.values():
            collView.companion.notification(compn, action)

    def showCreationOrderDlg(self, selName):
        sibs = []
        allNames = []
        idx = -1
        for objName in self.objectOrder:
            idx = idx + 1
            ctrl, parent = self.objects[objName][1:3]
            if parent == selName:
                sibs.append( (idx, objName) )
                allNames.append(objName)

        allNames = self.expandNamesToContainers(allNames)
        allSibs = []
        for name in allNames:
            allSibs.append( (self.objectOrder.index(name), name) )

        from CreationOrdDlg import CreationOrderDlg
        dlg = CreationOrderDlg(self, sibs, allSibs)
        if dlg.ShowModal() == wx.ID_OK:
            for idx, name in map(None, dlg.allCtrlIdxs, dlg.allCtrlNames):
                self.objectOrder[idx] = name

import CollectionEdit
