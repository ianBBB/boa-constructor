#-----------------------------------------------------------------------------
# Name:        BuildImage.py
# Purpose:     Copy all files specified in the CVS entry files recursively
#              to create an image for distribution
#                
# Author:      Riaan Booysen
#                
# Created:     2000/07/12
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

''' Copy all files specified in the CVS entry files recursively
to create an image for distribution '''

buildDest = '..\\Releases\\Image'
buildRoot = '..'

import os, shutil, string

def copyFilePath(srcFilepath, dstFilepath):
    try:
        f = open(os.path.join(srcFilepath, 'CVS', 'Entries'), 'r')
        dirpos = 0 
        try:
            txtEntries = f.readlines()
            for txtEntry in txtEntries:
                txtEntry = txtEntry.strip()
                if txtEntry:
                    if txtEntry == 'D':
                        pass
                    elif txtEntry[0] == 'D':
                        dirName = str.split(txtEntry, '/')[1]
                        copyFilePath(os.path.join(srcFilepath, dirName), 
                          os.path.join(dstFilepath, dirName))
                    else:
                        try:
                            filename = str.split(txtEntry, '/')[1]
                            print ('copying ', os.path.join(dstFilepath, filename))
                            try: os.makedirs(dstFilepath)
                            except OSError: pass
                            shutil.copy(os.path.join(srcFilepath, filename),
                              os.path.join(dstFilepath, filename))
                        except IOError: print ('Error', filename)
        finally:
            f.close()
    except IOError:
        print ('CVS does not exist')

copyFilePath(buildRoot, buildDest)