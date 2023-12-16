# ----------------------------------------------------------------------
# Name:        moduleparse.py
# Purpose:
#
# Author:      Riaan Booysen, based on 'pyclbr.py'
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   Changes (c) 1999 - 2007 Riaan Booysen
# Licence:     Python
# ----------------------------------------------------------------------

"""Parse one Python file and retrieve classes, methods, functions,
store the code spans and facilitate the manipulation of method bodies

This module is based on 'pyclbr.py' from the standard python lib

BUGS
Nested methods and classes not handled

<from pyclbr.py>
Continuation lines are not dealt with at all and strings may confuse
the hell out of the parser, but it usually works.

Continuation lines are now handled for class, method and function defs
"""

# XXX Dedented block (0 indent) should trigger end of class/func

# XXX Keep track of 'return' in function bodies for possible return type
# XXX identification

# XXX Add regex for __calling__ code.
# XXX Mainly so that line conts can be used

import os, sys
import importlib
import re
import string, pprint
# from types import IntType, StringType    #id([][,]id)*

import Preferences, Utils
from Utils import _

import methodparse

method_indent = Utils.getIndentBlock()
body_indent = method_indent * 2

id = '[A-Za-z_][A-Za-z0-9_]*'
is_id = re.compile(id)
obj_def = '[A-Za-z_][A-Za-z0-9_.]*'
blank_line = re.compile('^[ \t]*($|#)')
is_class = re.compile(r'^[ \t]*class[ \t]+(?P<id>%s)[ \t]*(?P<sup>\([^)]*\))?[ \t]*:' % id)
is_class_start = re.compile(r'^[ \t]*class[ \t]+(?P<id>%s)[ \t]*[\(\:]' % id)
is_method = re.compile(r'^[ \t]*def[ \t]+(?P<id>%s)[ \t]*\((?P<sig>.*)\)[ \t]*[:][ \t]*$' % id)
is_method_start = re.compile(r'^[ \t]*def[ \t]+(?P<id>%s)[ \t]*\(' % id)
is_func = re.compile(r'^def[ \t]+(?P<id>%s)[ \t]*\((?P<sig>.*)\)[ \t]*[:][ \t]*$' % id)
is_func_start = re.compile(r'^def[ \t]+(?P<id>%s)[ \t]*\(' % id)
is_attrib = re.compile(r'[ \t]*self[.](?P<name>%s)[ \t]*=[ \t]*' % id)
is_attrib_from_call = re.compile(r'[ \t]*self[.](?P<name>%s)[ \t]*=[ \t]*(?P<classpath>%s)\(' % (id, obj_def))
is_name = re.compile(r'[ \t]*(?P<name>%s)[ \t]*=[ \t]*' % id)
is_name_from_call = re.compile(r'[ \t]*(?P<name>%s)[ \t]*=[ \t]*(?P<classpath>%s)\(' % (id, obj_def))
## HELP don't know what are_names is meant to search for nor how to fix it (it produces and error when uncommented).
# are_names = re.compile(r'[ \t]*((?P<names>%s)[ \t]*[,][ \t]*)+(?P<lastname>%s)[ \t]*)*=[ \t]*' % (id, id))
is_import = re.compile(r'^[ \t]*import[ \t]+(?P<imp>[^#;]+)')
is_from = re.compile(r'^[ \t]*from[ \t]+(?P<module>%s([ \t]*\\.[ \t]*%s)*)[ \t]+import[ \t]+(?P<imp>[^#;]+)' % (id, id))
is_for = re.compile(r'^[ \t]*for[ \t]+(?P<names>.+)[ \t]+in[ \t]+.+[ \t]*:')
dedent = re.compile(r'^[^ \t]')
indent = re.compile(r'^[^ \t]*')
is_doc_quote = re.compile("'''")
id_doc_quote_dbl = re.compile('"""')
is_todo = re.compile(r'^[ \t]*# XXX')
is_todo2 = re.compile(r'^[ \t]*# TODO:')
is_wid = re.compile(r'^\[(?P<wids>.*)\][ \t]*[=][ \t]*wxNewId[(](?P<count>\d+)[)]$')
is_break_line = re.compile('^#-+(?P<descr>.*%s)-+$' % obj_def)
is_resource = '(?P<imppath>%s)[.]get(?P<imgname>%s)%%s[(][)]' % (obj_def, id)
is_resource_bitmap = re.compile(is_resource % 'Bitmap')
is_resource_icon = re.compile(is_resource % 'Icon')

