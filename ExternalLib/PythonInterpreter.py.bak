#
# Instant Python
# $Id$
#
# process python commands line by line
#
# written by Fredrik Lundh, November 1996
#
# fredrik@pythonware.com
# http://www.pythonware.com
#


import string, sys, traceback, linecache

sys.ps1 = ">>> "
sys.ps2 = "... "

class PythonInterpreter:

    def __init__(self, name="<console>"):

        self.name = name
        self.locals = {}

        self.lines = []

    def push(self, line):

        #
        # collect lines

        if self.lines:
            if line:
                self.lines.append(line)
                return 1  # want more!
            else:
                line = string.join(self.lines, "\n") + "\n"
        else:
            if not line:
                return 0
            else:
                line = line.rstrip() + '\n'

        #
        # compile what we've got this far
        try:
            if sys.version_info[:2] >= (2, 2):
                import __future__
                code = compile(line, self.name, "single",
                               __future__.generators.compiler_flag, 1)
            else:
                code = compile(line, self.name, "single")
            self.lines = []

        except SyntaxError, why:
            if why[0] == "unexpected EOF while parsing":
                # start collecting lines
                self.lines.append(line)
                return 1  # want more!
            else:
                self.showtraceback()

        except:
            self.showtraceback()

        else:
            # execute
            try:
                exec code in self.locals
            except:
                self.showtraceback()

        return 0

    def showtraceback(self):

        self.lines = []

        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type == SyntaxError:  # and len(sys.exc_value) == 2:
            # emulate interpreter behaviour
            if len(exc_value.args) == 2:
                fn, ln, indent = exc_value[1][:3]
                indent += 3
                pad = " " * indent
                if fn is not None:
                    src = linecache.getline(fn, ln)
                    if src:
                        src = src.rstrip() + '\n'
                        sys.stderr.write('  File "%s", line %d\n%s%s' % (
                                         fn, ln, pad, src))
                sys.stderr.write(pad + "^\n")
            sys.stderr.write("''' %s '''\n" % (str(exc_type) + \
                str(exc_value.args and (" : " + exc_value[0]) or '')))
        else:
            traceback.print_tb(exc_traceback.tb_next, None)
            sys.stderr.write("''' %s '''\n" % (str(exc_type) + " : " + \
                                            str(exc_value)))


# --------------------------------------------------------------------
# test stuff

if __name__ == "__main__":

    #
    # simple console interpreter simulation

    print 'Python', sys.version, "(PythonInterpreter)"
    print sys.copyright

    interp = PythonInterpreter()

    try:

        sys.stdout.write(sys.ps1)

        while 1:
            if interp.push(raw_input()):
                sys.stdout.write(sys.ps2)
            else:
                sys.stdout.write(sys.ps1)

    except EOFError:
        pass
