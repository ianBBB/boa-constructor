#----------------------------------------------------------------------
# Name:        EditorModels.py
# Purpose:     Model classes usually representing different types of
#              source code
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2007 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

""" The model classes represent different types of source code files,
    Different views can be connected to a model  """

print 'importing Models.EditorModels'

import os, sys, tempfile
from cStringIO import StringIO

import wx

import Preferences, Utils, EditorHelper
from Preferences import keyDefs
from Utils import _

_vc_hook = None

class EditorModel:
    defaultName = 'abstract'
    bitmap = 'None'
    imgIdx = -1
    objCnt = 0
    plugins = ()
    def __init__(self, data, name, editor, saved):
        self.active = False
        self.data = data
        self.savedAs = saved
        self.filename = name
        self.editor = editor
        self.transport = None
        self.prevSwitch = None

        self.views = {}
        self.modified = not saved
        self.viewsModified = []
        
        plugins = {}
        for Plugin in self.plugins:
            plugins[Plugin.name] = Plugin(self)
        self.plugins = plugins

    def destroy(self):
        self.views = ()
        self.viewsModified = ()
        self.plugins = ()

    def updateNameFromTransport(self):
        if self.transport:
            self.filename = self.transport.getURI()

    def reorderFollowingViewIdxs(self, idx):
        for view in self.views.values():
            if view.pageIdx > idx:
                view.pageIdx = view.pageIdx - 1

    def getDataAsLines(self):
        return StringIO(self.data).readlines()

    def setDataFromLines(self, lines):
        data = self.data
        strlines = []
        for line in lines:
            # XXX This is an unneeded bottleneck, why not on the joined str ???
            # encodes unicode in the default encoding
            strlines.append(Utils.stringFromControl(line))
        self.data = ''.join(strlines)
        self.modified = self.modified or self.data != data

    def hasUnsavedChanges(self):
        return self.modified or len(self.viewsModified)

    def notify(self):
        """ Update all views connected to this model.
            This method must be called after changes were made to the model """
        for view in self.views.values():
            view.update()

    def update(self):
        """ Rebuild additional derived structure, called when data is changed """
        for plugin in self.plugins:
            self.plugins[plugin].update()

    def refreshFromViews(self):
        for view in self.viewsModified:
            self.views[view].refreshModel()

    def getPageName(self):
        if getattr(Preferences, 'showFilenameExtensions', 0):
            return os.path.basename(self.filename)
        else:
            return os.path.splitext(os.path.basename(self.filename))[0]

    # XXX Move these names into overrideable attrs
    def getSourceView(self):
        views = self.views
        if views.has_key('Source'):
            return views['Source']
        elif views.has_key('ZopeHTML'):
            return views['ZopeHTML']
        return None




class FolderModel(EditorModel):
    modelIdentifier = 'Folder'
    defaultName = 'folder'
    bitmap = 'Folder.png'
    imgIdx = EditorHelper.imgFolder

    def __init__(self, data, name, editor, filepath):
        EditorModel.__init__(self, data, name, editor, True)
        self.filepath = filepath

class SysPathFolderModel(FolderModel):
    modelIdentifier = 'SysPathFolder'
    defaultName = 'syspathfolder'
    bitmap = 'Folder_green.png'
    imgIdx = EditorHelper.imgPathFolder

class CVSFolderModel(FolderModel):
    modelIdentifier = 'CVS Folder'
    defaultName = 'cvsfolder'
    bitmap = 'Folder_cyan.png'
    imgIdx = EditorHelper.imgCVSFolder

    def __init__(self, data, name, editor, filepath):
        FolderModel.__init__(self, data, name, editor, filepath)
        self.readFiles()

    def readFile(self, filename):
        f = open(filename, 'r')
        try: return f.read().strip()
        finally: f.close()

    def readFiles(self):
        self.root = self.readFile(os.path.join(self.filepath, 'Root'))
        self.repository = self.readFile(os.path.join(self.filepath, 'Repository'))
        self.entries = []

        f = open(os.path.join(self.filepath, 'Entries'), 'r')
        dirpos = 0
        try:
            txtEntries = f.readlines()
            for txtEntry in txtEntries:
                txtEntry = txtEntry.strip()
                if txtEntry:
                    if txtEntry == 'D':
                        pass
                        # maybe add all dirs?
                    elif txtEntry[0] == 'D':
                        self.entries.insert(dirpos, CVSDir(txtEntry))
                        dirpos = dirpos + 1
                    else:
                        try:
                            self.entries.append(CVSFile(txtEntry, self.filepath))
                        except IOError: pass
        finally:
            f.close()

