# pyright: ignore
# type: ignore

import os, sys

# just import to confirm resourcepackage is installed
import resourcepackage

src__init__ = '''"""Design-time __init__.py for resourcepackage

This is the scanning version of __init__.py for your
resource modules. You replace it with a blank or doc-only
init when ready to release.
"""
import sys

if not hasattr(sys, 'frozen'):
    import os
    if os.path.splitext(os.path.basename( __file__ ))[0] == "__init__":
        try:
            from resourcepackage import package, defaultgenerators
            generators = defaultgenerators.generators.copy()

            ### CUSTOMISATION POINT
            ## import specialised generators here, such as for wxPython
            #from resourcepackage import wxgenerators
            #generators.update( wxgenerators.generators )
        except ImportError:
            pass
        else:
            package = package.Package(
                    packageName = __name__,
                    directory = os.path.dirname( os.path.abspath(__file__) ),
                    generators = generators,
            )
            package.scan(
                    ### CUSTOMISATION POINT
                    ## force true -> always re-loads from external files, otherwise
                    ## only reloads if the file is newer than the generated .py file.
                    # force = 1,
            )
'''

def visitDir((onlyCleanup, packages), dirname, names):
    for name in names:
        path = os.path.join(dirname, name)
        if os.path.isdir(path):
            if name == 'CVS':
                continue
            packages.append(path)
        else:
            if os.path.splitext(name)[-1] in ('.py', '.pyc', '.pyo'):
                try:
                    os.remove(os.path.join(path))
                except Exception: pass


def createPackageInitFiles(paths, onlyCleanup=False):
    for path in paths:
        packages = []
        os.path.walk(path, visitDir, (onlyCleanup, packages))

        if not onlyCleanup:
            importLst = []
            for pth in packages:
                pck = pth[len(path)+1:].strip().replace('/', '.').replace('\\', '.')
                importLst.append(pck)
                open(os.path.join(pth, '__init__.py'), 'w').write(src__init__)

            sep = '\n'
            main_init = sep.join(['import %s'%pck for pck in importLst])
            init_file = os.path.join(path, '__init__.py')
            open(init_file, 'w').write(src__init__+sep*2+main_init+sep)
            cur_path = sys.path
            try:
                sys.path = [os.path.dirname(init_file)]+cur_path
                 exec(compile(open(init_file, 'rb').read(), init_file, 'exec'),
                     {'__file__': init_file})
            finally:
                sys.path = cur_path


if __name__ == '__main__':
    createPackageInitFiles(('../Images',), onlyCleanup=False)
    #createPackageInitFiles(('../Plug-ins/Images',), onlyCleanup=False)
