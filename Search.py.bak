#----------------------------------------------------------------------
# Name:        Search.py
# Purpose:     Searching html/txt file
#
# Author:      Riaan Booysen
#
# Created:     2000/01/08
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import os
import string, time

import wx

from Utils import _

def count(filename, pattern, caseSensitive):
    try: f = open(filename, 'r')
    except IOError: return 0
    try:
        data = f.read()
        if not caseSensitive:
            data = data.lower()
            pattern = pattern.lower()

        return data.count(pattern)
    finally:
        f.close()

def findInText(sourcelines, pattern, caseSensitive, includeLine = 0):
    results = []
    if not caseSensitive:
        sourcelines = [sourceline.lower() for sourceline in sourcelines]
        pattern = pattern.lower()

    matches = zip(sourcelines, range(len(sourcelines)))
    for line, sourceIdx in matches:
        idx = -1
        while 1:
            idx = line.find(pattern, idx + 1)
            if idx == -1: break
            else:
                result = [sourceIdx, idx]
                if includeLine:
                    result.append(line)
                results.append(tuple(result))
    return results

def findInFile(filename, pattern, caseSensitive, includeLine = 0):
    results = []
    try: f = open(filename, 'r')
    except IOError: return results
    try:
        sourcelines = f.readlines()
        return findInText(sourcelines, pattern, caseSensitive, includeLine)
    finally:
        f.close()

def defaultProgressCallback(dlg, count, file, msg):
    dlg.cont = dlg.Update(min(dlg.max-1, count), msg +' '+ file)

def findInFiles(parent, srchPath, pattern, callback = defaultProgressCallback, deeperPath = '', filemask = ('.htm', '.html', '.txt'), progressMsg = 'Search help files...', dlg = None, joiner = '/'):
    results = []
    names = os.listdir(srchPath)
    cnt = 0

    owndlg = False
    maxval = len(names)
    if not dlg:
        dlg = wx.ProgressDialog(progressMsg, _('Searching...'), maxval, parent,
                           wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
        dlg.max = maxval
        dlg.cont = 1
        owndlg = True
    try:
        for file in names:
            filePath = os.path.join(srchPath, file)

            if os.path.isdir(filePath):
                results.extend(findInFiles(parent, filePath, pattern,
                  callback, deeperPath+file+joiner, filemask, dlg = dlg, joiner = joiner))
            else:
                ext = os.path.splitext(file)[1]
                if ext in filemask or ('.*' in filemask and ext):
                    callback(dlg, cnt, file, _('Searching'))
                    ocs = count(filePath, pattern, 0)
                    if ocs:
                        results.append((ocs, deeperPath+file))
                else:
                    callback(dlg, cnt, file, _('Skipping'))

            if cnt < maxval -1:
                cnt = cnt + 1

            if not dlg.cont:
                break

        return results
    finally:
        if owndlg:
            dlg.Destroy()

class _file_iter:
    def __init__(self, folders, file_filter, bIncludeFilter = 1, bRecursive = 1):
        """
            folders - list of folders to go through. This list must not be empty
                      otherwise LookupError will be thrown
            file_filter - may be right name could be file filter by file
                          extension, if file_filter is empty then all files will
                          be included.
            bIncludeFilter - this flag indicates how to treat file_filter. If
                             bIncludeFilter == True then all files that meets
                             file_filter criteria will be included to resulting
                             list
            bRecursive - whether to walk through directories in recursive way or
                         not
        """
        self._folders = folders
        if not self._folders:
            raise LookupError(_("Root folder was not specified"))
        self._filters = []
        for sExt in file_filter:
            self._filters.append(sExt.lower())
        self._is_include_filter = bIncludeFilter
        self._is_recursive = bRecursive
        self._files = [] #resulting list

    def _is_to_include(self, sFullFileName):
        """This function will return True if file must be included and False if not"""
        if not self._filters:
            return 1 #all files must be included
        tpFileNameOnly = os.path.split( sFullFileName )
        sExt = '*.' + tpFileNameOnly[-1].split('.')[-1]
        if sExt.lower() in self._filters:
            #file extension within filters
            #if _is_include_filter = 1 then file must be included
            return self._is_include_filter
        else:
            #file extension not in filters
            #if _is_include_filter = 1 then file must be skiped
            return not self._is_include_filter

    def _GetFolderFileLists(self, sFullFolderName):
        """This function will return tuple(folders, files) where files is a list
           all files, according to file_filter and folders is all subfolders
           of given folders. All results are full names
        """
        lstFiles, lstFolders = [], []
        #getting all files from folder
        lstContents = os.listdir(sFullFolderName)
        for sPath in lstContents:
            #building full file name
            sFullPath = os.path.join(sFullFolderName, sPath)
            if os.path.isfile( sFullPath ) and self._is_to_include( sFullPath ):
                lstFiles.append( sFullPath )
            elif os.path.isdir( sFullPath ):
                lstFolders.append( sFullPath )
            else:
                pass
        return lstFolders, lstFiles

    def _walk(self):
        """This function will work through foldres and collect all files"""
        lstFolders = self._folders[:]
        while lstFolders:
            sCurrFolder = lstFolders.pop(0)
            lstToWalkFolders, lstFiles = self._GetFolderFileLists(sCurrFolder)
            if self._is_recursive:
                lstFolders.extend( lstToWalkFolders )
            self._files.extend( lstFiles )

    def __call__(self):
        self._files = []
        self._walk()
        return self._files

def listFiles(folders, file_filter, bIncludeFilter=1, bRecursive=1):
    return _file_iter(folders, file_filter, bIncludeFilter, bRecursive)()


if __name__ == '__main__':
    wx.PySimpleApp()
    f = wx.Frame(None, -1, 'results', size=(0, 0))
    print findInFiles(f, os.path.abspath('ExternalLib'), 'riaan', filemask = ('.*',))
