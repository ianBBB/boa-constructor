#-----------------------------------------------------------------------------
# Name:        wxNamespace.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------
import Preferences as _Prefs

import wx
import wx.html
# import wx.calendar  # does not appear to be used here
import wx.grid
import wx.stc
import wx.gizmos
# import wx.wizard  # does not appear to be used here

def getWxClass(name):
    return getWxObjPath(name)

##def getNamesOfType(aType):
##    res = []
##    for k, v in globals().items():
##        if type(v) == aType:
##            if _Prefs.ccFilterWxPtrNames and k[-3:] == 'Ptr':
##                continue
##            res.append(k)
##    return res

def getWxObjPath(objPath):
    pathSegs = objPath.split('.')
    if pathSegs[0] != 'wx':
        return None
    obj = wx
    for name in pathSegs[1:]:
        if hasattr(obj, name):
            obj = getattr(obj, name)
        else:
            return None
    return obj

def getWxNamespaceForObjPath(objPath):
    obj = getWxObjPath(objPath)
    if obj:
        return dir(obj)
    else:
        return []

