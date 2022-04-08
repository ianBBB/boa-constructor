#-----------------------------------------------------------------------------
# Name:        HTMLCyclops.py
# Purpose:     Displays a Cyclops report in HTML format.
#              Pretty much a copy of code from Cyclops by Tim Peters
#
# Author:      of changes, Riaan Booysen
#
# Created:     2000/05/20
# RCS-ID:      $Id$
# Copyright:   of changes (c) 1999 - 2007 Riaan Booysen
# Licence:     Dual GPL & Python
#-----------------------------------------------------------------------------

from ExternalLib import Cyclops

clGreen = '#228822'
clRed = '#882222'

def replaceLT(str):
    return '<font color="#000060" size="-1"><b>'+str.replace('<', '&lt;')+'</b></font>'

import repr
_repr = repr
del repr

class _CyclopsHTMLRepr(_repr.Repr):

    def __init__(self):
        _repr.Repr.__init__(self)
        # Boost the limit on types we don't know about; else it's too
        # easy to get a useless repr string when adding new types via
        # CycleFinder.chase_type.
        # Perhaps better to expose this class too, but-- sheesh --
        # this module is complicated enough!
        self.maxstring = self.maxother = 40

    # override base dictionary formatter; the code is almost the same,
    # we just leave the dict order alone

    def repr_dictionary(self, x, level):
        n = len(x)
        if n == 0:
            return replaceLT('{}')
        if level <= 0:
            return replaceLT('{...}')
        s = ''
        for k, v in x.items()[:min(n, self.maxdict)]:
            if s:
                s = s + ', '
            s = s + self.repr1(k, level-1)
            s = s + ': ' + self.repr1(v, level-1)
        if n > self.maxdict:
            s = s + ', ...'
        return '{' + s + '}'

    # don't chop instance, class or instance method reprs

    def repr_instance(self, x, level):
        try:
            return replaceLT(`x`)
            # Bugs in x.__repr__() can cause arbitrary
            # exceptions -- then make up something
        except:
            return replaceLT('<' + x.__class__.__name__ + ' instance at ' + \
                   hex(id(x))[2:] + '>')

    def repr_class(self, x, level):
        return replaceLT(`x`)

    repr_instance_method = repr_class

_quickrepr = _CyclopsHTMLRepr().repr

#def find_declarer(cls, attr):
#    while len(cls.__bases__):
#        if obj.__dict__.has_key(attr):
#            return obj

def find_declarer(cls, attr, found = 0):
#    print 'find_declarer', cls, attr, found
    if found:
        return found, cls
    else:
        for base in cls.__bases__:
            if base.__dict__.has_key(attr):
                return 1, base
            else:
                found, basecls = find_declarer(base, attr, 0)
    return found, cls

##print 'test find_declarer'
##print find_declarer(_CyclopsHTMLRepr, 'repr1')
##
##class A:
##    def __init__(self):
##        self.a = 10
##class B(A): pass
##
##a = A()
##b = B()
##print find_declarer(b.__class__, 'a')
##
indent = '&nbsp;&nbsp;&nbsp;&nbsp;'

class CycleFinderHTML(Cyclops.CycleFinder):
    def __init__(self):
        Cyclops.CycleFinder.__init__(self)
        self.report = []
        self.header = ['<h1>Cyclops report</h1>']#<h3> %s</h3><br>'%path.basename(self.model.filename)]

    def _add_section(self, name, text, docs = ''):
        if docs is None:
            docs = ''
        elif docs:
            docs = docs + '<br><br>'
        self.header.append('<a href="#%s">%s</a><br>'%(name, text))
        self.report.append('<a NAME="%s"><h3>%s:</h3></a>'%(name, text))
        self.report.append(docs)

    def _print_separator(self):
        self.report.append('<hr>')

    def _print_cycle(self, slice):
        n = len(slice)
        assert n >= 2
        self.report.append('<b>%d-element cycle</b><br>' % (n-1))
        for i in xrange(n):
            obj = slice[i][0]
            self.show_obj(obj)
            if i < n-1:
                if type(obj).__name__ == 'instance method':
                    attrib = obj.im_func.func_name

                    found, attrib_decl = find_declarer(obj.im_class, attrib)
