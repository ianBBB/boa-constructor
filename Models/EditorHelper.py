#-----------------------------------------------------------------------------
# Name:        EditorHelper.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2007
# Licence:     GPL
#-----------------------------------------------------------------------------

""" Global namespace for general IDE window ids, image indexes and registries """

import Preferences, Utils

(wxID_EDITOROPEN, wxID_EDITORSAVE, wxID_EDITORSAVEAS, wxID_EDITORCLOSEPAGE,
 wxID_EDITORREFRESH, wxID_EDITORDESIGNER, wxID_EDITORDEBUG, wxID_EDITORHELP,
 wxID_DEFAULTVIEWS, wxID_EDITORSWITCHTO, wxID_EDITORDIFF, wxID_EDITORPATCH,
 wxID_EDITORTOGGLEVIEW, wxID_EDITORSWITCHEXPLORER, wxID_EDITORSWITCHSHELL,
 wxID_EDITORSWITCHPALETTE, wxID_EDITORSWITCHINSPECTOR,
 wxID_EDITORTOGGLERO, wxID_EDITORHELPFIND, wxID_EDITORRELOAD,
 wxID_EDITORHELPABOUT, wxID_EDITORHELPGUIDE, wxID_EDITORHELPTIPS,
 wxID_EDITORHELPOPENEX,
 wxID_EDITORPREVPAGE, wxID_EDITORNEXTPAGE,
 wxID_EDITORBROWSEFWD, wxID_EDITORBROWSEBACK,
 wxID_EDITOREXITBOA, wxID_EDITOROPENRECENT,
 wxID_EDITORHIDEPALETTE, wxID_EDITORWINDIMS, wxID_EDITORWINDIMSLOAD,
 wxID_EDITORWINDIMSSAVE, wxID_EDITORWINDIMSRESDEFS,
 wxID_EDITORSWITCHPREFS,
) = Utils.wxNewIds(36)

imgCounter=0
def imgIdxRange(cnt=0):
    """ Allocates either a range of image indexes or a single one """
    global imgCounter
    if cnt:
        rng = range(imgCounter, imgCounter + cnt)
        imgCounter = imgCounter + cnt
        return rng
    else:
        imgCounter = imgCounter + 1
        return imgCounter - 1

builtinImgs =('Images/Modules/FolderUp.png',
              'Images/Modules/Folder.png',
              'Images/Modules/Folder_green.png',
              'Images/Modules/Folder_cyan.png',
              'Images/Shared/SystemObj.png',
              'Images/Shared/SystemObjOrdered.png',
              'Images/Shared/SystemObjBroken.png',
              'Images/Shared/SystemObjPending.png',
              'Images/Shared/SystemObjDisabled.png',
              'Images/Modules/ZopeConn.png',
              'Images/Shared/BoaLogo.png',
              'Images/Modules/Drive.png',
              'Images/Modules/NetDrive.png',
              'Images/Modules/FolderBookmark.png',
              'Images/Modules/OpenEditorModels.png',
              'Images/Modules/PrefsFolder.png',
              'Images/Shared/PrefsSTCStyles.png',
              'Images/Editor/RecentFiles.png',
              'Images/Editor/Shell.png',
              'Images/Editor/Explorer.png',
              'Images/Modules/HelpBook.png',
            )
# Like builtinImgs, but stores list of tuples, (imgIdx, name)
pluginImgs = []

def addPluginImgs(imgPath):
    imgIdx = imgIdxRange()
    pluginImgs.append( (imgIdx, imgPath) )

    return imgIdx


# Indexes for the imagelist
(imgFolderUp, imgFolder, imgPathFolder, imgCVSFolder, imgSystemObj,
 imgSystemObjOrdered, imgSystemObjBroken, imgSystemObjPending, imgSystemObjDisabled,
 imgZopeConnection, imgBoaLogo, imgFSDrive, imgNetDrive, imgFolderBookmark,
 imgOpenEditorModels, imgPrefsFolder, imgPrefsSTCStyles, imgRecentFiles,
 imgShell, imgExplorer, imgHelpBook, imgTextModel, imgBitmapFileModel,
 imgUnknownFileModel, imgInternalFileModel
) = imgIdxRange(25)

# List of name, func tuples that will be installed under the Tools menu.
editorToolsReg = []

# Registry of all modules {modelIdentifier : Model} (populated by EditorModels)
# Used for images and header identifier
modelReg = {}
# Mapping of file extension to model (populated by EditorModels)
extMap = {}
# List of image file extensions
imageExtReg = []
# Dict of ext:Model entries. For types where not all files of that ext are images
imageSubTypeExtReg = {}
# List of extensions for internal filetypes created by Boa
internalFilesReg = []
# Dict of ext:Model entries which can be further identified by reading a header from the source
inspectableFilesReg = {}
# List of extensions for additional binary files (will not be searched)
binaryFilesReg = []
def getBinaryFiles():
    return imageExtReg + binaryFilesReg

def initExtMap():
    # All non python files identified by extension
    for mod in modelReg.values():
        # if mod.ext not in ['.*', '.intfile', '.pybin'] +inspectableFilesReg.keys():
        if mod.ext not in ['.*', '.intfile', '.pybin'] + list(inspectableFilesReg.keys()):
            extMap[mod.ext] = mod
