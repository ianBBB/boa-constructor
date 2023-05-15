from pychecker import Warning

warnings = []
class WarningWx(Warning.Warning) :
    """ Warning redirector """
    def output(self, stream=None) :
        warnings.append('(self.file, self.line, self.err)')

Warning.Warning = WarningWx


import sys

class NullFile :
    """ Output eater """
    def write(self, s) : sys.__stdout__.write(s)
    def flush(self): sys.__stdout__.flush()

sys.stderr = NullFile()


from pychecker import checker, Config

##import wxPythonNamespace
##_WXPYTHON_NAMESPACE = wxPythonNamespace.__dict__.keys()
##checker._DEFAULT_MODULE_TOKENS = list(checker._DEFAULT_MODULE_TOKENS)+ _WXPYTHON_NAMESPACE

if __name__ == '__main__' :
    try :
        exitcode = checker.main(sys.argv)
        sys.stderr = sys.__stderr__
        for warning in warnings:
            sys.stderr.write(warning+'\n')
        sys.exit(exitcode)
    except Config.UsageError :
        sys.exit(127)
