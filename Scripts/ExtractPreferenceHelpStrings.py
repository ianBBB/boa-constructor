""" Script to read preference help comments and write it to a python source file
    that gettext type source scanners can pick up """

import os, sys

sys.path.insert(0, '..')

import moduleparse

def parsePrefsFile(prefsPath, comments, breaks):
    module = moduleparse.Module(os.path.basename(prefsPath), open(prefsPath).readlines())

    for name in module.global_order[:]:
        # Read possible comment/help or options
        comment = []
        option = ''
        idx = module.globals[name].start-2
        while idx >= 0:
            line = module.source[idx].strip()
            if len(line) > 11 and line[:11] == '## options:':
                option = line[11:].strip()
                idx = idx - 1
            elif len(line) > 8 and line[:8] == '## type:':
                option = '##'+line[8:].strip()
                idx = idx - 1
            elif line and line[0] == '#':
                comment.append(line[1:].lstrip())
                idx = idx - 1
            else:
                break
        comment.reverse()
        comments.append( (name, '\n'.join(comment)) )
        breaks.update(module.break_lines)

def createStringsFile(comments, breaks):
    srcComments = '\n'.join(['%s = _(%r)'%(name, comment) 
                             for name, comment in comments 
                             if comment])
    srcBreaks = '\n'.join(['_(%r)'%text for text in breaks.values() if text])
    
    open('prefs.rc.i18n.py', 'w').write(srcComments+'\n\n'+srcBreaks)

#-------------------------------------------------------------------------------
    
if __name__ == '__main__':
    comments = []
    breaks = {}
    parsePrefsFile('../Config/prefs_rc.py', comments, breaks)
    parsePrefsFile('../Config/prefs_msw_rc.py', comments, breaks)
    
    createStringsFile(comments, breaks)
    #print comments
