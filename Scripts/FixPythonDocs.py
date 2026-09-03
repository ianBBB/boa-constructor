"""Script that cleans up the Python documentation so that it can be used with the
wx.html.HTMLWindow class."""

import os

# set this to point to the python help html directory that should be cleaned up
docDir = '../NewDocs/python/dest'


subDirs = ['tut', 'ref', 'mac', 'ext', 'doc', 'api', 'lib', 'dist', 'inst', 'whatsnew']

anchor1 = "<tt id='"
anchor2 = "<a id='"

def fixNamedAnchors(docDir, subDirs):
    def visit_dir(files_excludes, dirname, names):
        excludes, = files_excludes
        for name in names:
            if name not in excludes:
                filename = os.path.join(dirname, name)
                if os.path.isfile(filename):
                    if not filename.endswith('.html'):
                        continue

                    data = origData = open(filename).read()

                    # anchor1
                    pos = 0
                    prev = -1
                    resLst = []
                    while 1:
                        pos = data.find(anchor1, 1)
                        if pos == -1:
                            break
                        ttIdStart = pos+len(anchor1)
                        ttId = data[ttIdStart:data.find("'", ttIdStart)]

                        resLst.append(data[:pos])
                        resLst.append("<a name='%s'></a>"%ttId)
                        data = data[pos:]

                    if data:
                        resLst.append(data)

                    data = ''.join(resLst)

                    # anchor2
                    pos = 0
                    prev = -1
                    resLst = []
                    while 1:
                        pos = data.find(anchor2, 1)
                        if pos == -1:
                            break

                        aIdStart = pos+len(anchor2)
                        aId = data[aIdStart:data.find("'", aIdStart)]

                        resLst.append(data[:pos+3])
                        resLst.append("name='%s' "%aId)
                        data = data[pos+3:]

                    if data:
                        resLst.append(data)

                    data = ''.join(resLst)

                    if data != origData:
                        print('fixed %s'%filename)
                        open(filename, 'w').write(data)


    for dirname, _dirs, names in os.walk(docDir):
        visit_dir(([''],), dirname, names)

def strip_utf8(docDir):
    utf8 = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'

    def visit_dir(files_excludes, dirname, names):
        excludes, = files_excludes
        for name in names:
            if name not in excludes:
                filename = os.path.join(dirname, name)
                if os.path.isfile(filename):
                    data = open(filename).read()
                    if utf8 in data:
                        data = data.replace(utf8, '')
                        open(filename, 'w').write(data)
                        print('rewrote', filename)

    for dirname, _dirs, names in os.walk(docDir):
        visit_dir(([''],), dirname, names)



if __name__ == '__main__':
    fixNamedAnchors(docDir, subDirs)
    strip_utf8(docDir)
