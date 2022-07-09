#----------------------------------------------------------------------
# Name:        methodparse.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
"""

Creation

self.<componentname> = <wxClassname>(<constr params>)

constructor
     compname
     classname
     params

Initialisation

self.<componentname>.?Set?<propertyname>(<value>)

property
    compname
    propname
    value


Event connection
(2 identified formats)
EVT_<event>(<connect to>, [<windowid>], <eventmethod>)
new formats
<connect to>.Bind(<event>, <eventmethod>, [id=<windowid>])

event
    eventname
    compname
    windowid
    triggermeth

---------------------------

Boilerplate

class frame1(wxFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self):
        self._init_utils()

    def __init__(self):
        self._init_ctrls()
"""

import re, string

import Preferences, Utils
from Utils import _

from Companions import EventCollections

import sourceconst

containers = [('(', ')'), ('{', '}'), ('[', ']')]
containBegin = [_c[0] for _c in containers]
containEnd = [_c[1] for _c in containers]

def incLevel(level, pos):
    return level + 1, pos + 1

def decLevel(level, pos):
    return max(level - 1, 0), pos + 1

def safesplitfields(params, delim, returnBlanks = 0,
      containBegin=containBegin, containEnd=containEnd):
    """ Returns a list of parameters split on delim but not if delim are
        within containers (), {}, [], '', ""
        Also skip '', "" content
        Note that results are stripped

        Added returnBlanks flag for compatibility with python's split
        split('', ',') returns ['']
        Usually I want the result of such a split to be []
    """

    locparams =  params
    list = []
    i = 0
    nestlevel = 0
    singlequotelevel = 0
    doublequotelevel = 0

    if returnBlanks and not params.strip():
        return [params]

    while i < len(locparams):
        curchar = locparams[i]
        # only check for delimiter if not inside some block
        if (not nestlevel) and (not singlequotelevel) and (not doublequotelevel)\
          and (curchar == delim):
            param = locparams[:i]
            list.append(param)
            locparams = locparams[i +1:].strip()
            i = 0
            continue

        if (not singlequotelevel) and (not doublequotelevel) and nestlevel and \
          (curchar in containEnd):
            nestlevel, i = decLevel(nestlevel, i)
            continue

        if (not singlequotelevel) and (not doublequotelevel) and \
          (curchar in containBegin):
            nestlevel, i = incLevel(nestlevel, i)
            continue

        # don't check anything except end quotes inside quote blocks
        if singlequotelevel and curchar == "'":
            singlequotelevel, i = decLevel(singlequotelevel, i)
            continue
        if doublequotelevel and curchar == '"':
            doublequotelevel, i = decLevel(doublequotelevel, i)
            continue

        if (not singlequotelevel) and curchar == '"':
            doublequotelevel, i = incLevel(doublequotelevel, i)
        elif (not doublequotelevel) and curchar == "'":
            singlequotelevel, i = incLevel(singlequotelevel, i)
        else:
            i = i + 1

    # add last entry not delimited by comma
    lastentry = locparams.strip()
    if lastentry:
        list.append(lastentry)
    return list

# XXX does not handle ",' yet
def matchbracket(text, findBracket, dir=None):
    if findBracket in containBegin or (dir is not None and dir == -1):
        dir = -1
        start = len(text)-1
        end = -1
        brktIdx = containBegin.index(findBracket)
    elif findBracket in containEnd or (dir is not None and dir == 1):
        dir = 1
        start = 0
        end = len(text)
        brktIdx = containEnd.index(findBracket)
    else:
        raise Exception(_('Unhandled bracket'))

    # () {} []
    levels = [0, 0, 0]

    for cIdx in range(start, end, dir):
        c = text[cIdx]
        if c in containBegin:
            idx = containBegin.index(c)
            levels[idx] = levels[idx] + dir
        elif c in containEnd:
            idx = containEnd.index(c)
            levels[idx] = levels[idx] - dir

        if levels[brktIdx] < 0:
            return cIdx
    return -1