class BasePersistentModel(EditorModel):
    fileModes = ('rb', 'wb')
    saveBmp = 'Images/Editor/Save.png'
    saveAsBmp = 'Images/Editor/SaveAs.png'

    def load(self, notify=True):
        """ Loads contents of data from file specified by self.filename.
            Note: Load's not really used much currently cause objects are
                  constructed with their data as parameter """
        if not self.transport:
            raise Exception, _('No transport for loading')

        self.data = self.transport.load(mode=self.fileModes[0])
        self.modified = False
        self.saved = False
        self.update()
        if notify: self.notify()

    def save(self, overwriteNewer=False):
        """ Saves contents of data to file specified by self.filename. """
        if not self.transport:
            raise Exception, _('No transport for saving')

        if self.filename:
            filename = self.transport.assertFilename(self.filename)
            # this check is to minimise interface change.
            if overwriteNewer:
                self.transport.save(filename, self.data, mode=self.fileModes[1],
                      overwriteNewer=True)
            else:
                self.transport.save(filename, self.data, mode=self.fileModes[1])
            self.modified = False
            self.saved = True

            for view in self.views.values():
                view.saveNotification()

            if _vc_hook:
                _vc_hook.save(filename, self.data, mode=self.fileModes[1])
        else:
            raise Exception, _('No filename')

    def saveAs(self, filename):
        """ Saves contents of data to file specified by filename.
            Override this to catch name changes. """
        # Catch transport changes
        from Explorers.Explorer import splitURI, getTransport
        protO, catO, resO, uriO = splitURI(self.filename)
        protN, catN, resN, uriN = splitURI(filename)

        if protO != protN:
            self.transport = getTransport(protN, catN, resN,
                  self.editor.explorerStore.transports)#explorer.tree.transports)

        # Rename and save
        oldname = self.filename
        self.filename = filename
        try:
            self.save(overwriteNewer=True)
        except:
            self.filename = oldname
            raise
        self.savedAs = True

    def localFilename(self, filename=None):
        if filename is None: filename = self.filename
        from Explorers.Explorer import splitURI
        return splitURI(filename)[2]

    def assertLocalFile(self, filename=None):
        # XXX depreciated (and silly!)

        if filename is None:
            filename = self.filename
        from Explorers.Explorer import splitURI
        prot, cat, filename, uri = splitURI(filename)
        assert prot=='file', _('Operation only supported on the filesystem.')
        return filename

    def checkLocalFile(self, filename=None):
        """ Either return the model's uri as a local filepath or raise an error """

        if filename is None:
            filename = self.filename
        from Explorers.Explorer import splitURI, TransportError
        prot, cat, filename, uri = splitURI(filename)
        if prot != 'file':
            raise TransportError, _('Operation only supported on the filesystem.')
        return filename

    def getDefaultData(self):
        return ''

    def new(self):
        self.data = self.getDefaultData()
        self.savedAs = False
        self.modified = True
        self.update()
        self.notify()

class PersistentModel(BasePersistentModel):
    def __init__(self, data, name, editor, saved):
        BasePersistentModel.__init__(self, data, name, editor, saved)
        if data: self.update()

    def load(self, notify=True):
        BasePersistentModel.load(self, False)
        self.update()
        if notify: self.notify()

