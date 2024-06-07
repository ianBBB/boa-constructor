import re, sys, os

addPageParams = re.compile("\s*parent\.AddPage\("\
  "(?P<select>bSelect)\s*=\s*((true|false)|[\w\.]+),\s*"\
  "(?P<imageId>imageId)\s*=\s*([-]?[0-9]+|[\w\.]+),\s*"\
  "(?P<page>pPage)\s*=\s*self.\w+,\s*"\
  "(?P<text>strText)\s*=\s*(('(?<=').*')|[\w\.])", re.M)

def UpdateNotebookParams(filename):
    oldSrc = src = open(filename).read()
    while 1:
        m = addPageParams.search(src)
        if m:
            #for grp in ('select', 'imageId', 'page', 'text'):
            src = src[:m.start('select')]+'select'+\
              src[m.end('select'):m.start('imageId')]+'imageId'+\
              src[m.end('imageId'):m.start('page')]+'page'+\
              src[m.end('page'):m.start('text')]+'text'+\
              src[m.end('text'):]
        else:
            break
    if oldSrc != src:
        os.rename(filename, filename+'.bak')
        open(filename, 'w').write(src)
        print('Updated', filename)
    else:
        print('Source for', filename, 'unchanged')
    

if __name__ == '__main__':
    assert len(sys.argv) >= 2, 'Missing filename(s) on the command-line to correct'
    for filename in sys.argv[1:]:
        UpdateNotebookParams(filename)