def parseMixedBody(parseClasses, lines):
    """ Return a dictionary with keys representing classes that
        'understood' the line and values a list of found instances
        of the found class
    """
    cat = {}
    unmatched = []
    for ParseClass in parseClasses:
        cat[ParseClass] = []

    idx = 0
    cont = ''
    while idx < len(lines):
        line = lines[idx].strip()
        ln = cont + line
        if (ln == 'pass') or (ln == ''):
            idx = idx + 1
            continue

        for ParseClass in parseClasses:
            # build up the string if lines continue
            try:
                res = ParseClass(ln).value()
            except IncompleteLineError:
                cont = ln
                break
            else:
                if res:
                    cat[ParseClass].append(res)
                    cont = ''
                    break
        else:
            if ln != '# %s'%sourceconst.code_gen_warning:
                unmatched.append(line)
        idx = idx + 1

    return cat, unmatched

class IncompleteLineError(Exception): pass

class PerLineParser:
    """ Class which parses 1 line of source code """
    def value(self):
        if self.m: return self
        else: return None
    def asText(self, stripFrameWinIdPrefix=''):
        """ Source representation of parsed line """
        return ''
    def getIdPrefix(self, name):
        return 'wxID_%s'%name.upper()
    def checkId(self, id, idPrfx):
        return id not in EventCollections.reservedWxNames and id.startswith(idPrfx)
    def prependFrameWinId(self, frame):
        pass

    def __repr__(self):
        return self.asText()

    def renameCompName2(self, old_value, new_value):
        """ notification of a rename, override to catch renames to vars and params
            All parse lines should be notified of renames, not just entries
            which have that name """
        if self.comp_name == old_value:
            self.comp_name = new_value

    def renameFrameName(self, old_value, new_value):
        self.frame_name = new_value

    def renameWindowId(self, windowid, old_frame_name, new_frame_name, old_ctrl_name, new_ctrl_name):
        xtra = windowid[len(Utils.windowIdentifier(old_frame_name, old_ctrl_name)):]
        return Utils.windowIdentifier(new_frame_name, new_ctrl_name)+xtra

    def extractKVParams(self, paramsStr):
        params = safesplitfields(paramsStr, ',')
        result = {}
        posArgs = 0
        for param in params:
            try:
                sidx = param.index('=')
            except ValueError:
                result[posArgs] = param.strip()
                posArgs += 1
            else:
                result[str(param[:sidx].strip())] = param[sidx+1:].strip()
        return result

    def KVParamsAsText(self, params):
        kvlist = []
        sortedkeys = list(params.keys())
        sortedkeys.sort()
        for key in sortedkeys:
            if isinstance(key, type(0)):
                kvlist.append(params[key])
            else:    
                kvlist.append(Preferences.cgKeywordArgFormat%{'keyword': key,
                                                         'value': params[key]})
        return ', '.join(kvlist)

    def checkContinued(self, line):
        line = line.strip()
        if line and line[-1] in (',', '('):
            raise IncompleteLineError


idc = '[A-Za-z_][A-Za-z0-9_]*'
idc2 = '[A-Za-z_][A-Za-z0-9_/.]*'
# self.name=class(params)
is_constr = re.compile('^[ \t]*self[.](?P<name>'+idc+')[ \t]*=[ \t]*(?P<class>'+\
  idc2+')\(((?P<params>.*)(\)|,))?$')
# class.__init__(self,params)
is_constr_frm = re.compile('^[ \t]*(?P<class>'+idc2+\
  ')[.]__init__\(self,[ \t]*((?P<params>.*)(\)|,))?$')
# self.name=self.factory.method(params)
is_constr_factory = re.compile('^[ \t]*self[.](?P<name>'+idc+')[ \t]*=[ \t]*self[.](?P<factory>'+\
  idc+')[.](?P<method>'+idc+')\((?P<params>.*)(\)|,)$')