#                    print 'XXXXX', found, attrib_decl, attrib
                    self.report.append('%s<a href="attrlink://%s.%s">this%s</a>-><br>' \
                      % (indent, str(attrib_decl), attrib, attrib))
                else:
                    index = slice[i+1][1]
                    attrib = self.tag_dispatcher[type(obj)](obj, index)

                    if attrib[0] == '.' and hasattr(obj, "__class__"):
                        found, attrib_decl = find_declarer(obj.__class__, attrib[1:])
                        self.report.append('%s<a href="attrlink://%s%s">this%s</a>-><br>' \
                          % (indent, str(attrib_decl), attrib, attrib))
                    else:
                        self.report.append(indent+'this' + \
                          attrib+ '-><br>')

    def show_obj(self, obj):
        """obj -> print short description of obj to sdtout.

        This is of the form

        <address> rc:<refcount> <typename>
            repr: <shortrepr>

        where
        <address>
            hex address of obj
        <refcount>
            If find_cycles() has been run and obj is in the root set
            or was found in a cycle, this is the number of references
            outstanding less the number held internally by
            CycleFinder.  In most cases, this is what the true
            refcount would be had you not used CycleFinder at all.
            You can screw that up, e.g. by installing a cycle filter
            that holds on to references to one or more cycle elements.
            If find_cycles() has not been run, or has but obj wasn't
            found in a cycle and isn't in the root set, <refcount> is
            "?".
        <typename>
            type(obj), as a string.  If obj.__class__ exists, also
            prints the class name.
        <shortrepr>
            repr(obj), but using a variant of the std module repr.py
            that limits the number of characters displayed.
        """

        objid = id(obj)
        rc = self.id2rc.get(objid, "?")
#        print type(obj).__name__, `type(obj).__name__`
        self.report.append('<font size="-1" color="#700060">%s</font> rc: %d <b>%s</b>'%(hex(objid), rc, type(obj).__name__))
        if hasattr(obj, "__class__"):
            self.report.append('<a href="classlink://%s">%s</a>'%(str(obj.__class__), str(obj.__class__)))
        self.report.append('<br>')
        self.report.append('&nbsp;&nbsp;&nbsp;&nbsp;%s<br>'%_quickrepr(obj))

    def add_stat_line(self, desc, value):
        if type(value) == type([]):
            lns = []
            for itm in value:
                lns.append('<td><b>%s</b></td>'%str(itm))
            self.report.append('<tr><td>%s</td>%s</tr>'%(desc, ' '.join(lns)))
        else:
            self.report.append('<tr><td>%s</td><td><b>%s</b></td></tr>' % (desc, str(value)))

    def stats_list(self):
        if len(self.cycles):
            cf = '<font size="+1" color="#FF0000">%d</font>' % len(self.cycles)
        else:
            cf = '<font size="+1" color="#00FF00">%d</font>' % len(self.cycles)
        return [('Objects in root set', len(self.roots)),
                ('Distinct structured objects reachable', len(self.seenids)),
                ('Distinct structured objects in cycles', len(self.cycleobjs)),
                ('Cycles found', cf),
                ('Cycles filtered out', self.ncyclesignored),
                ('Strongly connected components', len(self.sccno2objs)),
                ('Arcs examined', self.narcs)]

    def show_stats(self, stats_list, name = 'Stats', title = 'Statistics'):
        """Print statistics for the last run of find_cycles."""
        self._print_separator()
        self._add_section(name, title)
        self.report.append('<table>')
        for desc, value in stats_list:
            self.add_stat_line(desc, value)
        self.report.append('</table>')

#    def show_iterated_stats(self):


    def show_cycles(self):
        self._print_separator()
        self._add_section('AllCycles', 'All cycles')
        n = len(self.cycles)
        self.report.append('<ul>')
        for i in xrange(n):
            self.report.append('<li>')
            self._print_cycle(self.cycles[i])