class BitmapFileModel(PersistentModel):
    modelIdentifier = 'Bitmap'
    defaultName = 'bitmap'
    bitmap = 'Bitmap.png'
    imgIdx = EditorHelper.imgBitmapFileModel
    ext = '.bmp'

    fileModes = ('rb', 'wb')

    extTypeMap = {'.bmp': wx.BITMAP_TYPE_BMP, #'.gif': wx.BITMAP_TYPE_GIF,
                  '.jpg': wx.BITMAP_TYPE_JPEG, '.png': wx.BITMAP_TYPE_PNG}

    def save(self, overwriteNewer=False):
        ext = os.path.splitext(self.filename)[1].lower()
        if ext == '.gif':
            raise Exception, _('Saving .gif format not supported')

        PersistentModel.save(self, overwriteNewer)

    def saveAs(self, filename):
        # catch image type changes
        newExt = os.path.splitext(filename)[1].lower()
        oldExt = os.path.splitext(self.filename)[1].lower()
        updateViews = 0
        if newExt != oldExt:
            updateViews = 1
            import cStringIO
            bmp = wx.BitmapFromImage(wx.ImageFromStream(
                  cStringIO.StringIO(self.data)))
            fn = tempfile.mktemp(newExt)
            try:
                bmp.SaveFile(fn, self.extTypeMap[newExt])
            except KeyError:
                raise Exception, _('%s image file types not supported')%newExt
            try:
                # convert data to new image format
                self.data = open(fn, 'rb').read()
            finally:
                os.remove(fn)

        # Actually save the file
        PersistentModel.saveAs(self, filename)

        if updateViews:
            self.notify()

class SourceModel(BasePersistentModel):
    modelIdentifier = 'Source'
    def __init__(self, data, name, editor, saved):
        BasePersistentModel.__init__(self, data, name, editor, saved)

    def getCVSConflicts(self):
        # needless obscurity
        # numedLines = apply(map, (None,) + (lines, range(len(lines))) )

        # use model.module.source
        conflictStart = -1
        confCnt = 0
        lineNo = 0
        conflicts =[]
        for line in self.getDataAsLines():
            if line[:8] == '<<<<<<< ' and \
                  line[8:].strip() == os.path.basename(self.filename):
                conflictStart = lineNo
            if line[:8] == '>>>>>>> ':
                rev = line[8:]
                conflicts.append( (rev, conflictStart, lineNo - conflictStart) )
                confCnt = confCnt + 1
            lineNo = lineNo + 1
        return conflicts

    def applyChangeBlock(self, conflict, blockIdx):
        rev, start, size = conflict
        lines = self.getDataAsLines()

        blocks = Utils.split_seq(lines[start+1 : start+size], '=======')
        lines[start:start+size+1] = blocks[blockIdx]
        self.setDataFromLines(lines)

        self.update()
        self.notify()

        self.editor.updateModuleState(self)

    def acceptConflictChange(self, conflict):
        self.applyChangeBlock(conflict, 1)

    def rejectConflictChange(self, conflict):
        self.applyChangeBlock(conflict, 0)


class TextModel(PersistentModel):
    modelIdentifier = 'Text'
    defaultName = 'text'
    bitmap = 'Text.png'
    imgIdx = EditorHelper.imgTextModel
    ext = '.txt'

class UnknownFileModel(TextModel):
    modelIdentifier = 'Unknown'
    defaultName = '*'
    bitmap = 'Unknown.png'
    imgIdx = EditorHelper.imgUnknownFileModel
    ext = '.*'

class InternalFileModel(TextModel):
    modelIdentifier = 'Internal'
    defaultName = ''
    bitmap = 'InternalFile.png'
    imgIdx = EditorHelper.imgInternalFileModel
    ext = '.intfile'

#-------------------------------------------------------------------------------

modelReg = EditorHelper.modelReg
extMap = EditorHelper.extMap

# model registry: add to this dict to register a Model (needed for explorer images)
modelReg.update({
            TextModel.modelIdentifier: TextModel,
            UnknownFileModel.modelIdentifier: UnknownFileModel,
            BitmapFileModel.modelIdentifier: BitmapFileModel,
            InternalFileModel.modelIdentifier: InternalFileModel,
            })

extMap[''] = TextModel
extMap['.jpg'] = extMap['.gif'] = extMap['.png'] = extMap['.ico'] = BitmapFileModel

EditorHelper.imageExtReg.extend(['.bmp', '.jpg', '.gif', '.png', '.ico'])
EditorHelper.internalFilesReg.extend(['.umllay', '.implay', '.brk', '.trace', '.stack', '.cycles', '.prof', '.cached'])
EditorHelper.binaryFilesReg.extend(['.zexp', '.prof'])