class ConstructorParse(PerLineParser):
    def __init__(self, line=None, comp_name='', class_name='', params=None):
        self.comp_name = comp_name
        self.class_name = class_name
        if params is None: self.params = {}
        else:              self.params = params
        self.factory = None

        if line:
            self.m = is_constr_factory.search(line)
            if self.m:
                self.checkContinued(line)
                self.comp_name = self.m.group('name')
                self.class_name = ''
                self.factory = (self.m.group('factory'), self.m.group('method'))
                self.params = self.extractKVParams(self.m.group('params'))
            else:
                self.m = is_constr.search(line)
                if self.m:
                    self.checkContinued(line)
                    self.comp_name = self.m.group('name')
                    self.class_name = self.m.group('class')
                    self.params = self.extractKVParams(self.m.group('params'))
                else:
                    self.m = is_constr_frm.search(line)
                    if self.m:
                        self.checkContinued(line)
                        self.comp_name = ''
                        self.class_name = self.m.group('class')
                        self.params = self.extractKVParams(self.m.group('params'))


    def renameCompName2(self, old_value, new_value):
        if 'parent' in self.params and \
              self.params['parent'] == Utils.srcRefFromCtrlName(old_value):
            self.params['parent'] = Utils.srcRefFromCtrlName(new_value)
        if self.comp_name == old_value:
            self.comp_name = new_value
            if 'name' in self.params:
                self.params['name'] = repr(new_value)
            if 'id' in self.params and \
                  self.params['id'] not in EventCollections.reservedWxNames:
                self.params['id'] = \
                  self.params['id'][:-len(old_value)]+new_value.upper()
        if self.factory and self.factory[0] == old_value:
            self.factory = (new_value, self.factory[1])


    def prependFrameWinId(self, frame):
        idPrfx = self.getIdPrefix(frame)
        if 'id' in self.params and \
              self.params['id'] not in EventCollections.reservedWxNames:
            self.params['id'] = idPrfx + self.params['id']

    def asText(self, stripFrameWinIdPrefix=''):
        if stripFrameWinIdPrefix:
            idPrfx = self.getIdPrefix(stripFrameWinIdPrefix)
            params = {}
            params.update(self.params)
            if 'id' in params and self.checkId(params['id'], idPrfx):
                params['id'] = params['id'][len(idPrfx):]
        else:
            params = self.params

        if self.factory:
            factory, method = self.factory
            return 'self.%s = self.%s.%s(%s)' %(self.comp_name, factory, method,
              self.KVParamsAsText(params))
        elif self.comp_name:
            return 'self.%s = %s(%s)' %(self.comp_name, self.class_name,
              self.KVParamsAsText(params))
        else:
            return '%s.__init__(self, %s)' %(self.class_name,
              self.KVParamsAsText(params))
    
##is_constr_col = re.compile('^[ \t]*self._init_coll_(?P<meth>'+idc+\
##  ')[.]__init__\(self,[ \t]*(?P<params>.*)\)$')

coll_init = '_init_coll_'
idp = '[A-Za-z_][A-Za-z0-9_.]*'
# self.name(params)
is_prop = re.compile('^[ \t]*self[.](?P<name>'+idp+')[ \t]*\([ \t]*(?P<params>.*)[ \t]*(\)|,)$')
class PropertyParse(PerLineParser):
    def __init__(self, line=None, comp_name='', prop_setter='', params=None, prop_name=''):
        self.comp_name = comp_name
        self.prop_setter = prop_setter
        if params is None: self.params = []
        else:              self.params = params
        self.params = params
        self.prop_name = prop_name
        if line:
            self.m = is_prop.search(line)
            if self.m:
                self.checkContinued(line)
                self.params = safesplitfields(self.m.group('params'), ',')
                compsetter = self.m.group('name').split('.')

                if len(compsetter) < 1: raise Exception(_('Atleast 1 segment required, got: %r')%compsetter)
                if len(compsetter) == 1:
                    self.comp_name = ''
                    self.prop_setter = compsetter[0]
                elif len(compsetter) == 2:
                    self.comp_name = compsetter[0]
                    self.prop_setter = compsetter[1]
                else: raise Exception(_('Too many attribute levels'))
                
                if self.prop_setter == 'Bind':
                    self.m = None

    def renameCompName2(self, old_value, new_value):
        # XXX This is ugly but has to do until a better
        # XXX strategy is conceived.
        # XXX The problem is that the useful logic is in the
        # XXX companion which is not available for the clipboard
        # XXX The source's ctrl needs to be renamed for a companion
        # XXX to be created.

        # Rename references to ctrl in parameters of property
        oldCtrlSrcRef = Utils.srcRefFromCtrlName(old_value)
        newCtrlSrcRef = Utils.srcRefFromCtrlName(new_value)

        for idx in range(len(self.params)):
            segs = self.params[idx].split(oldCtrlSrcRef)
            if len(segs) > 1:
                lst = [segs[0]]
                for s in segs[1:]:
                    if s and s[0] in string.ascii_letters+string.digits+'_':
                        lst[-1] = lst[-1] + s
                    else:
                        lst.append(s)
                self.params[idx] = newCtrlSrcRef.join(lst)

            # Handle case where _init_coll_* methods are used as parameters
            param = self.params[idx]
            if param.startswith('self.'+coll_init):
                nameEnd = param.rfind('_')
                name = param[16:nameEnd]
                if name == old_value:
                    self.params[idx] = 'self.'+coll_init+new_value+param[nameEnd:]

        PerLineParser.renameCompName2(self, old_value, new_value)

    def asText(self, stripFrameWinIdPrefix=''):
        return '%s.%s(%s)' %(Utils.srcRefFromCtrlName(self.comp_name),
                self.prop_setter, ', '.join(self.params))

