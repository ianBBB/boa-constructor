#!/bin/env python
# Simple-minded Python identifier checker (Ka-Ping Yee, 1 April 1997)

import sys, string, tokenize, pprint
##import os, getopt
import __builtin__

warnings = []

def terse_warn(file, linenum, line, message, start=0, end=0):
    print ('%s:%d: %s' % (file, linenum, message))

def log_warn(file, linenum, line, message, start=0, end=0):
    warnings.append( (file, linenum, message) )

warn = log_warn
opt_i = 0
ignore_subobjs = 1

##def tty_warn(file, linenum, line, message, start=0, end=0):
##    print '%s:%d: %s\n  %s' % (file, linenum, message, line),
##
##BOLD, NORMAL = '\x1b[1m', '\x1b[0m'
##def vt100_warn(file, linenum, line, message, start=0, end=0):
##    print '%s:%d: %s' % (file, linenum, message)
##    print '  ' + line[:start] + BOLD + line[start:end] + NORMAL + line[end:],
##
##vt100_compatible = ('vt100', 'vt102', 'xterm', 'ansi', 'iris-ansi', 'linux')
##
##options, args = getopt.getopt(sys.argv[1:], 'vhi')
##if not args or ('-h', '') in options:
##    print "PyLint (1 April 1997) by Ka-Ping Yee"
##    print "usage: %s [-v] [-i] filename.py" % sys.argv[0]
##    print "    -v for verbose mode (display source lines)"
##    print "    -i to import modules that are imported in the file"
##    sys.exit(0)
##
##if args[0] == '-': file = sys.stdin
##else: file = open(args[0])
##opt_i = ('-i', '') in options
##if ('-v', '') not in options:
##    warn = terse_warn
##elif os.environ.has_key('TERM') and os.environ['TERM'] in vt100_compatible:
##    warn = vt100_warn
##else:
##    warn = tty_warn

try: 1/0
except: tb = sys.exc_traceback
special = {}
for name in str.split('and break class continue def del elif else except '
    'exec finally for from global if import in is lambda not or pass print '
    'raise return try while true false') + dir(__builtin__): special[name] = 1
member = {}
for name in [].__methods__ + {}.__methods__ + [].append.__members__ + \
    warn.__members__ + warn.func_code.__members__ + \
    tb.__members__ + tb.tb_frame.__members__ + \
    ['__dict__', '__methods__', '__members__']: member[name] = 1
#    file.__methods__ + file.__members__ + \
reserved = {}
for name in str.split('abs add and bases builtin builtins call class cmp '
    'coerce copy copyright deepcopy del delattr delitem delslice div divmod '
    'file float getattr getinitargs getitem getslice getstate hash hello hex '
    'init int invert len long lshift main mod mul name neg nonzero oct or pos '
    'pow radd rand rcmp rdiv rdivmod repr rlshift rmod rmul ror rpow rrshift '
    'rshift rsub rxor setattr setitem setslice setstate str sub version xor'):
    reserved['__'+name+'__'] = 1

position, modules, defined = {}, {}, {}

def init_globals(afilename):
    global warnings, position, modules, defined, modfrom, sawimport, last, parent, filename, bracket_depth

    warnings[:] = []
    position.clear(); modules.clear(); defined.clear()
    modfrom = sawimport = 0
    last = parent = ''
    filename = afilename
    bracket_depth = 0

init_globals('')
def count(type, token, (srow, scol), (erow, ecol), line,
    seen = special.has_key, imported = modules.has_key):
    global sawimport, modfrom, last, parent, modules, bracket_depth

    if token == 'import': sawimport = 1
    elif token in ('\r\n', '\n', ';'): modfrom, sawimport = '', 0
    elif token == '.': parent = last
    elif token == '(': bracket_depth = bracket_depth + 1
    elif token == ')': bracket_depth = bracket_depth - 1
    else:
        try:
            if last == 'from': modfrom = token
            elif last in ('class', 'def'): defined[token] = 1
            elif opt_i and modfrom and token == '*':
                try:
                    for name in dir(__import__(modfrom)):
                        if name[0] != '_': special[name] = 1
                except: pass
            if type != tokenize.NAME or seen(token): return
            if opt_i and not modfrom and sawimport and not imported(token):
                try:
                    modules[token] = {}
                    for name in dir(__import__(token)):
                        modules[token][name] = 1
                except: pass
            if parent and member.has_key(token): pass
            # RB:
            # Added the following two cases:
            #  Optionally ignore all sub_obj if not in importing mode
            #    Boa can't use importing mode for fear of interpreter pollution
            #  Ignore all wx* names these are from wxPython and usually imported
            #    with a from wxPython.* import *
            #    Maybe test should rather be directly against the wxPython
            #    namespaces
            # --
            elif parent and parent == 'self':
                special[token] = 1
            elif parent and ignore_subobjs and not opt_i: pass
            elif len(token) >= 3 and token[:2] == 'wx' and token[2] in string.uppercase: pass
            elif len(token) >= 5 and token[:4] == 'EVT_': pass
            # --
            elif imported(parent) and modules[parent].has_key(token): pass
            elif position.has_key(token):
                del position[token]
                special[token] = 1
            elif token[:2] == '__' == token[-2:]:
                if not reserved.has_key(token):
                    warn(filename, srow, line,
                        'dubious reserved name "%s"' % token, scol, ecol)
            elif last != 'from': position[token] = (srow, line, scol, ecol, bracket_depth)

        finally:
            last, parent = token, ''

def pylint(afile, filename):
##    print 'RESERVED'
##    pprint.pprint(reserved)
##    print 'SPECIAL'
##    pprint.pprint(special)
    init_globals(filename)
    try: tokenize.tokenize(afile.readline, count)
    except tokenize.TokenError, message:
        warn(filename, 0, '', message)
        sys.exit(1)
    
    unique = []
    for name, (linenum, line, start, end, brk_dpth) in position.items():
        unique.append( (linenum, (start, end, name, line, brk_dpth)) )
    unique.sort()
    for linenum, (start, end, name, line, brk_dpth) in unique:
        warn(filename, linenum, line, ('"%s" used only once (%d)',
             '"%s" defined but unused (%d)')[defined.has_key(name)] % (name, brk_dpth), start, end)

if __name__ == '__main__':
    pylint(open('pylint.py'), 'pylint.py')
    pprint.pprint(warnings)