#            if i < n-1:
#                self._print_separator()
            self.report.append('</li>')
        self.report.append('</ul>')

    def show_cycleobjs(self, compare=Cyclops.typename_address_cmp):
        """Each distinct object find_cycles found in a
        cycle is displayed.  The set of objects found in cycles is
        first sorted by the optional "compare" function.  By default,
        objects are sorted using their type name as the primary key
        and their storage address (id) as the secondary key; among
        objects of instance type, sorts by the instances' class names;
        among objects of class type, sorts by the classes' names.
        """

        self._print_separator()
        self._add_section('CycleObjs', 'Objects involved in cycles', self.show_cycleobjs.__doc__)
        objs = self.cycleobjs.values()
        objs.sort(compare)
        for obj in objs:
            self.show_obj(obj)

    def show_sccs(self, compare=Cyclops.typename_address_cmp):
        """Shows the objects in cycles partitioned into
        strongly connected components (that is, the largest groupings
        possible such that each object in an SCC is reachable from every
        other object in that SCC).  Within each SCC, objects are sorted
        as for show_cycleobjs.
        """

        self._print_separator()
        self._add_section('SCC', 'Cycle objects partitioned into maximal SCCs', self.show_sccs.__doc__)
        sccs = self.sccno2objs.values()
        n = len(sccs)
        self.report.append('<ul>')
        for i in xrange(n):
            self.report.append('<li><b>SCC %d of %d</b><br>' %(i+1, n))
            objs = sccs[i]
            objs.sort(compare)
            for obj in objs:
                self.show_obj(obj)
            self.report.append('</li>')
        self.report.append('</ul>')

    def show_arcs(self, compare=None):
        """Briefly, each arc in a
        cycle is categorized by the type of the source node, the kind
        of arc (how we got from the source to the destination), and
        the type of the destination node.  Each line of output
        consists of those three pieces of info preceded by the count
        of arcs of that kind.  By default, the rows are sorted first
        by column 2 (source node type), then by columns 3 and 4.
        """

        self._print_separator()
        self._add_section('ArcTypes', 'Arc types involved in cycles', self.show_arcs.__doc__)
        items = self.arctypes.items()
        if compare:
            items.sort(compare)
        else:
            items.sort()
        for triple, count in items:
            self.report.append('%6d %-20s %-20s -> %-20s<br>' % ((count,) + triple))

    def show_chased_types(self):
        ct = self.get_chased_types()
        self.header.append('<h3>Installed chasers</h3>')
        self.header.append('<ul>')
        if len(ct):
            for ch in ct:
                self.header.append('<li>%s</li>'%ch.__name__)
        else:
            self.header.append('<li>None</li>')
        self.header.append('</ul>')

    def iterate_til_steady_state(self, show_objs = 0, summary = 1):
        self._print_separator()
        self._add_section('CycleCycles', 'Purge root set')
        self.header.append('<ul>')
        cc = 0
        self.report.append('Non-cyclic root set objects:')
        stats = []
        self.report.append('<ul>')
        try:
            while 1:
#                print "*" * 70
#                print "non-cyclic root set objects:"
                sawitalready = {}
                numsurvivors = numdead = 0
                class_count = {}
                name = 'DeadRootSet%d'%cc
                desc = 'Iteration %d'%cc
                self.header.append('<a href="#%s">%s</a><br>'%(name, desc))
                self.report.append('<li><a NAME="%s"><b>%s</b></a></li><br>'%(name, desc))
                for rc, cyclic, x in self.get_rootset():
                    if not sawitalready.has_key(id(x)):
                        sawitalready[id(x)] = 1
                        if rc == 0:
                            numdead = numdead + 1
                            if show_objs:
                                self.report.append('<font color="%s">DEAD </font>'%clGreen)
                                self.show_obj(x)
                        elif not cyclic:
                            numsurvivors = numsurvivors + 1
                            if show_objs: self.show_obj(x)
                            if hasattr(x, '__class__'):
                                cn = x.__class__.__name__
                                if class_count.has_key(cn):
                                    class_count[cn][id(x)] = 0
                                else:
                                    class_count[cn] = {id(x):0}

                x = None
                desc = '<br><b><font color="%s">%d</font> dead; <font color="%s">%d</font> non-cycle & alive</b><br>' % (clGreen, numdead, clRed, numsurvivors)
                self.report.append(desc)

                desc = '<br><b>Summary of instance count:</b><br>'
                self.report.append(desc)
                clss = class_count.keys()
                clss.sort()
                for cls in clss:
                    desc = '%s: %d<br>' % (cls, len(class_count[cls]))
                    self.report.append(desc)

                sts = self.stats_list()+[('Dead', numdead), ('Non-cycle & alive', numsurvivors)]
                for idx in range(len(sts)):
                    if len(stats) < idx + 1:
                        stats.append((sts[idx][0], [sts[idx][1]]))
                    else:
                        stats[idx][1].append(sts[idx][1])

                if numdead == 0:
                    break
                self.find_cycles(1)

                cc = cc + 1

        finally:
            self.report.append('</ul>')
            self.header.append('</ul>')
            self.show_stats(stats, 'StatsFin', 'Purge root set statistics')

    def get_page(self):
        self.show_chased_types()
        return '\n'.join(self.header)+'\n'.join(self.report)