def ctrlNameFromMeth(meth):
    return '_'.join(meth.split('_')[3:-1])

# self._init_coll_method(comp_name, params)
is_coll_init = re.compile('^[ \t]*self[.](?P<method>'+coll_init+idp+\
      ')[ \t]*\((?P<comp_name>'+idp+')[ \t,]*(?P<params>.*)(\)|,)$')

class CollectionInitParse(PerLineParser):
    def __init__(self, line=None, comp_name='', method='', params=None, prop_name=''):
        self.comp_name = comp_name
        self.method = method
        if params is None: self.params = []
        else:              self.params = params
        self.prop_name = prop_name
        if line:
            self.m = is_coll_init.search(line)
            if self.m:
                self.checkContinued(line)
                self.params = safesplitfields(self.m.group('params'), ',')
                self.method = self.m.group('method')
                self.comp_name = self.m.group('comp_name')[5:]
                self.prop_name = self.method[len(coll_init)+len(self.comp_name)+1:]

    def getPropName(self):
        return self.method[len(coll_init)+len(self.comp_name)+1:]

    def renameCompName2(self, old_value, new_value):
        if self.comp_name == old_value:
            self.comp_name = new_value
            self.method = '%s%s_%s'%(coll_init, new_value, self.prop_name)

    def asText(self, stripFrameWinIdPrefix=False):
        return 'self.%s(%s)' %(self.method,
             ', '.join([Utils.srcRefFromCtrlName(self.comp_name)]+self.params))

# Because the object name of some collection items cannot be directly derived
# from the source, the information is attached to the items
def decorateParseItems(parseItems, ctrlName, frameName):
    for parseItem in parseItems:
        parseItem.ctrl_name = ctrlName
        parseItem.frame_name = frameName

#item_parent = 'parent'
# ident.method(params)
is_coll_item_init = re.compile('^[ \t]*(?P<ident>'+idp+')[.](?P<method>'+idc+\
      ')[ \t]*\([ \t,]*(?P<params>.*)(\)|,)')
class CollectionItemInitParse(PerLineParser):
    def __init__(self, line=None, comp_name='', method='', params=None):
        self.comp_name = comp_name
        self.ctrl_name = self.frame_name = '&None&'
        self.method = method
        if params is None: self.params = {}
        else: self.params = params
        if line:
            self.m = is_coll_item_init.search(line)
            if self.m:
                self.checkContinued(line)
                self.comp_name = self.m.group('ident')
                self.method = self.m.group('method')
                self.params = self.extractKVParams(self.m.group('params'))

    def renameFrameName(self, old_value, new_value):
        PerLineParser.renameFrameName(self, old_value, new_value)
        if 'id' in self.params:
            self.params['id'] = self.renameWindowId(self.params['id'],
                old_value, new_value, self.ctrl_name, self.ctrl_name)

    def renameCompName2(self, old_value, new_value):
        # Regenerate window ids
        if self.ctrl_name == old_value:
            self.ctrl_name = new_value
            if 'id' in self.params:
                self.params['id'] = self.renameWindowId(self.params['id'],
                      self.frame_name, self.frame_name, old_value, new_value)

        # Check for references
        src_old = Utils.srcRefFromCtrlName(old_value)
        for key, val in list(self.params.items())[:]:
            if val == src_old:
                self.params[key] = Utils.srcRefFromCtrlName(new_value)

    def prependFrameWinId(self, frame):
        idPrfx = self.getIdPrefix(frame)
        if 'id' in self.params and \
              self.params['id'] not in EventCollections.reservedWxNames:
            self.params['id'] = idPrfx + self.params['id']

    def asText(self, stripFrameWinIdPrefix=''):
        if stripFrameWinIdPrefix:
            idPrfx = self.getIdPrefix(stripFrameWinIdPrefix)
            params = {}
            params.update(self.params)
            if 'id' in params and self.checkId(params['id'], idPrfx):
                params['id'] = params['id'][len(idPrfx):]
        else:
            params = self.params
        return '%s.%s(%s)' %(self.comp_name, self.method, self.KVParamsAsText(params))

