#----------------------------------------------------------------------
# Name:        RTTI.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import sys, warnings

from types import *
import wx

warnings.filterwarnings('ignore', '', DeprecationWarning, 'RTTI')

def sort_proxy(self, other):
    return self < other and -1 or self > other and 1 or 0

class PropertyWrapper:
    # XXX This would be better implemented with subclassing
    def __init__(self, name, rType, getter, setter):
        """ Types: 'CtrlRoute', 'CompnRoute', 'EventRoute', 'NoneRoute',
                   'IndexRoute', 'NameRoute'
        """

        self.name = name
        self.routeType = rType
        self.getter = getter
        self.setter = setter
        self.ctrl = None
        self.compn = None

        # Not used yet
        self.setterName = ''

    def __cmp__(self, other):
        """ This is for sorting lists of PropertyWrappers """
#        sort_proxy(self.name, other.name)
        if self.name < other.name:
            return -1
        if self.name > other.name:
            return 1
        return 0

    def __repr__(self):
        return '<instance PropertyWrapper: %s, %s (%s, %s)'%(self.name,
          self.routeType, self.getter, self.setter)

    def connect(self, ctrl, compn):
        self.ctrl = ctrl
        self.compn = compn

    def getValue(self, *params):
        if self.routeType == 'CtrlRoute' and self.ctrl:
            return self.getter(self.ctrl)
        elif self.routeType == 'CompnRoute' and self.compn:
            return self.getter(self.compn)
        elif self.routeType == 'EventRoute' and self.compn and len(params):
            return self.getter(params[0])
        elif self.routeType == 'IndexRoute' and self.ctrl and len(params):
            return self.getter(self.ctrl, params[0])
        elif self.routeType == 'IdRoute' and self.ctrl and self.compn:
            return self.getter(self.ctrl, self.compn.getDesignTimeWinId())
        elif self.routeType == 'NameRoute':
            return self.getter(self.name)
        else:
            return None

    def setValue(self, value, *params):
        if self.routeType == 'CtrlRoute' and self.ctrl:
            self.setter(self.ctrl, value)
        elif self.routeType == 'CompnRoute' and self.compn:
            self.setter(value)
        elif self.routeType == 'EventRoute' and self.compn and len(params):
            self.setter(params[0], value)
        elif self.routeType == 'IndexRoute' and self.ctrl and len(params):
            self.setter(self.ctrl, params[0], value)
        elif self.routeType == 'IdRoute' and self.ctrl and self.compn:
            self.setter(self.ctrl, self.compn.getDesignTimeWinId(), value)
        elif self.routeType == 'ReApplyRoute' and self.compn and len(params):
            self.setter(*[self.ctrl], **params)
        elif self.routeType == 'NameRoute':
            return self.setter(self.name, value)

    def getSetterName(self):
        from types import FunctionType, MethodType
        if self.setter:
            if self.setterName:
                return self.setterName
            if type(self.setter) == FunctionType:
                return self.setter.func_name
            if type(self.setter) == MethodType:
                return self.setter.im_func.func_name
            else:
                return ''
        else:
            return ''

_methodTypeCache = {}
def getPropList(obj, cmp):
    """
       Function to extract sorted list of properties and getter/setter methods
       from a given object and companion.
       Property names that also occur in the Constructor list are stored under
       the 'constructor' key
       Vetoes are dangerous methods that should not be inspected

       Returns:
       {'constructor': [ PropertyWrapper, ... ],
        'properties': [ PropertyWrapper, ... ] }

    """
    def catalogProperty(name, methType, meths, constructors, propLst, constrLst):
        if constructors.has_key(name):
            constrLst.append(PropertyWrapper(name, methType, meths[0], meths[1]))
        else:
            propLst.append(PropertyWrapper(name, methType, meths[0], meths[1]))

    #getPropList(obj, cmp):-
    props = {}
    props['Properties'] = {}
    props['Methods'] = {}
    props['Built-ins'] = {}

    # traverse inheritance hierarchy
    # populate property list
    propLst = []
    constrLst = []
    #           2.4                          2.5
    if obj and (type(obj) is InstanceType or isinstance(obj, wx.Object)):
        traverseAndBuildProps(props, cmp.vetoedMethods(), obj, obj.__class__)

        # populate property list
        if cmp:
            constrNames = cmp.constructor()
        else:
            constrNames = {}
        propNames = props['Properties'].keys()
        propNames.sort()
        for propName in propNames:
            if cmp and propName in cmp.hideDesignTime():
                continue
            propMeths = props['Properties'][propName]
            try:
                catalogProperty(propName, 'CtrlRoute', propMeths,
                  constrNames, propLst, constrLst)
            except:
                catalogProperty(propName, 'NoneRoute', (None, None),
                  constrNames, propLst, constrLst)
        if cmp:
            xtraProps = cmp.properties()
            propNames = xtraProps.keys()
            propNames.sort()
            for propName in propNames:
                #if propName in cmp.hideDesignTime():
                #    continue
                propMeths = xtraProps[propName]
                try:
                    catalogProperty(propName, propMeths[0], propMeths[1:],
                      constrNames, propLst, constrLst)
                except: pass

        propLst.sort()
        constrLst.sort()
    else:
        if cmp:
            constrNames = cmp.constructor()
            xtraProps = cmp.properties()
            propNames = xtraProps.keys()
            propNames.sort()
            for propName in propNames:
                propMeths = xtraProps[propName]
                #try:
                catalogProperty(propName, propMeths[0], propMeths[1:],
                  constrNames, propLst, constrLst)
                #except:
                #    print 'prop error', sys.exc_info()
        else:
            pass #print 'Empty object', obj, cmp

    return {'constructor': constrLst, 'properties': propLst}

def getMethodType(method, obj, Class):
    """ classify methods according to prefix
        return category, property name, getter, setter
    """
    result = ('Methods', method, None, None)
    try:
        meth = getattr(obj, method)
    except TypeError:
        return result
    except Exception:
        #print obj, method
        return result

    if (type(meth) == MethodType):
        func = meth.im_func
        result = ('Methods', method, func, func)
        prefix = method[:3]
        property = method[3:]
        getname = 'Get'+property
        setname = 'Set'+property

        try:
            if (method[:2] == '__'):
                result = ('Built-ins', method, func, func)
            elif (prefix == 'Get') and hasattr(obj, setname) and property:
                #see if getter breaks
                v = func(obj)
                result = ('Properties', property, func, getattr(obj, setname).im_func)
            elif (prefix == 'Set') and hasattr(obj, getname) and property:
                #see if getter breaks
                getter = getattr(obj, getname).im_func
                v = getter(obj)
                result = ('Properties', property, getter, func)
        except Exception, err:
            pass
    return result

def traverseAndBuildProps(props, vetoes, obj, Class):
    for m in Class.__dict__.keys():
        if m not in vetoes:
            cat, name, methGetter, methSetter = \
              getMethodType(m, obj, Class.__dict__)

            if not props[cat].has_key(name):
                props[cat][name] = (methGetter, methSetter)

    for Cls in Class.__bases__:
        traverseAndBuildProps(props, vetoes, obj, Cls)

if __name__ == '__main__':
    wx.PySimpleApp()
    f = wx.Frame(None, -1, 'asd')
    c = wx.ComboBox(f, -1)
    props = {'Properties': {}, 'Built-ins': {}, 'Methods': {}}
    traverseAndBuildProps(props, [], c, c.__class__)
    import pprint
    pprint.pprint(props)