sq3string = r"(\b[rR])?'''([^'\\]|\\.|'(?!''))*(''')?"
dq3string = r'(\b[rR])?"""([^"\\]|\\.|"(?!""))*(""")?'
is_doc = re.compile('(?P<string>%s|%s)' % (sq3string, dq3string))

# XXX Provide for lines between entries
sep_line = '#[-]+.*'
str_name = '# Name:[ \t]*(?P<name>.*)'
str_purpose = '# Purpose:[ \t]*(?P<purpose>.*)'
str_author = '# Author:[ \t]*(?P<author>.*)'
str_created = '# Created:[ \t]*(?P<created>.*)'
str_rcs_id = '# RCS-ID:[ \t]*(?P<rcs_id>.*)'
str_copyright = '# Copyright:[ \t]*(?P<copyright>.*)'
str_licence = '# Licence:[ \t]*(?P<licence>[^#]*#[-]+)'

is_info = re.compile(sep_line + str_name + str_purpose + str_author + \
                     str_created + str_rcs_id + str_copyright + str_licence, re.DOTALL)


class ModuleParseError(Exception):
    pass


class CodeBlock:
    def __init__(self, sig, start, end):
        self.signature = sig
        self.start = start
        self.end = end
        self.locals = {}

    def __repr__(self):
        return '[%d - %d]' % (self.start, self.end)

    def renumber(self, from_line, increment):
        if self.start > from_line:
            self.start = self.start + increment
            self.end = self.end + increment
        elif self.end > from_line:
            self.end = self.end + increment

        for attr in list(self.locals.values()):
            attr.renumber(from_line, increment)

    def contains(self, line):
        return line >= self.start and line <= self.end

    def size(self):
        return self.end - self.start

    def getparams(self):
        self.params = {}
        for fld in methodparse.safesplitfields(self.sig, ','):
            kv = fld.split('=', 1)
            if len(kv) == 1:
                self.params[kv] = None
            else:
                self.params[kv[0]] = kv[1]
        return self.params

    def localnames(self):
        locls = list(self.locals.keys())
        return [name for name in [fld.split('=')[0]
                                  for fld in methodparse.safesplitfields(self.signature, ',')]
                if name not in locls] + list(self.locals.keys())


class Attrib:
    def __init__(self, name, lineno, objtype=''):
        self.name = name
        self.lineno = lineno
        self.objtype = objtype

    def renumber(self, from_line, increment):
        self.lineno = renumber(self.lineno, increment, from_line)


def renumber(lineno, increment, start):
    if lineno > start:
        return lineno + increment
    return lineno


# each Python class is represented by an instance of this class
class Class:
    """ Class to represent a Python class. """

    def __init__(self, module, name, super, file, lineno):
        self.module = module
        self.name = name
        if super is None:
            super = []
        self.super = super
        self.methods = {}
        self.method_order = []
        self.attributes = {}
        self.class_attributes = {}
        self.file = file
        self.block = CodeBlock('', lineno, lineno)

    def __repr__(self):
        return self.name + repr(self.block) + '\n' + '\n'.join(
            ['    ' + meth + repr(self.methods[meth]) for meth in self.method_order])

    def add_method(self, name, sig, linestart, lineend=None, to_bottom=1):
        if not lineend: lineend = linestart
        self.methods[name] = CodeBlock(sig, linestart, lineend)
        if to_bottom:
            self.method_order.append(name)
        else:
            self.method_order.insert(0, name)

    def end_method(self, name, lineend):
        self.methods[name].end = lineend

    def remove_method(self, name):
        del self.methods[name]
        self.method_order.remove(name)

    def add_attr(self, name, lineno, thetype=''):
        if name in self.attributes:
            self.attributes[name].append(CodeBlock(thetype, lineno, lineno))
        else:
            self.attributes[name] = [CodeBlock(thetype, lineno, lineno)]

    def add_class_attr(self, name, lineno, thetype=''):
        if name in self.class_attributes:
            self.class_attributes[name].append(CodeBlock(thetype, lineno, lineno))
        else:
            self.class_attributes[name] = [CodeBlock(thetype, lineno, lineno)]

    def add_local(self, name, meth, lineno, thetype=''):
        if meth in self.methods:
            if name not in self.methods[meth].locals:
                self.methods[meth].locals[name] = Attrib(name, lineno, thetype)

    def renumber(self, start, deltaLines):
        self.block.renumber(start, deltaLines)
        for block in list(self.methods.values()):
            block.renumber(start, deltaLines)
        for attr_lst in list(self.attributes.values()):
            for block in attr_lst:
                block.renumber(start, deltaLines)

    def getMethodForLineNo(self, line_no):
        for name, meth in list(self.methods.items()):
            if meth.contains(line_no):
                return name, meth
        return '', None

    def calcExtent(self):
        # return max(*[m.end for m in self.methods.values()])
        ext = 0
        for meth in list(self.methods.values()):
            if meth.end > ext:
                ext = meth.end
        return ext