### EVT_evtname(name, func)
##is_event2p = re.compile('^[ \t]*EVT_(?P<evtname>'+idc+')[ \t]*\([ \t]*(?P<name>'+\
##  idp+')[ \t]*\,[ \t]*self[.](?P<func>'+idp+')(\)|,)$')
### EVT_evtname(name, wid, func)
##is_event3p = re.compile('^[ \t]*EVT_(?P<evtname>'+idc+')[ \t]*\([ \t]*(?P<name>'+\
##  idp+')[ \t]*\,(?P<wid>.*)[ \t]*\,[ \t]*self[.](?P<func>'+idp+')(\)|,)$')

# EVT_evtname(params)
#is_event = re.compile('^[ \t]*EVT_(?P<evtname>'+idc+')[ \t]*\([ \t]*(?P<params>.*)(\)|,)$')
is_event = re.compile('^self(?P<compname>[.]'+idc2+')*\.Bind\([ \t]*(?P<evtname>'+idc2+'),[ \t]*(?P<otherparams>.*)(\)|,)$')

##class EventParse(PerLineParser):
##    def __init__(self, line=None, comp_name='', event_name='',
##      trigger_meth = '', windowid = None):
##        self.comp_name = comp_name
##        self.ctrl_name = self.frame_name = '&None&'
##        self.event_name = event_name
##        self.trigger_meth = trigger_meth
##        self.prev_trigger_meth = ''
##        self.windowid = windowid
##        self.show_scope = 'own' # can be 'all', 'own'
##        if line:
##            self.m = is_event.search(line)
##            if self.m:
##                self.checkContinued(line)
##
##                params = self.m.group('params').split(',')
##                name = params[0].strip()
##                if name != 'self':
##                    self.comp_name = name[5:]
##                if len(params) == 2:
##                    self.trigger_meth = params[1].strip()[5:]
##                elif len(params) == 3:
##                    self.windowid = params[1].strip()
##                    self.trigger_meth = params[2].strip()[5:]
##
##                self.event_name = self.m.group('evtname')
##
##    def renameFrameName(self, old_value, new_value):
##        PerLineParser.renameFrameName(self, old_value, new_value)
##        if self.windowid:
##            self.windowid = self.renameWindowId(self.windowid,
##                old_value, new_value, self.ctrl_name, self.ctrl_name)
##
##    def renameCompName2(self, old_value, new_value):
##        if self.ctrl_name == old_value:
##            self.ctrl_name = new_value
##            if self.comp_name:
##                self.comp_name = new_value
##            # Check for command events
##            if self.windowid:
##                self.windowid = self.renameWindowId(self.windowid,
##                      self.frame_name, self.frame_name, old_value, new_value)
##
##    def prependFrameWinId(self, frame):
##        if self.windowid:
##            idPrfx = self.getIdPrefix(frame)
##            if self.windowid not in EventCollections.reservedWxNames:
##                self.windowid = idPrfx + self.windowid
##
##    def asText(self, stripFrameWinIdPrefix=''):
##        if self.windowid:
##            windowid = self.windowid
##            if stripFrameWinIdPrefix:
##                idPrfx = self.getIdPrefix(stripFrameWinIdPrefix)
##                if self.checkId(windowid, idPrfx):
##                    windowid = windowid[len(idPrfx):]
##
##            return 'EVT_%s(%s, %s, self.%s)' %(self.event_name,
##              Utils.srcRefFromCtrlName(self.comp_name), windowid, self.trigger_meth)
##        else:
##            return 'EVT_%s(%s, self.%s)' %(self.event_name,
##              Utils.srcRefFromCtrlName(self.comp_name), self.trigger_meth)

