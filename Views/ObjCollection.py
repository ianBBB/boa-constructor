#-----------------------------------------------------------------------------
# Name:        ObjCollection.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2000
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
import sourceconst

class ObjectCollection:
    def __init__(self):#, creators = [], properties = [], events = [], collections = []):
        self.creators = []
        self.properties = []
        self.events = []
        self.collections = []
        self.initialisers = []
        self.finalisers = []

        self.creatorByName = {}
        self.propertiesByName = {}
        self.eventsByName = {}
        self.collectionsByName = {}

    def __repr__(self):
        return '<ObjectCollection instance: %s,\n %s,\n %s,\n %s,\nBy name:\n %s,\n %s,\n %s,\n %s,>'% (repr(self.creators), repr(self.properties),
           repr(self.collections), repr(self.events),
           repr(self.creatorByName), repr(self.propertiesByName),
           repr(self.collectionsByName), repr(self.eventsByName))

    def setup(self, creators, properties, events, collections, initialisers, finalisers):
        self.creators = creators
        self.properties = properties
        self.events = events
        self.collections = collections
        self.initialisers = initialisers
        self.finalisers = finalisers

    def merge(self, objColl):
        """ Merge another object collection with this one """

        def mergeList(myLst, newLst):
            for item in newLst:
                myLst.append(item)

        mergeList(self.creators, objColl.creators)
        mergeList(self.properties, objColl.properties)
        mergeList(self.events, objColl.events)
        mergeList(self.collections, objColl.collections)
        mergeList(self.initialisers, objColl.initialisers)
        mergeList(self.finalisers, objColl.finalisers)

        self.indexOnCtrlName()

    def getCtrlNames(self):
        """ Return a list of (name, class) tuples """
        return [ (self.creatorByName[n][0].comp_name, 
                  self.creatorByName[n][0].class_name )
                for n in self.creatorByName]

    def removeReference(self, name, method):
        i = 0
        while i < len(self.collections):
            if self.collections[i].method == method:
                del self.collections[i]
            else:
                i = i + 1

        if self.collectionsByName.has_key(name):
            namedColls = self.collectionsByName[name]

            i = 0
            while i < len(namedColls):
                if namedColls[i].method == method:
                    del namedColls[i]
                else:
                    i = i + 1

        i = 0
        while i < len(self.properties):
            prop = self.properties[i]
            if len(prop.params) and prop.params[0][5:len(method) +5] == method:
                del self.properties[i]
            else:
                i = i + 1

        i = 0
        if self.propertiesByName.has_key(name):
            props = self.propertiesByName[name]
            while i < len(props):
                prop = props[i]
                if len(prop.params) and prop.params[0][5:len(method) +5] == method:
                    del props[i]
                else:
                    i = i + 1

    def renameList(self, lst, dict, name, new_name):
        for item in lst:
            item.renameCompName2(name, new_name)

        # keep named colls in sync
        if dict.has_key(name):
            dict[new_name] = dict[name]
            del dict[name]

    def renameFrameList(self, lst, name, new_name):
        for item in lst:
            item.renameFrameName(name, new_name)

    def renameCtrl(self, name, new_name):
        self.renameList(self.creators, self.creatorByName, name, new_name)
        self.renameList(self.properties, self.propertiesByName, name, new_name)
        self.renameList(self.events, self.eventsByName, name, new_name)
        self.renameList(self.collections, self.collectionsByName, name, new_name)

    def renameFrame(self, name, new_name):
        self.renameFrameList(self.creators, name, new_name)
        self.renameFrameList(self.events, name, new_name)

    def deleteCtrl(self, name):
        for list in (self.creators, self.properties, self.events):
            i = 0
            while i < len(list):
                if list[i].comp_name == name:
                    del list[i]
                else:
                    i = i + 1

##    def findRootParent(self):
##        for crt in self.creators:
##            if crt.params.has_key('parent'):

    def reparent(self, oldParent, newParent):
        for crt in self.creators:
            if crt.params.has_key('parent') and crt.params['parent'] == oldParent:
                crt.params['parent'] = newParent

    def setupList(self, list):
        dict = {}
        for item in list:
            if not dict.has_key(item.comp_name):
                dict[item.comp_name] = []
            dict[item.comp_name].append(item)
        return dict

    def indexOnCtrlName(self):
        self.creatorByName = self.setupList(self.creators)
        self.propertiesByName = self.setupList(self.properties)
        self.eventsByName = self.setupList(self.events)
        self.collectionsByName = self.setupList(self.collections)

def isInitCollMeth(meth):
    return meth.startswith(sourceconst.init_coll)

def getCollName(collInitMethod, name):
    return collInitMethod[len(sourceconst.init_coll+name)+1:]