class Test2: pass


class Module:
    """ Represents a Python module.

    Parses and maintains dictionaries of the classes and
    functions defined in a module. """

    def finaliseEntry(self, cur_class, cur_meth, cur_func, lineno):
        """ When a new structure is encountered, finalise the current
        structure, whatever it is. """
        if cur_class:
            # Gobble up blank lines
            lineno = lineno - 1
            while not self.source[lineno - 1].strip():
                lineno = lineno - 1

            if cur_meth:
                cur_class.end_method(cur_meth, lineno)
                cur_meth = ''
            cur_class.block.end = lineno

            cur_class = None
            cur_func = None

        elif cur_func:
            cur_func.end = lineno - 1
            cur_func = None

        return cur_class, cur_meth, cur_func

    def readline(self):
        line = self.source[self.lineno]
        self.lineno = self.lineno + 1
        return line

    def decomment(self, line):
        return methodparse.safesplitfields(line, '#', returnBlanks=1)[0]

    line_conts = (',', '\\', '(')

    def readcontinuedlines(self, lineno, terminator):
        contline = ''
        while lineno < len(self.source):
            line = self.decomment(self.source[lineno]).rstrip()
            if line:
                if line[-1] in self.line_conts:
                    while line and line[-1] == '\\':
                        line = line[:-1]
                    contline = contline + line
                    lineno = lineno + 1
                    continue
                elif not terminator:
                    contline = contline + line
                    return lineno, contline
                elif line[-1] in string.digits + string.ascii_letters + '_':
                    contline = contline + line
                    lineno = lineno + 1
                    continue
                elif line[-1] == terminator:
                    contline = contline + line
                    return lineno, contline
                else:
                    break
            else:
                lineno = lineno + 1
                continue

        return -1, ''

    def __init__(self, module, modulesrc, eol=os.linesep):  # , classes = {}, class_order = [], file = ''):
        self.classes = {}  # classes
        self.class_order = []  # class_order
        self.functions = {}
        self.function_order = []
        self.todos = []
        self.wids = []
        self.name = module
        self.globals = {}
        self.global_order = []
        self.break_lines = {}

        # {name: [lineno], ...}
        self.imports = {}
        self.from_imports = {}
        self.from_imports_names = {}
        self.from_imports_star = []
        self.from_imports_star_cache = {}

        cur_class = None
        cur_meth = ''
        cur_func = None
        file = ''
        self.lineno = 0
        self.source = modulesrc
        self.eol = os.linesep
        if self.source:
            if self.source[0].endswith('\r\n'):  # win
                self.eol = '\r\n'
            elif self.source[0].endswith('\n'):  # unix
                self.eol = '\n'
            elif self.source[0].endswith('\r'):  # mac
                self.eol = '\r'

        self.loc = 0
        while self.lineno < len(self.source):
            self.loc = self.loc + 1
            line = self.readline().rstrip()

            cont, cur_class, cur_meth, cur_func = self.parseLine(module, file,
                                                                 line, self.lineno, cur_class, cur_meth, cur_func)

        # if it's the last class in the source, it will not dedent
        # check manually
        cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class, cur_meth,
                                                           cur_func, self.lineno + 1)

    def getObjType(self, rem):
        if rem:
            if rem[0] in ('"', "'"):
                return 'string'
            elif rem[0] in string.digits + '+-':
                return 'number'
            elif rem[0] == '{':
                return 'dict'
            elif rem[0] == '[':
                return 'list'
            elif rem[0] == '(':
                return 'tuple'
            elif rem[0] in string.ascii_letters + '_':
                return 'ref'
            # else: print 'Unhandled objtype', rem
        return ''

    def parseLineIsolated(self, line, lineno):
        cls = self.getClassForLineNo(lineno)
        if cls:
            mthName, mth = cls.getMethodForLineNo(lineno)
            return self.parseLine('', '', line, lineno, cls, mthName, None)
        else:
            fnc = self.getFunctionForLineNo(lineno)
            if fnc:
                return self.parseLine('', '', line, lineno, None, '', fnc)
        return self.parseLine('', '', line, lineno, None, '', None)

    def parseLine(self, module, file, line, lineno, cur_class, cur_meth, cur_func):
        res = is_todo.match(line) or is_todo2.match(line)
        if res:
            self.todos.append((lineno, line[res.span()[1]:].strip()))
            return 0, cur_class, cur_meth, cur_func

        if blank_line.match(line):
            # ignore blank (and comment only) lines
            self.loc = self.loc - 1
            if len(line) == 80:
                res = is_break_line.match(line)
                if res:
                    self.break_lines[lineno] = res.group('descr')

            return 0, cur_class, cur_meth, cur_func

        ##            if dedent.match(line):
        ##                print 'dedent', self.lineno

        res2 = is_class_start.match(line)
        if res2:
            res = is_class.match(line)
            if not res:
                # check for line conts
                lno, contl = self.readcontinuedlines(lineno - 1, ':')
                if lno == -1:
                    return 0, cur_class, cur_meth, cur_func
                class_name = res2.group('id')
                inherit = contl[contl.find('('):contl.rfind(')') + 1]
            else:
                class_name = res.group('id')
                inherit = res.group('sup')

            # we found a class definition
            cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class,
                                                               cur_meth, cur_func, lineno)
            if inherit:
                # the class inherits from other classes
                inherit = inherit[1:-1].strip()
                names = []
                for n in inherit.split(','):
                    n = n.strip()
                    if n:
                        if n in self.classes:
                            # we know this super class
                            n = self.classes[n]
                        else:
                            c = n.split('.')
                            if len(c) > 1:
                                # super class is of the
                                # form module.class:
                                # look in module for class
                                m = c[-2]
                                c = c[-1]
                        names.append(n)
                inherit = names
            # remember this class

            # An attempt at maintaining state on the fly
            # (way to much effort, must be done for every parsed type)
            ##           order = -1
            ##            for cn in self.class_order[:]:
            ##                c = self.classes[cn]
            ##                if c.block.start == lineno:
            ##                    print 'inplace class rename %d'%lineno
            ##                    # we are replacing (renaming) a class in-place
            ##                    if c.name != class_name:
            ##                        del self.classes[c.name]
            ##                        self.classes[class_name] = c
            ##
            ##                        idx = self.class_order.index(c.name)
            ##                        del self.class_order[idx]
            ##                        self.class_order.insert(idx, class_name)
            ##
            ##                    c.name = class_name
            ##                    c.super = inherit
            ##                    return 0, cur_class, cur_meth, cur_func
            ##
            ##                if lineno < c.block.start and order == -1:
            ##                    print 'non append order %d above %s:%d'%(lineno, c.name, c.block.start)
            ##                    order = self.class_order.index(cn)
            ##            else:
            cur_class = Class(module, class_name, inherit, file, lineno)
            cur_meth = ''
            self.classes[class_name] = cur_class
            self.class_order.append(class_name)
            ##            if order == -1:
            ##                self.class_order.append(class_name)
            ##            else:
            ##                self.class_order.insert(order, class_name)

            return 0, cur_class, cur_meth, cur_func

        res2 = is_func_start.match(line)
        if res2:
            res = is_func.match(line)
            if not res:
                lno, contl = self.readcontinuedlines(lineno - 1, ':')
                if lno == -1:
                    return 0, cur_class, cur_meth, cur_func
                res_group_id = res2.group('id')
                res_group_sig = contl[contl.find('(') + 1:contl.rfind(')')]
            else:
                res_group_id = res.group('id')
                res_group_sig = res.group('sig')

            cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class,
                                                               cur_meth, cur_func, lineno)
            func_name = res_group_id
            cur_func = self.functions[func_name] = CodeBlock(res_group_sig, lineno, 0)
            self.function_order.append(func_name)
            return 0, cur_class, cur_meth, cur_func

        res2 = is_method_start.match(line)
        if res2:
            res = is_method.match(line)
            if not res:
                lno, contl = self.readcontinuedlines(lineno - 1, ':')
                if lno == -1:
                    return 0, cur_class, cur_meth, cur_func
                res_group_id = res2.group('id')
                res_group_sig = contl[contl.find('(') + 1:contl.rfind(')')]
            else:
                res_group_id = res.group('id')
                res_group_sig = res.group('sig')

            # found a method definition
            if cur_class:
                # and we know the class it belongs to
                if cur_meth:
                    cur_class.end_method(cur_meth, lineno - 1)
                meth_name = res_group_id
                cur_class.add_method(meth_name, res_group_sig, lineno)
                cur_meth = meth_name
            return 0, cur_class, cur_meth, cur_func

        res = is_attrib_from_call.match(line)
        if res:
            # found a attribute binding
            if cur_class:
                # and we know the class it belongs to
                classpath = res.group('classpath')
                cur_class.add_attr(res.group('name'), lineno, classpath)

            return 0, cur_class, cur_meth, cur_func

        res = is_attrib.match(line)
        if res:
            # found a attribute binding with possible object type
            if cur_class:
                # and we know the class it belongs to
                rem = line[res.end():]
                objtype = self.getObjType(rem)
                cur_class.add_attr(res.group('name'), lineno, objtype)

            return 0, cur_class, cur_meth, cur_func

        res = is_for.match(line)
        if res:
            names = []
            for name in methodparse.safesplitfields(res.group('names'), ','):
                name = name.strip('()')
                if is_id.match(name):
                    names.append(name)

            if cur_class:
                # and we know the class it belongs to
                if cur_meth:
                    for name in names:
                        cur_class.add_local(name, cur_meth, lineno)
                # class variablr
                else:
                    for name in names:
                        cur_class.add_class_attr(name, lineno)
            # function
            elif cur_func:
                for name in names:
                    if name not in list(cur_func.locals.keys()):
                        cur_func.locals[name] = Attrib(name, lineno)
            # global
            else:
                for name in names:
                    if name not in self.globals:
                        self.globals[name] = CodeBlock('', self.lineno, lineno)
                        self.global_order.append(name)

            return 0, cur_class, cur_meth, cur_func

        if dedent.match(line):
            # end of class definition
            cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class,
                                                               cur_meth, cur_func, lineno)

        res = is_import.match(line)
        if res:
            if line[-1] == '\\':
                lno, contl = self.readcontinuedlines(lineno - 1, '')
                if lno == -1:
                    return 0, cur_class, cur_meth, cur_func
                res = is_import.match(contl)
                if not res:
                    return 0, cur_class, cur_meth, cur_func

            # import module
            for n in res.group('imp').split(','):
                n = n.strip()
                i = [s for s in n.split('.')]
                self.imports['.'.join(i)] = [lineno]
            return 0, cur_class, cur_meth, cur_func

        res = is_from.match(line)
        if res:
            # from module import stuff
            if line[-1] == '\\':
                lno, contl = self.readcontinuedlines(lineno - 1, '')
                if lno == -1:
                    return 0, cur_class, cur_meth, cur_func
                res = is_from.match(contl)
                if not res:
                    return 0, cur_class, cur_meth, cur_func

            mod, names = res.group('module'), res.group('imp').split(',')
            self.from_imports[mod] = [lineno]

            for n in names:
                n = n.strip()
                if n:
                    self.from_imports[mod].append(n)
                    if n != '*':
                        self.from_imports_names[n] = mod
                    else:
                        self.from_imports_star.append(mod)

            return 0, cur_class, cur_meth, cur_func

        res = is_wid.match(line)
        if res:
            self.wids.append((lineno, res))

        objtype = None
        res = is_name_from_call.match(line)
        if res:
            objtype = res.group('classpath')

        res = is_name.match(line)
        if res:
            rem = line[res.end():]
            if objtype is None:
                objtype = self.getObjType(rem)
            # found a name binding
            # class attribute
            if cur_class:
                # and we know the class it belongs to
                if cur_meth:
                    cur_class.add_local(res.group('name'), cur_meth, lineno, objtype)
                else:
                    # must be class attr
                    cur_class.add_class_attr(res.group('name'), lineno, line[res.end():])
            # function
            elif cur_func:
                name = res.group('name')
                if name not in list(cur_func.locals.keys()):
                    cur_func.locals[name] = Attrib(name, lineno, objtype)
            ##                if self.functions.has_key(cur_func):
            ##                    if name not in self.functions[cur_func].locals.keys():
            ##                        self.functions[cur_func].locals[name] = Attrib(name, lineno)
            # global
            else:
                name = res.group('name')
                if name not in self.globals:
                    self.globals[name] = CodeBlock(objtype, self.lineno, lineno)
                    self.global_order.append(name)

            return 0, cur_class, cur_meth, cur_func

        return 1, cur_class, cur_meth, cur_func

    def find_declarer(self, cls, attr, value, found=0):
        if found:
            return found, cls, value
        else:
            for base in cls.super:
                if isinstance(base, str):
                    return found, cls, value
                if attr in base.attributes:
                    return 1, base, base.attributes[attr]
                elif attr in base.methods:
                    return 1, base, base.methods[attr]
                elif attr in base.class_attributes:
                    return 1, base, base.class_attributes[attr]
                else:
                    found, cls, value = self.find_declarer(base, attr, value, 0)
        return found, cls, value

    def extractClassBody(self, class_name):
        block = self.classes[class_name].block
        return self.source[block.start:block.end]

    def addMethod(self, class_name, method_name, method_params, method_body, to_bottom=1):
        new_length = len(method_body) + 2
        if not method_body: return
        a_class = self.classes[class_name]
        if method_name in a_class.method_order:
            raise Exception(_('Method exists'))

        # Add a method code block
        if to_bottom or not a_class.method_order:
            ins_point = a_class.calcExtent()
            pre_blank = ['']
            post_blank = []
        else:
            ins_point = a_class.methods[a_class.method_order[0]].start - 1
            pre_blank = []
            post_blank = ['']

        # renumber code blocks
        self.renumber(new_length, ins_point)

        a_class.add_method(method_name, method_params, ins_point + 1, ins_point + \
                           new_length, to_bottom)

        # Add in source
        self.source[ins_point: ins_point] = \
            pre_blank + ['%sdef %s(%s):' % (method_indent, method_name, method_params)] + \
            method_body + post_blank

    def addLine(self, line, line_no):
        self.source.insert(line_no, line)
        self.renumber(1, line_no)

    def extractMethodBody(self, class_name, method_name):
        block = self.classes[class_name].methods[method_name]
        return self.source[block.start:block.end]

    def extractFunctionBody(self, function_name):
        block = self.functions[function_name]
        return self.source[block.start:block.end]

    def renumber(self, deltaLines, start):
        if deltaLines:
            for cls in list(self.classes.values()):
                cls.renumber(start, deltaLines)
            for func in list(self.functions.values()):
                func.renumber(func.start, deltaLines)
            for glob in list(self.globals.values()):
                glob.renumber(glob.start, deltaLines)
            for imptype in (self.imports, self.from_imports):
                for imp, lns in list(imptype.items()):
                    # imptype[imp][0] = renumber(imptype[imp][0], deltaLines, start)
                    lns[0] = renumber(lns[0], deltaLines, start)

    ##                    l = []
    ##                    for ln in lns:
    ##                        if ln > start:
    ##                            ln += deltaLines
    ##                        l.append(ln)
    ##                    imptype[imp] = l
    ##
    def replaceBody(self, name, code_block_dict, new_body):
        newLines = len(new_body)
        if not new_body: return
        code_block = code_block_dict[name]
        prevLines = code_block.end - code_block.start
        deltaLines = newLines - prevLines

        self.source[code_block.start: code_block.end] = new_body

        self.renumber(deltaLines, code_block.start)

    def replaceMethodBody(self, class_name, method_name, new_body):
        if not ' '.join(new_body).strip(): new_body = [body_indent + 'pass', '']
        self.replaceBody(method_name, self.classes[class_name].methods, new_body)

    def removeMethod(self, class_name, name):
        code_block = self.classes[class_name].methods[name]
        totLines = code_block.end - code_block.start + 1  # def decl

        self.source[code_block.start - 1: code_block.end] = []

        self.renumber(-totLines, code_block.start - 1)

        self.classes[class_name].remove_method(name)

    def searchDoc(self, body):
        try:
            m = is_doc.search(body)
        except RuntimeError as err:
            if str(err) != 'maximum recursion limit exceeded':
                raise
            else:
                return '<i>Doc string too big for sre</i>'
        if m:
            s, e = m.span()
            return body[s + 3:e - 3].strip()
        else:
            return ''

    def getModuleDoc(self):
        """ Return doc string for module. Scan the area from the start of the
            file up to the first occurence of a doc string containing structure
            like func or class """
        if self.class_order:
            classStart = self.classes[self.class_order[0]].block.start - 1
        else:
            classStart = len(self.source)

        if self.function_order:
            funcStart = self.functions[self.function_order[0]].start - 1
        else:
            funcStart = len(self.source)

        modTop = self.source[:min(classStart, funcStart)]
        return self.searchDoc(' '.join(self.formatDocStr(modTop)))

    def formatDocStr(self, lines):
        l = []
        for line in lines:
            if not line.strip():
                l.append('<P>')
            else:
                l.append(line)
        return l

    def getClassDoc(self, class_name):
        # delete all method bodies
        # XXX broken, returns first doc str in class
        ##        cbl = self.extractClassBody(class_name)
        ##        for meths in self.classes[class_name].methods.values():
        ##            pass
        cls = self.classes[class_name]

        if len(cls.method_order):
            methStart = cls.methods[cls.method_order[0]].start
        else:
            methStart = cls.block.end

        classDoc = self.source[cls.block.start: min(methStart,
                                                    cls.block.end)]

        return self.searchDoc(' '.join(self.formatDocStr(classDoc)))

    def getClassMethDoc(self, class_name, meth_name):
        """ Extract the doc string for a method """
        methDoc = self.extractMethodBody(class_name, meth_name)
        return self.searchDoc(' '.join(self.formatDocStr(methDoc)))

    def getFunctionDoc(self, function_name):
        funcDoc = self.extractFunctionBody(function_name)
        return self.searchDoc(' '.join(self.formatDocStr(funcDoc)))

    def renameClass(self, old_class_name, new_class_name):
        cls = self.classes[old_class_name]
        idx = cls.block.start - 1
        self.source[idx] = self.source[idx].replace(old_class_name,
                                                    new_class_name, 1)
        cls.name = new_class_name
        del self.classes[old_class_name]
        self.classes[new_class_name] = cls
        # rename order
        idx = self.class_order.index(old_class_name)
        del self.class_order[idx]
        self.class_order.insert(idx, new_class_name)

    def renameMethod(self, class_name, old_method_name, new_method_name):
        # untested
        meth = self.classes[class_name].methods[old_method_name]
        idx = meth.start - 1
        self.source[idx] = self.source[idx].replace(old_method_name,
                                                    new_method_name, 1)
        del self.classes[class_name].methods[old_method_name]
        self.classes[class_name].methods[new_method_name] = meth
        # rename order
        ##        idx = self.classes[class_name].method_order.index(old_method_name)
        ##        del self.classes[class_name].method_order[idx]
        ##        self.classes[class_name].method_order.insert(idx, new_method_name)

        self.classes[class_name].method_order[ \
            self.classes[class_name].method_order.index(old_method_name)] = new_method_name

    def addFunction(self, func_name, func_params, func_body):
        if not func_body: return

        # Add a func code block
        ins_point = len(self.source)
        self.functions[func_name] = CodeBlock(func_params,
                                              ins_point, ins_point + len(func_body))
        self.function_order.append(func_name)

        # Add in source
        self.source[ins_point: ins_point] = \
            ['def %s(%s):' % (func_name, func_params)] + func_body + ['']

    def replaceFunctionBody(self, func_name, new_body):
        self.replaceBody(func_name, self.functions, new_body)

    def removeFunction(self, func_name):
        cb = self.functions[func_name]
        ins_point = cb.start
        func_size = cb.end - ins_point

        self.source[ins_point: cb.end] = []
        self.function_order.remove(func_name)
        del self.functions[func_name]

        self.renumber(func_size, ins_point)

    def ExhaustBranch(self, name, classes, path, result):
        """This method will traverse the class heirarchy, from a given
        class and build up a nested dictionary of super-classes. The
        result is intended to be inverted, i.e. the highest level
        are the super classes."""

        def AddPathToHierarchy(path, result, fn):
            """We have an exhausted path. Simply put it into the result dictionary."""
            if path[0] in list(result.keys()):
                if len(path) > 1: fn(path[1:], result[path[0]], fn)
            else:
                for part in path:
                    result[part] = {}
                    result = result[part]

        rv = {}
        if name in classes:
            for cls in classes[name].super:
                if isinstance(cls, str):  # strings are always termination
                    rv[cls] = {}
                    exhausted = path + [cls]
                    exhausted.reverse()
                    AddPathToHierarchy(exhausted, result, AddPathToHierarchy)
                else:
                    rv[cls.name] = self.ExhaustBranch(cls.name, classes,
                                                      path + [cls.name], result)
        if len(rv) == 0:
            exhausted = path
            exhausted.reverse()
            AddPathToHierarchy(exhausted, result, AddPathToHierarchy)
        return rv

    def createHierarchy(self):
        """ Build the inheritance hierarchy """
        hierc = {}
        for cls in list(self.classes.keys()):
            self.ExhaustBranch(cls, self.classes, [cls], hierc)
        return hierc

    def getInfoBlock(self):
        info_block = {}
        c = []
        for cnt in range(len(self.source)):
            if self.source[cnt][:2] == '#-': c.append(cnt)
            if len(c) == 2:
                data = os.linesep.join(self.source[c[0]:c[1] + 1])

                info = is_info.search(data)
                if info:
                    for key in list(info.groupdict().keys()):
                        info_block[key] = info.group(key).strip()
                else:
                    return 'no info'

        return info_block

    def addImportStatement(self, impStmt, resourceImport=0):
        """ Adds an import statement to the code and internal dict if it isn't
            added yet """
        impLine = ''
        isImportFrom = 0
        defLineNo = self.lineno

        m = is_import.match(impStmt)
        if m:
            for n in m.group('imp').split(','):
                n = n.strip()
                if n not in self.imports:
                    self.imports[n] = [defLineNo]
                    impLine = impStmt
        else:
            m = is_from.match(impStmt)
            if m:
                mod = m.group('module')
                if mod not in self.from_imports:
                    self.from_imports[mod] = [defLineNo]
                    impLine = impStmt
                    isImportFrom = 1
            else:
                raise ModuleParseError(_('Import statement invalid: %s') % impStmt)

        if impLine:
            # Add it beneath import wx
            if 'wx' in self.imports:
                insLine = self.imports['wx'][0]
                # Component imports are in a block with the wx import
                if not resourceImport:
                    self.source.insert(insLine, impLine)
                    self.renumber(1, insLine)
                    # Resource import should create their own block under comps
                else:
                    allImports = []
                    for md, lns in list(self.from_imports.items()) + list(self.imports.items()):
                        for ln in lns:
                            allImports.append((ln, md))
                    allImports.sort()

                    # find the first gap after import wxPy
                    newInsLine = -1
                    nextImpLn = -1
                    idx = 0
                    prevLn = start = end = -1
                    while idx < len(allImports):
                        ln, md = allImports[idx]
                        if start == -1 and ln == insLine and md == 'wx':
                            start = ln
                        elif start != -1 and ln > prevLn + 1:
                            end = prevLn + 1
                            nextImpLn = ln
                            break

                        prevLn = ln
                        idx += 1

                    # after all other imports
                    lns = 0
                    if end == -1:
                        end = allImports[-1][0]
                        self.source.insert(end, self.eol)
                        lns += 1

                    insLine = end + lns
                    self.source.insert(insLine, impLine)
                    lns += 1
                    nextLine = self.source[end + lns].strip()
                    if nextLine and nextImpLn != -1:
                        # Add blank line if next line is not an import line
                        if end + lns != nextImpLn:
                            self.source.insert(end + lns, self.eol)
                            lns += 1

                    # correct the linenos added at start of func
                    if isImportFrom:
                        imports = self.from_imports
                    else:
                        imports = self.imports
                    for name, lins in list(imports.items()):
                        if imports[name][0] == defLineNo:
                            imports[name][0] = insLine

                    self.renumber(lns, end)

    def getClassForLineNo(self, line_no):
        for cls in list(self.classes.values()):
            if cls.block.contains(line_no):
                return cls
        return None

    def getFunctionForLineNo(self, line_no):
        for func in list(self.functions.values()):
            if func.contains(line_no):
                return func
        return None

    def getEOLFixedLines(self):
        res = []
        for line in self.source:
            if not (line.endswith('\r\n') or line.endswith('\n') or line.endswith('\r')):
                line += self.eol
            res.append(line)
        return res

    def __repr__(self):
        return 'Module: %s\n' % self.name + \
               'Classes: \n' + pprint.pformat(self.classes) + '\n' + \
               'Functions: \n' + pprint.pformat(self.functions) + '\n'