class EventParse(PerLineParser):
    def __init__(self, line=None, comp_name='', event_name='',
      trigger_meth = '', windowid = None):
        self.comp_name = comp_name
        self.ctrl_name = self.frame_name = '&None&'
        self.event_name = event_name
        self.trigger_meth = trigger_meth
        self.prev_trigger_meth = ''
        self.windowid = windowid
        self.show_scope = 'own' # can be 'all', 'own'
        if line:
            self.m = is_event.search(line)
            if self.m:
                self.checkContinued(line)

                params = self.m.group('otherparams').split(',')
                name = self.m.group('compname')
                if name is not None:
                    self.comp_name = name[1:]
                if len(params) == 1:
                    self.trigger_meth = params[0].strip()[5:]
                elif len(params) == 2:
                    self.trigger_meth = params[0].strip()[5:]
                    self.windowid = params[1].split('=')[-1].strip()

                self.event_name = self.m.group('evtname')

    def renameFrameName(self, old_value, new_value):
        PerLineParser.renameFrameName(self, old_value, new_value)
        if self.windowid:
            self.windowid = self.renameWindowId(self.windowid,
                old_value, new_value, self.ctrl_name, self.ctrl_name)

    def renameCompName2(self, old_value, new_value):
        if self.ctrl_name == old_value:
            self.ctrl_name = new_value
            if self.comp_name:
                self.comp_name = new_value
            # Check for command events
            if self.windowid:
                self.windowid = self.renameWindowId(self.windowid,
                      self.frame_name, self.frame_name, old_value, new_value)

    def prependFrameWinId(self, frame):
        if self.windowid:
            idPrfx = self.getIdPrefix(frame)
            if self.windowid not in EventCollections.reservedWxNames:
                self.windowid = idPrfx + self.windowid

    def asText(self, stripFrameWinIdPrefix=''):
        if self.windowid:
            windowid = self.windowid
            if stripFrameWinIdPrefix:
                idPrfx = self.getIdPrefix(stripFrameWinIdPrefix)
                if self.checkId(windowid, idPrfx):
                    windowid = windowid[len(idPrfx):]

            return '%s.Bind(%s, self.%s, id=%s)' %(Utils.srcRefFromCtrlName(self.comp_name), 
                self.event_name, self.trigger_meth, windowid)
        else:
            return '%s.Bind(%s, self.%s)' %(Utils.srcRefFromCtrlName(self.comp_name), 
                self.event_name, self.trigger_meth)

def testRename():
    cp = ConstructorParse("self.menu1 = wx.Menu(title = '')")
    print(cp.asText('wx.Frame1'))
    cp = ConstructorParse("self.button1 = wx.Button(id = wxID_WXFRAME1BUTTON1, label = 'button1', name = 'button1', parent = self, pos = wx.Point(232, 168), size = wx.Size(75, 23), style = 0)")
    print(cp.asText('wx.Frame1'))
    cp2 = ConstructorParse(cp.asText('wx.Frame1'))
    cp2.prependFrameWinId('wx.Frame2')
    print(cp2.asText())
    ciip = CollectionItemInitParse("parent.Append(checkable = False, helpString = '', id = wxID_WXFRAME1MENU1ITEMS0, item = 'Items0')")
    print(ciip.asText('wx.Frame1'))
    ciip2 = CollectionItemInitParse(ciip.asText('wx.Frame1'))
    ciip2.prependFrameWinId('wx.Frame2')
    print(ciip2.asText())
    #ep = EventParse("EVT_MENU(self, wxID_WXFRAME1MENU1ITEMS0, self.OnMenu1items0Menu)")
    #print ep.asText('wxFrame1')
    #ep2 = EventParse(ep.asText('wxFrame1'))
    #ep2.prependFrameWinId('wxFrame2')
    #print ep2.asText()

def testEvent():
    pass
    

def test():
    cp = parseMixedBody([ConstructorParse], [
     "        wxFrame.__init__(self, style = wxDEFAULT_FRAME_STYLE, name = '', ",
     "              parent = prnt, title = 'wxFrame2', id = wxID_WXFRAME2, ",
     "              pos = (-1, -1), size = (-1, -1))  ",
     "        self._init_utils()",
    ])#[0][ConstructorParse]

    print(cp)#[0].params

if __name__ == '__main__':
    test()