def moduleFile(module, path=[], inpackage=0):
    """Read a module file and return a dictionary of classes.

    Search for MODULE in PATH and sys.path, read and parse the
    module and return a dictionary with one entry for each class
    found in the module.

    XXX Package code not tested
    """
    if module in sys.builtin_module_names:
        # this is a built-in module
        return Module(module, [])

    # search the path for the module
    f = None
    if inpackage:
        try:
            f, file, (suff, mode, type) = importlib.abc.MetaPathFinder.find_spec(module, path)
        except ImportError:
            f = None
    if f is None:
    #     fullpath = path + sys.path
    #     f, file, (suff, mode, type) = imp.find_module(module, fullpath)
    # if type == imp.PKG_DIRECTORY:
    #     return Module(module, [], {'__path__': [file]}, ['__path__'])
    # if type != imp.PY_SOURCE:
    #     # not Python source, can't do anything with this module
    #     f.close()
    #     return Module(module, [])

        fullpath = path + sys.path
        f, file, (suff, mode, type) = importlib.abc.MetaPathFinder.find_spec(module, fullpath)
        if type == importlib.PKG_DIRECTORY:
            return Module(module, [], {'__path__': [file]}, ['__path__'])
        if type != importlib.PY_SOURCE:
            # not Python source, can't do anything with this module
            f.close()
            return Module(module, [])

    mod = Module(module, f.readlines())
    f.close()
    return mod


if __name__ == '__main__':
    lines = open('moduleparse.py', 'rb').readlines()
    m = Module('', lines[:])
    print(m.from_imports_names)
